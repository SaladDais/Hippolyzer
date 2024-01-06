import asyncio
from typing import Dict, Sequence

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.helpers import proxify
from hippolyzer.lib.base import llsd
from hippolyzer.lib.client.state import BaseClientRegion


MATERIAL_MAP_TYPE = Dict[UUID, dict]


class ClientMaterialManager:
    """
    Material manager for a specific region
    """

    def __init__(self, region: BaseClientRegion):
        self._region = proxify(region)
        self.materials: MATERIAL_MAP_TYPE = {}
        self._requesting_all_lock = asyncio.Lock()

    def clear(self):
        self.materials.clear()

    async def request_all_materials(self) -> MATERIAL_MAP_TYPE:
        """
        Request all materials within the sim

        Sigh, yes, this is best practice per indra :(
        """
        if self._requesting_all_lock.locked():
            # We're already requesting all materials, wait until the lock is free
            # and just return what was returned.
            async with self._requesting_all_lock:
                return self.materials

        async with self._requesting_all_lock:
            async with self._region.caps_client.get("RenderMaterials") as resp:
                resp.raise_for_status()
                # Clear out all previous materials, this is a complete response.
                self.materials.clear()
                self._process_materials_response(await resp.read())
            return self.materials

    async def request_materials(self, material_ids: Sequence[UUID]) -> MATERIAL_MAP_TYPE:
        if self._requesting_all_lock.locked():
            # Just wait for the in-flight request for all materials to complete
            # if we have one in flight.
            async with self._requesting_all_lock:
                # Wait for the lock to be released
                pass

        not_found = set(x for x in material_ids if (x not in self.materials))
        if not_found:
            # Request any materials we don't already have, if there were any
            data = {"Zipped": llsd.zip_llsd([x.bytes for x in material_ids])}
            async with self._region.caps_client.post("RenderMaterials", data=data) as resp:
                resp.raise_for_status()
                self._process_materials_response(await resp.read())

        # build up a dict of just the requested mats
        mats = {}
        for mat_id in material_ids:
            mats[mat_id] = self.materials[mat_id]
        return mats

    def _process_materials_response(self, response: bytes):
        entries = llsd.unzip_llsd(llsd.parse_xml(response)["Zipped"])
        for entry in entries:
            self.materials[UUID(bytes=entry["ID"])] = entry["Material"]
