import unittest

import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message_formatting import HumanMessageSerializer
from hippolyzer.lib.base.templates import TextureEntrySubfieldSerializer, TEFaceBitfield, TextureEntry

EXAMPLE_TE = b"\x89UgG$\xcbC\xed\x92\x0bG\xca\xed\x15F_\x08\xe7\xb2\x98\x04\xca\x10;\x85\x94\x05Lj\x8d\xd4" \
             b"\x0b\x1f\x01B\xcb\xe6|\x1d,\xa7sc\xa6\x1a\xa2L\xb1u\x01\x00\x00\x00\x00\x00\x00\x00\x00\x80?" \
             b"\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
             b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"


class TemplateTests(unittest.TestCase):

    def test_te_round_trips(self):
        deserialized = TextureEntrySubfieldSerializer.deserialize(None, EXAMPLE_TE)
        serialized = TextureEntrySubfieldSerializer.serialize(None, deserialized)
        self.assertEqual(EXAMPLE_TE, serialized)

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
            'OffsetsS': {None: 0},
            'OffsetsT': {None: 0},
            'Rotation': {None: 0},
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
        deser = spec.deserialize(None, msg["ObjectData"]["TextureEntry"], pod=True)
        self.assertEqual(deser, pod_te)

    def test_textureentry_defaults(self):
        te = TextureEntry()
        self.assertEqual(UUID('89556747-24cb-43ed-920b-47caed15465f'), te.Textures[None])


if __name__ == "__main__":
    unittest.main()
