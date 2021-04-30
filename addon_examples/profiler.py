"""
Debug performance issues in the proxy
/524 start_profiling
/524 stop_profiling
"""

import cProfile
from typing import *

from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager


class ProfilingAddon(BaseAddon):
    def __init__(self):
        # We don't want this to surive module reloads so it can be an
        # instance attribute rather than on session_manager.addon_ctx
        self.profile: Optional[cProfile.Profile] = None

    def handle_unload(self, session_manager: SessionManager):
        if self.profile is not None:
            self.profile.disable()
            self.profile = None

    @handle_command()
    async def start_profiling(self, _session: Session, _region: ProxiedRegion):
        """Start a cProfile session"""
        if self.profile is not None:
            self.profile.disable()
        self.profile = cProfile.Profile()
        self.profile.enable()
        print("Started profiling")

    @handle_command()
    async def stop_profiling(self, _session: Session, _region: ProxiedRegion):
        """Stop profiling and save to file"""
        if self.profile is None:
            return
        self.profile.disable()
        profile = self.profile
        self.profile = None

        print("Finished profiling")
        profile_path = await AddonManager.UI.save_file(caption="Save Profile")
        if profile_path:
            profile.dump_stats(profile_path)


addons = [ProfilingAddon()]
