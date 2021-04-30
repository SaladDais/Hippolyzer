"""
Example of how to request an Xfer
"""
from hippolyzer.lib.base.legacy_inv import InventoryModel
from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.proxy.addon_utils import BaseAddon, show_message
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session
from hippolyzer.lib.proxy.templates import XferFilePath


class XferExampleAddon(BaseAddon):
    @handle_command()
    async def get_mute_list(self, session: Session, region: ProxiedRegion):
        """Fetch the current user's mute list"""
        region.circuit.send_message(ProxiedMessage(
            'MuteListRequest',
            Block('AgentData', AgentID=session.agent_id, SessionID=session.id),
            Block("MuteData", MuteCRC=0),
        ))

        # Wait for any MuteListUpdate, dropping it before it reaches the viewer
        update_msg = await region.message_handler.wait_for('MuteListUpdate', timeout=5.0)
        mute_file_name = update_msg["MuteData"]["Filename"]
        if not mute_file_name:
            show_message("Nobody muted?")
            return

        xfer = await region.xfer_manager.request(
            file_name=mute_file_name, file_path=XferFilePath.CACHE)
        show_message(xfer.reassemble_chunks().decode("utf8"))

    @handle_command()
    async def get_task_inventory(self, session: Session, region: ProxiedRegion):
        """Get the inventory of the currently selected object"""
        region.circuit.send_message(ProxiedMessage(
            'RequestTaskInventory',
            # If no session is passed in we'll use the active session when the coro was created
            Block('AgentData', AgentID=session.agent_id, SessionID=session.id),
            Block('InventoryData', LocalID=session.selected.object_local),
        ))

        inv_message = await region.message_handler.wait_for('ReplyTaskInventory', timeout=5.0)

        # Xfer doesn't need to be immediately awaited, multiple signals can be waited on.
        xfer = region.xfer_manager.request(
            file_name=inv_message["InventoryData"]["Filename"], file_path=XferFilePath.CACHE)

        # Wait until we have the first packet so we can tell the expected length
        # The difference in time is obvious for large inventories, and we can cancel
        # mid-request if we want.
        show_message(f"Inventory is {await xfer.size_known} bytes")

        # Wait for the rest of the body to be done
        await xfer

        inv_model = InventoryModel.from_bytes(xfer.reassemble_chunks())
        item_names = [item.name for item in inv_model.items.values()]
        show_message(item_names)


addons = [XferExampleAddon()]
