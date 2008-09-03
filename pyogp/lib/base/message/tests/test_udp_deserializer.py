#standard libraries
import unittest, doctest
from uuid import UUID

#local libraries
from pyogp.lib.base.message.types import MsgType
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.interfaces import IPacket
from pyogp.lib.base.interfaces import IDeserialization, ISerialization
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


    def test_chat(self):
        msg = Message('ChatFromViewer',
                      Block('AgentData', AgentID=UUID('550e8400-e29b-41d4-a716-446655440000'),
                            SessionID=UUID('550e8400-e29b-41d4-a716-446655440000')),
                       Block('ChatData', Message='Hi Locklainn Tester', Type=1, Channel=0))
        packet = IPacket(msg)
        serializer = ISerialization(packet)
        packed_data = serializer.serialize()

        deserializer = IDeserialization(packed_data)
        packet = deserializer.deserialize()
        data = packet.message_data
        assert data.blocks['ChatData'][0].vars['Message'].data == 'Hi Locklainn Tester',\
               'Message for chat is incorrect'

        
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDeserializer))
    return suite
