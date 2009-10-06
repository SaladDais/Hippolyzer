
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

# standard python libs
import unittest

# pyogp
from pyogp.lib.base.message_manager import MessageManager
from pyogp.lib.base.caps import Capability
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.tests.mockup_net import MockupUDPServer, MockupUDPClient
from pyogp.lib.base.message.circuit import Host
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher

# pyogp tests
import pyogp.lib.base.tests.config 

from eventlet import api

class TestMessageManager(unittest.TestCase):

    def setUp(self):
        self.host = Host((MockupUDPServer(), 80))
        self.message_manager = MessageManager(self.host,
                                              capabilities={'EventQueueGet' : Capability('EventQueueGet', 'http://127.0.0.1')})

        
    def tearDown(self):
        pass

    def test_start_stop_monitors(self):
        self.message_manager.start_monitors()
        api.sleep(0)
        self.assertTrue(self.message_manager._is_running)
        self.assertTrue(self.message_manager.event_queue._running)
        self.message_manager.stop_monitors()
        api.sleep(2)
        self.assertFalse(self.message_manager._is_running)
        self.assertTrue(self.message_manager.event_queue.stopped)
        self.assertFalse(self.message_manager.event_queue._running)
        
    def test_enqueue_message(self):
        message = Message('TestMessage1',
                          Block('TestBlock1',
                                Test1 = 0),
                          Block('NeighborBlock',
                                Test0 = 0,
                                Test1 = 1,
                                Test2 = 2))
        self.message_manager.enqueue_message(message,
                                             reliable = True)
        self.assertEqual(self.message_manager.outgoing_queue[0][0].name,
                         'TestMessage1')
        self.assertTrue(self.message_manager.outgoing_queue[0][1])
        message2 = Message('TestMessage2',
                          Block('TestBlock1',
                                Test1 = 0),
                          Block('NeighborBlock',
                                Test0 = 0,
                                Test1 = 1,
                                Test2 = 2))
        self.message_manager.enqueue_message(message2,
                                             reliable = False,
                                             now = True)
        self.assertEqual(self.message_manager.outgoing_queue[0][0].name,
                         'TestMessage2')
        self.assertFalse(self.message_manager.outgoing_queue[0][1])
        

    def test_send_udp_message(self):
        self.message_manager.udp_dispatcher = UDPDispatcher(MockupUDPClient(),
                                                            self.message_manager.settings,
                                                            self.message_manager.message_handler)
        message = Message('PacketAck',
                      Block('Packets', ID=0x00000003))
        buf =  self.message_manager.send_udp_message(message)
        assert buf == \
               '\x00' + '\x00\x00\x00\x01' + '\x00' + '\xff\xff\xff\xfb' + \
               '\x01' + '\x03\x00\x00\x00', \
               'Received: ' + repr(buf) + '  ' + \
               'Expected: ' + repr('\x00' + '\x00\x00\x00\x01' + '\x00' + \
                            '\xff\xff\xff\xfb' + '\x01' + '\x03\x00\x00\x00')
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMessageManager))
    return suite
