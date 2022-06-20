import asyncio
import unittest
from typing import Any, Optional, List, Tuple

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer
from hippolyzer.lib.base.network.transport import UDPPacket, AbstractUDPTransport, ADDR_TUPLE
from hippolyzer.lib.proxy.lludp_proxy import InterceptingLLUDPProxyProtocol
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import SessionManager
from hippolyzer.lib.proxy.settings import ProxySettings
from hippolyzer.lib.proxy.transport import SOCKS5UDPTransport


class BaseProxyTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client_addr = ("127.0.0.1", 1)
        self.region_addr = ("127.0.0.1", 3)
        self.circuit_code = 1234
        self.session_manager = SessionManager(ProxySettings())
        self.session = self.session_manager.create_session({
            "session_id": UUID.random(),
            "secure_session_id": UUID.random(),
            "agent_id": UUID.random(),
            "circuit_code": self.circuit_code,
            "sim_ip": self.region_addr[0],
            "sim_port": self.region_addr[1],
            "region_x": 0,
            "region_y": 123,
            "seed_capability": "https://test.localhost:4/foo",
        })
        self.transport = MockTransport()
        self.protocol = InterceptingLLUDPProxyProtocol(
            self.client_addr, self.session_manager)
        self.protocol.transport = self.transport
        self.serializer = UDPMessageSerializer()
        self.session.objects.track_region_objects(123)

    def tearDown(self) -> None:
        self.protocol.close()

    async def _wait_drained(self):
        await asyncio.sleep(0.001)

    def _setup_default_circuit(self):
        self._setup_region_circuit(self.session.regions[-1])
        self.session.main_region = self.session.regions[-1]

    def _setup_region_circuit(self, region: ProxiedRegion):
        # Not going to send a UseCircuitCode, so have to pretend we already did the
        # client -> region NAT hole-punching
        self.protocol.session = self.session
        self.protocol.far_to_near_map[region.circuit_addr] = self.client_addr
        self.session_manager.claim_session(self.session.id)
        self.session.open_circuit(self.client_addr, region.circuit_addr,
                                  self.protocol.transport)

    def _msg_to_packet(self, msg: Message, src, dst) -> UDPPacket:
        return UDPPacket(src_addr=src, dst_addr=dst, data=self.serializer.serialize(msg),
                         direction=msg.direction)

    def _msg_to_datagram(self, msg: Message, src, dst, socks_header=True):
        packet = self._msg_to_packet(msg, src, dst)
        return SOCKS5UDPTransport.serialize(packet, force_socks_header=socks_header)


class MockTransport(AbstractUDPTransport):
    def sendto(self, data: Any, addr: Optional[ADDR_TUPLE] = ...) -> None:
        pass

    def abort(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __init__(self):
        super().__init__()
        self.packets: List[Tuple[bytes, Tuple[str, int]]] = []

    def send_packet(self, packet: UDPPacket) -> None:
        self.packets.append((packet.data, packet.dst_addr))
