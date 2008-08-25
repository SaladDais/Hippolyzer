#standard libraries
import unittest, doctest
from uuid import UUID

#local libraries
from pyogp.lib.base.message.message_types import MsgType
#import pyogp.lib.base.message.udpdeserializer
from pyogp.lib.base.interfaces import IDeserialization
from pyogp.lib.base.registration import init

#from indra.base.lluuid import UUID

class TestDeserializer(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        init()
        
    def test_deserialize(self):
        message = '\xff\xff\xff\xfb' + '\x03' + \
                  '\x01\x00\x00\x00' + '\x02\x00\x00\x00' + '\x03\x00\x00\x00'
        message = '\x00' + '\x00\x00\x00\x01' +'\x00' + message
        deserializer = IDeserialization(message)
        packet = deserializer.deserialize()
        data = packet.message_data
        assert packet.name == 'PacketAck', 'Incorrect deserialization'
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDeserializer))
    return suite
