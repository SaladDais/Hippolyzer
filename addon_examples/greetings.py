from hippolyzer.lib.base.datatypes import Vector3
from hippolyzer.lib.proxy.addon_utils import send_chat, BaseAddon, show_message
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class GreetingAddon(BaseAddon):
    @handle_command()
    async def greetings(self, session: Session, region: ProxiedRegion):
        """Greet everyone around you"""
        agent_obj = region.objects.lookup_fullid(session.agent_id)
        if not agent_obj:
            show_message("Don't have an agent object?")

        # Note that this will only have avatars closeish to your camera. The sim sends
        # KillObjects for avatars that get too far away.
        other_agents = [o for o in region.objects.all_avatars if o.FullID != agent_obj.FullID]

        if not other_agents:
            show_message("No other agents?")

        for other_agent in other_agents:
            dist = Vector3.dist(agent_obj.Position, other_agent.Position)
            if dist >= 19.0:
                continue
            nv = other_agent.NameValue.to_dict()
            send_chat(f"Greetings, {nv['FirstName']} {nv['LastName']}!")


addons = [GreetingAddon()]
