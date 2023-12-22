from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.inventory import InventoryItem
from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.client.asset_uploader import AssetUploader


class ProxyAssetUploader(AssetUploader):
    async def _handle_upload_complete(self, resp_payload: dict):
        # Check if this a failure response first, raising if it is
        await super()._handle_upload_complete(resp_payload)

        # Fetch enough data from AIS to tell the viewer about the new inventory item
        session = self._region.session()
        item_id = resp_payload["new_inventory_item"]
        ais_req_data = {
            "items": [
                {
                    "owner_id": session.agent_id,
                    "item_id": item_id,
                }
            ]
        }
        async with self._region.caps_client.post('FetchInventory2', llsd=ais_req_data) as resp:
            ais_item = InventoryItem.from_llsd((await resp.read_llsd())["items"][0], flavor="ais")

        # Got it, ship it off to the viewer
        message = Message(
            "UpdateCreateInventoryItem",
            Block(
                "AgentData",
                AgentID=session.agent_id,
                SimApproved=1,
                TransactionID=UUID.random(),
            ),
            ais_item.to_inventory_data(),
            direction=Direction.IN
        )
        self._region.circuit.send(message)
