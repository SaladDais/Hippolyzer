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

import logging
import unittest
import binascii

from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer
from hippolyzer.lib.base.settings import Settings
from hippolyzer.lib.base.message.data import msg_tmpl
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.message.template_parser import MessageTemplateParser
from hippolyzer.lib.base.message.template_dict import TemplateDictionary

AGENT_DATA_UPDATE = "C0 00 00 00 02 00 FF FF 01 83 1C 8A 77 67 E3 7B 42 2E AF B3 85 09 31 97 CA D1 03 4A 42 00 01 06 " \
                    "4B 72 61 66 74 00 01 01 00 1A "
AGENT_DATA_UPDATE = binascii.unhexlify(''.join(AGENT_DATA_UPDATE.split()))

AGENT_ANIMATION = "40 00 00 00 0A 00 05 1C 8A 77 67 E3 7B 42 2E AF B3 85 09 31 97 CA D1 4B 6F FF 1F B5 67 41 FD 85 EF" \
                  " A1 98 3B F2 B5 77 01 EF CF 67 0C 2D 18 81 28 97 3A 03 4E BC 80 6B 67 00 01 00 "
AGENT_ANIMATION = binascii.unhexlify(''.join(AGENT_ANIMATION.split()))

OBJECT_UPDATE = "C0 00 00 00 51 00 0C 00 01 EA 03 00 02 E6 03 00 01 BE FF 01 06 BC 8E 0B 00 01 69 94 8C 6A 4D 22 1B " \
                "66 EC E4 AC 31 63 93 CB 4B 57 89 98 01 09 03 00 01 51 40 88 3E 51 40 88 3E 51 40 88 3E 3C A2 44 B3 " \
                "42 9A 68 2B 42 C8 5B D1 41 00 18 4B 8C FF 3E BD 76 FF BE C5 44 00 01 BF 00 10 50 04 00 01 10 20 05 " \
                "00 04 64 64 00 0F 2E 00 01 A1 33 DC 77 0A 1A BB 27 A7 2E 78 64 63 AB 94 AB 00 08 80 3F 00 03 80 3F " \
                "00 0F 10 13 FF 00 08 80 3F 8F C2 F5 3D 00 0A 56 6F 43 CC 00 01 02 00 03 04 00 02 04 00 02 64 26 00 " \
                "03 0E 00 01 0E 00 01 19 00 01 80 00 01 80 00 01 80 00 01 80 00 01 80 00 01 80 91 11 D2 5E 2F 12 8F " \
                "81 55 A7 40 3A 78 B3 0E 2D 00 10 03 01 00 03 1E 25 6E A2 FF C5 E0 83 00 01 06 00 01 0D 0D 01 00 11 " \
                "0E DC 9B 83 98 9A 4A 76 AC C3 DB BF 37 54 61 88 00 22 "
OBJECT_UPDATE = binascii.unhexlify(''.join(OBJECT_UPDATE.split()))

COARSE_LOCATION_UPDATE = b'\x00\x00\x00\x00E\x00\xff\x06\x00\xff\xff\xff\xff\x00'

UNKNOWN_PACKET = b'\x00\x00\x00\x00E\x00\xff\xf0\x00\xff\xff\xff\xff\x00'


class TestPacketDecode(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        self.maxDiff = None
        self.template_file = msg_tmpl
        parser = MessageTemplateParser(self.template_file)
        self.template_list = parser.message_templates
        self.template_dict = TemplateDictionary(self.template_list)

        self.settings = Settings()
        self.settings.ENABLE_DEFERRED_PACKET_PARSING = False

    def test_agent_data_update(self):
        """test if the agent data update packet can be decoded"""
        message = AGENT_DATA_UPDATE
        deserializer = UDPMessageDeserializer(settings=self.settings)
        packet = deserializer.deserialize(message)
        assert packet is not None, "Wrong data"
        assert packet.name == 'AgentDataUpdate', "Wrong packet"
        assert packet.blocks['AgentData'][0].vars['LastName'] == 'Kraft', \
            "Wrong last name for agent update"
        assert packet.blocks['AgentData'][0].vars['FirstName'] == 'JB', \
            "Wrong first name for agent update"

    def test_agent_animation(self):
        """test if the agent data update packet can be decoded"""
        message = AGENT_ANIMATION
        deserializer = UDPMessageDeserializer(settings=self.settings)
        packet = deserializer.deserialize(message)
        assert packet is not None, "Wrong data 2"

    def test_object_update(self):
        """test if the object update packet can be decoded"""

        message = OBJECT_UPDATE

        deserializer = UDPMessageDeserializer(settings=self.settings)
        packet = deserializer.deserialize(message)
        assert packet is not None, "Wrong data"
        assert packet.name == 'ObjectUpdate', "Wrong packet"

        blocks = {}

        for block in packet.blocks:
            blocks[block] = 1

        self.assertTrue("RegionData" in blocks)
        self.assertTrue("ObjectData" in blocks)

    def test_course_location_roundtrips(self):
        message = COARSE_LOCATION_UPDATE
        deserializer = UDPMessageDeserializer(settings=self.settings)
        serializer = UDPMessageSerializer()
        parsed = deserializer.deserialize(message)
        logging.debug("Parsed blocks: %r " % (list(parsed.blocks.keys()),))
        self.assertEqual(message, serializer.serialize(parsed))

    def test_unknown_packet_roundtrips(self):
        message = UNKNOWN_PACKET
        deserializer = UDPMessageDeserializer(settings=self.settings)
        serializer = UDPMessageSerializer()
        parsed = deserializer.deserialize(message)
        logging.debug("Parsed blocks: %r " % (list(parsed.blocks.keys()),))
        self.assertEqual("UnknownMessage:240", parsed.name)
        self.assertEqual(message, serializer.serialize(parsed))
