"""
@file test_udp_serializer.py
@date 2008-09-16
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

#standard libraries
import unittest, doctest
from uuid import UUID

#local libraries
from pyogp.lib.base.message.types import MsgType
from pyogp.lib.base.message.interfaces import IPacket
from pyogp.lib.base.interfaces import ISerialization, IDeserialization
from pyogp.lib.base.registration import init

#from indra.base.lluuid import UUID

class TestSerializer(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        init()
        
    def test_serialize(self):
        message = '\xff\xff\xff\xfb' + '\x03' + \
                  '\x01\x00\x00\x00' + '\x02\x00\x00\x00' + '\x03\x00\x00\x00'
        message = '\x00' + '\x00\x00\x00\x01' +'\x00' + message
        deserializer = IDeserialization(message)
        packet = deserializer.deserialize()
        #print packet.send_flags
        #print packet.packet_id
        data = packet.message_data

        serializer = ISerialization(packet)
        packed_data = serializer.serialize()
        assert packed_data == message, "Incorrect serialization"
        
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSerializer))
    return suite
