"""
Body horror local animation mutator

Demonstrates programmatic modification / generation of animations

It will make you look absurd, obscene.
"""
import copy

import mitmproxy.http

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.llanim import Animation
from hippolyzer.lib.proxy.addon_utils import AssetAliasTracker, BaseAddon, GlobalProperty
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager
from hippolyzer.lib.base.vfs import STATIC_VFS


JOINT_REPLS = {
    "Left": "Right",
    "Right": "Left",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}


def _change_joint_name(joint_name: str):
    for orig, repl in JOINT_REPLS.items():
        if orig in joint_name:
            return joint_name.replace(orig, repl)
    return joint_name


def _mutate_anim_bytes(anim_bytes: bytes):
    anim = Animation.from_bytes(anim_bytes)
    new_joints = {}
    for name, joint in anim.joints.items():
        new_joints[_change_joint_name(name)] = joint
    anim.joints = new_joints
    for constraint in anim.constraints:
        constraint.source_volume = _change_joint_name(constraint.source_volume)
        constraint.target_volume = _change_joint_name(constraint.target_volume)
    return anim.to_bytes()


class HorrorAnimatorAddon(BaseAddon):
    horror_anim_tracker: AssetAliasTracker = GlobalProperty(AssetAliasTracker)

    def handle_init(self, session_manager: SessionManager):
        # We've reloaded, so make sure assets get new aliases
        self.horror_anim_tracker.invalidate_aliases()

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        tracker = self.horror_anim_tracker

        if message.name == "AvatarAnimation":
            # Only do this for the current user
            if message["Sender"]["ID"] != session.agent_id:
                return
            # Replace inbound anim IDs with alias IDs so we can force a cache
            # miss and replace the contents
            for block in message["AnimationList"][:]:
                anim_id = block["AnimID"]
                # Many of the anims in the static VFS have special meanings and the viewer
                # does different things based on the presence or absence of their IDs
                # in the motion list. Make sure those motions come through as usual, but
                # also add an alias so we can override the motions with an edited
                # version of the motion.
                if block["AnimID"] in STATIC_VFS:
                    new_block = copy.deepcopy(block)
                    new_block["AnimID"] = tracker.get_alias_uuid(anim_id)
                    message["AnimationList"].append(new_block)
                else:
                    block["AnimID"] = tracker.get_alias_uuid(anim_id)
        elif message.name == "AgentAnimation":
            # Make sure to remove any alias IDs from our outbound anim requests
            for block in message["AnimationList"]:
                orig_id = tracker.get_orig_uuid(block["AnimID"])
                if orig_id:
                    block["AnimID"] = orig_id

    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        if not flow.cap_data.asset_server_cap:
            return

        anim_id = flow.request.query.get("animatn_id")
        if not anim_id:
            return

        orig_anim_id = self.horror_anim_tracker.get_orig_uuid(UUID(anim_id))
        if not orig_anim_id:
            return

        flow.request.query["animatn_id"] = str(orig_anim_id)

        flow.can_stream = False
        flow.metadata["horror_anim"] = True

        if orig_anim_id in STATIC_VFS:
            # These animations are only in the static VFS and won't be served
            # by the asset server. Read the anim out of the static VFS and
            # send the response back immediately
            block = STATIC_VFS[orig_anim_id]
            anim_data = STATIC_VFS.read_block(block)
            flow.response = mitmproxy.http.Response.make(
                200,
                _mutate_anim_bytes(anim_data),
                {
                    "Content-Type": "binary/octet-stream",
                    "Connection": "close",
                }
            )
            return True

        # Partial requests for an anim wouldn't make any sense
        flow.request.headers.pop("Range", None)

    def handle_http_response(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        if not flow.metadata.get("horror_anim"):
            return

        if flow.response.status_code not in (200, 206):
            return

        flow.response.content = _mutate_anim_bytes(flow.response.content)
        # Not a range anymore, update the headers and status.
        flow.response.headers.pop("Content-Range", None)
        flow.response.status_code = 200

        return True


addons = [HorrorAnimatorAddon()]
