"""
Example mesh mangler addon, to be used with local mesh addon.

You can edit this live to apply various transforms to local mesh.
If there are no live local mesh instances, the transforms will be
applied to the mesh before upload.

I personally use manglers to strip bounding box materials you need
to add to give a mesh an arbitrary center of rotation / scaling.
"""
from hippolyzer.lib.base.helpers import reorient_coord
from hippolyzer.lib.base.mesh import MeshAsset
from hippolyzer.lib.proxy.addons import AddonManager

import local_mesh
AddonManager.hot_reload(local_mesh, require_addons_loaded=True)


def _reorient_coord_list(coord_list, orientation, min_val: int | float = 0):
    return [reorient_coord(x, orientation, min_val) for x in coord_list]


def reorient_mesh(orientation):
    # Returns a callable that will change `mesh` to match `orientation`
    # X=1, Y=2, Z=3
    def _reorienter(mesh: MeshAsset):
        for material in mesh.iter_lod_materials():
            if "Position" not in material:
                # Must be a NoGeometry LOD
                continue
            # We don't need to use positions_(to/from)_domain here since we're just naively
            # flipping the axes around.
            material["Position"] = _reorient_coord_list(material["Position"], orientation)
            # Are you even supposed to do this to the normals?
            material["Normal"] = _reorient_coord_list(material["Normal"], orientation, min_val=-1)
        return mesh
    return _reorienter


class ExampleMeshManglerAddon(local_mesh.BaseMeshManglerAddon):
    MESH_MANGLERS = [
        # Negate the X and Y axes on any mesh we upload or create temp
        reorient_mesh((-1, -2, 3)),
    ]


addons = [ExampleMeshManglerAddon()]
