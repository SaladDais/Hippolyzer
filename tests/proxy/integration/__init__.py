import asyncio
from typing import *
import unittest

from hippolyzer.lib.base.datatypes import *
from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer
from hippolyzer.lib.proxy.lludp_proxy import InterceptingLLUDPProxyProtocol
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.packets import ProxiedUDPPacket
from hippolyzer.lib.proxy.sessions import SessionManager


class MockTransport(asyncio.DatagramTransport):
    def __init__(self):
        super().__init__()
        self.packets: List[Tuple[bytes, Tuple[str, int]]] = []

    def sendto(self, data: Any, addr=None) -> None:
        self.packets.append((data, addr))


class BaseIntegrationTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.client_addr = ("127.0.0.1", 1)
        self.region_addr = ("127.0.0.1", 3)
        self.circuit_code = 1234
        self.session_manager = SessionManager()
        self.session = self.session_manager.create_session({
            "session_id": UUID.random(),
            "secure_session_id": UUID.random(),
            "agent_id": UUID.random(),
            "circuit_code": self.circuit_code,
            "sim_ip": self.region_addr[0],
            "sim_port": self.region_addr[1],
            "region_x": 1,
            "region_y": 2,
            "seed_capability": "https://test.localhost:4/foo",
        })
        self.transport = MockTransport()
        self.protocol = InterceptingLLUDPProxyProtocol(
            self.client_addr, self.session_manager)
        self.protocol.transport = self.transport
        self.serializer = UDPMessageSerializer()

    async def _wait_drained(self):
        await asyncio.sleep(0.001)

    def _setup_circuit(self):
        # Not going to send a UseCircuitCode, so have to pretend we already did the
        # client -> region NAT hole-punching
        self.protocol.session = self.session
        self.protocol.far_to_near_map[self.region_addr] = self.client_addr
        self.session_manager.claim_session(self.session.id)
        self.session.open_circuit(self.client_addr, self.region_addr,
                                  self.protocol.transport)
        self.session.main_region = self.session.regions[-1]
        self.session.main_region.handle = 0

    def _msg_to_datagram(self, msg: ProxiedMessage, src, dst, direction, socks_header=True):
        serialized = self.serializer.serialize(msg)
        packet = ProxiedUDPPacket(src_addr=src, dst_addr=dst, data=serialized,
                                  direction=direction)
        return packet.serialize(socks_header=socks_header)
