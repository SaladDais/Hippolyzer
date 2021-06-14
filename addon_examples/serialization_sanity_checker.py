"""
Validates that serialize(deserialize(packet)) == packet for any packet
that passes through the proxy. Useful for ensuring that serializers don't
change the meaning of a message, and that all of the viewer's quirks are
faithfully reproduced.
"""

import copy
import itertools
import logging
from typing import *

from hippolyzer.lib.base.message.msgtypes import PacketLayout
from hippolyzer.lib.base import serialization as se
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.network.transport import UDPPacket
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import SessionManager, Session

LOG = logging.getLogger(__name__)


class SerializationSanityChecker(BaseAddon):
    def __init__(self):
        self.serializer = UDPMessageSerializer()
        self.deserializer = UDPMessageDeserializer()

    def handle_proxied_packet(self, session_manager: SessionManager, packet: UDPPacket,
                              session: Optional[Session], region: Optional[ProxiedRegion]):
        # Well this doesn't even parse as a message, can't do anything about it.
        try:
            message = self.deserializer.deserialize(packet.data)
        except:
            LOG.error(f"Received unparseable message from {packet.src_addr!r}: {packet.data!r}")
            return
        try:
            message.ensure_parsed()
        except:
            LOG.exception(f"Exception during {message.name} message validation pre-parsing")
            return

        try:
            # We already know the message won't match if the serializers don't roundtrip.
            if message and self._roundtrip_var_serializers(message):
                ser = self.serializer.serialize(message)
                # LL's ObjectUpdate specifically randomly uses inefficient zero-coding
                # which is hard to reproduce. It means the same thing when decompressed,
                # so just expand both and compare. Technically this incorrectly expands the
                # acks too, but shouldn't matter because they should be the same in both.
                if message.name == "ObjectUpdate" and message.zerocoded:
                    orig_body = self.deserializer.zero_code_expand(packet.data[PacketLayout.PHL_NAME:])
                    ser_body = self.deserializer.zero_code_expand(ser[PacketLayout.PHL_NAME:])
                    matches = orig_body == ser_body
                else:
                    matches = packet.data == ser

                if not matches:
                    direction = "Out" if packet.outgoing else "In"
                    LOG.error("%s: %d %s\n%r != %r" %
                              (direction, message.packet_id, message.name, packet.data, ser))
        except:
            LOG.exception(f"Exception during message validation:\n{message!r}")

    def _roundtrip_var_serializers(self, message: Message):
        for block in itertools.chain(*message.blocks.values()):
            for var_name in block.vars.keys():
                orig_val = block[var_name]
                try:
                    orig_serializer = block.get_serializer(var_name)
                except KeyError:
                    # Don't have a serializer, onto the next field
                    continue
                # need to copy the serializer since we're going to replace a member function
                serializer: se.BaseSubfieldSerializer = copy.copy(orig_serializer)

                # Keep track of what got serialized at what position
                member_positions = []

                def _serialize_template(template, val):
                    writer = se.MemberTrackingBufferWriter(serializer.ENDIANNESS)
                    writer.write(template, val)
                    member_positions.clear()
                    member_positions.extend(writer.member_positions)
                    return writer.copy_buffer()

                serializer._serialize_template = _serialize_template
                try:
                    deser = serializer.deserialize(block, orig_val)
                except:
                    LOG.error(f"Exploded in deserializer for {message.name}.{block.name}.{var_name}")
                    raise

                # For now we consider returning UNSERIALIZABLE to be acceptable.
                # We should probably consider raising instead of returning that.
                if deser is se.UNSERIALIZABLE:
                    continue

                try:
                    new_val = serializer.serialize(block, deser)
                except:
                    LOG.error(f"Exploded in serializer for {message.name}.{block.name}.{var_name}")
                    raise

                if orig_val != new_val:
                    # OpenSim will put an extra NUL at the end of TEs with material fields
                    # whereas the viewer and SL just use EOF rather than explicit NUL to signal
                    # the end of the exception cases for the last field in a TE.
                    # OpenSim's behaviour isn't incorrect, but we're not going to reproduce it.
                    if var_name == "TextureEntry" and orig_val[:-1] == new_val and orig_val[-1] == 0:
                        continue
                    LOG.error("%d %s.%s.%s\n%r != %r" %
                              (message.packet_id, message.name, block.name, var_name, orig_val, new_val))
                    # This was templated, we can dig into which member mismatched
                    if member_positions:
                        # find the mismatch index
                        i = 0
                        bytes_zipped = itertools.zip_longest(orig_val, new_val, fillvalue=object())
                        for i, (old_byte, new_byte) in enumerate(bytes_zipped):
                            if old_byte != new_byte:
                                break
                        LOG.error(f"Mismatch at {i}, {member_positions!r}")
                    return False
        return True


addons = [SerializationSanityChecker()]
