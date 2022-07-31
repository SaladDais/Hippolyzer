from hippolyzer.lib.client.inventory_manager import InventoryManager
from hippolyzer.lib.client.state import BaseClientSession
from hippolyzer.lib.proxy.viewer_settings import iter_viewer_cache_dirs


class ProxyInventoryManager(InventoryManager):
    def __init__(self, session: BaseClientSession):
        super().__init__(session)
        for cache_dir in iter_viewer_cache_dirs():
            inv_cache_path = cache_dir / (str(session.agent_id) + ".inv.llsd.gz")
            if inv_cache_path.exists():
                self.load_cache(inv_cache_path)
