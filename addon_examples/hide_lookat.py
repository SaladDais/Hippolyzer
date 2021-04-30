"""
Drop outgoing packets that might leak what you're looking at, similar to Firestorm
"""

from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.packets import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session
from hippolyzer.lib.proxy.templates import ViewerEffectType


BLOCKED_EFFECTS = (
    ViewerEffectType.EFFECT_LOOKAT,
    ViewerEffectType.EFFECT_BEAM,
    ViewerEffectType.EFFECT_POINTAT,
    ViewerEffectType.EFFECT_EDIT,
)


def handle_lludp_message(_session: Session, region: ProxiedRegion, msg: ProxiedMessage):
    if msg.name == "ViewerEffect" and msg.direction == Direction.OUT:
        new_blocks = [b for b in msg["Effect"] if b["Type"] not in BLOCKED_EFFECTS]
        if new_blocks:
            msg["Effect"] = new_blocks
        else:
            # drop `ViewerEffect` entirely if left with no blocks
            region.circuit.drop_message(msg)
            # Short-circuit any other addons processing this message
            return True
