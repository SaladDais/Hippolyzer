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
import copy
from typing import *
from logging import getLogger

from .data_packer import TemplateDataPacker
from .message import Message, MsgBlockList
from .msgtypes import MsgType, MsgBlockType
from .template import MessageTemplateVariable, MessageTemplateBlock
from .template_dict import TemplateDictionary, DEFAULT_TEMPLATE_DICT
from hippolyzer.lib.base import exc
from hippolyzer.lib.base import serialization as se
from hippolyzer.lib.base.datatypes import RawBytes

logger = getLogger('message.udpserializer')


class UDPMessageSerializer:
    DEFAULT_TEMPLATE = DEFAULT_TEMPLATE_DICT

    def __init__(self, message_template=None):
        if message_template is not None:
            self.template_dict = TemplateDictionary(message_template=message_template)
        else:
            self.template_dict = self.DEFAULT_TEMPLATE

    def serialize(self, msg: Message):
        current_template = self.template_dict.get_template_by_name(msg.name)
        if current_template is None:
            raise exc.MessageSerializationError("message name", "invalid message name")

        # Header and trailers are all big-endian
        writer = se.BufferWriter("!")
        writer.write(se.U8, msg.send_flags)
        # Should already have a packet ID by this point
        # But treat it as "0" if not.
        writer.write(se.U32, msg.packet_id or 0)
        # pack in the offset to the data past the extra data.
        writer.write(se.U8, len(msg.extra))

        # Pull this off `msg` for thread-safety
        raw_body = msg.raw_body
        if raw_body is not None:
            # This is a deserialized message we never parsed the body of,
            # Just shove the raw body back in.
            writer.write_bytes(raw_body)
        else:
            # Everything in the body we need to serialize ourselves is little-endian
            # Note that msg_num is _not_ little-endian, but we don't need to pack the
            # frequency and message number. The template stores it because it doesn't
            # change per template.
            body_writer = se.BufferWriter("<")
            body_writer.write_bytes(current_template.msg_freq_num_bytes)
            body_writer.write_bytes(msg.extra)

            # We're going to pop off keys as we go, so shallow copy the dict.
            blocks = copy.copy(msg.blocks)

            missing_block = None
            # Iterate based on the order of the blocks in the message template
            for tmpl_block in current_template.blocks:
                block_list = blocks.pop(tmpl_block.name, None)
                # An expected block was missing entirely. trailing single blocks are routinely
                # omitted by SL. Not an error unless another block containing data follows it.
                # Keep track.
                if block_list is None:
                    missing_block = tmpl_block.name
                    logger.debug("No block %s, bailing out" % tmpl_block.name)
                    continue
                # Had a missing block before, but we found one later in the template?
                elif missing_block:
                    raise ValueError(f"Unexpected {tmpl_block.name} block after missing {missing_block}")
                self._serialize_block(body_writer, tmpl_block, block_list)
            if blocks:
                raise KeyError(f"Unexpected {tuple(blocks.keys())!r} blocks in {msg.name}")

            msg_body = body_writer.buffer
            if msg.zerocoded:
                msg_body = self.zero_code_compress(msg_body)
            writer.write_bytes(msg_body)

        if msg.has_acks:
            # ACKs are always written in reverse order
            for ack in reversed(msg.acks):
                writer.write(se.U32, ack)
            writer.write(se.U8, len(msg.acks))
        return writer.copy_buffer()

    def _serialize_block(self, writer: se.BufferWriter, tmpl_block: MessageTemplateBlock,
                         block_list: MsgBlockList):
        block_count = len(block_list)
        # Multiple block type means there is a static number of blocks
        if tmpl_block.block_type == MsgBlockType.MBT_MULTIPLE:
            if tmpl_block.number != block_count:
                raise exc.MessageSerializationError(tmpl_block.name, "multiple block len mismatch")

        # variable means the block variables can repeat, with a count prefix
        if tmpl_block.block_type == MsgBlockType.MBT_VARIABLE:
            writer.write(se.U8, block_count)

        for block in block_list:
            for template_var in tmpl_block.variables:
                var_data = block.vars.get(template_var.name)
                self._serialize_var(writer, var_data, template_var, block.fill_missing)

    def _serialize_var(self, writer: se.BufferWriter, var_data: Any,
                       template_var: MessageTemplateVariable, fill_missing: bool):
        if var_data is None:
            # Blocks can be set to automatically fill missing variables with
            # a reasonable default
            if fill_missing:
                var_type = template_var.type
                # Variable-length var, just leave it empty.
                if var_type.size == -1:
                    var_data = b""
                else:
                    var_data = RawBytes(b"\x00" * var_type.size)
            else:
                raise exc.MessageSerializationError(template_var.name, "variable value is not set")

        if isinstance(var_data, RawBytes):
            # RawBytes may be specified for any variable type, and is assumed to
            # include the prefixed little-endian length field, if applicable.
            writer.write_bytes(var_data)
            return

        packed_var = TemplateDataPacker.pack(var_data, template_var.type)

        # if its a VARIABLE type, we have to write in the size of the data
        if template_var.type == MsgType.MVT_VARIABLE:
            writer.write(se.UINT_BY_BYTES[template_var.size], len(packed_var))
        writer.write_bytes(packed_var)

    @staticmethod
    def zero_code_compress(data: bytes):
        compressed_buff = bytearray()
        zero_count = 0

        def _terminate_zeros():
            nonlocal zero_count
            if zero_count:
                compressed_buff.append(zero_count)
                zero_count = 0

        for char in data:
            if char == 0x00:
                zero_count += 1
                if zero_count == 1:
                    compressed_buff.append(0x00)
                # Terminate zeros before we need to use the wrap case,
                # the official encoder doesn't use it and it isn't handled
                # correctly on any decoder other than LL's.
                elif zero_count == 255:
                    _terminate_zeros()
            else:
                _terminate_zeros()
                compressed_buff.append(char)

        _terminate_zeros()

        return compressed_buff
