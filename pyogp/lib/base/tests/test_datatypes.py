
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

# standard python modules
import unittest
from struct import pack
from binascii import unhexlify
import uuid

# pyogp
from pyogp.lib.base.datatypes import *

class TestDatatypes(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        pass

    def test_Vector3_from_bytes(self):

        # test the 72 byte ObjectUpdate.ObjectData.ObjectData case
        hex_string = '00000000000000000000803f6666da41660000432fffff422233e34100000000000000000000000000000000000000000000000000000000000000000e33de3c000000000000000000000000'
        data = unhexlify(hex_string)

        # grab the position embedded starting at position 16
        Position = Vector3(data, 16)

        self.assertEquals(Position.__dict__, {'Y': 127.99840545654297, 'X': 128.00155639648438, 'Z': 28.399967193603516})
        self.assertEquals(Position(), (128.00155639648438, 127.99840545654297, 28.399967193603516))

    def test_Vector3_get_bytes(self):

        vector = Vector3(X = 128.0, Y = 128.0, Z = 22.0)

        vector_tuple = ((float(128.0), float(128.0), float(22.0)))
        size = len(vector_tuple)
        self.assertEquals(vector.get_bytes(), struct.pack("<" + str(size) + "f", float(128.0), float(128.0), float(22.0)))

    def test_Vector3_new(self):

        vector = Vector3()

        self.assertEquals(vector.__dict__, {'Y': 0.0, 'X': 0.0, 'Z': 0.0})
        self.assertEquals(vector(), (0.0, 0.0, 0.0))

    def test_Vector3_from_XYZ(self):

        vector = Vector3(X=128.0, Y=128.0, Z=22.0)

        self.assertEquals(vector.__dict__, {'Y': 128.0, 'X': 128.0, 'Z': 22.0})
        self.assertEquals(vector.X, 128.0)
        self.assertEquals(vector.Y, 128.0)        
        self.assertEquals(vector.Z, 22.0)

    def test_Quaternion_from_bytes(self):

        # test the 72 byte ObjectUpdate.ObjectData.ObjectData case
        hex_string = '00000000000000000000803f6666da41660000432fffff422233e34100000000000000000000000000000000000000000000000000000000000000000e33de3c000000000000000000000000'
        data = unhexlify(hex_string)

        # grab the position embedded starting at position 16
        quat = Quaternion(data, 0)

        self.assertEquals(quat.__dict__, {'Y': 0.0, 'X': 0.0, 'Z': 1.0, 'W': 27.299999237060547})
        self.assertEquals(quat(), (0.0, 0.0, 1.0, 27.299999237060547))

    def test_Quaternion_get_bytes(self):

        quat = Quaternion(X = 128.0, Y = 128.0, Z = 22.0, W = 123.456)

        self.assertEquals(quat.get_bytes(), struct.pack("<4f", float(128.0), float(128.0), float(22.0), float(123.456)))

    def test_Quaternion_new(self):

        quat = Quaternion()

        self.assertEquals(quat.__dict__, {'Y': 0.0, 'X': 0.0, 'Z': 0.0, 'W': 0.0})
        self.assertEquals(quat(), (0.0, 0.0, 0.0, 0.0))

    def test_Quaternion_from_XYZW(self):

        quat = Quaternion(X=128.0, Y=128.0, Z=22.0, W=0.0)

        self.assertEquals(quat.__dict__, {'Y': 128.0, 'X': 128.0, 'Z': 22.0, 'W': 0.0})
        self.assertEquals(quat(), (128.0, 128.0, 22.0, 0.0))

    def test_UUID_from_bytes(self):

        tmp_uuid = uuid.UUID('2b7f7a6e-32c5-dbfd-e2c7-926d1a9f0aca')
        tmp_uuid2 = uuid.UUID('1dd5efe2-faaf-1864-5ac9-bc61c5d8d7ea')

        test_uuid = UUID(bytes = tmp_uuid.bytes, offset = 0)
        test_uuid2 = UUID(bytes = tmp_uuid2.bytes, offset = 0)

        self.assertEquals(test_uuid.data(), uuid.UUID('2b7f7a6e-32c5-dbfd-e2c7-926d1a9f0aca'))
        self.assertEquals(test_uuid2.data(), uuid.UUID('1dd5efe2-faaf-1864-5ac9-bc61c5d8d7ea'))

    def test_UUID_get_bytes(self):

        test_uuid = UUID(string = '12345678-1234-1234-1234-123456789012')

        self.assertEquals(test_uuid.get_bytes(), uuid.UUID('12345678-1234-1234-1234-123456789012').bytes)


    def test_UUID_new(self):

        tmp_uuid = UUID()

        self.assertEquals(tmp_uuid.__dict__, {'uuid': uuid.UUID('00000000-0000-0000-0000-000000000000')})
        self.assertEquals(tmp_uuid(), uuid.UUID('00000000-0000-0000-0000-000000000000'))

    def test_UUID_from_string(self):

        uuid_string = '2b7f7a6e-32c5-dbfd-e2c7-926d1a9f0aca'

        self.assertEquals(UUID(string = uuid_string).data(), uuid.UUID('2b7f7a6e-32c5-dbfd-e2c7-926d1a9f0aca'))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDatatypes))
    return suite



