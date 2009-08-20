
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
from pyogp.lib.base.exc import *
from pyogp.lib.base.region import Region
from pyogp.lib.base.message.message import Message, Block

# pyogp tests
import pyogp.lib.base.tests.config 

class TestRegion(unittest.TestCase):

    def setUp(self):

        self.region = Region(global_x = 256, global_y = 256, seed_capability_url = 'fake_url', udp_blacklist = [], sim_ip = 1, sim_port = 1, circuit_code = 1, agent = None, settings = None, message_handler = None)

    def tearDown(self):

        pass

    def test_region_basic_attributes(self):

        self.assertEquals(self.region.sim_ip, 1)
        self.assertEquals(self.region.grid_y, 1)
        self.assertEquals(self.region.grid_x, 1)
        self.assertEquals(self.region.global_y, 256)
        self.assertEquals(self.region.global_x, 256)
        self.assertEquals(self.region.seed_capability_url, 'fake_url')
        self.assertEquals(self.region.agent, None)
        self.assertEquals(self.region.circuit_code, 1)

    def test_enqueue_message(self):

        fake_packet = Message('AgentDataUpdateRequest')
        fake_packet2 = Message('AgentDataUpdateRequest')

        self.region.enqueue_message(fake_packet)
        self.region.enqueue_message(fake_packet2)

        self.assertEquals(len(self.region.packet_queue), 2)

        for data in self.region.packet_queue:
            #self.assertEquals(('<class \'pyogp.lib.base.message.message.Message\'>', False), (str(type(data[0])), False))
            pass
            # ToDo: fix this test!

    def test_enqueue_urgent_message(self):

        fake_packet = Message('AgentDataUpdateRequest')
        fake_packet2 = Message('AgentDataUpdateRequest')

        fake_urgent_packet = Message('SetStartLocation')

        self.region.enqueue_message(fake_packet)
        self.region.enqueue_message(fake_packet2)
        self.region.send_message_next(fake_urgent_packet)

        self.assertEquals(len(self.region.packet_queue), 3)
        self.assertEquals(self.region.packet_queue[0][0].name, 'SetStartLocation')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRegion))
    return suite



