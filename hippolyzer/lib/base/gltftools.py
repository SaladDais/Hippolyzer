"""
WIP LLMesh -> glTF converter, for testing eventual glTF -> LLMesh conversion logic.
"""
# TODO:
#  * Simple tests
#  * Make skinning actually work correctly
#  * * The weird scaling on the collision volumes / fitted mesh bones will clearly be a problem.
#      Blender's Collada importer / export stuff appears to sidestep these problems (by only applying
#      the bind shape matrix to the model in the viewport?)
#  * Do we actually need to convert to GLTF coordinates space, or is it enough to parent everything
#    to a correctly rotated scene node? That would definitely be less nasty. I wasn't totally sure
#    how that would affect coordinates on re-exports if you did export selected without selecting the
#    scene root, though. This seems to be what assimp does so maybe it's fine?

import math
import pprint
import sys
import uuid
from pathlib import Path
from typing import *

import gltflib
import numpy as np
import transformations

from hippolyzer.lib.base.colladatools import llsd_to_mat4
from hippolyzer.lib.base.mesh import LLMeshSerializer, MeshAsset, positions_from_domain, SkinSegmentDict, VertexWeight
from hippolyzer.lib.base.mesh_skeleton import required_joint_hierarchy, SKELETON_JOINTS
from hippolyzer.lib.base.serialization import BufferReader


class IdentityList(list):
    """
    List, but does index() by object identity, not equality

    GLTF references objects by their index within some list, but we prefer to pass around
    actual object references internally. If we don't do this, then when we try and get
    a GLTF reference to a given object via `.index()` then we could end up actually getting
    a reference to some other object that just happens to be equal. This was causing issues
    with all primitives ending up with the same material, due to the default material's value
    being the same across all primitives.
    """
    def index(self, value, start: Optional[int] = None, stop: Optional[int] = None) -> int:
        view = self[start:stop]
        for i, x in enumerate(view):
            if x is value:
                if start:
                    return i + start
                return i
        raise ValueError(value)


def sl_to_gltf_coords(coords):
    """
    SL (X, Y, Z) -> GL (X, Z, Y), as GLTF commandeth

    Note that this will only work when reordering axes, flipping an axis is more complicated.
    """
    return coords[0], coords[2], coords[1], *coords[3:]


def sl_to_gltf_uv(uv):
    """Flip the V coordinate of a UV to match glTF convention"""
    return [uv[0], -uv[1]]


def sl_mat4_to_gltf(mat: np.ndarray) -> List[float]:
    """
    Convert an SL Mat4 to the glTF coordinate system

    This should only be done immediately before storing the matrix in a glTF structure!
    """
    decomp = [sl_to_gltf_coords(x) for x in transformations.decompose_matrix(mat)]
    return list(transformations.compose_matrix(*decomp).flatten(order='F'))


# Mat3 to convert points from SL coordinate space to GLTF coordinate space
POINT_TO_GLTF_MAT = transformations.compose_matrix(angles=(-(math.pi / 2), 0, 0))[:3, :3]


def sl_vec3_array_to_gltf(vec_list: np.ndarray) -> np.ndarray:
    new_array = []
    for x in vec_list:
        new_array.append(POINT_TO_GLTF_MAT.dot(x))
    return np.array(new_array)


def sl_weights_to_gltf(sl_weights: List[List[VertexWeight]]) -> Tuple[np.ndarray, np.ndarray]:
    """Convert SL Weights to separate JOINTS_0 and WEIGHTS_0 vec4 arrays"""
    joints = np.zeros((len(sl_weights), 4), dtype=np.uint8)
    weights = np.zeros((len(sl_weights), 4), dtype=np.float32)

    for i, vert_weights in enumerate(sl_weights):
        for j, vert_weight in enumerate(vert_weights):
            joints[i, j] = vert_weight.joint_idx
            weights[i, j] = vert_weight.weight

    return joints, weights


class GLTFBuilder:
    def __init__(self):
        self.scene = gltflib.Scene(nodes=[])
        self.model = gltflib.GLTFModel(
            asset=gltflib.Asset(version="2.0"),
            accessors=IdentityList(),
            nodes=IdentityList(),
            materials=IdentityList(),
            buffers=IdentityList(),
            bufferViews=IdentityList(),
            meshes=IdentityList(),
            skins=IdentityList(),
            scenes=IdentityList((self.scene,)),
            scene=0,
        )
        self.gltf = gltflib.GLTF(
            model=self.model,
            resources=IdentityList(),
        )

    def add_node(
            self,
            name: str,
            mesh: Optional[gltflib.Mesh] = None,
            transform: Optional[np.ndarray] = None,
    ) -> gltflib.Node:
        if transform is None:
            transform = np.identity(4)
        node = gltflib.Node(
            name=name,
            mesh=self.model.meshes.index(mesh) if mesh else None,
            matrix=sl_mat4_to_gltf(transform),
            children=[],
        )
        self.model.nodes.append(node)
        return node

    def add_mesh(
            self,
            name: str,
            primitives: List[gltflib.Primitive],
    ) -> gltflib.Mesh:
        for i, prim in enumerate(primitives):
            # Give the materials a name relating to what "face" they belong to
            self.model.materials[prim.material].name = f"{name}.{i:03}"
        mesh = gltflib.Mesh(name=name, primitives=primitives)
        self.model.meshes.append(mesh)
        return mesh

    def add_primitive(
            self,
            tris: np.ndarray,
            positions: np.ndarray,
            normals: np.ndarray,
            uvs: np.ndarray,
            weights: np.ndarray,
            joints: np.ndarray,
    ) -> gltflib.Primitive:
        # Make a Material for the primitive. Materials pretty much _are_ the primitives in
        # LLMesh, so just make them both in one go. We need a unique material for each primitive.
        material = gltflib.Material(
            pbrMetallicRoughness=gltflib.PBRMetallicRoughness(
                baseColorFactor=[1.0, 1.0, 1.0, 1.0],
                metallicFactor=0.0,
                roughnessFactor=0.0,
            ),
        )
        self.model.materials.append(material)

        attributes = gltflib.Attributes(
            POSITION=self.maybe_add_vec_array(sl_vec3_array_to_gltf(positions), gltflib.AccessorType.VEC3),
            NORMAL=self.maybe_add_vec_array(sl_vec3_array_to_gltf(normals), gltflib.AccessorType.VEC3),
            TEXCOORD_0=self.maybe_add_vec_array(np.array([sl_to_gltf_uv(uv) for uv in uvs]), gltflib.AccessorType.VEC2),
            JOINTS_0=self.maybe_add_vec_array(joints, gltflib.AccessorType.VEC4, gltflib.ComponentType.UNSIGNED_BYTE),
            WEIGHTS_0=self.maybe_add_vec_array(weights, gltflib.AccessorType.VEC4),
        )

        return gltflib.Primitive(
            attributes=attributes,
            indices=self.model.accessors.index(self.add_scalars(tris)),
            material=self.model.materials.index(material),
            mode=gltflib.PrimitiveMode.TRIANGLES,
        )

    def add_scalars(self, scalars: np.ndarray) -> gltflib.Accessor:
        """
        Add a potentially multidimensional array of scalars, returning the accessor

        Generally only used for triangle indices
        """
        scalar_bytes = scalars.astype(np.uint32).flatten().tobytes()
        buffer_view = self.add_buffer_view(scalar_bytes, None)
        accessor = gltflib.Accessor(
            bufferView=self.model.bufferViews.index(buffer_view),
            componentType=gltflib.ComponentType.UNSIGNED_INT,
            count=scalars.size,  # use the flattened size!
            type=gltflib.AccessorType.SCALAR.value,  # type: ignore
            min=[int(scalars.min())],  # type: ignore
            max=[int(scalars.max())],  # type: ignore
        )
        self.model.accessors.append(accessor)
        return accessor

    def maybe_add_vec_array(
            self,
            vecs: np.ndarray,
            vec_type: gltflib.AccessorType,
            component_type: gltflib.ComponentType = gltflib.ComponentType.FLOAT,
    ) -> Optional[int]:
        if not vecs.size:
            return None
        accessor = self.add_vec_array(vecs, vec_type, component_type)
        return self.model.accessors.index(accessor)

    def add_vec_array(
            self,
            vecs: np.ndarray,
            vec_type: gltflib.AccessorType,
            component_type: gltflib.ComponentType = gltflib.ComponentType.FLOAT
    ) -> gltflib.Accessor:
        """
        Add a two-dimensional array of vecs (positions, normals, weights, UVs) returning the accessor

        Vec type may be a vec2, vec3, or a vec4.
        """
        # Pretty much all of these are float32 except the ones that aren't
        dtype = np.float32
        if component_type == gltflib.ComponentType.UNSIGNED_BYTE:
            dtype = np.uint8
        vec_data = vecs.astype(dtype).tobytes()
        buffer_view = self.add_buffer_view(vec_data, target=None)
        accessor = gltflib.Accessor(
            bufferView=self.model.bufferViews.index(buffer_view),
            componentType=component_type,
            count=len(vecs),
            type=vec_type.value,  # type: ignore
            min=vecs.min(axis=0).tolist(),  # type: ignore
            max=vecs.max(axis=0).tolist(),  # type: ignore
        )
        self.model.accessors.append(accessor)
        return accessor

    def add_buffer_view(self, data: bytes, target: Optional[gltflib.BufferTarget]) -> gltflib.BufferView:
        """Create a buffer view and associated buffer and resource for a blob of data"""
        resource = gltflib.FileResource(filename=f"res-{uuid.uuid4()}.bin", data=data)
        self.gltf.resources.append(resource)

        buffer = gltflib.Buffer(uri=resource.filename, byteLength=len(resource.data))
        self.model.buffers.append(buffer)

        buffer_view = gltflib.BufferView(
            buffer=self.model.buffers.index(buffer),
            byteLength=buffer.byteLength,
            byteOffset=0,
            target=target
        )
        self.model.bufferViews.append(buffer_view)
        return buffer_view

    def add_joint_nodes(self, skin: SkinSegmentDict) -> Dict[str, gltflib.Node]:
        # TODO: Maybe this is smelly and we should instead just apply the chain's
        #  computed transform in the event of missing links along the way to root?
        #  It's not clear to me whether this will cause problems with mesh assets
        #  that expect to be able to reorient the entire mesh through the
        #  inverse bind matrices.
        joints: Dict[str, gltflib.Node] = {}
        required_joints = required_joint_hierarchy(skin['joint_names'])
        # If this is present, it overrides the joint position from the skeleton definition
        if 'alt_inverse_bind_matrix' in skin:
            joint_overrides = dict(zip(skin['joint_names'], skin['alt_inverse_bind_matrix']))
        else:
            joint_overrides = {}

        for joint_name in required_joints:
            joint_pos = SKELETON_JOINTS[joint_name].translation
            override = joint_overrides.get(joint_name)
            if override:
                # We specifically only want the translation from the override!
                joint_pos = transformations.translation_from_matrix(llsd_to_mat4(override))
            node = self.add_node(joint_name, transform=transformations.compose_matrix(translate=tuple(joint_pos)))
            joints[joint_name] = node

        # Add each joint to the child list of their respective parents
        for joint_name, joint_node in joints.items():
            parent_name = SKELETON_JOINTS[joint_name].parent
            if parent_name:
                joints[parent_name].children.append(self.model.nodes.index(joint_node))
        return joints

    def add_skin(self, name: str, joint_nodes: Dict[str, gltflib.Node], skin_seg: SkinSegmentDict) -> gltflib.Skin:
        joints_arr = []
        for joint_name in skin_seg['joint_names']:
            joints_arr.append(self.model.nodes.index(joint_nodes[joint_name]))

        # TODO: glTF also doesn't have a concept of a "bind shape matrix" per its skinning docs,
        #  so we may have to mix that into the mesh data or inverse bind matrices somehow.
        inv_binds = []
        for inv_bind in skin_seg['inverse_bind_matrix']:
            inv_bind = llsd_to_mat4(inv_bind)
            inv_binds.append(sl_mat4_to_gltf(inv_bind))
        inv_binds_data = np.array(inv_binds, dtype=np.float32).tobytes()
        buffer_view = self.add_buffer_view(inv_binds_data, target=None)
        accessor = gltflib.Accessor(
            bufferView=self.model.bufferViews.index(buffer_view),
            componentType=gltflib.ComponentType.FLOAT,
            count=len(inv_binds),
            type=gltflib.AccessorType.MAT4.value,  # type: ignore
        )
        self.model.accessors.append(accessor)
        accessor_idx = self.model.accessors.index(accessor)

        skin = gltflib.Skin(name=name, joints=joints_arr, inverseBindMatrices=accessor_idx)
        self.model.skins.append(skin)
        return skin


def build_gltf_mesh(builder: GLTFBuilder, mesh: MeshAsset, name: str):
    """Build a glTF version of a mesh, appending it and its armature to the scene root"""
    gltf_model = builder.model
    # Just the high LOD for now
    high_lod = mesh.segments['high_lod']
    primitives = []
    for submesh in high_lod:
        range_xyz = np.array(positions_from_domain(submesh['Position'], submesh['PositionDomain']))
        range_uv = np.array(positions_from_domain(submesh['TexCoord0'], submesh['TexCoord0Domain']))
        norms = np.array(submesh['Normal'])
        tris = np.array(submesh['TriangleList'])
        joints = np.array([])
        weights = np.array([])
        if 'Weights' in submesh:
            joints, weights = sl_weights_to_gltf(submesh['Weights'])
        primitives.append(builder.add_primitive(
            tris=tris,
            positions=range_xyz,
            normals=norms,
            uvs=range_uv,
            joints=joints,
            weights=weights,
        ))

    skin_seg: Optional[SkinSegmentDict] = mesh.segments.get('skin')
    skin = None
    armature_node = None
    mesh_transform = np.identity(4)
    if skin_seg:
        mesh_transform = llsd_to_mat4(skin_seg['bind_shape_matrix'])
        joint_nodes = builder.add_joint_nodes(skin_seg)

        # Give our armature a root node and parent the pelvis to it
        armature_node = builder.add_node("Armature")
        builder.scene.nodes.append(gltf_model.nodes.index(armature_node))
        armature_node.children.append(gltf_model.nodes.index(joint_nodes['mPelvis']))
        skin = builder.add_skin("Armature", joint_nodes, skin_seg)

    mesh_node = builder.add_node(
        name,
        builder.add_mesh(name, primitives),
        transform=mesh_transform,
    )
    if skin and False:
        # TODO: This badly mangles up the mesh right now, especially given the
        #  collision volume scales. Investigate using a more accurate skeleton def.
        mesh_node.skin = gltf_model.skins.index(skin)
        armature_node.children.append(gltf_model.nodes.index(mesh_node))
        builder.scene.nodes.append(gltf_model.nodes.index(armature_node))
    else:
        # Add a root node that will re-orient our scene into GLTF coords.
        # scene_node = builder.add_node("scene")
        # scene_node.children.append(gltf_model.nodes.index(mesh_node))
        builder.scene.nodes.append(gltf_model.nodes.index(mesh_node))


def main():
    # Take an llmesh file as an argument and spit out basename-converted.gltf
    with open(sys.argv[1], "rb") as f:
        reader = BufferReader("<", f.read())

    filename = Path(sys.argv[1]).stem
    mesh: MeshAsset = reader.read(LLMeshSerializer(parse_segment_contents=True))

    builder = GLTFBuilder()
    build_gltf_mesh(builder, mesh, filename)

    pprint.pprint(builder.model)
    builder.gltf.export_glb(sys.argv[1].rsplit(".", 1)[0] + "-converted.gltf")


if __name__ == "__main__":
    main()
