#standard libraries
import unittest, doctest

#local libraries
from pyogp.lib.base.data import msg_tmpl
from pyogp.lib.base.message.message_template import MessageTemplate, MessageTemplateBlock, MessageTemplateVariable
from pyogp.lib.base.message.message_template_dict import TemplateDictionary
from pyogp.lib.base.message.message_template_parser import MessageTemplateParser
from pyogp.lib.base.message.message_types import MsgFrequency, MsgTrust, \
     MsgEncoding, MsgDeprecation, MsgBlockType, MsgType

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
        hx = template.msg_num_hex
        trust = template.msg_trust
        enc = template.msg_encoding
        dep = template.msg_deprecation
        assert name == 'CompletePingCheck', "Expected: CompletePingCheck  Returned: " + name
        assert freq == MsgFrequency.HIGH_FREQUENCY_MESSAGE, "Expected: High  Returned: " + freq
        assert num == 2, "Expected: 2  Returned: " + str(num)
        assert hx == '\x02', "Expected: '\x02'  Returned: " + repr(hx)
        assert trust == MsgTrust.LL_NOTRUST, "Expected: NotTrusted  Returned: " + trust
        assert enc == MsgEncoding.LL_UNENCODED, "Expected: Unencoded  Returned: " + enc
        assert dep == MsgDeprecation.LL_NOTDEPRECATED, "Expected:   Returned: " + dep       

    def test_template_low(self):
        template = self.msg_dict['AddCircuitCode']
        hx = template.msg_num_hex
        assert hx == '\xff\xff\x00\x02', "Expected: " + r'\xff\xff\x00\x02' + " Returned: " + repr(hx)

    def test_deprecated(self):
        template = self.msg_dict['ObjectPosition']
        dep = template.msg_deprecation
        assert dep == MsgDeprecation.LL_DEPRECATED, "Expected:  Deprecated  Returned: " + dep

    def test_template_medium(self):
        template = self.msg_dict['RequestMultipleObjects']
        hx = template.msg_num_hex
        assert hx == '\xff\x03', "Expected: " + r'\xff\x03' + "  Returned: " + hx

    def test_template_fixed(self):
        template = self.msg_dict['PacketAck']
        num = template.msg_num
        hx = template.msg_num_hex
        assert num == 251, "Expected: 251  Returned: " + str(num)
        assert hx == '\xff\xff\xff\xfb', "Expected: " + r'\xff\xff\xff\xfb' + "  Returned: " + repr(hx)

    def test_block(self):
        block = self.msg_dict['OpenCircuit'].get_block('CircuitInfo')
        tp = block.type
        num = block.block_number
        assert tp == MsgBlockType.MBT_SINGLE, "Expected:   Single   Returned: " + tp       
        assert num == 0, "Expected:   0  Returned: " + str(num)               
        
    def test_block_multiple(self):
        block = self.msg_dict['NeighborList'].get_block('NeighborBlock')
        tp = block.type
        num = block.block_number
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

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplates))
    suite.addTest(makeSuite(TestDictionary))
    return suite
