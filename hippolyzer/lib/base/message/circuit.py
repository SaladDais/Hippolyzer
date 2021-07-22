from __future__ import annotations

import abc
import datetime as dt
import logging
from typing import *
from typing import Optional

from .message_handler import MessageHandler
from ..network.transport import AbstractUDPTransport, UDPPacket, Direction, ADDR_TUPLE
from .message import Block, Message
from .msgtypes import PacketFlags
from .udpserializer import UDPMessageSerializer


class Circuit:
    def __init__(self, near_host: Optional[ADDR_TUPLE], far_host: ADDR_TUPLE, transport):
        self.near_host: Optional[ADDR_TUPLE] = near_host
        self.host: ADDR_TUPLE = far_host
        self.is_alive = True
        self.transport: Optional[AbstractUDPTransport] = transport
        self.serializer = UDPMessageSerializer()
        self.last_packet_at = dt.datetime.now()
        self.packet_id_base = 0

    def _send_prepared_message(self, message: Message, transport=None):
        try:
            serialized = self.serializer.serialize(message)
        except:
            logging.exception(f"Failed to serialize: {message.to_dict()!r}")
            raise
        return self.send_datagram(serialized, message.direction, transport=transport)

    def send_datagram(self, data: bytes, direction: Direction, transport=None):
        self.last_packet_at = dt.datetime.now()
        src_addr, dst_addr = self.host, self.near_host
        if direction == Direction.OUT:
            src_addr, dst_addr = self.near_host, self.host

        packet = UDPPacket(src_addr, dst_addr, data, direction)
        (transport or self.transport).send_packet(packet)
        return packet

    def prepare_message(self, message: Message):
        if message.finalized:
            raise RuntimeError(f"Trying to re-send finalized {message!r}")
        message.packet_id = self.packet_id_base
        self.packet_id_base += 1
        if not message.acks:
            message.send_flags &= PacketFlags.ACK
        # If it was queued, it's not anymore
        message.queued = False
        message.finalized = True

    def send_message(self, message: Message, transport=None):
        if self.prepare_message(message):
            return self._send_prepared_message(message, transport)

    def send_acks(self, to_ack: Sequence[int], direction=Direction.OUT, packet_id=None):
        logging.debug("%r acking %r" % (direction, to_ack))
        # TODO: maybe tack this onto `.acks` for next message?
        message = Message('PacketAck', *[Block('Packets', ID=x) for x in to_ack])
        message.packet_id = packet_id
        message.direction = direction
        message.injected = True
        self.send_message(message)

    def __repr__(self):
        return "<%s %r : %r>" % (self.__class__.__name__, self.near_host, self.host)


class ConnectionHolder(abc.ABC):
    """
    Any object that has both a circuit and a message handler

    Preferred to explicitly passing around a circuit, message handler pair
    because generally a ConnectionHolder represents a region or a client.
    The same region or client may have multiple different circuits across the
    lifetime of a session (due to region restarts, etc.)
    """
    circuit: Optional[Circuit]
    message_handler: MessageHandler[Message, str]
