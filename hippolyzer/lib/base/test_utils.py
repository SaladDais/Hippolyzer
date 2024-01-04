import asyncio
from typing import Any, Optional, List, Tuple

from hippolyzer.lib.base.message.circuit import Circuit, ConnectionHolder
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.network.transport import AbstractUDPTransport, ADDR_TUPLE, UDPPacket


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


class MockHandlingCircuit(Circuit):
    def __init__(self, handler: MessageHandler[Message, str]):
        super().__init__(("127.0.0.1", 1), ("127.0.0.1", 2), None)
        self.handler = handler

    def _send_prepared_message(self, message: Message, transport=None):
        loop = asyncio.get_event_loop_policy().get_event_loop()
        loop.call_soon(self.handler.handle, message)


class MockConnectionHolder(ConnectionHolder):
    def __init__(self, circuit, message_handler):
        self.circuit = circuit
        self.message_handler = message_handler


async def soon(awaitable) -> Message:
    return await asyncio.wait_for(awaitable, timeout=1.0)
