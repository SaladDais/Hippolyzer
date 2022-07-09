"""
Example of how to request an Xfer
"""
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.inventory import InventoryModel
from hippolyzer.lib.base.templates import XferFilePath, AssetType, InventoryType, WearableType
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.proxy.addon_utils import BaseAddon, show_message
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class XferExampleAddon(BaseAddon):
    @handle_command()
    async def get_mute_list(self, session: Session, region: ProxiedRegion):
        """Fetch the current user's mute list"""
        region.circuit.send(Message(
            'MuteListRequest',
            Block('AgentData', AgentID=session.agent_id, SessionID=session.id),
            Block("MuteData", MuteCRC=0),
        ))

        # Wait for any MuteListUpdate, dropping it before it reaches the viewer
        update_msg = await region.message_handler.wait_for(('MuteListUpdate',), timeout=5.0)
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
        region.circuit.send(Message(
            'RequestTaskInventory',
            # If no session is passed in we'll use the active session when the coro was created
            Block('AgentData', AgentID=session.agent_id, SessionID=session.id),
            Block('InventoryData', LocalID=session.selected.object_local),
        ))

        inv_message = await region.message_handler.wait_for(('ReplyTaskInventory',), timeout=5.0)

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
        item_names = [item.name for item in inv_model.all_items]
        show_message(item_names)

    @handle_command()
    async def eyes_for_you(self, session: Session, region: ProxiedRegion):
        """Upload an eye bodypart and create an item for it"""
        asset_data = f"""LLWearable version 22
New Eyes

\tpermissions 0
\t{{
\t\tbase_mask\t7fffffff
\t\towner_mask\t7fffffff
\t\tgroup_mask\t00000000
\t\teveryone_mask\t00000000
\t\tnext_owner_mask\t00082000
\t\tcreator_id\t{session.agent_id}
\t\towner_id\t{session.agent_id}
\t\tlast_owner_id\t00000000-0000-0000-0000-000000000000
\t\tgroup_id\t00000000-0000-0000-0000-000000000000
\t}}
\tsale_info\t0
\t{{
\t\tsale_type\tnot
\t\tsale_price\t10
\t}}
type 3
parameters 2
98 0
99 0
textures 1
3 89556747-24cb-43ed-920b-47caed15465f
"""
        # If we want to create an item containing the asset we need to know the transaction id
        # used to create the asset.
        transaction_id = UUID.random()
        await region.xfer_manager.upload_asset(
            AssetType.BODYPART,
            data=asset_data,
            transaction_id=transaction_id
        )
        region.circuit.send(Message(
            'CreateInventoryItem',
            Block('AgentData', AgentID=session.agent_id, SessionID=session.id),
            Block(
                'InventoryBlock',
                CallbackID=0,
                # Null folder ID will put it in the default folder for the type
                FolderID=UUID(),
                TransactionID=transaction_id,
                NextOwnerMask=0x7fFFffFF,
                Type=AssetType.BODYPART,
                InvType=InventoryType.WEARABLE,
                WearableType=WearableType.EYES,
                Name='Eyes For You',
                Description=b''
            ),
        ))


addons = [XferExampleAddon()]
