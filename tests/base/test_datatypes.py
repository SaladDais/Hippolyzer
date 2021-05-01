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
import pickle
import unittest
import uuid

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import *


class TestDatatypes(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        pass

    def test_vector3_new(self):
        vector = Vector3()
        self.assertEqual(vector, (0.0, 0.0, 0.0))

    def test_vector3_from_xyz(self):
        vector = Vector3(X=128.0, Y=128.0, Z=22.0)
        self.assertEqual(vector.X, 128.0)
        self.assertEqual(vector.Y, 128.0)
        self.assertEqual(vector.Z, 22.0)

    def test_vector3_addition(self):
        vector = Vector3(1, 2, 3)
        vector2 = Vector3(0, 1, 2)
        self.assertEqual(vector + vector2, (1.0, 3.0, 5.0))

    def test_vector3_subtraction(self):
        vector = Vector3(1, 2, 3)
        vector2 = Vector3(0, 1, 2)
        self.assertEqual(vector - vector2, (1.0, 1.0, 1.0))

    def test_vector3_comparison(self):
        vector = Vector3(1, 2, 3)
        self.assertTrue(vector >= (0, 1, 2))
        self.assertTrue(vector < (4, 4, 4))

    def test_vector3_iteration(self):
        self.assertEqual((1, 2, 3), tuple(x for x in Vector3(1, 2, 3)))

    def test_vector3_str(self):
        self.assertEqual(str(Vector3(0, 0, 0)), "<0.0, 0.0, 0.0>")

    def test_vector3_repr(self):
        self.assertEqual(repr(Vector3(0, 0, 0)), "Vector3(0.0, 0.0, 0.0)")

    def test_vector3_parse(self):
        self.assertEqual(Vector3(0, 1, 0), Vector3.parse("<0, 1, 0>"))

    def test_quaternion_new(self):
        quat = Quaternion()
        self.assertEqual(quat, (0.0, 0.0, 0.0, 1.0))

    def test_quaternion_from_xyzw(self):
        quat = Quaternion(X=128.0, Y=128.0, Z=22.0)
        self.assertEqual(quat, (128.0, 128.0, 22.0, 0.0))

    def test_uuid_from_bytes(self):
        tmp_uuid = uuid.UUID('2b7f7a6e-32c5-dbfd-e2c7-926d1a9f0aca')
        tmp_uuid2 = uuid.UUID('1dd5efe2-faaf-1864-5ac9-bc61c5d8d7ea')

        test_uuid = UUID(bytes=tmp_uuid.bytes)
        test_uuid2 = UUID(bytes=tmp_uuid2.bytes)

        self.assertEqual(test_uuid, uuid.UUID('2b7f7a6e-32c5-dbfd-e2c7-926d1a9f0aca'))
        self.assertEqual(test_uuid2, uuid.UUID('1dd5efe2-faaf-1864-5ac9-bc61c5d8d7ea'))

    def test_uuid_get_bytes(self):
        test_uuid = UUID(val='12345678-1234-1234-1234-123456789012')
        self.assertEqual(test_uuid.bytes, uuid.UUID('12345678-1234-1234-1234-123456789012').bytes)

    def test_uuid_from_string(self):
        uuid_string = '2b7f7a6e-32c5-dbfd-e2c7-926d1a9f0aca'
        self.assertEqual(UUID(val=uuid_string), uuid.UUID('2b7f7a6e-32c5-dbfd-e2c7-926d1a9f0aca'))

    def test_uuid_combine(self):
        first = UUID('00000000-0000-0000-0000-000000000000')
        second = uuid.UUID('00000000-0100-0000-0000-000000000000')
        combined = UUID.combine(first, second)
        self.assertEqual(combined, UUID('8c4b3740-2538-dc5d-1ec2-6cb50e2c348b'))

    def test_uuid_equality(self):
        first = UUID('00000000-0000-0000-0000-000000000000')
        second = uuid.UUID('00000000-0000-0000-0000-000000000000')
        self.assertEqual(second, first)

    def test_uuid_hash_equality(self):
        first = UUID('00000000-0000-0000-0000-000000000000')
        second = uuid.UUID('00000000-0000-0000-0000-000000000000')
        self.assertEqual(hash(first), hash(second))

    def test_uuid_xor(self):
        first = UUID('00000000-0000-0000-0000-000000000101')
        second = uuid.UUID('00000000-0000-0000-0000-000000000110')
        self.assertEqual(UUID('00000000-0000-0000-0000-000000000011'), first ^ second)

    def test_pickleable(self):
        orig = Vector3(1, 2, 3)
        val = pickle.loads(pickle.dumps(orig, protocol=pickle.HIGHEST_PROTOCOL))
        self.assertEqual(orig, val)

    def test_tuplecoord_llsd_serialization(self):
        orig = Vector3(1, 2, 3)
        val = llsd.parse_xml(llsd.format_xml(orig))
        self.assertIsInstance(val, list)
        self.assertEqual(orig, tuple(val))

    def test_uuid_llsd_serialization(self):
        orig = UUID.random()
        val = llsd.parse_binary(llsd.format_binary(orig))
        self.assertIsInstance(val, UUID)
        self.assertEqual(orig, val)
