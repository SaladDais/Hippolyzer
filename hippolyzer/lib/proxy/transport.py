import socket
import struct

from hippolyzer.lib.base.network.transport import SocketUDPTransport, UDPPacket


class SOCKS5UDPTransport(SocketUDPTransport):
    HEADER_STRUCT = struct.Struct("!HBB4sH")

    @classmethod
    def serialize(cls, packet: UDPPacket, force_socks_header: bool = False) -> bytes:
        # Decide whether we need a header based on packet direction
        if packet.outgoing and not force_socks_header:
            return packet.data
        header = cls.HEADER_STRUCT.pack(
            0, 0, 1, socket.inet_aton(packet.far_addr[0]), packet.far_addr[1])
        return header + packet.data

    def send_packet(self, packet: UDPPacket) -> None:
        self.transport.sendto(self.serialize(packet), packet.dst_addr)
