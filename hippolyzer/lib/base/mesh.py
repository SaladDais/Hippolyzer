"""
http://wiki.secondlife.com/wiki/Mesh/Mesh_Asset_Format
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import logging
from typing import *
import zlib
from copy import deepcopy

import numpy as np
import recordclass

from hippolyzer.lib.base import serialization as se
from hippolyzer.lib.base.datatypes import Vector3, Vector2, UUID, TupleCoord
from hippolyzer.lib.base.llsd import zip_llsd, unzip_llsd
from hippolyzer.lib.base.serialization import ParseContext

LOG = logging.getLogger(__name__)


def llsd_to_mat4(mat: Union[np.ndarray, Sequence[float]]) -> np.ndarray:
    return np.array(mat).reshape((4, 4), order='F')


def mat4_to_llsd(mat: np.ndarray) -> List[float]:
    return list(mat.flatten(order='F'))


@dataclasses.dataclass
class MeshAsset:
    header: MeshHeaderDict = dataclasses.field(default_factory=dict)
    segments: MeshSegmentDict = dataclasses.field(default_factory=dict)
    raw_segments: Dict[str, bytes] = dataclasses.field(default_factory=dict)

    @classmethod
    def make_triangle(cls) -> MeshAsset:
        """Make an asset representing an un-rigged single-sided mesh triangle"""
        inst = cls()
        inst.header = {
            "version": 1,
            "high_lod": {"offset": 0, "size": 0},
            "physics_mesh": {"offset": 0, "size": 0},
            "physics_convex": {"offset": 0, "size": 0},
        }
        base_lod: LODSegmentDict = {
            'Normal': [
                Vector3(-0.0, -0.0, -1.0),
                Vector3(-0.0, -0.0, -1.0),
                Vector3(-0.0, -0.0, -1.0)
            ],
            'PositionDomain': {'Max': [0.5, 0.5, 0.0], 'Min': [-0.5, -0.5, 0.0]},
            'Position': [
                Vector3(0.0, 0.0, 0.0),
                Vector3(1.0, 0.0, 0.0),
                Vector3(0.5, 1.0, 0.0)
            ],
            'TexCoord0Domain': {'Max': [1.0, 1.0], 'Min': [0.0, 0.0]},
            'TexCoord0': [
                Vector2(0.0, 0.0),
                Vector2(1.0, 0.0),
                Vector2(0.5, 1.0)
            ],
            'TriangleList': [[0, 1, 2]],
        }
        inst.segments['physics_mesh'] = [deepcopy(base_lod)]
        inst.segments['high_lod'] = [deepcopy(base_lod)]
        convex_segment: PhysicsConvexSegmentDict = {
            'BoundingVerts': [
                Vector3(-0.0, 1.0, -1.0),
                Vector3(-1.0, -1.0, -1.0),
                Vector3(1.0, -1.0, -1.0)
            ],
            'Max': [0.5, 0.5, 0.0],
            'Min': [-0.5, -0.5, 0.0]
        }
        inst.segments['physics_convex'] = convex_segment
        return inst

    def iter_lods(self) -> Generator[List[LODSegmentDict], None, None]:
        for lod_name, lod_val in self.segments.items():
            if lod_name.endswith("_lod"):
                yield lod_val

    def iter_lod_materials(self) -> Generator[LODSegmentDict, None, None]:
        for lods in self.iter_lods():
            yield from lods


# These TypedDicts describe the expected shape of the LLSD in the mesh
# header and various segments. They're mainly for type hinting.
class MeshHeaderDict(TypedDict, total=False):
    """Header of the mesh file, includes offsets & sizes for segments' LLSD"""
    version: int
    creator: UUID
    date: dt.datetime
    physics_cost_data: PhysicsCostDataHeaderDict
    high_lod: LODSegmentHeaderDict
    medium_lod: LODSegmentHeaderDict
    low_lod: LODSegmentHeaderDict
    lowest_lod: LODSegmentHeaderDict
    physics_convex: PhysicsSegmentHeaderDict
    physics_mesh: PhysicsSegmentHeaderDict
    skin: SegmentHeaderDict
    physics_havok: PhysicsHavokSegmentHeaderDict


class SegmentHeaderDict(TypedDict):
    """Standard shape for segment references within the header"""
    offset: int
    size: int


class LODSegmentHeaderDict(SegmentHeaderDict, total=False):
    # Possibly only on lowest?
    mesh_triangles: int


class PhysicsSegmentHeaderDict(SegmentHeaderDict, total=False):
    # Populated by the server, not there on the client
    hash: bytes


class PhysicsHavokSegmentHeaderDict(PhysicsSegmentHeaderDict, total=False):
    version: int


class PhysicsCostDataHeaderDict(TypedDict, total=False):
    """Cost of physical representation, populated by server"""
    decomposition: float
    decomposition_discounted_vertices: int
    decomposition_hulls: int
    hull: float
    hull_discounted_vertices: float
    # Not sure what this is, always seems to be 9 floats -1 to 1 if present
    # Mat3?
    mesh: List[float]
    mesh_triangles: int


class MeshSegmentDict(TypedDict, total=False):
    """Dict of segments unpacked using the MeshHeaderDict"""
    high_lod: List[LODSegmentDict]
    medium_lod: List[LODSegmentDict]
    low_lod: List[LODSegmentDict]
    lowest_lod: List[LODSegmentDict]
    physics_convex: PhysicsConvexSegmentDict
    physics_mesh: List[LODSegmentDict]
    physics_havok: PhysicsHavokSegmentDict
    skin: SkinSegmentDict


class LODSegmentDict(TypedDict, total=False):
    """Represents a single entry within the material list of a LOD segment"""
    # Only present if True and no geometry
    NoGeometry: bool
    # -1.0 - 1.0
    Position: List[Vector3]
    PositionDomain: DomainDict
    # 0.0 - 1.0
    TexCoord0: List[Vector2]
    TexCoord0Domain: DomainDict
    # -1.0 - 1.0
    Normal: List[Vector3]
    # [[1,2,3], [1,3,4], ...]
    TriangleList: List[List[int]]
    # Only present if rigged
    Weights: List[List[VertexWeight]]


class DomainDict(TypedDict):
    """Description of the real range for quantized coordinates"""
    # number of elems depends on what the domain is for, Vec2 or Vec3
    Max: List[float]
    Min: List[float]


class VertexWeight(recordclass.RecordClass):
    """Vertex weight for a specific joint on a specific vertex"""
    # index of the joint within the joint_names list in the skin segment
    joint_idx: int
    # 0.0 - 1.0
    weight: float


class SkinSegmentDict(TypedDict, total=False):
    """Rigging information"""
    joint_names: List[str]
    # model -> world transform mat4 for model
    bind_shape_matrix: List[float]
    # world -> joint local transform mat4s
    inverse_bind_matrix: List[List[float]]
    # Transform mat4s for the joint nodes themselves.
    # The matrices may have scale or other components, but only the
    # translation component will be used by the viewer.
    # All translations are relative to the joint's parent.
    alt_inverse_bind_matrix: List[List[float]]
    lock_scale_if_joint_position: bool
    pelvis_offset: float


class PhysicsConvexSegmentDict(DomainDict, total=False):
    """
    Data for convex hull collisions, populated by the client

    Min / Max pos domain vals are inline, unlike for LODs, so this inherits from DomainDict
    """
    # Indices into the Positions list
    HullList: List[int]
    # -1.0 - 1.0, dequantized from binary field of U16s
    Positions: List[Vector3]
    # -1.0 - 1.0, dequantized from binary field of U16s
    BoundingVerts: List[Vector3]


class PhysicsHavokSegmentDict(TypedDict, total=False):
    """Cached data for Havok collisions, populated by sim and not used by client."""
    HullMassProps: HavokMassPropsDict
    MOPP: HavokMOPPDict
    MeshDecompMassProps: HavokMassPropsDict
    WeldingData: bytes


class HavokMassPropsDict(TypedDict, total=False):
    # Vec, center of mass
    CoM: List[float]
    # 9 floats, Mat3?
    inertia: List[float]
    mass: float
    volume: float


class HavokMOPPDict(TypedDict, total=False):
    """Memory Optimized Partial Polytope"""
    BuildType: int
    MoppData: bytes
    # 4 floats, Vec4?
    MoppInfo: List[float]


def positions_from_domain(positions: Iterable[TupleCoord], domain: DomainDict):
    """
    Used for turning positions into their actual positions within the mesh / domain

    for ex: positions_from_domain(lod["Position"], lod["PositionDomain])
    """
    lower = domain['Min']
    upper = domain['Max']
    return [
        x.interpolate(lower, upper) for x in positions
    ]


def positions_to_domain(positions: Iterable[TupleCoord], domain: DomainDict):
    """Used for turning positions into their actual positions within the mesh / domain"""
    lower = domain['Min']
    upper = domain['Max']
    return [
        x.within_domain(lower, upper) for x in positions
    ]


class VertexWeights(se.SerializableBase):
    """Serializer for a list of joint weights on a single vertex"""
    INFLUENCE_LIMIT = 4
    INFLUENCE_TERM = 0xFF

    @classmethod
    def serialize(cls, vals, writer: se.BufferWriter, ctx=None):
        if len(vals) > cls.INFLUENCE_LIMIT:
            raise ValueError(f"{vals!r} is too long, can only have {cls.INFLUENCE_LIMIT} influences!")
        for val in vals:
            joint_idx, influence = val
            writer.write(se.U8, joint_idx)
            writer.write(se.U16, round(influence * 0xFFff), ctx=ctx)
        if len(vals) != cls.INFLUENCE_LIMIT:
            writer.write(se.U8, cls.INFLUENCE_TERM)

    @classmethod
    def deserialize(cls, reader: se.Reader, ctx=None):
        # NOTE: normally you'd want to do something like arrange this into a nicely
        # aligned byte array with zero padding so that you could vectorize the decoding.
        # In cases where having a vertex with no weights is semantically equivalent to
        # having a vertex _with_ weights of a value of 0.0 that's fine. This isn't the case
        # in LL's implementation of mesh:
        #
        # https://bitbucket.org/lindenlab/viewer/src/d31a83fb946c49a38376ea3b312b5380d0c8c065/indra/llmath/llvolume.cpp#lines-2560:2628
        #
        # Consider the difference between handling of b"\x00\x00\x00\xFF" and b"\xFF" with the above logic.
        # To simplify round-tripping while preserving those semantics, we don't do a vectorized decode.
        # I had a vectorized numpy version, but those requirements made everything a bit of a mess.
        influence_list = []
        for _ in range(cls.INFLUENCE_LIMIT):
            joint_idx = reader.read_bytes(1)[0]
            if joint_idx == cls.INFLUENCE_TERM:
                break
            weight = reader.read(se.U16, ctx=ctx) / 0xFFff
            influence_list.append(VertexWeight(joint_idx, weight))
        return influence_list


class SegmentSerializer:
    """Serializer for binary fields within an LLSD object"""
    def __init__(self, templates):
        self._templates: Dict[str, se.SerializableBase] = templates

    def serialize(self, vals: Dict[str, Any]):
        new_segment = {}
        for key, val in vals.items():
            if key in self._templates and not isinstance(val, bytes):
                # Pretty much everything in mesh segments is little-endian other
                # than the LLSD itself.
                writer = se.BufferWriter("<")
                writer.write(self._templates[key], val)
                new_segment[key] = writer.copy_buffer()
            else:
                new_segment[key] = val
        return new_segment

    def deserialize(self, vals: Dict[str, Any]):
        new_segment = {}
        for key, val in vals.items():
            if key in self._templates:
                reader = se.BufferReader("<", val)
                new_segment[key] = reader.read(self._templates[key])
                if len(reader):
                    LOG.warning(f"{len(reader)} bytes left in reader on mesh key {key}")
            else:
                new_segment[key] = val
        return new_segment


class VecListAdapter(se.Adapter):
    def __init__(self, child_spec: se.SERIALIZABLE_TYPE, vec_type: Type):
        super().__init__(child_spec)
        self.vec_type = vec_type

    def encode(self, val: Any, ctx: Optional[ParseContext]) -> Any:
        return val

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        new_vals = []
        for elem in val:
            new_vals.append(self.vec_type(*elem))
        return new_vals


LE_U16: np.dtype = np.dtype(np.uint16).newbyteorder('<')  # noqa


LOD_SEGMENT_SERIALIZER = SegmentSerializer({
    # 16-bit indices to the verts making up the tri. Imposes a 16-bit
    # upper limit on verts in any given material in the mesh.
    "TriangleList": se.ExprAdapter(
        se.NumPyArray(se.BytesGreedy(), LE_U16, 3),
        decode_func=lambda x: x.tolist(),
    ),
    # These are used to interpolate between values in their respective domains
    # Each position represents a single vert.
    "Position": VecListAdapter(
        se.QuantizedNumPyArray(se.NumPyArray(se.BytesGreedy(), LE_U16, 3), 0.0, 1.0),
        Vector3,
    ),
    "TexCoord0": VecListAdapter(
        se.QuantizedNumPyArray(se.NumPyArray(se.BytesGreedy(), LE_U16, 2), 0.0, 1.0),
        Vector2,
    ),
    # Normals have a static domain between -1 and 1, so we just use that rather than 0.0 - 1.0.
    "Normal": VecListAdapter(
        se.QuantizedNumPyArray(se.NumPyArray(se.BytesGreedy(), LE_U16, 3), -1.0, 1.0),
        Vector3,
    ),
    "Weights": se.Collection(None, VertexWeights)
})


class LLMeshSerializer(se.SerializableBase):
    # Also used as serialization order for segments.
    # Note that there's conflicting info about whether skin is supposed to
    # come first or not but the viewer always puts it second last, so we will too.
    KNOWN_SEGMENTS = ("lowest_lod", "low_lod", "medium_lod", "high_lod",
                      "physics_mesh", "physics_convex", "skin", "physics_havok")

    # Define unpackers for specific binary fields within the parsed LLSD segments
    SEGMENT_TEMPLATES: Dict[str, SegmentSerializer] = {
        "lowest_lod": LOD_SEGMENT_SERIALIZER,
        "low_lod": LOD_SEGMENT_SERIALIZER,
        "medium_lod": LOD_SEGMENT_SERIALIZER,
        "high_lod": LOD_SEGMENT_SERIALIZER,
        "physics_mesh": LOD_SEGMENT_SERIALIZER,
        "physics_convex": SegmentSerializer({
            "BoundingVerts": se.Collection(None, se.Vector3U16(-1.0, 1.0)),
            "HullList": se.Collection(None, se.U8),
            "Positions": se.Collection(None, se.Vector3U16(-1.0, 1.0)),
        }),
    }

    def __init__(
        self,
        parse_segment_contents: bool = True,
        allow_invalid_segments: bool = False,
        include_raw_segments: bool = False,
    ):
        super().__init__()
        self.parse_segment_contents = parse_segment_contents
        self.allow_invalid_segments = allow_invalid_segments
        self.include_raw_segments = include_raw_segments

    @classmethod
    def _segment_sort(cls, key):
        if key in cls.KNOWN_SEGMENTS:
            return cls.KNOWN_SEGMENTS.index(key)
        # If we don't know what this is chuck it to the end
        return 0xFFffFFff

    def _is_segment_header(self, val):
        if not isinstance(val, dict):
            return False
        if "offset" not in val:
            return False
        if "size" not in val:
            return False
        return True

    def serialize(self, val: MeshAsset, writer: se.BufferWriter, ctx=None):
        all_segs = set(val.segments.keys()) | set(val.raw_segments.keys())
        missing_headers = all_segs - set(val.header.keys())
        if missing_headers:
            raise ValueError(f"Segments missing from header dict: {missing_headers}")

        # We write the body first so we can get the offsets and sizes
        # for each segment for the header.
        inner_writer = se.BufferWriter(writer.endianness)
        # Don't mutate the original header
        new_header = deepcopy(val.header)

        # Write the segments in their preferred order
        for key in sorted(new_header.keys(), key=self._segment_sort):
            segment_header = new_header[key]  # type: ignore
            if not self._is_segment_header(segment_header):
                # Doesn't look like a segment header
                continue
            if key not in self.KNOWN_SEGMENTS:
                # Serialize anyway, it's all LLSD.
                LOG.warning(f"Serializing unknown mesh segment {key}")

            # Try segments first, then raw_segments
            segment_val = val.segments.get(key, val.raw_segments.get(key))  # type: ignore
            if segment_val is None:
                if self.allow_invalid_segments:
                    continue
                raise ValueError(f"{key} segment in header missing from segments dict")
            start_offset = len(inner_writer)

            # Write the segment, updating the header with the new offsets and sizes
            segment_header["offset"] = start_offset
            if isinstance(segment_val, bytes):
                inner_writer.write_bytes(segment_val)
            else:
                if key in self.SEGMENT_TEMPLATES:
                    if isinstance(segment_val, (list, tuple)):
                        segment_val = [self.SEGMENT_TEMPLATES[key].serialize(x) for x in segment_val]
                    else:
                        segment_val = self.SEGMENT_TEMPLATES[key].serialize(segment_val)  # type: ignore
                inner_writer.write_bytes(zip_llsd(segment_val))
            segment_header["size"] = len(inner_writer) - start_offset
        writer.write(se.BinaryLLSD, new_header, ctx=ctx)
        writer.write_bytes(inner_writer.buffer)

    def deserialize(self, reader: se.Reader, ctx=None):
        mesh = MeshAsset()
        mesh.header = reader.read(se.BinaryLLSD, ctx=ctx)
        header_end = reader.tell()
        bytes_after_header = len(reader)
        for key, segment_header in mesh.header.items():
            if not self._is_segment_header(segment_header):
                # Doesn't look like a segment header
                continue
            if key not in self.KNOWN_SEGMENTS:
                LOG.warning(f"Encountered unknown mesh segment on decode: {key}")
            if segment_header['offset'] + segment_header['size'] > bytes_after_header:
                err_msg = f"{segment_header!r} would pass EOF, refusing to parse"
                if self.allow_invalid_segments:
                    LOG.debug(err_msg)
                    continue
                else:
                    raise ValueError(err_msg)
            reader.seek(header_end + segment_header['offset'])
            seg_bytes = reader.read_bytes(segment_header['size'])

            if self.allow_invalid_segments and all(b == 0x00 for b in seg_bytes):
                LOG.debug("Encountered padding segment, skipping")
                continue
            try:
                segment_llsd = unzip_llsd(seg_bytes)
            except zlib.error:
                if self.allow_invalid_segments:
                    LOG.debug(f"Failed to parse segment bytes for {key}")
                    continue
                raise
            if self.parse_segment_contents and key in self.SEGMENT_TEMPLATES:
                if isinstance(segment_llsd, (list, tuple)):
                    segment_parsed = [self.SEGMENT_TEMPLATES[key].deserialize(x) for x in segment_llsd]
                else:
                    segment_parsed = self.SEGMENT_TEMPLATES[key].deserialize(segment_llsd)
            else:
                segment_parsed = segment_llsd
            mesh.segments[key] = segment_parsed  # type: ignore
            if self.include_raw_segments:
                mesh.raw_segments[key] = seg_bytes
        return mesh
