from __future__ import annotations

import logging
from collections import deque
from typing import *

from hippolyzer.lib.base.message.circuit import Circuit
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.message.msgtypes import PacketFlags
from hippolyzer.lib.base.network.transport import Direction

LLUDP_LOGGING_HOOK = Optional[Callable[[Message], Any]]


class ProxiedCircuit(Circuit):
    def __init__(self, near_host, far_host, transport, logging_hook: LLUDP_LOGGING_HOOK = None):
        super().__init__(near_host, far_host, transport)
        self.in_injections = InjectionTracker(0)
        self.out_injections = InjectionTracker(0)
        self.logging_hook: LLUDP_LOGGING_HOOK = logging_hook

    def _send_prepared_message(self, message: Message, transport=None):
        try:
            serialized = self.serializer.serialize(message)
        except:
            logging.exception(f"Failed to serialize: {message.to_dict()!r}")
            raise
        if self.logging_hook and message.synthetic:
            self.logging_hook(message)
        return self.send_datagram(serialized, message.direction, transport=transport)

    def _get_injections(self, direction: Direction):
        if direction == Direction.OUT:
            return self.out_injections, self.in_injections
        return self.in_injections, self.out_injections

    def prepare_message(self, message: Message):
        if message.finalized:
            raise RuntimeError(f"Trying to re-send finalized {message!r}")
        if message.queued:
            # This is due to be dropped, nothing should be sending the original
            raise RuntimeError(f"Trying to send original of queued {message!r}")
        fwd_injections, reverse_injections = self._get_injections(message.direction)

        message.finalized = True

        # Injected, let's gen an ID
        if message.packet_id is None:
            message.packet_id = fwd_injections.gen_injectable_id()
            message.synthetic = True
        # This message wasn't injected by the proxy so we need to rewrite packet IDs
        # to account for IDs the real creator of the packet couldn't have known about.
        elif not message.synthetic:
            # was_dropped needs the unmodified packet ID
            if fwd_injections.was_dropped(message.packet_id) and message.name != "PacketAck":
                logging.warning("Attempting to re-send previously dropped %s:%s, did we ack?" %
                                (message.packet_id, message.name))
            message.packet_id = fwd_injections.get_effective_id(message.packet_id)
            fwd_injections.track_seen(message.packet_id)
            message.acks = tuple(
                reverse_injections.get_original_id(x) for x in message.acks
                if not reverse_injections.was_injected(x)
            )

            if message.name == "PacketAck":
                if not self._rewrite_packet_ack(message, reverse_injections) and not message.acks:
                    logging.debug(f"Dropping {message.direction} ack for injected packets!")
                    # Let caller know this shouldn't be sent at all, it's strictly ACKs for
                    # injected packets.
                    return False
            elif message.name == "StartPingCheck":
                self._rewrite_start_ping_check(message, fwd_injections)

        if message.acks:
            message.send_flags |= PacketFlags.ACK
        else:
            message.send_flags &= ~PacketFlags.ACK
        return True

    def _rewrite_packet_ack(self, message: Message, reverse_injections):
        new_blocks = []
        for block in message["Packets"]:
            packet_id = block["ID"]
            # This is an ACK for one the proxy injected, don't confuse
            # the other side by sending through the ACK
            if reverse_injections.was_injected(packet_id):
                continue
            block["ID"] = reverse_injections.get_original_id(packet_id)
            new_blocks.append(block)

        # Sending a PacketAck with nothing in it would be suspicious
        if not new_blocks:
            return False
        message["Packets"] = new_blocks
        return True

    def _rewrite_start_ping_check(self, message: Message, fwd_injections):
        orig_id = message["PingID"]["OldestUnacked"]
        new_id = fwd_injections.get_effective_id(orig_id)
        if orig_id != new_id:
            logging.debug("Rewrote oldest unacked %s -> %s" % (orig_id, new_id))
        # Get a list of unacked IDs for the direction this StartPingCheck is heading
        fwd_unacked = (a for (d, a) in self.unacked_reliable.keys() if d == message.direction)
        # Use the proxy's oldest unacked ID if it's older than the client's
        new_id = min((new_id, *fwd_unacked))
        message["PingID"]["OldestUnacked"] = new_id

    def drop_message(self, message: Message):
        if message.finalized:
            raise RuntimeError(f"Trying to drop finalized {message!r}")
        if message.packet_id is None:
            return
        fwd_injections, reverse_injections = self._get_injections(message.direction)

        fwd_injections.mark_dropped(message.packet_id)
        message.dropped = True
        message.finalized = True

        # Was sent reliably, tell the other end that we saw it and to shut up.
        if message.reliable:
            self.send_acks([message.packet_id], ~message.direction)

        # This packet had acks for the other end, send them in a separate PacketAck
        effective_acks = tuple(
            reverse_injections.get_original_id(x) for x in message.acks
            if not reverse_injections.was_injected(x)
        )
        if effective_acks:
            self.send_acks(effective_acks, message.direction, packet_id=message.packet_id)


class InjectionTracker:
    # TODO: WARNING! DOESN'T DEAL WITH PACKET ID WRAPAROUND WHATSOEVER!
    #  Circuits that last for hundreds of hours can be expected to break.
    #  Maybe just kill circuit when that happens to prevent silent wonkiness.
    def __init__(self, last_seen_id=0, maxlen=10000):
        self._packet_id_base = last_seen_id
        self._injection_base = 0
        self._maxlen = maxlen
        self.injections: deque[int] = deque(maxlen=maxlen)
        self.dropped: deque[int] = deque(maxlen=maxlen)

    def gen_injectable_id(self) -> int:
        new_id = self._packet_id_base + 1
        if len(self.injections) == self.injections.maxlen:
            # ID is about to fall off, old enough we can just add
            # it to the base for all Packet ID corrections.
            self._injection_base += 1
        self.injections.append(new_id)
        self.track_seen(new_id)
        return new_id

    def was_injected(self, packet_id: int):
        return packet_id in self.injections

    def was_dropped(self, packet_id: int):
        return packet_id in self.dropped

    def get_effective_id(self, orig_id: int):
        new_id = orig_id + self._injection_base
        for packet_id in self.injections:
            if new_id < packet_id and new_id not in self.injections:
                break
            new_id += 1
        if orig_id != new_id:
            logging.debug("Effective corrected %d -> %d" % (orig_id, new_id))
        return new_id

    def get_original_id(self, effective_id: int):
        if effective_id in self.injections:
            raise ValueError(f"No original ID for injected packet {effective_id}!")

        new_id = effective_id
        for packet_id in reversed(self.injections):
            if packet_id > new_id:
                break
            new_id -= 1
        new_id -= self._injection_base
        if effective_id != new_id:
            logging.debug("Orig corrected %d -> %d" % (effective_id, new_id))
        return new_id

    def track_seen(self, orig_id: int):
        # Sent a new packet that's legitimately larger than
        # What we were using to generate injected packet IDs.
        # Use that instead.
        oldest_tracked = self._packet_id_base - self._maxlen
        if orig_id > self._packet_id_base:
            self._packet_id_base = orig_id
        elif oldest_tracked > orig_id:
            logging.warning(f"Received VERY old packet ID {orig_id}, likely generated invalid ID.")

    def mark_dropped(self, packet_id: int):
        if packet_id not in self.dropped:
            self.dropped.append(packet_id)

    def __repr__(self):
        return f"{self.__class__.__name__}(inject_base={self._injection_base}," \
               f" packet_base={self._packet_id_base})"
