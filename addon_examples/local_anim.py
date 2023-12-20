"""
Local animations

/524 load_local_anim
 assuming you loaded something.anim
/524 start_local_anim something
/524 stop_local_anim something
/524 save_local_anim something

If you want to trigger the animation from an object to simulate llStartAnimation():
llOwnerSay("@start_local_anim:something=force");

Also includes a concept of "anim manglers" similar to the "mesh manglers" of the
local mesh addon. This is useful if you want to test making procedural changes
to animations before uploading them. The manglers will be applied to any uploaded
animations as well.

May also be useful if you need to make ad-hoc changes to a bunch of animations on
bulk upload, like changing priority or removing a joint.
"""

import asyncio
import logging
import pathlib
from abc import abstractmethod
from typing import *

from hippolyzer.lib.base import serialization as se
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.helpers import get_mtime
from hippolyzer.lib.base.llanim import Animation
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.message.msgtypes import PacketFlags
from hippolyzer.lib.proxy import addon_ctx
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.addon_utils import BaseAddon, SessionProperty, GlobalProperty, show_message
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.http_asset_repo import HTTPAssetRepo
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager


class LocalAnimAddon(BaseAddon):
    # name -> path, only for anims actually from files
    local_anim_paths: Dict[str, str] = SessionProperty(dict)
    # name -> anim bytes
    local_anim_bytes: Dict[str, bytes] = SessionProperty(dict)
    # name -> mtime or None. Only for anims from files.
    local_anim_mtimes: Dict[str, Optional[float]] = SessionProperty(dict)
    # name -> current asset ID (changes each play)
    local_anim_playing_ids: Dict[str, UUID] = SessionProperty(dict)
    anim_manglers: List[Callable[[Animation], Animation]] = GlobalProperty(list)

    def handle_init(self, session_manager: SessionManager):
        self.remangle_local_anims(session_manager)

    def handle_session_init(self, session: Session):
        # Reload anims and reload any manglers if we have any
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

    @handle_command(anim_name=str)
    async def save_local_anim(self, _session: Session, _region: ProxiedRegion, anim_name: str):
        """Save a named local anim to disk"""
        anim_bytes = self.local_anim_bytes.get(anim_name)
        if not anim_bytes:
            return
        filename = await AddonManager.UI.save_file(filter_str="SL Anim (*.anim)", default_suffix="anim")
        if not filename:
            return
        with open(filename, "wb") as f:
            f.write(anim_bytes)

    async def _try_reload_anims(self, session: Session):
        while True:
            region = session.main_region
            if not region:
                await asyncio.sleep(1.0)
                continue

            # Loop over local anims we loaded
            for anim_name, anim_id in self.local_anim_paths.items():
                anim_id = self.local_anim_playing_ids.get(anim_name)
                if not anim_id:
                    continue
                # is playing right now, check if there's a newer version
                try:
                    self.apply_local_anim_from_file(session, region, anim_name, only_if_changed=True)
                except Exception:
                    logging.exception("Exploded while replaying animation")
            await asyncio.sleep(1.0)

    def handle_rlv_command(self, session: Session, region: ProxiedRegion, source: UUID,
                           behaviour: str, options: List[str], param: str):
        # We only handle commands
        if param != "force":
            return

        if behaviour == "stop_local_anim":
            self.apply_local_anim(session, region, options[0], new_data=None)
            return True
        elif behaviour == "start_local_anim":
            self.apply_local_anim_from_file(session, region, options[0])
            return True

    @classmethod
    def apply_local_anim(cls, session: Session, region: ProxiedRegion,
                         anim_name: str, new_data: Optional[bytes] = None):
        asset_repo: HTTPAssetRepo = session.session_manager.asset_repo
        next_id: Optional[UUID] = None
        new_msg = Message(
            "AgentAnimation",
            Block(
                "AgentData",
                AgentID=session.agent_id,
                SessionID=session.id,
            ),
            flags=PacketFlags.RELIABLE,
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
            cls.local_anim_bytes[anim_name] = new_data
        else:
            # No data means just stop the anim
            cls.local_anim_playing_ids.pop(anim_name, None)
            cls.local_anim_bytes.pop(anim_name, None)

        region.circuit.send(new_msg)
        print(f"Changing {anim_name} to {next_id}")

    @classmethod
    def apply_local_anim_from_file(cls, session: Session, region: ProxiedRegion,
                                   anim_name: str, only_if_changed=False):
        anim_path = cls.local_anim_paths.get(anim_name)
        anim_data = None
        if anim_path:
            old_mtime = cls.local_anim_mtimes.get(anim_name)
            mtime = get_mtime(anim_path)
            if only_if_changed and old_mtime == mtime:
                return

            # file might not even exist anymore if mtime is `None`,
            # anim will automatically stop if that happens.
            if mtime:
                if only_if_changed:
                    print(f"Re-applying {anim_name}")
                else:
                    print(f"Playing {anim_name}")

                with open(anim_path, "rb") as f:
                    anim_data = f.read()
                anim_data = cls._mangle_anim(anim_data)
            cls.local_anim_mtimes[anim_name] = mtime
        else:
            print(f"Unknown anim {anim_name!r}")
        cls.apply_local_anim(session, region, anim_name, new_data=anim_data)

    @classmethod
    def _mangle_anim(cls, anim_data: bytes) -> bytes:
        if not cls.anim_manglers:
            return anim_data
        reader = se.BufferReader("<", anim_data)
        spec = se.Dataclass(Animation)
        anim = reader.read(spec)
        for mangler in cls.anim_manglers:
            anim = mangler(anim)
        writer = se.BufferWriter("<")
        writer.write(spec, anim)
        return writer.copy_buffer()

    @classmethod
    def remangle_local_anims(cls, session_manager: SessionManager):
        # Anim manglers are global, so we need to re-mangle anims for all sessions
        for session in session_manager.sessions:
            # Push the context of this session onto the stack so we can access
            # session-scoped properties
            with addon_ctx.push(new_session=session, new_region=session.main_region):
                cls.local_anim_mtimes.clear()

    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        if flow.name == "NewFileAgentInventoryUploader":
            # Don't bother looking at this if we have no manglers
            if not self.anim_manglers:
                return
            # This is kind of a crappy match but these magic bytes shouldn't match anything that SL
            # allows as an upload type but animations.
            if not flow.request.content or not flow.request.content.startswith(b"\x01\x00\x00\x00"):
                return

            # Replace the uploaded anim with the mangled version
            flow.request.content = self._mangle_anim(flow.request.content)
            show_message("Mangled upload request")


class BaseAnimManglerAddon(BaseAddon):
    """Base class for addons that mangle uploaded or file-based local animations"""
    ANIM_MANGLERS: List[Callable[[Animation], Animation]]

    def handle_init(self, session_manager: SessionManager):
        # Add our manglers into the list
        LocalAnimAddon.anim_manglers.extend(self.ANIM_MANGLERS)
        LocalAnimAddon.remangle_local_anims(session_manager)

    def handle_unload(self, session_manager: SessionManager):
        # Clean up our manglers before we go away
        mangler_list = LocalAnimAddon.anim_manglers
        for mangler in self.ANIM_MANGLERS:
            if mangler in mangler_list:
                mangler_list.remove(mangler)
        LocalAnimAddon.remangle_local_anims(session_manager)


class BaseAnimHelperAddon(BaseAddon):
    """
    Base class for local creation of procedural animations

    Animation generated by build_anim() gets applied to all active sessions
    """
    ANIM_NAME: str

    def handle_session_init(self, session: Session):
        self._reapply_anim(session, session.main_region)

    def handle_session_closed(self, session: Session):
        LocalAnimAddon.apply_local_anim(session, session.main_region, self.ANIM_NAME, None)

    def handle_unload(self, session_manager: SessionManager):
        for session in session_manager.sessions:
            # TODO: Nasty. Since we need to access session-local attrs we need to set the
            #  context even though we also explicitly pass session and region.
            #  Need to rethink the LocalAnimAddon API.
            with addon_ctx.push(session, session.main_region):
                LocalAnimAddon.apply_local_anim(session, session.main_region, self.ANIM_NAME, None)

    @abstractmethod
    def build_anim(self) -> Animation:
        pass

    def _reapply_anim(self, session: Session, region: ProxiedRegion):
        LocalAnimAddon.apply_local_anim(session, region, self.ANIM_NAME, self.build_anim().to_bytes())


addons = [LocalAnimAddon()]
