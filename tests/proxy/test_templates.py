import math
import unittest

import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base.datatypes import UUID, Vector3
from hippolyzer.lib.base.message.message_formatting import HumanMessageSerializer
from hippolyzer.lib.base.templates import TextureEntrySubfieldSerializer, TEFaceBitfield, TextureEntryCollection, \
    PackedTERotation, TextureEntry

EXAMPLE_TE = b'\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_\x08\xca*\x98:\x18\x02,\r\xf4\x1e\xc6\xf5\x91\x01]\x83\x014' \
             b'\x00\x90i+\x10\x80\xa1\xaa\xa2g\x11o\xa8]\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x80?' \
             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
             b'\x00\x00\x00\x00\x00\x00\x00'


class TemplateTests(unittest.TestCase):
    def test_te_round_trips(self):
        deserialized = TextureEntrySubfieldSerializer.deserialize(None, EXAMPLE_TE)
        serialized = TextureEntrySubfieldSerializer.serialize(None, deserialized)
        self.assertEqual(EXAMPLE_TE, serialized)

    def test_realize_te(self):
        deserialized: TextureEntryCollection = TextureEntrySubfieldSerializer.deserialize(None, EXAMPLE_TE)
        realized = deserialized.realize(4)
        self.assertEqual(UUID('ca2a983a-1802-2c0d-f41e-c6f591015d83'), realized[3].Textures)
        self.assertEqual(UUID('89556747-24cb-43ed-920b-47caed15465f'), realized[1].Textures)
        with self.assertRaises(ValueError):
            deserialized.realize(3)

    def test_tecollection_from_tes(self):
        deserialized: TextureEntryCollection = TextureEntrySubfieldSerializer.deserialize(None, EXAMPLE_TE)
        # The TE collection should re-serialize to the same collection when split up and regrouped
        self.assertEqual(deserialized, TextureEntryCollection.from_tes(deserialized.realize(4)))

    def test_face_bitfield_round_trips(self):
        test_val = b"\x81\x03"
        reader = se.BufferReader("!", test_val)
        deserialized = reader.read(TEFaceBitfield)

        writer = se.BufferWriter("!")
        writer.write(TEFaceBitfield, deserialized)
        self.assertEqual(writer.copy_buffer(), test_val)

    def test_can_use_templated_pod_message(self):
        pod_te = {
            'Textures': {
                None: '89556747-24cb-43ed-920b-47caed15465f',
                (3,): 'ca2a983a-1802-2c0d-f41e-c6f591015d83',
                (0,): '34009069-2b10-80a1-aaa2-67116fa85dc6'
            },
            'Color': {None: b'\xff\xff\xff\xff'},
            'ScalesS': {None: 1.0},
            'ScalesT': {None: 1.0},
            'OffsetsS': {None: 0.0},
            'OffsetsT': {None: 0.0},
            'Rotation': {None: 0.0},
            'BasicMaterials': {None: {'Bump': 0, 'FullBright': False, 'Shiny': 'OFF'}},
            'MediaFlags': {None: {'WebPage': False, 'TexGen': 'DEFAULT', '_Unused': 0}}, 'Glow': {None: 0},
            'Materials': {None: '00000000-0000-0000-0000-000000000000'},
        }
        msg = HumanMessageSerializer.from_human_string(f"""
        OUT ObjectImage
        [AgentData]
          AgentID = {UUID()}
          SessionID = {UUID()}
        [ObjectData]
          ObjectLocalID = 700966
          MediaURL = b''
          TextureEntry =| {repr(pod_te)}
        """)
        # Make sure from/to_human_string doesn't change meaning
        str_msg = HumanMessageSerializer.to_human_string(msg, beautify=True)
        msg = HumanMessageSerializer.from_human_string(str_msg)
        spec = msg["ObjectData"][0].get_serializer("TextureEntry")
        data_field = msg["ObjectData"]["TextureEntry"]
        # Serialization order and format should match indra's exactly
        self.assertEqual(EXAMPLE_TE, data_field)
        deser = spec.deserialize(None, data_field, pod=True)
        self.assertEqual(pod_te, deser)

    def test_textureentry_defaults(self):
        te = TextureEntryCollection()
        self.assertEqual(UUID('89556747-24cb-43ed-920b-47caed15465f'), te.Textures[None])

    def test_textureentry_rotation_packing(self):
        writer = se.BufferWriter("!")
        writer.write(PackedTERotation(), math.pi * 2)
        # fmod() makes this loop back around to 0
        self.assertEqual(b"\x00\x00", writer.copy_buffer())
        writer.clear()

        writer.write(PackedTERotation(), -math.pi * 2)
        # fmod() makes this loop back around to 0
        self.assertEqual(b"\x00\x00", writer.copy_buffer())
        writer.clear()

        writer.write(PackedTERotation(), 0)
        self.assertEqual(b"\x00\x00", writer.copy_buffer())
        writer.clear()

        # These both map to -32768 because of overflow in the positive case
        # that isn't caught by exact equality to math.pi * 2
        writer.write(PackedTERotation(), math.pi * 1.999999)
        self.assertEqual(b"\x80\x00", writer.copy_buffer())
        writer.clear()

        writer.write(PackedTERotation(), math.pi * -1.999999)
        self.assertEqual(b"\x80\x00", writer.copy_buffer())
        writer.clear()

    def test_textureentry_rotation_unpacking(self):
        reader = se.BufferReader("!", b"\x00\x00")
        self.assertEqual(0, reader.read(PackedTERotation()))

        reader = se.BufferReader("!", b"\x80\x00")
        self.assertEqual(-math.pi * 2, reader.read(PackedTERotation()))

        # This quantization method does not allow for any representation of
        # F_TWO_PI itself, just a value slightly below it! The float representation
        # is ever so slightly different from the C++ version, but it should still
        # round-trip correctly.
        reader = se.BufferReader("!", b"\x7f\xff")
        self.assertEqual(6.282993559581101, reader.read(PackedTERotation()))

        writer = se.BufferWriter("!")
        writer.write(PackedTERotation(), 6.282993559581101)
        self.assertEqual(b"\x7f\xff", writer.copy_buffer())

    def test_textureentry_st_to_uv_coords(self):
        te = TextureEntry(ScalesS=0.5, ScalesT=0.5, OffsetsS=-0.25, OffsetsT=0.25, Rotation=math.pi / 2)
        self.assertEqual(Vector3(0.25, 0.75), te.st_to_uv(Vector3(0.5, 0.5)))
