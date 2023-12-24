import asyncio
import datetime as dt

from hippolyzer.lib.base.helpers import get_mtime
from hippolyzer.lib.client.inventory_manager import InventoryManager
from hippolyzer.lib.client.state import BaseClientSession
from hippolyzer.lib.proxy.viewer_settings import iter_viewer_cache_dirs


class ProxyInventoryManager(InventoryManager):
    def __init__(self, session: BaseClientSession):
        super().__init__(session)
        newest_cache = None
        newest_timestamp = dt.datetime(year=1970, month=1, day=1, tzinfo=dt.timezone.utc)
        # So consumers know when the inventory should be complete
        self.cache_loaded: asyncio.Event = asyncio.Event()
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
        else:
            self.cache_loaded.set()
