
"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""

#standard libraries
import unittest
import doctest
import re

#local libraries
from pyogp.lib.base.message.data import msg_tmpl
from pyogp.lib.base.message.template import MessageTemplate, MessageTemplateBlock, MessageTemplateVariable
from pyogp.lib.base.message.template_dict import TemplateDictionary
from pyogp.lib.base.message.template_parser import MessageTemplateParser
from pyogp.lib.base.message.msgtypes import MsgFrequency, MsgTrust, MsgEncoding, MsgDeprecation, MsgBlockType, MsgType

class TestDictionary(unittest.TestCase):

    def setUp(self):
        self.template_file = msg_tmpl
        parser = MessageTemplateParser(self.template_file)
        self.template_list = parser.message_templates

    def tearDown(self):
        pass

    def test_create_dictionary(self):
        try:
            msg_dict = TemplateDictionary(None)
            assert False, "Template dictionary fail case list==None not caught"
        except:
            assert True

    def test_get_packet(self):
        msg_dict = TemplateDictionary(self.template_list)
        packet = msg_dict.get_template('ConfirmEnableSimulator')
        assert packet != None, "get_packet failed"
        assert packet.frequency == MsgFrequency.MEDIUM_FREQUENCY_MESSAGE, "Incorrect frequency for ConfirmEnableSimulator"
        assert packet.msg_num == 8, "Incorrect message number for ConfirmEnableSimulator"

    def test_get_packet_pair(self):
        msg_dict = TemplateDictionary(self.template_list)
        packet = msg_dict.get_template_by_pair('Medium', 8)
        assert packet.name == 'ConfirmEnableSimulator', "Frequency-Number pair resulting in incorrect packet"        

class TestTemplates(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        self.template_file = msg_tmpl
        self.parser = MessageTemplateParser(self.template_file)
        self.msg_dict = TemplateDictionary(self.parser.message_templates)

    def test_parser(self):
        parser = MessageTemplateParser(self.template_file)
        assert parser.message_templates != None, "Parsing template file failed"

    def test_parser_fail(self):
        try:
            parser = MessageTemplateParser(None)
            assert False, "Fail case TEMPLATE_FILE == NONE not caught"
        except:
            assert True

    def test_parser_version(self):
        version = self.parser.version
        assert version == 2.0, "Version not correct, expected 2.0, got " + str(version)

    def test_template(self):
        template = self.msg_dict['CompletePingCheck']
        name = template.name
        freq = template.frequency
        num = template.msg_num
        trust = template.msg_trust
        enc = template.msg_encoding
        dep = template.msg_deprecation
        assert name == 'CompletePingCheck', "Expected: CompletePingCheck  Returned: " + name
        assert freq == MsgFrequency.HIGH_FREQUENCY_MESSAGE, "Expected: High  Returned: " + freq
        assert num == 2, "Expected: 2  Returned: " + str(num)
        assert trust == MsgTrust.LL_NOTRUST, "Expected: NotTrusted  Returned: " + trust
        assert enc == MsgEncoding.LL_UNENCODED, "Expected: Unencoded  Returned: " + enc
        # assert dep == MsgDeprecation.LL_NOTDEPRECATED, "Expected:   Returned: " + str(dep)       

    """def test_template_low(self):
        template = self.msg_dict['AddCircuitCode']
        hx = template.msg_num_hex
        assert hx == '\xff\xff\x00\x02', "Expected: " + r'\xff\xff\x00\x02' + " Returned: " + repr(hx)"""

    def test_deprecated(self):
        template = self.msg_dict['ObjectPosition']
        dep = template.msg_deprecation
        assert dep == MsgDeprecation.LL_DEPRECATED, "Expected:  Deprecated  Returned: " + str(dep)

    """def test_template_medium(self):
        template = self.msg_dict['RequestMultipleObjects']
        hx = template.msg_num_hex
        assert hx == '\xff\x03', "Expected: " + r'\xff\x03' + "  Returned: " + hx"""

    def test_template_fixed(self):
        template = self.msg_dict['PacketAck']
        num = template.msg_num
        #hx = template.msg_num_hex
        assert num == 251, "Expected: 251  Returned: " + str(num)
        #assert hx == '\xff\xff\xff\xfb', "Expected: " + r'\xff\xff\xff\xfb' + "  Returned: " + repr(hx)

    def test_blacklisted(self):
        template = self.msg_dict['TeleportFinish']
        self.assertEquals(template.get_deprecation_as_string(),
                          'UDPBlackListed')
    def test_block(self):
        block = self.msg_dict['OpenCircuit'].get_block('CircuitInfo')
        tp = block.block_type             #block.block_type vs block.type issue
        num = block.number
        assert tp == MsgBlockType.MBT_SINGLE, "Expected:   Single   Returned: " + tp       
        assert num == 0, "Expected:   0  Returned: " + str(num)               

    def test_block_multiple(self):
        block = self.msg_dict['NeighborList'].get_block('NeighborBlock')
        tp = block.block_type   #block.block_type vs block.type issue
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
        blocks = template.get_blocks()
        count = len(blocks)
        assert blocks[0].name == 'CircuitCode', "Add block failed"
        assert template.get_block('CircuitCode') != None, "Get block failed"

    def test_add_variable(self):
        block = MessageTemplateBlock('CircuitCode')
        variable = MessageTemplateVariable("PingID", MsgType.MVT_U8, 1)
        block.add_variable(variable)
        var_list = block.get_variables()
        assert var_list[0].name == 'PingID', "Add variable failed"
        assert block.get_variable('PingID') != None, "Get variable failed"

    def test_counts(self):
        l = ".*?Low\s*?(\d+).*"
        m = ".*?Medium\s*?(\d+).*"
        h = ".*?High\s*?(\d+).*"
        f = ".*?Fixed\s*?(0(X|x)\w+).*"
        self.template_file.seek(0)
        lines = self.template_file
        low_count = 0
        medium_count = 0
        high_count = 0
        fixed_count = 0
        while True:            
            try:
                line = lines.next()
            except StopIteration:
                break

            low = re.match(l, line)
            medium = re.match(m, line)
            high = re.match(h, line)
            fixed = re.match(f, line)
            if low:
                low_count += 1
            if medium:
                medium_count += 1
            if high:
                high_count += 1
            if fixed:
                fixed_count += 1

        frequency_counter = {"low":0, 'medium':0, "high":0, 'fixed':0}
        for template in self.msg_dict.message_templates.values():
            frequency_counter[template.get_frequency_as_string()]+=1
        self.assertEquals(low_count, frequency_counter["low"])
        self.assertEquals(medium_count, frequency_counter["medium"])
        self.assertEquals(high_count, frequency_counter["high"])
        self.assertEquals(fixed_count, frequency_counter["fixed"])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplates))
    suite.addTest(makeSuite(TestDictionary))
    return suite

