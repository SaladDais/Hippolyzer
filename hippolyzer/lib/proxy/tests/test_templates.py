import unittest

import hippolyzer.lib.base.serialization as se
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


if __name__ == "__main__":
    unittest.main()
