from __future__ import annotations

import itertools
import random
import struct
import unittest
from typing import *

import lazy_object_proxy

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.message_logger import FilteringMessageLogger, LLUDPMessageLogEntry
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session
from hippolyzer.lib.proxy.test_utils import BaseProxyTest


UNKNOWN_PACKET = b'\x00\x00\x00\x00E\x00\xff\xf0\x00\xff\xff\xff\xff\x00'


class MockAddon(BaseAddon):
    def __init__(self):
        self.events = []

    def handle_session_init(self, session: Session):
        self.events.append(("session_init", session.id))

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        self.events.append(("lludp", session.id, region.circuit_addr, message.name))
        if message.name == "UndoLand":
            # Simulate a message being taken out of the regular proxying flow
            message.take()
            return True

    def handle_object_updated(self, session: Session, region: ProxiedRegion,
                              obj: Object, updated_props: Set[str], msg: Optional[Message]):
        self.events.append(("object_update", session.id, region.circuit_addr, obj.LocalID, updated_props))


class SimpleMessageLogger(FilteringMessageLogger):
    @property
    def entries(self):
        return self._filtered_entries


class LLUDPIntegrationTests(BaseProxyTest):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.addon = MockAddon()
        self.deserializer = UDPMessageDeserializer()
        AddonManager.init([], self.session_manager, [self.addon])

    def _make_objectupdate_compressed(self, localid: Optional[int] = None, handle: Optional[int] = 123):
        if localid is None:
            localid = random.getrandbits(32)

        return b'\x00\x00\x00\x0c\xba\x00\r' + struct.pack("<Q", handle) + b'\xff\xff\x03\xd0\x04\x00\x10' \
               b'\xe6\x00\x12\x12\x10\xbf\x16XB~\x8f\xb4\xfb\x00\x1a\xcd\x9b\xe5' + struct.pack("<I", localid) + \
               b'\t\x00\xcdG\x00\x00\x03\x00\x00\x00\x1cB\x00\x00\x1cB\xcd\xcc\xcc=\xedG,' \
               b'B\x9e\xb1\x9eBff\xa0A\x00\x00\x00\x00\x00\x00\x00\x00[' \
               b'\x8b\xf8\xbe\xc0\x00\x00\x00k\x9b\xc4\xfe3\nOa\xbb\xe2\xe4\xb2C\xac7\xbd\x00\x00\x00\x00\x00' \
               b'\x00\x00\x00\x00\x00\xa2=\x010\x00\x11\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed' \
               b'\x15F_@ \x00\x00\x00\x00d\x96\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
               b'\x00?\x00\x00\x00\x1c\x9fJoI\x8dH\xa0\x9d\xc4&\'\'\x19=g\x00\x00\x00\x003\x00ff\x86\xbf' \
               b'\x00ff\x86?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x89UgG$\xcbC' \
               b'\xed\x92\x0bG\xca\xed\x15F_\x10\x00\x00\x003\x00\x01\x01\x00\x00\x00\x00\xdb\x0f\xc9@\xa6' \
               b'\x9b\xc4=\xd0\x04\x00\x10\xe6\x00\xc2\xa62\xe2\x9b\xd7L\xc4\xbb\xd6\x1fKC\xa6\xdf\x8d\\\x04\x00' \
               b'\x00\t\x00\xd3G\x00\x00\x03\x00\x00\x00\x1cB\x00\x00\x1cB\xcd\xcc\xcc=\t\x08\x9cA\xf2\x03' \
               b'\xa5Bff\xa0A\x00\x00\x00\x00\x00\x00\x00\x00[\x8b\xf8' \
               b'\xbe\xc0\x00\x00\x00\x0b\x1b\xa0\xd1\x97=C\xcd\xae\x19\xfd\xc9\xbb\x88\x05\xc3\x00\x00\x00\x00\x00' \
               b'\x00\x00\x00\x00\x00\xa2=\x010\x00\x11\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed' \
               b'\x15F_@ \x00\x00\x00\x00d\x96\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
               b'\x00?\x00\x00\x00\xbd\x8b\xd7h{\xdbM\xbc\x8c3X\xa6\xa6\x0c\x94\xd7\x00\x00\x00\x003\x00ff\x86\xbf' \
               b'\x00ff\x86?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x89UgG$\xcbC' \
               b'\xed\x92\x0bG\xca\xed\x15F_\x10\x00\x00\x003\x00\x01\x01\x00\x00\x00\x00\xdb\x0f\xc9@\xa6' \
               b'\x9b\xc4=\xd0\x04\x00\x10\xe6\x00\xd1e\xac\xff,NBK\x91d\xbb\x15\\\x0b\xc3\x9c\xe2\x05\x00\x00' \
               b'\t\x00\xbbG\x00\x00\x03\x00\x00\x00\x1cB\x00\x00\x1cB\xcd\xcc\xcc=\x0f5\x97AY\x98ZBff' \
               b'\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\xe6Y0\xbf\xc0\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG' \
               b'\xca\xed\x15F_\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa2=\x010\x00\x11\x00\x00\x00' \
               b'#\xce\xf8\xf4\x0cJD.\xb7"\x96\x1cK\xd9\x01\x1b@ ' \
               b'\x00\x00\x00\x00d\x96\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
               b'?\x00\x00\x003\xe1\xa1\xcf<\xbdD\xc4\xa0\xe6b\xe9\xbf=\xa2@\x00\x00\x00\x003\x00ff\x86\xbf' \
               b'\x00ff\x86?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x89UgG$\xcbC' \
               b'\xed\x92\x0bG\xca\xed\x15F_\x10\x00\x00\x003\x00\x01\x01\x00\x00\x00\x00\xdb\x0f\xc9@\xa6' \
               b'\x9b\xc4='

    async def test_session_claiming(self):
        # Need a UseCircuitCode to claim a pending session
        msg = Message(
            "UseCircuitCode",
            Block("CircuitCode", Code=self.circuit_code, SessionID=self.session.id,
                  ID=self.session.agent_id),
            packet_id=1,
        )
        datagram = self._msg_to_datagram(msg, self.client_addr, self.region_addr,
                                         socks_header=True)
        self.protocol.datagram_received(datagram, self.client_addr)
        await self._wait_drained()
        self.assertFalse(self.session.pending)
        # session should now be tied to the protocol
        self.assertEqual(self.session, self.protocol.session)
        # Packet got forwarded through
        self.assertEqual(len(self.transport.packets), 1)

    async def test_bad_session_unclaimed(self):
        # Need a UseCircuitCode to claim a pending session
        msg = Message(
            "UseCircuitCode",
            Block("CircuitCode", Code=self.circuit_code, SessionID=UUID.random(),
                  ID=self.session.agent_id),
            packet_id=1,
        )
        datagram = self._msg_to_datagram(msg, self.client_addr, self.region_addr,
                                         socks_header=True)
        self.protocol.datagram_received(datagram, source_addr=self.client_addr)
        await self._wait_drained()
        # Packet got dropped completely
        self.assertTrue(self.session.pending)
        self.assertIsNone(self.protocol.session)
        self.assertEqual(len(self.transport.packets), 0)

    async def test_bad_circuit_not_sent(self):
        # Need a UseCircuitCode to claim a pending session
        msg = Message(
            "UseCircuitCode",
            Block("CircuitCode", Code=self.circuit_code, SessionID=self.session.id,
                  ID=self.session.agent_id),
            packet_id=1,
        )
        datagram = self._msg_to_datagram(msg, self.client_addr, (self.region_addr[0], 9),
                                         socks_header=True)
        self.protocol.datagram_received(datagram, source_addr=self.client_addr)
        await self._wait_drained()
        # The session claim will still work
        self.assertFalse(self.session.pending)
        self.assertEqual(self.session, self.protocol.session)
        # Packet should not get sent, though and should not be handled
        self.assertEqual(len(self.transport.packets), 0)

    @unittest.skip("expensive")
    async def test_benchmark(self):
        num_times = 10_000
        self._setup_default_circuit()
        for _ in range(num_times):
            self.protocol.datagram_received(self._make_objectupdate_compressed(), self.region_addr)
        await self._wait_drained()
        self.assertEqual(len(self.transport.packets), num_times)

    async def test_forwarded_with_header(self):
        self._setup_default_circuit()
        obj_update = self._make_objectupdate_compressed()
        self.protocol.datagram_received(obj_update, self.region_addr)
        await self._wait_drained()
        packets = self.transport.packets
        self.assertEqual(len(packets), 1)
        data, dst_addr = packets[0]
        # Was being sent towards the client
        self.assertEqual(dst_addr, self.client_addr)
        # The data should not have changed since we haven't injected
        # or dropped anything
        self.assertEqual(obj_update, data)

    async def test_addon_hooks(self):
        self._setup_default_circuit()
        obj_update = self._make_objectupdate_compressed()
        self.protocol.datagram_received(obj_update, self.region_addr)
        await self._wait_drained()
        expected_lludp_event = ("lludp", self.session.id, self.region_addr, "ObjectUpdateCompressed")
        self.assertTrue(any(x == expected_lludp_event for x in self.addon.events))

    async def test_object_added_with_tes(self):
        self._setup_default_circuit()
        obj_update = self._make_objectupdate_compressed(1234)
        self.protocol.datagram_received(obj_update, self.region_addr)
        await self._wait_drained()
        obj = self.session.regions[0].objects.lookup_localid(1234)
        self.assertIsInstance(obj.TextureEntry, lazy_object_proxy.Proxy)
        self.assertEqual(obj.TextureEntry.Textures[None], UUID("1c9f4a6f-498d-48a0-9dc4-262727193d67"))
        self.assertEqual(len(self.session.regions[0].objects), 3)

    async def test_object_updated_changed_property_list(self):
        self._setup_default_circuit()
        # One creating update and one no-op update
        obj_update = self._make_objectupdate_compressed(1234)
        self.protocol.datagram_received(obj_update, self.region_addr)
        obj_update = self._make_objectupdate_compressed(1234)
        self.protocol.datagram_received(obj_update, self.region_addr)
        await self._wait_drained()
        self.assertEqual(3, len(self.session.regions[0].objects))
        object_events = [e for e in self.addon.events if e[0] == "object_update"]
        # 3 objects in example packet and we sent it twice
        self.assertEqual(6, len(object_events))
        # Only TextureEntry should be marked updated since it's a proxy object
        self.assertEqual(object_events[-1][-1], {"TextureEntry"})

    async def test_message_logger(self):
        message_logger = SimpleMessageLogger()
        self.session_manager.message_logger = message_logger
        self._setup_default_circuit()
        obj_update = self._make_objectupdate_compressed(1234)
        self.protocol.datagram_received(obj_update, self.region_addr)
        await self._wait_drained()
        entries = message_logger.entries
        self.assertEqual(1, len(entries))
        self.assertEqual("ObjectUpdateCompressed", entries[0].name)

    async def test_filtering_logged_messages(self):
        message_logger = SimpleMessageLogger()
        self.session_manager.message_logger = message_logger
        self._setup_default_circuit()
        obj_update = self._make_objectupdate_compressed(1234)
        self.protocol.datagram_received(obj_update, self.region_addr)
        msg = self.serializer.serialize(Message(
            "UndoLand",
            Block("AgentData", AgentID=UUID(), SessionID=UUID()),
            direction=Direction.IN,
        ))
        self.protocol.datagram_received(msg, self.region_addr)
        await self._wait_drained()
        message_logger.set_filter("ObjectUpdateCompressed")
        entries = message_logger.entries
        self.assertEqual(1, len(entries))
        self.assertEqual("ObjectUpdateCompressed", entries[0].name)

    async def test_logging_taken_message(self):
        message_logger = SimpleMessageLogger()
        self.session_manager.message_logger = message_logger
        self._setup_default_circuit()
        msg = self.serializer.serialize(Message(
            "UndoLand",
            Block("AgentData", AgentID=UUID(), SessionID=UUID()),
            direction=Direction.IN,
        ))
        self.protocol.datagram_received(msg, self.region_addr)
        await self._wait_drained()
        entries = message_logger.entries
        self.assertEqual(len(entries), 1)
        entry: LLUDPMessageLogEntry = entries[0]  # type: ignore
        self.assertEqual(entry.name, "UndoLand")
        self.assertEqual(entry.message.dropped, True)

    async def test_logging_unknown_message(self):
        message_logger = SimpleMessageLogger()
        self.session_manager.message_logger = message_logger
        self._setup_default_circuit()
        self.protocol.datagram_received(UNKNOWN_PACKET, self.region_addr)
        await self._wait_drained()
        entries = message_logger.entries
        self.assertEqual(len(entries), 1)
        entry: LLUDPMessageLogEntry = entries[0]  # type: ignore
        # Freezing shouldn't affect this
        entry.freeze()
        self.assertEqual(entry.name, "UnknownMessage:240")
        self.assertEqual(entry.message.dropped, False)
        self.assertEqual(entry.message.unknown_message, True)

    async def test_session_message_handler(self):
        self._setup_default_circuit()
        obj_update = self._make_objectupdate_compressed(1234)
        fut = self.session.message_handler.wait_for(('ObjectUpdateCompressed',))
        self.protocol.datagram_received(obj_update, self.region_addr)
        self.assertEqual("ObjectUpdateCompressed", (await fut).name)

    def test_roundtrip_objectupdatecompressed(self):
        msg_bytes = self._make_objectupdate_compressed()
        message: Message = self.deserializer.deserialize(msg_bytes)
        for block in itertools.chain(*message.blocks.values()):
            for var_name in block.vars.keys():
                orig_val = block[var_name]
                try:
                    serializer = block.get_serializer(var_name)
                except KeyError:
                    # Don't have a serializer, onto the next field
                    continue
                deser = serializer.deserialize(block, orig_val)
                new_val = serializer.serialize(block, deser)
                if orig_val != new_val:
                    raise AssertionError(f"{block.name}.{var_name} didn't reserialize correctly,"
                                         f"{orig_val!r} != {new_val!r}")
        new_msg_bytes = self.serializer.serialize(message)
        self.assertEqual(new_msg_bytes, msg_bytes)
