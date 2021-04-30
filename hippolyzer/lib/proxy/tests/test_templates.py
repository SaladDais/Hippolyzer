import unittest

import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.templates import TextureEntrySubfieldSerializer, TEFaceBitfield

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
                (3,): 'e7b29804-ca10-3b85-9405-4c6a8dd40b1f',
                (0,): '42cbe67c-1d2c-a773-63a6-1aa24cb17501'
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
        msg = ProxiedMessage.from_human_string(f"""
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
        msg = ProxiedMessage.from_human_string(msg.to_human_string(beautify=True))
        spec = msg["ObjectData"][0].get_serializer("TextureEntry")
        deser = spec.deserialize(None, msg["ObjectData"]["TextureEntry"], pod=True)
        self.assertEqual(deser, pod_te)


if __name__ == "__main__":
    unittest.main()
