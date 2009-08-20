
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
import unittest, doctest
import pprint
import binascii
import re, datetime

#local libraries
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.message.data import msg_tmpl
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.udpdeserializer import UDPMessageDeserializer
from pyogp.lib.base.message.template_parser import MessageTemplateParser
from pyogp.lib.base.message.template_dict import TemplateDictionary

AGENT_DATA_UPDATE="C0 00 00 00 02 00 FF FF 01 83 1C 8A 77 67 E3 7B 42 2E AF B3 85 09 31 97 CA D1 03 4A 42 00 01 06 4B 72 61 66 74 00 01 01 00 1A"
AGENT_DATA_UPDATE =  binascii.unhexlify(''.join(AGENT_DATA_UPDATE.split()))

AGENT_ANIMATION="40 00 00 00 0A 00 05 1C 8A 77 67 E3 7B 42 2E AF B3 85 09 31 97 CA D1 4B 6F FF 1F B5 67 41 FD 85 EF A1 98 3B F2 B5 77 01 EF CF 67 0C 2D 18 81 28 97 3A 03 4E BC 80 6B 67 00 01 00"
AGENT_ANIMATION =  binascii.unhexlify(''.join(AGENT_ANIMATION.split()))

OBJECT_UPDATE = "C0 00 00 00 51 00 0C 00 01 EA 03 00 02 E6 03 00 01 BE FF 01 06 BC 8E 0B 00 01 69 94 8C 6A 4D 22 1B 66 EC E4 AC 31 63 93 CB 4B 57 89 98 01 09 03 00 01 51 40 88 3E 51 40 88 3E 51 40 88 3E 3C A2 44 B3 42 9A 68 2B 42 C8 5B D1 41 00 18 4B 8C FF 3E BD 76 FF BE C5 44 00 01 BF 00 10 50 04 00 01 10 20 05 00 04 64 64 00 0F 2E 00 01 A1 33 DC 77 0A 1A BB 27 A7 2E 78 64 63 AB 94 AB 00 08 80 3F 00 03 80 3F 00 0F 10 13 FF 00 08 80 3F 8F C2 F5 3D 00 0A 56 6F 43 CC 00 01 02 00 03 04 00 02 04 00 02 64 26 00 03 0E 00 01 0E 00 01 19 00 01 80 00 01 80 00 01 80 00 01 80 00 01 80 00 01 80 91 11 D2 5E 2F 12 8F 81 55 A7 40 3A 78 B3 0E 2D 00 10 03 01 00 03 1E 25 6E A2 FF C5 E0 83 00 01 06 00 01 0D 0D 01 00 11 0E DC 9B 83 98 9A 4A 76 AC C3 DB BF 37 54 61 88 00 22"
OBJECT_UPDATE =  binascii.unhexlify(''.join(OBJECT_UPDATE.split()))

class TestPacketDecode(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        self.template_file = msg_tmpl
        parser = MessageTemplateParser(self.template_file)
        self.template_list = parser.message_templates        
        self.template_dict = TemplateDictionary(self.template_list)

        self.settings = Settings()
        self.settings.ENABLE_DEFERRED_PACKET_PARSING = False

    def test_agent_data_update(self):
        """test if the agent data update packet can be decoded"""
        message = AGENT_DATA_UPDATE
        size = len(message)
        deserializer = UDPMessageDeserializer(settings = self.settings)
        packet = deserializer.deserialize(message)
        assert packet != None, "Wrong data"
        assert packet.name == 'AgentDataUpdate', "Wrong packet"
        assert packet.blocks['AgentData'][0].vars['LastName'].data == 'Kraft', \
               "Wrong last name for agent update"
        assert packet.blocks['AgentData'][0].vars['FirstName'].data == 'JB', \
               "Wrong first name for agent update"

    def test_agent_animation(self):
        """test if the agent data update packet can be decoded"""
        message = AGENT_ANIMATION
        size = len(message)
        deserializer = UDPMessageDeserializer(settings = self.settings)
        packet = deserializer.deserialize(message)
        assert packet != None, "Wrong data 2"

    def test_object_update(self):
        """test if the object update packet can be decoded"""

        message = OBJECT_UPDATE

        deserializer = UDPMessageDeserializer(settings = self.settings)
        packet = deserializer.deserialize(message)
        assert packet != None, "Wrong data"
        assert packet.name == 'ObjectUpdate', "Wrong packet"

        blocks = {}

        for block in packet.blocks:
            blocks[block] = 1

        self.assert_("RegionData" in blocks)
        self.assert_("ObjectData" in blocks)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPacketDecode))
    return suite



