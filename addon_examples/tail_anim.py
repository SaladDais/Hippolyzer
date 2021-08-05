"""
Tail animation generator

Demonstrates programmatic generation of local motions using BaseAnimHelperAddon

You can use this to create an animation with a script, fiddle with it until it
looks right, then finally save it with /524 save_local_anim <ANIM_NAME>.

The built animation is automatically applied to all active sessions when loaded,
and is re-generated whenever the script is edited. Unloading the script stops
the animations.
"""

from hippolyzer.lib.base.anim_utils import shift_keyframes, smooth_rot
from hippolyzer.lib.base.datatypes import Quaternion
from hippolyzer.lib.base.llanim import Animation, Joint
from hippolyzer.lib.proxy.addons import AddonManager

import local_anim
AddonManager.hot_reload(local_anim, require_addons_loaded=True)


class TailAnimator(local_anim.BaseAnimHelperAddon):
    # Should be unique
    ANIM_NAME = "tail_anim"

    def build_anim(self) -> Animation:
        anim = Animation(
            base_priority=5,
            duration=5.0,
            loop_out_point=5.0,
            loop=True,
        )
        # Iterate along tail joints 1 through 6
        for joint_num in range(1, 7):
            # Give further along joints a wider range of motion
            start_rot = Quaternion.from_euler(0.2, -0.3, 0.15 * joint_num)
            end_rot = Quaternion.from_euler(-0.2, -0.3, -0.15 * joint_num)
            rot_keyframes = [
                # Tween between start_rot and end_rot, using smooth interpolation.
                # SL's keyframes only allow linear interpolation which doesn't look great
                # for natural motions. `smooth_rot()` gets around that by generating
                # smooth inter frames for SL to linearly interpolate between.
                *smooth_rot(start_rot, end_rot, inter_frames=10, time=0.0, duration=2.5),
                *smooth_rot(end_rot, start_rot, inter_frames=10, time=2.5, duration=2.5),
            ]
            anim.joints[f"mTail{joint_num}"] = Joint(
                priority=5,
                # Each joint's frames should be ahead of the previous joint's by 2 frames
                rot_keyframes=shift_keyframes(rot_keyframes, joint_num * 2),
            )
        return anim


addons = [TailAnimator()]
