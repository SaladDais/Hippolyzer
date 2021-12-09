"""
Recapitator addon, merges a base head shape into body shapes.

Only works if both the base shapes and shapes you need to edit are modify.

Useful if you switch heads a lot. Most heads come with a base shape you
have to start from if you don't want the head to look like garbage. If you
have an existing shape for your body, you have to write down all the values
of the base shape's head sliders and edit them onto your body shapes.

This addon does basically the same thing by intercepting shape uploads. After
enabling recapitation, you save the base head shape once. Then the next time you
edit and save a body shape, it will be saved with the head sliders from your base
shape.
"""
import logging
from typing import *

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.templates import AssetType, WearableType
from hippolyzer.lib.base.wearables import Wearable, VISUAL_PARAMS
from hippolyzer.lib.proxy.addon_utils import BaseAddon, SessionProperty, AssetAliasTracker, show_message
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager


# Get all VisualParam IDs that belong to head sliders
HEAD_EDIT_GROUPS = ("shape_head", "shape_eyes", "shape_ears", "shape_nose", "shape_mouth", "shape_chin")
HEAD_PARAM_IDS = [v.id for v in VISUAL_PARAMS if v.edit_group in HEAD_EDIT_GROUPS]


class RecapitatorAddon(BaseAddon):
    transaction_remappings: AssetAliasTracker = SessionProperty(AssetAliasTracker)
    recapitating: bool = SessionProperty(bool)
    recapitation_mappings: Dict[int, float] = SessionProperty(dict)

    @handle_command()
    async def enable_recapitation(self, _session: Session, _region: ProxiedRegion):
        """Apply base head shape when saving subsequent shapes"""
        self.recapitating = True
        self.recapitation_mappings.clear()
        show_message("Recapitation enabled, wear the base shape containing the head parameters and save it.")

    @handle_command()
    async def disable_recapitation(self, _session: Session, _region: ProxiedRegion):
        self.recapitating = False
        show_message("Recapitation disabled")

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if not self.recapitating:
            return
        if message.direction != Direction.OUT:
            return
        if message.name != "AssetUploadRequest":
            return
        if message["AssetBlock"]["Type"] != AssetType.BODYPART:
            return

        # Pending asset upload for a bodypart asset. Take the message and request
        # it from the client ourself so we can see what it wants to upload
        new_message = message.take()
        self._schedule_task(self._proxy_bodypart_upload(session, region, new_message))
        return True

    async def _proxy_bodypart_upload(self, session: Session, region: ProxiedRegion, message: Message):
        asset_block = message["AssetBlock"]
        # Asset will already be in the viewer's VFS as the expected asset ID, calculate it.
        asset_id = session.transaction_to_assetid(asset_block["TransactionID"])
        success = False
        try:
            # Xfer the asset from the viewer if it wasn't small enough to fit in AssetData
            if asset_block["AssetData"]:
                asset_data = asset_block["AssetData"]
            else:
                xfer = await region.xfer_manager.request(
                    vfile_id=asset_id,
                    vfile_type=AssetType.BODYPART,
                    direction=Direction.IN,
                )
                asset_data = xfer.reassemble_chunks()

            wearable = Wearable.from_bytes(asset_data)
            # If they're uploading a shape, process it.
            if wearable.wearable_type == WearableType.SHAPE:
                if self.recapitation_mappings:
                    # Copy our previously saved head params over
                    for key, value in self.recapitation_mappings.items():
                        wearable.parameters[key] = value
                    # Upload the changed version
                    asset_data = wearable.to_bytes()
                    show_message("Recapitated shape")
                else:
                    # Don't have a recapitation mapping yet, use this shape as the base.
                    for param_id in HEAD_PARAM_IDS:
                        self.recapitation_mappings[param_id] = wearable.parameters[param_id]
                    show_message("Got base parameters for recapitation, head parameters will be copied")

            # Upload it ourselves with a new transaction ID that can be traced back to
            # the original. This is important because otherwise the viewer will use its
            # own cached version of the shape, under the assumption it wasn't modified
            # during upload.
            new_transaction_id = self.transaction_remappings.get_alias_uuid(
                asset_block["TransactionID"]
            )
            await region.xfer_manager.upload_asset(
                asset_type=AssetType.BODYPART,
                data=asset_data,
                transaction_id=new_transaction_id,
            )
            success = True
        except:
            logging.exception("Exception while recapitating")
        # Tell the viewer about the status of its original upload
        region.circuit.send(Message(
            "AssetUploadComplete",
            Block("AssetBlock", UUID=asset_id, Type=asset_block["Type"], Success=success),
            direction=Direction.IN,
        ))

    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        # Skip requests that aren't related to patching an existing item
        if flow.cap_data.cap_name != "InventoryAPIv3":
            return
        if flow.request.method != "PATCH":
            return
        if "/item/" not in flow.request.url:
            return

        parsed = llsd.parse_xml(flow.request.content)
        if parsed.get("type") != "bodypart":
            return
        # `hash_id` being present means we're updating the item to point to a newly
        # uploaded asset. It's actually a transaction ID.
        transaction_id: Optional[UUID] = parsed.get("hash_id")
        if not transaction_id:
            return
        # We have an original transaction ID, do we need to remap it to an alias ID?
        orig_id = self.transaction_remappings.get_alias_uuid(transaction_id, create=False)
        if not orig_id:
            return

        parsed["hash_id"] = orig_id
        flow.request.content = llsd.format_xml(parsed)


addons = [RecapitatorAddon()]
