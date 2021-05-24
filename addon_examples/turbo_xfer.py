"""
Speed up outbound Xfer requests (usually for object inventory listings)
by 20x at the cost of potentially missing dropped packets.

Useful for builders working on objects with very large inventories.

Xfers have their own, terrible reliability system that probably pre-dates
LLUDP reliability. Each packet has to be ACKed before the far end will send
the next packet. Each packet can be around 1200 bytes and will fit 1.5
inventory items worth of data.

Let's say your sim ping is 100 ms. Because each packet needs to be ACKed
before the next will be sent, it'll take around `num_items * 100 / 1.5`
milliseconds before you receive the full inventory list of an object.
That means for an object with 300 items, it'll take about 20 seconds
for you to download the full inventory, and those downloads are triggered
every time the inventory is changed.

By faking ACKs for packets we haven't received yet, we can trick the server
into sending us packets much faster than it would otherwise. The only problem
is that if an inbound SendXferPacket gets lost after we faked an ACK for it,
we have no way to re-request it. The Xfer will just fail. But it's faster so
who cares.
"""

import asyncio

from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.templates import XferPacket
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.packets import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session
from hippolyzer.lib.proxy.xfer_manager import Xfer


ACK_AHEAD_PACKETS = 20


class TurboXferAddon(BaseAddon):
    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: ProxiedMessage):
        if message.direction != Direction.OUT:
            return
        if message.name != "RequestXfer":
            return

        self._schedule_task(self._accelerate_xfer(session, region, message["XferID"]["ID"]))

    async def _accelerate_xfer(self, _session: Session, region: ProxiedRegion, xfer_id: int):
        message_handler = region.message_handler
        with message_handler.subscribe_async(
                ("SendXferPacket",),
                predicate=Xfer(xfer_id=xfer_id).is_our_message,
                take=False,
        ) as get_msg:
            next_ackable = 0
            while msg := await asyncio.wait_for(get_msg(), 0.5):
                # We're sending our own confirms, drop ones from the viewer
                if msg.name == "SendXferPacket":
                    packet_id: XferPacket = msg["XferID"][0].deserialize_var("Packet")
                    ack_to = packet_id.PacketID + ACK_AHEAD_PACKETS
                    for i in range(next_ackable, ack_to):
                        region.circuit.send_message(ProxiedMessage(
                            "ConfirmXferPacket",
                            Block("XferID", ID=xfer_id, Packet=i),
                            direction=Direction.OUT,
                        ))
                    next_ackable = ack_to
                    if packet_id.IsEOF:
                        return


addons = [TurboXferAddon()]
