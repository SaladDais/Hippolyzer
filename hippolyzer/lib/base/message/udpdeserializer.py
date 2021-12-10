"""
Copyright 2009, Linden Research, Inc.
  See NOTICE.md for previous contributors
Copyright 2021, Salad Dais
All Rights Reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
import io
from typing import *
import weakref
from logging import getLogger

from hippolyzer.lib.base.datatypes import JankStringyBytes
from hippolyzer.lib.base.settings import Settings
from .template import MessageTemplateVariable
from .template_dict import DEFAULT_TEMPLATE_DICT
from .msgtypes import MsgType, MsgBlockType, PacketLayout
from .data_packer import TemplateDataPacker
from .message import Message, Block

from hippolyzer.lib.base import exc
from hippolyzer.lib.base import serialization as se

LOG = getLogger('message.udpdeserializer')


# Message numbers are variable width, number of \xFFs at the start determines
# The frequency of the message and how wide the actual message number will be
_MSG_NUM_SPECS: Tuple[Tuple[str, se.SerializablePrimitive], ...] = (
    # (frequency name, msg_num_spec), in ascending order of FF prefix length
    ("High", se.U8),    # b""
    ("Medium", se.U8),  # b"\xFF"
    ("Low", se.U16),    # b"\xFF\xFF"
    ("Fixed", se.U8),   # b"\xFF\xFF\xFF"
)


def _parse_msg_num(reader: se.BufferReader):
    ff_prefix_len = 0
    msg_num_bytes = reader.read_bytes(3, peek=True, check_len=False)
    for val in msg_num_bytes:
        if val != 0xFF:
            # found the start of the msg num
            break
        ff_prefix_len += 1
    reader.read_bytes(ff_prefix_len)
    frequency, msg_num_spec = _MSG_NUM_SPECS[ff_prefix_len]
    return frequency, reader.read(msg_num_spec)


class UDPMessageDeserializer:
    DEFAULT_TEMPLATE = DEFAULT_TEMPLATE_DICT

    def __init__(self, settings=None):
        self.settings = settings or Settings()
        self.template_dict = self.DEFAULT_TEMPLATE

    def deserialize(self, msg_buff: bytes) -> Message:
        msg = self._parse_message_header(msg_buff)
        if not self.settings.ENABLE_DEFERRED_PACKET_PARSING:
            try:
                self.parse_message_body(msg)
            except exc.DataPackingError as error:
                raise exc.MessageDeserializationError(msg.name, error)
        return msg

    def _parse_message_header(self, data: bytes) -> Message:
        msg_size = len(data)
        if PacketLayout.PACKET_ID_LENGTH >= msg_size:
            raise exc.MessageDeserializationError("packet length", "packet header too short")

        reader = se.BufferReader("!", data)

        msg: Message = Message("Placeholder")
        msg.synthetic = False
        msg.send_flags = reader.read(se.U8)
        msg.packet_id = reader.read(se.U32)

        # ACK_FLAG - means the incoming packet is ACKing some old packets of ours
        if msg.has_acks:
            # Last byte in the message is the number of acks
            msg_size -= 1
            with reader.scoped_seek(-1, io.SEEK_END):
                num_acks = reader.read(se.U8)
                # Preceded by the IDs to be ACKed
                acks_field_len = num_acks * 4
                msg_size -= acks_field_len
                # Would ACKs collide with packet ID?
                if PacketLayout.PACKET_ID_LENGTH >= msg_size:
                    raise exc.MessageDeserializationError("packet length", "bad acks")

                # ACKs are meant to be read backwards from the end of the message,
                # so just insert at the head instead of appending
                reader.seek(msg_size)
                acks = []
                for ack in range(num_acks):
                    acks.insert(0, reader.read(se.U32))
            msg.acks = tuple(acks)
            # Snip the acks off the end so data in message blocks can't collide with them
            data = data[:msg_size]

        # at the offset position, the messages stores the offset to where the
        # payload begins (may be extra header information with no semantic meaning
        # in between)
        msg.offset = reader.read(se.U8)

        if msg.zerocoded:
            # Snip and decode just enough to fit a zerocoded message num, and worst-case
            # extra length. Both the message number and extra field are zero-coded!
            header = data[PacketLayout.PHL_NAME:16 + (msg.offset * 2)]
            reader = se.BufferReader("!", self.zero_code_expand(header))

        frequency, num = _parse_msg_num(reader)
        current_template = self.template_dict.get_template_by_pair(frequency, num)
        if current_template is None:
            raise exc.MessageTemplateNotFound("deserializing data")
        msg.name = current_template.name

        # extra field, see note regarding msg.offset
        msg.raw_extra = reader.read_bytes(msg.offset)

        # Useful for snipping the template contents out of a message and comparing
        msg.body_boundaries = (PacketLayout.PACKET_ID_LENGTH, msg_size)
        msg.raw_body = bytes(data[PacketLayout.PHL_NAME:])
        msg.deserializer = weakref.ref(self)
        return msg

    def parse_message_body(self, msg: Message):
        raw_body = msg.raw_body
        # Already parsed if we don't have a raw body
        if not raw_body:
            return
        msg.raw_body = None
        msg.deserializer = None

        if msg.zerocoded:
            raw_body = self.zero_code_expand(raw_body)

        # From here on almost everything we need to actually parse is little-endian
        reader = se.BufferReader("<", raw_body)

        # Skip past message number and extra fields
        current_template = self.template_dict.get_template_by_name(msg.name)
        reader.seek(current_template.get_msg_freq_num_len() + msg.offset)

        for tmpl_block in current_template.blocks:
            LOG.debug("Parsing %s:%s" % (msg.name, tmpl_block.name))
            # EOF?
            if not len(reader):
                # Seems like even some "Single" blocks are optional?
                # Ex. EstateBlock in ImprovedInstantMessage.
                LOG.debug("Data ended before block %s, bailing out" % tmpl_block.name)
                break

            if tmpl_block.block_type == MsgBlockType.MBT_SINGLE:
                repeat_count = 1
            elif tmpl_block.block_type == MsgBlockType.MBT_MULTIPLE:
                repeat_count = tmpl_block.number
            elif tmpl_block.block_type == MsgBlockType.MBT_VARIABLE:
                repeat_count = reader.read(se.U8)
            else:
                raise ValueError("ERROR: Unknown block type: %s in %s packet." %
                                 (str(tmpl_block.block_type), msg.name))

            # Track that we _saw_ this block at least.
            msg.create_block_list(tmpl_block.name)

            for i in range(repeat_count):
                current_block = Block(tmpl_block.name)
                LOG.debug("Adding block %s" % current_block.name)
                msg.add_block(current_block)

                for tmpl_variable in tmpl_block.variables:
                    context_str = f"{msg.name}.{tmpl_block.name}.{tmpl_variable.name}"
                    try:
                        current_block[tmpl_variable.name] = self._parse_var(
                            reader=reader,
                            tmpl_variable=tmpl_variable,
                        )
                    except:
                        LOG.exception(f"Raised while parsing var in {context_str}")
                        raise

        if not msg.blocks and current_template.blocks:
            raise exc.MessageDeserializationError("message", "message is empty")

        if len(reader):
            LOG.warning(f"Left {len(reader)} bytes unread past end of {msg.name} message, "
                        f"is your message template up to date? {reader.read_bytes(len(reader))!r}")

    def _parse_var(self, reader: se.BufferReader, tmpl_variable: MessageTemplateVariable):
        data_size = tmpl_variable.size
        if tmpl_variable.type == MsgType.MVT_VARIABLE:
            # In this case tmpl_var.size describes the size of the length field in bytes,
            # read the actual length.
            data_size = reader.read(se.UINT_BY_BYTES[data_size])

        unpacked_data = TemplateDataPacker.unpack(
            reader.read_bytes(data_size, to_bytes=False),
            tmpl_variable.type,
        )

        # bytes need a little extra guesswork as to whether they're really strings
        # or just plain bytes.
        if not isinstance(unpacked_data, bytes):
            return unpacked_data

        # If this is a binary blob then we don't have to touch it, keep it as bytes.
        if tmpl_variable.probably_binary:
            return unpacked_data
        # Truncated strings need to be treated carefully
        if tmpl_variable.probably_text and unpacked_data.endswith(b"\x00"):
            try:
                return unpacked_data.decode("utf8").rstrip("\x00")
            except UnicodeDecodeError:
                return JankStringyBytes(unpacked_data)
        elif tmpl_variable.type in {MsgType.MVT_FIXED, MsgType.MVT_VARIABLE}:
            # No idea if this should be bytes or a string... make an object that's sort of both.
            return JankStringyBytes(unpacked_data)
        else:
            raise ValueError(f"Unhandled case for binary data? {tmpl_variable}")

    @staticmethod
    def zero_code_expand(msg_buf: bytes):
        decode_buf = bytearray()
        in_zero = False
        for c in msg_buf:
            # Well beyond what the viewer allows zerocoding to expand to
            if len(decode_buf) > 0x3000:
                raise ValueError("Unreasonably large zerocoded message")

            if c == 0x00:
                # Always have to write the zero in case we're the last byte
                decode_buf.append(0x00)
                # zerocoding continuation. ironically the canonical compressor
                # will never use these, but they're valid.
                if in_zero:
                    decode_buf.extend(b"\x00" * 255)
                in_zero = True
            else:
                # This byte is the number of zeros to write
                if in_zero:
                    # The initial zero was already written
                    zero_count = c - 1
                    decode_buf.extend(b"\x00" * zero_count)
                    in_zero = False
                # Regular character
                else:
                    decode_buf.append(c)

        return decode_buf
