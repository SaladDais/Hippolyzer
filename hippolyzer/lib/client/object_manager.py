"""
Manager for a client's view of objects in the region and world.
"""

from __future__ import annotations

import asyncio
import collections
import enum
import itertools
import logging
import math
import weakref
from typing import *

from hippolyzer.lib.base.datatypes import UUID, Vector3
from hippolyzer.lib.base.helpers import proxify
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.objects import (
    normalize_object_update,
    normalize_terse_object_update,
    normalize_object_update_compressed_data,
    normalize_object_update_compressed,
    Object, handle_to_global_pos,
)
from hippolyzer.lib.client.namecache import NameCache, NameCacheEntry
from hippolyzer.lib.client.state import BaseClientSession, BaseClientRegion
from hippolyzer.lib.base.templates import PCode, ObjectStateSerializer


LOG = logging.getLogger(__name__)


class OrphanManager:
    """Tracker for objects that are parented to objects the client doesn't know about"""

    def __init__(self):
        self._orphans: Dict[int, List[int]] = collections.defaultdict(list)

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

    def collect_orphans(self, parent_localid: int) -> Sequence[int]:
        return self._orphans.pop(parent_localid, [])

    def track_orphan(self, obj: Object):
        self.track_orphan_by_id(obj.LocalID, obj.ParentID)

    def track_orphan_by_id(self, local_id, parent_id):
        if len(self._orphans) > 100:
            LOG.warning(f"Orphaned object dict is getting large: {len(self._orphans)}")
        self._orphans[parent_id].append(local_id)


OBJECT_OR_LOCAL = Union[Object, int]


class LocationType(enum.IntEnum):
    NONE = enum.auto()
    COARSE = enum.auto()
    EXACT = enum.auto()


class UpdateType(enum.IntEnum):
    OBJECT_UPDATE = enum.auto()
    PROPERTIES = enum.auto()
    FAMILY = enum.auto()
    COSTS = enum.auto()


class Avatar:
    """Wrapper for an avatar known through ObjectUpdate or CoarseLocationUpdate"""

    def __init__(
            self,
            full_id: UUID,
            region_handle: int,
            obj: Optional["Object"] = None,
            coarse_location: Optional[Vector3] = None,
            resolved_name: Optional[NameCacheEntry] = None,
    ):
        self.FullID: UUID = full_id
        self.Object: Optional["Object"] = obj
        self.RegionHandle: int = region_handle
        # TODO: Allow hooking into getZOffsets FS bridge response
        #  to fill in the Z axis if it's infinite
        self.CoarseLocation = coarse_location
        self.Valid = True
        self._resolved_name = resolved_name

    @property
    def LocationType(self) -> "LocationType":
        if self.Object and self.Object.AncestorsKnown:
            return LocationType.EXACT
        if self.CoarseLocation is not None:
            return LocationType.COARSE
        return LocationType.NONE

    @property
    def RegionPosition(self) -> Vector3:
        if self.Object and self.Object.AncestorsKnown:
            return self.Object.RegionPosition
        if self.CoarseLocation is not None:
            return self.CoarseLocation
        raise ValueError(f"Avatar {self.FullID} has no known position")

    @property
    def GlobalPosition(self) -> Vector3:
        return self.RegionPosition + handle_to_global_pos(self.RegionHandle)

    @property
    def Name(self) -> Optional[str]:
        if not self._resolved_name:
            return None
        return str(self._resolved_name)

    @property
    def PreferredName(self) -> Optional[str]:
        if not self._resolved_name:
            return None
        return self._resolved_name.preferred_name

    def __repr__(self):
        loc_str = str(self.RegionPosition) if self.LocationType != LocationType.NONE else "?"
        return f"<{self.__class__.__name__} {self.FullID} {self.Name!r} @ {loc_str}>"


class ClientObjectManager:
    """
    Object manager for a specific region
    """

    def __init__(self, region: BaseClientRegion):
        self._region: BaseClientRegion = region
        self._localid_lookup: Dict[int, Object] = {}
        self._fullid_lookup: Dict[UUID, int] = {}
        self.coarse_locations: Dict[UUID, Vector3] = {}
        self._object_futures: Dict[Tuple[int, int], List[asyncio.Future]] = {}
        self._orphan_manager = OrphanManager()
        # Objects that we've seen references to but don't have data for
        self.missing_locals = set()

        self._world_objects: ClientWorldObjectManager = proxify(region.session().objects)

        message_handler = region.message_handler
        message_handler.subscribe("CoarseLocationUpdate",
                                  self._handle_coarse_location_update)
        message_handler.subscribe("KillObject",
                                  self._handle_kill_object)
        message_handler.subscribe("ObjectProperties",
                                  self._handle_object_properties_generic)
        message_handler.subscribe("ObjectPropertiesFamily",
                                  self._handle_object_properties_generic)

    def __len__(self):
        return len(self._localid_lookup)

    @property
    def all_objects(self) -> Iterable[Object]:
        return self._localid_lookup.values()

    def lookup_localid(self, localid: int) -> Optional[Object]:
        return self._localid_lookup.get(localid, None)

    def lookup_fullid(self, fullid: UUID) -> Optional[Object]:
        local_id = self._fullid_lookup.get(fullid, None)
        if local_id is None:
            return None
        return self.lookup_localid(local_id)

    @property
    def all_avatars(self) -> Iterable[Avatar]:
        return tuple(a for a in self._world_objects.all_avatars
                     if a.RegionHandle == self._region.handle)

    def lookup_avatar(self, fullid: UUID) -> Optional[Avatar]:
        for avatar in self.all_avatars:
            if avatar.FullID == fullid:
                return avatar
        return None

    def _update_existing_object(self, obj: Object, new_properties: dict, update_type: UpdateType):
        new_parent_id = new_properties.get("ParentID", obj.ParentID)
        new_region_handle = new_properties.get("RegionHandle", obj.RegionHandle)
        new_local_id = new_properties.get("LocalID", obj.LocalID)
        old_parent_id = obj.ParentID
        old_region_handle = obj.RegionHandle
        old_region = self._region.session().region_by_handle(old_region_handle)

        actually_updated_props = set()

        if old_region_handle != new_region_handle:
            # The object just changed regions, we have to remove it from the old one.
            # Our LocalID will most likely change because, well, our locale changed.
            old_region.objects.untrack_object(obj)
        elif obj.LocalID != new_local_id:
            # Our LocalID changed, and we deal with linkages to other prims by
            # LocalID association. Break any links since our LocalID is changing.
            # Could happen if we didn't mark an attachment prim dead and the parent agent
            # came back into the sim. Attachment FullIDs do not change across TPs,
            # LocalIDs do. This at least lets us partially recover from the bad state.
            new_localid = new_properties["LocalID"]
            LOG.warning(f"Got an update with new LocalID for {obj.FullID}, {obj.LocalID} != {new_localid}. "
                        f"May have mishandled a KillObject for a prim that left and re-entered region.")
            old_region.objects.untrack_object(obj)
            obj.LocalID = new_localid
            old_region.objects.track_object(obj)
            actually_updated_props |= {"LocalID"}

        actually_updated_props |= obj.update_properties(new_properties)

        if new_region_handle != old_region_handle:
            # Region just changed to this region, we should have untracked it before
            # so mark it tracked on this region. This should implicitly pick up any
            # orphans and handle parent ID changes.
            self.track_object(obj)
            # `Avatar` instances are owned by WorldObjectManager, let it know an avatar
            # just changed regions so it can update the RegionHandle.
            # TODO: These kinds of complex interdependencies between world / region
            #  object managers shows that almost all logic should just be in the world
            #  object manager, with the region object manager just being a thin wrapper
            #  around it. Could have a dict keyed on region handle that contained
            #  region-specific state like localid lookups, orphan manager, etc.
            if obj.PCode == PCode.AVATAR:
                self._world_objects.rebuild_avatar_objects()
        elif new_parent_id != old_parent_id:
            # Parent ID changed, but we're in the same region
            self._unparent_object(obj, old_parent_id)
            self._parent_object(obj, insert_at_head=True)

        if actually_updated_props:
            self.run_object_update_hooks(obj, actually_updated_props, update_type)

    def _track_new_object(self, obj: Object):
        self.track_object(obj)
        self._world_objects.handle_new_object(obj)
        self.run_object_update_hooks(obj, set(obj.to_dict().keys()), UpdateType.OBJECT_UPDATE)

    def track_object(self, obj: Object):
        obj_same_localid = self._localid_lookup.get(obj.LocalID)
        if obj_same_localid:
            LOG.error(f"Clobbering existing object with LocalID {obj.LocalID}! "
                      f"{obj.to_dict()} clobbered {obj_same_localid.to_dict()}")
            # Clear the clobbered object out of the FullID lookup
            self._fullid_lookup.pop(obj_same_localid.FullID, None)
        self._localid_lookup[obj.LocalID] = obj
        self._fullid_lookup[obj.FullID] = obj.LocalID
        # If it was missing, it's not missing anymore.
        self.missing_locals -= {obj.LocalID}

        self._parent_object(obj)

        # Adopt any of our orphaned child objects.
        for orphan_local in self._orphan_manager.collect_orphans(obj.LocalID):
            child_obj = self.lookup_localid(orphan_local)
            # Shouldn't be any dead children in the orphanage
            assert child_obj is not None
            self._parent_object(child_obj)

    def untrack_object(self, obj: Object):
        former_child_ids = obj.ChildIDs[:]
        for child_id in former_child_ids:
            child_obj = self.lookup_localid(child_id)
            assert child_obj is not None
            self._unparent_object(child_obj, child_obj.ParentID)

        # Place any remaining unkilled children in the orphanage
        for child_id in former_child_ids:
            self._orphan_manager.track_orphan_by_id(child_id, obj.LocalID)

        assert not obj.ChildIDs

        # Make sure the parent knows we went away
        self._unparent_object(obj, obj.ParentID)

        self._cancel_futures(obj.LocalID)

        # Do this last in case we only have a weak reference
        del self._fullid_lookup[obj.FullID]
        del self._localid_lookup[obj.LocalID]

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

    def _kill_object_by_local_id(self, local_id: int):
        obj = self.lookup_localid(local_id)
        self.missing_locals -= {local_id}
        child_ids: Sequence[int]

        self._cancel_futures(local_id)
        if obj:
            self.run_kill_object_hooks(obj)
            child_ids = obj.ChildIDs
        else:
            LOG.debug(f"Tried to kill unknown object {local_id}")
            # If it had any orphans, they need to die.
            child_ids = self._orphan_manager.collect_orphans(local_id)

        # KillObject implicitly kills descendents
        # This may mutate child_ids, use the reversed iterator so we don't
        # invalidate the iterator during removal.
        for child_id in reversed(child_ids):
            # indra special-cases avatar PCodes and doesn't mark them dead
            # due to cascading kill. Is this correct? Do avatars require
            # explicit kill?
            child_obj = self.lookup_localid(child_id)
            if child_obj and child_obj.PCode == PCode.AVATAR:
                continue
            self._kill_object_by_local_id(child_id)

        # Have to do this last, since untracking will clear child IDs
        if obj:
            self.untrack_object(obj)
            self._world_objects.handle_object_gone(obj)

    def handle_object_update(self, packet: Message):
        seen_locals = []
        for block in packet['ObjectData']:
            object_data = normalize_object_update(block, self._region.handle)

            seen_locals.append(object_data["LocalID"])
            # Do a lookup by FullID, if an object with this FullID already exists anywhere in
            # our view of the world then we want to move it to this region.
            obj = self._world_objects.lookup_fullid(object_data["FullID"])
            if obj:
                self._update_existing_object(obj, object_data, UpdateType.OBJECT_UPDATE)
            else:
                self._track_new_object(Object(**object_data))
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def handle_terse_object_update(self, packet: Message):
        seen_locals = []
        for block in packet['ObjectData']:
            object_data = normalize_terse_object_update(block, self._region.handle)
            obj = self.lookup_localid(object_data["LocalID"])
            # Can only update existing object with this message
            if obj:
                # Need the Object as context because decoding state requires PCode.
                state_deserializer = ObjectStateSerializer.deserialize
                object_data["State"] = state_deserializer(ctx_obj=obj, val=object_data["State"])

            seen_locals.append(object_data["LocalID"])
            if obj:
                self._update_existing_object(obj, object_data, UpdateType.OBJECT_UPDATE)
            else:
                self.missing_locals.add(object_data["LocalID"])
                LOG.debug(f"Received terse update for unknown object {object_data['LocalID']}")

        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    # noinspection PyUnusedLocal
    def _lookup_cache_entry(self, local_id: int, crc: int) -> Optional[bytes]:
        return None

    def handle_object_update_cached(self, packet: Message):
        seen_locals = []
        missing_locals = set()
        for block in packet['ObjectData']:
            seen_locals.append(block["ID"])
            update_flags = block.deserialize_var("UpdateFlags", make_copy=False)

            # Check if we already know about the object
            obj = self.lookup_localid(block["ID"])
            if obj is not None and obj.CRC == block["CRC"]:
                self._update_existing_object(obj, {
                    "UpdateFlags": update_flags,
                    "RegionHandle": self._region.handle,
                }, UpdateType.OBJECT_UPDATE)
                continue

            cached_obj_data = self._lookup_cache_entry(block["ID"], block["CRC"])
            if cached_obj_data is not None:
                cached_obj = normalize_object_update_compressed_data(cached_obj_data)
                cached_obj["UpdateFlags"] = update_flags
                cached_obj["RegionHandle"] = self._region.handle
                self._track_new_object(Object(**cached_obj))
                continue

            # Don't know about it and wasn't cached.
            missing_locals.add(block["ID"])
        self.missing_locals.update(missing_locals)
        self._handle_object_update_cached_misses(missing_locals)
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_object_update_cached_misses(self, local_ids: Set[int]):
        self.request_objects(local_ids)

    def handle_object_update_compressed(self, packet: Message):
        seen_locals = []
        for block in packet['ObjectData']:
            object_data = normalize_object_update_compressed(block, self._region.handle)
            seen_locals.append(object_data["LocalID"])
            obj = self._world_objects.lookup_fullid(object_data["FullID"])
            if obj:
                self._update_existing_object(obj, object_data, UpdateType.OBJECT_UPDATE)
            else:
                self._track_new_object(Object(**object_data))
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_object_properties_generic(self, packet: Message):
        seen_locals = []
        for block in packet["ObjectData"]:
            object_properties = dict(block.items())
            if packet.name == "ObjectProperties":
                object_properties["TextureID"] = block.deserialize_var("TextureID")

            obj = self.lookup_fullid(block["ObjectID"])
            if obj:
                seen_locals.append(obj.LocalID)
                self._update_existing_object(obj, object_properties, UpdateType.PROPERTIES)
            else:
                LOG.debug(f"Received {packet.name} for unknown {block['ObjectID']}")
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_kill_object(self, packet: Message):
        seen_locals = []
        for block in packet["ObjectData"]:
            self._kill_object_by_local_id(block["ID"])
            seen_locals.append(block["ID"])
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_coarse_location_update(self, packet: Message):
        self.coarse_locations.clear()

        coarse_locations: Dict[UUID, Vector3] = {}
        for agent_block, location_block in zip(packet["AgentData"], packet["Location"]):
            x, y, z = location_block["X"], location_block["Y"], location_block["Z"]
            coarse_locations[agent_block["AgentID"]] = Vector3(
                X=x,
                Y=y,
                # The z-axis is multiplied by 4 to obtain true Z location
                # The z-axis is also limited to 1020m in height
                # If z == 255 then the true Z is unknown.
                # http://wiki.secondlife.com/wiki/CoarseLocationUpdate
                Z=z * 4 if z != 255 else math.inf,
            )

        self.coarse_locations.update(coarse_locations)
        self._world_objects.rebuild_avatar_objects()

    def clear(self):
        for obj in self._localid_lookup.values():
            self._world_objects.handle_object_gone(obj)
        self.coarse_locations.clear()
        self._localid_lookup.clear()
        self._fullid_lookup.clear()
        self._orphan_manager.clear()
        self.missing_locals.clear()
        for fut in tuple(itertools.chain(*self._object_futures.values())):
            fut.cancel()
        self._object_futures.clear()
        self._world_objects.rebuild_avatar_objects()

    # noinspection PyUnusedLocal
    def _is_localid_selected(self, local_id: int):
        return False

    def _process_get_object_cost_response(self, parsed: dict):
        if "error" in parsed:
            return
        for object_id, object_costs in parsed.items():
            obj = self.lookup_fullid(UUID(object_id))
            if not obj:
                LOG.debug(f"Received ObjectCost for unknown {object_id}")
                continue
            obj.ObjectCosts.update(object_costs)
            self.run_object_update_hooks(obj, {"ObjectCosts"}, UpdateType.COSTS)

    def run_object_update_hooks(self, obj: Object, updated_props: Set[str], update_type: UpdateType):
        futures = self._object_futures.get((obj.LocalID, update_type), [])
        for fut in futures[:]:
            fut.set_result(obj)
        if obj.PCode == PCode.AVATAR and "NameValue" in updated_props:
            if obj.NameValue:
                self._world_objects.name_cache.update(obj.FullID, obj.NameValue.to_dict())

    def run_kill_object_hooks(self, obj: Object):
        pass

    def _cancel_futures(self, local_id: int):
        # Object went away, so need to kill any pending futures.
        for fut_key, futs in self._object_futures.items():
            if fut_key[0] == local_id:
                for fut in futs:
                    fut.cancel()
                break

    def request_object_properties(self, objects: Union[OBJECT_OR_LOCAL, Sequence[OBJECT_OR_LOCAL]])\
            -> List[asyncio.Future[Object]]:
        if isinstance(objects, (Object, int)):
            objects = (objects,)
        if not objects:
            return []

        local_ids = tuple((o.LocalID if isinstance(o, Object) else o) for o in objects)

        # Don't mess with already selected objects
        unselected_ids = tuple(local for local in local_ids if not self._is_localid_selected(local))
        ids_to_req = unselected_ids

        session = self._region.session()
        while ids_to_req:
            blocks = [
                Block("AgentData", AgentID=session.agent_id, SessionID=session.id),
                *[Block("ObjectData", ObjectLocalID=x) for x in ids_to_req[:100]],
            ]
            # Selecting causes ObjectProperties to be sent
            self._region.circuit.send_message(Message("ObjectSelect", blocks))
            self._region.circuit.send_message(Message("ObjectDeselect", blocks))
            ids_to_req = ids_to_req[100:]

        futures = []
        for local_id in local_ids:
            fut = asyncio.Future()
            if local_id in unselected_ids:
                # Need to wait until we get our reply
                fut_key = (local_id, UpdateType.PROPERTIES)
                local_futs = self._object_futures.get(fut_key, [])
                local_futs.append(fut)
                self._object_futures[fut_key] = local_futs
                fut.add_done_callback(local_futs.remove)
            else:
                # This was selected so we should already have up to date info
                fut.set_result(self.lookup_localid(local_id))
            futures.append(fut)
        return futures

    def request_missing_objects(self) -> List[asyncio.Future[Object]]:
        return self.request_objects(self.missing_locals)

    def request_objects(self, local_ids: Union[int, Iterable[int]]) -> List[asyncio.Future[Object]]:
        """
        Request object local IDs, returning a list of awaitable handles for the objects

        Some may never be resolved, so use `asyncio.wait()` or `asyncio.wait_for()`.
        """
        if isinstance(local_ids, int):
            local_ids = (local_ids,)
        if isinstance(local_ids, set):
            local_ids = tuple(local_ids)

        session = self._region.session()
        ids_to_req = local_ids
        while ids_to_req:
            self._region.circuit.send_message(Message(
                "RequestMultipleObjects",
                Block("AgentData", AgentID=session.agent_id, SessionID=session.id),
                *[Block("ObjectData", CacheMissType=0, ID=x) for x in ids_to_req[:100]],
            ))
            ids_to_req = ids_to_req[100:]

        futures = []
        for local_id in local_ids:
            fut = asyncio.Future()
            fut_key = (local_id, UpdateType.OBJECT_UPDATE)
            local_futs = self._object_futures.get(fut_key, [])
            local_futs.append(fut)
            self._object_futures[fut_key] = local_futs
            fut.add_done_callback(local_futs.remove)
            futures.append(fut)
        return futures


class ClientWorldObjectManager:
    """Manages Objects for a session's whole world"""
    def __init__(self, session: BaseClientSession, name_cache: Optional[NameCache]):
        self._session: BaseClientSession = session
        self._fullid_lookup: Dict[UUID, Object] = {}
        self._avatars: Dict[UUID, Avatar] = {}
        self._avatar_objects: Dict[UUID, Object] = {}
        self.name_cache = name_cache or NameCache()
        message_handler = self._session.message_handler
        message_handler.subscribe("ObjectUpdate", self._handle_object_update)
        message_handler.subscribe("ImprovedTerseObjectUpdate",
                                  self._handle_terse_object_update)
        message_handler.subscribe("ObjectUpdateCompressed",
                                  self._handle_object_update_compressed)
        message_handler.subscribe("ObjectUpdateCached",
                                  self._handle_object_update_cached)

    def lookup_fullid(self, full_id: UUID) -> Optional[Object]:
        return self._fullid_lookup.get(full_id, None)

    @property
    def all_objects(self) -> Iterable[Object]:
        return self._fullid_lookup.values()

    def lookup_avatar(self, full_id: UUID) -> Optional[Avatar]:
        return {a.FullID: a for a in self.all_avatars}.get(full_id, None)

    @property
    def all_avatars(self) -> Iterable[Avatar]:
        return tuple(self._avatars.values())

    def __len__(self):
        return len(self._fullid_lookup)

    def _wrap_region_update_handler(self, handler: Callable, message: Message):
        """
        Dispatch an ObjectUpdate to a region's handler based on RegionHandle

        Indra doesn't care what region actually sent the message, just what
        region handle is in the message, so we need a global message handler
        plus dispatch.
        """
        handle = message["RegionData"]["RegionHandle"]
        region = self._session.region_by_handle(handle)
        if not region:
            LOG.warning(f"Got {message.name} for unknown region {handle}")
            return
        return handler(region.objects, message)

    def _handle_object_update(self, message: Message):
        self._wrap_region_update_handler(ClientObjectManager.handle_object_update, message)

    def _handle_terse_object_update(self, message: Message):
        self._wrap_region_update_handler(ClientObjectManager.handle_terse_object_update, message)

    def _handle_object_update_compressed(self, message: Message):
        self._wrap_region_update_handler(ClientObjectManager.handle_object_update_compressed, message)

    def _handle_object_update_cached(self, message: Message):
        self._wrap_region_update_handler(ClientObjectManager.handle_object_update_cached, message)

    def handle_new_object(self, obj: Object):
        """Called by a region's ObjectManager when a new Object is tracked"""
        self._fullid_lookup[obj.FullID] = obj
        if obj.PCode == PCode.AVATAR:
            self._avatar_objects[obj.FullID] = obj
            self.rebuild_avatar_objects()

    def handle_object_gone(self, obj: Object):
        """Called by a region's ObjectManager on KillObject or region going away"""
        self._fullid_lookup.pop(obj.FullID, None)
        if obj.PCode == PCode.AVATAR:
            self._avatar_objects.pop(obj.FullID, None)
            self.rebuild_avatar_objects()

    def rebuild_avatar_objects(self):
        # Merge together avatars known through coarse locations or objects
        coarse_locations: Dict[UUID, Tuple[int, Vector3]] = {}
        for region in self._session.regions:
            for av_key, location in region.objects.coarse_locations.items():
                coarse_locations[av_key] = (region.handle, location)
        current_av_details: Dict[UUID, Tuple[Optional[Tuple[int, Vector3]], Optional[Object]]] = {}
        for av_key in set(coarse_locations.keys()) | set(self._avatar_objects.keys()):
            details = (coarse_locations.get(av_key), self._avatar_objects.get(av_key))
            current_av_details[av_key] = details

        # Look for changes in avatars we're already tracking
        for existing_key in tuple(self._avatars.keys()):
            av = self._avatars[existing_key]
            if existing_key in current_av_details:
                # This avatar this exists, update it.
                coarse_pair, av_obj = current_av_details[existing_key]
                av.Object = av_obj
                if coarse_pair:
                    coarse_handle, coarse_location = coarse_pair
                    av.CoarseLocation = coarse_location
                    av.RegionHandle = coarse_handle
                if av_obj:
                    av.Object = av_obj
                    av.RegionHandle = av_obj.RegionHandle
            else:
                # Avatar isn't in coarse locations or objects, it's gone.
                self._avatars.pop(existing_key, None)
                av.Object = None
                av.CoarseLocation = None
                av.Valid = False

        # Check for any new avatars
        for av_key, (coarse_pair, av_obj) in current_av_details.items():
            if av_key in self._avatars:
                continue
            region_handle = None
            coarse_location = None
            if coarse_pair:
                region_handle, coarse_location = coarse_pair
            if av_obj:
                region_handle = av_obj.RegionHandle
            assert region_handle is not None
            self._avatars[av_key] = Avatar(
                full_id=av_key,
                region_handle=region_handle,
                resolved_name=self.name_cache.lookup(av_key, create_if_none=True),
                coarse_location=coarse_location,
                obj=av_obj,
            )

    def request_missing_objects(self) -> List[asyncio.Future[Object]]:
        futs = []
        for region in self._session.regions:
            futs.extend(region.objects.request_missing_objects())
        return futs

    def request_object_properties(self, objects: Union[Object, Sequence[Object]]) \
            -> List[asyncio.Future[Object]]:
        # Doesn't accept local ID unlike ObjectManager because they're ambiguous here.
        if isinstance(objects, Object):
            objects = (objects,)
        if not objects:
            return []

        # Has to be sent to the region they belong to, so split the objects out by region handle.
        objs_by_region = collections.defaultdict(list)
        for obj in objects:
            objs_by_region[obj.RegionHandle].append(obj)

        futs = []
        for region_handle, region_objs in objs_by_region.items():
            region = self._session.region_by_handle(region_handle)
            futs.extend(region.objects.request_object_properties(region_objs))
        return futs

    async def load_ancestors(self, obj: Object, wait_time: float = 1.0):
        """
        Ensure that the entire chain of parents above this object is loaded

        Use this to make sure the object you're dealing with isn't orphaned and
        its RegionPosition can be determined.
        """
        region = self._session.region_by_handle(obj.RegionHandle)
        while obj.ParentID:
            if obj.Parent is None:
                await asyncio.wait_for(region.objects.request_objects(obj.ParentID)[0], wait_time)
            obj = obj.Parent

    def clear(self):
        self._fullid_lookup.clear()
        self._avatars.clear()
        self._avatar_objects.clear()
