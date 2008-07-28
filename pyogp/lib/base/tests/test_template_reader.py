#standard libraries
import unittest, doctest

#local libraries
from pyogp.lib.base.data import msg_tmpl
from pyogp.lib.base.message.message_template import MessageTemplate, MessageTemplateBlock, MessageTemplateVariable
from pyogp.lib.base.message.message_template_parser import MessageTemplateParser
from pyogp.lib.base.message.message_template_builder import MessageTemplateBuilder
from pyogp.lib.base.message.message_template_reader import MessageTemplateReader
from pyogp.lib.base.message.message_template_dict import TemplateDictionary
from pyogp.lib.base.message.message_types import MsgType, PackFlags

class TestTemplateReader(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        self.template_file = msg_tmpl
        parser = MessageTemplateParser(self.template_file)
        self.template_list = parser.message_templates
        self.template_dict = TemplateDictionary(self.template_list)
        self.builder = MessageTemplateBuilder(self.template_dict)
        self.reader = MessageTemplateReader(self.template_dict)

    def test_validation(self):
        self.builder.new_message('CompletePingCheck')
        self.builder.next_block('PingID')
        self.builder.add_data('PingID', 0x01, MsgType.MVT_U8)
        message, size = self.builder.build_message()
        message = PackFlags.LL_NONE + '\x00\x00\x00\x00' +'\x00' + message
        size = len(message)
        assert self.reader.validate_message(message, size) == True, \
               "Validation failed"
        assert self.reader.current_template.name == 'CompletePingCheck', \
               "Validation failed to get current template"

    def test_clear_message(self):
        self.builder.new_message('CompletePingCheck')
        self.builder.next_block('PingID')
        self.builder.add_data('PingID', 0x01, MsgType.MVT_U8)
        message, size = self.builder.build_message()
        message = PackFlags.LL_NONE + '\x00\x00\x00\x00' +'\x00' + message
        size = len(message)
        self.reader.validate_message(message, size)
        assert self.reader.current_template != None, "Validate failed"
        self.reader.clear_message()
        assert self.reader.current_template == None, "Clear message failed"

    def test_validation_fail_size(self):
        try:
            self.reader.validate_message('\x00\x00\x00\x00', 4)
            assert False, "Validation held with packet being too small"
        except:
            assert True

    def test_validation_fail(self):
        message = PackFlags.LL_NONE + '\x00\x00\x00\x01' + '\x00'
        message += '\xff\xff\x01\xC2'
        assert self.reader.validate_message(message, len(message)) == False, \
              "Validation passed with incorrect message"
            
    def test_validation_except(self):
        try:
            self.reader.validate_message('\x00\x00\x00\x00\x00\x00\x00', 7)
            assert False, "Validation held with packet being not correct"
        except:
            assert True
            
    def test_read(self):
        self.builder.new_message('CompletePingCheck')
        self.builder.next_block('PingID')
        self.builder.add_data('PingID', 0x01, MsgType.MVT_U8)
        message, size = self.builder.build_message()
        message = PackFlags.LL_NONE + '\x00\x00\x00\x01' + '\x00' + message
        size = len(message)
        assert self.reader.validate_message(message, size), "Validation failed for test_read"
        assert self.reader.read_message(message), "Read failed"
        assert self.reader.get_data('PingID', 'PingID', MsgType.MVT_U8) == 1, \
               "Read error: PingID incorrect"
        
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplateReader))
    return suite
