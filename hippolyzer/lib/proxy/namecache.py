from __future__ import annotations

import dataclasses
import logging
from typing import *

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.proxy.viewer_settings import iter_viewer_cache_dirs

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
    from hippolyzer.lib.proxy.message import ProxiedMessage


@dataclasses.dataclass
class NameCacheEntry:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None

    def __str__(self):
        if self.display_name:
            return f"{self.display_name} ({self.legacy_name})"
        return self.legacy_name

    @property
    def legacy_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def preferred_name(self):
        if self.display_name:
            return self.display_name
        return self.legacy_name


class NameCache:
    def __init__(self):
        self._cache: Dict[UUID, NameCacheEntry] = {}

    def create_subscriptions(
            self,
            message_handler: MessageHandler[ProxiedMessage],
            http_message_handler: MessageHandler[HippoHTTPFlow],
    ):
        message_handler.subscribe("UUIDNameReply", self._handle_uuid_name_reply)
        http_message_handler.subscribe("GetDisplayNames", self._handle_get_display_names)

    def load_viewer_caches(self):
        for cache_dir in iter_viewer_cache_dirs():
            try:
                namecache_file = cache_dir / "avatar_name_cache.xml"
                if namecache_file.exists():
                    with open(namecache_file, "rb") as f:
                        namecache_bytes = f.read()
                    agents = llsd.parse_xml(namecache_bytes)["agents"]
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

    def lookup(self, uuid: UUID) -> Optional[NameCacheEntry]:
        return self._cache.get(uuid)

    def update(self, uuid: UUID, vals: dict):
        # upsert the cache entry
        entry = self._cache.get(uuid) or NameCacheEntry()
        if "FirstName" in vals:
            entry.first_name = vals["FirstName"]
        if "LastName" in vals:
            entry.last_name = vals["LastName"]
        if "DisplayName" in vals:
            entry.display_name = vals["DisplayName"] if vals["DisplayName"] else None
        self._cache[uuid] = entry

    def _handle_uuid_name_reply(self, msg: ProxiedMessage):
        for block in msg.blocks["UUIDNameBlock"]:
            self.update(block["ID"], {
                "FirstName": block["FirstName"],
                "LastName": block["LastName"],
            })

    def _handle_get_display_names(self, flow: HippoHTTPFlow):
        if flow.response.status_code != 200:
            return
        parsed = llsd.parse_xml(flow.response.content)
        for agent in parsed["agents"]:
            # Don't set display name if they just have the default
            display_name = None
            if not agent["is_display_name_default"]:
                display_name = agent["display_name"]
            self.update(agent["id"], {
                "FirstName": agent["legacy_first_name"],
                "LastName": agent["legacy_last_name"],
                "DisplayName": display_name,
            })
