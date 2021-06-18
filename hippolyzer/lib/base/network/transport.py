import abc
import asyncio
import enum
import socket
from typing import *


ADDR_TUPLE = Tuple[str, int]


class Direction(enum.Enum):
    OUT = enum.auto()
    IN = enum.auto()

    def __invert__(self):
        if self == self.OUT:
            return self.IN
        return self.OUT


class UDPPacket:
    def __init__(
            self,
            src_addr: Optional[ADDR_TUPLE],
            dst_addr: ADDR_TUPLE,
            data: bytes,
            direction: Direction
    ):
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.data = data
        self.direction = direction
        self.meta = {}

    @property
    def outgoing(self):
        return self.direction == Direction.OUT

    @property
    def incoming(self):
        return self.direction == Direction.IN

    @property
    def far_addr(self):
        if self.outgoing:
            return self.dst_addr
        return self.src_addr


class AbstractUDPTransport(abc.ABC):
    __slots__ = ()

    @abc.abstractmethod
    def send_packet(self, packet: UDPPacket) -> None:
        pass

    @abc.abstractmethod
    def close(self) -> None:
        pass


class SocketUDPTransport(AbstractUDPTransport):
    def __init__(self, transport: Union[asyncio.DatagramTransport, socket.socket]):
        super().__init__()
        self.transport = transport

    def send_packet(self, packet: UDPPacket) -> None:
        if not packet.outgoing:
            raise ValueError(f"{self.__class__.__name__} can only send outbound packets")
        self.transport.sendto(packet.data, packet.dst_addr)

    def close(self) -> None:
        self.transport.close()
