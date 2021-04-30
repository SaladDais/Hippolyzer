from __future__ import annotations

import collections
import copy
import logging
import typing
import weakref
from typing import *

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID, TaggedUnion
from hippolyzer.lib.base.helpers import proxify
from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.namevalue import NameValueCollection
from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.templates import PCode, ObjectStateSerializer

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion

LOG = logging.getLogger(__name__)


class OrphanManager:
    def __init__(self):
        self._orphans: typing.Dict[int, typing.List[int]] = collections.defaultdict(list)

    def clear(self):
        return self._orphans.clear()

    def untrack_orphan(self, obj: Object, parent_id: int):
        if parent_id not in self._orphans:
            return False
        orphan_list = self._orphans[parent_id]
        removed = False
        if obj.LocalID in orphan_list:
            orphan_list.remove(obj.LocalID)
            removed = True
        # List is empty now, get rid of it.
        if not orphan_list:
            del self._orphans[parent_id]
        return removed

    def collect_orphans(self, parent: Object) -> typing.Sequence[int]:
        return self._orphans.pop(parent.LocalID, [])

    def track_orphan(self, obj: Object):
        self.track_orphan_by_id(obj.LocalID, obj.ParentID)

    def track_orphan_by_id(self, local_id, parent_id):
        if len(self._orphans) > 100:
            LOG.warning(f"Orphaned object dict is getting large: {len(self._orphans)}")
        self._orphans[parent_id].append(local_id)


OBJECT_OR_LOCAL = typing.Union[Object, int]


class ObjectManager:
    """Object manager for a specific region"""

    def __init__(self, region: ProxiedRegion):
        self._localid_lookup: typing.Dict[int, Object] = {}
        self._fullid_lookup: typing.Dict[UUID, int] = {}
        # Objects that we've seen references to but don't have data for
        self.missing_locals = set()
        self._region: ProxiedRegion = proxify(region)
        self._orphan_manager = OrphanManager()

        message_handler = region.message_handler
        message_handler.subscribe("ObjectUpdate", self._handle_object_update)
        message_handler.subscribe("ImprovedTerseObjectUpdate",
                                  self._handle_terse_object_update)
        message_handler.subscribe("ObjectUpdateCompressed",
                                  self._handle_object_update_compressed)
        message_handler.subscribe("ObjectUpdateCached",
                                  self._handle_object_update_cached)
        message_handler.subscribe("ObjectProperties",
                                  self._handle_object_properties_generic)
        message_handler.subscribe("ObjectPropertiesFamily",
                                  self._handle_object_properties_generic)
        region.http_message_handler.subscribe("GetObjectCost",
                                              self._handle_get_object_cost)
        message_handler.subscribe("KillObject",
                                  self._handle_kill_object)

    @property
    def all_objects(self) -> typing.Iterable[Object]:
        return self._localid_lookup.values()

    @property
    def all_avatars(self) -> typing.Iterable[Object]:
        # This is only avatars within draw distance. Might be useful to have another
        # accessor for UUID + pos that's based on CoarseLocationUpdate.
        return (o for o in self.all_objects if o.PCode == PCode.AVATAR)

    def lookup_localid(self, localid) -> typing.Optional[Object]:
        return self._localid_lookup.get(localid, None)

    def lookup_fullid(self, fullid: UUID) -> typing.Optional[Object]:
        local_id = self._fullid_lookup.get(fullid, None)
        if local_id is None:
            return None
        return self.lookup_localid(local_id)

    def _track_object(self, obj: Object):
        self._localid_lookup[obj.LocalID] = obj
        self._fullid_lookup[obj.FullID] = obj.LocalID
        # If it was missing, it's not missing anymore.
        self.missing_locals -= {obj.LocalID}

        self._parent_object(obj)

        # Adopt any of our orphaned child objects.
        for orphan_local in self._orphan_manager.collect_orphans(obj):
            child_obj = self.lookup_localid(orphan_local)
            # Shouldn't be any dead children in the orphanage
            assert child_obj is not None
            self._parent_object(child_obj)

        self._notify_object_updated(obj, set(obj.to_dict().keys()))

    def _parent_object(self, obj: Object, insert_at_head=False):
        if obj.ParentID:
            parent = self.lookup_localid(obj.ParentID)
            if parent is not None:
                assert obj.LocalID not in parent.ChildIDs
                # Link order is never explicitly passed to clients, so we have to do
                # some nasty guesswork based on order of received initial ObjectUpdates
                # Note that this is broken in the viewer as well, and there doesn't seem
                # to be a foolproof way to get this.
                idx = 0 if insert_at_head else len(parent.ChildIDs)
                parent.ChildIDs.insert(idx, obj.LocalID)
                parent.Children.insert(idx, obj)
                obj.Parent = weakref.proxy(parent)
            else:
                self.missing_locals.add(obj.ParentID)
                self._orphan_manager.track_orphan(obj)
                obj.Parent = None
                LOG.debug(f"{obj.LocalID} updated with parent {obj.ParentID}, but parent wasn't found!")

    def _unparent_object(self, obj: Object, old_parent_id: int):
        obj.Parent = None
        if old_parent_id:
            # Had a parent, remove this from the child list.
            removed = self._orphan_manager.untrack_orphan(obj, old_parent_id)

            old_parent = self.lookup_localid(old_parent_id)
            if old_parent:
                if obj.LocalID in old_parent.ChildIDs:
                    idx = old_parent.ChildIDs.index(obj.LocalID)
                    del old_parent.ChildIDs[idx]
                    del old_parent.Children[idx]
                else:
                    # Something is very broken if this happens
                    LOG.warning(f"Changing parent of {obj.LocalID}, but old parent didn't correctly adopt, "
                                f"was {'' if removed else 'not '}in orphan list")
            else:
                LOG.debug(f"Changing parent of {obj.LocalID}, but couldn't find old parent")

    def _update_existing_object(self, obj: Object, new_properties):
        new_parent_id = new_properties.get("ParentID", obj.ParentID)
        old_parent_id = obj.ParentID

        actually_updated_props = obj.update_properties(new_properties)

        if new_parent_id != old_parent_id:
            self._unparent_object(obj, old_parent_id)
            self._parent_object(obj, insert_at_head=True)

        # Common case where this may be falsy is if we get an ObjectUpdateCached
        # that didn't have a changed UpdateFlags field.
        if actually_updated_props:
            self._notify_object_updated(obj, actually_updated_props)

    def _normalize_object_update(self, block: Block):
        object_data = {
            "FootCollisionPlane": None,
            "SoundFlags": block["Flags"],
            "SoundGain": block["Gain"],
            "SoundRadius": block["Radius"],
            **dict(block.items()),
            "TextureEntry": block.deserialize_var("TextureEntry", make_copy=False),
            "NameValue": block.deserialize_var("NameValue", make_copy=False),
            "TextureAnim": block.deserialize_var("TextureAnim", make_copy=False),
            "ExtraParams": block.deserialize_var("ExtraParams", make_copy=False) or {},
            "PSBlock": block.deserialize_var("PSBlock", make_copy=False).value,
            "UpdateFlags": block.deserialize_var("UpdateFlags", make_copy=False),
            "State": block.deserialize_var("State", make_copy=False),
            **block.deserialize_var("ObjectData", make_copy=False).value,
        }
        # Empty == not updated
        if not object_data["TextureEntry"]:
            object_data.pop("TextureEntry")
        # OwnerID is only set in this packet if a sound is playing. Don't allow
        # ObjectUpdates to clobber _real_ OwnerIDs we had from ObjectProperties
        # with a null UUID.
        if object_data["OwnerID"] == UUID():
            del object_data["OwnerID"]
        del object_data["Flags"]
        del object_data["Gain"]
        del object_data["Radius"]
        del object_data["ObjectData"]
        return object_data

    def _handle_object_update(self, packet: ProxiedMessage):
        seen_locals = []
        for block in packet['ObjectData']:
            object_data = self._normalize_object_update(block)

            seen_locals.append(object_data["ID"])
            obj = self.lookup_fullid(object_data["FullID"])
            if obj:
                self._update_existing_object(obj, object_data)
            else:
                obj = Object(**object_data)
                self._track_object(obj)
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _normalize_terse_object_update(self, block: Block):
        object_data = {
            **block.deserialize_var("Data", make_copy=False),
            **dict(block.items()),
            "TextureEntry": block.deserialize_var("TextureEntry", make_copy=False),
        }
        object_data.pop("Data")
        # Empty == not updated
        if object_data["TextureEntry"] is None:
            object_data.pop("TextureEntry")
        return object_data

    def _handle_terse_object_update(self, packet: ProxiedMessage):
        seen_locals = []
        for block in packet['ObjectData']:
            object_data = self._normalize_terse_object_update(block)
            obj = self.lookup_localid(object_data["ID"])
            # Can only update existing object with this message
            if obj:
                # Need the Object as context because decoding state requires PCode.
                state_deserializer = ObjectStateSerializer.deserialize
                object_data["State"] = state_deserializer(ctx_obj=obj, val=object_data["State"])

            seen_locals.append(object_data["ID"])
            if obj:
                self._update_existing_object(obj, object_data)
            else:
                self.missing_locals.add(object_data["ID"])
                LOG.debug(f"Received terse update for unknown object {object_data['ID']}")

        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_object_update_cached(self, packet: ProxiedMessage):
        seen_locals = []
        for block in packet['ObjectData']:
            seen_locals.append(block["ID"])
            obj = self.lookup_localid(block["ID"])
            if obj is not None:
                self._update_existing_object(obj, {
                    "UpdateFlags": block.deserialize_var("UpdateFlags", make_copy=False),
                })
            else:
                self.missing_locals.add(block["ID"])
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _normalize_object_update_compressed(self, block: Block):
        # TODO: ObjectUpdateCompressed doesn't provide a default value for unused
        #  fields, whereas ObjectUpdate and friends do (TextColor, etc.)
        #  need some way to normalize ObjectUpdates so they won't appear to have
        #  changed just because an ObjectUpdate got sent with a default value
        # Only do a shallow copy
        compressed = copy.copy(block.deserialize_var("Data", make_copy=False))
        # Only used for determining which sections are present
        del compressed["Flags"]

        ps_block = compressed.pop("PSBlockNew", None)
        if ps_block is None:
            ps_block = compressed.pop("PSBlock", None)
        if ps_block is None:
            ps_block = TaggedUnion(0, None)
        compressed.pop("PSBlock", None)
        if compressed["NameValue"] is None:
            compressed["NameValue"] = NameValueCollection()

        object_data = {
            "PSBlock": ps_block.value,
            # Parent flag not set means explicitly un-parented
            "ParentID": compressed.pop("ParentID", None) or 0,
            **compressed,
            **dict(block.items()),
            "UpdateFlags": block.deserialize_var("UpdateFlags", make_copy=False),
        }
        if object_data["TextureEntry"] is None:
            object_data.pop("TextureEntry")
        # Don't clobber OwnerID in case the object has a proper one.
        if object_data["OwnerID"] == UUID():
            del object_data["OwnerID"]
        object_data.pop("Data")
        return object_data

    def _handle_object_update_compressed(self, packet: ProxiedMessage):
        seen_locals = []
        for block in packet['ObjectData']:
            object_data = self._normalize_object_update_compressed(block)
            obj = self.lookup_localid(object_data["ID"])
            seen_locals.append(object_data["ID"])
            if obj:
                self._update_existing_object(obj, object_data)
            else:
                obj = Object(**object_data)
                self._track_object(obj)
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_object_properties_generic(self, packet: ProxiedMessage):
        seen_locals = []
        for block in packet["ObjectData"]:
            object_properties = dict(block.items())
            if packet.name == "ObjectProperties":
                object_properties["TextureID"] = block.deserialize_var("TextureID")

            obj = self.lookup_fullid(block["ObjectID"])
            if obj:
                seen_locals.append(obj.LocalID)
                self._update_existing_object(obj, object_properties)
            else:
                LOG.debug(f"Received {packet.name} for unknown {block['ObjectID']}")
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_kill_object(self, packet: ProxiedMessage):
        seen_locals = []
        for block in packet["ObjectData"]:
            obj = self.lookup_localid(block["ID"])
            seen_locals.append(block["ID"])
            self.missing_locals -= {block["ID"]}
            if obj:
                AddonManager.handle_object_killed(self._region.session(), self._region, obj)

                former_child_ids = obj.ChildIDs[:]
                for child_id in former_child_ids:
                    child_obj = self.lookup_localid(child_id)
                    assert child_obj is not None
                    self._unparent_object(child_obj, child_obj.ParentID)

                del self._localid_lookup[obj.LocalID]
                del self._fullid_lookup[obj.FullID]

                # Place any remaining unkilled children in the orphanage
                for child_id in former_child_ids:
                    self._orphan_manager.track_orphan_by_id(child_id, obj.LocalID)

                assert not obj.ChildIDs

                # Make sure the parent knows we went away
                self._unparent_object(obj, obj.ParentID)
            else:
                logging.debug(f"Received {packet.name} for unknown {block['ID']}")
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_get_object_cost(self, flow: HippoHTTPFlow):
        parsed = llsd.parse_xml(flow.response.content)
        if "error" in parsed:
            return
        for object_id, object_costs in parsed.items():
            obj = self.lookup_fullid(UUID(object_id))
            if not obj:
                LOG.debug(f"Received ObjectCost for unknown {object_id}")
                continue
            obj.ObjectCosts.update(object_costs)
            self._notify_object_updated(obj, {"ObjectCosts"})

    def _notify_object_updated(self, obj: Object, updated_props: Set[str]):
        AddonManager.handle_object_updated(self._region.session(), self._region, obj, updated_props)

    def clear(self):
        self._localid_lookup.clear()
        self._fullid_lookup.clear()
        self._orphan_manager.clear()
        self.missing_locals.clear()

    def request_object_properties(self, objects: typing.Union[OBJECT_OR_LOCAL, typing.Sequence[OBJECT_OR_LOCAL]]):
        if isinstance(objects, (Object, int)):
            objects = (objects,)
        if not objects:
            return

        session = self._region.session()

        local_ids = tuple((o.LocalID if isinstance(o, Object) else o) for o in objects)

        # Don't mess with already selected objects
        local_ids = tuple(local for local in local_ids if local not in session.selected.object_locals)

        while local_ids:
            blocks = [
                Block("AgentData", AgentID=session.agent_id, SessionID=session.id),
                *[Block("ObjectData", ObjectLocalID=x) for x in local_ids[:100]],
            ]
            # Selecting causes ObjectProperties to be sent
            self._region.circuit.send_message(ProxiedMessage("ObjectSelect", blocks))
            self._region.circuit.send_message(ProxiedMessage("ObjectDeselect", blocks))
            local_ids = local_ids[100:]

    def request_missing_objects(self):
        self.request_objects(self.missing_locals)

    def request_objects(self, local_ids):
        if isinstance(local_ids, int):
            local_ids = (local_ids,)
        if isinstance(local_ids, set):
            local_ids = tuple(local_ids)

        session = self._region.session()
        while local_ids:
            self._region.circuit.send_message(ProxiedMessage(
                "RequestMultipleObjects",
                Block("AgentData", AgentID=session.agent_id, SessionID=session.id),
                *[Block("ObjectData", CacheMissType=0, ID=x) for x in local_ids[:100]],
            ))
            local_ids = local_ids[100:]
