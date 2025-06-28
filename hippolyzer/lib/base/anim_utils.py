"""
Assorted utilities to make creating animations from scratch easier
"""

import copy
from typing import List, Union, Mapping

from hippolyzer.lib.base.datatypes import Vector3, Quaternion
from hippolyzer.lib.base.llanim import PosKeyframe, RotKeyframe, JOINTS_DICT, Joint
from hippolyzer.lib.base.mesh_skeleton import AVATAR_SKELETON
from hippolyzer.lib.base.multidict import OrderedMultiDict


def smooth_step(t: float):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def rot_interp(r0: Quaternion, r1: Quaternion, t: float):
    """
    Bad quaternion interpolation

    TODO: This is definitely not correct yet seems to work ok? Implement slerp.
    """
    # Ignore W
    r0 = r0.data(3)
    r1 = r1.data(3)
    return Quaternion(*map(lambda pair: ((pair[0] * (1.0 - t)) + (pair[1] * t)), zip(r0, r1)))


def unique_frames(frames: List[Union[PosKeyframe, RotKeyframe]]):
    """Drop frames where time and coordinate are exact duplicates of another frame"""
    new_frames = []
    for frame in frames:
        # TODO: fudge factor for float comparison instead
        if frame not in new_frames:
            new_frames.append(frame)
    return new_frames


def shift_keyframes(frames: List[Union[PosKeyframe, RotKeyframe]], num: int):
    """
    Shift keyframes around by `num` frames

    Assumes keyframes occur at a set cadence, and that first and last keyframe are at the same coord.
    """

    # Get rid of duplicate frames
    frames = unique_frames(frames)
    pop_idx = -1
    insert_idx = 0
    if num < 0:
        insert_idx = len(frames) - 1
        pop_idx = 0
        num = -num
    old_times = [f.time for f in frames]
    new_frames = frames.copy()
    # Drop last, duped frame. We'll copy the first frame to replace it later
    new_frames.pop(-1)
    for _ in range(num):
        new_frames.insert(insert_idx, new_frames.pop(pop_idx))

    # Put first frame back on the end
    new_frames.append(copy.copy(new_frames[0]))

    assert len(old_times) == len(new_frames)
    assert new_frames[0] == new_frames[-1]
    # Make the times of the shifted keyframes match up with the previous timeline
    for old_time, new_frame in zip(old_times, new_frames):
        new_frame.time = old_time
    return new_frames


def smooth_pos(start: Vector3, end: Vector3, inter_frames: int, time: float, duration: float) -> List[PosKeyframe]:
    """Generate keyframes to smoothly interpolate between two positions"""
    frames = [PosKeyframe(time=time, pos=start)]
    for i in range(0, inter_frames):
        t = (i + 1) / (inter_frames + 1)
        smooth_t = smooth_step(t)
        pos = Vector3(smooth_t, smooth_t, smooth_t).interpolate(start, end)
        frames.append(PosKeyframe(time=time + (t * duration), pos=pos))
    return frames + [PosKeyframe(time=time + duration, pos=end)]


def smooth_rot(start: Quaternion, end: Quaternion, inter_frames: int, time: float, duration: float)\
        -> List[RotKeyframe]:
    """Generate keyframes to smoothly interpolate between two rotations"""
    frames = [RotKeyframe(time=time, rot=start)]
    for i in range(0, inter_frames):
        t = (i + 1) / (inter_frames + 1)
        smooth_t = smooth_step(t)
        frames.append(RotKeyframe(time=time + (t * duration), rot=rot_interp(start, end, smooth_t)))
    return frames + [RotKeyframe(time=time + duration, rot=end)]


def mirror_joints(joints_dict: Mapping[str, Joint]) -> JOINTS_DICT:
    """Mirror a joints dict so left / right are swapped, including transformations"""
    new_joints: JOINTS_DICT = OrderedMultiDict()

    for joint_name, joint in joints_dict.items():
        inverse_joint_node = AVATAR_SKELETON[joint_name].inverse
        if not inverse_joint_node:
            new_joints[joint_name] = joint
            continue

        # Okay, this is one we have to actually mirror
        new_joint = Joint(joint.priority, [], [])

        for rot_keyframe in joint.rot_keyframes:
            new_joint.rot_keyframes.append(RotKeyframe(
                time=rot_keyframe.time,
                # Just need to mirror on yaw and roll
                rot=Quaternion.from_euler(*(rot_keyframe.rot.to_euler() * Vector3(-1, 1, -1)))
            ))

        for pos_keyframe in joint.pos_keyframes:
            new_joint.pos_keyframes.append(PosKeyframe(
                time=pos_keyframe.time,
                # Y is left / right so just negate it.
                pos=pos_keyframe.pos * Vector3(1, -1, 1)
            ))

        new_joints[inverse_joint_node.name] = new_joint

    return new_joints
