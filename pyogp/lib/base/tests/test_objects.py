"""
@file test_objects.py
@date 2009-03-20
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
from binascii import unhexlify

#related

# pyogp
from pyogp.lib.base.objects import *
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.region import Region

# pyogp messaging
from pyogp.lib.base.message.udpdeserializer import UDPPacketDeserializer

# pyogp tests
import pyogp.lib.base.tests.config 

class TestObjects(unittest.TestCase):

    def setUp(self):

        self.settings = Settings()
        self.settings.ENABLE_DEFERRED_PACKET_PARSING = False

        self.deserializer = UDPPacketDeserializer(settings = self.settings)

        self.region = Region()
        self.region.SimName = 'TestMe'

        self.object_store = Objects(region = self.region, settings = self.settings)

    def tearDown(self):

        pass

    def test_ObjectUpdateCompressed_handling(self):

        ouc_hex_string = '4000000012000D00C8030000FE03002AFF06100802109E002B7F7A6E32C5DBFDE2C7926D1A9F0ACAF476000009000F00000003000000003F0000003F0000003F7E8E03435E550743CDCCB24100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F0000000000000000000000000000003C0902109E001DD5EFE2FAAF18645AC9BC61C5D8D7EAF376000009000F00000003000000003F0000003F0000003F0000014300000043CAC0C64100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F000000000000000000000000000000100802109E0050B8926A9EFEAA75C4E9D8946BA812A5C076000009001100000003000000003F0000003F0000003F00000C4300000043CDCCB24100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F0000000000000000000000000000003C0902109E00CAB68676A725E9D925B06D925F0BC5F2BF76000009000F00000003000000003F0000003F0000003F000001430000004343C1C64100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F000000000000000000000000000000100802109E0078716204266469BAEAA52587D877D4EF9074000009001900000003000000003F0000003F0000003F176B0243DE4E08435853BC4100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F0000000000000000000000000000003C0902109E0093CBC3E18DAB07EAD4ED2631AAA569FC8C76000009000F00000003000000003F0000003F0000003F000001430000004329C1C64100000000000000000000000000000000000000000000000000000000000000000010000000006464000000000000000000010000000000002E0000008955674724CB43ED920B47CAED15465F0000000000000000803F000000803F000000000000000000000000000000'

        ouc_binary = unhexlify(ouc_hex_string)

        packet = self.deserializer.deserialize(ouc_binary)

        onObjectUpdateCompressed(packet, self.object_store)

        known_objects = []

        for _object in  self.object_store.object_store:
            known_objects.append((_object.FullID, _object.ID))

        self.assertEquals(known_objects, [(uuid.UUID('2b7f7a6e-32c5-dbfd-e2c7-926d1a9f0aca'), 30452L), (uuid.UUID('1dd5efe2-faaf-1864-5ac9-bc61c5d8d7ea'), 30451L), (uuid.UUID('50b8926a-9efe-aa75-c4e9-d8946ba812a5'), 30400L), (uuid.UUID('cab68676-a725-e9d9-25b0-6d925f0bc5f2'), 30399L), (uuid.UUID('78716204-2664-69ba-eaa5-2587d877d4ef'), 29840L), (uuid.UUID('93cbc3e1-8dab-07ea-d4ed-2631aaa569fc'), 30348L)])    

        def new packet(_ID, _State, _FullID, _CRC, _PCode, _Material, _ClickAction, _Scale, _ObjectData, _ParentID, _UpdateFlags, _PathCurve, _ProfileCurve, _PathBegin, _PathEnd, _PathScaleX, _PathScaleY, _PathS hearX, _PathShearY, _PathTwist, _PathTwistBegin, _PathRadiusOffset, _PathTaperX, _PathTaperY, _PathRevolutions, _PathSkew, _ProfileBegin, _ProfileEnd, _ProfileHollow, _TextureEntry, _TextureAnim, _NameValue, _Data , _Text, _TextColor, _MediaURL, _PSBlock, _ExtraParams, _Sound, _OwnerID, _Gain, _Flags, _Radius, _JointType, _JointPivot, _JointAxisOrAnchor, FootCollisionPlane, Position, Velocity, Acceleration, Rotation, AngularVelocity):

            packet = ObjectUpdateCompressedPacket() # from message/packets.py

            packet.ObjectData['UpdateFlags'] = _UpdateFlags 
            
            # Prepare the Data 
            Data['LocalID']  = struct.pack("<I",_ID)
            Data['FullID']   = UUID(_FullID).get_bytes()
            Data['PCode']    = struct.pack(">B",PCode)
            
            # If this is a Primitive (PCode = 9)
            if PCode = 9:
                Data['State'] = struct.pack(">B", _State)[0]
                Data['CRC']   = struct.pack("<I", _CRC)[0]
                Data['Material'] = struct.pack(">B", _Material)[0]
                Data['ClickAction'] = struct.pack(">B", ClickAction)[0]
                Data['Scale'] = Vector3(_Scale).get_bytes()
                Data['Position'] = Vector3(Position).get_bytes()
                Data['Rotation'] = Vector3(Rotation).get_bytes()
                Data['Flags'] = struct.pack(">B",_Flags)[0]
                Data['OwnerID'] = uuid.UUID(_OwnerID)
                Data['PathCurve'] = struct.pack(">B",_PathCurve)
                Data['PathBegin'] = struct.pack("<H",_PathBegin)
                Data['PathEnd'] = struct.pack("<H",_PathEnd)
                Data['PathScaleX'] = struct.pack("<B",_PathScaleX)
                Data['PathScaleY'] = struct.pack("<

            packet.ObjectData['ObjectData'] = binary represesentation of uuids vectors and blah

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestObjects))
    return suite
