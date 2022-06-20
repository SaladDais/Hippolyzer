"""
Check object manager state against region ViewerObject cache

Can't look at every object we've tracked and every object in VOCache
and report mismatches due to weird VOCache cache eviction criteria and certain
cacheable objects not being added to the VOCache.

Off the top of my head, animesh objects get explicit KillObjects at extreme
view distances same as avatars, but will still be present in the cache even
though they will not be in gObjectList.
"""
import asyncio
import logging
from typing import *

from hippolyzer.lib.base.objects import normalize_object_update_compressed_data
from hippolyzer.lib.base.templates import ObjectUpdateFlags, PCode
from hippolyzer.lib.proxy.addon_utils import BaseAddon, GlobalProperty
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import SessionManager, Session
from hippolyzer.lib.proxy.vocache import is_valid_vocache_dir, RegionViewerObjectCacheChain

LOG = logging.getLogger(__name__)


class ObjectManagementValidator(BaseAddon):
    base_cache_path: Optional[str] = GlobalProperty(None)
    orig_auto_request: Optional[bool] = GlobalProperty(None)

    def handle_init(self, session_manager: SessionManager):
        if self.orig_auto_request is None:
            self.orig_auto_request = session_manager.settings.ALLOW_AUTO_REQUEST_OBJECTS
        session_manager.settings.ALLOW_AUTO_REQUEST_OBJECTS = False

        async def _choose_cache_path():
            while not self.base_cache_path:
                cache_dir = await AddonManager.UI.open_dir("Choose the base cache directory")
                if not cache_dir:
                    return
                if not is_valid_vocache_dir(cache_dir):
                    continue
                self.base_cache_path = cache_dir

        if not self.base_cache_path:
            self._schedule_task(_choose_cache_path(), session_scoped=False)

    def handle_unload(self, session_manager: SessionManager):
        session_manager.settings.ALLOW_AUTO_REQUEST_OBJECTS = self.orig_auto_request

    def handle_session_init(self, session: Session):
        # Use only the specified cache path for the vocache
        session.cache_dir = self.base_cache_path

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if message.name != "DisableSimulator":
            return
        # Send it off to the client without handling it normally,
        # we need to defer region teardown in the proxy
        region.circuit.send(message)
        self._schedule_task(self._check_cache_before_region_teardown(region))
        return True

    async def _check_cache_before_region_teardown(self, region: ProxiedRegion):
        await asyncio.sleep(0.5)
        print("Ok, checking cache differences")
        try:
            # Index will have been rewritten, so re-read it.
            region_cache_chain = RegionViewerObjectCacheChain.for_region(
                handle=region.handle,
                cache_id=region.cache_id,
                cache_dir=self.base_cache_path
            )
            if not region_cache_chain.region_caches:
                print(f"no caches for {region!r}?")
                return
            all_full_ids = set()
            for obj in region.objects.all_objects:
                cacheable = True
                orig_obj = obj
                # Walk along the ancestry checking for things that would make the tree non-cacheable
                while obj is not None:
                    if obj.UpdateFlags & ObjectUpdateFlags.TEMPORARY_ON_REZ:
                        cacheable = False
                    if obj.PCode == PCode.AVATAR:
                        cacheable = False
                    obj = obj.Parent
                if cacheable:
                    all_full_ids.add(orig_obj.FullID)

            for key in all_full_ids:
                obj = region.objects.lookup_fullid(key)
                cached_data = region_cache_chain.lookup_object_data(obj.LocalID, obj.CRC)
                if not cached_data:
                    continue
                orig_dict = obj.to_dict()
                parsed_data = normalize_object_update_compressed_data(cached_data)
                updated = obj.update_properties(parsed_data)
                # Can't compare this yet
                updated -= {"TextureEntry"}
                if updated:
                    print(key)
                    for attr in updated:
                        print("\t", attr, orig_dict[attr], parsed_data[attr])
        finally:
            # Ok to teardown region in the proxy now
            region.mark_dead()


addons = [ObjectManagementValidator()]
