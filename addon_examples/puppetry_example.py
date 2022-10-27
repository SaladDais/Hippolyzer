"""
Control a puppetry-enabled viewer and make your neck spin like crazy

It currently requires a custom rebased Firestorm with puppetry applied on top,
and patches applied on top to make startup LEAP scripts be treated as puppetry modules.
Basically, you probably don't want to use this yet. But hey, Puppetry is still only
on the beta grid anyway.
"""
import asyncio
import enum
import logging
import math
from typing import *

import outleap

from hippolyzer.lib.base.datatypes import Quaternion
from hippolyzer.lib.proxy.addon_utils import BaseAddon, SessionProperty
from hippolyzer.lib.proxy.sessions import Session

LOG = logging.getLogger(__name__)


class BodyPartMask(enum.IntFlag):
    """Which joints to send the viewer as part of "move" puppetry command"""
    HEAD = 1 << 0
    FACE = 1 << 1
    LHAND = 1 << 2
    RHAND = 1 << 3
    FINGERS = 1 << 4


def register_puppetry_command(func: Callable[[dict], Awaitable[None]]):
    """Register a method as handling inbound puppetry commands from the viewer"""
    func._puppetry_command = True
    return func


class PuppetryExampleAddon(BaseAddon):
    server_skeleton: Dict[str, Dict[str, Any]] = SessionProperty(dict)
    camera_num: int = SessionProperty(0)
    parts_active: BodyPartMask = SessionProperty(lambda: BodyPartMask(0x1F))
    puppetry_api: Optional[outleap.LLPuppetryAPI] = SessionProperty(None)
    leap_client: Optional[outleap.LEAPClient] = SessionProperty(None)

    def handle_session_init(self, session: Session):
        if not session.leap_client:
            return
        self.puppetry_api = outleap.LLPuppetryAPI(session.leap_client)
        self.leap_client = session.leap_client
        self._schedule_task(self._serve())
        self._schedule_task(self._exorcist(session))

    @register_puppetry_command
    async def enable_parts(self, args: dict):
        if (new_mask := args.get("parts_mask")) is not None:
            self.parts_active = BodyPartMask(new_mask)

    @register_puppetry_command
    async def set_camera(self, args: dict):
        if (camera_num := args.get("camera_num")) is not None:
            self.camera_num = camera_num

    @register_puppetry_command
    async def stop(self, _args: dict):
        LOG.info("Viewer asked us to stop puppetry")

    @register_puppetry_command
    async def log(self, _args: dict):
        # Intentionally ignored, we don't care about things the viewer
        # asked us to log
        pass

    @register_puppetry_command
    async def set_skeleton(self, args: dict):
        # Don't really care about what the viewer thinks the view of the skeleton is.
        # Just log store it.
        self.server_skeleton = args

    async def _serve(self):
        """Handle inbound puppetry commands from viewer in a loop"""
        async with self.leap_client.listen_scoped("puppetry.controller") as listener:
            while True:
                msg = await listener.get()
                cmd = msg["command"]
                handler = getattr(self, cmd, None)
                if handler is None or not hasattr(handler, "_puppetry_command"):
                    LOG.warning(f"Unknown puppetry command {cmd!r}: {msg!r}")
                    continue
                await handler(msg.get("args", {}))

    async def _exorcist(self, session):
        """Do the Linda Blair thing with your neck"""
        spin_rad = 0.0
        while True:
            await asyncio.sleep(0.05)
            if not session.main_region:
                continue
            # Wrap spin_rad around if necessary
            while spin_rad > math.pi:
                spin_rad -= math.pi * 2

            # LEAP wants rot as a quaternion with just the imaginary parts.
            neck_rot = Quaternion.from_euler(0, 0, spin_rad).data(3)
            self.puppetry_api.move({
                "mNeck": {"no_constraint": True, "local_rot": neck_rot},
            })
            spin_rad += math.pi / 25


addons = [PuppetryExampleAddon()]
