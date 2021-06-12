import dataclasses
from typing import *

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.message.message_handler import MessageHandler


@dataclasses.dataclass
class NameCacheEntry:
    full_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None

    def __str__(self):
        if self.display_name:
            return f"{self.display_name} ({self.legacy_name})"
        if self.legacy_name:
            return self.legacy_name
        return f"(???) ({self.full_id})"

    @property
    def legacy_name(self) -> Optional[str]:
        if self.first_name is None:
            return None
        return f"{self.first_name} {self.last_name}"

    @property
    def preferred_name(self) -> Optional[str]:
        if self.display_name:
            return self.display_name
        return self.legacy_name


class NameCache:
    def __init__(self):
        self._cache: Dict[UUID, NameCacheEntry] = {}

    def create_subscriptions(
            self,
            message_handler: MessageHandler[Message, str],
    ):
        message_handler.subscribe("UUIDNameReply", self._handle_uuid_name_reply)

    def lookup(self, uuid: UUID, create_if_none: bool = False) -> Optional[NameCacheEntry]:
        val = self._cache.get(uuid)
        if create_if_none and val is None:
            val = NameCacheEntry(full_id=uuid)
            self._cache[uuid] = val
        return val

    def update(self, full_id: UUID, vals: dict):
        # upsert the cache entry
        entry = self._cache.get(full_id) or NameCacheEntry(full_id=full_id)
        if "FirstName" in vals:
            entry.first_name = vals["FirstName"]
        if "LastName" in vals:
            entry.last_name = vals["LastName"]
        if "DisplayName" in vals:
            entry.display_name = vals["DisplayName"] if vals["DisplayName"] else None
        self._cache[full_id] = entry

    def _handle_uuid_name_reply(self, msg: Message):
        for block in msg.blocks["UUIDNameBlock"]:
            self.update(block["ID"], {
                "FirstName": block["FirstName"],
                "LastName": block["LastName"],
            })

    def _process_display_names_response(self, parsed: dict):
        """Handle the response from the GetDisplayNames cap"""
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
