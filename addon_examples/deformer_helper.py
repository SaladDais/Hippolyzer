"""
Helper for making deformer anims. This could have a GUI I guess.
"""
import dataclasses
from typing import *

import numpy as np
import transformations

from hippolyzer.lib.base.datatypes import Vector3, Quaternion, UUID
from hippolyzer.lib.base.llanim import Joint, Animation, PosKeyframe, RotKeyframe
from hippolyzer.lib.base.mesh import MeshAsset, SegmentHeaderDict, SkinSegmentDict, LLMeshSerializer
from hippolyzer.lib.base.serialization import BufferWriter
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


def build_mesh_deformer(joints: Dict[str, DeformerJoint]) -> bytes:
    skin_seg = SkinSegmentDict(
        joint_names=[],
        bind_shape_matrix=identity_mat4(),
        inverse_bind_matrix=[],
        alt_inverse_bind_matrix=[],
        pelvis_offset=0.0,
        lock_scale_if_joint_position=False
    )
    for joint_name, joint in joints.items():
        # We can only represent joint translations, ignore this joint if it doesn't have any.
        if not joint.pos:
            continue
        skin_seg['joint_names'].append(joint_name)
        # Inverse bind matrix isn't actually used, so we can just give it a placeholder value of the
        # identity mat4. This might break things in weird ways because the matrix isn't actually sensible.
        skin_seg['inverse_bind_matrix'].append(identity_mat4())
        # Create a flattened mat4 that only has a translation component of our joint pos
        # The viewer ignores any other component of these matrices so no point putting shear
        # or perspective or whatever :)
        joint_mat4 = pos_to_mat4(joint.pos)
        # Ask the viewer to override this joint's usual parent-relative position with our matrix
        skin_seg['alt_inverse_bind_matrix'].append(joint_mat4)

    # Make a dummy mesh and shove our skin segment onto it. None of the tris are rigged, so the
    # viewer will freak out and refuse to display the tri, only the joint translations will be used.
    # Supposedly a mesh with a `skin` segment but no weights on the material should just result in an
    # effectively unrigged material, but that's not the case. Oh well.
    mesh = MeshAsset.make_triangle()
    mesh.header['skin'] = SegmentHeaderDict(offset=0, size=0)
    mesh.segments['skin'] = skin_seg

    writer = BufferWriter("!")
    writer.write(LLMeshSerializer(), mesh)
    return writer.copy_buffer()


def identity_mat4() -> List[float]:
    """
    Return an "Identity" mat4

    Effectively represents a transform of no rot, no translation, no shear, no perspective
    and scaling by 1.0 on every axis.
    """
    return list(np.identity(4).flatten('F'))


def pos_to_mat4(pos: Vector3) -> List[float]:
    """Convert a position Vector3 to a Translation Mat4"""
    return list(transformations.compose_matrix(translate=tuple(pos)).flatten('F'))


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
                           behaviour: str, options: List[str], param: str):
        # An object in-world can also tell the client how to deform itself via
        # RLV-style commands.

        # We only handle commands
        if param != "force":
            return

        if behaviour == "stop_deforming":
            self.deform_joints.clear()
        elif behaviour == "deform_joints":
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

    @handle_command()
    async def save_deformer_as_mesh(self, _session: Session, _region: ProxiedRegion):
        """
        Export the deformer as a crafted rigged mesh rather than an animation

        Mesh deformers have the advantage that they don't cause your joints to "stick"
        like animations do when using animations with pos keyframes.
        """
        filename = await AddonManager.UI.save_file(filter_str="LL Mesh (*.llmesh)")
        if not filename:
            return
        with open(filename, "wb") as f:
            f.write(build_mesh_deformer(self.deform_joints))

    @handle_command()
    async def upload_deformer_as_mesh(self, _session: Session, region: ProxiedRegion):
        """Same as save_deformer_as_mesh, but uploads the mesh directly to SL."""

        mesh_bytes = build_mesh_deformer(self.deform_joints)
        try:
            # Send off mesh to calculate upload cost
            upload_token = await region.asset_uploader.initiate_mesh_upload("deformer", mesh_bytes)
        except Exception as e:
            show_message(e)
            raise

        if not await AddonManager.UI.confirm("Upload", f"Spend {upload_token.linden_cost}L on upload?"):
            return

        # Do the actual upload
        try:
            await region.asset_uploader.complete_upload(upload_token)
        except Exception as e:
            show_message(e)
            raise


addons = [DeformerAddon()]
