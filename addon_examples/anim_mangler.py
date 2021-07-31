"""
Example anim mangler addon, to be used with local anim addon.

You can edit this live to apply various transforms to local anims,
as well as any uploaded anims. Any changes will be reflected in currently
playing local anims.

This example modifies any position keys of an animation's mHipRight joint.
"""
from hippolyzer.lib.base.llanim import Animation
from hippolyzer.lib.proxy.addons import AddonManager

import local_anim
AddonManager.hot_reload(local_anim, require_addons_loaded=True)


def offset_right_hip(anim: Animation):
    hip_joint = anim.joints.get("mHipRight")
    if hip_joint:
        for pos_frame in hip_joint.pos_keyframes:
            pos_frame.pos.Z *= 2.5
            pos_frame.pos.X *= 5.0
    return anim


class ExampleAnimManglerAddon(local_anim.BaseAnimManglerAddon):
    ANIM_MANGLERS = [
        offset_right_hip,
    ]


addons = [ExampleAnimManglerAddon()]
