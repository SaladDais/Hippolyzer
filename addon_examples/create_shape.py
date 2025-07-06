"""
Demonstrates item creation as well as bodypart / clothing upload
"""

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.templates import WearableType, Permissions
from hippolyzer.lib.base.wearables import Wearable, VISUAL_PARAMS
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class ShapeCreatorAddon(BaseAddon):
    @handle_command()
    async def create_shape(self, session: Session, region: ProxiedRegion):
        """Make a shape with pre-set parameters and place it in the body parts folder"""

        wearable = Wearable.make_default(WearableType.SHAPE)
        # Max out the jaw jut param
        jaw_param = VISUAL_PARAMS.by_name("Jaw Jut")
        wearable.parameters[jaw_param.id] = jaw_param.value_max
        wearable.name = "Cool Shape"

        # A unique transaction ID is needed to tie the item creation to the following asset upload.
        transaction_id = UUID.random()
        item = await session.inventory.create_item(
            UUID.ZERO,  # This will place it in the default folder for the type
            name=wearable.name,
            type=wearable.wearable_type.asset_type,
            inv_type=wearable.wearable_type.asset_type.inventory_type,
            wearable_type=wearable.wearable_type,
            next_mask=Permissions.MOVE | Permissions.MODIFY | Permissions.COPY | Permissions.TRANSFER,
            transaction_id=transaction_id,
        )
        print(f"Created {item!r}")
        await region.xfer_manager.upload_asset(
            wearable.wearable_type.asset_type,
            wearable.to_str(),
            transaction_id=transaction_id,
        )


addons = [ShapeCreatorAddon()]
