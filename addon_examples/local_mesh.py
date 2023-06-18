"""
Allows specifying a target object to apply a mesh preview to. When a local mesh target
is specified, hitting the "calculate upload cost" button in the mesh uploader will instead
apply the mesh to the local mesh target. It works on attachments too. Useful for testing rigs before a
final, real upload.

Select an object and do /524 set_local_mesh_target, then go through the mesh upload flow.
Mesh pieces will be mapped to your object based on object name. Note that if you're using Blender
these will be based on the name of your _geometry nodes_ and not the objects themselves.

The object you select as a mesh target must contain a mesh prim. The mesh objects you use as a local
mesh target should have at least as many faces as the mesh you want to apply to it or you won't
be able to set textures on those faces correctly.

When you're done with local mesh and want to allow regular mesh upload again, do
/524 disable_local_mesh

Does not attempt to apply textures uploaded with the mesh.
"""
from __future__ import annotations

import ctypes
import secrets
from typing import *

import mitmproxy.http

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import *
from hippolyzer.lib.base.mesh import LLMeshSerializer, MeshAsset
from hippolyzer.lib.base import serialization as se
from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.base.templates import ExtraParamType
from hippolyzer.lib.proxy import addon_ctx
from hippolyzer.lib.proxy.addon_utils import show_message, BaseAddon, GlobalProperty, SessionProperty
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.http_asset_repo import HTTPAssetRepo
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager


def _modify_crc(crc_tweak, crc_val):
    return ctypes.c_uint32(crc_val ^ crc_tweak).value


def _mangle_mesh_list(mesh_list: List[bytes], manglers: List[Callable]) -> List[bytes]:
    if not mesh_list or not manglers:
        return mesh_list
    new_mesh_list = []
    mesh_ser = LLMeshSerializer()
    for mesh_bytes in mesh_list:
        reader = se.BufferReader("!", mesh_bytes)
        mesh: MeshAsset = reader.read(mesh_ser)
        for mangler in manglers:
            mesh = mangler(mesh)
        writer = se.BufferWriter("!")
        writer.write(mesh_ser, mesh)
        new_mesh_list.append(writer.copy_buffer())
    return new_mesh_list


class MeshUploadInterceptingAddon(BaseAddon):
    mesh_crc_tweak: int = GlobalProperty(default=secrets.randbits(32))
    mesh_manglers: List[Callable[[MeshAsset], MeshAsset]] = GlobalProperty(list)
    # LocalIDs being targeted for local mesh
    local_mesh_target_locals: List[int] = SessionProperty(list)
    # Name -> mesh index mapping
    local_mesh_mapping: Dict[str, int] = SessionProperty(dict)
    # originally supplied mesh bytes, indexed by mesh index.
    # mostly used for re-mangling if mesh manglers changed.
    local_mesh_orig_bytes: List[bytes] = SessionProperty(list)
    # Above, but for the local asset IDs
    local_mesh_asset_ids: List[UUID] = SessionProperty(list)

    def handle_init(self, session_manager: SessionManager):
        # Other plugins can add to this list to apply transforms to mesh
        # whenever it's uploaded.
        self.remangle_local_mesh(session_manager)

    @handle_command()
    async def set_local_mesh_target(self, session: Session, region: ProxiedRegion):
        """Set the currently selected objects as the target for local mesh"""
        selected_links = [region.objects.lookup_localid(l_id) for l_id in session.selected.object_locals]
        selected_links = [o for o in selected_links if o is not None]
        if not selected_links:
            show_message("Nothing selected")
            return
        old_locals = self.local_mesh_target_locals
        self.local_mesh_target_locals = [
            x.LocalID
            for x in selected_links
            if ExtraParamType.MESH in x.ExtraParams
        ]

        if old_locals:
            # Return the old objects to normal
            self.mesh_crc_tweak = secrets.randbits(32)
            region.objects.request_objects(old_locals)

        if not self.local_mesh_target_locals:
            show_message("There must be at least one mesh object in the linkset!")
            return

        # We'll need the name for all of these to pick which mesh asset to
        # apply to them.
        region.objects.request_object_properties(self.local_mesh_target_locals)
        show_message(f"Targeting {self.local_mesh_target_locals}")

    @handle_command()
    async def disable_local_mesh(self, session: Session, region: ProxiedRegion):
        """Disable local mesh mode, allowing mesh upload and returning targets to normal"""
        # Put the target objects back to normal and kill the temp assets
        old_locals = tuple(self.local_mesh_target_locals)
        self.local_mesh_target_locals.clear()
        asset_repo: HTTPAssetRepo = session.session_manager.asset_repo
        for asset_id in self.local_mesh_asset_ids:
            del asset_repo[asset_id]
        self.local_mesh_asset_ids.clear()
        self.local_mesh_asset_ids.clear()
        self.local_mesh_mapping.clear()
        if old_locals:
            region.objects.request_objects(old_locals)
        show_message(f"Cleared target {old_locals}")

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        # Replace any mesh asset IDs in tracked objects with our local assets
        if not self.local_mesh_target_locals:
            return
        if not self.local_mesh_asset_ids:
            return

        if message.name == "ObjectUpdate":
            for block in message["ObjectData"]:
                if block["ID"] not in self.local_mesh_target_locals:
                    continue
                block["CRC"] = _modify_crc(self.mesh_crc_tweak, block["CRC"])
                parsed_params = block.deserialize_var("ExtraParams")
                if not parsed_params:
                    continue
                obj = region.objects.lookup_localid(block["ID"])
                if not obj:
                    return
                parsed_params[ExtraParamType.MESH]["Asset"] = self._pick_mesh_asset(obj)
                block.serialize_var("ExtraParams", parsed_params)
        elif message.name == "ObjectUpdateCompressed":
            for block in message["ObjectData"]:
                update_data = block.deserialize_var("Data")
                if not update_data:
                    continue
                if update_data["ID"] not in self.local_mesh_target_locals:
                    continue
                update_data["CRC"] = _modify_crc(self.mesh_crc_tweak, update_data["CRC"])
                if not update_data.get("ExtraParams"):
                    continue

                obj = region.objects.lookup_localid(update_data["ID"])
                if not obj:
                    return
                extra_params = update_data["ExtraParams"]
                extra_params[ExtraParamType.MESH]["Asset"] = self._pick_mesh_asset(obj)
                block.serialize_var("Data", update_data)

    def _pick_mesh_asset(self, obj: Object) -> UUID:
        mesh_idx = self.local_mesh_mapping.get(obj.Name, 0)
        # Use whatever the first mesh was if we don't have a match on name.
        return self.local_mesh_asset_ids[mesh_idx]

    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        cap_data = flow.cap_data
        if not cap_data:
            return
        if cap_data.cap_name == "NewFileAgentInventory":
            # Might be an upload cost calculation request for mesh, includes the actual mesh data.
            payload = llsd.parse_xml(flow.request.content)
            if "asset_resources" not in payload:
                return

            orig_mesh_list = payload["asset_resources"].get("mesh_list")
            if not orig_mesh_list:
                return

            # Replace the mesh instances in the payload with versions run through our mangler
            new_mesh_list = _mangle_mesh_list(orig_mesh_list, self.mesh_manglers)
            payload["asset_resources"]["mesh_list"] = new_mesh_list

            # We have local mesh instances, re-use the data sent along with the upload cost
            # request to apply the mesh to our local mesh objects intead.
            if self.local_mesh_target_locals:
                region: ProxiedRegion = cap_data.region()
                asset_repo: HTTPAssetRepo = session_manager.asset_repo
                # Apply the new mesh to any local mesh targets
                self._replace_local_mesh(region, asset_repo, new_mesh_list)
                # Keep the original bytes around in case manglers get reloaded
                # and we want to re-run them
                self.local_mesh_orig_bytes = orig_mesh_list
                instances = payload["asset_resources"]["instance_list"]
                # To figure out what mesh index applies to what object name
                self.local_mesh_mapping = {x["mesh_name"]: x["mesh"] for x in instances}

                # Fake a response, we don't want to actually send off the request.
                flow.response = mitmproxy.http.Response.make(
                    200,
                    b"",
                    {
                        "Content-Type": "text/plain",
                        "Connection": "close",
                    }
                )
                show_message("Applying local mesh")
            # Even if we're not in local mesh mode, we want the upload cost for
            # our mangled mesh
            elif self.mesh_manglers:
                flow.request.content = llsd.format_xml(payload)
                show_message("Mangled upload cost request")
        elif cap_data.cap_name == "NewFileAgentInventoryUploader":
            # Don't bother looking at this if we have no manglers
            if not self.mesh_manglers:
                return
            # Depending on what asset is being uploaded the body may not even be LLSD.
            if not flow.request.content or b"mesh_list" not in flow.request.content:
                return
            payload = llsd.parse_xml(flow.request.content)
            if not payload.get("mesh_list"):
                return

            payload["mesh_list"] = _mangle_mesh_list(payload["mesh_list"], self.mesh_manglers)
            flow.request.content = llsd.format_xml(payload)
            show_message("Mangled upload request")

    def handle_object_updated(self, session: Session, region: ProxiedRegion,
                              obj: Object, updated_props: Set[str], msg: Optional[Message]):
        if obj.LocalID not in self.local_mesh_target_locals:
            return
        if "Name" not in updated_props or obj.Name is None:
            return
        # A local mesh target has a new name, which mesh we need to apply
        # to the object may have changed.
        self.mesh_crc_tweak = secrets.randbits(32)
        region.objects.request_objects(obj.LocalID)

    @classmethod
    def _replace_local_mesh(cls, region: ProxiedRegion, asset_repo, mesh_list: List[bytes]) -> None:
        cls.mesh_crc_tweak = secrets.randbits(32)

        for asset_id in cls.local_mesh_asset_ids:
            del asset_repo[asset_id]
        cls.local_mesh_asset_ids.clear()
        for mesh_blob in mesh_list:
            cls.local_mesh_asset_ids.append(asset_repo.create_asset(mesh_blob))
        # Ask for a full update so we can clobber the mesh param
        # Janky hack around the fact that we don't know how to build
        # them from scratch yet.
        region.objects.request_objects(cls.local_mesh_target_locals)

    @classmethod
    def remangle_local_mesh(cls, session_manager: SessionManager):
        # We want CRCs that are stable for the duration of the session, but will
        # cause a cache miss for objects cached before this session. Generate a
        # random value to XOR all CRCs with
        # We need to regen this when we force a re-mangle to indicate that the
        # viewer should pay attention to the incoming ObjectUpdate
        cls.mesh_crc_tweak = secrets.randbits(32)

        asset_repo: HTTPAssetRepo = session_manager.asset_repo
        # Mesh manglers are global, so we need to re-mangle mesh for all sessions
        for session in session_manager.sessions:
            # Push the context of this session onto the stack so we can access
            # session-scoped properties
            with addon_ctx.push(new_session=session, new_region=session.main_region):
                if not cls.local_mesh_target_locals:
                    continue
                orig_bytes = cls.local_mesh_orig_bytes
                if not orig_bytes:
                    continue
                show_message("Remangling mesh", session=session)
                mesh_list = _mangle_mesh_list(orig_bytes, cls.mesh_manglers)
                cls._replace_local_mesh(session.main_region, asset_repo, mesh_list)


class BaseMeshManglerAddon(BaseAddon):
    """Base class for addons that mangle uploaded or local mesh"""
    MESH_MANGLERS: List[Callable[[MeshAsset], MeshAsset]]

    def handle_init(self, session_manager: SessionManager):
        # Add our manglers into the list
        MeshUploadInterceptingAddon.mesh_manglers.extend(self.MESH_MANGLERS)
        # Tell the local mesh plugin that the mangler list changed, and to re-apply
        MeshUploadInterceptingAddon.remangle_local_mesh(session_manager)

    def handle_unload(self, session_manager: SessionManager):
        # Clean up our manglers before we go away
        mangler_list = MeshUploadInterceptingAddon.mesh_manglers
        for mangler in self.MESH_MANGLERS:
            if mangler in mangler_list:
                mangler_list.remove(mangler)
        MeshUploadInterceptingAddon.remangle_local_mesh(session_manager)


addons = [MeshUploadInterceptingAddon()]
