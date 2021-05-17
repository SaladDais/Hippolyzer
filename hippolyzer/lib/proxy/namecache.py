from __future__ import annotations

import dataclasses
from typing import *

from hippolyzer.lib.base.datatypes import UUID

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.message import ProxiedMessage


@dataclasses.dataclass
class NameCacheEntry:
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    DisplayName: Optional[str] = None


class NameCache:
    # TODO: persist this somewhere across runs
    def __init__(self):
        self._cache: Dict[UUID, NameCacheEntry] = {}

    def lookup(self, uuid: UUID) -> Optional[NameCacheEntry]:
        return self._cache.get(uuid)

    def update(self, uuid: UUID, vals: dict):
        # upsert the cache entry
        entry = self._cache.get(uuid) or NameCacheEntry()
        entry.LastName = vals.get("LastName") or entry.LastName
        entry.FirstName = vals.get("FirstName") or entry.FirstName
        entry.DisplayName = vals.get("DisplayName") or entry.DisplayName
        self._cache[uuid] = entry

    def handle_uuid_name_reply(self, msg: ProxiedMessage):
        """UUID lookup reply handler to be registered by regions"""
        for block in msg.blocks["UUIDNameBlock"]:
            self.update(block["ID"], {
                "FirstName": block["FirstName"],
                "LastName": block["LastName"],
            })
