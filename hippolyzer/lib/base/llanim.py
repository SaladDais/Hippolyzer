from __future__ import annotations

import dataclasses
import enum
from typing import *

import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base.datatypes import Vector3, Quaternion
from hippolyzer.lib.base.multidict import OrderedMultiDict


# Forward declarations so the dataclasses can be declared in natural order
JOINT_DATACLASS = se.ForwardSerializable(lambda: se.Dataclass(Joint))
CONSTRAINT_DATACLASS = se.ForwardSerializable(lambda: se.Dataclass(Constraint))
POSKEYFRAME_DATACLASS = se.ForwardSerializable(lambda: se.Dataclass(PosKeyframe))
ROTKEYFRAME_DATACLASS = se.ForwardSerializable(lambda: se.Dataclass(RotKeyframe))


@dataclasses.dataclass
class Animation:
    major_version: int = se.dataclass_field(se.U16, default=1)
    minor_version: int = se.dataclass_field(se.U16, default=0)
    base_priority: int = se.dataclass_field(se.S32)
    duration: float = se.dataclass_field(se.F32)
    emote_name: str = se.dataclass_field(se.CStr())
    loop_in_point: float = se.dataclass_field(se.F32)
    loop_out_point: float = se.dataclass_field(se.F32)
    loop: int = se.dataclass_field(se.S32)
    ease_in_duration: float = se.dataclass_field(se.F32)
    ease_out_duration: float = se.dataclass_field(se.F32)
    hand_pose: HandPose = se.dataclass_field(lambda: se.IntEnum(HandPose, se.U32), default=0)
    joints: OrderedMultiDict[str, Joint] = se.dataclass_field(se.MultiDictAdapter(
        se.Collection(se.U32, se.Tuple(se.CStr(), JOINT_DATACLASS)),
    ))
    constraints: List[Constraint] = se.dataclass_field(
        se.Collection(se.S32, CONSTRAINT_DATACLASS),
    )

    def to_bytes(self):
        writer = se.BufferWriter("<")
        writer.write(se.Dataclass(type(self)), self)
        return writer.copy_buffer()

    @classmethod
    def from_bytes(cls, buff) -> "Animation":
        reader = se.BufferReader("<", buff)
        return reader.read(se.Dataclass(cls))


@dataclasses.dataclass
class Joint:
    priority: int = se.dataclass_field(se.S32)
    rot_keyframes: List[RotKeyframe] = se.dataclass_field(
        se.Collection(se.S32, ROTKEYFRAME_DATACLASS)
    )
    pos_keyframes: List[PosKeyframe] = se.dataclass_field(
        se.Collection(se.S32, POSKEYFRAME_DATACLASS),
    )


def _get_version_from_context(ctx: se.ParseContext) -> Tuple[int, int]:
    return ctx._root.major_version, ctx._root.minor_version


@dataclasses.dataclass
class RotKeyframe:
    time: float = se.dataclass_field(lambda: VERSIONED_TIME)
    rot: Quaternion = se.dataclass_field(se.ContextSwitch(
        _get_version_from_context,
        {
            (0, 1): se.PackedQuat(se.Vector3),
            (1, 0): se.PackedQuat(se.Vector3U16(-1.0, 1.0)),
        },
    ))


@dataclasses.dataclass
class PosKeyframe:
    time: float = se.dataclass_field(lambda: VERSIONED_TIME)
    pos: Vector3 = se.dataclass_field(se.ContextSwitch(
        _get_version_from_context,
        {
            (0, 1): se.Vector3,
            (1, 0): se.Vector3U16(-5.0, 5.0),
        },
    ))


class QuantizedTime(se.QuantizedFloatBase):
    def __init__(self, prim_spec: se.SerializablePrimitive):
        super().__init__(prim_spec, zero_median=False)

    def _get_upper_limit(self, ctx: se.ParseContext) -> float:
        # Upper limit is the "duration" from the parent animation
        return ctx._root.duration

    def encode(self, val: Any, ctx: Optional[se.ParseContext]) -> Any:
        return self._float_to_quantized(val, 0.0, self._get_upper_limit(ctx))

    def decode(self, val: Any, ctx: Optional[se.ParseContext], pod: bool = False) -> Any:
        return self._quantized_to_float(val, 0.0, self._get_upper_limit(ctx))


VERSIONED_TIME = se.ContextSwitch(
    _get_version_from_context,
    {
        (0, 1): se.F32,
        (1, 0): QuantizedTime(se.U16),
    },
)


class ConstraintType(enum.IntEnum):
    POINT = 0
    PLANE = 1


@dataclasses.dataclass
class Constraint:
    chain_length: int = se.dataclass_field(se.U8)
    type: ConstraintType = se.dataclass_field(se.IntEnum(ConstraintType, se.U8))
    source_volume: str = se.dataclass_field(se.StrFixed(16))
    source_offset: Vector3 = se.dataclass_field(se.Vector3)
    target_volume: str = se.dataclass_field(se.StrFixed(16))
    target_offset: Vector3 = se.dataclass_field(se.Vector3)
    target_dir: Vector3 = se.dataclass_field(se.Vector3())
    ease_in_start: float = se.dataclass_field(se.F32)
    ease_in_stop: float = se.dataclass_field(se.F32)
    ease_out_start: float = se.dataclass_field(se.F32)
    ease_out_stop: float = se.dataclass_field(se.F32)


class HandPose(enum.IntEnum):
    SPREAD = 0
    RELAXED = 1
    POINT = 2
    FIST = 3
    RELAXED_L = 4
    POINT_L = 5
    FIST_L = 6
    RELAXED_R = 7
    POINT_R = 8
    FIST_R = 9
    SALUTE_R = 10
    TYPING = 11
    PEACE_R = 12
    PALM_R = 13
