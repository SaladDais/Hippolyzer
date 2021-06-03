"""
Test client handling of messages with malformed bodies

Serializes message, but mutates parts of the message body before the ACKs.

You don't want to use this unless you're a viewer developer trying to fix bugs.
There's a 95% chance it will crash your viewer, and maybe make you teleport random
places. Definitely don't test it while logged in with an account with access to
anything important.
"""
import copy
import datetime as dt
import logging
import random

from hippolyzer.lib.base.message.msgtypes import PacketLayout
from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session

LOG = logging.getLogger(__name__)


class PacketMutationAddon(BaseAddon):
    def __init__(self):
        self.serializer = UDPMessageSerializer()

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        # Only inbound messages, don't fiddle with the sim.
        if message.direction != Direction.IN:
            return
        # Messing with these may kill your circuit
        if message.name in ("PacketAck", "StartPingCheck", "CompletePingCheck"):
            return

        # Give login time to complete
        if session.started_at + dt.timedelta(seconds=10) > dt.datetime.now():
            return

        # Do it randomly
        if random.random() < 0.5:
            return

        # We need to take this message because we're going to
        # send our own re-serialized version. Don't use take_message()
        # because we're going to keep packet_id and acks the same.
        prepared = copy.deepcopy(message)
        # This message only had ACKs that were dropped.
        if not region.circuit.prepare_message(prepared):
            return

        serialized = bytearray(self.serializer.serialize(prepared))

        # Figure out where the ACKs will be so we don't mess those up
        acks_size = 0
        if prepared.acks:
            acks_size = 1 + (len(prepared.acks) * 4)

        # Give enough space for the message name, and ignore the acks at the end
        # mesage name can be 5 bytes if zerocoded.
        body_slice = slice(PacketLayout.PHL_NAME + 5 + message.offset, -1 - acks_size)
        body_view = serialized[body_slice]
        # The message is too small and we're left with nothing.
        if not body_view:
            return

        # Can be switched out with _flip_body_bytes() or something
        changed_body = self._truncate_body(body_view)
        if changed_body is None:
            return
        serialized[body_slice] = changed_body

        # Send out the raw mutated datagram
        region.circuit.send_datagram(serialized, message.direction)
        # Tell the proxy that we already sent the message and to short-circuit
        return True

    def _truncate_body(self, body_view: bytearray):
        # Don't want to mess with bodies this short.
        if len(body_view) < 4:
            return
        # Slice off the last bit of the body
        del body_view[int(len(body_view) * 0.7):-1]
        return body_view

    def _flip_body_bytes(self, body_view: bytearray):
        # Don't want to mess with bodies this short.
        if len(body_view) < 4:
            return

        # randomly flip bytes up to 19 bytes away from the end
        for i in range(-19, 0):
            if random.random() < 0.3:
                body_view[i] = (~body_view[i]) & 0xFF
        return body_view


addons = [PacketMutationAddon()]
