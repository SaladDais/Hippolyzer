import random

from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class SimulatePacketLossAddon(BaseAddon):
    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        # Messing with these may kill your circuit
        if message.name in {"PacketAck", "StartPingCheck", "CompletePingCheck", "UseCircuitCode",
                            "CompleteAgentMovement", "AgentMovementComplete"}:
            return
        # Simulate 30% packet loss
        if random.random() > 0.7:
            # Do nothing, drop this packet on the floor
            return True
        return


addons = [SimulatePacketLossAddon()]
