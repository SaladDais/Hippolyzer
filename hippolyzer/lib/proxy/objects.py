from __future__ import annotations

import asyncio
import collections
import enum
import itertools
import logging
import math
import typing
import weakref
from typing import *

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID, Vector3
from hippolyzer.lib.base.helpers import proxify
from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.objects import (
    handle_to_global_pos,
    normalize_object_update,
    normalize_terse_object_update,
    normalize_object_update_compressed_data,
    normalize_object_update_compressed,
    Object,
)
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.namecache import NameCache, NameCacheEntry
from hippolyzer.lib.proxy.templates import PCode, ObjectStateSerializer
from hippolyzer.lib.proxy.vocache import RegionViewerObjectCacheChain

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion
    from hippolyzer.lib.proxy.sessions import Session

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

    def collect_orphans(self, parent_localid: int) -> typing.Sequence[int]:
        return self._orphans.pop(parent_localid, [])

    def track_orphan(self, obj: Object):
        self.track_orphan_by_id(obj.LocalID, obj.ParentID)

    def track_orphan_by_id(self, local_id, parent_id):
        if len(self._orphans) > 100:
            LOG.warning(f"Orphaned object dict is getting large: {len(self._orphans)}")
        self._orphans[parent_id].append(local_id)


OBJECT_OR_LOCAL = typing.Union[Object, int]


class LocationType(enum.IntEnum):
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
        self._coarse_location = coarse_location
        self._resolved_name = resolved_name

    @property
    def LocationType(self) -> "LocationType":
        if self.Object and self.Object.AncestorsKnown:
            return LocationType.EXACT
        return LocationType.COARSE

    @property
    def RegionPosition(self) -> Vector3:
        if self.Object and self.Object.AncestorsKnown:
            return self.Object.RegionPosition
        if self._coarse_location is not None:
            return self._coarse_location
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


class ObjectManager:
    """
    Object manager for a specific region
    """

    def __init__(self, region: ProxiedRegion, use_vo_cache: bool = False):
        self._region: ProxiedRegion = proxify(region)
        self.use_vo_cache = use_vo_cache
        self.cache_loaded: bool = False
        self.object_cache: RegionViewerObjectCacheChain = RegionViewerObjectCacheChain([])
        self._localid_lookup: typing.Dict[int, Object] = {}
        self._fullid_lookup: typing.Dict[UUID, int] = {}
        self._coarse_locations: typing.Dict[UUID, Vector3] = {}
        self._object_futures: typing.Dict[Tuple[int, int], List[asyncio.Future]] = {}
        # Objects that we've seen references to but don't have data for
        self.missing_locals = set()
        self._orphan_manager = OrphanManager()
        self._world_objects: WorldObjectManager = region.session().objects
        self.name_cache: NameCache = region.session().session_manager.name_cache

        message_handler = region.message_handler
        message_handler.subscribe("CoarseLocationUpdate",
                                  self._handle_coarse_location_update)
        region.http_message_handler.subscribe("GetObjectCost",
                                              self._handle_get_object_cost)
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

    @property
    def all_avatars(self) -> Iterable[Avatar]:
        av_objects = {o.FullID: o for o in self.all_objects if o.PCode == PCode.AVATAR}
        all_ids = set(av_objects.keys()) | self._coarse_locations.keys()

        avatars: List[Avatar] = []
        for av_id in all_ids:
            av_obj = av_objects.get(av_id)
            coarse_location = self._coarse_locations.get(av_id)

            avatars.append(Avatar(
                full_id=av_id,
                region_handle=self._region.handle,
                coarse_location=coarse_location,
                obj=av_obj,
                resolved_name=self.name_cache.lookup(av_id),
            ))
        return avatars

    def lookup_localid(self, localid: int) -> typing.Optional[Object]:
        return self._localid_lookup.get(localid, None)

    def lookup_fullid(self, fullid: UUID) -> typing.Optional[Object]:
        local_id = self._fullid_lookup.get(fullid, None)
        if local_id is None:
            return None
        return self.lookup_localid(local_id)

    def lookup_avatar(self, fullid: UUID) -> typing.Optional[Avatar]:
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

        # The object just changed regions, we have to remove it from the old one.
        if old_region_handle != new_region_handle:
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
            # so mark it tracked on this region.
            self.track_object(obj)
        elif new_parent_id != old_parent_id:
            # LocalID just changed and we're in the same region
            self._unparent_object(obj, old_parent_id)
            self._parent_object(obj, insert_at_head=True)

        if actually_updated_props:
            self.run_object_update_hooks(obj, actually_updated_props, update_type)

    def _track_new_object(self, obj: Object):
        self.track_object(obj)
        self._world_objects.handle_new_object(obj)
        self.run_object_update_hooks(obj, set(obj.to_dict().keys()), UpdateType.OBJECT_UPDATE)

    def track_object(self, obj: Object):
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

    def _cancel_futures(self, local_id: int):
        # Object was killed, so need to kill any pending futures.
        for fut_key, futs in self._object_futures.items():
            if fut_key[0] == local_id:
                for fut in futs:
                    fut.cancel()
                break

    def _kill_object_by_local_id(self, local_id: int):
        obj = self.lookup_localid(local_id)
        self.missing_locals -= {local_id}
        child_ids: Sequence[int]

        self._cancel_futures(local_id)
        if obj:
            AddonManager.handle_object_killed(self._region.session(), self._region, obj)
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

    def handle_object_update(self, packet: ProxiedMessage):
        seen_locals = []
        for block in packet['ObjectData']:
            object_data = normalize_object_update(block, self._region.handle)

            seen_locals.append(object_data["LocalID"])
            obj = self._world_objects.lookup_fullid(object_data["FullID"])
            if obj:
                self._update_existing_object(obj, object_data, UpdateType.OBJECT_UPDATE)
            else:
                obj = Object(**object_data)
                self._track_new_object(obj)
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def handle_terse_object_update(self, packet: ProxiedMessage):
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

    def handle_object_update_cached(self, packet: ProxiedMessage):
        seen_locals = []
        for block in packet['ObjectData']:
            seen_locals.append(block["ID"])
            update_flags = block.deserialize_var("UpdateFlags", make_copy=False)

            # Check if we already know about the object
            obj = self.lookup_localid(block["ID"])
            if obj is not None:
                self._update_existing_object(obj, {
                    "UpdateFlags": update_flags,
                    "RegionHandle": self._region.handle,
                }, UpdateType.OBJECT_UPDATE)
                continue

            # Check if the object is in a viewer's VOCache
            cached_obj_data = self.object_cache.lookup_object_data(block["ID"], block["CRC"])
            if cached_obj_data is not None:
                cached_obj = normalize_object_update_compressed_data(cached_obj_data)
                cached_obj["UpdateFlags"] = update_flags
                cached_obj["RegionHandle"] = self._region.handle
                self._track_new_object(Object(**cached_obj))
                continue

            # Don't know about it and wasn't cached.
            self.missing_locals.add(block["ID"])
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def handle_object_update_compressed(self, packet: ProxiedMessage):
        seen_locals = []
        for block in packet['ObjectData']:
            object_data = normalize_object_update_compressed(block, self._region.handle)
            seen_locals.append(object_data["LocalID"])
            obj = self._world_objects.lookup_fullid(object_data["FullID"])
            if obj:
                self._update_existing_object(obj, object_data, UpdateType.OBJECT_UPDATE)
            else:
                obj = Object(**object_data)
                self._track_new_object(obj)
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
                self._update_existing_object(obj, object_properties, UpdateType.PROPERTIES)
            else:
                LOG.debug(f"Received {packet.name} for unknown {block['ObjectID']}")
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
            self.run_object_update_hooks(obj, {"ObjectCosts"}, UpdateType.COSTS)

    def _handle_kill_object(self, packet: ProxiedMessage):
        seen_locals = []
        for block in packet["ObjectData"]:
            self._kill_object_by_local_id(block["ID"])
            seen_locals.append(block["ID"])
        packet.meta["ObjectUpdateIDs"] = tuple(seen_locals)

    def _handle_coarse_location_update(self, packet: ProxiedMessage):
        # TODO: This could lead to weird situations when an avatar crosses a
        #  region border. Might temporarily still have a CoarseLocationUpdate containing
        #  the avatar in the old region, making the avatar appear to be in both regions.
        #  figure out best way to deal with that. Store CoarseLocations by region handle
        #  and always use the newest one containing a particular avatar ID?
        self._coarse_locations.clear()

        coarse_locations: typing.Dict[UUID, Vector3] = {}
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

        self._coarse_locations.update(coarse_locations)

    def run_object_update_hooks(self, obj: Object, updated_props: Set[str], update_type: UpdateType):
        if obj.PCode == PCode.AVATAR and "NameValue" in updated_props:
            if obj.NameValue:
                self.name_cache.update(obj.FullID, obj.NameValue.to_dict())
        futures = self._object_futures.get((obj.LocalID, update_type), [])
        for fut in futures[:]:
            fut.set_result(obj)
        AddonManager.handle_object_updated(self._region.session(), self._region, obj, updated_props)

    def load_cache(self):
        if not self.use_vo_cache or self.cache_loaded:
            return
        handle = self._region.handle
        if not handle:
            LOG.warning(f"Tried to load cache for {self._region} without a handle")
            return
        self.cache_loaded = True
        self.object_cache = RegionViewerObjectCacheChain.for_region(handle, self._region.cache_id)

    def clear(self):
        for obj in self._localid_lookup.values():
            self._world_objects.handle_object_gone(obj)
        self._localid_lookup.clear()
        self._fullid_lookup.clear()
        self._coarse_locations.clear()
        self._orphan_manager.clear()
        self.missing_locals.clear()
        for fut in tuple(itertools.chain(*self._object_futures.values())):
            fut.cancel()
        self._object_futures.clear()
        self.object_cache = RegionViewerObjectCacheChain([])
        self.cache_loaded = False

    def request_object_properties(self, objects: typing.Union[OBJECT_OR_LOCAL, typing.Sequence[OBJECT_OR_LOCAL]])\
            -> List[asyncio.Future[Object]]:
        if isinstance(objects, (Object, int)):
            objects = (objects,)
        if not objects:
            return []

        session = self._region.session()

        local_ids = tuple((o.LocalID if isinstance(o, Object) else o) for o in objects)

        # Don't mess with already selected objects
        unselected_ids = tuple(local for local in local_ids if local not in session.selected.object_locals)
        ids_to_req = unselected_ids

        while ids_to_req:
            blocks = [
                Block("AgentData", AgentID=session.agent_id, SessionID=session.id),
                *[Block("ObjectData", ObjectLocalID=x) for x in ids_to_req[:100]],
            ]
            # Selecting causes ObjectProperties to be sent
            self._region.circuit.send_message(ProxiedMessage("ObjectSelect", blocks))
            self._region.circuit.send_message(ProxiedMessage("ObjectDeselect", blocks))
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

    def request_objects(self, local_ids) -> List[asyncio.Future[Object]]:
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
            self._region.circuit.send_message(ProxiedMessage(
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


class WorldObjectManager:
    """Manages Objects for a session's whole world"""
    def __init__(self, session: Session):
        self._session: Session = proxify(session)
        self._fullid_lookup: Dict[UUID, Object] = {}
        message_handler = self._session.message_handler
        message_handler.subscribe("ObjectUpdate", self._handle_object_update)
        message_handler.subscribe("ImprovedTerseObjectUpdate",
                                  self._handle_terse_object_update)
        message_handler.subscribe("ObjectUpdateCompressed",
                                  self._handle_object_update_compressed)
        message_handler.subscribe("ObjectUpdateCached",
                                  self._handle_object_update_cached)

    def _wrap_region_update_handler(self, handler: Callable, message: ProxiedMessage):
        """
        Dispatch an ObjectUpdate to a region's handler based on RegionHandle

        Indra doesn't care what region actually sent the message, just what
        region handle is in the message, so we need a global message handler
        plus dispatch.
        """
        region = self._session.region_by_handle(message["RegionData"]["RegionHandle"])
        if not region:
            return
        return handler(region.objects, message)

    def _handle_object_update(self, message: ProxiedMessage):
        self._wrap_region_update_handler(ObjectManager.handle_object_update, message)

    def _handle_terse_object_update(self, message: ProxiedMessage):
        self._wrap_region_update_handler(ObjectManager.handle_terse_object_update, message)

    def _handle_object_update_compressed(self, message: ProxiedMessage):
        self._wrap_region_update_handler(ObjectManager.handle_object_update_compressed, message)

    def _handle_object_update_cached(self, message: ProxiedMessage):
        self._wrap_region_update_handler(ObjectManager.handle_object_update_cached, message)

    def handle_new_object(self, obj: Object):
        """Called by a region's ObjectManager when a new Object is tracked"""
        self._fullid_lookup[obj.FullID] = obj

    def handle_object_gone(self, obj: Object):
        """Called by a region's ObjectManager on KillObject or region going away"""
        self._fullid_lookup.pop(obj.FullID, None)

    def lookup_fullid(self, full_id: UUID) -> Optional[Object]:
        return self._fullid_lookup.get(full_id, None)

    def __len__(self):
        return len(self._fullid_lookup)

    @property
    def all_objects(self) -> Iterable[Object]:
        return self._fullid_lookup.values()

    @property
    def all_avatars(self) -> Iterable[Avatar]:
        return itertools.chain(*(r.objects.all_avatars for r in self._session.regions))

    def request_missing_objects(self) -> List[asyncio.Future[Object]]:
        futs = []
        for region in self._session.regions:
            futs.extend(region.objects.request_missing_objects())
        return futs

    def request_object_properties(self, objects: typing.Union[Object, typing.Sequence[Object]]) \
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

    async def ensure_ancestors_loaded(self, obj: Object):
        """
        Ensure that the entire chain of parents above this object is loaded

        Use this to make sure the object you're dealing with isn't orphaned and
        its RegionPosition can be determined.
        """
        region = self._session.region_by_handle(obj.RegionHandle)
        while obj.ParentID:
            if obj.Parent is None:
                await asyncio.wait_for(region.objects.request_objects(obj.ParentID)[0], 1.0)
            obj = obj.Parent
