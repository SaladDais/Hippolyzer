"""
Example of how to control a viewer over LEAP

Must launch the viewer with `outleap-agent` LEAP script.
See https://github.com/SaladDais/outleap/ for more info on LEAP / outleap.
"""

import outleap
from outleap.scripts.inspector import LEAPInspectorGUI

from hippolyzer.lib.proxy.addon_utils import send_chat, BaseAddon, show_message
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager


# Path found using `outleap-inspector`
FPS_PATH = outleap.UIPath("/main_view/menu_stack/status_bar_container/status/time_and_media_bg/FPSText")


class LEAPExampleAddon(BaseAddon):
    async def handle_leap_client_added(self, session_manager: SessionManager, leap_client: outleap.LEAPClient):
        # You can do things as soon as the LEAP client connects, like if you want to automate
        # login or whatever.
        viewer_control_api = outleap.LLViewerControlAPI(leap_client)
        # Ask for a config value and print it in the viewer logs
        print(await viewer_control_api.get("Global", "StatsPilotFile"))

    @handle_command()
    async def show_ui_inspector(self, session: Session, _region: ProxiedRegion):
        """Spawn a GUI for inspecting the UI state"""
        if not session.leap_client:
            show_message("No LEAP client connected?")
            return
        LEAPInspectorGUI(session.leap_client).show()

    @handle_command()
    async def say_fps(self, session: Session, _region: ProxiedRegion):
        """Say your current FPS in chat"""
        if not session.leap_client:
            show_message("No LEAP client connected?")
            return

        window_api = outleap.LLWindowAPI(session.leap_client)
        fps = (await window_api.get_info(path=FPS_PATH))['value']

        send_chat(f"LEAP says I'm running at {fps} FPS!")


addons = [LEAPExampleAddon()]
