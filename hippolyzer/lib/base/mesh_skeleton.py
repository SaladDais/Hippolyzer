from __future__ import annotations

import copy
import dataclasses
import re
import weakref
from typing import *

import transformations
from lxml import etree

from hippolyzer.lib.base.datatypes import Vector3, RAD_TO_DEG
from hippolyzer.lib.base.helpers import get_resource_filename
from hippolyzer.lib.base.mesh import MeshAsset, SkinSegmentDict, llsd_to_mat4

MAYBE_JOINT_REF = Optional[str]
SKELETON_REF = Optional[Callable[[], "Skeleton"]]


@dataclasses.dataclass
class JointNode:
    name: str
    parent_name: MAYBE_JOINT_REF
    skeleton: SKELETON_REF
    translation: Vector3
    pivot: Vector3  # pivot point for the joint, generally the same as translation
    rotation: Vector3  # Euler rotation in degrees
    scale: Vector3
    type: str  # bone or collision_volume
    support: str

    def __hash__(self):
        return hash((self.name, self.type))

    @property
    def matrix(self):
        return transformations.compose_matrix(
            scale=tuple(self.scale),
            angles=tuple(self.rotation / RAD_TO_DEG),
            translate=tuple(self.translation),
        )

    @property
    def parent(self) -> Optional[JointNode]:
        if self.parent_name:
            return self.skeleton()[self.parent_name]
        return None

    @property
    def index(self) -> int:
        bone_idx = 0
        for node in self.skeleton().joint_dict.values():
            if node.type != "bone":
                continue
            if self is node:
                return bone_idx
            bone_idx += 1
        raise KeyError(f"{self.name!r} doesn't exist in skeleton")

    @property
    def ancestors(self) -> Sequence[JointNode]:
        joint_node = self
        skeleton = self.skeleton()
        ancestors: List[JointNode] = []
        while joint_node.parent_name:
            joint_node = skeleton.joint_dict.get(joint_node.parent_name)
            ancestors.append(joint_node)
        return ancestors

    @property
    def children(self) -> Sequence[JointNode]:
        children: List[JointNode] = []
        for node in self.skeleton().joint_dict.values():
            if node.parent_name and node.parent_name == self.name:
                children.append(node)
        return children

    @property
    def inverse(self) -> Optional[JointNode]:
        l_re = re.compile(r"(.*?(?:_|\b))L((?:_|\b).*)")
        r_re = re.compile(r"(.*?(?:_|\b))R((?:_|\b).*)")

        inverse_name = None
        if "Left" in self.name:
            inverse_name = self.name.replace("Left", "Right")
        elif "LEFT" in self.name:
            inverse_name = self.name.replace("LEFT", "RIGHT")
        elif l_re.match(self.name):
            inverse_name = re.sub(l_re, r"\1R\2", self.name)
        elif "Right" in self.name:
            inverse_name = self.name.replace("Right", "Left")
        elif "RIGHT" in self.name:
            inverse_name = self.name.replace("RIGHT", "LEFT")
        elif r_re.match(self.name):
            inverse_name = re.sub(r_re, r"\1L\2", self.name)

        if inverse_name:
            return self.skeleton().joint_dict.get(inverse_name)
        return None

    @property
    def descendents(self) -> Set[JointNode]:
        descendents: Set[JointNode] = set()
        ancestors: Set[str] = {self.name}
        last_ancestors: Set[str] = set()
        while last_ancestors != ancestors:
            last_ancestors = ancestors.copy()
            for node in self.skeleton().joint_dict.values():
                if node.parent_name and node.parent_name in ancestors:
                    ancestors.add(node.name)
                    descendents.add(node)
        return descendents


class Skeleton:
    def __init__(self, root_node: Optional[etree.ElementBase] = None):
        self.joint_dict: Dict[str, JointNode] = {}
        if root_node is not None:
            self._parse_node_children(root_node, None)

    def __getitem__(self, item: str) -> JointNode:
        return self.joint_dict[item]

    def clone(self) -> Self:
        val = copy.deepcopy(self)
        skel_ref = weakref.ref(val)
        for joint in val.joint_dict.values():
            joint.skeleton = skel_ref
        return val

    def _parse_node_children(self, node: etree.ElementBase, parent_name: MAYBE_JOINT_REF):
        name = node.get('name')
        joint = JointNode(
            name=name,
            parent_name=parent_name,
            skeleton=weakref.ref(self),
            translation=_get_vec_attr(node, "pos", Vector3()),
            pivot=_get_vec_attr(node, "pivot", Vector3()),
            rotation=_get_vec_attr(node, "rot", Vector3()),
            scale=_get_vec_attr(node, "scale", Vector3(1, 1, 1)),
            support=node.get('support', 'base'),
            type=node.tag,
        )
        self.joint_dict[name] = joint
        for child in node.iterchildren():
            self._parse_node_children(child, joint.name)

    def merge_mesh_skeleton(self, mesh: MeshAsset) -> None:
        """Update this skeleton with a skeleton definition from a mesh asset"""
        skin_seg: Optional[SkinSegmentDict] = mesh.segments.get('skin')
        if not skin_seg:
            return

        for joint_name, matrix in zip(skin_seg['joint_names'], skin_seg.get('alt_inverse_bind_matrix', [])):
            # We're only meant to use the translation component from the alt inverse bind matrix.
            joint_decomp = transformations.decompose_matrix(llsd_to_mat4(matrix))
            joint_node = self.joint_dict.get(joint_name)
            if not joint_node:
                continue
            joint_node.translation = Vector3(*joint_decomp[3])

        if pelvis_offset := skin_seg.get('pelvis_offset'):
            # TODO: Should we even do this?
            pelvis_node = self["mPelvis"]
            pelvis_node.translation += Vector3(0, 0, pelvis_offset)


def _get_vec_attr(node, attr_name: str, default: Vector3) -> Vector3:
    attr_val = node.get(attr_name, None)
    if not attr_val:
        return default
    return Vector3(*(float(x) for x in attr_val.split(" ") if x))


def load_avatar_skeleton() -> Skeleton:
    skel_path = get_resource_filename("lib/base/data/avatar_skeleton.xml")
    with open(skel_path, 'r') as f:
        skel_root = etree.fromstring(f.read())
    return Skeleton(skel_root.getchildren()[0])


AVATAR_SKELETON = load_avatar_skeleton()
