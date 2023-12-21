"""
Loading task inventory doesn't actually need to be slow.

By using a cap instead of the slow xfer path and sending the LLSD inventory
model we get 15x speedups even when mocking things behind the scenes by using
a hacked up version of xfer. See turbo_object_inventory.py
"""

import asyncio

import asgiref.wsgi
from typing import *

from flask import Flask, Response, request

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.inventory import InventoryModel, InventoryObject
from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.templates import XferFilePath, AssetType
from hippolyzer.lib.proxy import addon_ctx
from hippolyzer.lib.proxy.webapp_cap_addon import WebAppCapAddon

app = Flask("GetTaskInventoryCapApp")


@app.route('/', methods=["GET"])
async def get_task_inventory():
    # Should always have the current region, the cap handler is bound to one.
    # Just need to pull it from the `addon_ctx` module's global.
    region = addon_ctx.region.get()
    session = addon_ctx.session.get()
    obj_id = UUID(request.args["task_id"])
    obj = region.objects.lookup_fullid(obj_id)
    if not obj:
        return Response(f"Couldn't find {obj_id}", status=404, mimetype="text/plain")
    request_msg = Message(
        'RequestTaskInventory',
        Block('AgentData', AgentID=session.agent_id, SessionID=session.id),
        Block('InventoryData', LocalID=obj.LocalID),
    )
    # Keep around a dict of chunks we saw previously in case we have to restart
    # an Xfer due to missing chunks. We don't expect chunks to change across Xfers
    # so this can be used to recover from dropped SendXferPackets in subsequent attempts
    existing_chunks: Dict[int, bytes] = {}
    for _ in range(3):
        # Any previous requests will have triggered a delete of the inventory file
        # by marking it complete on the server-side. Re-send our RequestTaskInventory
        # To make sure there's a fresh copy.
        region.circuit.send(request_msg.take())
        inv_message = await region.message_handler.wait_for(
            ('ReplyTaskInventory',),
            predicate=lambda x: x["InventoryData"]["TaskID"] == obj.FullID,
            timeout=5.0,
        )
        # No task inventory, send the reply as-is
        file_name = inv_message["InventoryData"]["Filename"]
        if not file_name:
            # The "Contents" folder always has to be there, if we don't put it here
            # then the viewer will have to lie about it being there itself.
            return Response(
                llsd.format_xml({
                    "inventory": [
                        InventoryObject(
                            name="Contents",
                            parent_id=UUID.ZERO,
                            type=AssetType.CATEGORY,
                            obj_id=obj_id
                        ).to_llsd()
                    ],
                    "inv_serial": inv_message["InventoryData"]["Serial"],
                }),
                headers={"Content-Type": "application/llsd+xml"},
                status=200,
            )

        last_serial = request.args.get("last_serial", None)
        if last_serial:
            last_serial = int(last_serial)
        if inv_message["InventoryData"]["Serial"] == last_serial:
            # Nothing has changed since the version of the inventory they say they have, say so.
            return Response("", status=304)

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

        inv_model = InventoryModel.from_str(xfer.reassemble_chunks().decode("utf8"))

        return Response(
            llsd.format_xml({
                "inventory": inv_model.to_llsd(),
                "inv_serial": inv_message["InventoryData"]["Serial"],
            }),
            headers={"Content-Type": "application/llsd+xml"},
        )
    raise asyncio.TimeoutError("Failed to get inventory after 3 tries")


class GetTaskInventoryCapExampleAddon(WebAppCapAddon):
    # A cap URL with this name will be tied to each region when
    # the sim is first connected to. The URL will be returned to the
    # viewer in the Seed if the viewer requests it by name.
    CAP_NAME = "GetTaskInventoryExample"
    # Any asgi app should be fine.
    APP = asgiref.wsgi.WsgiToAsgi(app)


addons = [GetTaskInventoryCapExampleAddon()]
