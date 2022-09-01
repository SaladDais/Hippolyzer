"""
WIP LLMesh -> glTF converter, for testing eventual glTF -> LLMesh conversion logic.
"""
# TODO:
#  * Simple tests
#  * Make skinning actually work correctly
#  * * The weird scaling on the collision volumes / fitted mesh bones will clearly be a problem.
#      Blender's Collada importer / export stuff appears to sidestep these problems (by only applying
#      the bind shape matrix to the model in the viewport?)

import dataclasses
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
from hippolyzer.lib.base.mesh_skeleton import AVATAR_SKELETON
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
    # TODO: This is probably not correct. We definitely need to flip Z but there's
    #  probably a better way to do it.
    decomp = [sl_to_gltf_coords(x) for x in transformations.decompose_matrix(mat)]
    trans = decomp[3]
    decomp[3] = (trans[0], trans[1], -trans[2])
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
        # We need to re-normalize these since the quantization can mess them up
        collected_weights = []
        for j, vert_weight in enumerate(vert_weights):
            joints[i, j] = vert_weight.joint_idx
            collected_weights.append(vert_weight.weight)
        weight_sum = sum(collected_weights)
        if weight_sum:
            for j, weight in enumerate(collected_weights):
                weights[i, j] = weight / weight_sum

    return joints, weights


class GLTFBuilder:
    def __init__(self):
        self.scene = gltflib.Scene(nodes=IdentityList())
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

    def add_nodes_from_llmesh(self, mesh: MeshAsset, name: str, mesh_transform: Optional[np.ndarray] = None):
        """Build a glTF version of a mesh asset, appending it and its armature to the scene root"""
        # TODO: mesh data instancing?
        if mesh_transform is None:
            mesh_transform = np.identity(4)

        primitives = []
        # Just the high LOD for now
        for submesh in mesh.segments['high_lod']:
            range_xyz = np.array(positions_from_domain(submesh['Position'], submesh['PositionDomain']))
            norms = np.array(submesh['Normal'])
            tris = np.array(submesh['TriangleList'])
            joints = np.array([])
            weights = np.array([])
            range_uv = np.array([])
            if "TexCoord0" in submesh:
                range_uv = np.array(positions_from_domain(submesh['TexCoord0'], submesh['TexCoord0Domain']))
            if 'Weights' in submesh:
                joints, weights = sl_weights_to_gltf(submesh['Weights'])
            primitives.append(self.add_primitive(
                tris=tris,
                positions=range_xyz,
                normals=norms,
                uvs=range_uv,
                joints=joints,
                weights=weights,
            ))

        skin_seg: Optional[SkinSegmentDict] = mesh.segments.get('skin')
        skin = None
        if skin_seg:
            mesh_transform = llsd_to_mat4(skin_seg['bind_shape_matrix'])
            joint_nodes = self.add_joint_nodes(skin_seg)

            # Give our armature a root node and parent the pelvis to it
            armature_node = self.add_node("Armature")
            self.scene.nodes.append(self.model.nodes.index(armature_node))
            armature_node.children.append(self.model.nodes.index(joint_nodes['mPelvis']))
            skin = self.add_skin("Armature", joint_nodes, skin_seg)
            skin.skeleton = self.model.nodes.index(armature_node)

        mesh_node = self.add_node(
            name,
            self.add_mesh(name, primitives),
            transform=mesh_transform,
        )
        if skin and False:
            # Node translation isn't relevant, we're going to use the bind matrices
            mesh_node.matrix = None

            # TODO: This badly mangles up the mesh right now, especially given the
            #  collision volume scales. This is an issue in blender where it doesn't
            #  apply the inverse bind matrices relative to the scale and rotation of
            #  the bones themselves, as it should. Blender's glTF loader tries to recover
            #  from this by applying certain transforms as a pose, but the damage has
            #  been done by that point. Nobody else runs really runs into this because
            #  they have the good sense to not use some nightmare abomination rig with
            #  scaling and rotation on the skeleton like SL does.
            #
            #  I can't see any way to properly support this without changing how Blender
            #  handles armatures to make inverse bind matrices relative to bone scale and rot
            #  (which they probably won't and shouldn't do, since there's no internal concept
            #  of bone scale or rot in Blender right now.)
            #
            #  Should investigate an Avastar-style approach of optionally retargeting
            #  to a Blender-compatible rig with translation-only bones, and modify
            #  the bind matrices to accommodate. The glTF importer supports metadata through
            #  the "extras" fields, so we can potentially abuse the "bind_mat" metadata field
            #  that Blender already uses for the "Keep Bind Info" Collada import / export hack.
            mesh_node.skin = self.model.skins.index(skin)

        self.scene.nodes.append(self.model.nodes.index(mesh_node))

    def add_node(
            self,
            name: str,
            mesh: Optional[gltflib.Mesh] = None,
            transform: Optional[np.ndarray] = None,
    ) -> gltflib.Node:
        node = gltflib.Node(
            name=name,
            mesh=self.model.meshes.index(mesh) if mesh else None,
            matrix=sl_mat4_to_gltf(transform) if transform is not None else None,
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
        required_joints = AVATAR_SKELETON.get_required_joints(skin['joint_names'])
        # If this is present, it overrides the joint position from the skeleton definition
        if 'alt_inverse_bind_matrix' in skin:
            joint_overrides = dict(zip(skin['joint_names'], skin['alt_inverse_bind_matrix']))
        else:
            joint_overrides = {}

        for joint_name in required_joints:
            joint = AVATAR_SKELETON[joint_name]
            joint_matrix = joint.matrix
            override = joint_overrides.get(joint_name)
            decomp = list(transformations.decompose_matrix(joint_matrix))
            if override:
                # We specifically only want the translation from the override!
                decomp_override = transformations.decompose_matrix(llsd_to_mat4(override))
                decomp[3] = decomp_override[3]
                joint_matrix = transformations.compose_matrix(*decomp)
            node = self.add_node(joint_name, transform=joint_matrix)
            joints[joint_name] = node

        # Add each joint to the child list of their respective parents
        for joint_name, joint_node in joints.items():
            if parent := AVATAR_SKELETON[joint_name].parent:
                joints[parent().name].children.append(self.model.nodes.index(joint_node))
        return joints

    def add_skin(self, name: str, joint_nodes: Dict[str, gltflib.Node], skin_seg: SkinSegmentDict) -> gltflib.Skin:
        joints_arr = []
        for joint_name in skin_seg['joint_names']:
            joints_arr.append(self.model.nodes.index(joint_nodes[joint_name]))

        # glTF also doesn't have a concept of a "bind shape matrix" like Collada does
        # per its skinning docs, so we have to mix it into the inverse bind matrices.
        # See https://github.com/KhronosGroup/glTF-Tutorials/blob/master/gltfTutorial/gltfTutorial_020_Skins.md
        # TODO: apply the bind shape matrix to the mesh data instead?
        inv_binds = []
        bind_shape_matrix = llsd_to_mat4(skin_seg['bind_shape_matrix'])
        for joint_name, inv_bind in zip(skin_seg['joint_names'], skin_seg['inverse_bind_matrix']):
            inv_bind = np.matmul(llsd_to_mat4(inv_bind), bind_shape_matrix)
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

    def finalize(self):
        """Clean up the mesh to pass the glTF smell test, should be done last"""
        def _nullify_empty_lists(dc):
            for field in dataclasses.fields(dc):
                # Empty lists should be replaced with None
                if getattr(dc, field.name) == []:
                    setattr(dc, field.name, None)

        for node in self.model.nodes:
            _nullify_empty_lists(node)
        _nullify_empty_lists(self.model)
        return self.gltf


def main():
    # Take an llmesh file as an argument and spit out basename-converted.gltf
    with open(sys.argv[1], "rb") as f:
        reader = BufferReader("<", f.read())

    filename = Path(sys.argv[1]).stem
    mesh: MeshAsset = reader.read(LLMeshSerializer(parse_segment_contents=True))

    builder = GLTFBuilder()
    builder.add_nodes_from_llmesh(mesh, filename)
    gltf = builder.finalize()

    pprint.pprint(gltf.model)
    gltf.export_glb(sys.argv[1].rsplit(".", 1)[0] + "-converted.gltf")


if __name__ == "__main__":
    main()
