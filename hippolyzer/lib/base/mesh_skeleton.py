from __future__ import annotations

import dataclasses
import weakref
from typing import *

import transformations
from lxml import etree

from hippolyzer.lib.base.datatypes import Vector3, RAD_TO_DEG
from hippolyzer.lib.base.helpers import get_resource_filename


MAYBE_JOINT_REF = Optional[Callable[[], "JointNode"]]
SKELETON_REF = Optional[Callable[[], "Skeleton"]]


@dataclasses.dataclass
class JointNode:
    name: str
    parent: MAYBE_JOINT_REF
    skeleton: SKELETON_REF
    translation: Vector3
    pivot: Vector3  # pivot point for the joint, generally the same as translation
    rotation: Vector3  # Euler rotation in degrees
    scale: Vector3
    type: str  # bone or collision_volume

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
        ancestors = []
        while joint_node.parent:
            joint_node = joint_node.parent()
            ancestors.append(joint_node)
        return ancestors

    @property
    def children(self) -> Sequence[JointNode]:
        children = []
        for node in self.skeleton().joint_dict.values():
            if node.parent and node.parent() == self:
                children.append(node)
        return children

    @property
    def descendents(self) -> Set[JointNode]:
        descendents = set()
        ancestors = {self}
        last_ancestors = set()
        while last_ancestors != ancestors:
            last_ancestors = ancestors
            for node in self.skeleton().joint_dict.values():
                if node.parent and node.parent() in ancestors:
                    ancestors.add(node)
                    descendents.add(node)
        return descendents


class Skeleton:
    def __init__(self, root_node: etree.ElementBase):
        self.joint_dict: Dict[str, JointNode] = {}
        self._parse_node_children(root_node, None)

    def __getitem__(self, item: str) -> JointNode:
        return self.joint_dict[item]

    def _parse_node_children(self, node: etree.ElementBase, parent: MAYBE_JOINT_REF):
        name = node.get('name')
        joint = JointNode(
            name=name,
            parent=parent,
            skeleton=weakref.ref(self),
            translation=_get_vec_attr(node, "pos", Vector3()),
            pivot=_get_vec_attr(node, "pivot", Vector3()),
            rotation=_get_vec_attr(node, "rot", Vector3()),
            scale=_get_vec_attr(node, "scale", Vector3(1, 1, 1)),
            type=node.tag,
        )
        self.joint_dict[name] = joint
        for child in node.iterchildren():
            self._parse_node_children(child, weakref.ref(joint))


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
