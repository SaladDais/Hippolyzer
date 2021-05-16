from hippolyzer.lib.base.datatypes import Vector3
from hippolyzer.lib.proxy.addon_utils import send_chat, BaseAddon, show_message
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class GreetingAddon(BaseAddon):
    @handle_command()
    async def greetings(self, session: Session, region: ProxiedRegion):
        """Greet everyone around you"""
        our_avatar = region.objects.lookup_avatar(session.agent_id)
        if not our_avatar:
            show_message("Don't have an agent object?")

        other_avatars = [o for o in region.objects.all_avatars if o.FullID != our_avatar.FullID]

        if not other_avatars:
            show_message("No other avatars?")

        for other_avatar in other_avatars:
            dist = Vector3.dist(our_avatar.RegionPosition, other_avatar.RegionPosition)
            if dist >= 19.0:
                continue
            if other_avatar.Name is None:
                continue
            send_chat(f"Greetings, {other_avatar.Name}!")


addons = [GreetingAddon()]
