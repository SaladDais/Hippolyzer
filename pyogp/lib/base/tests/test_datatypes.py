"""
@file test_datatypes.py
@date 2009-03-18
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

# standard python modules
import unittest
from struct import pack
from binascii import unhexlify 

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

    def test_Vector3_new(self):

        vector = Vector3()

        self.assertEquals(vector.__dict__, {'Y': 0.0, 'X': 0.0, 'Z': 0.0})
        self.assertEquals(vector(), (0.0, 0.0, 0.0))

    def test_Vector3_from_XYZ(self):

        vector = Vector3(X=128.0, Y=128.0, Z=22.0)

        self.assertEquals(vector.__dict__, {'Y': 128.0, 'X': 128.0, 'Z': 22.0})
        self.assertEquals(vector(), (128.0, 128.0, 22.0))

    def test_Quaternion_from_bytes(self):

        # test the 72 byte ObjectUpdate.ObjectData.ObjectData case
        hex_string = '00000000000000000000803f6666da41660000432fffff422233e34100000000000000000000000000000000000000000000000000000000000000000e33de3c000000000000000000000000'
        data = unhexlify(hex_string)

        # grab the position embedded starting at position 16
        quat = Quaternion(data, 0)

        self.assertEquals(quat.__dict__, {'Y': 0.0, 'X': 0.0, 'Z': 1.0, 'W': 27.299999237060547})
        self.assertEquals(quat(), (0.0, 0.0, 1.0, 27.299999237060547))

    def test_Quaternion_new(self):

        quat = Quaternion()

        self.assertEquals(quat.__dict__, {'Y': 0.0, 'X': 0.0, 'Z': 0.0, 'W': 0.0})
        self.assertEquals(quat(), (0.0, 0.0, 0.0, 0.0))

    def test_Quaternion_from_XYZW(self):

        quat = Quaternion(X=128.0, Y=128.0, Z=22.0, W=0.0)

        self.assertEquals(quat.__dict__, {'Y': 128.0, 'X': 128.0, 'Z': 22.0, 'W': 0.0})
        self.assertEquals(quat(), (128.0, 128.0, 22.0, 0.0))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDatatypes))
    return suite