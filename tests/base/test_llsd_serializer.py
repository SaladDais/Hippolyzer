
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

from hippolyzer.lib.base.message.llsd_msg_serializer import LLSDMessageSerializer
from hippolyzer.lib.base.message.message import Message, Block


class TestLLSDSerializer(unittest.TestCase):
    def setUp(self):
        self.serializer = LLSDMessageSerializer()
        self.test_msg = Message(
            "EnableSimulator",
            Block(
                "SimulatorInfo",
                Handle=200,
                IP="127.0.0.1",
                Port=201,
            ),
        )
        self.test_dict = {
            "message": "EnableSimulator",
            "body": {
                "SimulatorInfo": [{
                    "Handle": b'\x00\x00\x00\x00\x00\x00\x00\xc8',
                    "IP": b"\x7f\x00\x00\x01",
                    "Port": 201,
                }]
            }
        }
        self.test_xml = b'<?xml version="1.0" ?><llsd><map><key>message</key><string>EnableSimulator</string>' \
                        b'<key>body</key><map><key>SimulatorInfo</key><array><map><key>Handle</key><binary>' \
                        b'AAAAAAAAAMg=</binary><key>IP</key><binary>fwAAAQ==</binary><key>Port</key><integer>' \
                        b'201</integer></map></array></map></map></llsd>'

    def test_dict_serialization(self):
        msg_dict = self.serializer.serialize(self.test_msg, as_dict=True)
        self.assertEqual(msg_dict, self.test_dict)

    def test_xml_serialization(self):
        msg_xml = self.serializer.serialize(self.test_msg)
        self.assertEqual(msg_xml, self.test_xml)

    def test_dict_deserialization(self):
        msg = self.serializer.deserialize(self.test_dict)
        self.assertEqual(self.test_msg.to_dict(), msg.to_dict())

    def test_xml_deserialization(self):
        msg = self.serializer.deserialize(self.test_xml)
        self.assertEqual(self.test_msg.to_dict(), msg.to_dict())
