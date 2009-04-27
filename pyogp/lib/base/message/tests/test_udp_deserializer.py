#standard libraries
import unittest, doctest
from uuid import UUID

#local libraries
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.message.types import MsgType
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.packet import UDPPacket
from pyogp.lib.base.message.udpdeserializer import UDPPacketDeserializer
from pyogp.lib.base.message.udpserializer import UDPPacketSerializer

#from indra.base.lluuid import UUID

class TestDeserializer(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        self.settings = Settings()
        self.settings.ENABLE_DEFERRED_PACKET_PARSING = False

    def test_deserialize(self):
        message = '\xff\xff\xff\xfb' + '\x03' + \
                  '\x01\x00\x00\x00' + '\x02\x00\x00\x00' + '\x03\x00\x00\x00'
        message = '\x00' + '\x00\x00\x00\x01' +'\x00' + message
        deserializer = UDPPacketDeserializer(settings = self.settings)
        packet = deserializer.deserialize(message)
        data = packet.message_data
        assert packet.name == 'PacketAck', 'Incorrect deserialization'


    def test_chat(self):
        msg = Message('ChatFromViewer',
                      Block('AgentData', AgentID=UUID('550e8400-e29b-41d4-a716-446655440000'),
                            SessionID=UUID('550e8400-e29b-41d4-a716-446655440000')),
                       Block('ChatData', Message='Hi Locklainn Tester', Type=1, Channel=0))
        packet = UDPPacket(msg)
        serializer = UDPPacketSerializer()
        packed_data = serializer.serialize(packet)

        deserializer = UDPPacketDeserializer(settings = self.settings)
        packet = deserializer.deserialize(packed_data)
        data = packet.message_data
        assert data.blocks['ChatData'][0].vars['Message'].data == 'Hi Locklainn Tester',\
               'Message for chat is incorrect'



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDeserializer))
    return suite

"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

