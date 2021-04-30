"""
Helper for making deformer anims. This could have a GUI I guess.
"""
import dataclasses
from typing import *

from hippolyzer.lib.base.datatypes import Vector3, Quaternion, UUID
from hippolyzer.lib.base.llanim import Joint, Animation, PosKeyframe, RotKeyframe
from hippolyzer.lib.proxy.addon_utils import show_message, BaseAddon, SessionProperty
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.commands import handle_command, Parameter
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session

import local_anim
# We require any addons from local_anim to be loaded, and we want
# our addon to be reloaded whenever local_anim changes.
AddonManager.hot_reload(local_anim, require_addons_loaded=True)


@dataclasses.dataclass
class DeformerJoint:
    pos: Optional[Vector3] = None
    rot: Optional[Quaternion] = None


def build_deformer(joints: Dict[str, DeformerJoint]) -> bytes:
    anim = Animation(
        major_version=1,
        minor_version=0,
        base_priority=5,
        duration=1.0,
        loop_out_point=1.0,
        loop=True,
    )

    for joint_name, joint in joints.items():
        if not any((joint.pos, joint.rot)):
            continue
        anim.joints[joint_name] = Joint(
            priority=5,
            rot_keyframes=[RotKeyframe(time=0.0, rot=joint.rot)] if joint.rot else [],
            pos_keyframes=[PosKeyframe(time=0.0, pos=joint.pos)] if joint.pos else [],
        )
    return anim.to_bytes()


class DeformerAddon(BaseAddon):
    deform_joints: Dict[str, DeformerJoint] = SessionProperty(dict)

    @handle_command()
    async def save_deformer(self, _session: Session, _region: ProxiedRegion):
        filename = await AddonManager.UI.save_file(filter_str="SL Anim (*.anim)")
        if not filename:
            return
        with open(filename, "wb") as f:
            f.write(build_deformer(self.deform_joints))

    # `sep=None` makes `coord` greedy, taking the rest of the message
    @handle_command(
        joint_name=str,
        coord_type=str,
        coord=Parameter(Vector3.parse, sep=None),
    )
    async def set_deformer_joint(self, session: Session, region: ProxiedRegion,
                                 joint_name: str, coord_type: str, coord: Vector3):
        """
        Set a coordinate for a joint in the deformer

        Example:
            set_deformer_joint mNeck pos <0, 0, 0.5>
            set_deformer_joint mNeck rot <0, 180, 0>
        """
        joint_data = self.deform_joints.setdefault(joint_name, DeformerJoint())

        if coord_type == "pos":
            joint_data.pos = coord
        elif coord_type == "rot":
            joint_data.rot = Quaternion.from_euler(*coord, degrees=True)
        else:
            show_message(f"Unknown deformer component {coord_type}")
            return
        self._reapply_deformer(session, region)

    @handle_command()
    async def stop_deforming(self, session: Session, region: ProxiedRegion):
        """Disable any active deformer, may have to reset skeleton manually"""
        self.deform_joints.clear()
        self._reapply_deformer(session, region)

    def _reapply_deformer(self, session: Session, region: ProxiedRegion):
        anim_data = None
        if self.deform_joints:
            anim_data = build_deformer(self.deform_joints)
        local_anim.LocalAnimAddon.apply_local_anim(session, region, "deformer_addon", anim_data)

    def handle_rlv_command(self, session: Session, region: ProxiedRegion, source: UUID,
                           cmd: str, options: List[str], param: str):
        # An object in-world can also tell the client how to deform itself via
        # RLV-style commands.

        # We only handle commands
        if param != "force":
            return

        if cmd == "stop_deforming":
            self.deform_joints.clear()
        elif cmd == "deform_joints":
            self.deform_joints.clear()
            for joint_data in options:
                joint_split = joint_data.split("|")
                pos = Vector3(*joint_split[1].split("/")) if joint_split[1] else None
                rot = Quaternion(*joint_split[2].split("/")) if joint_split[2] else None
                self.deform_joints[joint_split[0]] = DeformerJoint(pos=pos, rot=rot)
        else:
            return

        self._reapply_deformer(session, region)
        return True


addons = [DeformerAddon()]
