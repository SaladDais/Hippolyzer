"""
ObjectUpdate blame tracker, to figure out what objects are spamming updates

Assumes that you've received a full ObjectUpdate for everything (meaning the proxy
object tracker knows about it) and that you have received an ObjectProperties for
everything you want the name of. You can force a full ObjectUpdate for everything
by relogging with an empty object cache. Doing the "precache_objects" command
before you start tracking can help too.
"""
from typing import *

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.base.templates import PCode
from hippolyzer.lib.proxy.addon_utils import BaseAddon, show_message, SessionProperty
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class ObjectUpdateBlameAddon(BaseAddon):
    update_blame_counter: Counter[UUID] = SessionProperty(Counter)
    should_track_update_blame: bool = SessionProperty(False)

    @handle_command()
    async def precache_objects(self, _session: Session, region: ProxiedRegion):
        """
        Make the proxy's object tracker request any missing objects

        Should be done before tracking update blame to make sure the proxy
        knows about any objects that are cached in the client but not by the proxy
        """
        region.objects.request_missing_objects()

    @handle_command()
    async def object_cache_miss_stats(self, _session: Session, region: ProxiedRegion):
        show_message(len(region.objects.missing_locals))

    @handle_command()
    async def track_update_blame(self, _session: Session, _region: ProxiedRegion):
        self.should_track_update_blame = True

    @handle_command()
    async def untrack_update_blame(self, _session: Session, _region: ProxiedRegion):
        self.should_track_update_blame = False

    @handle_command()
    async def clear_update_blame(self, _session: Session, _region: ProxiedRegion):
        self.update_blame_counter.clear()

    @handle_command()
    async def dump_update_blame(self, _session: Session, region: ProxiedRegion):
        print("ObjectUpdate blame:")
        for obj_id, count in self.update_blame_counter.most_common(50):
            obj = region.objects.lookup_fullid(obj_id)
            name = obj.Name if obj and obj.Name else "<Unknown>"
            print(f"{obj_id} ({name!r}): {count}")

    def handle_object_updated(self, session: Session, region: ProxiedRegion,
                              obj: Object, updated_props: Set[str], msg: Optional[Message]):
        if not self.should_track_update_blame:
            return
        if region != session.main_region:
            return
        # Log this as related to the parent object unless the parent is an avatar
        if obj.Parent and obj.Parent.PCode != PCode.AVATAR:
            obj = obj.Parent

        if obj.PCode != PCode.PRIMITIVE:
            return

        self.update_blame_counter[obj.FullID] += 1
        # Ask the region for the object name if we don't know it
        if obj.Name is None:
            region.objects.request_object_properties(obj)


addons = [ObjectUpdateBlameAddon()]
