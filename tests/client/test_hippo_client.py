import asyncio
import copy
import unittest
import xmlrpc.client
from typing import Tuple, Optional

import aioresponses

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.circuit import Circuit
from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.network.transport import AbstractUDPTransport, UDPPacket, Direction
from hippolyzer.lib.base.test_utils import MockTransport, MockConnectionHolder
from hippolyzer.lib.client.hippo_client import HippoClient, HippoClientProtocol


class MockServer(MockConnectionHolder):
    def __init__(self, circuit, message_handler):
        super().__init__(circuit, message_handler)
        self.deserializer = UDPMessageDeserializer()
        self.protocol: Optional[HippoClientProtocol] = None

    def process_inbound(self, packet: UDPPacket):
        """Process a packet that the client sent to us"""
        message = self.deserializer.deserialize(packet.data)
        message.direction = Direction.IN
        if message.reliable:
            self.circuit.send_acks((message.packet_id,))
        self.circuit.collect_acks(message)
        if message.name != "PacketAck":
            self.message_handler.handle(message)


class PacketForwardingTransport(MockTransport):
    def __init__(self):
        super().__init__()
        self.protocol: Optional[HippoClientProtocol] = None

    def send_packet(self, packet: UDPPacket):
        super().send_packet(packet)
        self.protocol.datagram_received(packet.data, packet.src_addr)


class MockServerTransport(MockTransport):
    """Used for the client to send packets out"""
    def __init__(self, server: MockServer):
        super().__init__()
        self._server = server

    def send_packet(self, packet: UDPPacket) -> None:
        super().send_packet(packet)
        # Directly pass the packet to the server
        packet = copy.copy(packet)
        packet.direction = Direction.IN
        # Delay calling so the client can do its ACK bookkeeping first
        asyncio.get_event_loop_policy().get_event_loop().call_soon(lambda: self._server.process_inbound(packet))


class MockHippoClient(HippoClient):
    def __init__(self, server: MockServer):
        super().__init__()
        self.server = server

    async def _create_transport(self) -> Tuple[AbstractUDPTransport, HippoClientProtocol]:
        protocol = HippoClientProtocol(self.session)
        # TODO: This isn't great, but whatever.
        self.server.circuit.transport.protocol = protocol
        return MockServerTransport(self.server), protocol


async def _soon(get_msg) -> Message:
    return await asyncio.wait_for(get_msg(), timeout=1.0)


class TestHippoClient(unittest.IsolatedAsyncioTestCase):
    FAKE_LOGIN_URI = "http://127.0.0.1:1/login.cgi"
    FAKE_LOGIN_RESP = {
        "session_id": str(UUID(int=1)),
        "secure_session_id": str(UUID(int=2)),
        "agent_id": str(UUID(int=3)),
        "circuit_code": 123,
        "sim_ip": "127.0.0.1",
        "sim_port": 2,
        "region_x": 0,
        "region_y": 123,
        "seed_capability": "https://127.0.0.1:4/foo",
    }
    FAKE_SEED_RESP = {
        "EventQueueGet": "https://127.0.0.1:5/",
    }
    FAKE_EQ_RESP = {
        "id": 1,
        "events": [{"message": "ViewerFrozenMessage", "body": {"FrozenData": [{"Data": False}]}}],
    }

    async def asyncSetUp(self):
        self.server_handler = MessageHandler()
        self.server_transport = PacketForwardingTransport()
        self.server_circuit = Circuit(("127.0.0.1", 2), ("127.0.0.1", 99), self.server_transport)
        self.server = MockServer(self.server_circuit, self.server_handler)
        self.aio_mock = aioresponses.aioresponses()
        self.aio_mock.start()
        self.aio_mock.post(
            self.FAKE_LOGIN_URI,
            body=xmlrpc.client.dumps((self.FAKE_LOGIN_RESP,), None, True)
        )
        self.aio_mock.post(self.FAKE_LOGIN_RESP['seed_capability'], body=llsd.format_xml(self.FAKE_SEED_RESP))
        self.aio_mock.post(self.FAKE_SEED_RESP['EventQueueGet'], body=llsd.format_xml(self.FAKE_EQ_RESP), repeat=True)
        self.client = MockHippoClient(self.server)

    async def asyncTearDown(self):
        await self.client.aclose()
        self.aio_mock.stop()

    async def _log_client_in(self, client: MockHippoClient):
        async def _do_login():
            await client.login("foo", "bar", login_uri=self.FAKE_LOGIN_URI)

        login_task = asyncio.create_task(_do_login())
        with self.server_handler.subscribe_async(
                ("*",),
        ) as get_msg:
            assert (await _soon(get_msg)).name == "UseCircuitCode"
            assert (await _soon(get_msg)).name == "CompleteAgentMovement"
            self.server.circuit.send(Message(
                'RegionHandshake',
                Block('RegionInfo', fill_missing=True),
                Block('RegionInfo2', fill_missing=True),
                Block('RegionInfo3', fill_missing=True),
                Block('RegionInfo4', fill_missing=True),
            ))
            assert (await _soon(get_msg)).name == "RegionHandshakeReply"
            assert (await _soon(get_msg)).name == "AgentThrottle"
            await login_task

    async def test_login(self):
        await self._log_client_in(self.client)
        with self.server_handler.subscribe_async(
                ("*",),
        ) as get_msg:
            logout_task = asyncio.create_task(self.client.logout())
            assert (await _soon(get_msg)).name == "LogoutRequest"
            await logout_task

    async def test_eq(self):
        await self._log_client_in(self.client)
        with self.client.session.message_handler.subscribe_async(
                ("ViewerFrozenMessage",),
        ) as get_msg:
            assert (await _soon(get_msg)).name == "ViewerFrozenMessage"
