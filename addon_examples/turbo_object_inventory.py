"""
Speed up outbound object inventory listing requests
by 20x at the cost of potentially failing to request some due to
dropped packets.

Useful for builders working on objects with very large inventories that
change very often.

Object Inventory transfers use the Xfer system. Xfers have their own,
terrible reliability system that probably pre-dates LLUDP reliability.
Each packet has to be ACKed before the far end will send the next packet.
Each packet can be around 1200 bytes and will fit 1.5 inventory items worth of data.

Let's say your sim ping is 100 ms. Because each packet needs to be ACKed
before the next will be sent, it'll take around `num_items * 100 / 1.5`
milliseconds before you receive the full inventory list of an object.
That means for an object with 300 items, it'll take about 20 seconds
for you to download the full inventory, and those downloads are triggered
every time the inventory is changed.

By faking ACKs for packets we haven't received yet, we can trick the server
into sending us packets much faster than it would otherwise. The only problem
is that if an inbound SendXferPacket gets lost after we faked an ACK for it,
we have no way to re-request it. The Xfer will just fail. The viewer will also
drop any out-of-order xfer packets, so packet re-ordering is a problem.

To deal with that, the proxy attempts its own Xfers using all the chunks
from the previous attempts before sending a final, reconstructed Xfer
to the viewer.
"""

import asyncio
from typing import *

from hippolyzer.lib.base.templates import XferFilePath
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session
from hippolyzer.lib.base.xfer_manager import Xfer


class TurboObjectInventoryAddon(BaseAddon):
    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if message.direction != Direction.OUT:
            return
        if message.name != "RequestTaskInventory":
            return

        self._schedule_task(self._proxy_task_inventory_request(region, message.take()))
        return True

    async def _proxy_task_inventory_request(
            self,
            region: ProxiedRegion,
            request_msg: Message
    ):
        # Keep around a dict of chunks we saw previously in case we have to restart
        # an Xfer due to missing chunks. We don't expect chunks to change across Xfers
        # so this can be used to recover from dropped SendXferPackets in subsequent attempts
        existing_chunks: Dict[int, bytes] = {}
        for i in range(3):
            # Any previous requests will have triggered a delete of the inventory file
            # by marking it complete on the server-side. Re-send our RequestTaskInventory
            # To make sure there's a fresh copy.
            region.circuit.send(request_msg.take())
            inv_message = await region.message_handler.wait_for(('ReplyTaskInventory',), timeout=5.0)
            # No task inventory, send the reply as-is
            file_name = inv_message["InventoryData"]["Filename"]
            if not file_name:
                region.circuit.send(inv_message)
                return

            xfer = region.xfer_manager.request(
                file_name=file_name,
                file_path=XferFilePath.CACHE,
                turbo=True,
            )
            xfer.chunks.update(existing_chunks)
            try:
                await xfer
            except asyncio.TimeoutError:
                # We likely failed the request due to missing chunks, store
                # the chunks that we _did_ get for the next attempt.
                existing_chunks.update(xfer.chunks)
                continue

            # Send the original ReplyTaskInventory to the viewer so it knows the file is ready
            region.circuit.send(inv_message)
            proxied_xfer = Xfer(data=xfer.reassemble_chunks())

            # Wait for the viewer to request the inventory file
            await region.xfer_manager.serve_inbound_xfer_request(
                xfer=proxied_xfer,
                request_predicate=lambda x: x["XferID"]["Filename"] == file_name,
                # indra's XferManager throttles confirms, so even local transfers will be
                # slow if we wait for confirmation.
                wait_for_confirm=False,
            )
            return
        raise asyncio.TimeoutError("Failed to get inventory after 3 tries")


addons = [TurboObjectInventoryAddon()]
