
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

from hippolyzer.lib.base.datatypes import *
from hippolyzer.lib.base.message.msgtypes import MsgType
from hippolyzer.lib.base.settings import Settings
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer
from hippolyzer.lib.base.message.data_packer import TemplateDataPacker


class TestSerializer(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        self.settings = Settings()
        self.settings.ENABLE_DEFERRED_PACKET_PARSING = False
        self.deserializer = UDPMessageDeserializer(settings=self.settings)
        self.serializer = UDPMessageSerializer()

    def test_serialize(self):
        body = b'\xff\xff\xff\xfb' + b'\x03' + \
               b'\x01\x00\x00\x00' + b'\x02\x00\x00\x00' + b'\x03\x00\x00\x00'
        message = b'\x00' + b'\x00\x00\x00\x01' + b'\x00' + body
        packet = self.deserializer.deserialize(message)
        packed_data = self.serializer.serialize(packet)
        assert packed_data == message, "Incorrect serialization"

    def test_acks_roundtrip(self):
        body = b'\xff\xff\xff\xfb' + b'\x03' + \
               b'\x01\x00\x00\x00' + b'\x02\x00\x00\x00' + b'\x03\x00\x00\x00'
        # Two acks
        trailer = b"\x00\x00\x00\x02\x00\x00\x00\x01\x02"
        message = b'\x10' + b'\x00\x00\x00\x01' + b'\x00' + body + trailer
        packet = self.deserializer.deserialize(message)
        self.assertEqual(packet.acks, (1, 2))
        self.assertEqual(self.serializer.serialize(packet), message)

    def test_template_data_packers(self):
        cases = {
            MsgType.MVT_FIXED: b"foobar",
            MsgType.MVT_VARIABLE: b"foobar\x00",
            MsgType.MVT_S8: -2,
            MsgType.MVT_U8: 2,
            MsgType.MVT_BOOL: 1,
            MsgType.MVT_LLUUID: UUID.random(),
            MsgType.MVT_IP_ADDR: "127.0.0.1",
            MsgType.MVT_IP_PORT: 500,
            MsgType.MVT_U16: 500,
            MsgType.MVT_U32: 500,
            MsgType.MVT_U64: 500,
            MsgType.MVT_S16: -500,
            MsgType.MVT_S32: -500,
            MsgType.MVT_S64: -500,
            MsgType.MVT_F32: 1.0,
            MsgType.MVT_F64: 1.0,
            MsgType.MVT_LLVector3: Vector3(),
            MsgType.MVT_LLVector3d: (0.0, 1.0, 0.0),
            MsgType.MVT_LLVector4: (0.0, 1.0, 0.0, 1.0),
            MsgType.MVT_LLQuaternion: Quaternion()
        }
        for case_type, case in cases.items():
            packed = TemplateDataPacker.pack(case, case_type)
            unpacked = TemplateDataPacker.unpack(packed, case_type)
            assert case == unpacked, (case_type, case, unpacked)

        # String case is special, it gets a null terminator.
        packed = TemplateDataPacker.pack("foobar", MsgType.MVT_VARIABLE)
        unpacked = TemplateDataPacker.unpack(packed, MsgType.MVT_VARIABLE)
        self.assertEqual(unpacked, b"foobar\x00")

    def test_simple_zero_coding(self):
        val = b"\x01\x00\x01"
        compressed = self.serializer.zero_code_compress(val)
        self.assertEqual(b"\x01\x00\x01\x01", compressed)

    def test_large_zero_coding(self):
        val = b"\x01" + (b"\x00" * 255) + b"\x00\x00\x01"
        compressed = self.serializer.zero_code_compress(val)
        # Make sure we didn't use the wrap case
        self.assertEqual(b"\x01\x00\xFF\x00\x02\x01", compressed)

    def test_twice_large_zero_coding(self):
        val = b"\x01" + (b"\x00" * 255 * 2) + b"\x00\x00\x01"
        compressed = self.serializer.zero_code_compress(val)
        self.assertEqual(b"\x01\x00\xFF\x00\xFF\x00\x02\x01", compressed)
