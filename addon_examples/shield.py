"""Block potentially bad things"""
from hippolyzer.lib.base.templates import IMDialogType, XferFilePath
from hippolyzer.lib.proxy.addon_utils import BaseAddon, show_message
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session

SUSPICIOUS_PACKETS = {
    "TransferRequest",
    "UUIDNameRequest",
    "UUIDGroupNameRequest",
    "OpenCircuit",
    "AddCircuitCode",
}
REGULAR_IM_DIALOGS = (IMDialogType.TYPING_STOP, IMDialogType.TYPING_STOP, IMDialogType.NOTHING_SPECIAL)


class ShieldAddon(BaseAddon):
    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
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
        if message.name == "RequestXfer":
            xfer_block = message["XferID"][0]
            # Don't allow Xfers for files, only assets
            if xfer_block["FilePath"] != XferFilePath.NONE or xfer_block["Filename"]:
                show_message(f"Blocked suspicious {message.name} packet")
                region.circuit.drop_message(message)
                return True


addons = [ShieldAddon()]
