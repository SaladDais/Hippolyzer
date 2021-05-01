from __future__ import annotations

import random
import struct
from typing import *
import unittest

import lazy_object_proxy

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.packets import ProxiedUDPPacket, Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session

from . import BaseIntegrationTest


class MockAddon(BaseAddon):
    def __init__(self):
        self.events = []

    def handle_session_init(self, session: Session):
        self.events.append(("session_init", session.id))

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: ProxiedMessage):
        self.events.append(("lludp", session.id, region.circuit_addr, message.name))

    def handle_object_updated(self, session: Session, region: ProxiedRegion,
                              obj: Object, updated_props: Set[str]):
        self.events.append(("object_update", session.id, region.circuit_addr, obj.LocalID))


class LLUDPIntegrationTests(BaseIntegrationTest):
    def setUp(self) -> None:
        super().setUp()
        self.addon = MockAddon()
        AddonManager.init([], self.session_manager, [self.addon])

    def _make_objectupdate_compressed(self, localid: Optional[int] = None):
        if localid is None:
            localid = random.getrandbits(32)

        return b'\x00\x00\x00\x0c\xba\x00\r\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x03\xd0\x04\x00\x10' \
               b'\xe6\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_' + struct.pack("<I", localid) + \
               b'\t\x00\xcdG\x00\x00\x03\x00\x00\x00\x1cB\x00\x00\x1cB\xcd\xcc\xcc=\xedG,' \
               b'B\x9e\xb1\x9eBff\xa0A\x00\x00\x00\x00\x00\x00\x00\x00[' \
               b'\x8b\xf8\xbe\xc0\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_\x00\x00\x00\x00\x00' \
               b'\x00\x00\x00\x00\x00\xa2=\x010\x00\x11\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed' \
               b'\x15F_@ \x00\x00\x00\x00d\x96\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
               b'\x00?\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_\x00\x00\x00\x003\x00ff\x86\xbf' \
               b'\x00ff\x86?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x89UgG$\xcbC' \
               b'\xed\x92\x0bG\xca\xed\x15F_\x10\x00\x00\x003\x00\x01\x01\x00\x00\x00\x00\xdb\x0f\xc9@\xa6' \
               b'\x9b\xc4=\xd0\x04\x00\x10\xe6\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_\\\x04\x00\x00\t' \
               b'\x00\xd3G\x00\x00\x03\x00\x00\x00\x1cB\x00\x00\x1cB\xcd\xcc\xcc=\t\x08\x9cA\xf2\x03' \
               b'\xa5Bff\xa0A\x00\x00\x00\x00\x00\x00\x00\x00[' \
               b'\x8b\xf8\xbe\xc0\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_\x00\x00\x00\x00\x00' \
               b'\x00\x00\x00\x00\x00\xa2=\x010\x00\x11\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed' \
               b'\x15F_@ \x00\x00\x00\x00d\x96\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
               b'\x00?\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_\x00\x00\x00\x003\x00ff\x86\xbf' \
               b'\x00ff\x86?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x89UgG$\xcbC' \
               b'\xed\x92\x0bG\xca\xed\x15F_\x10\x00\x00\x003\x00\x01\x01\x00\x00\x00\x00\xdb\x0f\xc9@\xa6' \
               b'\x9b\xc4=\xd0\x04\x00\x10\xe6\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_\xe2\x05\x00\x00' \
               b'\t\x00\xbbG\x00\x00\x03\x00\x00\x00\x1cB\x00\x00\x1cB\xcd\xcc\xcc=\x0f5\x97AY\x98ZBff' \
               b'\xa0A\x00\x00\x00\x00\x00\x00\x00\x00\xe6Y0\xbf\xc0\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG' \
               b'\xca\xed\x15F_\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa2=\x010\x00\x11\x00\x00\x00' \
               b'\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_@ ' \
               b'\x00\x00\x00\x00d\x96\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
               b'?\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_\x00\x00\x00\x003\x00ff\x86\xbf' \
               b'\x00ff\x86?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x89UgG$\xcbC' \
               b'\xed\x92\x0bG\xca\xed\x15F_\x10\x00\x00\x003\x00\x01\x01\x00\x00\x00\x00\xdb\x0f\xc9@\xa6' \
               b'\x9b\xc4='

    async def test_session_claiming(self):
        # Need a UseCircuitCode to claim a pending session
        msg = ProxiedMessage(
            "UseCircuitCode",
            Block("CircuitCode", Code=self.circuit_code, SessionID=self.session.id,
                  ID=self.session.agent_id),
            packet_id=1,
        )
        datagram = self._msg_to_datagram(msg, self.client_addr, self.region_addr,
                                         Direction.OUT, socks_header=True)
        self.protocol.datagram_received(datagram, self.client_addr)
        await self._wait_drained()
        self.assertFalse(self.session.pending)
        # session should now be tied to the protocol
        self.assertEqual(self.session, self.protocol.session)
        # Packet got forwarded through
        self.assertEqual(len(self.transport.packets), 1)

    async def test_bad_session_unclaimed(self):
        # Need a UseCircuitCode to claim a pending session
        msg = ProxiedMessage(
            "UseCircuitCode",
            Block("CircuitCode", Code=self.circuit_code, SessionID=UUID.random(),
                  ID=self.session.agent_id),
            packet_id=1,
        )
        datagram = self._msg_to_datagram(msg, self.client_addr, self.region_addr,
                                         Direction.OUT, socks_header=True)
        self.protocol.datagram_received(datagram, source_addr=self.client_addr)
        await self._wait_drained()
        # Packet got dropped completely
        self.assertTrue(self.session.pending)
        self.assertIsNone(self.protocol.session)
        self.assertEqual(len(self.transport.packets), 0)

    async def test_bad_circuit_not_sent(self):
        # Need a UseCircuitCode to claim a pending session
        msg = ProxiedMessage(
            "UseCircuitCode",
            Block("CircuitCode", Code=self.circuit_code, SessionID=self.session.id,
                  ID=self.session.agent_id),
            packet_id=1,
        )
        datagram = self._msg_to_datagram(msg, self.client_addr, (self.region_addr[0], 9),
                                         Direction.OUT, socks_header=True)
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
        self._setup_circuit()
        for _ in range(num_times):
            self.protocol.datagram_received(self._make_objectupdate_compressed(), self.region_addr)
        await self._wait_drained()
        self.assertEqual(len(self.transport.packets), num_times)

    async def test_forwarded_with_header(self):
        self._setup_circuit()
        obj_update = self._make_objectupdate_compressed()
        self.protocol.datagram_received(obj_update, self.region_addr)
        await self._wait_drained()
        packets = self.transport.packets
        self.assertEqual(len(packets), 1)
        data, dst_addr = packets[0]
        # Was being sent towards the client
        self.assertEqual(dst_addr, self.client_addr)
        # Which means it has a SOCKS header we need to ignore
        data = data[ProxiedUDPPacket.HEADER_STRUCT.size:]
        # The data should not have changed since we haven't injected
        # or dropped anything
        self.assertEqual(obj_update, data)

    async def test_addon_hooks(self):
        self._setup_circuit()
        obj_update = self._make_objectupdate_compressed()
        self.protocol.datagram_received(obj_update, self.region_addr)
        await self._wait_drained()
        expected_lludp_event = ("lludp", self.session.id, self.region_addr, "ObjectUpdateCompressed")
        self.assertTrue(any(x == expected_lludp_event for x in self.addon.events))

    async def test_object_added_with_tes(self):
        self._setup_circuit()
        obj_update = self._make_objectupdate_compressed(1234)
        self.protocol.datagram_received(obj_update, self.region_addr)
        await self._wait_drained()
        obj = self.session.regions[0].objects.lookup_localid(1234)
        self.assertIsInstance(obj.TextureEntry, lazy_object_proxy.Proxy)
        self.assertEqual(obj.TextureEntry.Textures[None], UUID("89556747-24cb-43ed-920b-47caed15465f"))