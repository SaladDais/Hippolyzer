
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
from binascii import unhexlify

#related

# pyogp
from pyogp.lib.base.appearance import *
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.agent import Agent
from pyogp.lib.base.region import Region
from pyogp.lib.base.datatypes import *
# pyogp messaging
from pyogp.lib.base.message.udpdeserializer import UDPMessageDeserializer

# pyogp tests
import pyogp.lib.base.tests.config 

class TestAppearance(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()
        self.agent = Agent()
        self.appearance = AppearanceManager(self.agent, settings = self.settings)
        self.agent.agent_id = UUID("01234567-89ab-cdef-0123-456789abcdef")
        self.agent.session_id = UUID("fedcba98-7654-3210-fedc-ba9876543210")
        self.agent.region = DummyRegion()
        
    def tearDown(self):
        pass

    def test_request_agent_wearables(self):
        self.agent.appearance.request_agent_wearables()
        packet_list = self.agent.region.dummy_packet_holder
        self.assertEquals(len(packet_list), 1)
        packet = packet_list.pop()
        self.assertEquals(self.agent.agent_id, packet.blocks["AgentData"][0].get_variable('AgentID').data)
        self.assertEquals(self.agent.session_id, packet.blocks["AgentData"][0].get_variable('SessionID').data)

    def test_request_agent_noAgentIDorSessionID(self):
        packet_list = self.agent.region.dummy_packet_holder
        self.agent.agent_id = None
        self.agent.appearance.request_agent_wearables()
        self.assertEquals(len(packet_list), 0)
        self.agent.agent_id = UUID()
        self.agent.appearance.request_agent_wearables()
        self.assertEquals(len(packet_list), 0)
        self.agent.agent_id = UUID("01234567-89ab-cdef-0123-456789abcdef")
        self.agent.session_id = None
        self.agent.appearance.request_agent_wearables()
        self.assertEquals(len(packet_list), 0)
        self.agent.session_id = UUID()
        self.agent.appearance.request_agent_wearables()
        self.assertEquals(len(packet_list), 0)
        
   
    def test_send_AgentIsNowWearing(self):
        pass
    
class DummyRegion(Region):
    dummy_packet_holder = []
    def enqueue_message(self, packet, reliable = False):
        self.dummy_packet_holder.append(packet)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAppearance))
    return suite
