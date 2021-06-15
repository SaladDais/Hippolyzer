from __future__ import annotations

import asyncio
import logging
import socket
import struct
from typing import Optional, List, Tuple

from hippolyzer.lib.base.network.transport import UDPPacket, Direction
from hippolyzer.lib.proxy.transport import SOCKS5UDPTransport


class SOCKS5Server:
    SOCKS_VERSION = 5

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        logging.info('Accepting connection from %s:%s' % addr)

        ctx = ProxyClientContext(writer)

        # greeting header
        # read and unpack 2 bytes from a client
        header = await reader.readexactly(2)
        version, num_methods = struct.unpack("!BB", header)

        # socks 5
        if version != self.SOCKS_VERSION or not num_methods:
            ctx.close()
            return

        # Don't support auth
        if 0 not in set(await reader.readexactly(num_methods)):
            # close connection
            ctx.close()
            return

        # send welcome message
        writer.write(struct.pack("!BB", self.SOCKS_VERSION, 0))
        await writer.drain()

        try:
            while await self.handle_command(ctx, reader, writer):
                pass
        finally:
            logging.info("Closing connection from %s:%s" % addr)
            ctx.close()

    def _udp_protocol_creator(self, source_addr):
        return lambda: UDPProxyProtocol(source_addr)

    async def handle_command(self, ctx: ProxyClientContext,
                             reader: asyncio.StreamReader,
                             writer: asyncio.StreamWriter):
        if reader.at_eof():
            return False
        try:
            data = await reader.readexactly(4)
        except asyncio.IncompleteReadError:
            return True

        version, cmd, _, address_type = struct.unpack("!BBBB", data)
        if version != self.SOCKS_VERSION:
            await self._write_reply(writer, code=1)
            logging.warning("Bad SOCKS version %d" % version)
            return False

        # TODO: support IPv6
        # We basically only read these to ignore them since they
        # don't matter in the UDP scheme.
        if address_type == 1:  # IPv4
            _address = socket.inet_ntoa(await reader.readexactly(4))
        elif address_type == 3:  # Domain name
            domain_length = (await reader.readexactly(1))[0]
            _address = await reader.readexactly(domain_length)
        else:
            await self._write_reply(writer, code=1)
            logging.warning("Bad addr type %d" % address_type)
            return False

        _port = struct.unpack('!H', await reader.readexactly(2))[0]

        try:
            # UDP Associate
            if cmd == 3:
                loop = asyncio.get_running_loop()
                transport, protocol = await loop.create_datagram_endpoint(
                    self._udp_protocol_creator(writer.get_extra_info("peername")),
                    local_addr=('0.0.0.0', 0))
                ctx.udp_associations.append(protocol)  # type: ignore
                udp_addr, udp_port = transport.get_extra_info("sockname")
                logging.info("Bound to %s:%s" % (udp_addr, udp_port))
                await self._write_reply(writer, addr_type=1, addr=udp_addr, port=udp_port)
            else:
                # We explicitly don't support TCP proxying!
                logging.warning("Unknown cmd %d" % cmd)
                await self._write_reply(writer, code=7)
                return False

        except Exception:
            logging.exception("Exception when handling SOCKS command")
            return False

        return True

    async def _write_reply(self, writer, code=0, addr_type=0, addr="0.0.0.0", port=0):
        reply = struct.pack(
            "!BBBB4sH",
            self.SOCKS_VERSION,
            code,
            0,
            addr_type,
            socket.inet_aton(addr),
            port
        )
        writer.write(reply)
        await writer.drain()


class ProxyClientContext:
    """
    Context about the connected client, one per TCP SOCKS 5 connection

    Destroyed along with any associated UDP ports when connection dies for any reason.
    """
    def __init__(self, writer):
        self.writer: asyncio.StreamWriter = writer
        self.udp_associations: List[UDPProxyProtocol] = []

    def close(self):
        self.writer.close()
        for association in self.udp_associations:
            try:
                association.close()
            except:
                logging.exception("Exception while cleaning up UDP")


class UDPProxyProtocol(asyncio.DatagramProtocol):
    """
    Wrapper for a SOCKS 5 UDP association.

    One per active UDP association / logical client instance,
    tightly bound to the expected client IP
    """
    def __init__(self, source_addr: Tuple[str, int]):
        self.socks_client_addr: Tuple[str, int] = source_addr
        self.far_to_near_map = {}
        self.transport: Optional[SOCKS5UDPTransport] = None

    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = SOCKS5UDPTransport(transport)

    def _parse_socks_datagram(self, data):
        rsv, frag, address_type = struct.unpack("!HBB", data[:4])
        if rsv != 0 or frag != 0:
            return None

        data = data[4:]

        if address_type == 1:  # IPv4
            address = socket.inet_ntoa(data[:4])
            data = data[4:]
        elif address_type == 3:  # Domain name
            domain_length = data[0]
            address = data[1:1 + domain_length]
            data = data[1 + domain_length:]
        else:
            logging.error("Don't understand addr type %d" % address_type)
            return None

        port = struct.unpack('!H', data[:2])[0]
        data = data[2:]
        return (address, port), data

    def datagram_received(self, data, source_addr):
        near_addr = self.far_to_near_map.get(source_addr)
        # Packet from the client IP that wasn't registered as a far addr
        if not near_addr and source_addr[0] == self.socks_client_addr[0]:
            socks_parsed = self._parse_socks_datagram(data)
            if socks_parsed:
                remote_addr, data = socks_parsed
                # register the destination as a known far addr
                # this allows us to have source and dest addr on the same IP
                # since we expect a send from client->far to happen first
                self.far_to_near_map[remote_addr] = source_addr
                src_packet = UDPPacket(
                    src_addr=source_addr,
                    dst_addr=remote_addr,
                    data=data,
                    direction=Direction.OUT,
                )
            else:
                logging.warning("Got non-SOCKS packet from local? %r" % data)
                return
        # From the far end, send it to the client
        else:
            if not near_addr:
                logging.warning("Got datagram from unknown host %s:%s" % source_addr)
                return

            src_packet = UDPPacket(
                src_addr=source_addr,
                dst_addr=near_addr,
                data=data,
                direction=Direction.IN,
            )

        try:
            self.handle_proxied_packet(src_packet)
        except:
            logging.exception("Barfed while handling UDP packet!")
            raise

    def handle_proxied_packet(self, packet):
        self.transport.send_packet(packet)

    def close(self):
        logging.info("Closing UDP transport")
        self.transport.close()
