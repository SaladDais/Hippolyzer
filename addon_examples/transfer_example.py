"""
Example of how to request a Transfer
"""
from typing import *

from hippolyzer.lib.base.inventory import InventoryModel, InventoryItem
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.templates import (
    AssetType,
    EstateAssetType,
    TransferRequestParamsSimEstate,
    TransferRequestParamsSimInvItem,
    TransferSourceType,
    XferFilePath,
)
from hippolyzer.lib.proxy.addon_utils import BaseAddon, show_message
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class TransferExampleAddon(BaseAddon):
    @handle_command()
    async def get_covenant(self, _session: Session, region: ProxiedRegion):
        """Get the current region's covenent"""
        transfer = await region.transfer_manager.request(
            source_type=TransferSourceType.SIM_ESTATE,
            params=TransferRequestParamsSimEstate(
                EstateAssetType=EstateAssetType.COVENANT,
            ),
        )
        show_message(transfer.reassemble_chunks().decode("utf8"))

    @handle_command()
    async def get_first_script(self, session: Session, region: ProxiedRegion):
        """Get the contents of the first script in the selected object"""
        # Ask for the object inventory so we can find a script
        region.circuit.send(Message(
            'RequestTaskInventory',
            Block('AgentData', AgentID=session.agent_id, SessionID=session.id),
            Block('InventoryData', LocalID=session.selected.object_local),
        ))
        inv_message = await region.message_handler.wait_for(('ReplyTaskInventory',), timeout=5.0)

        # Xfer the inventory file and look for a script
        xfer = await region.xfer_manager.request(
            file_name=inv_message["InventoryData"]["Filename"], file_path=XferFilePath.CACHE)
        inv_model = InventoryModel.from_bytes(xfer.reassemble_chunks())
        first_script: Optional[InventoryItem] = None
        for item in inv_model.all_items:
            if item.type == "lsltext":
                first_script = item
        if not first_script:
            show_message("No scripts in object?")
            return

        # Ask for the actual script contents
        transfer = await region.transfer_manager.request(
            source_type=TransferSourceType.SIM_INV_ITEM,
            params=TransferRequestParamsSimInvItem(
                OwnerID=first_script.permissions.owner_id,
                TaskID=inv_model.root.node_id,
                ItemID=first_script.item_id,
                AssetType=AssetType.LSL_TEXT,
            ),
        )
        show_message(transfer.reassemble_chunks().decode("utf8"))


addons = [TransferExampleAddon()]
