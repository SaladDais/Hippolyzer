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

import typing

from .msgtypes import MsgType, MsgBlockType
from ..datatypes import UUID


class MessageTemplateVariable:
    def __init__(self, name, tp, size):
        self.name = name
        self.type: MsgType = tp
        self.size = size
        self._probably_binary = None
        self._probably_text = None

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, tp={self.type!r}, size={self.size!r})"

    @property
    def probably_binary(self):
        if self._probably_binary is not None:
            return self._probably_binary

        if self.type not in {MsgType.MVT_FIXED, MsgType.MVT_VARIABLE}:
            self._probably_binary = False
        else:
            self._probably_binary = any(x in self.name for x in
                                        ("Binary", "Data", "Handle", "Color", "Texture", "Params", "NameValue"))
        return self._probably_binary

    @property
    def probably_text(self):
        if self._probably_text is not None:
            return self._probably_text

        if self.type not in {MsgType.MVT_FIXED, MsgType.MVT_VARIABLE}:
            self._probably_text = False
        else:
            self._probably_text = any(x in self.name for x in (
                "Name", "Text", "Title", "Description", "Message", "Label", "Method", "Filename",
            ))
            self._probably_text = self._probably_text and self.name != "NameValue"
        return self._probably_text

    @property
    def default_value(self):
        if self.type.is_int:
            return 0
        elif self.type.is_float:
            return 0.0
        elif self.type == MsgType.MVT_LLUUID:
            return UUID()
        elif self.type == MsgType.MVT_BOOL:
            return False
        elif self.type == MsgType.MVT_VARIABLE:
            if self.probably_binary:
                return b""
            if self.probably_text:
                return ""
            return b""
        elif self.type in (MsgType.MVT_LLVector3, MsgType.MVT_LLVector3d, MsgType.MVT_LLQuaternion):
            return 0.0, 0.0, 0.0
        elif self.type == MsgType.MVT_LLVector4:
            return 0.0, 0.0, 0.0, 0.0
        elif self.type == MsgType.MVT_FIXED:
            return b"\x00" * self.size
        elif self.type == MsgType.MVT_IP_ADDR:
            return "0.0.0.0"
        return None


class MessageTemplateBlock:
    def __init__(self, name):
        self.variables: typing.List[MessageTemplateVariable] = []
        self.variable_map: typing.Dict[str, MessageTemplateVariable] = {}
        self.name = name
        self.block_type: MsgBlockType = MsgBlockType.MBT_SINGLE
        self.number = 0

    def add_variable(self, var):
        self.variable_map[var.name] = var
        self.variables.append(var)

    def get_variable(self, name):
        return self.variable_map[name]


class MessageTemplate(object):
    frequency_strings = {-1: 'fixed', 1: 'high', 2: 'medium', 4: 'low'}  # strings for printout
    deprecation_strings = ["Deprecated", "UDPDeprecated", "UDPBlackListed", "NotDeprecated"]  # using _as_string methods
    encoding_strings = ["Unencoded", "Zerocoded"]  # etc
    trusted_strings = ["Trusted", "NotTrusted"]  # etc LDE 24oct2008

    def __init__(self, name):
        self.blocks: typing.List[MessageTemplateBlock] = []
        self.block_map: typing.Dict[str, MessageTemplateBlock] = {}

        # this is the function or object that will handle this type of message
        self.received_count = 0

        self.name = name
        self.frequency = None
        self.msg_num = 0
        self.msg_freq_num_bytes = None
        self.msg_trust = None
        self.msg_deprecation = None
        self.msg_encoding = None

    def add_block(self, block):
        self.block_map[block.name] = block
        self.blocks.append(block)

    def get_block(self, name):
        return self.block_map[name]

    def get_msg_freq_num_len(self):
        if self.frequency == -1:
            return 4
        return self.frequency

    def get_frequency_as_string(self):
        return MessageTemplate.frequency_strings[self.frequency]

    def get_deprecation_as_string(self):
        return MessageTemplate.deprecation_strings[self.msg_deprecation]
