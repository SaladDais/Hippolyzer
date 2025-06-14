"""
You don't need RLV, we have RLV at home.

RLV at home:
"""

from typing import *

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.templates import ChatType
from hippolyzer.lib.proxy.addon_utils import BaseAddon, send_chat
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


def send_rlv_chat(channel: int, message: str):
    # We always shout.
    send_chat(channel=channel, message=message, chat_type=ChatType.NORMAL)


class RLVAtHomeAddon(BaseAddon):
    """
    Addon for pretending to be an RLV-enabled viewer

    Useful if you want only a specific subset of RLV and don't want everything RLV normally allows,
    or want to override some RLV builtins.
    """
    def handle_rlv_command(self, session: Session, region: ProxiedRegion, source: UUID,
                           behaviour: str, options: List[str], param: str) -> bool | None:
        # print(behaviour, options, param)
        if behaviour == "clear":
            return True
        elif behaviour in ("versionnum", "versionnew", "version"):
            # People tend to just check that this returned anything at all. Just say we're 2.0.0 for all of these.
            send_rlv_chat(int(param), "2.0.0")
            return True
        elif behaviour == "getinv":
            # Pretend we don't have anything
            send_rlv_chat(int(param), "")
            return True
        elif behaviour == "sit":
            # Sure, we can sit on stuff, whatever.
            region.circuit.send(Message(
                'AgentRequestSit',
                Block('AgentData', AgentID=session.agent_id, SessionID=session.id),
                Block('TargetObject', TargetID=UUID(options[0]), Offset=(0, 0, 0)),
            ))
            return True
        return None


addons = [RLVAtHomeAddon()]
