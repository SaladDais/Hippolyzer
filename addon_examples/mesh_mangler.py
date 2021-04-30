"""
Example mesh mangler addon, to be used with local mesh addon.

You can edit this live to apply various transforms to local mesh.
If there are no live local mesh instances, the transforms will be
applied to the mesh before upload.

I personally use manglers to strip bounding box materials you need
to add to give a mesh an arbitrary center of rotation / scaling.
"""

from hippolyzer.lib.base.mesh import MeshAsset
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.sessions import SessionManager

import local_mesh
AddonManager.hot_reload(local_mesh, require_addons_loaded=True)


def _reorient_coord(coord, orientation):
    coords = []
    for axis in orientation:
        axis_idx = abs(axis) - 1
        coords.append(coord[axis_idx] if axis >= 0 else 1.0 - coord[axis_idx])
    if coord.__class__ in (list, tuple):
        return coord.__class__(coords)
    return coord.__class__(*coords)


def _reorient_coord_list(coord_list, orientation):
    return [_reorient_coord(x, orientation) for x in coord_list]


def reorient_mesh(orientation):
    # Returns a callable that will change `mesh` to match `orientation`
    # X=1, Y=2, Z=3
    def _reorienter(mesh: MeshAsset):
        for material in mesh.iter_lod_materials():
            # We don't need to use positions_(to/from)_domain here since we're just naively
            # flipping the axes around.
            material["Position"] = _reorient_coord_list(material["Position"], orientation)
            # Are you even supposed to do this to the normals?
            material["Normal"] = _reorient_coord_list(material["Normal"], orientation)
        return mesh
    return _reorienter


OUR_MANGLERS = [
    # Negate the X and Y axes on any mesh we upload or create temp
    reorient_mesh((-1, -2, 3)),
]


class MeshManglerExampleAddon(BaseAddon):
    def handle_init(self, session_manager: SessionManager):
        # Add our manglers into the list
        local_mesh_addon = local_mesh.MeshUploadInterceptingAddon
        local_mesh_addon.mesh_manglers.extend(OUR_MANGLERS)
        # Tell the local mesh plugin that the mangler list changed, and to re-apply
        local_mesh_addon.remangle_local_mesh(session_manager)

    def handle_unload(self, session_manager: SessionManager):
        # Clean up our manglers before we go away
        local_mesh_addon = local_mesh.MeshUploadInterceptingAddon
        mangler_list = local_mesh_addon.mesh_manglers
        for mangler in OUR_MANGLERS:
            if mangler in mangler_list:
                mangler_list.remove(mangler)
        local_mesh_addon.remangle_local_mesh(session_manager)


addons = [MeshManglerExampleAddon()]
