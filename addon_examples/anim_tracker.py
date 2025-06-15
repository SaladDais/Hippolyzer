"""
Debugger for detecting when animations within an object get started or stopped

Useful for tracking down animation sequence-related bugs within your LSL scripts,
or debugging automatic animation stopping behavior in the viewer.

If an animation unexpectedly stops and nobody requested it be stopped, it's a potential viewer bug (or priority issue).
If an animation unexpectedly stops and the viewer requested it be stopped, it's also a potential viewer bug.
If an animation unexpectedly stops and only the server requested it be stopped, it's a potential script / server bug.
"""

from typing import *

from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.base.templates import AssetType
from hippolyzer.lib.proxy.addon_utils import BaseAddon, SessionProperty
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.addon_utils import show_message


class AnimTrackerAddon(BaseAddon):
    should_track_anims: bool = SessionProperty(False)
    anims_lookup: Dict[UUID, str] = SessionProperty(dict)
    last_tracker_anims: Set[UUID] = SessionProperty(set)

    def _format_anim_diffs(self, started_anims: Set[UUID], stopped_anims: Set[UUID]):
        added_strs = [f"+{self.anims_lookup[x]!r}" for x in started_anims]
        removed_strs = [f"-{self.anims_lookup[x]!r}" for x in stopped_anims]

        return ", ".join(removed_strs + added_strs)

    @handle_command()
    async def track_anims(self, session: Session, region: ProxiedRegion):
        """Track when animations within this object get started or stopped"""
        if self.should_track_anims:
            self.last_tracker_anims.clear()
            self.anims_lookup.clear()

        selected = region.objects.lookup_localid(session.selected.object_local)
        if not selected:
            return

        self.should_track_anims = True

        object_items = await region.objects.request_object_inv(selected)

        anims: Dict[UUID, str] = {}
        for item in object_items:
            if item.type != AssetType.ANIMATION:
                continue
            anims[item.true_asset_id] = item.name

        self.anims_lookup = anims

    @handle_command()
    async def stop_tracking_anims(self, _session: Session, _region: ProxiedRegion):
        """Stop reporting differences"""
        if self.should_track_anims:
            self.should_track_anims = False
            self.last_tracker_anims.clear()
            self.anims_lookup.clear()

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if not self.should_track_anims:
            return

        if message.name != "AgentAnimation" or message.direction != Direction.OUT:
            # AgentAnimation is the message the viewer uses to request manually starting or stopping animations.
            # We don't care about other messages, we're just interested in distinguishing cases where the viewer
            # specifically requested something vs something being done by the server on its own.
            return
        av = region.objects.lookup_avatar(session.agent_id)
        if not av or not av.Object:
            print("Somehow didn't know about our own av object?")
            return

        current_anims = set([x for x in av.Object.Animations if x in self.anims_lookup])
        started_anims: Set[UUID] = set()
        stopped_anims: Set[UUID] = set()

        for block in message["AnimationList"]:
            anim_id = block["AnimID"]
            if anim_id not in self.anims_lookup:
                continue

            start_anim = block["StartAnim"]
            already_started = anim_id in current_anims
            if start_anim == already_started:
                # No change
                continue

            if start_anim:
                started_anims.add(anim_id)
            else:
                stopped_anims.add(anim_id)

        if started_anims or stopped_anims:
            show_message("Viewer Requested Anims: " + self._format_anim_diffs(started_anims, stopped_anims))

    def handle_object_updated(self, session: Session, region: ProxiedRegion,
                              obj: Object, updated_props: Set[str], msg: Optional[Message]):
        if not self.should_track_anims:
            return
        if obj.FullID != session.agent_id:
            return
        if "Animations" not in updated_props:
            return

        current_anims = set([x for x in obj.Animations if x in self.anims_lookup])
        started_anims = current_anims - self.last_tracker_anims
        stopped_anims = self.last_tracker_anims - current_anims

        self.last_tracker_anims.clear()
        self.last_tracker_anims.update(current_anims)

        if started_anims or stopped_anims:
            show_message("Anim Diffs: " + self._format_anim_diffs(started_anims, stopped_anims))


addons = [AnimTrackerAddon()]
