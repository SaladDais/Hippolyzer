#standard libraries
import unittest, doctest
import pprint
import binascii

from zope.component import getUtility

#local libraries
from pyogp.lib.base.message.data import msg_tmpl
from pyogp.lib.base.message.interfaces import IUDPDispatcher
from pyogp.lib.base.interfaces import IDeserialization
from pyogp.lib.base.message.template_parser import MessageTemplateParser
from pyogp.lib.base.message.template_dict import TemplateDictionary
from pyogp.lib.base.registration import init

AGENT_DATA_UPDATE="C0 00 00 00 02 00 FF FF 01 83 1C 8A 77 67 E3 7B 42 2E AF B3 85 09 31 97 CA D1 03 4A 42 00 01 06 4B 72 61 66 74 00 01 01 00 1A"
AGENT_DATA_UPDATE =  binascii.unhexlify(''.join(AGENT_DATA_UPDATE.split()))

AGENT_ANIMATION="40 00 00 00 0A 00 05 1C 8A 77 67 E3 7B 42 2E AF B3 85 09 31 97 CA D1 4B 6F FF 1F B5 67 41 FD 85 EF A1 98 3B F2 B5 77 01 EF CF 67 0C 2D 18 81 28 97 3A 03 4E BC 80 6B 67 00 01 00"
AGENT_ANIMATION =  binascii.unhexlify(''.join(AGENT_ANIMATION.split()))



class TestPacketDecode(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        init()
        self.template_file = msg_tmpl
        parser = MessageTemplateParser(self.template_file)
        self.template_list = parser.message_templates        
        self.template_dict = TemplateDictionary(self.template_list)
        
    def test_agent_data_update(self):
        """test if the agent data update packet can be decoded"""
        message = AGENT_DATA_UPDATE
        size = len(message)
        deserializer = IDeserialization(message)
        packet = deserializer.deserialize()
        assert packet != None, "Wrong data"
        assert packet.message_data.name == 'AgentDataUpdate', "Wrong packet"
        assert packet.message_data.blocks['AgentData'][0].vars['LastName'].data == 'Kraft\x00', \
               "Wrong last name for agent update"
        assert packet.message_data.blocks['AgentData'][0].vars['FirstName'].data == 'JB\x00', \
               "Wrong first name for agent update"
        
    def test_agent_animation(self):
        """test if the agent data update packet can be decoded"""
        message = AGENT_ANIMATION
        size = len(message)
        deserializer = IDeserialization(message)
        packet = deserializer.deserialize()
        assert packet != None, "Wrong data 2"

        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPacketDecode))
    return suite

