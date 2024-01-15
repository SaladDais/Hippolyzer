import asyncio
import math
import random
import unittest
from typing import *
from unittest import mock

from hippolyzer.lib.base.datatypes import *
from hippolyzer.lib.base.helpers import create_logged_task
from hippolyzer.lib.base.message.message import Block, Message as Message
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer
from hippolyzer.lib.base.objects import Object, normalize_object_update_compressed_data
from hippolyzer.lib.base.templates import ExtraParamType, PCode, JUST_CREATED_FLAGS
from hippolyzer.lib.client.object_manager import ObjectUpdateType
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.vocache import RegionViewerObjectCacheChain, RegionViewerObjectCache, ViewerObjectCacheEntry
from hippolyzer.lib.proxy.test_utils import BaseProxyTest

OBJECT_UPDATE_COMPRESSED_DATA = (
    b"\x12\x12\x10\xbf\x16XB~\x8f\xb4\xfb\x00\x1a\xcd\x9b\xe5\xd2\x04\x00\x00\t\x00\xcdG\x00\x00"
    b"\x03\x00\x00\x00\x1cB\x00\x00\x1cB\xcd\xcc\xcc=\xedG,"
    b"B\x9e\xb1\x9eBff\xa0A\x00\x00\x00\x00\x00\x00\x00\x00["
    b"\x8b\xf8\xbe\xc0\x00\x00\x00k\x9b\xc4\xfe3\nOa\xbb\xe2\xe4\xb2C\xac7\xbd\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\xa2=\x010\x00\x11\x00\x00\x00\x89UgG$\xcbC\xed\x92\x0bG\xca\xed"
    b"\x15F_@ \x00\x00\x00\x00d\x96\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00?\x00\x00\x00\x1c\x9fJoI\x8dH\xa0\x9d\xc4&''\x19=g\x00\x00\x00\x003\x00ff\x86\xbf"
    b"\x00ff\x86?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x89UgG$\xcbC"
    b"\xed\x92\x0bG\xca\xed\x15F_\x10\x00\x00\x003\x00\x01\x01\x00\x00\x00\x00\xdb\x0f\xc9@\xa6"
    b"\x9b\xc4="
)


class WrappingMessageHandler:
    """Calls both the session and region-local message handlers"""
    def __init__(self, region: ProxiedRegion):
        self.region = region

    def handle(self, message: Message):
        message.sender = self.region.circuit_addr
        self.region.session().message_handler.handle(message)
        self.region.message_handler.handle(message)


class ObjectTrackingAddon(BaseAddon):
    def __init__(self):
        super().__init__()
        self.events = []

    def handle_object_updated(self, session, region, obj: Object, updated_props: Set[str], msg: Optional[Message]):
        self.events.append(("update", obj, updated_props))

    def handle_object_killed(self, session, region, obj: Object):
        self.events.append(("kill", obj))


class ObjectManagerTestMixin(BaseProxyTest):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._setup_default_circuit()
        self.region = self.session.main_region
        self.message_handler = WrappingMessageHandler(self.region)
        patched = mock.patch('hippolyzer.lib.proxy.vocache.RegionViewerObjectCacheChain.for_region')
        self.addCleanup(patched.stop)
        self.mock_get_region_object_cache_chain = patched.start()
        self.mock_get_region_object_cache_chain.return_value = RegionViewerObjectCacheChain([])
        self.region_object_manager = self.region.objects
        self.serializer = UDPMessageSerializer()
        self.deserializer = UDPMessageDeserializer()
        self.object_addon = ObjectTrackingAddon()
        AddonManager.init([], None, [self.object_addon])

    def _create_object_update(self, local_id=None, full_id=None, parent_id=None, pos=None, rot=None,
                              pcode=None, namevalue=None, region_handle=None) -> Message:
        pos = pos if pos is not None else (1.0, 2.0, 3.0)
        rot = rot if rot is not None else (0.0, 0.0, 0.0, 1.0)
        pcode = pcode if pcode is not None else PCode.PRIMITIVE
        if region_handle is None:
            region_handle = 123
        msg = Message(
            "ObjectUpdate",
            Block("RegionData", RegionHandle=region_handle, TimeDilation=123),
            Block(
                "ObjectData",
                ID=local_id if local_id is not None else random.getrandbits(32),
                FullID=full_id if full_id else UUID.random(),
                PCode=pcode,
                Scale=Vector3(0.5, 0.5, 0.5),
                UpdateFlags=268568894,
                PathCurve=16,
                ParentID=parent_id if parent_id else 0,
                ProfileCurve=1,
                PathScaleX=100,
                PathScaleY=100,
                NameValue=namevalue,
                TextureEntry=b'\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00'
                             b'\x00\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                TextColor=b'\x00\x00\x00\x00',
                ExtraParams=b'\x00',
                fill_missing=True,
            )
        )
        msg["ObjectData"][0].serialize_var(
            "ObjectData",
            (
                60,
                {
                    'Position': pos,
                    'Velocity': (0.0, 0.0, 0.0),
                    'Acceleration': (0.0, 0.0, 0.0),
                    'Rotation': rot,
                    'AngularVelocity': (0.0, 0.0, 0.0)
                }
            )
        )
        # Run through (de)serializer to fill in any missing vars
        return self.deserializer.deserialize(self.serializer.serialize(msg))

    def _create_object(self, local_id=None, full_id=None, parent_id=None, pos=None, rot=None,
                       pcode=None, namevalue=None, region_handle=None) -> Object:
        msg = self._create_object_update(
            local_id=local_id, full_id=full_id, parent_id=parent_id, pos=pos, rot=rot,
            pcode=pcode, namevalue=namevalue, region_handle=region_handle)
        self.message_handler.handle(msg)
        actual_handle = msg["RegionData"]["RegionHandle"]
        region = self.session.region_by_handle(actual_handle)
        return region.objects.lookup_fullid(msg["ObjectData"]["FullID"])

    def _create_kill_object(self, local_id) -> Message:
        return Message(
            "KillObject",
            Block(
                "ObjectData",
                ID=local_id,
            )
        )

    def _kill_object(self, local_id: int):
        self.message_handler.handle(self._create_kill_object(local_id))

    def _create_object_update_cached(self, local_id: int, region_handle: int = 123,
                                     crc: int = 22, flags: int = 4321):
        return Message(
            'ObjectUpdateCached',
            Block("RegionData", TimeDilation=102, RegionHandle=region_handle),
            Block(
                "ObjectData",
                ID=local_id,
                CRC=crc,
                UpdateFlags=flags,
            )
        )

    def _get_avatar_positions(self) -> Dict[UUID, Vector3]:
        return {av.FullID: av.RegionPosition for av in self.region_object_manager.all_avatars}


class RegionObjectManagerTests(ObjectManagerTestMixin, unittest.IsolatedAsyncioTestCase):
    def test_basic_tracking(self):
        """Does creating an object result in it being tracked?"""
        msg = self._create_object_update()
        self.message_handler.handle(msg)
        obj = self.region_object_manager.lookup_fullid(msg["ObjectData"]["FullID"])
        self.assertIsNotNone(obj)

    def test_terse_object_update(self):
        msg = self._create_object_update(pos=Vector3(1, 2, 3))
        self.message_handler.handle(msg)
        local_id = msg["ObjectData"]["ID"]
        msg = Message(
            'ImprovedTerseObjectUpdate',
            Block('RegionData', RegionHandle=123, TimeDilation=65345),
            Block(
                'ObjectData',
                Data_={
                    'ID': local_id,
                    'State': 0,
                    'FootCollisionPlane': None,
                    'Position': Vector3(-2, -3, -4),
                    'Velocity': Vector3(-0.0, -0.0, -0.0),
                    'Acceleration': Vector3(-0.0, -0.0, -0.0),
                    'Rotation': Quaternion(0, 0, 0, 1),
                    'AngularVelocity': Vector3(-0.0, -0.0, -0.0)
                },
                TextureEntry_=None,
            ),
        )
        self.message_handler.handle(msg)
        obj = self.region_object_manager.lookup_localid(local_id)
        self.assertEqual(obj.Position, Vector3(-2, -3, -4))

    def test_parent_tracking(self):
        """Are basic parenting scenarios handled?"""
        parent = self._create_object()
        child = self._create_object(parent_id=parent.LocalID)
        self.assertSequenceEqual([child.LocalID], parent.ChildIDs)

    def test_orphan_parent_tracking(self):
        child = self._create_object(local_id=2, parent_id=1)
        self.assertEqual({1}, self.region_object_manager.missing_locals)
        parent = self._create_object(local_id=1)
        self.assertEqual(set(), self.region_object_manager.missing_locals)
        self.assertSequenceEqual([child.LocalID], parent.ChildIDs)

    def test_killing_parent_kills_children(self):
        _child = self._create_object(local_id=2, parent_id=1)
        parent = self._create_object(local_id=1)
        # This should orphan the child again
        self._kill_object(parent.LocalID)
        parent = self._create_object(local_id=1)
        # We should not have picked up any children
        self.assertSequenceEqual([], parent.ChildIDs)

    def test_hierarchy_killed(self):
        _child = self._create_object(local_id=3, parent_id=2)
        _other_child = self._create_object(local_id=4, parent_id=2)
        _parent = self._create_object(local_id=2, parent_id=1)
        grandparent = self._create_object(local_id=1)
        # KillObject implicitly kills all known descendents at that point
        self._kill_object(grandparent.LocalID)
        self.assertEqual(0, len(self.region_object_manager))

    def test_hierarchy_avatar_not_killed(self):
        _child = self._create_object(local_id=3, parent_id=2)
        _parent = self._create_object(local_id=2, parent_id=1, pcode=PCode.AVATAR)
        grandparent = self._create_object(local_id=1)
        # KillObject should only "unsit" child avatars (does this require an ObjectUpdate
        # or is ParentID=0 implied?)
        self._kill_object(grandparent.LocalID)
        self.assertEqual(2, len(self.region_object_manager))
        self.assertIsNotNone(self.region_object_manager.lookup_localid(2))

    def test_attachment_orphan_parent_tracking(self):
        """
        Test that multi-level parenting trees handle orphaning correctly.

        Technically there can be at least 4 levels of parenting if sitting.
        object -> seated agent -> attachment root -> attachment child
        """
        child = self._create_object(local_id=3, parent_id=2)
        parent = self._create_object(local_id=2, parent_id=1)
        self.assertSequenceEqual([child.LocalID], parent.ChildIDs)

    def test_unparenting_succeeds(self):
        child = self._create_object(local_id=3, parent_id=2)
        parent = self._create_object(local_id=2)
        msg = self._create_object_update(local_id=child.LocalID, full_id=child.FullID, parent_id=0)
        self.message_handler.handle(msg)
        self.assertEqual(0, child.ParentID)
        self.assertSequenceEqual([], parent.ChildIDs)

    def test_reparenting_succeeds(self):
        child = self._create_object(local_id=3, parent_id=2)
        parent = self._create_object(local_id=2)
        second_parent = self._create_object(local_id=1)
        msg = self._create_object_update(local_id=child.LocalID,
                                         full_id=child.FullID, parent_id=second_parent.LocalID)
        self.message_handler.handle(msg)
        self.assertEqual(second_parent.LocalID, child.ParentID)
        self.assertSequenceEqual([], parent.ChildIDs)
        self.assertSequenceEqual([child.LocalID], second_parent.ChildIDs)

    def test_reparenting_without_known_parent_succeeds(self):
        child = self._create_object(local_id=3, parent_id=2)
        second_parent = self._create_object(local_id=1)
        msg = self._create_object_update(local_id=child.LocalID,
                                         full_id=child.FullID, parent_id=second_parent.LocalID)
        self.message_handler.handle(msg)
        # Create the original parent after its former child has been reparented
        parent = self._create_object(local_id=2)
        self.assertEqual(second_parent.LocalID, child.ParentID)
        self.assertSequenceEqual([], parent.ChildIDs)
        self.assertSequenceEqual([child.LocalID], second_parent.ChildIDs)

    def test_reparenting_with_neither_parent_known_succeeds(self):
        child = self._create_object(local_id=3, parent_id=2)
        msg = self._create_object_update(local_id=child.LocalID,
                                         full_id=child.FullID, parent_id=1)
        self.message_handler.handle(msg)
        second_parent = self._create_object(local_id=1)
        self.assertEqual(second_parent.LocalID, child.ParentID)
        self.assertSequenceEqual([child.LocalID], second_parent.ChildIDs)

    def test_property_changes_reported_correctly(self):
        obj = self._create_object(local_id=1)
        msg = self._create_object_update(local_id=obj.LocalID, full_id=obj.FullID, pos=(2.0, 2.0, 2.0))
        self.message_handler.handle(msg)
        events = self.object_addon.events
        self.assertEqual(2, len(events))
        self.assertEqual({"Position", "TextureEntry"}, events[1][2])

    def test_region_position(self):
        parent = self._create_object(pos=(0.0, 1.0, 0.0))
        child = self._create_object(parent_id=parent.LocalID, pos=(0.0, 1, 0.0))

        self.assertEqual(parent.RegionPosition, (0.0, 1.0, 0.0))
        self.assertEqual(child.RegionPosition, (0.0, 2.0, 0.0))

    def test_orphan_region_position(self):
        child = self._create_object(local_id=2, parent_id=1, pos=(0.0, 1, 0.0))

        with self.assertRaises(ValueError):
            getattr(child, "RegionPosition")

    def test_rotated_region_position(self):
        parent = self._create_object(pos=(0.0, 1.0, 0.0), rot=Quaternion.from_euler(0, 0, 180, True))
        child = self._create_object(parent_id=parent.LocalID, pos=(0.0, 1.0, 0.0))

        self.assertEqual(parent.RegionPosition, (0.0, 1.0, 0.0))
        self.assertEqual(child.RegionPosition, (0.0, 0.0, 0.0))

    def test_rotated_region_position_multi_level(self):
        rot = Quaternion.from_euler(0, 0, 180, True)
        grandparent = self._create_object(pos=(0.0, 1.0, 0.0), rot=rot)
        parent = self._create_object(parent_id=grandparent.LocalID, pos=(0.0, 1.0, 0.0), rot=rot)
        child = self._create_object(parent_id=parent.LocalID, pos=(1.0, 2.0, 0.0))

        self.assertEqual(grandparent.RegionPosition, (0.0, 1.0, 0.0))
        self.assertEqual(parent.RegionPosition, (0.0, 0.0, 0.0))
        self.assertEqual(child.RegionPosition, (1.0, 2.0, 0.0))

    def test_global_position(self):
        obj = self._create_object(pos=(0.0, 0.0, 0.0))
        self.assertEqual(obj.GlobalPosition, (0.0, 123.0, 0.0))

    def test_avatar_locations(self):
        agent1_id = UUID.random()
        agent2_id = UUID.random()
        self.message_handler.handle(Message(
            "CoarseLocationUpdate",
            Block("AgentData", AgentID=agent1_id),
            Block("AgentData", AgentID=agent2_id),
            Block("Location", X=1, Y=2, Z=3),
            Block("Location", X=2, Y=3, Z=4),
        ))
        self.assertDictEqual(self._get_avatar_positions(), {
            # CoarseLocation's Z axis is multiplied by 4
            agent1_id: Vector3(1, 2, 12),
            agent2_id: Vector3(2, 3, 16),
        })

        # Simulate an avatar sitting on an object
        seat_object = self._create_object(pos=(0, 0, 3))
        # If we have a real object pos it should override coarse pos
        avatar_obj = self._create_object(full_id=agent1_id, pcode=PCode.AVATAR,
                                         parent_id=seat_object.LocalID, pos=Vector3(0, 0, 2))
        self.assertDictEqual(self._get_avatar_positions(), {
            # Agent is seated, make sure this is region and not local pos
            agent1_id: Vector3(0, 0, 5),
            agent2_id: Vector3(2, 3, 16),
        })

        # Simulate missing parent for agent
        self._kill_object(seat_object.LocalID)
        self.assertDictEqual(self._get_avatar_positions(), {
            # Agent is seated, but we don't know its parent. We have
            # to use the coarse location.
            agent1_id: Vector3(1, 2, 12),
            agent2_id: Vector3(2, 3, 16),
        })

        # If the object is killed and no coarse pos, it shouldn't be in the dict
        # CoarseLocationUpdates are expected to be complete, so any agents missing
        # are no longer in the sim.
        self._kill_object(avatar_obj.LocalID)
        self.message_handler.handle(Message(
            "CoarseLocationUpdate",
            Block("AgentData", AgentID=agent2_id),
            Block("Location", X=2, Y=3, Z=4),
        ))
        self.assertDictEqual(self._get_avatar_positions(), {
            agent2_id: Vector3(2, 3, 16),
        })

        # 255 on Z axis means we can't guess the real Z
        self.message_handler.handle(Message(
            "CoarseLocationUpdate",
            Block("AgentData", AgentID=agent2_id),
            Block("Location", X=2, Y=3, Z=math.inf),
        ))
        self.assertDictEqual(self._get_avatar_positions(), {
            agent2_id: Vector3(2, 3, math.inf),
        })
        agent2_avatar = self.region_object_manager.lookup_avatar(agent2_id)
        self.assertEqual(agent2_avatar.GlobalPosition, Vector3(2, 126, math.inf))

    def test_name_cache(self):
        # Receiving an update with a NameValue for an avatar should update NameCache
        obj = self._create_object(
            pcode=PCode.AVATAR,
            namevalue='DisplayName STRING RW DS 𝔲𝔫𝔦𝔠𝔬𝔡𝔢𝔫𝔞𝔪𝔢\n'
                      'FirstName STRING RW DS firstname\n'
                      'LastName STRING RW DS Resident\n'
                      'Title STRING RW DS foo'.encode("utf8"),
        )
        self.assertEqual(self.session_manager.name_cache.lookup(obj.FullID).first_name, "firstname")
        av = self.region_object_manager.lookup_avatar(obj.FullID)
        self.assertEqual(av.Name, "𝔲𝔫𝔦𝔠𝔬𝔡𝔢𝔫𝔞𝔪𝔢 (firstname Resident)")
        self.assertEqual(av.PreferredName, "𝔲𝔫𝔦𝔠𝔬𝔡𝔢𝔫𝔞𝔪𝔢")

    def test_normalize_cache_data(self):
        normalized = normalize_object_update_compressed_data(OBJECT_UPDATE_COMPRESSED_DATA)
        expected = {
            'PSBlock': None,
            'ParentID': 0,
            'LocalID': 1234,
            'FullID': UUID('121210bf-1658-427e-8fb4-fb001acd9be5'),
            'PCode': PCode.PRIMITIVE,
            'State': 0,
            'CRC': 18381,
            'Material': 3,
            'ClickAction': 0,
            'Scale': Vector3(39.0, 39.0, 0.10000000149011612),
            'Position': Vector3(43.07024002075195, 79.34690856933594, 20.049999237060547),
            'Rotation': Quaternion(0.0, 0.0, -0.48543819785118103, 0.8742709854884798),
            'OwnerID': UUID('6b9bc4fe-330a-4f61-bbe2-e4b243ac37bd'),
            'AngularVelocity': Vector3(0.0, 0.0, 0.0791015625),
            'TreeSpecies': None,
            'ScratchPad': None,
            'Text': b'',
            'TextColor': b'',
            'MediaURL': b'',
            'Sound': UUID(),
            'SoundGain': 0.0,
            'SoundFlags': 0,
            'SoundRadius': 0.0,
            'NameValue': [],
            'PathCurve': 32,
            'ProfileCurve': 0,
            'PathBegin': 0,
            'PathEnd': 25600,
            'PathScaleX': 150,
            'PathScaleY': 0,
            'PathShearX': 0,
            'PathShearY': 0,
            'PathTwist': 0,
            'PathTwistBegin': 0,
            'PathRadiusOffset': 0,
            'PathTaperX': 0,
            'PathTaperY': 0,
            'PathRevolutions': 0,
            'PathSkew': 0,
            'ProfileBegin': 0,
            'ProfileEnd': 0,
            'ProfileHollow': 0,
        }
        filtered_normalized = {k: v for k, v in normalized.items() if k in expected}
        self.assertDictEqual(filtered_normalized, expected)
        sculpt_texture = normalized["ExtraParams"][ExtraParamType.SCULPT]["Texture"]
        self.assertEqual(sculpt_texture, UUID('89556747-24cb-43ed-920b-47caed15465f'))
        self.assertIsNotNone(normalized['TextureAnim'])
        self.assertIsNotNone(normalized['TextureEntry'])

    def test_object_cache(self):
        self.mock_get_region_object_cache_chain.return_value = RegionViewerObjectCacheChain([
            RegionViewerObjectCache(self.region.cache_id, [
                ViewerObjectCacheEntry(
                    local_id=1234,
                    crc=22,
                    data=OBJECT_UPDATE_COMPRESSED_DATA,
                )
            ])
        ])
        cache_msg = self._create_object_update_cached(1234, flags=4321)
        obj = self.region_object_manager.lookup_localid(1234)
        self.assertIsNone(obj)
        self.region_object_manager.load_cache()
        self.message_handler.handle(cache_msg)
        obj = self.region_object_manager.lookup_localid(1234)
        self.assertEqual(obj.FullID, UUID('121210bf-1658-427e-8fb4-fb001acd9be5'))
        # Flags from the ObjectUpdateCached should have been merged in
        self.assertEqual(obj.UpdateFlags, 4321)

    async def test_request_objects(self):
        # request five objects, three of which won't receive an ObjectUpdate
        futures = self.region_object_manager.request_objects((1234, 1235, 1236, 1237))
        self._create_object(1234)
        self._create_object(1235)
        done, pending = await asyncio.wait(futures, timeout=0.0001)
        objects = await asyncio.gather(*done)
        # wait() returns unordered results, so use a set.
        self.assertEqual(set(o.LocalID for o in objects), {1234, 1235})
        pending = list(pending)
        self.assertEqual(2, len(pending))
        pending_1, pending_2 = pending

        # Timing out should cancel
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(pending_1, 0.00001)
        self.assertTrue(pending_1.cancelled())

        fut = self.region_object_manager.request_objects(1238)[0]
        self._kill_object(1238)
        self.assertTrue(fut.cancelled())

        # Object manager being cleared due to region death should cancel
        self.assertFalse(pending_2.cancelled())
        self.region_object_manager.clear()
        self.assertTrue(pending_2.cancelled())
        # The clear should have triggered the objects to be removed from the world view as well
        # as the region view
        self.assertEqual(0, len(self.session.objects))
        self.assertEqual(0, len(self.region_object_manager))


class SessionObjectManagerTests(ObjectManagerTestMixin, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.second_region = self.session.register_region(
            ("127.0.0.1", 9), "https://localhost:5", 124
        )
        self.session.objects.track_region_objects(124)
        self._setup_region_circuit(self.second_region)

    def test_get_fullid(self):
        obj = self._create_object()
        self.assertIs(self.session.objects.lookup_fullid(obj.FullID), obj)
        self._kill_object(obj.LocalID)
        self.assertIsNone(self.session.objects.lookup_fullid(obj.FullID))

    def test_region_handle_change(self):
        obj = self._create_object(region_handle=123)
        self.assertEqual(obj.RegionHandle, 123)
        self.assertIs(self.region.objects.lookup_fullid(obj.FullID), obj)
        self.assertIs(self.region.objects.lookup_localid(obj.LocalID), obj)

        # Send an update moving the object to the new region
        self._create_object(local_id=~obj.LocalID & 0xFFffFFff, full_id=obj.FullID, region_handle=124)
        self.assertEqual(obj.RegionHandle, 124)
        self.assertIsNone(self.region.objects.lookup_fullid(obj.FullID))
        self.assertIsNone(self.region.objects.lookup_localid(obj.LocalID))
        self.assertIs(self.second_region.objects.lookup_fullid(obj.FullID), obj)
        self.assertIs(self.second_region.objects.lookup_localid(obj.LocalID), obj)
        self.assertEqual(1, len(self.session.objects))
        self.assertEqual(0, len(self.region.objects))
        self.assertEqual(1, len(self.second_region.objects))

    def test_object_moved_to_bad_region(self):
        obj = self._create_object(region_handle=123)
        msg = self._create_object_update(
            local_id=~obj.LocalID & 0xFFffFFff, full_id=obj.FullID, region_handle=999)
        self.message_handler.handle(msg)
        # Should not be in this region anymore
        self.assertEqual(0, len(self.region_object_manager))
        # Should still be tracked by the session
        self.assertEqual(1, len(self.session.objects))
        self.assertIsNotNone(self.session.objects.lookup_fullid(obj.FullID))

    def test_linkset_region_handle_change(self):
        parent = self._create_object(region_handle=123)
        child = self._create_object(region_handle=123, parent_id=parent.LocalID)
        self._create_object(local_id=~parent.LocalID & 0xFFffFFff, full_id=parent.FullID, region_handle=124)
        # Children reference their parents, not the other way around. Moving this to a new region
        # should have cleared the list because it now has no children in the same region.
        self.assertEqual([], parent.ChildIDs)
        # Move the child to the same region
        self._create_object(
            local_id=child.LocalID, full_id=child.FullID, region_handle=124, parent_id=parent.LocalID)
        # Child should be back in the children list
        self.assertEqual([child.LocalID], parent.ChildIDs)
        self.assertEqual(parent.LocalID, child.ParentID)
        self.assertEqual(0, len(self.region.objects))
        self.assertEqual(2, len(self.second_region.objects))
        self.assertEqual(0, len(self.region.objects.missing_locals))
        self.assertEqual(0, len(self.second_region.objects.missing_locals))

    def test_all_objects(self):
        obj = self._create_object()
        self.assertEqual([obj], list(self.session.objects.all_objects))

    def test_all_avatars(self):
        obj = self._create_object(pcode=PCode.AVATAR)
        av_list = list(self.session.objects.all_avatars)
        self.assertEqual(1, len(av_list))
        self.assertEqual(obj, av_list[0].Object)

    def test_avatars_preference(self):
        # If we have a coarselocation for an avatar in one region and
        # an actual object in another, we should always prefer the
        # one with the actual object.
        av_1 = self._create_object(pcode=PCode.AVATAR, region_handle=123)
        av_2 = self._create_object(pcode=PCode.AVATAR, region_handle=124)
        # Coarse location shouldn't be used for either of these
        self.session.region_by_handle(123).message_handler.handle(Message(
            "CoarseLocationUpdate",
            Block("AgentData", AgentID=av_2.FullID),
            Block("Location", X=2, Y=3, Z=4),
        ))
        self.session.region_by_handle(124).message_handler.handle(Message(
            "CoarseLocationUpdate",
            Block("AgentData", AgentID=av_1.FullID),
            Block("Location", X=2, Y=3, Z=4),
        ))
        av_list = list(self.session.objects.all_avatars)
        self.assertEqual(2, len(av_list))
        self.assertTrue(all(a.Object for a in av_list))

    def test_lookup_avatar(self):
        av_1 = self._create_object(pcode=PCode.AVATAR)
        av_obj = self.session.objects.lookup_avatar(av_1.FullID)
        self.assertEqual(av_1.FullID, av_obj.FullID)

    async def test_requesting_properties(self):
        obj = self._create_object()
        futs = self.session.objects.request_object_properties(obj)
        self.message_handler.handle(Message(
            "ObjectProperties",
            Block("ObjectData", ObjectID=obj.FullID, Name="Foobar", TextureID=b""),
        ))
        await asyncio.wait_for(futs[0], timeout=0.0001)
        self.assertEqual(obj.Name, "Foobar")

    async def test_load_ancestors(self):
        child = self._create_object(region_handle=123, parent_id=1)
        parentless = self._create_object(region_handle=123)
        orphaned = self._create_object(region_handle=123, parent_id=9)

        async def _create_after():
            await asyncio.sleep(0.001)
            self._create_object(region_handle=123, local_id=child.ParentID)
        _ = create_logged_task(_create_after())

        await self.session.objects.load_ancestors(child)
        await self.session.objects.load_ancestors(parentless)
        with self.assertRaises(asyncio.TimeoutError):
            await self.session.objects.load_ancestors(orphaned, wait_time=0.005)

    async def test_auto_request_objects(self):
        self.session_manager.settings.AUTOMATICALLY_REQUEST_MISSING_OBJECTS = True
        self.message_handler.handle(self._create_object_update_cached(1234))
        self.message_handler.handle(self._create_object_update_cached(1235))
        self.assertEqual({1234, 1235}, self.region_object_manager.queued_cache_misses)
        # Pretend viewer sent out its own RequestMultipleObjects
        self.message_handler.handle(Message(
            'RequestMultipleObjects',
            Block("RegionData", SessionID=self.session.id, AgentID=self.session.agent_id),
            Block(
                "ObjectData",
                ID=1234,
            )
        ))
        # Proxy should have killed its pending request for 1234
        self.assertEqual({1235}, self.region_object_manager.queued_cache_misses)

    async def test_auto_request_avatar_seats(self):
        # Avatars' parent links should always be requested regardless of
        # object auto-request setting's value.
        seat_id = 999
        av = self._create_object(pcode=PCode.AVATAR, parent_id=seat_id)
        self.assertEqual({seat_id}, self.region_object_manager.queued_cache_misses)
        # Need to wait for it to decide it's worth requesting
        await asyncio.sleep(0.22)
        self.assertEqual(set(), self.region_object_manager.queued_cache_misses)
        # Make sure we sent a request after the timeout
        req_msg = self.deserializer.deserialize(self.transport.packets[-1][0])
        self.assertEqual("RequestMultipleObjects", req_msg.name)
        self.assertEqual(
            [{'CacheMissType': 0, 'ID': seat_id}],
            req_msg.to_dict()['body']['ObjectData'],
        )
        # Parent should not be requested again if an unrelated property like pos changes
        self._create_object(local_id=av.LocalID, full_id=av.FullID,
                            pcode=PCode.AVATAR, parent_id=seat_id, pos=(1, 2, 9))
        self.assertEqual(set(), self.region_object_manager.queued_cache_misses)

    async def test_handle_object_update_event(self):
        with self.session.objects.events.subscribe_async(
            message_names=(ObjectUpdateType.UPDATE,),
            predicate=lambda e: e.object.UpdateFlags & JUST_CREATED_FLAGS and "LocalID" in e.updated,
        ) as get_events:
            self._create_object(local_id=999)
            evt = await asyncio.wait_for(get_events(), 1.0)
            self.assertEqual(999, evt.object.LocalID)

    async def test_handle_object_update_predicate(self):
        with self.session.objects.events.subscribe_async(
            message_names=(ObjectUpdateType.UPDATE,),
        ) as get_events:
            self._create_object(local_id=999)
            evt = await asyncio.wait_for(get_events(), 1.0)
            self.assertEqual(999, evt.object.LocalID)

    async def test_handle_object_update_events_two_subscribers(self):
        with self.session.objects.events.subscribe_async(
            message_names=(ObjectUpdateType.UPDATE,),
        ) as get_events:
            with self.session.objects.events.subscribe_async(
                    message_names=(ObjectUpdateType.UPDATE,),
            ) as get_events2:
                self._create_object(local_id=999)
                evt = await asyncio.wait_for(get_events(), 1.0)
                evt2 = await asyncio.wait_for(get_events2(), 1.0)
                self.assertEqual(999, evt.object.LocalID)
                self.assertEqual(evt, evt2)

    async def test_handle_object_update_events_two_subscribers_timeout(self):
        with self.session.objects.events.subscribe_async(
            message_names=(ObjectUpdateType.UPDATE,),
        ) as get_events:
            with self.session.objects.events.subscribe_async(
                    message_names=(ObjectUpdateType.UPDATE,),
            ) as get_events2:
                self._create_object(local_id=999)
                evt = asyncio.wait_for(get_events(), 0.01)
                evt2 = asyncio.wait_for(get_events2(), 0.01)
                await asyncio.gather(evt, evt2)
