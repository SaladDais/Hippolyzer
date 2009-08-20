
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

#standard libraries
import unittest, doctest
from uuid import UUID

#local libraries
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.message.msgtypes import MsgType
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.udpdeserializer import UDPMessageDeserializer
from pyogp.lib.base.message.udpserializer import UDPMessageSerializer

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
        deserializer = UDPMessageDeserializer(settings = self.settings)
        packet = deserializer.deserialize(message)

        assert packet.name == 'PacketAck', 'Incorrect deserialization'


    def test_chat(self):
        msg = Message('ChatFromViewer',
                      Block('AgentData', AgentID=UUID('550e8400-e29b-41d4-a716-446655440000'),
                            SessionID=UUID('550e8400-e29b-41d4-a716-446655440000')),
                       Block('ChatData', Message='Hi Locklainn Tester', Type=1, Channel=0))
        serializer = UDPMessageSerializer()
        packed_data = serializer.serialize(msg)

        deserializer = UDPMessageDeserializer(settings = self.settings)
        packet = deserializer.deserialize(packed_data)
        data = packet.blocks
        assert data['ChatData'][0].vars['Message'].data == 'Hi Locklainn Tester',\
               'Message for chat is incorrect'



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDeserializer))
    return suite



