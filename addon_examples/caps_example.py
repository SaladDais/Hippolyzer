"""
Example of how to make simple Caps requests
"""
import aiohttp

from hippolyzer.lib.proxy.addon_utils import BaseAddon, show_message
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class CapsExampleAddon(BaseAddon):
    @handle_command()
    async def test_caps(self, _session: Session, region: ProxiedRegion):
        caps_client = region.caps_client
        # We can pass in a ClientSession if we want to do keep-alive across requests
        async with aiohttp.ClientSession() as aio_sess:
            async with caps_client.get("SimulatorFeatures", session=aio_sess) as resp:
                await resp.read_llsd()
        # Or we can have one created for us just for this request
        async with caps_client.get("SimulatorFeatures") as resp:
            show_message(await resp.read_llsd())

        # POSTing LLSD works
        req = caps_client.post("AgentPreferences", llsd={
            "hover_height": 0.5,
        })
        # Request object can be built, then awaited
        async with req as resp:
            show_message(await resp.read_llsd())


addons = [CapsExampleAddon()]
