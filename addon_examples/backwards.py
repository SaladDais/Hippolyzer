"""
All buttons make you go backwards.

Except for backward, which makes you go left.
"""

from hippolyzer.lib.base.templates import AgentControlFlags
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


NUDGE_MASK = sum(x for x in AgentControlFlags if "NUDGE" in x.name)
FAST_MASK = sum(x for x in AgentControlFlags if "FAST" in x.name)
DIR_MASK = sum(x for x in AgentControlFlags if
               any(x.name.endswith(y) for y in ("_POS", "_NEG")))
BACK_MASK = (AgentControlFlags.AT_NEG | AgentControlFlags.NUDGE_AT_NEG)


class BackwardsAddon(BaseAddon):
    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if message.name == "AgentUpdate":
            agent_data_block = message["AgentData"][0]
            flags: AgentControlFlags = agent_data_block.deserialize_var("ControlFlags")
            # Don't want these at all.
            flags &= ~(AgentControlFlags.TURN_LEFT | AgentControlFlags.TURN_RIGHT)

            any_nudge = bool(flags & NUDGE_MASK)
            any_fast = bool(flags & FAST_MASK)
            dir_vals = flags & DIR_MASK

            going_back = bool(flags & BACK_MASK)
            other_dir_vals = dir_vals & ~BACK_MASK

            new_flags = AgentControlFlags(0)
            # back -> left
            if going_back:
                if any_nudge:
                    new_flags |= AgentControlFlags.NUDGE_LEFT_POS
                else:
                    new_flags |= AgentControlFlags.LEFT_POS
                    if any_fast:
                        new_flags |= AgentControlFlags.FAST_LEFT
            # anything else -> back
            if other_dir_vals:
                if any_nudge:
                    new_flags |= AgentControlFlags.NUDGE_AT_NEG
                else:
                    new_flags |= AgentControlFlags.AT_NEG
                    if any_fast:
                        new_flags |= AgentControlFlags.FAST_AT
            agent_data_block["ControlFlags"] = new_flags


addons = [BackwardsAddon()]
