"""
Example of how to upload assets, assumes assets are already encoded
in the appropriate format.

/524 upload_asset <asset type>
"""
from pathlib import Path
from typing import *

from hippolyzer.lib.base.mesh import LLMeshSerializer
from hippolyzer.lib.base.serialization import BufferReader
from hippolyzer.lib.base.templates import AssetType
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.addon_utils import show_message, BaseAddon
from hippolyzer.lib.proxy.commands import handle_command, Parameter
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

        try:
            if asset_type == AssetType.MESH:
                # Kicking off a mesh upload works a little differently internally
                # Half-parse the mesh so that we can figure out how many faces it has
                reader = BufferReader("!", file_body)
                mesh = reader.read(LLMeshSerializer(parse_segment_contents=False))
                upload_token = await region.asset_uploader.initiate_mesh_upload(
                    name, mesh, flags=flags
                )
            else:
                upload_token = await region.asset_uploader.initiate_asset_upload(
                    name, asset_type, file_body, flags=flags,
                )
        except Exception as e:
            show_message(e)
            raise

        if not await AddonManager.UI.confirm("Upload", f"Spend {upload_token.linden_cost}L on upload?"):
            return

        # Do the actual upload
        try:
            await region.asset_uploader.complete_upload(upload_token)
        except Exception as e:
            show_message(e)
            raise


addons = [UploaderAddon()]
