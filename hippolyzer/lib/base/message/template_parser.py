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
import struct
import re

from . import template
from .msgtypes import MsgFrequency, MsgTrust, MsgEncoding
from .msgtypes import MsgDeprecation, MsgBlockType, MsgType
from ..exc import MessageTemplateParsingError, MessageTemplateNotFound

MESSAGE = 1
BLOCK = 2
DATA = 3


class MessageTemplateParser:
    """a parser which parses the message template and creates MessageTemplate objects
       which are stored in self.message_templates
    """

    START_RE = re.compile(r'.*{.*')
    END_RE = re.compile(r'.*}.*')
    BLOCK_DATA_RE = re.compile(r'.*?(\w+)\s+(\w+)(\s+(\d+))?.*')
    BLOCK_HEADER_RE = re.compile(r'.*?(\w+)\s+(\w+)(\s+(\d+))?.*')
    MESSAGE_HEADER_RE = re.compile(r'.*?(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)(\s+(\w+))?.*')
    VERSION_RE = re.compile(r"version.(.+)")
    COMMENT_RE = re.compile(r"^\s*//.*$")

    def __init__(self, template_file):
        if template_file is None:
            raise MessageTemplateNotFound("initializing template parser")

        self.template_file = template_file
        self.message_templates = []
        self.version = ''
        self.count = 0
        self.state = 0
        self._parse_template_file()

    def _add_template(self, new_template):
        self.count += 1
        self.message_templates.append(new_template)

    def _parse_template_file(self):

        # regular expressions
        self.template_file.seek(0)
        lines = self.template_file

        current_template = None
        current_block = None

        for line in lines:
            if self.COMMENT_RE.match(line):
                continue

            start = self.START_RE.match(line)
            end = self.END_RE.match(line)

            if self.version == '':
                version_test = self.VERSION_RE.match(line)  # gets packet headers
                if version_test is not None:
                    parts = version_test.group(1)
                    parts = parts.split()
                    self.version = float(parts[0])

            if start:
                self.state += 1

            if self.state == MESSAGE:
                message_header = self.MESSAGE_HEADER_RE.match(line)
                if message_header is not None:
                    current_template = self._start_new_template(message_header)
                    self._add_template(current_template)

            if self.state == BLOCK:
                block_header = self.BLOCK_HEADER_RE.match(line)
                if block_header is not None:
                    current_block = self._start_new_block(block_header)
                    current_template.add_block(current_block)

            if self.state == DATA:
                block_data = self.BLOCK_DATA_RE.match(line)
                if block_data is not None:
                    current_block.add_variable(self._start_new_var(block_data))

            if end:
                self.state -= 1

    def _start_new_template(self, match):

        new_template = template.MessageTemplate(match.group(1))

        frequency = None
        freq_str = match.group(2)
        if freq_str == 'Low':
            frequency = MsgFrequency.LOW_FREQUENCY_MESSAGE
        elif freq_str == 'Medium':
            frequency = MsgFrequency.MEDIUM_FREQUENCY_MESSAGE
        elif freq_str == 'High':
            frequency = MsgFrequency.HIGH_FREQUENCY_MESSAGE
        elif freq_str == 'Fixed':
            frequency = MsgFrequency.FIXED_FREQUENCY_MESSAGE

        new_template.frequency = frequency

        msg_num = int(match.group(3), 0)
        if frequency == MsgFrequency.FIXED_FREQUENCY_MESSAGE:
            # have to do this because Fixed messages are stored as a long in the template
            msg_num &= 0xff
            msg_num_bytes = struct.pack('!BBBB', 0xff, 0xff, 0xff, msg_num)
        elif frequency == MsgFrequency.LOW_FREQUENCY_MESSAGE:
            msg_num_bytes = struct.pack('!BBH', 0xff, 0xff, msg_num)
        elif frequency == MsgFrequency.MEDIUM_FREQUENCY_MESSAGE:
            msg_num_bytes = struct.pack('!BB', 0xff, msg_num)
        elif frequency == MsgFrequency.HIGH_FREQUENCY_MESSAGE:
            msg_num_bytes = struct.pack('!B', msg_num)
        else:
            raise Exception("don't know about frequency %s" % frequency)

        new_template.msg_num = msg_num
        new_template.msg_freq_num_bytes = msg_num_bytes

        msg_trust = None
        msg_trust_str = match.group(4)
        if msg_trust_str == 'Trusted':
            msg_trust = MsgTrust.LL_TRUSTED
        elif msg_trust_str == 'NotTrusted':
            msg_trust = MsgTrust.LL_NOTRUST

        new_template.msg_trust = msg_trust

        msg_encoding = None
        msg_encoding_str = match.group(5)
        if msg_encoding_str == 'Unencoded':
            msg_encoding = MsgEncoding.LL_UNENCODED
        elif msg_encoding_str == 'Zerocoded':
            msg_encoding = MsgEncoding.LL_ZEROCODED

        new_template.msg_encoding = msg_encoding

        msg_dep = None
        msg_dep_str = match.group(7)
        if msg_dep_str:
            if msg_dep_str == 'Deprecated':
                msg_dep = MsgDeprecation.LL_DEPRECATED
            elif msg_dep_str == 'UDPDeprecated':
                msg_dep = MsgDeprecation.LL_UDPDEPRECATED
            elif msg_dep_str == 'UDPBlackListed':
                msg_dep = MsgDeprecation.LL_UDPBLACKLISTED
            elif msg_dep_str == 'NotDeprecated':
                msg_dep = MsgDeprecation.LL_NOTDEPRECATED
        else:
            msg_dep = MsgDeprecation.LL_NOTDEPRECATED
        if msg_dep is None:
            raise MessageTemplateParsingError("Unknown msg_dep field %s" % match.group(0))
        new_template.msg_deprecation = msg_dep

        return new_template

    def _start_new_block(self, match):

        new_block = template.MessageTemplateBlock(match.group(1))

        block_type = None
        block_num = 0

        block_type_str = match.group(2)
        if block_type_str == 'Single':
            block_type = MsgBlockType.MBT_SINGLE
        elif block_type_str == 'Multiple':
            block_type = MsgBlockType.MBT_MULTIPLE
            block_num = int(match.group(4))
        elif block_type_str == 'Variable':
            block_type = MsgBlockType.MBT_VARIABLE

        new_block.block_type = block_type
        new_block.number = block_num

        return new_block

    def _start_new_var(self, match):

        type_string = match.group(2)
        var_type = None
        var_size = -1
        if type_string == 'U8':
            var_type = MsgType.MVT_U8
        elif type_string == 'U16':
            var_type = MsgType.MVT_U16
        elif type_string == 'U32':
            var_type = MsgType.MVT_U32
        elif type_string == 'U64':
            var_type = MsgType.MVT_U64
        elif type_string == 'S8':
            var_type = MsgType.MVT_S8
        elif type_string == 'S16':
            var_type = MsgType.MVT_S16
        elif type_string == 'S32':
            var_type = MsgType.MVT_S32
        elif type_string == 'S64':
            var_type = MsgType.MVT_S64
        elif type_string == 'F32':
            var_type = MsgType.MVT_F32
        elif type_string == 'F64':
            var_type = MsgType.MVT_F64
        elif type_string == 'LLVector3':
            var_type = MsgType.MVT_LLVector3
        elif type_string == 'LLVector3d':
            var_type = MsgType.MVT_LLVector3d
        elif type_string == 'LLVector4':
            var_type = MsgType.MVT_LLVector4
        elif type_string == 'LLQuaternion':
            var_type = MsgType.MVT_LLQuaternion
        elif type_string == 'LLUUID':
            var_type = MsgType.MVT_LLUUID
        elif type_string == 'BOOL':
            var_type = MsgType.MVT_BOOL
        elif type_string == 'IPADDR':
            var_type = MsgType.MVT_IP_ADDR
        elif type_string == 'IPPORT':
            var_type = MsgType.MVT_IP_PORT
        elif type_string == 'Fixed' or type_string == 'Variable':
            if type_string == 'Fixed':
                var_type = MsgType.MVT_FIXED
            elif type_string == 'Variable':
                var_type = MsgType.MVT_VARIABLE

            var_size = int(match.group(4))
            if var_size <= 0:
                raise MessageTemplateParsingError("variable size %s does not match %s" % (var_size, type_string))
        # if the size hasn't been read yet, then read it from message_types
        if var_size == -1:
            var_size = var_type.size

        return template.MessageTemplateVariable(match.group(1),
                                                var_type, var_size)
