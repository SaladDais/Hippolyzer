import unittest
import uuid

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.message.msgtypes import PacketFlags
from hippolyzer.lib.proxy.circuit import ProxiedCircuit, InjectionTracker
from hippolyzer.lib.proxy.packets import Direction
from hippolyzer.lib.proxy.message import ProxiedMessage


class MockedProxyCircuit(ProxiedCircuit):
    def __init__(self):
        super().__init__(("127.0.0.1", 0), ("0.0.0.0", 0), None)
        self.sent_simple = []
        self.sent_msgs = []
        # Use a small maxlen to test what happens when injected
        # IDs get evicted from the deque
        self.out_injections = InjectionTracker(0, maxlen=10)
        self.in_injections = InjectionTracker(0, maxlen=10)

    def _send_prepared_message(self, msg: ProxiedMessage, direction, transport=None):
        self.sent_simple.append((msg.packet_id, msg.name, direction, msg.injected, msg.acks))
        self.sent_msgs.append(msg)


class PacketIDTests(unittest.TestCase):
    def setUp(self) -> None:
        self.circuit = MockedProxyCircuit()

    def _send_message(self, msg, outgoing=True):
        direction = Direction.OUT if outgoing else Direction.IN
        return self.circuit.send_message(msg, direction)

    def test_basic(self):
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=1))
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=2))

        self.assertSequenceEqual(self.circuit.sent_simple, (
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (2, "ChatFromViewer", Direction.OUT, False, ()),
        ))

    def test_inject(self):
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=1))
        self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=2))

        self.assertSequenceEqual(self.circuit.sent_simple, (
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (2, "ChatFromViewer", Direction.OUT, True, ()),
            (3, "ChatFromViewer", Direction.OUT, False, ()),
        ))

    def test_max_injected(self):
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=1))
        for _ in range(5):
            self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=2))

        self.assertEqual(self.circuit.out_injections.get_original_id(1), 1)
        self.assertEqual(self.circuit.out_injections.get_original_id(7), 2)

        for _ in range(7):
            self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=3))

        self.assertEqual(len(self.circuit.sent_simple), 15)

        for i in range(15):
            pack = self.circuit.sent_simple[i]
            # Check that the sequence nums match what we'd expect
            self.assertEqual(pack[0], i + 1)
            # Make sure only 1 and 15 are marked not injected
            self.assertEqual(pack[3], i + 1 not in (1, 7, 15))

        # Make sure we're still able to get the original ID
        self.assertEqual(self.circuit.out_injections.get_original_id(15), 3)

    def test_inject_hole_in_sequence(self):
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=1))
        self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=4))
        self._send_message(ProxiedMessage('ChatFromViewer'))

        self.assertSequenceEqual(self.circuit.sent_simple, (
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (2, "ChatFromViewer", Direction.OUT, True, ()),
            (5, "ChatFromViewer", Direction.OUT, False, ()),
            (6, "ChatFromViewer", Direction.OUT, True, ()),
        ))

    def test_inject_misordered(self):
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=2))
        self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=1))

        self.assertSequenceEqual(self.circuit.sent_simple, [
            (2, "ChatFromViewer", Direction.OUT, False, ()),
            (3, "ChatFromViewer", Direction.OUT, True, ()),
            (1, "ChatFromViewer", Direction.OUT, False, ()),
        ])

    def test_inject_multiple(self):
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=1))
        self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=2))
        self._send_message(ProxiedMessage('ChatFromViewer'))

        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (2, "ChatFromViewer", Direction.OUT, True, ()),
            (3, "ChatFromViewer", Direction.OUT, True, ()),
            (4, "ChatFromViewer", Direction.OUT, True, ()),
            (5, "ChatFromViewer", Direction.OUT, False, ()),
            (6, "ChatFromViewer", Direction.OUT, True, ()),
        ])

    def test_packet_ack_field_converted(self):
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=1))
        self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer', flags=PacketFlags.RELIABLE))
        self._send_message(ProxiedMessage('ChatFromSimulator', packet_id=1, acks=(2, 3, 4)), outgoing=False)
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=2, flags=PacketFlags.RELIABLE))
        self._send_message(ProxiedMessage('ChatFromSimulator', packet_id=2, acks=[5]), outgoing=False)
        self._send_message(ProxiedMessage('ChatFromViewer'))

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

    def test_packet_ack_proxied_message_converted(self):
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=1))
        self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer'))
        self._send_message(ProxiedMessage('ChatFromViewer', flags=PacketFlags.RELIABLE))
        self._send_message(
            ProxiedMessage(
                'PacketAck',
                Block('Packets', ID=2),
                Block('Packets', ID=3),
                Block('Packets', ID=4),
                packet_id=1,
            ),
            outgoing=False
        )
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=2, flags=PacketFlags.RELIABLE))
        self._send_message(
            ProxiedMessage('PacketAck', Block('Packets', ID=5), packet_id=2),
            outgoing=False
        )
        self._send_message(ProxiedMessage('ChatFromViewer'))

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

    def test_drop_proxied_message(self):
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=1))
        self.circuit.drop_message(
            ProxiedMessage('ChatFromViewer', packet_id=2, flags=PacketFlags.RELIABLE),
            Direction.OUT,
        )
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=3))

        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (1, "PacketAck", Direction.IN, True, ()),
            (3, "ChatFromViewer", Direction.OUT, False, ()),
        ])
        self.assertEqual(self.circuit.sent_msgs[1]["Packets"][0]["ID"], 2)

    def test_unreliable_proxied_message(self):
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=1))
        self.circuit.drop_message(
            ProxiedMessage('ChatFromViewer', packet_id=2),
            Direction.OUT,
        )
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=3))

        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (3, "ChatFromViewer", Direction.OUT, False, ()),
        ])

    def test_dropped_proxied_message_acks_sent(self):
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=1))
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=2))
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=3))
        self._send_message(ProxiedMessage('ChatFromSimulator'), outgoing=False)
        self.circuit.drop_message(
            ProxiedMessage('ChatFromViewer', packet_id=4, acks=(4,)),
            Direction.OUT,
        )
        self._send_message(ProxiedMessage('ChatFromViewer', packet_id=5))

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

    def test_resending_or_dropping(self):
        self.circuit.send_message(ProxiedMessage('ChatFromViewer', packet_id=1))
        to_drop = ProxiedMessage('ChatFromViewer', packet_id=2, flags=PacketFlags.RELIABLE)
        self.circuit.drop_message(to_drop, Direction.OUT)
        with self.assertRaises(RuntimeError):
            # Re-dropping the same message should raise
            self.circuit.drop_message(to_drop, Direction.OUT)
        # Clears finalized flag
        to_drop.packet_id = None
        self.circuit.send_message(to_drop, Direction.OUT)
        with self.assertRaises(RuntimeError):
            self.circuit.send_message(to_drop, Direction.OUT)
        self.assertSequenceEqual(self.circuit.sent_simple, [
            (1, "ChatFromViewer", Direction.OUT, False, ()),
            (1, "PacketAck", Direction.IN, True, ()),
            # ended up getting the same packet ID when injected
            (2, "ChatFromViewer", Direction.OUT, True, ()),
        ])


class HumanReadableMessageTests(unittest.TestCase):
    def test_basic(self):
        val = """
        OUT FooMessage
        [SomeBlock]
        # IGNORE ME
        SomeFloat = 1.0
        SomeStr = "baz"
        SomeVec = <1,1,1>
        [OtherBlock]
        UUID = 1f4ffb55-022e-49fb-8c63-6f159aed9b24
        """

        msg = ProxiedMessage.from_human_string(val)
        self.assertEqual(msg.name, "FooMessage")
        self.assertEqual(set(msg.blocks.keys()), {"SomeBlock", "OtherBlock"})
        self.assertSequenceEqual(msg["SomeBlock"][0]["SomeVec"], (1.0, 1.0, 1.0))
        self.assertEqual(msg["OtherBlock"][0]["UUID"], uuid.UUID("1f4ffb55-022e-49fb-8c63-6f159aed9b24"))

    def test_eval_allowed(self):
        val = """
        OUT FooMessage
        [SomeBlock]
        evaled =$ 1+1
        """

        msg = ProxiedMessage.from_human_string(val, safe=False)
        self.assertEqual(msg["SomeBlock"][0]["evaled"], 2)

    def test_eval_disallowed(self):
        val = """
        OUT FooMessage
        [SomeBlock]
        evaled =$ 1+1
        """

        with self.assertRaises(ValueError):
            ProxiedMessage.from_human_string(val)


class TestMessageSubfieldSerializers(unittest.TestCase):
    def setUp(self):
        self.chat_msg = ProxiedMessage(
            'ChatFromViewer',
            Block('AgentData',
                  AgentID=UUID('550e8400-e29b-41d4-a716-446655440000'),
                  SessionID=UUID('550e8400-e29b-41d4-a716-446655440000')),
            Block('ChatData', Message="Chatting\n", Type=1, Channel=0))

    def test_pretty_repr(self):
        expected_repr = r"""ProxiedMessage('ChatFromViewer',
  Block('AgentData', AgentID=UUID('550e8400-e29b-41d4-a716-446655440000'), SessionID=UUID('550e8400-e29b-41d4-a716-446655440000')),
  Block('ChatData', Message='Chatting\n', Type_=ChatType.NORMAL, Channel=0), direction=Direction.OUT)"""
        self.assertEqual(expected_repr, self.chat_msg.repr(pretty=True))
