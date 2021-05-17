import math
import random
import unittest
from typing import *

from hippolyzer.lib.base.datatypes import *
from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer
from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.objects import ObjectManager
from hippolyzer.lib.proxy.message import ProxiedMessage as Message
from hippolyzer.lib.proxy.templates import PCode


class MockRegion:
    def __init__(self, message_handler: MessageHandler):
        self.session = lambda: None
        self.handle = 123
        self.message_handler = message_handler
        self.http_message_handler = MessageHandler()


class ObjectTrackingAddon(BaseAddon):
    def __init__(self):
        super().__init__()
        self.events = []

    def handle_object_updated(self, session, region, obj: Object, updated_props: Set[str]):
        self.events.append(("update", obj, updated_props))

    def handle_object_killed(self, session, region, obj: Object):
        self.events.append(("kill", obj))


class ObjectManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.message_handler = MessageHandler()
        self.region = MockRegion(self.message_handler)
        self.object_manager = ObjectManager(self.region)  # type: ignore
        self.serializer = UDPMessageSerializer()
        self.deserializer = UDPMessageDeserializer(message_cls=Message)
        self.object_addon = ObjectTrackingAddon()
        AddonManager.init([], None, [self.object_addon])

    def _create_object_update(self, local_id=None, full_id=None, parent_id=None, pos=None, rot=None,
                              pcode=None, namevalue=None) -> Message:
        pos = pos if pos is not None else (1.0, 2.0, 3.0)
        rot = rot if rot is not None else (0.0, 0.0, 0.0, 1.0)
        pcode = pcode if pcode is not None else PCode.PRIMITIVE
        msg = Message(
            "ObjectUpdate",
            Block("RegionData", RegionHandle=123, TimeDilation=123),
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
                       pcode=None, namevalue=None) -> Object:
        msg = self._create_object_update(
            local_id=local_id, full_id=full_id, parent_id=parent_id, pos=pos, rot=rot,
            pcode=pcode, namevalue=namevalue)
        self.message_handler.handle(msg)
        return self.object_manager.lookup_fullid(msg["ObjectData"]["FullID"])

    def _create_kill_object(self, local_id) -> Message:
        return Message(
            "KillObject",
            Block(
                "ObjectData",
                ID=local_id,
            )
        )

    def _kill_object(self, obj: Object):
        self.message_handler.handle(self._create_kill_object(obj.LocalID))

    def _get_avatar_positions(self) -> Dict[UUID, Vector3]:
        return {av.FullID: av.RegionPosition for av in self.object_manager.all_avatars}

    def test_basic_tracking(self):
        """Does creating an object result in it being tracked?"""
        msg = self._create_object_update()
        self.message_handler.handle(msg)
        obj = self.object_manager.lookup_fullid(msg["ObjectData"]["FullID"])
        self.assertIsNotNone(obj)

    def test_parent_tracking(self):
        """Are basic parenting scenarios handled?"""
        parent = self._create_object()
        child = self._create_object(parent_id=parent.LocalID)
        self.assertSequenceEqual([child.LocalID], parent.ChildIDs)

    def test_orphan_parent_tracking(self):
        child = self._create_object(local_id=2, parent_id=1)
        self.assertEqual({1}, self.object_manager.missing_locals)
        parent = self._create_object(local_id=1)
        self.assertEqual(set(), self.object_manager.missing_locals)
        self.assertSequenceEqual([child.LocalID], parent.ChildIDs)

    def test_killing_parent_kills_children(self):
        _child = self._create_object(local_id=2, parent_id=1)
        parent = self._create_object(local_id=1)
        # This should orphan the child again
        self._kill_object(parent)
        parent = self._create_object(local_id=1)
        # We should not have picked up any children
        self.assertSequenceEqual([], parent.ChildIDs)

    def test_hierarchy_killed(self):
        _child = self._create_object(local_id=3, parent_id=2)
        _other_child = self._create_object(local_id=4, parent_id=2)
        _parent = self._create_object(local_id=2, parent_id=1)
        grandparent = self._create_object(local_id=1)
        # KillObject implicitly kills all known descendents at that point
        self._kill_object(grandparent)
        self.assertEqual(0, len(self.object_manager))

    def test_hierarchy_avatar_not_killed(self):
        _child = self._create_object(local_id=3, parent_id=2)
        _parent = self._create_object(local_id=2, parent_id=1, pcode=PCode.AVATAR)
        grandparent = self._create_object(local_id=1)
        # KillObject should only "unsit" child avatars (does this require an ObjectUpdate
        # or is ParentID=0 implied?)
        self._kill_object(grandparent)
        self.assertEqual(2, len(self.object_manager))
        self.assertIsNotNone(self.object_manager.lookup_localid(2))

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
        self.assertEqual({"Position"}, events[1][2])

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

        # If the object is killed and no coarse pos, it shouldn't be in the dict
        # CoarseLocationUpdates are expected to be complete, so any agents missing
        # are no longer in the sim.
        self._kill_object(avatar_obj)
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

    def test_name_cache(self):
        # Receiving an update with a NameValue for an avatar should update NameCache
        obj = self._create_object(
            pcode=PCode.AVATAR,
            namevalue=b'DisplayName STRING RW DS unicodename\n'
                      b'FirstName STRING RW DS firstname\n'
                      b'LastName STRING RW DS Resident\n'
                      b'Title STRING RW DS foo',
        )
        self.assertEqual(self.object_manager.name_cache.lookup(obj.FullID).FirstName, "firstname")
        av = self.object_manager.lookup_avatar(obj.FullID)
        self.assertEqual(av.Name, "firstname Resident")
