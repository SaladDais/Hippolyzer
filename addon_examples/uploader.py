"""
Example of how to upload assets, assumes assets are already encoded
in the appropriate format.

/524 upload <asset type>
"""
import pprint
from pathlib import Path
from typing import *

import aiohttp

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.templates import AssetType
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.addon_utils import ais_item_to_inventory_data, show_message, BaseAddon
from hippolyzer.lib.proxy.commands import handle_command, Parameter
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class UploaderAddon(BaseAddon):
    @handle_command(
        asset_type=Parameter(lambda x: AssetType[x.upper()]),
        flags=Parameter(int, optional=True)
    )
    async def upload_asset(self, _session: Session, region: ProxiedRegion,
                           asset_type: AssetType, flags: Optional[int] = None):
        """Upload a raw asset with optional flags"""
        inv_type = asset_type.inventory_type
        file = await AddonManager.UI.open_file()
        if not file:
            return
        file = Path(file)
        if not file.exists():
            show_message(f"{file} does not exist")
            return
        name = file.stem

        with open(file, "rb") as f:
            file_body = f.read()

        params = {
            "asset_type": asset_type.human_name,
            "description": "(No Description)",
            "everyone_mask": 0,
            "group_mask": 0,
            "folder_id": UUID(),  # Puts it in the default folder, I guess. Undocumented.
            "inventory_type": inv_type.human_name,
            "name": name,
            "next_owner_mask": 581632,
        }
        if flags is not None:
            params['flags'] = flags

        caps = region.caps_client
        async with aiohttp.ClientSession() as sess:
            async with caps.post('NewFileAgentInventory', llsd=params, session=sess) as resp:
                parsed = await resp.read_llsd()
                if "uploader" not in parsed:
                    show_message(f"Upload error!: {parsed!r}")
                    return
                print("Got upload URL, uploading...")

            async with caps.post(parsed["uploader"], data=file_body, session=sess) as resp:
                upload_parsed = await resp.read_llsd()

            if "new_inventory_item" not in upload_parsed:
                show_message(f"Got weird upload resp: {pprint.pformat(upload_parsed)}")
                return

        await self._force_inv_update(region, upload_parsed['new_inventory_item'])

    @handle_command(item_id=UUID)
    async def force_inv_update(self, _session: Session, region: ProxiedRegion, item_id: UUID):
        """Force an inventory update for a given item id"""
        await self._force_inv_update(region, item_id)

    async def _force_inv_update(self, region: ProxiedRegion, item_id: UUID):
        session = region.session()
        ais_req_data = {
            "items": [
                {
                    "owner_id": session.agent_id,
                    "item_id": item_id,
                }
            ]
        }
        async with region.caps_client.post('FetchInventory2', llsd=ais_req_data) as resp:
            ais_item = (await resp.read_llsd())["items"][0]

        message = Message(
            "UpdateCreateInventoryItem",
            Block(
                "AgentData",
                AgentID=session.agent_id,
                SimApproved=1,
                TransactionID=UUID.random(),
            ),
            ais_item_to_inventory_data(ais_item),
            direction=Direction.IN
        )
        region.circuit.send(message)


addons = [UploaderAddon()]
