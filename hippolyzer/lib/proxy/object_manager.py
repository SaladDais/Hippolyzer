from __future__ import annotations

import logging
from typing import *

from hippolyzer.lib.base import llsd
from hippolyzer.lib.client.object_manager import (
    ClientObjectManager,
    UpdateType,
)

from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.vocache import RegionViewerObjectCacheChain

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion

LOG = logging.getLogger(__name__)


class ProxyObjectManager(ClientObjectManager):
    """
    Object manager for a specific region
    """
    _region: ProxiedRegion

    def __init__(
            self,
            region: ProxiedRegion,
            use_vo_cache: bool = False
    ):
        super().__init__(region)
        self.use_vo_cache = use_vo_cache
        self.cache_loaded = False
        self.object_cache = RegionViewerObjectCacheChain([])

        region.http_message_handler.subscribe("GetObjectCost",
                                              self._handle_get_object_cost)

    def _handle_get_object_cost(self, flow: HippoHTTPFlow):
        parsed = llsd.parse_xml(flow.response.content)
        self._process_get_object_cost_response(parsed)

    def run_object_update_hooks(self, obj: Object, updated_props: Set[str], update_type: UpdateType):
        super().run_object_update_hooks(obj, updated_props, update_type)
        AddonManager.handle_object_updated(self._region.session(), self._region, obj, updated_props)

    def run_kill_object_hooks(self, obj: Object):
        AddonManager.handle_object_killed(self._region.session(), self._region, obj)

    def _lookup_cache_entry(self, local_id: int, crc: int) -> Optional[bytes]:
        return self.object_cache.lookup_object_data(local_id, crc)

    def load_cache(self):
        if not self.use_vo_cache or self.cache_loaded:
            return
        handle = self._region.handle
        if not handle:
            LOG.warning(f"Tried to load cache for {self._region} without a handle")
            return
        self.cache_loaded = True
        self.object_cache = RegionViewerObjectCacheChain.for_region(handle, self._region.cache_id)

    def _handle_object_update_cached_misses(self, local_ids: Set[int]):
        # Don't do anything automatically. People have to manually ask for
        # missed objects to be fetched.
        pass

    def clear(self):
        super().clear()
        self.object_cache = RegionViewerObjectCacheChain([])
        self.cache_loaded = False

    def _is_localid_selected(self, localid: int):
        return localid in self._region.session().selected.object_locals
