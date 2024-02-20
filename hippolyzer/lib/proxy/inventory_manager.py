import asyncio
import datetime as dt
import functools
import logging
from typing import *

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.helpers import get_mtime, create_logged_task
from hippolyzer.lib.client.inventory_manager import InventoryManager
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.viewer_settings import iter_viewer_cache_dirs

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.sessions import Session


LOG = logging.getLogger(__name__)


class ProxyInventoryManager(InventoryManager):
    _session: "Session"

    def __init__(self, session: "Session"):
        # These handlers all need their processing deferred until the cache has been loaded.
        # Since cache is loaded asynchronously, the viewer may get ahead of us due to parsing
        # the cache faster and start requesting inventory details we can't do anything with yet.
        self._handle_update_create_inventory_item = self._wrap_with_cache_defer(
            self._handle_update_create_inventory_item
        )
        self._handle_remove_inventory_item = self._wrap_with_cache_defer(
            self._handle_remove_inventory_item
        )
        self._handle_remove_inventory_folder = self._wrap_with_cache_defer(
            self._handle_remove_inventory_folder
        )
        self._handle_bulk_update_inventory = self._wrap_with_cache_defer(
            self._handle_bulk_update_inventory
        )
        self._handle_move_inventory_item = self._wrap_with_cache_defer(
            self._handle_move_inventory_item
        )
        self.process_aisv3_response = self._wrap_with_cache_defer(
            self.process_aisv3_response
        )

        # Base constructor after, because it registers handlers to specific methods, which need to
        # be wrapped before we call they're registered. Handlers are registered by method reference,
        # not by name!
        super().__init__(session)
        session.http_message_handler.subscribe("InventoryAPIv3", self._handle_aisv3_flow)
        newest_cache = None
        newest_timestamp = dt.datetime(year=1970, month=1, day=1, tzinfo=dt.timezone.utc)
        # So consumers know when the inventory should be complete
        self.cache_loaded: asyncio.Event = asyncio.Event()
        self._cache_deferred_calls: List[Tuple[Callable[..., None], Tuple]] = []
        # Look for the newest version of the cached inventory and use that.
        # Not foolproof, but close enough if we're not sure what viewer is being used.
        for cache_dir in iter_viewer_cache_dirs():
            inv_cache_path = cache_dir / (str(session.agent_id) + ".inv.llsd.gz")
            if inv_cache_path.exists():
                mod = get_mtime(inv_cache_path)
                if not mod:
                    continue
                mod_ts = dt.datetime.fromtimestamp(mod, dt.timezone.utc)
                if mod_ts <= newest_timestamp:
                    continue
                newest_cache = inv_cache_path

        if newest_cache:
            cache_load_fut = asyncio.ensure_future(asyncio.to_thread(self.load_cache, newest_cache))
            # Meh. Don't care if it fails.
            cache_load_fut.add_done_callback(lambda *args: self.cache_loaded.set())
            create_logged_task(self._apply_deferred_after_loaded(), "Apply deferred inventory", LOG)
        else:
            self.cache_loaded.set()

    async def _apply_deferred_after_loaded(self):
        await self.cache_loaded.wait()
        LOG.info("Applying deferred inventory calls")
        deferred_calls = self._cache_deferred_calls[:]
        self._cache_deferred_calls.clear()
        for func, args in deferred_calls:
            try:
                func(*args)
            except:
                LOG.exception("Failed to apply deferred inventory call")

    def _wrap_with_cache_defer(self, func: Callable[..., None]):
        @functools.wraps(func)
        def wrapped(*inner_args):
            if not self.cache_loaded.is_set():
                self._cache_deferred_calls.append((func, inner_args))
            else:
                func(*inner_args)
        return wrapped

    def _handle_aisv3_flow(self, flow: HippoHTTPFlow):
        if flow.response.status_code < 200 or flow.response.status_code > 300:
            # Probably not a success
            return
        content_type = flow.response.headers.get("Content-Type", "")
        if "llsd" not in content_type:
            # Okay, probably still some kind of error...
            return

        # Try and add anything from the response into the model
        self.process_aisv3_response(llsd.parse(flow.response.content))
