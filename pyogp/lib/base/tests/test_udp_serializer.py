#standard libraries
import unittest, doctest
from uuid import UUID

#local libraries
from pyogp.lib.base.message.message_types import MsgType
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
        print repr(packed_data)
        assert packed_data == message, "Incorrect serialization"
        
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSerializer))
    return suite
