"""
Local animations

/524 load_local_anim
 assuming you loaded something.anim
/524 start_local_anim something
/524 stop_local_anim something

If you want to trigger the animation from an object to simulate llStartAnimation():
llOwnerSay("@start_local_anim:something=force");
"""

import asyncio
import os
import pathlib
from typing import *

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.addon_utils import BaseAddon, SessionProperty
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.http_asset_repo import HTTPAssetRepo
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


def _get_mtime(path: str):
    try:
        return os.stat(path).st_mtime
    except:
        return None


class LocalAnimAddon(BaseAddon):
    # name -> path, only for anims actually from files
    local_anim_paths: Dict[str, str] = SessionProperty(dict)
    # name -> mtime or None. Only for anims from files.
    local_anim_mtimes: Dict[str, Optional[float]] = SessionProperty(dict)
    # name -> current asset ID (changes each play)
    local_anim_playing_ids: Dict[str, UUID] = SessionProperty(dict)

    def handle_session_init(self, session: Session):
        self._schedule_task(self._try_reload_anims(session))

    @handle_command()
    async def load_local_anim(self, _session: Session, _region: ProxiedRegion):
        """Load a local animation file into the list of local anims"""
        filename = await AddonManager.UI.open_file(filter_str="SL Anim (*.anim)")
        if filename:
            p = pathlib.Path(filename)
            self.local_anim_paths[p.stem] = filename

    @handle_command(anim_name=str)
    async def start_local_anim(self, session: Session, region: ProxiedRegion, anim_name):
        """
        Start a named local animation

        Assuming you loaded an animation named something.anim:
            start_local_anim something
        """
        self.apply_local_anim_from_file(session, region, anim_name)

    @handle_command(anim_name=str)
    async def stop_local_anim(self, session: Session, region: ProxiedRegion, anim_name):
        """Stop a named local animation"""
        self.apply_local_anim(session, region, anim_name, new_data=None)

    async def _try_reload_anims(self, session: Session):
        while True:
            region = session.main_region
            if not region:
                await asyncio.sleep(2.0)
                continue

            # Loop over local anims we loaded
            for anim_name, anim_id in self.local_anim_paths.items():
                anim_id = self.local_anim_playing_ids.get(anim_name)
                if not anim_id:
                    continue
                # is playing right now, check if there's a newer version
                self.apply_local_anim_from_file(session, region, anim_name, only_if_changed=True)
            await asyncio.sleep(2.0)

    def handle_rlv_command(self, session: Session, region: ProxiedRegion, source: UUID,
                           cmd: str, options: List[str], param: str):
        # We only handle commands
        if param != "force":
            return

        if cmd == "stop_local_anim":
            self.apply_local_anim(session, region, options[0], new_data=None)
            return True
        elif cmd == "start_local_anim":
            self.apply_local_anim_from_file(session, region, options[0])
            return True

    @classmethod
    def apply_local_anim(cls, session: Session, region: ProxiedRegion,
                         anim_name: str, new_data: Optional[bytes] = None):
        asset_repo: HTTPAssetRepo = session.session_manager.asset_repo
        next_id: Optional[UUID] = None
        new_msg = ProxiedMessage(
            "AgentAnimation",
            Block(
                "AgentData",
                AgentID=session.agent_id,
                SessionID=session.id,
            ),
        )

        # Stop any old version of the anim that might be playing first
        cur_id = cls.local_anim_playing_ids.get(anim_name)
        if cur_id:
            new_msg.add_block(Block(
                "AnimationList",
                AnimID=cur_id,
                StartAnim=False,
            ))

        if new_data is not None:
            # Create a temp asset ID for the new version and send out a start request
            next_id = asset_repo.create_asset(new_data, one_shot=True)
            new_msg.add_block(Block(
                "AnimationList",
                AnimID=next_id,
                StartAnim=True,
            ))
            cls.local_anim_playing_ids[anim_name] = next_id
        else:
            # No data means just stop the anim
            cls.local_anim_playing_ids.pop(anim_name, None)

        region.circuit.send_message(new_msg)
        print(f"Changing {anim_name} to {next_id}")

    @classmethod
    def apply_local_anim_from_file(cls, session: Session, region: ProxiedRegion,
                                   anim_name: str, only_if_changed=False):
        anim_path = cls.local_anim_paths.get(anim_name)
        anim_data = None
        if anim_path:
            old_mtime = cls.local_anim_mtimes.get(anim_name)
            mtime = _get_mtime(anim_path)
            if only_if_changed and old_mtime == mtime:
                return

            cls.local_anim_mtimes[anim_name] = mtime
            # file might not even exist anymore if mtime is `None`,
            # anim will automatically stop if that happens.
            if mtime:
                if only_if_changed:
                    print(f"Re-applying {anim_name}")
                else:
                    print(f"Playing {anim_name}")

                with open(anim_path, "rb") as f:
                    anim_data = f.read()
        else:
            print(f"Unknown anim {anim_name!r}")
        cls.apply_local_anim(session, region, anim_name, new_data=anim_data)


addons = [LocalAnimAddon()]
