import dataclasses
import enum
import math
import unittest
import uuid
from io import BytesIO
from typing import Optional

import numpy as np

from hippolyzer.lib.base.datatypes import *
import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base.llanim import Animation, Joint, RotKeyframe
from hippolyzer.lib.base.namevalue import NameValuesSerializer, NameValueSerializer


class BaseSerializationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.writer = se.BufferWriter("!")

    def _get_reader(self, pod=False):
        return se.BufferReader(self.writer.endianness, self.writer.copy_buffer(), pod)

    def _assert_coords_fuzzy_equals(self, expected, val):
        if len(expected) != len(expected):
            # Take advantage of existing formatting, this will fail
            self.assertSequenceEqual(expected, val)
        for x, y in zip(expected, val):
            if not math.isclose(x, y, rel_tol=1e-4):
                self.assertSequenceEqual(expected, val)


class SerializationTests(BaseSerializationTest):
    def test_basic(self):
        self.writer.write(se.U32, 1)
        self.writer.write(se.U16, 2)
        reader = self._get_reader()
        self.assertEqual(reader.read(se.U32), 1)
        self.assertEqual(reader.read(se.U16), 2)
        # No more data left
        self.assertFalse(reader)

    def test_peeking(self):
        self.writer.write(se.U32, 1)
        reader = self._get_reader()
        self.assertEqual(reader.read(se.U32, peek=True), 1)
        self.assertEqual(reader.read(se.U32, peek=True), 1)
        # Should still be data left
        self.assertTrue(reader)

    def test_basic_collection(self):
        orig_list = [1, 2, 3, 4]
        coll = se.Collection(se.U8, se.U16)
        self.writer.write(coll, orig_list)
        reader = self._get_reader()
        self.assertListEqual(reader.read(coll), orig_list)
        self.assertFalse(reader)

    def test_greedy_collection(self):
        orig_list = [1, 2, 3, 4]
        coll = se.Collection(None, se.U16)
        self.writer.write(coll, orig_list)
        reader = self._get_reader()
        self.assertListEqual(reader.read(coll), orig_list)
        self.assertFalse(reader)

    def test_overly_large_collection_raises(self):
        orig_list = [1] * 300
        coll = se.Collection(se.U8, se.U16)
        with self.assertRaises(ValueError):
            self.writer.write(coll, orig_list)

    def test_strings(self):
        self.writer.write(se.Str(se.U8), "foobar")
        self.writer.write(se.Str(se.U16), "baz")
        reader = self._get_reader()
        self.assertEqual(reader.read(se.Str(se.U8)), "foobar")
        self.assertEqual(reader.read(se.Str(se.U16)), "baz")

    def test_prim_ranges(self):
        self.assertEqual(se.S32.max_val, 2147483647)
        self.assertEqual(se.S32.min_val, -2147483648)
        self.assertEqual(se.U32.max_val, 4294967295)
        self.assertEqual(se.U32.min_val, 0)
        self.assertEqual(se.S8.max_val, 127)
        self.assertEqual(se.S8.min_val, -128)

    def test_fixed_strings(self):
        spec = se.StrFixed(5)
        self.writer.write(spec, "foo")
        self.writer.write(spec, "quuxy")
        with self.assertRaises(ValueError):
            self.writer.write(spec, "verylong")
        reader = self._get_reader()
        self.assertEqual(reader.read(spec), "foo")
        self.assertEqual(reader.read(spec), "quuxy")

    def test_fixed(self):
        self.writer.write(se.BytesFixed(3), b"foo")
        with self.assertRaises(ValueError):
            self.writer.write(se.BytesFixed(3), b"foobar")
        reader = self._get_reader()
        self.assertEqual(reader.read(se.BytesFixed(3)), b"foo")

    def test_uuid(self):
        val = uuid.uuid4()
        self.writer.write(se.UUID, val)
        reader = self._get_reader()
        self.assertEqual(reader.read(se.UUID), val)

    def test_uuid_pod(self):
        val = uuid.uuid4()
        self.writer.write(se.UUID, val)
        reader = self._get_reader(pod=True)
        self.assertEqual(reader.read(se.UUID), str(val))

    def test_template(self):
        template = se.Template({
            "num_1": se.U64,
            "some_nums": se.Collection(se.U8, se.U16),
            "test_str": se.Str(se.U8),
        })

        vals = {
            "num_1": 2,
            "some_nums": [1, 4, 3],
            "test_str": "hi hello",
        }
        self.writer.write(template, vals)
        reader = self._get_reader()
        self.assertDictEqual(reader.read(template), vals)

    def test_cstr(self):
        self.writer.write(se.CStr(), "foobaz")
        self.writer.write(se.U8, 1)
        reader = self._get_reader()
        self.assertEqual(reader.read(se.CStr()), "foobaz")
        self.assertEqual(reader.read(se.U8), 1)

    def test_template_size(self):
        templ = se.Template({
            "foo": se.UUID,
            "bar": se.S32,
        })
        self.assertEqual(templ.calc_size(), 20)

    def test_enum_switch(self):
        class Foo(enum.IntEnum):
            STR = 0
            U16 = 1

        template = se.EnumSwitch(se.IntEnum(Foo, se.U8), {
            Foo.STR: se.CStr(),
            Foo.U16: se.U16,
        })

        self.writer.write(template, (Foo.STR, "foo"))
        self.writer.write(template, (Foo.U16, 12))
        reader = self._get_reader()
        self.assertSequenceEqual(reader.read(template), (Foo.STR, "foo"))
        self.assertSequenceEqual(reader.read(template), (Foo.U16, 12))

    def test_enum_switch_pod(self):
        class Foo(enum.IntEnum):
            STR = 0
            U16 = 1

        template = se.EnumSwitch(se.IntEnum(Foo, se.U8), {
            Foo.STR: se.CStr(),
            Foo.U16: se.U16,
        })

        self.writer.write(template, ("STR", "foo"))
        reader = self._get_reader(pod=True)
        self.assertSequenceEqual(reader.read(template), ("STR", "foo"))

    def test_flag_switch(self):
        class Foo(enum.IntFlag):
            STR = 1
            U16 = enum.auto()
            U32 = enum.auto()
            U64 = enum.auto()

        template = se.FlagSwitch(se.IntFlag(Foo, se.U8), {
            Foo.STR: se.CStr(),
            Foo.U16: se.U16,
            Foo.U32: se.U32,
            # U64 intentionally missing
        })

        expected = {
            Foo.STR: "barbaz",
            Foo.U32: 20000,
        }

        self.writer.write(template, expected)
        reader = self._get_reader()
        self.assertSequenceEqual(reader.read(template), expected)

    def test_flag_switch_pod(self):
        class Foo(enum.IntFlag):
            STR = 1
            U16 = enum.auto()
            U32 = enum.auto()
            U64 = enum.auto()

        template = se.FlagSwitch(se.IntFlag(Foo, se.U8), {
            Foo.STR: se.CStr(),
            Foo.U16: se.U16,
            Foo.U32: se.U32,
            # U64 intentionally missing
        })

        expected = {
            "STR": "barbaz",
            "U32": 20000,
        }

        self.writer.write(template, expected)
        reader = self._get_reader(pod=True)
        self.assertSequenceEqual(reader.read(template), expected)

    def test_length_switch(self):
        template = se.LengthSwitch({
            4: se.Collection(2, se.U16),
            2: se.U16,
        })

        self.writer.write(se.U16, 1)
        reader = self._get_reader()
        self.assertEqual(reader.read(template), TaggedUnion(2, 1))
        self.writer.write(se.U8, 0)
        reader = self._get_reader()
        with self.assertRaises(KeyError):
            reader.read(template)
        self.writer.write(se.U8, 2)
        reader = self._get_reader()
        self.assertSequenceEqual(reader.read(template), TaggedUnion(4, [1, 2]))

    def test_length_switch_catch_all(self):
        template = se.LengthSwitch({
            2: se.U16,
            None: se.Null
        })

        self.writer.write(se.U32, 1)
        read_template = self._get_reader().read(template)
        # Real length returned, but catchall template should be used for both read and write.
        self.assertEqual(read_template, TaggedUnion(4, None))
        self.writer.buffer.clear()
        self.writer.write(template, read_template)
        self.assertEqual(len(self.writer), 0)

    def test_tuple_coords(self):
        self.writer.write(se.Vector3D, (0.0, 1.0, 2.0))
        reader = self._get_reader()
        self.assertEqual(len(reader), 8 * 3)
        self._assert_coords_fuzzy_equals(reader.read(se.Vector3D()), (0.0, 1.0, 2.0))
        self.assertFalse(reader)

    def test_vector3_quat(self):
        expected = Quaternion(0.08283, 0.19996, -0.37361, 0.90198)
        self.writer.write(se.PackedQuat(se.Vector3), expected)
        reader = self._get_reader()
        self.assertEqual(len(reader), 4 * 3)
        self._assert_coords_fuzzy_equals(reader.read(se.PackedQuat(se.Vector3)), expected)
        self.assertFalse(reader)

    def test_vector3_quat_pod(self):
        expected = (0.08283, 0.19996, -0.37361, 0.90198)
        self.writer.write(se.PackedQuat(se.Vector3), expected)
        reader = self._get_reader(pod=True)
        self.assertEqual(len(reader), 4 * 3)
        self._assert_coords_fuzzy_equals(reader.read(se.PackedQuat(se.Vector3)), expected)
        self.assertFalse(reader)

    def test_int_enum(self):
        class Foo(enum.IntEnum):
            bar = 1
            baz = 2

        packed = se.IntEnum(Foo, se.U8, strict=False)
        self.writer.write(packed, "bar")
        # Allowed to write invalid enum vals
        self.writer.write(packed, 3)
        with self.assertRaises(KeyError):
            # Unknown lookup strs are bad though
            self.writer.write(packed, "quuxy")

        reader = self._get_reader()
        self.assertEqual(reader.read(packed), Foo.bar)
        # not strict, will return int for unrecognized
        self.assertEqual(reader.read(packed), 3)
        self.assertFalse(reader)

    def test_int_flag(self):
        class Foo(enum.IntFlag):
            bar = 1
            baz = enum.auto()
            quux = enum.auto()

        packed = se.IntFlag(Foo, se.U8)
        self.writer.write(packed, ("bar", "quux"))
        # Allowed to write invalid enum vals
        self.writer.write(packed, 3)
        with self.assertRaises(KeyError):
            # Unknown lookup strs are bad though
            self.writer.write(packed, ("quuxy",))

        reader = self._get_reader()
        self.assertEqual(reader.read(packed), Foo.bar | Foo.quux)
        self.assertEqual(reader.read(packed), Foo.bar | Foo.baz)
        self.assertFalse(reader)

    def test_int_flag_pod(self):
        class Foo(enum.IntFlag):
            bar = 1
            baz = 2
            quux = 4

        packed = se.IntFlag(Foo, se.U8)
        self.writer.write(packed, Foo.bar | Foo.quux | 8)
        reader = self._get_reader(pod=True)
        self.assertEqual(reader.read(packed), ("bar", "quux", 8))

    def test_bit_field(self):
        bitfield = se.BitField(se.U32, {"bar": 31, "foo": 1})
        expected = {"foo": 1, "bar": 2}
        self.writer.write(bitfield, expected)
        self.writer.write(se.U32, 2147483649)

        reader = self._get_reader()
        self.assertEqual(reader.read(bitfield), expected)
        self.assertEqual(reader.read(bitfield), {"foo": 1, "bar": 1})

    def test_bitfield_dataclass(self):
        class SomeEnum(enum.IntEnum):
            FOO = 0
            BAR = 1
            BAZ = 2

        @dataclasses.dataclass
        class SomeDataclass:
            some: SomeEnum = se.bitfield_field(bits=2, adapter=se.IntEnum(SomeEnum))
            number: int = se.bitfield_field(bits=30)

        bitfield = se.BitfieldDataclass(SomeDataclass, se.U32)

        expected = SomeDataclass(some=SomeEnum.BAR, number=200)
        self.writer.write(bitfield, expected)

        reader = self._get_reader()
        self.assertEqual(reader.read(bitfield), expected)

        # Now do the POD case
        self.writer.clear()
        self.writer.write(bitfield, expected)

        reader = self._get_reader(pod=True)
        self.assertEqual(reader.read(bitfield), {
            "some": "BAR",
            "number": 200,
        })

    def test_optional_prefixed(self):
        template = se.OptionalPrefixed(se.U8)
        self.writer.write(template, None)
        self.writer.write(template, 20)

        reader = self._get_reader()
        self.assertEqual(reader.read(template), None)
        self.assertEqual(reader.read(template), 20)

    def test_optional_flagged(self):
        class Foo(enum.IntFlag):
            STR = 1
            U16 = enum.auto()
            U32 = enum.auto()
            U64 = enum.auto()

        flag_spec = se.IntFlag(Foo, se.U8)
        template = se.Template({
            "Flags": flag_spec,
            "String1": se.OptionalFlagged("Flags", flag_spec, Foo.STR, se.CStr()),
            "Int1": se.OptionalFlagged("Flags", flag_spec, Foo.U16, se.U16),
            "Int2": se.OptionalFlagged("Flags", flag_spec, Foo.U32, se.U32),
            # U64 intentionally missing
        })

        val = {
            "Flags": Foo.STR | Foo.U16 | Foo.U64,
            "String1": "barbaz",
            "Int1": 20000,
        }

        self.writer.write(template, val)
        reader = self._get_reader()
        self.assertSequenceEqual(reader.read(template), {"Int2": None, **val})

    def test_optional_flagged_pod(self):
        class Foo(enum.IntFlag):
            STR = 1
            U16 = enum.auto()
            U32 = enum.auto()
            U64 = enum.auto()

        flag_spec = se.IntFlag(Foo, se.U8)
        template = se.Template({
            "Flags": flag_spec,
            "String1": se.OptionalFlagged("Flags", flag_spec, Foo.STR, se.CStr()),
            "Int1": se.OptionalFlagged("Flags", flag_spec, Foo.U16, se.U16),
            "Int2": se.OptionalFlagged("Flags", flag_spec, Foo.U32, se.U32),
            # U64 intentionally missing
        })

        val = {
            "Flags": ("STR", "U16", "U64"),
            "String1": "barbaz",
            "Int1": 20000,
        }

        self.writer.write(template, val)
        reader = self._get_reader(pod=True)
        self.assertSequenceEqual(reader.read(template), {"Int2": None, **val})

    def test_typed_bytearray(self):
        template = se.Template({
            "Int1": se.U32,
        })
        arr_template = se.TypedByteArray(se.U32, template)
        self.writer.write(arr_template, {"Int1": 1})
        # len field + int1
        self.assertEqual(len(self.writer), 8)
        self.assertEqual(self._get_reader().read(arr_template), {"Int1": 1})

        # trailing bytes left unparsed inside the array should fail
        self.writer.buffer.clear()
        self.writer.write(se.U32, 5)
        self.writer.write_bytes(b"x" * 5)
        with self.assertRaises(ValueError):
            print(self._get_reader().read(arr_template))

    def test_parse_context(self):
        test_self = self

        class Foo(se.SerializableBase):
            def __init__(self):
                self.ser_called = False
                self.deser_called = False

            def serialize(self, val, writer: se.BufferWriter, ctx: Optional[se.ParseContext]):
                test_self.assertEqual(ctx["bar"], 1)
                test_self.assertEqual(ctx._["plugh"], 2)
                self.ser_called = True

            def deserialize(self, reader: se.BufferReader, ctx: Optional[se.ParseContext]):
                test_self.assertEqual(ctx["bar"], 1)
                test_self.assertEqual(ctx._["plugh"], 2)
                self.deser_called = True

        foo_spec = Foo()
        template = se.Template({
            "plugh": se.U16,
            "quux": se.Template({
                "bar": se.U16,
                "baz": foo_spec,
            })
        })
        self.writer.write(template, {"plugh": 2, "quux": {"bar": 1, "baz": None}})
        self._get_reader().read(template)
        self.assertTrue(foo_spec.deser_called)
        self.assertTrue(foo_spec.ser_called)

    def test_multidict(self):
        test_list = [
            (1, 2),
            (1, 3),
            (4, 3),
            (1, 4),
        ]
        spec = se.Collection(se.U32, se.Tuple(se.U8, se.U32))
        multi_spec = se.MultiDictAdapter(spec)
        self.writer.write(spec, test_list)
        written_buff = self.writer.copy_buffer()
        reader = self._get_reader()
        deser = reader.read(multi_spec)
        item_view = deser.items(multi=True)
        for i in range(2):
            self.assertEqual(list(item_view), test_list)

        self.writer.clear()
        self.writer.write(multi_spec, deser)
        self.assertEqual(written_buff, self.writer.copy_buffer())

    def test_dataclass(self):
        @dataclasses.dataclass
        class Foobar:
            foo: int = se.dataclass_field(se.U8)
            bar: str = se.dataclass_field(se.CStr())

        spec = se.Dataclass(Foobar)
        inst = Foobar(foo=1, bar="log off")

        self.writer.write(spec, inst)
        reader = self._get_reader()
        deser: Foobar = reader.read(spec)
        self.assertEqual(inst, deser)
        self.assertEqual(deser.bar, "log off")


class FileSerializationTests(BaseSerializationTest):
    def _get_reader(self, pod=False):
        return se.FHReader(self.writer.endianness, BytesIO(self.writer.copy_buffer()), pod=pod)

    def test_simple(self):
        self.writer.write(se.CStr(), "foobar")
        self.writer.write(se.CStr(), "baz")
        reader = self._get_reader()
        self.assertEqual(reader.read(se.CStr()), "foobar")
        self.assertEqual(reader.read(se.CStr(), peek=True), "baz")
        self.assertTrue(reader)
        self.assertEqual(len(reader), 4)
        self.assertEqual(reader.read(se.CStr()), "baz")
        self.assertFalse(reader)


class QuantizedFloatSerializationTests(BaseSerializationTest):
    def _test_quantized_float_roundtrips(self, prim: se.SerializablePrimitive):
        test_ranges = [
            se.QuantizedFloat(prim, 0.0, 1.0),
            # Make sure we test the 0.0 median point special-casing
            se.QuantizedFloat(prim, -1.0, 1.0),
            # Lopsided, with zero in the middle-ish
            se.QuantizedFloat(prim, -2.0, 1.0),
        ]
        for packed in test_ranges:
            for i in range(prim.min_val, prim.max_val):
                self.writer.buffer = bytearray()
                self.writer.write(prim, i)
                initial_buf = self.writer.copy_buffer()
                reader = self._get_reader()
                first_read = reader.read(packed)
                self.writer.buffer.clear()
                self.writer.write(packed, first_read)
                self.assertEqual(initial_buf, self.writer.copy_buffer())

    def test_quantized_u8_roundtrips(self):
        self._test_quantized_float_roundtrips(se.U8)

    def test_quantized_s8_roundtrips(self):
        self._test_quantized_float_roundtrips(se.S8)

    @unittest.skip("expensive")
    def test_quantized_u16_roundtrips(self):
        self._test_quantized_float_roundtrips(se.U16)

    @unittest.skip("expensive")
    def test_quantized_s16_roundtrips(self):
        self._test_quantized_float_roundtrips(se.S16)

    def test_quantized_tuplecoords(self):
        packed = se.Vector3U16(-2.0, 2.0)
        self.writer.write(packed, (-2.0, 1.0, 2.0))
        self.writer.write(packed, (-2.0, 1.0, 1.0))
        reader = self._get_reader()
        self.assertEqual(len(reader), 2 * 6)
        self._assert_coords_fuzzy_equals(reader.read(packed), (-2.0, 1.0, 2.0))
        with self.assertRaises(AssertionError):
            self._assert_coords_fuzzy_equals(reader.read(packed), (-2.0, 1.0, 2.0))
        self.assertFalse(reader)

    def test_quantized_tuple_comes_through_zero(self):
        test_val = b"\x7f\xff\x7f\xff\x7f\xff"
        packed = se.Vector3U16(-64.0, 64.0)
        self.writer.write_bytes(test_val)
        reader = self._get_reader()
        first_read = reader.read(packed)
        self.assertEqual(first_read, Vector3(0, 0, 0))
        self.writer.buffer.clear()
        self.writer.write(packed, first_read)
        self.assertEqual(self.writer.copy_buffer(), test_val)

    def test_quantized_tuplecoords_component_scales(self):
        packed = se.Vector3U16(component_scales=(
            (0.0, 1.0),
            (0.0, 1.0),
            (0.0, 4096.0)
        ))
        self.writer.write(packed, (0.0, 1.0, 4095.0))
        reader = self._get_reader()
        self.assertEqual(len(reader), 6)
        self._assert_coords_fuzzy_equals(reader.read(packed), (0.0, 1.0, 4095.0))
        self.assertFalse(reader)

    def test_quantized_tuple_signed(self):
        class Vector3S16(se.QuantizedTupleCoord):
            ELEM_SPEC = se.S16
            NUM_ELEMS = 3
            COORD_CLS = Vector3

        vec_ser = Vector3S16(-2.0, 2.0)
        init_buf = b"\x80\x00\x00\x00\x7f\xff"
        self.writer.write_bytes(init_buf)
        reader = self._get_reader()
        self.assertEqual(len(reader), 6)
        unpacked = reader.read(vec_ser)
        self._assert_coords_fuzzy_equals(unpacked, (-2.0, 0.0, 2.0))
        self.assertFalse(reader)
        self.writer.buffer.clear()
        self.writer.write(vec_ser, unpacked)
        self.assertEqual(self.writer.copy_buffer(), init_buf)

    def test_quantized_extremes(self):
        spec = se.QuantizedFloat(se.S16, -2.0, 1.0)
        self.writer.write_bytes(b"\x80\x00\x7f\xff")
        reader = self._get_reader()
        self.assertEqual(-2.0, reader.read(spec))
        self.assertEqual(1.0, reader.read(spec))

    def test_fixed_point_tuplecoord(self):
        expected_bytes = b"\xff\x80\x00\x00\x7f\x7f"
        spec = se.FixedPointVector3U16(8, 7, signed=True)
        self.writer.write_bytes(expected_bytes)
        vec: Vector3 = self._get_reader().read(spec)
        self._assert_coords_fuzzy_equals(tuple(vec), (255.0, -256.0, -1.0078))
        self.writer.clear()
        self.writer.write(spec, vec)
        self.assertEqual(expected_bytes, self.writer.copy_buffer())


class NameValueSerializationTests(BaseSerializationTest):
    EXAMPLE_NAMEVALUES = 'DisplayName STRING RW DS 𝔲𝔫𝔦𝔠𝔬𝔡𝔢𝔫𝔞𝔪𝔢\n' \
                         'FirstName STRING RW DS firstname\n' \
                         'LastName STRING RW DS Resident\n' \
                         'Title STRING RW DS foo'.encode("utf8")

    def test_basic(self):
        val = self.EXAMPLE_NAMEVALUES
        self.writer.write_bytes(val)
        reader = self._get_reader(pod=False)
        deser = reader.read(NameValuesSerializer)

        self.assertEqual(deser.to_dict()['Title'], 'foo')
        self.assertEqual(deser.to_dict()['DisplayName'], '𝔲𝔫𝔦𝔠𝔬𝔡𝔢𝔫𝔞𝔪𝔢')

        self.writer.clear()
        self.writer.write(NameValuesSerializer, deser)
        self.assertEqual(val, self.writer.copy_buffer())

    def test_pod(self):
        val = self.EXAMPLE_NAMEVALUES
        self.writer.write_bytes(val)
        reader = self._get_reader(pod=True)
        deser = reader.read(NameValuesSerializer)

        self.assertEqual('Title STRING RW DS foo', deser[3])

        self.writer.clear()
        self.writer.write(NameValuesSerializer, deser)
        self.assertEqual(val, self.writer.copy_buffer())

    def test_namevalue_stringify(self):
        test_types = [
            b"Alpha STRING R S 'Twas brillig and the slighy toves/Did gyre and gimble in the wabe",
            b"Beta F32 R S 3.14159",
            b"Gamma S32 R S -12345",
            b"Delta VEC3 R S <1.2, -3.4, 5.6>",
            b"Epsilon U32 R S 12345",
            b"Zeta ASSET R S 041a8591-6f30-42f8-b9f7-7f281351f375",
            b"Eta U64 R S 9223372036854775807"
        ]

        for test in test_types:
            self.writer.clear()
            self.writer.write_bytes(test)
            reader = self._get_reader()
            self.assertEqual(test.decode("utf8"), str(reader.read(NameValueSerializer())))

    def test_namevalues_stringify(self):
        test_list = b"Alpha STRING R S 'Twas brillig and the slighy toves/Did gyre and gimble in the wabe\n" + \
                    b"Beta F32 R S 3.14159\n" + \
                    b"Gamma S32 R S -12345\n" + \
                    b"Delta VEC3 R S <1.2, -3.4, 5.6>\n" + \
                    b"Epsilon U32 R S 12345\n" + \
                    b"Zeta ASSET R S 041a8591-6f30-42f8-b9f7-7f281351f375\n" + \
                    b"Eta U64 R S 9223372036854775807"

        self.writer.clear()
        self.writer.write_bytes(test_list)
        reader = self._get_reader()
        deser = reader.read(NameValuesSerializer)
        self.assertEqual(test_list.decode("utf8"), str(deser))

        # Check that deserializer doesn't raise for any of the fields
        deser.to_dict()


class NumPySerializationTests(BaseSerializationTest):
    def setUp(self) -> None:
        super().setUp()
        self.writer.endianness = "<"

    def test_simple(self):
        quant_spec = se.Vector3U16(0.0, 1.0)
        self.writer.write(quant_spec, Vector3(0, 0.1, 0))
        self.writer.write(quant_spec, Vector3(1, 1, 1))

        reader = self._get_reader()
        np_spec = se.NumPyArray(se.BytesGreedy(), np.dtype(np.uint16), 3)
        np_val = reader.read(np_spec)
        expected_arr = np.array([[0, 6554, 0], [0xFFFF, 0xFFFF, 0xFFFF]], dtype=np.uint16)
        np.testing.assert_array_equal(expected_arr, np_val)

        # Make sure writing the array back works correctly
        orig_buf = self.writer.copy_buffer()
        self.writer.clear()
        self.writer.write(np_spec, expected_arr)
        self.assertEqual(orig_buf, self.writer.copy_buffer())

    def test_quantization(self):
        quant_spec = se.Vector3U16(0.0, 1.0)
        self.writer.write(quant_spec, Vector3(0, 0.1, 0))
        self.writer.write(quant_spec, Vector3(1, 1, 1))

        reader = self._get_reader()
        np_spec = se.QuantizedNumPyArray(se.NumPyArray(se.BytesGreedy(), np.dtype(np.uint16), 3), 0.0, 1.0)
        np_val = reader.read(np_spec)
        expected_arr = np.array([[0, 0.1, 0], [1, 1, 1]], dtype=np.float64)
        np.testing.assert_array_almost_equal(expected_arr, np_val, decimal=5)

        # Make sure writing the array back works correctly
        orig_buf = self.writer.copy_buffer()
        self.writer.clear()
        self.writer.write(np_spec, expected_arr)
        self.assertEqual(orig_buf, self.writer.copy_buffer())


class AnimSerializationTests(BaseSerializationTest):
    SIMPLE_ANIM = b'\x01\x00\x00\x00\x01\x00\x00\x00H\x11\xd1?\x00\x00\x00\x00\x00H\x11\xd1?\x00\x00\x00\x00' \
                  b'\xcd\xccL>\x9a\x99\x99>\x01\x00\x00\x00\x02\x00\x00\x00mNeck\x00\x01\x00\x00\x00\x03\x00' \
                  b'\x00\x00r\n\xff\x7f\xff\x7f\xff\x7f\xfa\xd0\xff\x7f\xff\x7f\xff\x7f\xff\xff\xff\x7f\xff' \
                  b'\x7f\xff\x7f\x00\x00\x00\x00mHead\x00\x01\x00\x00\x00\x14\x00\x00\x00r\n!\x84\xfbz\xab' \
                  b'\x81X\x1f?\x83\xed\x86\xbe\x82\xcb)\xfd\x81\xdc\x86\x08\x83>4\xf9\x7f\xfa~\x92\x82\xb1>' \
                  b'\xdb\x7f\x9d\x80H\x82$I\x82\x81\xad\x89M\x82\x97S\x01\x84\x98\x916\x82\n^L\x86\xfc\x919' \
                  b'\x82}h\xff\x86\xc4\x8c\x93\x82\xefr\x9c\x84\xd7\x85\xe3\x82b}\xb7\x7f\x90\x81\x96\x82\xd5' \
                  b'\x87\xa2~,\x84a\x82H\x92\xd7\x80w\x8aU\x82\xbb\x9c\xa7\x836\x8f4\x82.\xa7\xeb\x84\xa3\x8eX' \
                  b'\x82\xa1\xb1\x9b\x84\x80\x8a\xb6\x82\x14\xbc:\x83\xe8\x85\xf0\x82\x87\xc6^\x813\x83\xd1\x82' \
                  b'\xfa\xd0\xb7\x7f\x90\x81\x96\x82\xff\xff\xb7\x7f\x90\x81\x96\x82\x00\x00\x00\x00\x00\x00\x00\x00'

    def setUp(self) -> None:
        super().setUp()
        self.writer.endianness = "<"

    def test_basic(self):
        self.writer.write_bytes(self.SIMPLE_ANIM)
        spec = se.Dataclass(Animation)
        anim: Animation = self._get_reader().read(spec)
        self.assertEqual(len(anim.joints), 2)
        self.writer.clear()
        self.writer.write(spec, anim)
        self.assertEqual(self.SIMPLE_ANIM, self.writer.copy_buffer())

    def test_elided_fields_allowed(self):
        spec = se.Dataclass(Animation)
        # Should use the defaults for the unspecified fields
        anim = Animation(
            major_version=1,
            minor_version=0,
            base_priority=5,
            duration=1.0,
            loop_out_point=1.0,
        )
        self.assertIsNotNone(anim)
        self.assertEqual(len(anim.joints), 0)
        anim.joints["mPelvis"] = Joint(priority=5, rot_keyframes=[
            RotKeyframe(time=0.0, rot=Quaternion(0, 0, 0, 1))
        ])
        self.assertEqual(len(anim.joints), 1)
        self.writer.write(spec, anim)
        reader = self._get_reader()
        deser = reader.read(spec)
        self.assertEqual(anim, deser)

    def test_dict_context_allowed(self):
        spec = se.Dataclass(RotKeyframe)
        kf = RotKeyframe(time=0.0, rot=Quaternion())
        ctx = se.ParseContext({"major_version": 1, "minor_version": 0, "duration": 5.0})
        self.writer.write(spec, kf, ctx=ctx)
        # U16 for time, (x, y, z)
        self.assertEqual(se.U16.calc_size() * 4, len(self.writer))

        self.writer.clear()
        # Shouldn't need duration for v0.1
        ctx = se.ParseContext({"major_version": 0, "minor_version": 1})
        self.writer.write(spec, kf, ctx=ctx)
        # F32 for time, (x, y, z)
        self.assertEqual(se.F32.calc_size() * 4, len(self.writer))


class SubfieldSerializationTests(BaseSerializationTest):
    def test_enum(self):
        class FooEnum(enum.IntEnum):
            FOO = 1
            BAR = 2

        ser = se.IntEnumSubfieldSerializer(FooEnum)

        self.assertEqual(ser.deserialize(None, 1, pod=False), FooEnum.FOO)
        self.assertEqual(ser.deserialize(None, 1, pod=True), "FOO")
        self.assertEqual(ser.deserialize(None, 3, pod=True), se.UNSERIALIZABLE)
        self.assertEqual(ser.deserialize(None, 3, pod=False), 3)

        self.assertEqual(ser.serialize(None, "FOO"), 1)
        self.assertEqual(ser.serialize(None, FooEnum.FOO), 1)
        self.assertEqual(ser.serialize(None, 3), 3)

    def test_flags(self):
        class FooFlags(enum.IntFlag):
            FOO = 1
            BAR = 1 << 1

        ser = se.IntFlagSubfieldSerializer(FooFlags)

        self.assertEqual(ser.deserialize(None, 1, pod=False), FooFlags.FOO)
        self.assertEqual(ser.deserialize(None, 3, pod=False), FooFlags.FOO | FooFlags.BAR)
        self.assertEqual(ser.deserialize(None, 1, pod=True), ("FOO",))
        self.assertEqual(ser.deserialize(None, 3, pod=True), ("FOO", "BAR"))
        self.assertEqual(ser.deserialize(None, 7, pod=True), ("FOO", "BAR", 4))

        self.assertEqual(ser.serialize(None, ()), 0)
        self.assertEqual(ser.serialize(None, 0), 0)
        self.assertEqual(ser.serialize(None, ("FOO", "BAR")), 3)
        self.assertEqual(ser.serialize(None, FooFlags.FOO), 1)
        self.assertEqual(ser.serialize(None, 3), 3)
        self.assertEqual(ser.serialize(None, 7), 7)
