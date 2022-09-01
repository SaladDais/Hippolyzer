import dataclasses
import weakref
from typing import *

import transformations
from lxml import etree

from hippolyzer.lib.base.datatypes import Vector3, RAD_TO_DEG
from hippolyzer.lib.base.helpers import get_resource_filename


MAYBE_JOINT_REF = Optional[Callable[[], "JointNode"]]


@dataclasses.dataclass(unsafe_hash=True)
class JointNode:
    name: str
    parent: MAYBE_JOINT_REF
    translation: Vector3
    pivot: Vector3  # pivot point for the joint, generally the same as translation
    rotation: Vector3  # Euler rotation in degrees
    scale: Vector3
    type: str  # bone or collision_volume

    @property
    def matrix(self):
        return transformations.compose_matrix(
            scale=tuple(self.scale),
            angles=tuple(self.rotation / RAD_TO_DEG),
            translate=tuple(self.translation),
        )


@dataclasses.dataclass
class Skeleton:
    joint_dict: Dict[str, JointNode]

    def __getitem__(self, item: str) -> JointNode:
        return self.joint_dict[item]

    @classmethod
    def _parse_node_children(cls, joint_dict: Dict[str, JointNode], node: etree.ElementBase, parent: MAYBE_JOINT_REF):
        name = node.get('name')
        joint = JointNode(
            name=name,
            parent=parent,
            translation=_get_vec_attr(node, "pos", Vector3()),
            pivot=_get_vec_attr(node, "pivot", Vector3()),
            rotation=_get_vec_attr(node, "rot", Vector3()),
            scale=_get_vec_attr(node, "scale", Vector3(1, 1, 1)),
            type=node.tag,
        )
        joint_dict[name] = joint
        for child in node.iterchildren():
            cls._parse_node_children(joint_dict, child, weakref.ref(joint))

    @classmethod
    def from_xml(cls, node: etree.ElementBase):
        joint_dict = {}
        cls._parse_node_children(joint_dict, node, None)
        return cls(joint_dict)

    def get_required_joints(self, joint_names: Collection[str]) -> Set[str]:
        """Get all joints required to have a chain from all joints up to the root joint"""
        required = set(joint_names)
        for joint_name in joint_names:
            joint_node = self.joint_dict.get(joint_name)
            while joint_node:
                required.add(joint_node.name)
                if not joint_node.parent:
                    break
                joint_node = joint_node.parent()
        return required


def load_avatar_skeleton() -> Skeleton:
    skel_path = get_resource_filename("lib/base/data/avatar_skeleton.xml")
    with open(skel_path, 'r') as f:
        skel_root = etree.fromstring(f.read())
    return Skeleton.from_xml(skel_root.getchildren()[0])


def _get_vec_attr(node, attr_name, default) -> Vector3:
    attr_val = node.get(attr_name, None)
    if not attr_val:
        return default
    return Vector3(*(float(x) for x in attr_val.split(" ") if x))


AVATAR_SKELETON = load_avatar_skeleton()
