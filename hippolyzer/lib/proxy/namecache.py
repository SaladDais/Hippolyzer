from __future__ import annotations

import logging
from typing import *

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.client.namecache import NameCache
from hippolyzer.lib.proxy.viewer_settings import iter_viewer_cache_dirs

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow


class ProxyNameCache(NameCache):
    def create_subscriptions(
            self,
            message_handler: MessageHandler[Message, str],
            http_message_handler: Optional[MessageHandler[HippoHTTPFlow, str]] = None,
    ):
        super().create_subscriptions(message_handler)
        if http_message_handler is not None:
            http_message_handler.subscribe("GetDisplayNames", self._handle_get_display_names)

    def load_viewer_caches(self):
        for cache_dir in iter_viewer_cache_dirs():
            try:
                namecache_file = cache_dir / "avatar_name_cache.xml"
                if namecache_file.exists():
                    with open(namecache_file, "rb") as f:
                        namecache_bytes = f.read()
                    agents = llsd.parse_xml(namecache_bytes)["agents"]
                    # Can be `None` if the file was just created
                    if not agents:
                        continue
                    for agent_id, agent_data in agents.items():
                        # Don't set display name if they just have the default
                        display_name = None
                        if not agent_data["is_display_name_default"]:
                            display_name = agent_data["display_name"]
                        self.update(UUID(agent_id), {
                            "FirstName": agent_data["legacy_first_name"],
                            "LastName": agent_data["legacy_last_name"],
                            "DisplayName": display_name,
                        })
            except:
                logging.exception(f"Failed to load namecache from {cache_dir}")

    def _handle_get_display_names(self, flow: HippoHTTPFlow):
        if flow.response.status_code != 200:
            return
        self._process_display_names_response(llsd.parse_xml(flow.response.content))
