import os
import unittest

from hippolyzer.lib.base.mesh import LLMeshSerializer, MeshAsset
import hippolyzer.lib.base.serialization as se

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class TestMesh(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # Use a rigged cube SLM from the upload process as a test file
        slm_file = os.path.join(BASE_PATH, "test_resources", "testslm.slm")
        with open(slm_file, "rb") as f:
            cls.slm_bytes = f.read()

    def _get_test_mesh_reader(self):
        return se.BufferReader("!", self.slm_bytes)

    def _parse_test_mesh(self):
        reader = self._get_test_mesh_reader()
        mesh: MeshAsset = reader.read(LLMeshSerializer(parse_segment_contents=True))
        return mesh

    def test_basic(self):
        mesh = self._parse_test_mesh()
        self.assertEqual(mesh.header["lowest_lod"]["offset"], 211)
        self.assertSequenceEqual(mesh.segments["skin"]["joint_names"], ["mPelvis"])

    def test_round_trip(self):
        serializer = LLMeshSerializer()
        writer = se.BufferWriter("!")
        writer.write(serializer, self._parse_test_mesh())
        # Write it at least once on this machine in case the gzip impl changes
        first_buf = writer.copy_buffer()
        writer.clear()
        reader = se.BufferReader("!", first_buf)
        writer.write(serializer, reader.read(serializer))
        second_buf = writer.copy_buffer()
        self.assertEqual(first_buf, second_buf)
        # Dates may not round-trip correctly, but length should always be the same
        self.assertEqual(len(first_buf), len(self.slm_bytes))

    def test_serialize_raw_segments(self):
        serializer = LLMeshSerializer(include_raw_segments=True)
        reader = se.BufferReader("!", self.slm_bytes)
        mesh: MeshAsset = reader.read(serializer)
        mesh.raw_segments['high_lod'] += b"foobar"
        expected_high = mesh.raw_segments['high_lod']
        mesh.segments.pop("high_lod")
        writer = se.BufferWriter("!")
        writer.write(serializer, mesh)
        reader = se.BufferReader("!", writer.copy_buffer())
        mesh: MeshAsset = reader.read(serializer)
        self.assertEqual(mesh.raw_segments['high_lod'], expected_high)

    def test_iter_materials(self):
        mesh = self._parse_test_mesh()
        lod_list = list(mesh.iter_lods())
        self.assertEqual(4, len(lod_list))
        self.assertIsInstance(lod_list[0], list)
        mat_list = list(mesh.iter_lod_materials())
        self.assertEqual(4, len(mat_list))
        self.assertIsInstance(mat_list[0], dict)

    def test_make_default_triangle(self):
        tri = MeshAsset.make_triangle()
        self.assertEqual(0.5, tri.segments['high_lod'][0]['Position'][2].X)
        self.assertEqual(1, tri.header['version'])
