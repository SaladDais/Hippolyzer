#standard libraries
import unittest, doctest

#local libraries
from pyogp.lib.base.data import msg_tmpl
from pyogp.lib.base.message.message_template import MessageTemplate, MessageTemplateBlock, MessageTemplateVariable
from pyogp.lib.base.message.message_template_parser import MessageTemplateParser
from pyogp.lib.base.message.message_template_builder import MessageTemplateBuilder
from pyogp.lib.base.message.message_template_dict import TemplateDictionary


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
        assert self.reader.validate_message(message, size) == True, \
               "Validation failed"

    def test_validation_fail(self):
        assert self.reader.validate_message('\x00\x00\x00\x00', 4) == False, \
               "Validation failed"

    def test_validation(self):
        self.builder.new_message('CompletePingCheck')
        self.builder.next_block('PingID')
        self.builder.add_data('PingID', 0x01, MsgType.MVT_U8)
        message, size = self.builder.build_message()
        self.reader.validate_message(message, size)
        msg = self.reader.read_message(message)
        
        
"""def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplateReader))
    return suite"""
