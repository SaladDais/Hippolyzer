import enum
import socket
import struct
import typing


class Direction(enum.Enum):
    OUT = enum.auto()
    IN = enum.auto()

    def __invert__(self):
        if self == self.OUT:
            return self.IN
        return self.OUT


ADDR_TUPLE = typing.Tuple[str, int]


class ProxiedUDPPacket:
    HEADER_STRUCT = struct.Struct("!HBB4sH")

    def __init__(self, src_addr: ADDR_TUPLE, dst_addr: ADDR_TUPLE, data: bytes, direction: Direction):
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.data = data
        self.direction = direction

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

    def _make_socks_header(self):
        return self.HEADER_STRUCT.pack(
            0, 0, 1, socket.inet_aton(self.far_addr[0]), self.far_addr[1])

    def serialize(self, socks_header=None):
        # Decide whether we need a header based on packet direction
        if socks_header is None:
            socks_header = self.incoming
        if not socks_header:
            return self.data
        return self._make_socks_header() + self.data
