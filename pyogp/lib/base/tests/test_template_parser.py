#standard libraries
import unittest, doctest

#local libraries
from pyogp.lib.base.data import msg_tmpl
from pyogp.lib.base.message_template import MessageTemplate, MessageTemplateBlock, MessageTemplateVariable
from pyogp.lib.base.message_template_dict import TemplateDictionary
from pyogp.lib.base.message_template_parser import MessageTemplateParser

class TestDictionary(unittest.TestCase):
    def setUp(self):
        self.template_file = msg_tmpl
        parser = MessageTemplateParser(self.template_file)
        self.template_list = parser.get_template_list()

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
        assert packet.get_frequency() == 'Medium', "Incorrect frequency for ConfirmEnableSimulator"
        assert packet.get_message_number() == 8, "Incorrect message number for ConfirmEnableSimulator"

    def test_get_packet_pair(self):
        msg_dict = TemplateDictionary(self.template_list)
        packet = msg_dict.get_template_by_pair('Medium', 8)
        assert packet.get_name() == 'ConfirmEnableSimulator', "Frequency-Number pair resulting in incorrect packet"        

class TestTemplates(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        self.template_file = msg_tmpl

    def test_parser(self):
        parser = MessageTemplateParser(self.template_file)
        assert parser.get_template_list() != None, "Parsing template file failed"

    def test_parser_fail(self):
        try:
            parser = MessageTemplateParser(None)
            assert False, "Fail case TEMPLATE_FILE == NONE not caught"
        except:
            assert True
                        
    def test_parser_version(self):
        parser = MessageTemplateParser(self.template_file)
        version = parser.get_version()
        assert version == 2.0, "Version not correct, expected 2.0, got " + str(version)

    def test_template(self):
        template = MessageTemplate(('CompletePingCheck', 'High', '2', 'NotTrusted', 'Unencoded'))
        name = template.get_name()
        freq = template.get_frequency()
        num = template.get_message_number()
        hx = template.get_message_hex_num()
        trust = template.get_trust()
        enc = template.get_encoding()
        dep = template.get_deprecation()
        assert name == 'CompletePingCheck', "Expected: CompletePingCheck  Returned: " + name
        assert freq == 'High', "Expected: High  Returned: " + freq
        assert num == 2, "Expected: 2  Returned: " + str(num)
        assert hx == '\x02', "Expected: '\x02'  Returned: " + repr(hx)
        assert trust == 'NotTrusted', "Expected: NotTrusted  Returned: " + trust
        assert enc == 'Unencoded', "Expected: Unencoded  Returned: " + enc
        assert dep == '', "Expected:   Returned: " + dep       

    def test_template_low_deprecated(self):
        template = MessageTemplate(('CompletePingCheck', 'Low', '2', 'NotTrusted', 'Unencoded', 'Deprecated'))
        hx = template.get_message_hex_num()
        dep = template.get_deprecation()
        assert hx == '\xff\xff\x00\x02', "Expected: '\xff\xff\x00\x02'  Returned: " + repr(hx)
        assert dep == 'Deprecated', "Expected:  Deprecated  Returned: " + dep       

    def test_template_medium(self):
        template = MessageTemplate(('CompletePingCheck', 'Medium', '2', 'NotTrusted', 'Unencoded', 'Deprecated'))
        hx = template.get_message_hex_num()
        dep = template.get_deprecation()
        assert hx == '\xff\x02', "Expected: " + r'\xff\x02' + "  Returned: " + hx

    def test_template_fixed(self):
        template = MessageTemplate(('CompletePingCheck', 'Fixed', '0xFFFFFFFB', 'NotTrusted', 'Unencoded'))
        num = template.get_message_number()
        hx = template.get_message_hex_num()
        assert num == 251, "Expected: 251  Returned: " + str(num)
        assert hx == '\xff\xff\xff\xfb', "Expected: " + r'\xff\xff\xff\xfb' + "  Returned: " + repr(hx)

    def test_block(self):
        block = MessageTemplateBlock(('PingID', 'Single'))
        name = block.get_name()
        tp = block.get_block_type()
        num = block.get_block_number()
        assert name == 'PingID', "Expected:   PingID    Returned" + name       
        assert tp == 'Single', "Expected:   Single   Returned: " + tp       
        assert num == 0, "Expected:   0  Returned: " + str(num)               
        
    def test_block_multiple(self):
        block = MessageTemplateBlock(('CircuitCode', 'Multiple', '2'))
        name = block.get_name()
        tp = block.get_block_type()
        num = block.get_block_number()
        assert name == 'CircuitCode', "Expected:   CircuitCode    Returned" + name       
        assert tp == 'Multiple', "Expected:   Multiple   Returned: " + tp
        assert num == 2, "Expected:   2  Returned: " + str(num)               

    def test_variable(self):
        variable = MessageTemplateVariable("PingID", "U8")
        name = variable.get_name()
        tp = variable.get_type()
        assert name == 'PingID', "Expected: PingID  Returned:  " + name
        assert tp == 'U8', "Expected: U8  Returned:  " + tp        

    def test_add_get_block(self):
        template = MessageTemplate(('CompletePingCheck', 'High', '2', 'NotTrusted', 'Unencoded'))
        block = MessageTemplateBlock(('CircuitCode', 'Multiple', '2'))
        template.add_block(block)
        blocks = template.get_blocks()
        count = len(blocks)
        assert blocks[0].get_name() == 'CircuitCode', "Add block failed"
        assert template.get_block('CircuitCode') != None, "Get block failed"
        
    def test_add_variable(self):
        block = MessageTemplateBlock(('CircuitCode', 'Multiple', '2'))
        variable = MessageTemplateVariable("PingID", "U8")
        block.add_variable(variable)
        var_list = block.get_variables()
        assert var_list[0].get_name() == 'PingID', "Add variable failed"
        assert block.get_variable('PingID') != None, "Get variable failed"

    def test_StartPingCheck(self):
        parser = MessageTemplateParser(self.template_file)
        template_list = parser.get_template_list()
        my_template = template_list[4]
        name = my_template.get_name()
        frequency = my_template.get_frequency()
        num = my_template.get_message_number()
        hx = my_template.get_message_hex_num()
        trust = my_template.get_trust()
        code = my_template.get_encoding()
        deprecate = my_template.get_deprecation()
        block_count = len(my_template.get_blocks())
        my_block = my_template.get_block('PingID')
        p_id = my_block.get_variable('PingID')
        assert name == 'StartPingCheck', "Expected: StartPingCheck  Returned: " + name
        assert frequency == 'High', "Expected: High  Returned: " + frequency
        assert num == 1, "Expected: 1  Returned: " + str(num)
        assert hx == '\x01', "Expected: " + r'\x01' + "  Returned: " + repr(hx)
        assert trust == 'NotTrusted', "Expected: NotTrusted  Returned: " + trust
        assert code == 'Unencoded', "Expected: Unencoded  Returned: " + code
        assert deprecate == '', "Expected:    Returned: " + str(deprecate)
        assert block_count == 1, "Expected: 1  Returned: " + str(block_count)
        assert my_block != None, "Getting block PingID failed"
        assert p_id != None, "Getting variable PingID failed"

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplates))
    suite.addTest(makeSuite(TestDictionary))
    return suite
