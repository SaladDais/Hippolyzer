import unittest

from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.message.msgtypes import PacketFlags
from hippolyzer.lib.proxy.circuit import ProxiedCircuit, InjectionTracker
from hippolyzer.lib.base.network.transport import Direction


class MockedProxyCircuit(ProxiedCircuit):
    def __init__(self):
        super().__init__(("127.0.0.1", 0), ("0.0.0.0", 0), None)
        self.sent_simple = []
        self.sent_msgs = []
        # Use a small maxlen to test what happens when injected
        # IDs get evicted from the deque
        self.out_injections = InjectionTracker(0, maxlen=10)
        self.in_injections = InjectionTracker(0, maxlen=10)

    def _send_prepared_message(self, msg: Message, transport=None):
        self.sent_simple.append((msg.packet_id, msg.name, msg.direction, msg.synthetic, msg.acks))
        self.sent_msgs.append(msg)


class PacketIDTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.circuit = MockedProxyCircuit()

    def _send_message(self, msg, outgoing=True):
        msg.direction = Direction.OUT if outgoing else Direction.IN
        return self.circuit.send(msg)

    async def test_basic(self):
        self._send_message(Message('ChatFromViewer', packet_id=1))
        self._send_message(Message('ChatFromViewer', packet_id=2))

        self.assertSequenceEqual(self.circuit.sent_simple, (
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (2, "ChatFromViewer", Direction.OUT, False, ()),
        ))

    async def test_inject(self):
        self._send_message(Message('ChatFromViewer', packet_id=1))
        self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer', packet_id=2))

        self.assertSequenceEqual(self.circuit.sent_simple, (
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (2, "ChatFromViewer", Direction.OUT, True, ()),
            (3, "ChatFromViewer", Direction.OUT, False, ()),
        ))

    async def test_max_injected(self):
        self._send_message(Message('ChatFromViewer', packet_id=1))
        for _ in range(5):
            self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer', packet_id=2))

        self.assertEqual(self.circuit.out_injections.get_original_id(1), 1)
        self.assertEqual(self.circuit.out_injections.get_original_id(7), 2)

        for _ in range(7):
            self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer', packet_id=3))

        self.assertEqual(len(self.circuit.sent_simple), 15)

        for i in range(15):
            pack = self.circuit.sent_simple[i]
            # Check that the sequence nums match what we'd expect
            self.assertEqual(pack[0], i + 1)
            # Make sure only 1 and 15 are marked not injected
            self.assertEqual(pack[3], i + 1 not in (1, 7, 15))

        # Make sure we're still able to get the original ID
        self.assertEqual(self.circuit.out_injections.get_original_id(15), 3)

    async def test_inject_hole_in_sequence(self):
        self._send_message(Message('ChatFromViewer', packet_id=1))
        self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer', packet_id=4))
        self._send_message(Message('ChatFromViewer'))

        self.assertSequenceEqual(self.circuit.sent_simple, (
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (2, "ChatFromViewer", Direction.OUT, True, ()),
            (5, "ChatFromViewer", Direction.OUT, False, ()),
            (6, "ChatFromViewer", Direction.OUT, True, ()),
        ))

    async def test_inject_misordered(self):
        self._send_message(Message('ChatFromViewer', packet_id=2))
        self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer', packet_id=1))

        self.assertSequenceEqual(self.circuit.sent_simple, [
            (2, "ChatFromViewer", Direction.OUT, False, ()),
            (3, "ChatFromViewer", Direction.OUT, True, ()),
            (1, "ChatFromViewer", Direction.OUT, False, ()),
        ])

    async def test_inject_multiple(self):
        self._send_message(Message('ChatFromViewer', packet_id=1))
        self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer', packet_id=2))
        self._send_message(Message('ChatFromViewer'))

        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (2, "ChatFromViewer", Direction.OUT, True, ()),
            (3, "ChatFromViewer", Direction.OUT, True, ()),
            (4, "ChatFromViewer", Direction.OUT, True, ()),
            (5, "ChatFromViewer", Direction.OUT, False, ()),
            (6, "ChatFromViewer", Direction.OUT, True, ()),
        ])

    async def test_packet_ack_field_converted(self):
        self._send_message(Message('ChatFromViewer', packet_id=1))
        self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer', flags=PacketFlags.RELIABLE))
        self._send_message(Message('ChatFromSimulator', packet_id=1, acks=(2, 3, 4)), outgoing=False)
        self._send_message(Message('ChatFromViewer', packet_id=2, flags=PacketFlags.RELIABLE))
        self._send_message(Message('ChatFromSimulator', packet_id=2, acks=[5]), outgoing=False)
        self._send_message(Message('ChatFromViewer'))

        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (2, "ChatFromViewer", Direction.OUT, True, ()),
            (3, "ChatFromViewer", Direction.OUT, True, ()),
            (4, "ChatFromViewer", Direction.OUT, True, ()),
            # Ack for packet viewer didn't know about should be removed
            (1, "ChatFromSimulator", Direction.IN, False, ()),
            (5, "ChatFromViewer", Direction.OUT, False, ()),
            # Ack for packet viewer did know about should have its ID shifted down
            # to account for injections viewer didn't know about
            (2, "ChatFromSimulator", Direction.IN, False, (2,)),
            (6, "ChatFromViewer", Direction.OUT, True, ()),
        ])

    async def test_packet_ack_proxied_message_converted(self):
        self._send_message(Message('ChatFromViewer', packet_id=1))
        self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer'))
        self._send_message(Message('ChatFromViewer', flags=PacketFlags.RELIABLE))
        self._send_message(
            Message(
                'PacketAck',
                Block('Packets', ID=2),
                Block('Packets', ID=3),
                Block('Packets', ID=4),
                packet_id=1,
            ),
            outgoing=False
        )
        self._send_message(Message('ChatFromViewer', packet_id=2, flags=PacketFlags.RELIABLE))
        self._send_message(
            Message('PacketAck', Block('Packets', ID=5), packet_id=2),
            outgoing=False
        )
        self._send_message(Message('ChatFromViewer'))

        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (2, "ChatFromViewer", Direction.OUT, True, ()),
            (3, "ChatFromViewer", Direction.OUT, True, ()),
            (4, "ChatFromViewer", Direction.OUT, True, ()),
            # Ack for packet viewer didn't know about was dropped, not present
            (5, "ChatFromViewer", Direction.OUT, False, ()),
            # Ack for packet viewer did know about should have its ID shifted down
            # to account for injections viewer didn't know about
            (2, "PacketAck", Direction.IN, False, ()),
            (6, "ChatFromViewer", Direction.OUT, True, ()),
        ])

        self.assertEqual(self.circuit.sent_msgs[5]["Packets"][0]["ID"], 2)

    async def test_drop_proxied_message(self):
        self._send_message(Message('ChatFromViewer', packet_id=1))
        self.circuit.drop_message(Message('ChatFromViewer', packet_id=2, flags=PacketFlags.RELIABLE))
        self._send_message(Message('ChatFromViewer', packet_id=3))

        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (1, "PacketAck", Direction.IN, True, ()),
            (3, "ChatFromViewer", Direction.OUT, False, ()),
        ])
        self.assertEqual(self.circuit.sent_msgs[1]["Packets"][0]["ID"], 2)

    async def test_unreliable_proxied_message(self):
        self._send_message(Message('ChatFromViewer', packet_id=1))
        self.circuit.drop_message(Message('ChatFromViewer', packet_id=2))
        self._send_message(Message('ChatFromViewer', packet_id=3))

        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (3, "ChatFromViewer", Direction.OUT, False, ()),
        ])

    async def test_dropped_proxied_message_acks_sent(self):
        self._send_message(Message('ChatFromViewer', packet_id=1))
        self._send_message(Message('ChatFromViewer', packet_id=2))
        self._send_message(Message('ChatFromViewer', packet_id=3))
        self._send_message(Message('ChatFromSimulator'), outgoing=False)
        self.circuit.drop_message(Message('ChatFromViewer', packet_id=4, acks=(4,)))
        self._send_message(Message('ChatFromViewer', packet_id=5))

        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (2, "ChatFromViewer", Direction.OUT, False, ()),
            (3, "ChatFromViewer", Direction.OUT, False, ()),
            (1, "ChatFromSimulator", Direction.IN, True, ()),
            # PacketAcking embedded acks on message dropping is a
            # special case that will just use the dropped message's ID.
            # If it had no acks we just leave a hole in the message sequence.
            (4, "PacketAck", Direction.OUT, True, ()),
            (5, "ChatFromViewer", Direction.OUT, False, ()),
        ])
        # We injected an incoming packet, so "4" is really "3"
        self.assertEqual(self.circuit.sent_msgs[4]["Packets"][0]["ID"], 3)

    async def test_resending_or_dropping(self):
        self.circuit.send(Message('ChatFromViewer', packet_id=1))
        to_drop = Message('ChatFromViewer', packet_id=2, flags=PacketFlags.RELIABLE)
        self.circuit.drop_message(to_drop)
        with self.assertRaises(RuntimeError):
            # Re-dropping the same message should raise
            self.circuit.drop_message(to_drop)
        # Returns a new message without finalized flag
        new_msg = to_drop.take()
        self.circuit.send(new_msg)
        with self.assertRaises(RuntimeError):
            self.circuit.send(new_msg)
        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (1, "PacketAck", Direction.IN, True, ()),
            # ended up getting the same packet ID when injected
            (2, "ChatFromViewer", Direction.OUT, True, ()),
        ])

    async def test_reliable_unacked_queueing(self):
        self._send_message(Message('ChatFromViewer', flags=PacketFlags.RELIABLE))
        self._send_message(Message('ChatFromViewer', flags=PacketFlags.RELIABLE, packet_id=2))
        # Only the first, injected message should be queued for resends
        self.assertEqual({(Direction.OUT, 1)}, set(self.circuit.unacked_reliable))

    async def test_reliable_resend_cadence(self):
        self._send_message(Message('ChatFromViewer', flags=PacketFlags.RELIABLE))
        resend_info = self.circuit.unacked_reliable[(Direction.OUT, 1)]
        self.circuit.resend_unacked()
        # Should have been too soon to retry
        self.assertEqual(10, resend_info.tries_left)
        # Switch to allowing resends every 0s
        self.circuit.resend_every = 0.0
        self.circuit.resend_unacked()
        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, True, ()),
            # Should have resent
            (1, "ChatFromViewer", Direction.OUT, True, ()),
        ])
        self.assertEqual(9, resend_info.tries_left)
        for _ in range(resend_info.tries_left):
            self.circuit.resend_unacked()
        # Should have used up all the retry attempts and been kicked out of the retry queue
        self.assertEqual(set(), set(self.circuit.unacked_reliable))

    async def test_reliable_ack_collection(self):
        msg = Message('ChatFromViewer', flags=PacketFlags.RELIABLE)
        fut = self.circuit.send_reliable(msg)
        self.assertEqual(1, len(self.circuit.unacked_reliable))
        # Shouldn't count, this is an ACK going in the wrong direction!
        ack_msg = Message("PacketAck", Block("Packets", ID=msg.packet_id))
        self.circuit.collect_acks(ack_msg)
        self.assertEqual(1, len(self.circuit.unacked_reliable))
        self.assertFalse(fut.done())
        # But it should count if the ACK message is heading in
        ack_msg.direction = Direction.IN
        self.circuit.collect_acks(ack_msg)
        self.assertEqual(0, len(self.circuit.unacked_reliable))
        self.assertTrue(fut.done())

    async def test_start_ping_check(self):
        # Should not break if no unacked
        self._send_message(Message(
            "StartPingCheck",
            Block("PingID", PingID=0, OldestUnacked=20),
            packet_id=5,
        ))

        injected_msg = Message('ChatFromViewer', flags=PacketFlags.RELIABLE)
        self._send_message(injected_msg)

        self._send_message(Message(
            "StartPingCheck",
            Block("PingID", PingID=0, OldestUnacked=20),
            packet_id=8,
        ))
        # Oldest unacked should have been replaced with the injected packet's ID, it's older!
        self.assertEqual(self.circuit.sent_msgs[2]["PingID"]["OldestUnacked"], injected_msg.packet_id)
