"""
@file test_event_queue.py
@date 2009-2-25
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

# standard python libs
import unittest

# related
from indra.base import llsd

# pyogp
from pyogp.lib.base.event_queue import EventQueueClient
from pyogp.lib.base.exc import *

# pyogp tests
import pyogp.lib.base.tests.config 

class TestEventQueue(unittest.TestCase):

    def setUp(self):

        self.eq = EventQueueClient()

    def tearDown(self):

        pass

    def test__decode_eq_result(self):

        data = {'events': [{'body': {'SimulatorInfo': [{'IP': '\xd8R R', 'Handle': '\x00\x03\xe4\x00\x00\x03\xe9\x00', 'Port': 13001}]}, 'message': 'EnableSimulator'}, {'body': {'SimulatorInfo': [{'IP': '\xd8R\x0f\x06', 'Handle': '\x00\x03\xe5\x00\x00\x03\xe8\x00', 'Port': 13000}]}, 'message': 'EnableSimulator'}, {'body': {'SimulatorInfo': [{'IP': '\xd8R R', 'Handle': '\x00\x03\xe4\x00\x00\x03\xe9\x00', 'Port': 13001}]}, 'message': 'EnableSimulator'}, {'body': {'SimulatorInfo': [{'IP': '\xd8R\x0f\x06', 'Handle': '\x00\x03\xe5\x00\x00\x03\xe8\x00', 'Port': 13000}]}, 'message': 'EnableSimulator'}], 'id': -2054685694}

        packets = self.eq._decode_eq_result(data)

        for packet in packets:
            self.assertEquals(str(type(packet)), '<class \'pyogp.lib.base.message.packet.UDPPacket\'>')

    def test__decode_eq_result2(self):

        llsd_data = '<llsd><map><key>events</key><array><map><key>body</key><map><key>AgentData</key><array><map><key>AgentID</key><uuid>a517168d-1af5-4854-ba6d-672c8a59e439</uuid></map></array><key>GroupData</key><array><map><key>AcceptNotices</key><boolean>1</boolean><key>Contribution</key><integer>0</integer><key>GroupID</key><uuid>4dd70b7f-8b3a-eef9-fc2f-909151d521f6</uuid><key>GroupInsigniaID</key><uuid /><key>GroupName</key><string>Enus&apos; Construction Crew</string><key>GroupPowers</key><binary encoding="base64">AAA5ABgBAAA=</binary><key>ListInProfile</key><boolean>0</boolean></map><map><key>AcceptNotices</key><boolean>1</boolean><key>Contribution</key><integer>0</integer><key>GroupID</key><uuid>69fd708c-3f20-a01b-f9b5-b5c4b310e5ca</uuid><key>GroupInsigniaID</key><uuid /><key>GroupName</key><string>EnusBot Army</string><key>GroupPowers</key><binary encoding="base64">AAD5ABgBAAA=</binary><key>ListInProfile</key><boolean>0</boolean></map></array></map><key>message</key><string>AgentGroupDataUpdate</string></map><map><key>body</key><map><key>AgeVerificationBlock</key><array><map><key>RegionDenyAgeUnverified</key><boolean>0</boolean></map></array><key>MediaData</key><array><map><key>MediaDesc</key><string /><key>MediaHeight</key><integer>0</integer><key>MediaLoop</key><integer>1</integer><key>MediaType</key><string>none/none</string><key>MediaWidth</key><integer>0</integer><key>ObscureMedia</key><integer>1</integer><key>ObscureMusic</key><integer>1</integer></map></array><key>ParcelData</key><array><map><key>AABBMax</key><array><real>256</real><real>256</real><real>50</real></array><key>AABBMin</key><array><real>0</real><real>0</real><real>0</real></array><key>Area</key><integer>65536</integer><key>AuctionID</key><binary encoding="base64">AAAAAA==</binary><key>AuthBuyerID</key><uuid /><key>Bitmap</key><binary encoding="base64">//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////8=</binary><key>Category</key><integer>255</integer><key>ClaimDate</key><integer>1088625472</integer><key>ClaimPrice</key><integer>0</integer><key>Desc</key><string /><key>GroupID</key><uuid /><key>GroupPrims</key><integer>0</integer><key>IsGroupOwned</key><boolean>0</boolean><key>LandingType</key><integer>1</integer><key>LocalID</key><integer>15</integer><key>MaxPrims</key><integer>3750</integer><key>MediaAutoScale</key><integer>0</integer><key>MediaID</key><uuid /><key>MediaURL</key><string /><key>MusicURL</key><string /><key>Name</key><string /><key>OtherCleanTime</key><integer>0</integer><key>OtherCount</key><integer>4096</integer><key>OtherPrims</key><integer>0</integer><key>OwnerID</key><uuid>dd1e79b2-ddfe-4080-8206-242ab63f4a19</uuid><key>OwnerPrims</key><integer>44</integer><key>ParcelFlags</key><binary encoding="base64">egAAAQ==</binary><key>ParcelPrimBonus</key><real>1</real><key>PassHours</key><real>1</real><key>PassPrice</key><integer>10</integer><key>PublicCount</key><integer>0</integer><key>RegionDenyAnonymous</key><boolean>0</boolean><key>RegionDenyIdentified</key><boolean>0</boolean><key>RegionDenyTransacted</key><boolean>0</boolean><key>RegionPushOverride</key><boolean>0</boolean><key>RentPrice</key><integer>0</integer><key>RequestResult</key><integer>0</integer><key>SalePrice</key><integer>10000</integer><key>SelectedPrims</key><integer>0</integer><key>SelfCount</key><integer>0</integer><key>SequenceID</key><integer>0</integer><key>SimWideMaxPrims</key><integer>3750</integer><key>SimWideTotalPrims</key><integer>44</integer><key>SnapSelection</key><boolean>0</boolean><key>SnapshotID</key><uuid /><key>Status</key><integer>0</integer><key>TotalPrims</key><integer>44</integer><key>UserLocation</key><array><real>0</real><real>0</real><real>0</real></array><key>UserLookAt</key><array><real>0</real><real>0</real><real>0</real></array></map></array></map><key>message</key><string>ParcelProperties</string></map><map><key>body</key><map><key>SimulatorInfo</key><array><map><key>Handle</key><binary encoding="base64">AAP8AAADxAA=</binary><key>IP</key><binary encoding="base64">2FISdw==</binary><key>Port</key><integer>13002</integer></map></array></map><key>message</key><string>EnableSimulator</string></map></array><key>id</key><integer>-182442759</integer></map></llsd>'

        data = llsd.parse(llsd_data)

        packets = self.eq._decode_eq_result(data)

        packet_names = []

        for packet in packets:
            self.assertEquals(str(type(packet)), '<class \'pyogp.lib.base.message.packet.UDPPacket\'>')
            packet_names.append(packet.name)

        self.assertEquals(packet_names, ['AgentGroupDataUpdate', 'ParcelProperties', 'EnableSimulator'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEventQueue))
    return suite
