
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
from pyogp.lib.base.objects import *
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.region import Region
from pyogp.lib.base.agent import Agent
from pyogp.lib.base.datatypes import UUID, Vector3

# pyogp messaging
from pyogp.lib.base.message.udpdeserializer import UDPMessageDeserializer
from pyogp.lib.base.message.message import Message, Block

# pyogp tests
import pyogp.lib.base.tests.config 

class TestObjects(unittest.TestCase):

    def setUp(self):

        self.settings = Settings()
        self.settings.ENABLE_DEFERRED_PACKET_PARSING = False

        self.deserializer = UDPMessageDeserializer(settings = self.settings)

        self.region = Region()
        self.region.SimName = 'TestMe'

        self.object_store = ObjectManager(region = self.region, settings = self.settings)
        self.object_store.enable_callbacks()
        self.data = []
    def tearDown(self):

        pass

    def test_ObjectUpdateCompressed_handling(self):

        ouc_hex_string = '4000000012000D00C8030000FE03002AFF06100802109E002B7F7A6E32C5DBFDE2C7926D1A9F0ACAF476000009000F00000003000000003F0000003F0000003F7E8E03435E550743CDCCB24100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F0000000000000000000000000000003C0902109E001DD5EFE2FAAF18645AC9BC61C5D8D7EAF376000009000F00000003000000003F0000003F0000003F0000014300000043CAC0C64100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F000000000000000000000000000000100802109E0050B8926A9EFEAA75C4E9D8946BA812A5C076000009001100000003000000003F0000003F0000003F00000C4300000043CDCCB24100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F0000000000000000000000000000003C0902109E00CAB68676A725E9D925B06D925F0BC5F2BF76000009000F00000003000000003F0000003F0000003F000001430000004343C1C64100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F000000000000000000000000000000100802109E0078716204266469BAEAA52587D877D4EF9074000009001900000003000000003F0000003F0000003F176B0243DE4E08435853BC4100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F0000000000000000000000000000003C0902109E0093CBC3E18DAB07EAD4ED2631AAA569FC8C76000009000F00000003000000003F0000003F0000003F000001430000004329C1C64100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F000000000000000000000000000000'

        ouc_binary = unhexlify(ouc_hex_string)

        packet = self.deserializer.deserialize(ouc_binary)

        self.object_store.onObjectUpdateCompressed(packet)

        known_objects = []

        for _object in  self.object_store.object_store:
            known_objects.append((str(_object.FullID), _object.LocalID))

        self.assertEquals(known_objects, [(str(uuid.UUID('2b7f7a6e-32c5-dbfd-e2c7-926d1a9f0aca')), 30452), (str(uuid.UUID('1dd5efe2-faaf-1864-5ac9-bc61c5d8d7ea')), 30451), (str(uuid.UUID('50b8926a-9efe-aa75-c4e9-d8946ba812a5')), 30400), (str(uuid.UUID('cab68676-a725-e9d9-25b0-6d925f0bc5f2')), 30399), (str(uuid.UUID('78716204-2664-69ba-eaa5-2587d877d4ef')), 29840), (str(uuid.UUID('93cbc3e1-8dab-07ea-d4ed-2631aaa569fc')), 30348)])

    def test_onObjectUpdateCompressed_with_extraparams(self):

        hex_data = '4000000027000D00C5030000FD03005EFE0510880210A200E2BA7AC7DB2824E3484DF418B045E62D306F020009001F00000003000000804000000040CDCC4C3D0D00204000000000880FEC3A00000000000000000000000020000000000000000000000000000000000000002D6F02000010000000006464000000000000000000010000000000002E000000CD02D3C2BFA5D1CD1B54CA8863A470B50000000000000000803F000000803F000000000000000000000000000000D00402100B016CBAFC4A97589481CD74C7CCC89E7440339C02000900D71E0000030061370C403904A43F544E2240A6F00B438BCA0343CE9FBF41F52752BE5081E4BD7EE25D3F08000000DD1E79B2DDFE40808206242AB63F4A1919000000020000000800000000036400014004260026000300800080808000800080E67F784EC24DD115ADF9E7A3F963D08483BD6CBAFC4A97589481CD74C7CCC89E74402B000000000DFFFFFFFFFFFFFFBF03030202013000110000003849A2E01B51E318A882D938A339E8380120000000006496000000000000000000000000000000002E000000F4543F569C0EE096247C62F0CE048159005B5B5B00000000803F000000803F000000000000000000000000000000D00C0210B800D2B300C371F1688727506D48DA05E2F51C9C02000900330100000300000080400AD7233C0000804048FD184076A46ABF62E78640B2EA583EFC1499BE058BE73C2000000000000000000000000000000000000000339C0200001000000000646400000000000000000001000000000000440000009C793FCEB9B9FC1F9DD98342659BFA420A6EEF3A490087A10A461B81F7D20CDFC8005B5B5B00000000803F02000080BF000000803F000000000000000000000000000000D00C0210B800DBB7D1103F650859D4943DC40FFB2B611D9C02000900380100000300000080400AD7233C00008040EA91523F3E074EC09AE94B408699313E6D57213DA5D757BF2000000000000000000000000000000000000000339C0200001000000000646400000000000000000001000000000000440000009C793FCEB9B9FC1F9DD98342659BFA420A07B0098C45C22DE52151D8076EAB1065005B5B5B00000000803F02000080BF000000803F000000000000000000000000000000D00C0210B8001F389EB9863928FFC37BA3E4F39A7FED1E9C02000900550100000300000080400AD7233C00008040FC3648BFCDE542C09AD16F3F835F473DF0955D3DD9016EBF2000000000000000000000000000000000000000339C0200001000000000646400000000000000000001000000000000440000009C793FCEB9B9FC1F9DD98342659BFA420A6EEF3A490087A10A461B81F7D20CDFC8005B5B5B00000000803F02000080BF000000803F000000000000000000000000000000'

        ouc_binary = unhexlify(hex_data)

        packet = self.deserializer.deserialize(ouc_binary)

        self.object_store.onObjectUpdateCompressed(packet)

        known_objects = []

        for _object in  self.object_store.object_store:
            known_objects.append((str(_object.FullID), _object.LocalID))
        
        self.assertEquals(known_objects, [(str(uuid.UUID('e2ba7ac7-db28-24e3-484d-f418b045e62d')), 159536), (str(uuid.UUID('6cbafc4a-9758-9481-cd74-c7ccc89e7440')), 171059), (str(uuid.UUID('d2b300c3-71f1-6887-2750-6d48da05e2f5')), 171036), (str(uuid.UUID('dbb7d110-3f65-0859-d494-3dc40ffb2b61')), 171037), (str(uuid.UUID('1f389eb9-8639-28ff-c37b-a3e4f39a7fed')), 171038)])

    def test_onObjectUpdate_selected(self):

        self.object_store.agent = Agent()
        fake_uuid = UUID()
        fake_uuid.random()
        packet = Message('ObjectUpdate',
                         Block('RegionData',
                               RegionHandle=0,
                               TimeDilation=0),
                         Block('ObjectData',
                               ID=1,
                               State=1,
                               FullID=fake_uuid,
                               CRC=0,
                               PCode=0,
                               Material=0,
                               ClickAction=0,
                               Scale=Vector3(X=0.0, Y=0.0, Z=0.0),
                               ObjectData='',
                               ParentID=fake_uuid,
                               UpdateFlags=0,
                               ProfileCurve=0,
                               PathBegin=0.0,
                               PathEnd=0.0,
                               PathScaleX=0.0,
                               PathScaleY=0.0,
                               PathShearX=0.0,
                               PathShearY=0.0,
                               PathTwist=-1,
                               PathTwistBegin=-1,
                               PathRadiusOffset=-1,
                               PathTaperX=-1,
                               PathTaperY=-1,
                               PathRevolutions=0,
                               PathSkew=-1,
                               ProfileBegin=0,
                               ProfileEnd=0,
                               ProfileHollow=0,
                               TextureEntry='',
                               TextureAnim='',
                               NameValue='Test',
                               Data='',
                               Text='',
                               TextColor=0x0,
                               MedialURL=''))
        
        def callback(payload):
            self.data.append("foo")
        object_handler = self.object_store.agent.events_handler.register("ObjectSelected")
        object_handler.subscribe(callback)
        self.object_store.region.message_handler.handle(packet)
        self.assertTrue(self.data.pop, "foo")
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestObjects))
    return suite


