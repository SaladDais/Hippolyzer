"""Block potentially bad things"""
from hippolyzer.lib.proxy.addon_utils import BaseAddon, show_message
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.packets import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session
from hippolyzer.lib.proxy.templates import IMDialogType

SUSPICIOUS_PACKETS = {"RequestXfer", "TransferRequest", "UUIDNameRequest",
                      "UUIDGroupNameRequest", "OpenCircuit"}
REGULAR_IM_DIALOGS = (IMDialogType.TYPING_STOP, IMDialogType.TYPING_STOP, IMDialogType.NOTHING_SPECIAL)


class ShieldAddon(BaseAddon):
    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: ProxiedMessage):
        if message.direction != Direction.IN:
            return
        if message.name in SUSPICIOUS_PACKETS:
            show_message(f"Blocked suspicious {message.name} packet")
            region.circuit.drop_message(message)
            return True
        if message.name == "ImprovedInstantMessage":
            msg_block = message["MessageBlock"][0]
            if msg_block["Dialog"] not in REGULAR_IM_DIALOGS:
                return
            from_agent = message["AgentData"]["AgentID"]
            if from_agent == session.agent_id:
                expected_id = from_agent
            else:
                expected_id = from_agent ^ session.agent_id
            msg_block["ID"] = expected_id


addons = [ShieldAddon()]
