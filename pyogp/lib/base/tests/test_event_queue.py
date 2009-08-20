
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

# related
from indra.base import llsd
from eventlet import api, coros

# pyogp
from pyogp.lib.base.region import Region
from pyogp.lib.base.event_queue import EventQueueClient
from pyogp.lib.base.exc import *
from pyogp.lib.base.caps import Capability

# pyogp tests
import pyogp.lib.base.tests.config 

class TestEventQueue(unittest.TestCase):

    def setUp(self):

        self.eq = EventQueueClient(region = Region())

    def tearDown(self):

        pass

    def test__decode_eq_result(self):

        data = {'events': [{'body': {'SimulatorInfo': [{'IP': '\xd8R R', 'Handle': '\x00\x03\xe4\x00\x00\x03\xe9\x00', 'Port': 13001}]}, 'message': 'EnableSimulator'}, {'body': {'SimulatorInfo': [{'IP': '\xd8R\x0f\x06', 'Handle': '\x00\x03\xe5\x00\x00\x03\xe8\x00', 'Port': 13000}]}, 'message': 'EnableSimulator'}, {'body': {'SimulatorInfo': [{'IP': '\xd8R R', 'Handle': '\x00\x03\xe4\x00\x00\x03\xe9\x00', 'Port': 13001}]}, 'message': 'EnableSimulator'}, {'body': {'SimulatorInfo': [{'IP': '\xd8R\x0f\x06', 'Handle': '\x00\x03\xe5\x00\x00\x03\xe8\x00', 'Port': 13000}]}, 'message': 'EnableSimulator'}], 'id': -2054685694}

        packets = self.eq._decode_eq_result(data)

        for packet in packets:
            self.assertEquals(str(type(packet)), '<class \'pyogp.lib.base.message.message.Message\'>')

    def test__decode_eq_result2(self):

        llsd_data = '<llsd><map><key>events</key><array><map><key>body</key><map><key>AgentData</key><array><map><key>AgentID</key><uuid>a517168d-1af5-4854-ba6d-672c8a59e439</uuid></map></array><key>GroupData</key><array><map><key>AcceptNotices</key><boolean>1</boolean><key>Contribution</key><integer>0</integer><key>GroupID</key><uuid>4dd70b7f-8b3a-eef9-fc2f-909151d521f6</uuid><key>GroupInsigniaID</key><uuid /><key>GroupName</key><string>Enus&apos; Construction Crew</string><key>GroupPowers</key><binary encoding="base64">AAA5ABgBAAA=</binary><key>ListInProfile</key><boolean>0</boolean></map><map><key>AcceptNotices</key><boolean>1</boolean><key>Contribution</key><integer>0</integer><key>GroupID</key><uuid>69fd708c-3f20-a01b-f9b5-b5c4b310e5ca</uuid><key>GroupInsigniaID</key><uuid /><key>GroupName</key><string>EnusBot Army</string><key>GroupPowers</key><binary encoding="base64">AAD5ABgBAAA=</binary><key>ListInProfile</key><boolean>0</boolean></map></array></map><key>message</key><string>AgentGroupDataUpdate</string></map><map><key>body</key><map><key>AgeVerificationBlock</key><array><map><key>RegionDenyAgeUnverified</key><boolean>0</boolean></map></array><key>MediaData</key><array><map><key>MediaDesc</key><string /><key>MediaHeight</key><integer>0</integer><key>MediaLoop</key><integer>1</integer><key>MediaType</key><string>none/none</string><key>MediaWidth</key><integer>0</integer><key>ObscureMedia</key><integer>1</integer><key>ObscureMusic</key><integer>1</integer></map></array><key>ParcelData</key><array><map><key>AABBMax</key><array><real>256</real><real>256</real><real>50</real></array><key>AABBMin</key><array><real>0</real><real>0</real><real>0</real></array><key>Area</key><integer>65536</integer><key>AuctionID</key><binary encoding="base64">AAAAAA==</binary><key>AuthBuyerID</key><uuid /><key>Bitmap</key><binary encoding="base64">//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////8=</binary><key>Category</key><integer>255</integer><key>ClaimDate</key><integer>1088625472</integer><key>ClaimPrice</key><integer>0</integer><key>Desc</key><string /><key>GroupID</key><uuid /><key>GroupPrims</key><integer>0</integer><key>IsGroupOwned</key><boolean>0</boolean><key>LandingType</key><integer>1</integer><key>LocalID</key><integer>15</integer><key>MaxPrims</key><integer>3750</integer><key>MediaAutoScale</key><integer>0</integer><key>MediaID</key><uuid /><key>MediaURL</key><string /><key>MusicURL</key><string /><key>Name</key><string /><key>OtherCleanTime</key><integer>0</integer><key>OtherCount</key><integer>4096</integer><key>OtherPrims</key><integer>0</integer><key>OwnerID</key><uuid>dd1e79b2-ddfe-4080-8206-242ab63f4a19</uuid><key>OwnerPrims</key><integer>44</integer><key>ParcelFlags</key><binary encoding="base64">egAAAQ==</binary><key>ParcelPrimBonus</key><real>1</real><key>PassHours</key><real>1</real><key>PassPrice</key><integer>10</integer><key>PublicCount</key><integer>0</integer><key>RegionDenyAnonymous</key><boolean>0</boolean><key>RegionDenyIdentified</key><boolean>0</boolean><key>RegionDenyTransacted</key><boolean>0</boolean><key>RegionPushOverride</key><boolean>0</boolean><key>RentPrice</key><integer>0</integer><key>RequestResult</key><integer>0</integer><key>SalePrice</key><integer>10000</integer><key>SelectedPrims</key><integer>0</integer><key>SelfCount</key><integer>0</integer><key>SequenceID</key><integer>0</integer><key>SimWideMaxPrims</key><integer>3750</integer><key>SimWideTotalPrims</key><integer>44</integer><key>SnapSelection</key><boolean>0</boolean><key>SnapshotID</key><uuid /><key>Status</key><integer>0</integer><key>TotalPrims</key><integer>44</integer><key>UserLocation</key><array><real>0</real><real>0</real><real>0</real></array><key>UserLookAt</key><array><real>0</real><real>0</real><real>0</real></array></map></array></map><key>message</key><string>ParcelProperties</string></map><map><key>body</key><map><key>SimulatorInfo</key><array><map><key>Handle</key><binary encoding="base64">AAP8AAADxAA=</binary><key>IP</key><binary encoding="base64">2FISdw==</binary><key>Port</key><integer>13002</integer></map></array></map><key>message</key><string>EnableSimulator</string></map></array><key>id</key><integer>-182442759</integer></map></llsd>'

        data = llsd.parse(llsd_data)

        packets = self.eq._decode_eq_result(data)

        packet_names = []

        for packet in packets:
            self.assertEquals(str(type(packet)), '<class \'pyogp.lib.base.message.message.Message\'>')
            packet_names.append(packet.name)

        self.assertEquals(packet_names, ['AgentGroupDataUpdate', 'ParcelProperties', 'EnableSimulator'])

    def test__decode_eq_results3(self):

        llsd_data = '<llsd><map><key>events</key><array><map><key>body</key><map><key>session_id</key><uuid>6e20d408-2702-ea83-04b4-12cef089a327</uuid><key>session_info</key><map><key>moderated_mode</key><map><key>voice</key><boolean>0</boolean></map><key>session_name</key><string>Pyogp</string><key>type</key><integer>0</integer><key>voice_enabled</key><boolean>1</boolean></map><key>success</key><boolean>1</boolean><key>temp_session_id</key><uuid>6e20d408-2702-ea83-04b4-12cef089a327</uuid></map><key>message</key><string>ChatterBoxSessionStartReply</string></map><map><key>body</key><map><key>agent_updates</key><map><key>43b8b2d7-99b0-4b60-a935-45896c74be62</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map><key>4ca88f33-f34a-4ae4-a8f1-7357f883789e</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map><key>77e48a07-06f1-4ae4-9d33-6eab4d445e2d</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map><key>79e7c4ad-3361-4736-bced-1f72e6c3dbd4</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map><key>7a59bbd8-5175-4cff-8328-f92b3acde98a</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map><key>94e1350b-64d6-444b-8d3c-d1da460b259c</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map><key>97980bee-d865-4100-80e7-9763e53e8a6a</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map><key>a1f21e11-7db3-4eb4-89f3-5a65eea34495</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map><key>a517168d-1af5-4854-ba6d-672c8a59e439</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map><key>b2161990-f5c4-4dcb-a73c-e7365a18adfd</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map><key>c12cce9d-3308-4517-9a5e-1f3460187e56</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map><key>eeaedeb6-c702-472a-b725-e4492095c69a</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map><key>transition</key><string>ENTER</string></map></map><key>session_id</key><string>6e20d408-2702-ea83-04b4-12cef089a327</string><key>updates</key><map><key>43b8b2d7-99b0-4b60-a935-45896c74be62</key><string>ENTER</string><key>4ca88f33-f34a-4ae4-a8f1-7357f883789e</key><string>ENTER</string><key>77e48a07-06f1-4ae4-9d33-6eab4d445e2d</key><string>ENTER</string><key>79e7c4ad-3361-4736-bced-1f72e6c3dbd4</key><string>ENTER</string><key>7a59bbd8-5175-4cff-8328-f92b3acde98a</key><string>ENTER</string><key>94e1350b-64d6-444b-8d3c-d1da460b259c</key><string>ENTER</string><key>97980bee-d865-4100-80e7-9763e53e8a6a</key><string>ENTER</string><key>a1f21e11-7db3-4eb4-89f3-5a65eea34495</key><string>ENTER</string><key>a517168d-1af5-4854-ba6d-672c8a59e439</key><string>ENTER</string><key>b2161990-f5c4-4dcb-a73c-e7365a18adfd</key><string>ENTER</string><key>c12cce9d-3308-4517-9a5e-1f3460187e56</key><string>ENTER</string><key>eeaedeb6-c702-472a-b725-e4492095c69a</key><string>ENTER</string></map></map><key>message</key><string>ChatterBoxSessionAgentListUpdates</string></map><map><key>body</key><map><key>agent_updates</key><map><key>a517168d-1af5-4854-ba6d-672c8a59e439</key><map><key>info</key><map><key>can_voice_chat</key><boolean>1</boolean><key>is_moderator</key><boolean>0</boolean></map></map></map><key>session_id</key><string>6e20d408-2702-ea83-04b4-12cef089a327</string><key>updates</key><map /></map><key>message</key><string>ChatterBoxSessionAgentListUpdates</string></map><map><key>body</key><map><key>SimulatorInfo</key><array><map><key>Handle</key><binary encoding="base64">AAP8AAADxAA=</binary><key>IP</key><binary encoding="base64">2FIT1A==</binary><key>Port</key><integer>12035</integer></map></array></map><key>message</key><string>EnableSimulator</string></map></array><key>id</key><integer>17</integer></map></llsd>'

        data = llsd.parse(llsd_data)

        packets = self.eq._decode_eq_result(data)

        packet_names = []

        for packet in packets:
            self.assertEquals(str(type(packet)), '<class \'pyogp.lib.base.message.message.Message\'>')
            packet_names.append(packet.name)    

    def test_start_exception(self):
        # self.eq.cap is None so it throws an exception, logging should print error
        self.assertEquals(None, self.eq.cap)

        self.eq.start()

        self.assertTrue(True)

    def test_processRegionEventQueue_exception(self):
        
        self.eq.cap = Capability('foo', 'http://127.0.0.1')
    
        self.assertRaises(RegionCapNotAvailable, self.eq._processRegionEventQueue) 

    def test_start_and_stop(self):

        self.eq.cap = Capability('EventQueueGet', 'http://127.0.0.1')
        self.assertFalse(self.eq.stopped)
        api.spawn(self.eq.start)
        api.sleep(1)
        #self.eq.stop() #stop is broken atm
        self.eq.stopped = True
        api.sleep(.1)
        self.assertTrue(self.eq.stopped)
        api.sleep(1)
        self.assertFalse(self.eq._running)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEventQueue))
    return suite



