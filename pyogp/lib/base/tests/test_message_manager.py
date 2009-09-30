
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
from pyogp.lib.client.region import Region

# pyogp tests
import pyogp.lib.base.tests.config 

from eventlet import api

class TestMessageManager(unittest.TestCase):

    def setUp(self):
        region = Region()
        region.sim_ip = '127.0.0.1'
        region.sim_port = '9009'
        self.message_manager = MessageManager(region, capabilities={'EventQueueGet' : Capability('EventQueueGet', 'http://127.0.0.1')})
                                              
    def tearDown(self):
        pass

    def test_start_stop_monitors(self):
        self.message_manager.start_monitors()
        api.sleep(0)
        self.assertTrue(self.message_manager._is_running)
        self.assertTrue(self.message_manager.event_queue._running)
        self.message_manager.stop_monitors()
        api.sleep(0)
        self.assertFalse(self.message_manager._is_running)
        #self.assertFalse(self.message_manager.event_queue._running)
        
    def test_enqueue_message(self):
        pass

    def test_send_udp_message(self):
        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMessageManager))
    return suite
