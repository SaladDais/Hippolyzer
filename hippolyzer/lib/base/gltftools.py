"""
WIP LLMesh -> glTF converter, for testing eventual glTF -> LLMesh conversion logic.
"""
# TODO:
#  * Simple tests
#  * Round-tripping skinning data from Blender-compatible glTF back to LLMesh (maybe through rig retargeting?)
#  * Panda3D-glTF viewer for LLMesh? The glTFs seem to work fine in Panda3D-glTF's `gltf-viewer`.
#  * Check if skew and projection components of transform matrices are ignored in practice as the spec requires.
#    I suppose this would render some real assets impossible to represent with glTF.

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

from hippolyzer.lib.base.datatypes import Vector3
from hippolyzer.lib.base.mesh import (
    LLMeshSerializer, MeshAsset, positions_from_domain, SkinSegmentDict, VertexWeight, llsd_to_mat4
)
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


def normalize_vec3(a):
    norm = np.linalg.norm(a)
    if norm == 0:
        return a
    return a / norm


def apply_bind_shape_matrix(bind_shape_matrix: np.ndarray, verts: np.ndarray, norms: np.ndarray) \
        -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply the bind shape matrix to the mesh data

    glTF expects all verts and normals to be in armature-local space so that mesh data can be shared
    between differently-oriented armatures. Or something.
    # https://github.com/KhronosGroup/glTF-Blender-IO/issues/566#issuecomment-523119339

    glTF also doesn't have a concept of a "bind shape matrix" like Collada does
    per its skinning docs, so we have to mix it into the mesh data manually.
    See https://github.com/KhronosGroup/glTF-Tutorials/blob/master/gltfTutorial/gltfTutorial_020_Skins.md
    """
    scale, _, angles, translation, _ = transformations.decompose_matrix(bind_shape_matrix)
    scale_mat = transformations.compose_matrix(scale=scale)[:3, :3]
    rot_mat = transformations.euler_matrix(*angles)[:3, :3]
    rot_scale_mat = scale_mat @ np.linalg.inv(rot_mat)

    # Apply the SRT transform to each vert
    verts = (verts @ rot_scale_mat) + translation

    # Our scale is unlikely to be uniform, so we have to fix up our normals as well.
    # https://paroj.github.io/gltut/Illumination/Tut09%20Normal%20Transformation.html
    inv_transpose_mat = np.transpose(np.linalg.inv(bind_shape_matrix)[:3, :3])
    new_norms = [normalize_vec3(inv_transpose_mat @ norm) for norm in norms]

    return verts, np.array(new_norms)


@dataclasses.dataclass
class JointContext:
    node: gltflib.Node
    # Original matrix for the bone, may have custom translation, but otherwise the same.
    orig_matrix: np.ndarray
    # xform that must be applied to inverse bind matrices to account for the changed bone
    fixup_matrix: np.ndarray


JOINT_CONTEXT_DICT = Dict[str, JointContext]


class GLTFBuilder:
    def __init__(self, blender_compatibility=False):
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
            extensionsUsed=["KHR_materials_specular"],
            scene=0,
        )
        self.gltf = gltflib.GLTF(
            model=self.model,
            resources=IdentityList(),
        )
        self.blender_compatibility = blender_compatibility

    def add_nodes_from_llmesh(self, mesh: MeshAsset, name: str, mesh_transform: Optional[np.ndarray] = None):
        """Build a glTF version of a mesh asset, appending it and its armature to the scene root"""
        # TODO: mesh data instancing?
        #  consider https://github.com/KhronosGroup/glTF-Blender-IO/issues/1634.
        if mesh_transform is None:
            mesh_transform = np.identity(4)

        skin_seg: Optional[SkinSegmentDict] = mesh.segments.get('skin')
        skin = None
        if skin_seg:
            mesh_transform = llsd_to_mat4(skin_seg['bind_shape_matrix'])
            joint_ctxs = self.add_joints(skin_seg)

            # Give our armature a root node and parent the pelvis to it
            armature_node = self.add_node("Armature")
            self.scene.nodes.append(self.model.nodes.index(armature_node))
            armature_node.children.append(self.model.nodes.index(joint_ctxs['mPelvis'].node))
            skin = self.add_skin("Armature", joint_ctxs, skin_seg)
            skin.skeleton = self.model.nodes.index(armature_node)

        primitives = []
        # Just the high LOD for now
        for submesh in mesh.segments['high_lod']:
            verts = np.array(positions_from_domain(submesh['Position'], submesh['PositionDomain']))
            norms = np.array(submesh['Normal'])
            tris = np.array(submesh['TriangleList'])
            joints = np.array([])
            weights = np.array([])
            range_uv = np.array([])
            if "TexCoord0" in submesh:
                range_uv = np.array(positions_from_domain(submesh['TexCoord0'], submesh['TexCoord0Domain']))
            if 'Weights' in submesh:
                joints, weights = sl_weights_to_gltf(submesh['Weights'])

            if skin:
                # Convert verts and norms to armature-local space
                verts, norms = apply_bind_shape_matrix(mesh_transform, verts, norms)

            primitives.append(self.add_primitive(
                tris=tris,
                positions=verts,
                normals=norms,
                uvs=range_uv,
                joints=joints,
                weights=weights,
            ))

        mesh_node = self.add_node(
            name,
            self.add_mesh(name, primitives),
            transform=mesh_transform,
        )
        if skin:
            # Node translation isn't relevant, we're going to use the bind matrices
            # If you pull this into Blender you may want to untick "Guess Original Bind Pose",
            # it guesses that based on the inverse bind matrices which may have Maya poisoning.
            # TODO: Maybe we could automatically undo that by comparing expected bone scale and rot
            #  to scale and rot in the inverse bind matrices, and applying fixups to the
            #  bind shape matrix and inverse bind matrices?
            mesh_node.matrix = None
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
            extensions={
                "KHR_materials_specular": {
                    "specularFactor": 0.0,
                    "specularColorFactor": [0, 0, 0]
                },
            }
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

    def add_joints(self, skin: SkinSegmentDict) -> JOINT_CONTEXT_DICT:
        # There may be some joints not present in the mesh that we need to add to reach the mPelvis root
        required_joints = set()
        for joint_name in skin['joint_names']:
            joint_node = AVATAR_SKELETON[joint_name]
            required_joints.add(joint_node)
            required_joints.update(joint_node.ancestors)

        # If this is present, it may override the joint positions from the skeleton definition
        if 'alt_inverse_bind_matrix' in skin:
            joint_overrides = dict(zip(skin['joint_names'], skin['alt_inverse_bind_matrix']))
        else:
            joint_overrides = {}

        built_joints: JOINT_CONTEXT_DICT = {}
        for joint in required_joints:
            joint_matrix = joint.matrix

            # Do we have a joint position override that would affect joint_matrix?
            override = joint_overrides.get(joint.name)
            if override:
                decomp = list(transformations.decompose_matrix(joint_matrix))
                # We specifically only want the translation from the override!
                translation = transformations.translation_from_matrix(llsd_to_mat4(override))
                # Only do it if the difference is over 0.1mm though
                if Vector3.dist(Vector3(*translation), joint.translation) > 0.0001:
                    decomp[3] = translation
                    joint_matrix = transformations.compose_matrix(*decomp)

            # Do we need to mess with the bone's matrices to make Blender cooperate?
            orig_matrix = joint_matrix
            fixup_matrix = np.identity(4)
            if self.blender_compatibility:
                joint_matrix, fixup_matrix = self._fix_blender_joint(joint_matrix)

            # TODO: populate "extras" here with the metadata the Blender collada stuff uses to store
            #  "bind_mat" and "rest_mat" so we can go back to our original matrices when exporting
            #  from blender to .dae!
            gltf_joint = self.add_node(joint.name, transform=joint_matrix)

            # Store the node along with any fixups we may need to apply to the bind matrices later
            built_joints[joint.name] = JointContext(gltf_joint, orig_matrix, fixup_matrix)

        # Add each joint to the child list of their respective parent
        for joint_name, joint_ctx in built_joints.items():
            if parent := AVATAR_SKELETON[joint_name].parent:
                built_joints[parent().name].node.children.append(self.model.nodes.index(joint_ctx.node))
        return built_joints

    def _fix_blender_joint(self, joint_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Split a joint matrix into a joint matrix and fixup matrix

        If we don't account for weird scaling on the collision volumes, then
        Blender freaks out. This is an issue in blender where it doesn't
        apply the inverse bind matrices relative to the scale and rotation of
        the bones themselves, as it should per the glTF spec. Blender's glTF loader
        tries to recover from this by applying certain transforms as a pose, but
        the damage has been done by that point. Nobody else runs really runs into
        this because they have the good sense to not use some nightmare abomination
        rig with scaling and rotation on the skeleton like SL does.

        Blender will _only_ correctly handle the translation component of the joint,
        any other transforms need to be mixed into the inverse bind matrices themselves.
        There's no internal concept of bone scale or rot in Blender right now.

        Should investigate an Avastar-style approach of optionally retargeting
        to a Blender-compatible rig with translation-only bones, and modify
        the bind matrices to accommodate. The glTF importer supports metadata through
        the "extras" fields, so we can potentially abuse the "bind_mat" metadata field
        that Blender already uses for the "Keep Bind Info" Collada import / export hack.

        For context:
        * https://github.com/KhronosGroup/glTF-Blender-IO/issues/1305
        * https://developer.blender.org/T38660 (these are Collada, but still relevant)
        * https://developer.blender.org/T29246
        * https://developer.blender.org/T50412
        * https://developer.blender.org/T53620 (FBX but still relevant)
        """
        scale, shear, angles, translate, projection = transformations.decompose_matrix(joint_matrix)
        joint_matrix = transformations.compose_matrix(translate=translate)
        fixup_matrix = transformations.compose_matrix(scale=scale, angles=angles)
        return joint_matrix, fixup_matrix

    def add_skin(self, name: str, joint_nodes: JOINT_CONTEXT_DICT, skin_seg: SkinSegmentDict) -> gltflib.Skin:
        joints_arr = []
        for joint_name in skin_seg['joint_names']:
            joint_ctx = joint_nodes[joint_name]
            joints_arr.append(self.model.nodes.index(joint_ctx.node))

        inv_binds = []
        for joint_name, inv_bind in zip(skin_seg['joint_names'], skin_seg['inverse_bind_matrix']):
            joint_ctx = joint_nodes[joint_name]
            inv_bind = joint_ctx.fixup_matrix @ llsd_to_mat4(inv_bind)
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

    builder = GLTFBuilder(blender_compatibility=True)
    builder.add_nodes_from_llmesh(mesh, filename)
    gltf = builder.finalize()

    pprint.pprint(gltf.model)
    gltf.export_glb(sys.argv[1].rsplit(".", 1)[0] + "-converted.gltf")


if __name__ == "__main__":
    main()
