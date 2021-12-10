from __future__ import annotations

import abc
import asyncio
import copy
import dataclasses
import datetime as dt
import logging
from typing import *
from typing import Optional

from .message_handler import MessageHandler
from ..network.transport import AbstractUDPTransport, UDPPacket, Direction, ADDR_TUPLE
from .message import Block, Message
from .msgtypes import PacketFlags
from .udpserializer import UDPMessageSerializer


@dataclasses.dataclass
class ReliableResendInfo:
    last_resent: dt.datetime
    message: Message
    completed: asyncio.Future = dataclasses.field(default_factory=asyncio.Future)
    tries_left: int = 10


class Circuit:
    def __init__(self, near_host: Optional[ADDR_TUPLE], far_host: ADDR_TUPLE, transport):
        self.near_host: Optional[ADDR_TUPLE] = near_host
        self.host: ADDR_TUPLE = far_host
        self.is_alive = True
        self.transport: Optional[AbstractUDPTransport] = transport
        self.serializer = UDPMessageSerializer()
        self.last_packet_at = dt.datetime.now()
        self.packet_id_base = 0
        self.unacked_reliable: Dict[Tuple[Direction, int], ReliableResendInfo] = {}
        self.resend_every: float = 3.0

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
        if message.acks:
            message.send_flags |= PacketFlags.ACK
        else:
            message.send_flags &= ~PacketFlags.ACK
        # If it was queued, it's not anymore
        message.queued = False
        message.finalized = True

    def send(self, message: Message, transport=None) -> UDPPacket:
        if self.prepare_message(message):
            # If the message originates from us then we're responsible for resends.
            if message.reliable and message.synthetic:
                self.unacked_reliable[(message.direction, message.packet_id)] = ReliableResendInfo(
                    last_resent=dt.datetime.now(),
                    message=message,
                )
            return self._send_prepared_message(message, transport)

    # Temporary alias
    send_message = send

    def send_reliable(self, message: Message, transport=None) -> asyncio.Future:
        """send() wrapper that always sends reliably and allows `await`ing ACK receipt"""
        if not message.synthetic:
            raise ValueError("Not able to send non-synthetic message reliably!")
        message.send_flags |= PacketFlags.RELIABLE
        self.send(message, transport)
        return self.unacked_reliable[(message.direction, message.packet_id)].completed

    def collect_acks(self, message: Message):
        effective_acks = list(message.acks)
        if message.name == "PacketAck":
            effective_acks.extend(x["ID"] for x in message["Packets"])
        for ack in effective_acks:
            resend_info = self.unacked_reliable.pop((~message.direction, ack), None)
            if resend_info:
                resend_info.completed.set_result(None)

    def resend_unacked(self):
        for resend_info in list(self.unacked_reliable.values()):
            # Not time to attempt a resend yet
            if dt.datetime.now() - resend_info.last_resent < dt.timedelta(seconds=self.resend_every):
                continue

            msg = copy.copy(resend_info.message)
            resend_info.tries_left -= 1
            # We were on our last try and we never received an ack
            if not resend_info.tries_left:
                logging.warning(f"Giving up on unacked {msg.packet_id}")
                del self.unacked_reliable[(msg.direction, msg.packet_id)]
                resend_info.completed.set_exception(TimeoutError("Exceeded resend limit"))
                continue
            resend_info.last_resent = dt.datetime.now()
            msg.send_flags |= PacketFlags.RESENT
            self._send_prepared_message(msg)

    def send_acks(self, to_ack: Sequence[int], direction=Direction.OUT, packet_id=None):
        logging.debug("%r acking %r" % (direction, to_ack))
        # TODO: maybe tack this onto `.acks` for next message?
        message = Message('PacketAck', *[Block('Packets', ID=x) for x in to_ack])
        message.packet_id = packet_id
        message.direction = direction
        self.send(message)

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
