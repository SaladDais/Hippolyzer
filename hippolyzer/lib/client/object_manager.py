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
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.objects import (
    normalize_object_update,
    normalize_terse_object_update,
    normalize_object_update_compressed_data,
    normalize_object_update_compressed,
    Object, handle_to_global_pos,
)
from hippolyzer.lib.base.settings import Settings
from hippolyzer.lib.client.namecache import NameCache, NameCacheEntry
from hippolyzer.lib.client.state import BaseClientSession, BaseClientRegion
from hippolyzer.lib.base.templates import PCode, ObjectStateSerializer


LOG = logging.getLogger(__name__)
OBJECT_OR_LOCAL = Union[Object, int]


class ObjectUpdateType(enum.IntEnum):
    OBJECT_UPDATE = enum.auto()
    PROPERTIES = enum.auto()
    FAMILY = enum.auto()
    COSTS = enum.auto()
    KILL = enum.auto()


class ClientObjectManager:
    """
    Object manager for a specific region
    """

    __slots__ = ("_region", "_world_objects", "state")

    def __init__(self, region: BaseClientRegion):
        self._region: BaseClientRegion = proxify(region)
        self._world_objects: ClientWorldObjectManager = proxify(region.session().objects)
        self.state: RegionObjectsState = RegionObjectsState()

    def __len__(self):
        return len(self.state.localid_lookup)

    @property
    def all_objects(self) -> Iterable[Object]:
        return self.state.localid_lookup.values()

    @property
    def missing_locals(self) -> Set[int]:
        return self.state.missing_locals

    def clear(self):
        self.state.clear()
        if self._region.handle is not None:
            # We're tracked by the world object manager, tell it to untrack
            # any objects that we owned
            self._world_objects.clear_region_objects(self._region.handle)

    def lookup_localid(self, localid: int) -> Optional[Object]:
        return self.state.lookup_localid(localid)

    def lookup_fullid(self, fullid: UUID) -> Optional[Object]:
        obj = self._world_objects.lookup_fullid(fullid)
        if obj is None or obj.RegionHandle != self._region.handle:
            return None
        return obj

    @property
    def all_avatars(self) -> Iterable[Avatar]:
        return tuple(a for a in self._world_objects.all_avatars
                     if a.RegionHandle == self._region.handle)

    def lookup_avatar(self, fullid: UUID) -> Optional[Avatar]:
        for avatar in self.all_avatars:
            if avatar.FullID == fullid:
                return avatar
        return None

    # noinspection PyUnusedLocal
    def _is_localid_selected(self, local_id: int):
        return False

    def request_object_properties(self, objects: Union[OBJECT_OR_LOCAL, Sequence[OBJECT_OR_LOCAL]]) \
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
                *[Block("ObjectData", ObjectLocalID=x) for x in ids_to_req[:255]],
            ]
            # Selecting causes ObjectProperties to be sent
            self._region.circuit.send(Message("ObjectSelect", blocks))
            self._region.circuit.send(Message("ObjectDeselect", blocks))
            ids_to_req = ids_to_req[255:]

        futures = []
        for local_id in local_ids:
            if local_id in unselected_ids:
                # Need to wait until we get our reply
                fut = self.state.register_future(local_id, ObjectUpdateType.PROPERTIES)
            else:
                # This was selected so we should already have up to date info
                fut = asyncio.Future()
                fut.set_result(self.lookup_localid(local_id))
            futures.append(fut)
        return futures

    def request_missing_objects(self) -> List[asyncio.Future[Object]]:
        return self.request_objects(self.state.missing_locals)

    def request_objects(self, local_ids: Union[int, Iterable[int]]) -> List[asyncio.Future[Object]]:
        """
        Request object local IDs, returning a list of awaitable handles for the objects

        Some may never be resolved, so use `asyncio.wait()` or `asyncio.wait_for()`.
        """
        if isinstance(local_ids, int):
            local_ids = (local_ids,)
        elif isinstance(local_ids, set):
            local_ids = tuple(local_ids)

        session = self._region.session()

        ids_to_req = local_ids
        while ids_to_req:
            self._region.circuit.send(Message(
                "RequestMultipleObjects",
                Block("AgentData", AgentID=session.agent_id, SessionID=session.id),
                *[Block("ObjectData", CacheMissType=0, ID=x) for x in ids_to_req[:255]],
            ))
            ids_to_req = ids_to_req[255:]

        futures = []
        for local_id in local_ids:
            futures.append(self.state.register_future(local_id, ObjectUpdateType.OBJECT_UPDATE))
        return futures


class ObjectEvent:
    __slots__ = ("object", "updated", "update_type")

    object: Object
    updated: Set[str]
    update_type: ObjectUpdateType

    def __init__(self, obj: Object, updated: Set[str], update_type: ObjectUpdateType):
        self.object = obj
        self.updated = updated
        self.update_type = update_type

    @property
    def name(self) -> ObjectUpdateType:
        return self.update_type


class ClientWorldObjectManager:
    """Manages Objects for a session's whole world"""
    def __init__(self, session: BaseClientSession, settings: Settings, name_cache: Optional[NameCache]):
        self._session: BaseClientSession = session
        self._settings = settings
        self.name_cache = name_cache or NameCache()
        self.events: MessageHandler[ObjectEvent, ObjectUpdateType] = MessageHandler(take_by_default=False)
        self._fullid_lookup: Dict[UUID, Object] = {}
        self._avatars: Dict[UUID, Avatar] = {}
        self._avatar_objects: Dict[UUID, Object] = {}
        self._region_managers: Dict[int, ClientObjectManager] = {}
        message_handler = self._session.message_handler
        message_handler.subscribe("ObjectUpdate", self._handle_object_update)
        message_handler.subscribe("ImprovedTerseObjectUpdate",
                                  self._handle_terse_object_update)
        message_handler.subscribe("ObjectUpdateCompressed",
                                  self._handle_object_update_compressed)
        message_handler.subscribe("ObjectUpdateCached",
                                  self._handle_object_update_cached)
        message_handler.subscribe("CoarseLocationUpdate",
                                  self._handle_coarse_location_update)
        message_handler.subscribe("KillObject",
                                  self._handle_kill_object)
        message_handler.subscribe("ObjectProperties",
                                  self._handle_object_properties_generic)
        message_handler.subscribe("ObjectPropertiesFamily",
                                  self._handle_object_properties_generic)

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

    def _get_region_state(self, handle: int) -> Optional[RegionObjectsState]:
        val = self._get_region_manager(handle)
        if val is None:
            return None
        return val.state

    def track_region_objects(self, handle: int):
        """Start tracking objects for a region"""
        if self._get_region_manager(handle) is None:
            self._region_managers[handle] = proxify(self._session.region_by_handle(handle).objects)

    def clear_region_objects(self, handle: int):
        """Handle signal that a region object manager was just cleared"""
        # Make sure they're gone from our lookup table
        for obj in tuple(self._fullid_lookup.values()):
            if obj.RegionHandle == handle:
                del self._fullid_lookup[obj.FullID]
        self._rebuild_avatar_objects()

    def _get_region_manager(self, handle: int) -> Optional[ClientObjectManager]:
        return self._region_managers.get(handle)

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
            region_mgr = self._get_region_manager(region_handle)
            futs.extend(region_mgr.request_object_properties(region_objs))
        return futs

    async def load_ancestors(self, obj: Object, wait_time: float = 1.0):
        """
        Ensure that the entire chain of parents above this object is loaded

        Use this to make sure the object you're dealing with isn't orphaned and
        its RegionPosition can be determined.
        """
        region_mgr = self._get_region_manager(obj.RegionHandle)
        while obj.ParentID:
            if obj.Parent is None:
                await asyncio.wait_for(region_mgr.request_objects(obj.ParentID)[0], wait_time)
            obj = obj.Parent

    def clear(self):
        self._avatars.clear()
        for region_mgr in self._region_managers.values():
            region_mgr.clear()
        if self._fullid_lookup:
            LOG.warning(f"Had {len(self._fullid_lookup)} objects not tied to a region manager!")
        self._fullid_lookup.clear()
        self._rebuild_avatar_objects()
        self._region_managers.clear()

    def _update_existing_object(self, obj: Object, new_properties: dict, update_type: ObjectUpdateType):
        old_parent_id = obj.ParentID
        new_parent_id = new_properties.get("ParentID", obj.ParentID)
        old_local_id = obj.LocalID
        new_local_id = new_properties.get("LocalID", obj.LocalID)
        old_region_handle = obj.RegionHandle
        new_region_handle = new_properties.get("RegionHandle", obj.RegionHandle)
        old_region_state = self._get_region_state(old_region_handle)
        new_region_state = self._get_region_state(new_region_handle)

        actually_updated_props = set()

        if old_region_handle != new_region_handle:
            # The object just changed regions, we have to remove it from the old one.
            # Our LocalID will most likely change because, well, our locale changed.
            old_region_state.untrack_object(obj)
        elif old_local_id != new_local_id:
            # Our LocalID changed, and we deal with linkages to other prims by
            # LocalID association. Break any links since our LocalID is changing.
            # Could happen if we didn't mark an attachment prim dead and the parent agent
            # came back into the sim. Attachment FullIDs do not change across TPs,
            # LocalIDs do. This at least lets us partially recover from the bad state.
            new_localid = new_properties["LocalID"]
            LOG.warning(f"Got an update with new LocalID for {obj.FullID}, {obj.LocalID} != {new_localid}. "
                        f"May have mishandled a KillObject for a prim that left and re-entered region.")
            old_region_state.untrack_object(obj)
            obj.LocalID = new_localid
            old_region_state.track_object(obj)
            actually_updated_props |= {"LocalID"}

        actually_updated_props |= obj.update_properties(new_properties)

        if new_region_handle != old_region_handle:
            # Region just changed to this region, we should have untracked it before
            # so mark it tracked on this region. This should implicitly pick up any
            # orphans and handle parent ID changes.
            if new_region_state is not None:
                new_region_state.track_object(obj)
            else:
                # This will leave a regionless object in the global lookup dict, same as indra.
                LOG.warning(f"Tried to move object {obj!r} to unknown region {new_region_handle}")

            if obj.PCode == PCode.AVATAR:
                # `Avatar` instances are handled separately. Update all Avatar objects so
                # we can deal with the RegionHandle change.
                self._rebuild_avatar_objects()
        elif new_parent_id != old_parent_id:
            # Parent ID changed, but we're in the same region
            new_region_state.handle_object_reparented(obj, old_parent_id=old_parent_id)

        if actually_updated_props and new_region_state is not None:
            self._run_object_update_hooks(obj, actually_updated_props, update_type)

    def _track_new_object(self, region: RegionObjectsState, obj: Object):
        region.track_object(obj)
        self._fullid_lookup[obj.FullID] = obj
        if obj.PCode == PCode.AVATAR:
            self._avatar_objects[obj.FullID] = obj
            self._rebuild_avatar_objects()
        self._run_object_update_hooks(obj, set(obj.to_dict().keys()), ObjectUpdateType.OBJECT_UPDATE)

    def _kill_object_by_local_id(self, region_state: RegionObjectsState, local_id: int):
        obj = region_state.lookup_localid(local_id)
        region_state.missing_locals -= {local_id}
        child_ids: Sequence[int]

        if obj:
            self._run_kill_object_hooks(obj)
            child_ids = obj.ChildIDs
        else:
            LOG.debug(f"Tried to kill unknown object {local_id}")
            # Kill any pending futures it might have had since untrack_object()
            # won't be called.
            region_state.cancel_futures(local_id)
            # If it had any orphans, they need to die.
            child_ids = region_state.collect_orphans(local_id)

        # KillObject implicitly kills descendents
        # This may mutate child_ids, use the reversed iterator so we don't
        # invalidate the iterator during removal.
        for child_id in reversed(child_ids):
            # indra special-cases avatar PCodes and doesn't mark them dead
            # due to cascading kill. Is this correct? Do avatars require
            # explicit kill? Does this imply ParentID = 0 or do we need
            # an explicit follow-up update?
            child_obj = region_state.lookup_localid(child_id)
            if child_obj and child_obj.PCode == PCode.AVATAR:
                continue
            self._kill_object_by_local_id(region_state, child_id)

        # Have to do this last, since untracking will clear child IDs
        if obj:
            region_state.untrack_object(obj)
            self._fullid_lookup.pop(obj.FullID, None)
            if obj.PCode == PCode.AVATAR:
                self._avatar_objects.pop(obj.FullID, None)
                self._rebuild_avatar_objects()

    def _handle_object_update(self, msg: Message):
        seen_locals = []
        handle = msg["RegionData"]["RegionHandle"]
        region_state = self._get_region_state(handle)
        for block in msg['ObjectData']:
            object_data = normalize_object_update(block, handle)
            seen_locals.append(object_data["LocalID"])
            if region_state is None:
                LOG.warning(f"Got ObjectUpdate for unknown region {handle}: {object_data!r}")
            # Do a lookup by FullID, if an object with this FullID already exists anywhere in
            # our view of the world then we want to move it to this region.
            obj = self.lookup_fullid(object_data["FullID"])
            if obj:
                self._update_existing_object(obj, object_data, ObjectUpdateType.OBJECT_UPDATE)
            else:
                if region_state is None:
                    continue
                self._track_new_object(region_state, Object(**object_data))
        msg.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_terse_object_update(self, msg: Message):
        seen_locals = []
        handle = msg["RegionData"]["RegionHandle"]
        region_state = self._get_region_state(handle)
        for block in msg['ObjectData']:
            object_data = normalize_terse_object_update(block, handle)

            if region_state is None:
                LOG.warning(f"Got ImprovedTerseObjectUpdate for unknown region {handle}: {object_data!r}")
                continue

            obj = region_state.lookup_localid(object_data["LocalID"])
            # Can only update existing object with this message
            if obj:
                # Need the Object as context because decoding state requires PCode.
                state_deserializer = ObjectStateSerializer.deserialize
                object_data["State"] = state_deserializer(ctx_obj=obj, val=object_data["State"])
                self._update_existing_object(obj, object_data, ObjectUpdateType.OBJECT_UPDATE)
            else:
                if region_state:
                    region_state.missing_locals.add(object_data["LocalID"])
                LOG.debug(f"Received terse update for unknown object {object_data['LocalID']}")
            seen_locals.append(object_data["LocalID"])

        msg.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_object_update_cached(self, msg: Message):
        seen_locals = []
        missing_locals = set()
        handle = msg["RegionData"]["RegionHandle"]
        region_state = self._get_region_state(handle)
        for block in msg['ObjectData']:
            seen_locals.append(block["ID"])
            update_flags = block.deserialize_var("UpdateFlags", make_copy=False)

            if region_state is None:
                LOG.warning(f"Got ObjectUpdateCached for unknown region {handle}: {block!r}")
                continue

            # Check if we already know about the object
            obj = region_state.lookup_localid(block["ID"])
            if obj is not None and obj.CRC == block["CRC"]:
                self._update_existing_object(obj, {
                    "UpdateFlags": update_flags,
                    "RegionHandle": handle,
                }, ObjectUpdateType.OBJECT_UPDATE)
                continue

            cached_obj_data = self._lookup_cache_entry(handle, block["ID"], block["CRC"])
            if cached_obj_data is not None:
                cached_obj = normalize_object_update_compressed_data(cached_obj_data)
                cached_obj["UpdateFlags"] = update_flags
                cached_obj["RegionHandle"] = handle
                self._track_new_object(region_state, Object(**cached_obj))
                continue

            # Don't know about it and wasn't cached.
            missing_locals.add(block["ID"])
        if region_state:
            region_state.missing_locals.update(missing_locals)
        if missing_locals:
            self._handle_object_update_cached_misses(handle, missing_locals)
        msg.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_object_update_cached_misses(self, region_handle: int, missing_locals: Set[int]):
        """Handle an ObjectUpdateCached that referenced some un-cached local IDs"""
        region_mgr = self._get_region_manager(region_handle)
        region_mgr.request_objects(missing_locals)

    # noinspection PyUnusedLocal
    def _lookup_cache_entry(self, region_handle: int, local_id: int, crc: int) -> Optional[bytes]:
        return None

    def _handle_object_update_compressed(self, msg: Message):
        seen_locals = []
        handle = msg["RegionData"]["RegionHandle"]
        region_state = self._get_region_state(handle)
        for block in msg['ObjectData']:
            object_data = normalize_object_update_compressed(block, handle)
            seen_locals.append(object_data["LocalID"])
            if region_state is None:
                LOG.warning(f"Got ObjectUpdateCompressed for unknown region {handle}: {object_data!r}")
            obj = self.lookup_fullid(object_data["FullID"])
            if obj:
                self._update_existing_object(obj, object_data, ObjectUpdateType.OBJECT_UPDATE)
            else:
                if region_state is None:
                    continue
                self._track_new_object(region_state, Object(**object_data))
        msg.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_object_properties_generic(self, packet: Message):
        seen_locals = []
        for block in packet["ObjectData"]:
            object_properties = dict(block.items())
            if packet.name == "ObjectProperties":
                object_properties["TextureID"] = block.deserialize_var("TextureID")

            obj = self.lookup_fullid(block["ObjectID"])
            if obj:
                seen_locals.append(obj.LocalID)
                self._update_existing_object(obj, object_properties, ObjectUpdateType.PROPERTIES)
            else:
                LOG.debug(f"Received {packet.name} for unknown {block['ObjectID']}")
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_kill_object(self, message: Message):
        seen_locals = []

        # Have to look up region based on sender, handle not sent in this message
        region = self._session.region_by_circuit_addr(message.sender)
        region_state = region.objects.state
        for block in message["ObjectData"]:
            self._kill_object_by_local_id(region_state, block["ID"])
            seen_locals.append(block["ID"])
        message.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_coarse_location_update(self, message: Message):
        # Have to look up region based on sender, handle not sent in this message
        region = self._session.region_by_circuit_addr(message.sender)
        region_state = region.objects.state
        region_state.coarse_locations.clear()

        coarse_locations: Dict[UUID, Vector3] = {}
        for agent_block, location_block in zip(message["AgentData"], message["Location"]):
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

        region_state.coarse_locations.update(coarse_locations)
        self._rebuild_avatar_objects()

    def _process_get_object_cost_response(self, parsed: dict):
        if "error" in parsed:
            return
        for object_id, object_costs in parsed.items():
            obj = self.lookup_fullid(UUID(object_id))
            if not obj:
                LOG.debug(f"Received ObjectCost for unknown {object_id}")
                continue
            obj.ObjectCosts.update(object_costs)
            self._run_object_update_hooks(obj, {"ObjectCosts"}, ObjectUpdateType.COSTS)

    def _run_object_update_hooks(self, obj: Object, updated_props: Set[str], update_type: ObjectUpdateType):
        region_state = self._get_region_state(obj.RegionHandle)
        region_state.resolve_futures(obj, update_type)
        if obj.PCode == PCode.AVATAR and "NameValue" in updated_props:
            if obj.NameValue:
                self.name_cache.update(obj.FullID, obj.NameValue.to_dict())
        self.events.handle(ObjectEvent(obj, updated_props, update_type))

    def _run_kill_object_hooks(self, obj: Object):
        self.events.handle(ObjectEvent(obj, set(), ObjectUpdateType.KILL))

    def _rebuild_avatar_objects(self):
        # Get all avatars known through coarse locations and which region the location was in
        coarse_locations: Dict[UUID, Tuple[int, Vector3]] = {}
        for region_handle, region in self._region_managers.items():
            for av_key, location in region.state.coarse_locations.items():
                coarse_locations[av_key] = (region_handle, location)

        # Merge together avatars known through coarse locations or objects, with details for both
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
                    # If we have a real value for Z then throw away any stale guesses
                    if av.CoarseLocation.Z != math.inf:
                        av.GuessedZ = None
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
                # Already handled in the update step above
                continue
            region_handle = None
            coarse_location = None
            if coarse_pair:
                region_handle, coarse_location = coarse_pair
            if av_obj:
                # Prefer the region handle from the Object if we have one
                region_handle = av_obj.RegionHandle
            assert region_handle is not None
            self._avatars[av_key] = Avatar(
                full_id=av_key,
                region_handle=region_handle,
                resolved_name=self.name_cache.lookup(av_key, create_if_none=True),
                coarse_location=coarse_location,
                obj=av_obj,
            )


class RegionObjectsState:
    """
    Internal class for tracking Object state within a specific region

    Should only be directly used by the world and region ObjectManagers.
    """

    __slots__ = (
        "handle", "missing_locals", "_orphans", "localid_lookup", "coarse_locations",
        "_object_futures"
    )

    def __init__(self):
        self.missing_locals = set()
        self.localid_lookup: Dict[int, Object] = {}
        self.coarse_locations: Dict[UUID, Vector3] = {}
        self._object_futures: Dict[Tuple[int, int], List[asyncio.Future]] = {}
        self._orphans: Dict[int, List[int]] = collections.defaultdict(list)

    def clear(self):
        """Called by the owning ObjectManager when it knows the region is going away"""
        for fut in tuple(itertools.chain(*self._object_futures.values())):
            fut.cancel()
        self._object_futures.clear()
        self._orphans.clear()
        self.coarse_locations.clear()
        self.missing_locals.clear()
        self.localid_lookup.clear()

    def lookup_localid(self, localid: int) -> Optional[Object]:
        return self.localid_lookup.get(localid)

    def track_object(self, obj: Object):
        """Assign ownership of Object to this region"""
        obj_same_localid = self.localid_lookup.get(obj.LocalID)
        if obj_same_localid:
            LOG.error(f"Clobbering existing object with LocalID {obj.LocalID}! "
                      f"{obj.to_dict()} clobbered {obj_same_localid.to_dict()}")
        self.localid_lookup[obj.LocalID] = obj
        # If it was missing, it's not missing anymore.
        self.missing_locals -= {obj.LocalID}

        self._parent_object(obj)

        # Adopt any of our orphaned child objects.
        for orphan_local in self.collect_orphans(obj.LocalID):
            child_obj = self.localid_lookup.get(orphan_local)
            # Shouldn't be any dead children in the orphanage
            assert child_obj is not None
            self._parent_object(child_obj)

    def untrack_object(self, obj: Object):
        """
        Take ownership of an Object from this region

        Can happen due to the object being killed, or due to it moving to another region
        """
        former_child_ids = obj.ChildIDs[:]
        for child_id in former_child_ids:
            child_obj = self.localid_lookup.get(child_id)
            assert child_obj is not None
            self._unparent_object(child_obj, child_obj.ParentID)

        # Place any remaining unkilled children in the orphanage
        for child_id in former_child_ids:
            self._track_orphan(child_id, obj.LocalID)

        assert not obj.ChildIDs

        # Make sure the parent knows we went away
        self._unparent_object(obj, obj.ParentID)
        # Object doesn't belong to this region anymore and won't receive
        # any updates, cancel any pending futures
        self.cancel_futures(obj.LocalID)

        del self.localid_lookup[obj.LocalID]

    def _parent_object(self, obj: Object, insert_at_head=False):
        """Create any links to ancestor Objects for obj"""
        if obj.ParentID:
            parent = self.localid_lookup.get(obj.ParentID)
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
                # We have a parent, but we don't have an Object for it yet
                self.missing_locals.add(obj.ParentID)
                self._track_orphan(obj.LocalID, parent_id=obj.ParentID)
                obj.Parent = None
                LOG.debug(f"{obj.LocalID} updated with parent {obj.ParentID}, but parent wasn't found!")

    def _unparent_object(self, obj: Object, old_parent_id: int):
        """Break any links to ancestor Objects for obj"""
        obj.Parent = None
        if old_parent_id:
            # Had a parent, remove this from the child and orphan lists.
            removed = self._untrack_orphan(obj, old_parent_id)

            old_parent = self.localid_lookup.get(old_parent_id)
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

    def handle_object_reparented(self, obj: Object, old_parent_id: int):
        """Recreate any links to ancestor Objects for obj due to parent changes"""
        self._unparent_object(obj, old_parent_id)
        self._parent_object(obj, insert_at_head=True)

    def collect_orphans(self, parent_localid: int) -> Sequence[int]:
        """Take ownership of any orphan IDs belonging to parent_localid"""
        return self._orphans.pop(parent_localid, [])

    def _track_orphan(self, local_id: int, parent_id: int):
        if len(self._orphans) > 100:
            LOG.warning(f"Orphaned object dict is getting large: {len(self._orphans)}")
        self._orphans[parent_id].append(local_id)

    def _untrack_orphan(self, obj: Object, parent_id: int):
        """Remove obj from parent_id's list of orphans if present"""
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

    def register_future(self, local_id: int, future_type: ObjectUpdateType) -> asyncio.Future[Object]:
        fut = asyncio.Future()
        fut_key = (local_id, future_type)
        local_futs = self._object_futures.get(fut_key, [])
        local_futs.append(fut)
        self._object_futures[fut_key] = local_futs
        fut.add_done_callback(local_futs.remove)
        return fut

    def resolve_futures(self, obj: Object, update_type: ObjectUpdateType):
        futures = self._object_futures.get((obj.LocalID, update_type), [])
        for fut in futures[:]:
            fut.set_result(obj)

    def cancel_futures(self, local_id: int):
        # Object went away, so need to kill any pending futures.
        for fut_key, futs in self._object_futures.items():
            if fut_key[0] == local_id:
                for fut in futs:
                    fut.cancel()
                break


class LocationType(enum.IntEnum):
    NONE = enum.auto()
    COARSE = enum.auto()
    EXACT = enum.auto()


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
        self.GuessedZ: Optional[float] = None
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
            if self.CoarseLocation.Z == math.inf and self.GuessedZ is not None:
                coarse = self.CoarseLocation
                return Vector3(coarse.X, coarse.Y, self.GuessedZ)
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

    @property
    def DisplayName(self) -> Optional[str]:
        if not self._resolved_name:
            return None
        return self._resolved_name.display_name

    @property
    def LegacyName(self) -> Optional[str]:
        if not self._resolved_name:
            return None
        return self._resolved_name.legacy_name

    def __repr__(self):
        loc_str = str(self.RegionPosition) if self.LocationType != LocationType.NONE else "?"
        return f"<{self.__class__.__name__} {self.FullID} {self.Name!r} @ {loc_str}>"
