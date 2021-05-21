
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
from binascii import unhexlify
from uuid import UUID

from hippolyzer.lib.base.datatypes import Vector3
from hippolyzer.lib.base.message.data_packer import TemplateDataPacker
from hippolyzer.lib.base.message.msgtypes import MsgType
from hippolyzer.lib.base.settings import Settings
from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer


class TestDeserializer(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        self.settings = Settings()
        self.settings.ENABLE_DEFERRED_PACKET_PARSING = False
        self.deserializer = UDPMessageDeserializer(settings=self.settings)

    def test_deserialize(self):
        body = b'\xff\xff\xff\xfb' + b'\x03' + \
               b'\x01\x00\x00\x00' + b'\x02\x00\x00\x00' + b'\x03\x00\x00\x00'
        message = b'\x00' + b'\x00\x00\x00\x01' + b'\x00' + body
        packet = self.deserializer.deserialize(message)

        assert packet.name == 'PacketAck', 'Incorrect deserialization'

    def test_chat(self):
        msg = Message('ChatFromViewer',
                      Block('AgentData', AgentID=UUID('550e8400-e29b-41d4-a716-446655440000'),
                            SessionID=UUID('550e8400-e29b-41d4-a716-446655440000')),
                      Block('ChatData', Message='Hi Locklainn Tester', Type=1, Channel=0))
        serializer = UDPMessageSerializer()
        packed_data = serializer.serialize(msg)

        packet = self.deserializer.deserialize(packed_data)
        data = packet.blocks
        self.assertEqual(data['ChatData'][0].vars['Message'], 'Hi Locklainn Tester')

    def test_simple_zero_coding(self):
        val = b"\x01\x00\x01\x01"
        decoded = self.deserializer.zero_code_expand(val)
        self.assertEqual(b"\x01\x00\x01", decoded)

    def test_wrap_zero_coding(self):
        val = b"\x01\x00\x00\x02\x01"
        decoded = self.deserializer.zero_code_expand(val)
        self.assertEqual(b"\x01" + (b"\x00" * 256) + b"\x00\x00\x01", decoded)

    def test_double_wrap_zero_coding(self):
        val = b"\x01\x00\x00\x00\x02\x01"
        decoded = self.deserializer.zero_code_expand(val)
        self.assertEqual(b"\x01" + (b"\x00" * 256 * 2) + b"\x00\x00\x01", decoded)

    def test_trailing_zero(self):
        val = b"\x00"
        decoded = self.deserializer.zero_code_expand(val)
        self.assertEqual(val, decoded)

    def test_vector3_from_bytes(self):
        # test the 72 byte ObjectUpdate.ObjectData.ObjectData case
        hex_string = '00000000000000000000803f6666da41660000432fffff422233e34100000000000000000000000000000000000000' \
                     '000000000000000000000000000e33de3c000000000000000000000000'
        position = TemplateDataPacker.unpack(unhexlify(hex_string)[16:16 + 12], MsgType.MVT_LLVector3)
        self.assertEqual(position, (128.00155639648438, 127.99840545654297, 28.399967193603516))
        self.assertIsInstance(position, Vector3)
