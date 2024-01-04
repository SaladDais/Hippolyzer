
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

import unittest
import re

from hippolyzer.lib.base.message.data import msg_tmpl
from hippolyzer.lib.base.message.template import MessageTemplate, MessageTemplateBlock, MessageTemplateVariable
from hippolyzer.lib.base.message.template_dict import TemplateDictionary
from hippolyzer.lib.base.message.template_parser import MessageTemplateParser
from hippolyzer.lib.base.message.msgtypes import MsgFrequency, MsgEncoding, \
    MsgDeprecation, MsgBlockType, MsgType


class TestDictionary(unittest.TestCase):

    def setUp(self):
        self.template_file = msg_tmpl
        parser = MessageTemplateParser(self.template_file)
        self.template_list = parser.message_templates

    def test_create_dictionary(self):
        TemplateDictionary(None)

    def test_get_packet(self):
        msg_dict = TemplateDictionary(self.template_list)
        packet = msg_dict.get_template_by_name('ConfirmEnableSimulator')
        assert packet is not None, "get_packet failed"
        assert packet.frequency == MsgFrequency.MEDIUM, "Incorrect frequency"
        assert packet.num == 8, "Incorrect message number for ConfirmEnableSimulator"

    def test_get_packet_pair(self):
        msg_dict = TemplateDictionary(self.template_list)
        packet = msg_dict.get_template_by_pair('Medium', 8)
        assert packet.name == 'ConfirmEnableSimulator', "Frequency-Number pair resulting in incorrect packet"


class TestTemplates(unittest.TestCase):
    def setUp(self):
        self.template_file = msg_tmpl
        self.parser = MessageTemplateParser(self.template_file)
        self.msg_dict = TemplateDictionary(self.parser.message_templates)

    def test_parser(self):
        parser = MessageTemplateParser(self.template_file)
        assert parser.message_templates is not None, "Parsing template file failed"

    def test_parser_fail(self):
        with self.assertRaises(Exception):
            _parser = MessageTemplateParser(None)

    def test_parser_version(self):
        version = self.parser.version
        assert version == 2.0, "Version not correct, expected 2.0, got " + str(version)

    def test_template(self):
        template = self.msg_dict['CompletePingCheck']
        name = template.name
        freq = template.frequency
        num = template.num
        trust = template.trusted
        enc = template.encoding
        assert name == 'CompletePingCheck', "Expected: CompletePingCheck  Returned: " + name
        assert freq == MsgFrequency.HIGH, "Expected: High  Returned: " + freq
        assert num == 2, "Expected: 2  Returned: " + str(num)
        assert not trust, "Expected: NotTrusted  Returned: " + trust
        assert enc == MsgEncoding.UNENCODED, "Expected: Unencoded  Returned: " + enc

    def test_deprecated(self):
        template = self.msg_dict['ObjectPosition']
        dep = template.deprecation
        assert dep == MsgDeprecation.DEPRECATED, "Expected:  Deprecated  Returned: " + str(dep)

    def test_template_fixed(self):
        template = self.msg_dict['PacketAck']
        num = template.num
        assert num == 251, "Expected: 251  Returned: " + str(num)

    def test_blacklisted(self):
        template = self.msg_dict['TeleportFinish']
        self.assertEqual(template.deprecation,
                         MsgDeprecation.UDPBLACKLISTED)

    def test_block(self):
        block = self.msg_dict['OpenCircuit'].get_block('CircuitInfo')
        tp = block.block_type
        num = block.number
        assert tp == MsgBlockType.MBT_SINGLE, "Expected:   Single   Returned: " + tp
        assert num == 0, "Expected:   0  Returned: " + str(num)

    def test_block_multiple(self):
        block = self.msg_dict['NeighborList'].get_block('NeighborBlock')
        tp = block.block_type
        num = block.number
        assert tp == MsgBlockType.MBT_MULTIPLE, "Expected:   Multiple   Returned: " + tp
        assert num == 4, "Expected:   4  Returned: " + str(num)

    def test_variable(self):
        variable = self.msg_dict['StartPingCheck'].get_block('PingID').get_variable('PingID')
        tp = variable.type
        assert tp == MsgType.MVT_U8, "Expected: U8  Returned:  " + str(tp)

    def test_add_get_block(self):
        template = MessageTemplate('CompletePingCheck')
        block = MessageTemplateBlock('CircuitCode')
        template.add_block(block)
        blocks = template.blocks
        assert blocks[0].name == 'CircuitCode', "Add block failed"
        assert template.get_block('CircuitCode') is not None, "Get block failed"

    def test_add_variable(self):
        block = MessageTemplateBlock('CircuitCode')
        variable = MessageTemplateVariable("PingID", MsgType.MVT_U8, 1)
        block.add_variable(variable)
        var_list = block.variables
        assert var_list[0].name == 'PingID', "Add variable failed"
        assert block.get_variable('PingID') is not None, "Get variable failed"

    def test_counts(self):
        low_re = r".*?Low\s*?(\d+).*"
        med_re = r".*?Medium\s*?(\d+).*"
        high_re = r".*?High\s*?(\d+).*"
        fixed_re = r".*?Fixed\s*?(0(X|x)\w+).*"
        self.template_file.seek(0)
        lines = self.template_file
        low_count = 0
        medium_count = 0
        high_count = 0
        fixed_count = 0
        while True:
            try:
                line = next(lines)
            except StopIteration:
                break

            low = re.match(low_re, line)
            medium = re.match(med_re, line)
            high = re.match(high_re, line)
            fixed = re.match(fixed_re, line)
            if low:
                low_count += 1
            if medium:
                medium_count += 1
            if high:
                high_count += 1
            if fixed:
                fixed_count += 1

        frequency_counter = {"low": 0, 'medium': 0, "high": 0, 'fixed': 0}
        for template in list(self.msg_dict.message_templates.values()):
            frequency_counter[template.frequency.name.lower()] += 1
        self.assertEqual(low_count, frequency_counter["low"])
        self.assertEqual(medium_count, frequency_counter["medium"])
        self.assertEqual(high_count, frequency_counter["high"])
        self.assertEqual(fixed_count, frequency_counter["fixed"])
