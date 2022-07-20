from __future__ import annotations

import asyncio
import logging
from typing import *

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.templates import PCode
from hippolyzer.lib.client.namecache import NameCache
from hippolyzer.lib.client.object_manager import (
    ClientObjectManager,
    ObjectUpdateType, ClientWorldObjectManager,
)

from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.settings import ProxySettings
from hippolyzer.lib.proxy.vocache import RegionViewerObjectCacheChain

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion
    from hippolyzer.lib.proxy.sessions import Session

LOG = logging.getLogger(__name__)


class ProxyObjectManager(ClientObjectManager):
    """
    Object manager for a specific region
    """
    _region: ProxiedRegion

    def __init__(
            self,
            region: ProxiedRegion,
            may_use_vo_cache: bool = False
    ):
        super().__init__(region)
        self.may_use_vo_cache = may_use_vo_cache
        self.cache_loaded = False
        self.object_cache = RegionViewerObjectCacheChain([])
        self._cache_miss_timer: Optional[asyncio.TimerHandle] = None
        self.queued_cache_misses: Set[int] = set()
        region.message_handler.subscribe(
            "RequestMultipleObjects",
            self._handle_request_multiple_objects,
        )

    def load_cache(self):
        if not self.may_use_vo_cache or self.cache_loaded:
            return
        handle = self._region.handle
        if not handle:
            LOG.warning(f"Tried to load cache for {self._region} without a handle")
            return
        self.cache_loaded = True
        self.object_cache = RegionViewerObjectCacheChain.for_region(
            handle=handle,
            cache_id=self._region.cache_id,
            cache_dir=self._region.session().cache_dir,
        )

    def request_missed_cached_objects_soon(self, report_only=False):
        if self._cache_miss_timer:
            self._cache_miss_timer.cancel()
        # Basically debounce. Will only trigger 0.2 seconds after the last time it's invoked to
        # deal with the initial flood of ObjectUpdateCached and the natural lag time between that
        # and the viewers' RequestMultipleObjects messages
        loop = asyncio.get_event_loop_policy().get_event_loop()
        self._cache_miss_timer = loop.call_later(0.2, self._request_missed_cached_objects, report_only)

    def _request_missed_cached_objects(self, report_only: bool):
        self._cache_miss_timer = None
        if not self.queued_cache_misses:
            # All the queued cache misses ended up being satisfied without us
            # having to request them, no need to fire off a request.
            return
        if report_only:
            print(f"Would have automatically requested {self.queued_cache_misses!r}")
        else:
            self.request_objects(self.queued_cache_misses)
        self.queued_cache_misses.clear()

    def clear(self):
        super().clear()
        self.object_cache = RegionViewerObjectCacheChain([])
        self.cache_loaded = False
        self.queued_cache_misses.clear()
        if self._cache_miss_timer:
            self._cache_miss_timer.cancel()
        self._cache_miss_timer = None

    def _is_localid_selected(self, localid: int):
        return localid in self._region.session().selected.object_locals

    def _handle_request_multiple_objects(self, msg: Message):
        # Remove any queued cache misses that the viewer just requested for itself
        self.queued_cache_misses -= {b["ID"] for b in msg["ObjectData"]}


class ProxyWorldObjectManager(ClientWorldObjectManager):
    _session: Session
    _settings: ProxySettings

    def __init__(self, session: Session, settings: ProxySettings, name_cache: Optional[NameCache]):
        super().__init__(session, settings, name_cache)
        session.http_message_handler.subscribe(
            "GetObjectCost",
            self._handle_get_object_cost
        )
        session.http_message_handler.subscribe(
            "FirestormBridge",
            self._handle_firestorm_bridge_request,
        )

    def _handle_object_update_cached_misses(self, region_handle: int, missing_locals: Set[int]):
        region_mgr: Optional[ProxyObjectManager] = self._get_region_manager(region_handle)
        if not self._settings.ALLOW_AUTO_REQUEST_OBJECTS:
            if self._settings.USE_VIEWER_OBJECT_CACHE:
                region_mgr.queued_cache_misses |= missing_locals
                region_mgr.request_missed_cached_objects_soon(report_only=True)
        elif self._settings.AUTOMATICALLY_REQUEST_MISSING_OBJECTS:
            # Schedule these local IDs to be requested soon if the viewer doesn't request
            # them itself. Ideally we could just mutate the CRC of the ObjectUpdateCached
            # to force a CRC cache miss in the viewer, but that appears to cause the viewer
            # to drop the resulting ObjectUpdateCompressed when the CRC doesn't match?
            # It was causing all objects to go missing even though the ObjectUpdateCompressed
            # was received.
            region_mgr: Optional[ProxyObjectManager] = self._get_region_manager(region_handle)
            region_mgr.queued_cache_misses |= missing_locals
            region_mgr.request_missed_cached_objects_soon()

    def _run_object_update_hooks(self, obj: Object, updated_props: Set[str], update_type: ObjectUpdateType):
        super()._run_object_update_hooks(obj, updated_props, update_type)
        region = self._session.region_by_handle(obj.RegionHandle)
        if self._settings.ALLOW_AUTO_REQUEST_OBJECTS:
            if obj.PCode == PCode.AVATAR and "ParentID" in updated_props:
                if obj.ParentID and not region.objects.lookup_localid(obj.ParentID):
                    # If an avatar just sat on an object we don't know about, add it to the queued
                    # cache misses and request it if the viewer doesn't. This should happen
                    # regardless of the auto-request missing objects setting because otherwise we
                    # have no way to get a sitting agent's true region location, even if it's ourselves.
                    region.objects.queued_cache_misses.add(obj.ParentID)
                    region.objects.request_missed_cached_objects_soon()
        AddonManager.handle_object_updated(self._session, region, obj, updated_props)

    def _run_kill_object_hooks(self, obj: Object):
        super()._run_kill_object_hooks(obj)
        region = self._session.region_by_handle(obj.RegionHandle)
        AddonManager.handle_object_killed(self._session, region, obj)

    def _lookup_cache_entry(self, region_handle: int, local_id: int, crc: int) -> Optional[bytes]:
        region_mgr: Optional[ProxyObjectManager] = self._get_region_manager(region_handle)
        return region_mgr.object_cache.lookup_object_data(local_id, crc)

    def _handle_get_object_cost(self, flow: HippoHTTPFlow):
        parsed = llsd.parse_xml(flow.response.content)
        self._process_get_object_cost_response(parsed)

    def _handle_firestorm_bridge_request(self, flow: HippoHTTPFlow):
        """
        Pull guessed avatar Z offsets from Firestorm Bridge requests

        CoarseLocationUpdate packets can only represent heights up to 1024, so
        viewers typically use an LSL bridge to get avatar heights beyond that range
        and combine it with their X and Y coords from CoarseLocationUpdate packets.
        """
        if not flow.request.content.startswith(b'<llsd><string>getZOffsets|'):
            return
        parsed: str = llsd.parse_xml(flow.response.content)
        if not parsed:
            return

        # av_1_id, 1025.001, av_2_id, 3000.0, ...
        split = parsed.split(", ")
        for av_id, z_offset in zip(split[0::2], split[1::2]):
            av_id = UUID(av_id)
            z_offset = float(z_offset)
            av = self.lookup_avatar(av_id)
            if not av:
                continue
            av.GuessedZ = z_offset
