# This currently implements basic LLMesh -> Collada.
#
# TODO:
#  * inverse, Collada -> LLMesh (for simple cases, maybe using impasse rather than pycollada)
#  * round-tripping tests, LLMesh->Collada->LLMesh
#  * * Can't really test using Collada->LLMesh->Collada because Collada->LLMesh is almost always
#      going to be lossy due to how SL represents vertex data and materials compared to what
#      Collada allows.
#  * Eventually scrap this and just use GLTF instead once we know we have the semantics correct
#  * * Collada was just easier to bootstrap given that it's the only officially supported input format
#  * * Collada tooling sucks and even LL is moving away from it
#  * * Ensuring LLMesh->Collada and LLMesh->GLTF conversion don't differ semantically is easy via assimp.

import logging
import os.path
import secrets
import sys
from typing import Dict, Optional

import collada
import collada.source
from collada import E
from lxml import etree
import numpy as np
import transformations

from hippolyzer.lib.base.helpers import get_resource_filename
from hippolyzer.lib.base.serialization import BufferReader
from hippolyzer.lib.base.mesh import (
    LLMeshSerializer,
    MeshAsset,
    positions_from_domain,
    SkinSegmentDict,
    llsd_to_mat4,
)

LOG = logging.getLogger(__name__)
DIR = os.path.dirname(os.path.realpath(__file__))


def mat4_to_collada(mat: np.ndarray) -> np.ndarray:
    return mat.flatten(order='C')


def mesh_to_collada(ll_mesh: MeshAsset, include_skin=True) -> collada.Collada:
    dae = collada.Collada()
    axis = collada.asset.UP_AXIS.Z_UP
    dae.assetInfo.upaxis = axis
    scene = collada.scene.Scene("scene", [llmesh_to_node(ll_mesh, dae, include_skin=include_skin)])

    dae.scenes.append(scene)
    dae.scene = scene
    return dae


def llmesh_to_node(ll_mesh: MeshAsset, dae: collada.Collada, uniq=None,
                   include_skin=True, node_transform: Optional[np.ndarray] = None) -> collada.scene.Node:
    if node_transform is None:
        node_transform = np.identity(4)

    should_skin = False
    skin_seg = ll_mesh.segments.get('skin')
    bind_shape_matrix = None
    if include_skin and skin_seg:
        bind_shape_matrix = llsd_to_mat4(skin_seg["bind_shape_matrix"])
        should_skin = True
        # Transform from the skin will be applied on the controller, not the node
        node_transform = np.identity(4)

    if not uniq:
        uniq = secrets.token_urlsafe(4)

    geom_nodes = []
    node_name = f"mainnode{uniq}"
    # TODO: do the other LODs?
    for submesh_num, submesh in enumerate(ll_mesh.segments["high_lod"]):
        # Make sure none of our IDs collide with those of other nodes
        sub_uniq = uniq + str(submesh_num)

        range_xyz = positions_from_domain(submesh["Position"], submesh["PositionDomain"])
        xyz = np.array([x.data() for x in range_xyz])

        range_uv = positions_from_domain(submesh['TexCoord0'], submesh['TexCoord0Domain'])
        uv = np.array([x.data() for x in range_uv]).flatten()

        norms = np.array([x.data() for x in submesh["Normal"]])

        effect = collada.material.Effect(
            id=f"effect{sub_uniq}",
            params=[],
            specular=(0.0, 0.0, 0.0, 0.0),
            reflectivity=(0.0, 0.0, 0.0, 0.0),
            emission=(0.0, 0.0, 0.0, 0.0),
            ambient=(0.0, 0.0, 0.0, 0.0),
            reflective=0.0,
            shadingtype="blinn",
            shininess=0.0,
            diffuse=(1.0, 1.0, 1.0),
        )
        mat = collada.material.Material(f"material{sub_uniq}", f"material{sub_uniq}", effect)

        dae.materials.append(mat)
        dae.effects.append(effect)

        vert_src = collada.source.FloatSource(f"verts-array{sub_uniq}", xyz.flatten(), ("X", "Y", "Z"))
        norm_src = collada.source.FloatSource(f"norms-array{sub_uniq}", norms.flatten(), ("X", "Y", "Z"))
        # UV maps have to have the same name or they'll behave weirdly when objects are merged.
        uv_src = collada.source.FloatSource("uvs-array", np.array(uv), ("U", "V"))

        geom = collada.geometry.Geometry(dae, f"geometry{sub_uniq}", "geometry", [vert_src, norm_src, uv_src])

        input_list = collada.source.InputList()
        input_list.addInput(0, 'VERTEX', f'#verts-array{sub_uniq}', set="0")
        input_list.addInput(0, 'NORMAL', f'#norms-array{sub_uniq}', set="0")
        input_list.addInput(0, 'TEXCOORD', '#uvs-array', set="0")

        tri_idxs = np.array(submesh["TriangleList"]).flatten()
        matnode = collada.scene.MaterialNode(f"materialref{sub_uniq}", mat, inputs=[])
        tri_set = geom.createTriangleSet(tri_idxs, input_list, f'materialref{sub_uniq}')
        geom.primitives.append(tri_set)
        dae.geometries.append(geom)

        if should_skin:
            joint_names = np.array(skin_seg['joint_names'], dtype=object)
            joints_source = collada.source.NameSource(f"joint-names{sub_uniq}", joint_names, ("JOINT",))
            # PyCollada has a bug where it doesn't set the source URI correctly. Fix it.
            accessor = joints_source.xmlnode.find(f"{dae.tag('technique_common')}/{dae.tag('accessor')}")
            if not accessor.get('source').startswith('#'):
                accessor.set('source', f"#{accessor.get('source')}")

            flattened_bind_poses = []
            for bind_pose in skin_seg['inverse_bind_matrix']:
                flattened_bind_poses.append(mat4_to_collada(llsd_to_mat4(bind_pose)))
            flattened_bind_poses = np.array(flattened_bind_poses)
            inv_bind_source = _create_mat4_source(f"bind-poses{sub_uniq}", flattened_bind_poses, "TRANSFORM")

            weight_joint_idxs = []
            weights = []
            vert_weight_counts = []
            cur_weight_idx = 0
            for vert_weights in submesh['Weights']:
                vert_weight_counts.append(len(vert_weights))
                for vert_weight in vert_weights:
                    weights.append(vert_weight.weight)
                    weight_joint_idxs.append(vert_weight.joint_idx)
                    weight_joint_idxs.append(cur_weight_idx)
                    cur_weight_idx += 1

            weights_source = collada.source.FloatSource(f"skin-weights{sub_uniq}", np.array(weights), ("WEIGHT",))
            # We need to make a controller for each material since materials are essentially distinct meshes
            # in SL, with their own distinct sets of weights and vertex data.
            controller_node = E.controller(
                E.skin(
                    E.bind_shape_matrix(' '.join(str(x) for x in mat4_to_collada(bind_shape_matrix))),
                    joints_source.xmlnode,
                    inv_bind_source.xmlnode,
                    weights_source.xmlnode,
                    E.joints(
                        E.input(semantic="JOINT", source=f"#joint-names{sub_uniq}"),
                        E.input(semantic="INV_BIND_MATRIX", source=f"#bind-poses{sub_uniq}")
                    ),
                    E.vertex_weights(
                        E.input(semantic="JOINT", source=f"#joint-names{sub_uniq}", offset="0"),
                        E.input(semantic="WEIGHT", source=f"#skin-weights{sub_uniq}", offset="1"),
                        E.vcount(' '.join(str(x) for x in vert_weight_counts)),
                        E.v(' '.join(str(x) for x in weight_joint_idxs)),
                        count=str(len(submesh['Weights']))
                    ),
                    source=f"#geometry{sub_uniq}"
                ),
                id=f"Armature-{sub_uniq}",
                name=node_name
            )
            controller = collada.controller.Controller.load(dae, {}, controller_node)
            dae.controllers.append(controller)
            geom_node = collada.scene.ControllerNode(controller, [matnode])
        else:
            geom_node = collada.scene.GeometryNode(geom, [matnode])

        geom_nodes.append(geom_node)

    node = collada.scene.Node(
        node_name,
        children=geom_nodes,
        transforms=[collada.scene.MatrixTransform(mat4_to_collada(node_transform))],
    )
    if should_skin:
        # We need a skeleton per _mesh asset_ because you could have incongruous skeletons
        # within the same linkset.
        # TODO: can we maintain some kind of skeleton cache, where if this skeleton has no conflicts
        #  with another skeleton in the cache, we just use that skeleton and add any additional joints?
        skel_root = load_skeleton_nodes()
        transform_skeleton(skel_root, dae, skin_seg)
        skel = collada.scene.Node.load(dae, skel_root, {})
        skel.children.append(node)
        skel.id = f"Skel-{uniq}"
        skel.save()
        node = skel
    return node


def load_skeleton_nodes() -> etree.ElementBase:
    # TODO: this sucks. Can't we construct nodes with the appropriate transformation
    #  matrices from the data in `avatar_skeleton.xml`?
    skel_path = get_resource_filename("lib/base/data/male_collada_joints.xml")
    with open(skel_path, 'r') as f:
        return etree.fromstring(f.read())


def transform_skeleton(skel_root: etree.ElementBase, dae: collada.Collada, skin_seg: SkinSegmentDict,
                       include_unreferenced_bones=False):
    """Update skeleton XML nodes to account for joint translations in the mesh"""
    joint_nodes: Dict[str, collada.scene.Node] = {}
    for skel_node in skel_root.iter():
        # xpath is loathsome so this is easier.
        if skel_node.tag != dae.tag('node') or skel_node.get('type') != 'JOINT':
            continue
        joint_nodes[skel_node.get('name')] = collada.scene.Node.load(dae, skel_node, {})
    for joint_name, matrix in zip(skin_seg['joint_names'], skin_seg.get('alt_inverse_bind_matrix', [])):
        joint_node = joint_nodes[joint_name]
        joint_decomp = transformations.decompose_matrix(llsd_to_mat4(matrix))
        joint_node.matrix = mat4_to_collada(transformations.compose_matrix(translate=joint_decomp[3]))
        # Update the underlying XML element with the new transform matrix
        joint_node.save()

    if not include_unreferenced_bones:
        needed_heirarchy = set()
        for skel_node in joint_nodes.values():
            skel_node = skel_node.xmlnode
            if skel_node.get('name') in skin_seg['joint_names']:
                # Add this joint and any ancestors the list of needed joints
                while skel_node is not None:
                    needed_heirarchy.add(skel_node.get('name'))
                    skel_node = skel_node.getparent()

        for skel_node in joint_nodes.values():
            skel_node = skel_node.xmlnode
            if skel_node.get('name') not in needed_heirarchy:
                skel_node.getparent().remove(skel_node)

    pelvis_offset = skin_seg.get('pelvis_offset')

    # TODO: should we even do this here? It's not present in the collada, just
    #  something that's specified in the uploader before conversion to LLMesh.
    if pelvis_offset and 'mPelvis' in joint_nodes:
        pelvis_node = joint_nodes['mPelvis']
        # Column-major!
        pelvis_node.matrix[3][2] += pelvis_offset
        pelvis_node.save()


def _create_mat4_source(name: str, data: np.ndarray, semantic: str):
    # PyCollada has no way to make a source with a float4x4 semantic. Do it a bad way.
    # Note that collada demands column-major matrices whereas LLSD mesh has them row-major!
    source = collada.source.FloatSource(name, data, tuple(f"M{x}" for x in range(16)))
    accessor = source.xmlnode[1][0]
    for child in list(accessor):
        accessor.remove(child)
    accessor.append(E.param(name=semantic, type="float4x4"))
    return source


def fix_weird_bind_matrices(skin_seg: SkinSegmentDict) -> None:
    """
    Fix weird-looking bind matrices to have sensible scaling and rotations

    Sometimes we get enormous inverse bind matrices (each component 10k+) and tiny
    bind shape matrix components. This detects inverse bind shape matrices
    with weird scales and tries to set them to what they "should" be without
    the weird inverted scaling.
    """

    # Sometimes we get mesh assets that have the vertex data naturally in y-up orientation,
    # and get re-oriented to z-up not through the bind shape matrix, but through the
    # transforms in the inverse bind matrices!
    #
    # Blender, for one, does not like this very much, and generally won't generate mesh
    # assets like this, as explained here https://developer.blender.org/T38660.
    # In vanilla Blender, these mesh assets will show up scaled and rotated _only_ according
    # to the bind shape matrix, which may end up with the model 25 meters tall and sitting
    # on its side.
    #
    # https://avalab.org/avastar/292/knowledge/compare-workbench/, while somewhat outdated,
    # has some information on rest pose vs default pose and scaling that I believe is relevant.
    # https://github.com/KhronosGroup/glTF-Blender-IO/issues/994 as well.
    #
    # While trying to figure out what was going on, I searched for something like
    # "inverse bind matrix scale collada", "bind pose scale blender", etc. Pretty much every
    # result was either a bug filed by, or a question asked by the creator of Avastar, or an SL user.
    # I think that says a lot about how annoying it is to author mesh for SL in particular.
    #
    # I spent a good month or so tearing my hair out over this wondering how these values could
    # even be possible. I wasn't sure how I should write mesh import code if I don't understand
    # how to interpret existing data, or how it even ended up the way it did. Turns out I wasn't
    # misinterpreting the data, the data really is just weird.
    #
    # I'd also had the idea that you could sniff which body a given rigged asset was meant
    # for by doing trivial matching on the inverse bind matrices, but obviously that isn't true!
    #
    # Basically:
    # 1) Maya is evil and generates evil, this evil bleeds into SL's assets through transforms.
    # 2) Blender is also evil, but in a manner that doesn't agree with Maya's evil.
    # 3) Collada was a valiant effort, but is evil in practice. Seemingly simple Collada
    #    files are interpreted completely differently by Blender, Maya, and sometimes SL.
    # 4) Those three evils collude to make an interop nightmare for everyone like "oh my rigger
    #    rigs using Maya and now my model is huge and all my normals are fucked on reimport"
    # 5) Yes, there's still good reasons to be using Avastar in 2022 even though nobody authoring
    #    rigged mesh for any other use has to use something similar.

    if not skin_seg['joint_names']:
        return

    # TODO: calculate the correct inverse bind matrix scale & rotations from avatar_skeleton.xml
    #  definitions. If the rotation and scale factors are the same across all inverse bind matrices then
    #  they can be moved over to the bind shape matrix to keep Blender happy.
    #  Maybe add a scaled / rotated empty as a parent for the armature instead?
    return


def main():
    # Take an llmesh file as an argument and spit out basename-converted.dae
    with open(sys.argv[1], "rb") as f:
        reader = BufferReader("<", f.read())

    mesh = mesh_to_collada(reader.read(LLMeshSerializer(parse_segment_contents=True)))
    mesh.write(sys.argv[1].rsplit(".", 1)[0] + "-converted.dae")


if __name__ == "__main__":
    main()
