from typing import NamedTuple, Union, Optional, List

import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.mesh import MeshAsset, LLMeshSerializer
from hippolyzer.lib.base.templates import AssetType
from hippolyzer.lib.client.state import BaseClientRegion


class UploadError(Exception):
    pass


class UploadToken(NamedTuple):
    linden_cost: int
    uploader_url: str
    payload: bytes


class MeshUploadDetails(NamedTuple):
    mesh_bytes: bytes
    num_faces: int


class AssetUploader:
    def __init__(self, region: BaseClientRegion):
        self._region = region

    async def initiate_asset_upload(self, name: str, asset_type: AssetType,
                                    body: bytes, flags: Optional[int] = None) -> UploadToken:
        payload = {
            "asset_type": asset_type.to_lookup_name(),
            "description": "(No Description)",
            "everyone_mask": 0,
            "group_mask": 0,
            "folder_id": UUID.ZERO,  # Puts it in the default folder, I guess. Undocumented.
            "inventory_type": asset_type.inventory_type.to_lookup_name(),
            "name": name,
            "next_owner_mask": 581632,
        }
        if flags is not None:
            payload['flags'] = flags
        resp_payload = await self._make_newfileagentinventory_req(payload)

        return UploadToken(resp_payload["upload_price"], resp_payload["uploader"], body)

    async def _make_newfileagentinventory_req(self, payload: dict):
        async with self._region.caps_client.post("NewFileAgentInventory", llsd=payload) as resp:
            resp.raise_for_status()
            resp_payload = await resp.read_llsd()
        # Need to sniff the resp payload for this because SL sends a 200 status code on error
        if "error" in resp_payload:
            raise UploadError(resp_payload)
        return resp_payload

    async def complete_upload(self, token: UploadToken) -> dict:
        async with self._region.caps_client.post(token.uploader_url, data=token.payload) as resp:
            resp.raise_for_status()
            resp_payload = await resp.read_llsd()
        # The actual upload endpoints return 200 on error, have to sniff the payload to figure
        # out if it actually failed...
        if "error" in resp_payload:
            raise UploadError(resp_payload)
        await self._handle_upload_complete(resp_payload)
        return resp_payload

    async def _handle_upload_complete(self, resp_payload: dict):
        """
        Generic hook called when any asset upload completes.

        Could trigger an AIS fetch to send the viewer details about the item we just created,
        assuming we were in proxy context.
        """
        pass

    # The mesh upload flow is a little special, so it gets its own method
    async def initiate_mesh_upload(self, name: str, mesh: Union[MeshUploadDetails, MeshAsset],
                                   flags: Optional[int] = None) -> UploadToken:
        if isinstance(mesh, MeshAsset):
            writer = se.BufferWriter("!")
            writer.write(LLMeshSerializer(), mesh)
            mesh = MeshUploadDetails(writer.copy_buffer(), len(mesh.segments['high_lod']))

        asset_resources = self._build_asset_resources(name, [mesh])
        payload = {
            'asset_resources': asset_resources,
            'asset_type': 'mesh',
            'description': '(No Description)',
            'everyone_mask': 0,
            'folder_id': UUID.ZERO,
            'group_mask': 0,
            'inventory_type': 'object',
            'name': name,
            'next_owner_mask': 581632,
            'texture_folder_id': UUID.ZERO
        }
        if flags is not None:
            payload['flags'] = flags
        resp_payload = await self._make_newfileagentinventory_req(payload)

        upload_body = llsd.format_xml(asset_resources)
        return UploadToken(resp_payload["upload_price"], resp_payload["uploader"], upload_body)

    def _build_asset_resources(self, name: str, meshes: List[MeshUploadDetails]) -> dict:
        instances = []
        for mesh in meshes:
            instances.append({
                'face_list': [{
                    'diffuse_color': [1.0, 1.0, 1.0, 1.0],
                    'fullbright': False
                }] * mesh.num_faces,
                'material': 3,
                'mesh': 0,
                'mesh_name': name,
                'physics_shape_type': 2,
                'position': [0.0, 0.0, 0.0],
                'rotation': [0.7071067690849304, 0.0, 0.0, 0.7071067690849304],
                'scale': [1.0, 1.0, 1.0]
            })

        return {
            'instance_list': instances,
            'mesh_list': [mesh.mesh_bytes for mesh in meshes],
            'metric': 'MUT_Unspecified',
            'texture_list': []
        }
