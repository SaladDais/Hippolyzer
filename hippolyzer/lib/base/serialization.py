import abc
import contextlib
import dataclasses
import enum
import math
import struct
import types
import weakref
from io import SEEK_CUR, SEEK_SET, SEEK_END, RawIOBase, BufferedIOBase
from typing import *

import lazy_object_proxy

import hippolyzer.lib.base.llsd as llsd
import hippolyzer.lib.base.datatypes as dtypes
import hippolyzer.lib.base.helpers as helpers
from hippolyzer.lib.base.multidict import OrderedMultiDict


SERIALIZABLE_TYPE = Union["SerializableBase", Type["SerializableBase"]]
SUBFIELD_SERIALIZERS: Dict[Tuple[str, str, str], "BaseSubfieldSerializer"] = {}
HTTP_SERIALIZERS: Dict[str, "BaseHTTPSerializer"] = {}


class _Unserializable:
    def __bool__(self):
        return False


UNSERIALIZABLE = _Unserializable()
_T = TypeVar("_T")


class ParseContext:
    def __init__(self, wrapped: Sequence, parent=None):
        # Allow walking up a level inside serializers
        self._: "ParseContext" = weakref.proxy(parent) if parent is not None else None
        self._wrapped = wrapped

    @property
    def _root(self):
        obj = self._
        while obj._ is not None:
            obj = obj._
        return obj

    def __getitem__(self, item):
        return self._wrapped[item]

    def __getattr__(self, item):
        try:
            return getattr(self._wrapped, item)
        except AttributeError:
            try:
                return self._wrapped[item]
            except:
                pass
            raise

    def __len__(self):
        return len(self._wrapped)

    def __bool__(self):
        return bool(self._wrapped)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._wrapped!r}, parent={self._!r})"


class BufferWriter:
    __slots__ = ("endianness", "buffer")

    def __init__(self, endianness, buffer=None):
        self.endianness = endianness
        self.buffer = buffer or bytearray()

    def __len__(self):
        return len(self.buffer)

    def __bool__(self):
        return len(self) > 0

    def write(self, ser_type: SERIALIZABLE_TYPE, val, ctx=None):
        # Mainly exists because `writer.write(type, val)` reads nicer than
        # `type.serialize(val, writer)`.
        ser_type.serialize(val, self, ctx=ctx)

    def write_bytes(self, val):
        self.buffer.extend(val)

    def clear(self):
        self.buffer.clear()

    def copy_buffer(self):
        return bytes(self.buffer)

    @contextlib.contextmanager
    def enter_member(self, member_id):
        # no-op, subclasses can override this to keep track of where they are
        # in the template hierarchy
        yield


class MemberTrackingBufferWriter(BufferWriter):
    def __init__(self, endianness, buffer=None):
        super().__init__(endianness, buffer)
        self.member_stack = []
        self.member_positions = []

    def clear(self):
        super().clear()
        self.member_stack = []
        self.member_positions = []

    @contextlib.contextmanager
    def enter_member(self, member_id):
        self.member_stack.append(member_id)
        self.member_positions.append((len(self), tuple(self.member_stack)))
        try:
            yield
        finally:
            self.member_stack.pop()


class Reader(abc.ABC):
    __slots__ = ("endianness", "pod")

    seekable: bool

    def __init__(self, endianness, pod=False):
        self.endianness = endianness
        self.pod = pod

    @abc.abstractmethod
    def __bool__(self):
        """Whether there's any data left in the reader"""
        raise NotImplementedError()

    @abc.abstractmethod
    def __len__(self) -> int:
        """Number of bytes left in the reader"""
        raise NotImplementedError()

    @abc.abstractmethod
    def tell(self) -> int:
        """Position within the reader"""
        raise NotImplementedError()

    @abc.abstractmethod
    def seek(self, pos: int, whence: int = SEEK_SET):
        raise NotImplementedError()

    @contextlib.contextmanager
    def scoped_seek(self, pos: int, whence: int = SEEK_SET):
        old_pos = self.tell()
        try:
            self.seek(pos=pos, whence=whence)
            yield
        finally:
            self.seek(old_pos)

    @contextlib.contextmanager
    def scoped_pod(self, pod: bool):
        old_pod = self.pod
        try:
            self.pod = pod
            yield
        finally:
            self.pod = old_pod

    def read(self, ser_type: SERIALIZABLE_TYPE, ctx=None, peek=False):
        if peek:
            with self.scoped_seek(pos=0, whence=SEEK_CUR):
                return ser_type.deserialize(self, ctx)

        return ser_type.deserialize(self, ctx)

    @abc.abstractmethod
    def read_bytes(self, num_bytes, peek=False, to_bytes=False, check_len=True):
        raise NotImplementedError()


class BufferReader(Reader):
    __slots__ = ("_buffer", "_pos", "_len")

    seekable: bool = True

    def __init__(self, endianness, buffer, pod=False):
        super().__init__(endianness, pod)
        self._buffer = buffer
        self._pos = 0
        self._len = len(buffer)

    def __bool__(self):
        return self._len > self._pos

    def __len__(self):
        return self._len - self._pos

    def tell(self) -> int:
        return self._pos

    def seek(self, pos: int, whence: int = SEEK_SET):
        if whence == SEEK_CUR:
            new_pos = self._pos + pos
        elif whence == SEEK_END:
            new_pos = self._len + pos
        else:
            new_pos = pos

        if new_pos > self._len or new_pos < 0:
            raise IOError(f"Tried to seek to {new_pos} in buffer of {self._len} bytes")
        self._pos = new_pos

    def read_bytes(self, num_bytes, peek=False, to_bytes=False, check_len=True):
        end_pos = self._pos + num_bytes
        if end_pos > self._len and check_len:
            raise ValueError(f"{len(self)} bytes left, needed {num_bytes}")

        read_bytes = self._buffer[self._pos:end_pos]
        if to_bytes:
            read_bytes = bytes(read_bytes)
        if not peek:
            self._pos = end_pos
        return read_bytes


class FHReader(Reader):
    __slots__ = ("fh",)

    def __init__(self, endianness, fh, pod=False):
        super().__init__(endianness, pod)
        self.fh: Union[RawIOBase, BufferedIOBase] = fh

    @property
    def seekable(self):
        return self.fh.seekable()

    def __bool__(self):
        # If this is a pipe or something we won't be able to seek.
        # Just assume there's always data left.
        if not self.seekable:
            return True
        return len(self) > 0

    def __len__(self) -> int:
        cur_pos = self.tell()
        with self.scoped_seek(0, whence=SEEK_END):
            return self.tell() - cur_pos

    def tell(self) -> int:
        return self.fh.tell()

    def seek(self, pos: int, whence: int = SEEK_SET):
        self.fh.seek(pos, whence)

    def read_bytes(self, num_bytes, peek=False, to_bytes=False, check_len=True):
        if peek:
            with self.scoped_seek(0, whence=SEEK_CUR):
                return self.fh.read(num_bytes)
        return self.fh.read(num_bytes)


class SerializableBase(abc.ABC):
    __slots__ = ()
    OPTIONAL = False

    @classmethod
    def calc_size(cls):
        return None

    @classmethod
    @abc.abstractmethod
    def serialize(cls, val, writer: BufferWriter, ctx: Optional[ParseContext]):
        pass

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, reader: Reader, ctx: Optional[ParseContext]):
        pass

    @classmethod
    def need_pod(cls, reader, pod=None):
        if pod is not None:
            return pod
        return reader.pod

    @classmethod
    def default_value(cls) -> Any:
        # None may be a valid default, so return MISSING as a sentinel val
        return dataclasses.MISSING


class Adapter(SerializableBase, abc.ABC):
    """Massages data on the way in / out without knowledge of how it's written"""
    __slots__ = ("_child_spec",)

    def __init__(self, child_spec: Optional[SERIALIZABLE_TYPE]):
        self._child_spec = child_spec
        super().__init__()

    def calc_size(self):
        if self._child_spec is None:
            return None
        return self._child_spec.calc_size()

    @abc.abstractmethod
    def encode(self, val: Any, ctx: Optional[ParseContext]) -> Any:
        raise NotImplementedError()

    @abc.abstractmethod
    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        raise NotImplementedError()

    def serialize(self, val, writer: BufferWriter, ctx: Optional[ParseContext]):
        writer.write(self._child_spec, self.encode(val, ctx), ctx=ctx)

    def deserialize(self, reader: Reader, ctx: Optional[ParseContext]):
        return self.decode(reader.read(self._child_spec, ctx=ctx), ctx=ctx, pod=reader.pod)


class ForwardSerializable(SerializableBase):
    """
    Used for deferring evaluation of a Serializable until it's actually used
    """
    __slots__ = ("_func", "_wrapped")

    def __init__(self, func: Callable[[], SERIALIZABLE_TYPE]):
        super().__init__()
        self._func = func
        self._wrapped = dataclasses.MISSING

    def _ensure_evaled(self):
        if self._wrapped is dataclasses.MISSING:
            self._wrapped = self._func()

    def __getattr__(self, attr):
        return getattr(self._wrapped, attr)

    def default_value(self) -> Any:
        if self._wrapped is dataclasses.MISSING:
            return dataclasses.MISSING
        return self._wrapped.default_value()

    def serialize(self, val, writer: BufferWriter, ctx: Optional[ParseContext]):
        self._ensure_evaled()
        return self._wrapped.serialize(val, writer, ctx=ctx)

    def deserialize(self, reader: Reader, ctx: Optional[ParseContext]):
        self._ensure_evaled()
        return self._wrapped.deserialize(reader, ctx=ctx)


class Template(SerializableBase):
    __slots__ = ("_template_spec", "_skip_missing", "_size")

    def __init__(self, template_spec: Dict[str, SERIALIZABLE_TYPE], skip_missing=False):
        self._template_spec = template_spec
        self._skip_missing = skip_missing
        self._size = dataclasses.MISSING

    def calc_size(self):
        if self._size is not dataclasses.MISSING:
            return self._size
        sum_bytes = 0
        for _, field_type in self._template_spec.items():
            size = field_type.calc_size()
            if size is None:
                sum_bytes = None
                break
            sum_bytes += size
        self._size = sum_bytes
        return self._size

    def serialize(self, values, writer: BufferWriter, ctx):
        ctx = ParseContext(values, parent=ctx)
        for field_name, field_type in self._template_spec.items():
            if field_type.OPTIONAL:
                val = values.get(field_name)
            else:
                val = values[field_name]

            with writer.enter_member(field_name):
                field_type.serialize(val, writer, ctx=ctx)

    def keys(self):
        return (spec[0] for spec in self._template_spec.items())

    def deserialize(self, reader: Reader, ctx):
        read_dict = {}
        ctx = ParseContext(read_dict, parent=ctx)
        for field_name, field_type in self._template_spec.items():
            val = field_type.deserialize(reader, ctx=ctx)
            if field_type.OPTIONAL and self._skip_missing and val is None:
                continue
            read_dict[field_name] = val
        return read_dict

    def default_value(self) -> Any:
        return dict


class IdentityAdapter(Adapter):
    def __init__(self):
        super().__init__(None)

    def encode(self, val: Any, ctx: Optional[ParseContext]) -> Any:
        return val

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        return val


class BoolAdapter(Adapter):
    def __init__(self, child_spec: Optional[SERIALIZABLE_TYPE] = None):
        super().__init__(child_spec)

    def encode(self, val: Any, ctx: Optional[ParseContext]) -> Any:
        return bool(val)

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        return bool(val)


class Struct(SerializableBase):
    __slots__ = ("_struct_fmt", "_le_struct", "_be_struct")

    def __init__(self, struct_fmt):
        self._struct_fmt: str = struct_fmt

        # Fixed endian-ness
        if struct_fmt[:1] in "!><":
            self._be_struct = self._le_struct = struct.Struct(struct_fmt)
        else:
            self._le_struct = struct.Struct("<" + struct_fmt)
            self._be_struct = struct.Struct(">" + struct_fmt)

    def calc_size(self):
        return self._be_struct.size

    def _pick_struct(self, endian: str):
        return self._be_struct if endian != "<" else self._le_struct

    def serialize(self, vals, writer: BufferWriter, ctx):
        struct_obj = self._pick_struct(writer.endianness)
        writer.write_bytes(struct_obj.pack(*vals))

    def deserialize(self, reader: Reader, ctx):
        struct_obj = self._pick_struct(reader.endianness)
        return struct_obj.unpack(reader.read_bytes(struct_obj.size, to_bytes=False))


class SerializablePrimitive(Struct):
    __slots__ = ("_default_val", "_is_signed", "_max_val", "_min_val")

    def __init__(self, struct_fmt: str, default_val):
        super().__init__(struct_fmt)
        self._default_val = default_val
        self._is_signed = self._struct_fmt.lower() == self._struct_fmt
        max_val = (2 ** (8 * self._be_struct.size)) - 1
        min_val = 0
        if self.is_signed:
            max_val = max_val // 2
            min_val = -1 - max_val
        self._max_val = max_val
        self._min_val = min_val

    def serialize(self, val, writer: BufferWriter, ctx):
        struct_obj = self._pick_struct(writer.endianness)
        writer.write_bytes(struct_obj.pack(val))

    def deserialize(self, reader: Reader, ctx):
        return super().deserialize(reader, ctx)[0]

    @property
    def is_signed(self):
        return self._is_signed

    @property
    def max_val(self):
        return self._max_val

    @property
    def min_val(self):
        return self._min_val

    def default_value(self) -> Any:
        return self._default_val


U8 = SerializablePrimitive("B", 0)
S8 = SerializablePrimitive("b", 0)
U16 = SerializablePrimitive("H", 0)
S16 = SerializablePrimitive("h", 0)
U32 = SerializablePrimitive("I", 0)
S32 = SerializablePrimitive("i", 0)
U64 = SerializablePrimitive("Q", 0)
S64 = SerializablePrimitive("q", 0)
F32 = SerializablePrimitive("f", 0.0)
F64 = SerializablePrimitive("d", 0.0)
BOOL = U8


UINT_BY_BYTES = {
    1: U8,
    2: U16,
    4: U32,
    8: U64,
}


class BytesBase(SerializableBase, abc.ABC):
    __slots__ = ()

    @abc.abstractmethod
    def deserialize(self, reader: Reader, ctx, to_bytes=True):
        raise NotImplementedError()

    def default_value(self) -> Any:
        return b""


class ByteArray(BytesBase):
    __slots__ = ("_len_spec",)

    def __init__(self, len_spec):
        super().__init__()
        self._len_spec: SerializablePrimitive = len_spec

    def serialize(self, instance, writer: BufferWriter, ctx):
        max_val = self._len_spec.max_val
        if max_val < len(instance):
            raise ValueError(f"{instance!r} is wider than {max_val}")
        writer.write(self._len_spec, len(instance), ctx=ctx)
        writer.write_bytes(instance)

    def deserialize(self, reader: Reader, ctx, to_bytes=True):
        bytes_len = reader.read(self._len_spec, ctx=ctx)
        return reader.read_bytes(bytes_len, to_bytes=to_bytes)


class BytesFixed(BytesBase):
    def __init__(self, size):
        super().__init__()
        self._size = size

    def calc_size(self):
        return self._size

    def serialize(self, instance, writer: BufferWriter, ctx):
        if len(instance) != self._size:
            raise ValueError(f"length of {instance!r} is not {self._size}")
        writer.write_bytes(instance)

    def deserialize(self, reader: Reader, ctx, to_bytes=True):
        return reader.read_bytes(self._size, to_bytes=to_bytes)

    def default_value(self) -> Any:
        return b"\x00" * self._size


class BytesGreedy(BytesBase):
    def serialize(self, val, writer: BufferWriter, ctx: Optional[ParseContext]):
        writer.write_bytes(val)

    def deserialize(self, reader: Reader, ctx: Optional[ParseContext], to_bytes=True):
        return reader.read_bytes(len(reader))


class Str(SerializableBase):
    def __init__(self, len_spec, null_term=True):
        self._bytes_tmpl = ByteArray(len_spec)
        self._null_term = null_term

    def serialize(self, instance, writer: BufferWriter, ctx):
        if isinstance(instance, str):
            instance = instance.encode("utf8")
            if self._null_term:
                instance += b"\x00"
        writer.write(self._bytes_tmpl, instance, ctx=ctx)

    def deserialize(self, reader: Reader, ctx):
        return reader.read(self._bytes_tmpl, ctx=ctx).rstrip(b"\x00").decode("utf8")

    def default_value(self) -> Any:
        return ""


class StrFixed(SerializableBase):
    def __init__(self, length: int):
        self._bytes_tmpl = BytesFixed(length)
        self._length = length

    def serialize(self, instance, writer: BufferWriter, ctx):
        if isinstance(instance, str):
            instance = instance.encode("utf8")
        if len(instance) > self._length:
            raise ValueError(f"{instance!r} can't fit in {self._length}")
        # Pad with nulls
        instance += b"\x00" * (self._length - len(instance))
        writer.write(self._bytes_tmpl, instance, ctx=ctx)

    def deserialize(self, reader: Reader, ctx):
        return reader.read(self._bytes_tmpl, ctx=ctx).rstrip(b"\x00").decode("utf8")

    def default_value(self) -> Any:
        return ""


class BytesTerminated(BytesBase):
    def __init__(self, terminators: Sequence[bytes], write_terminator: bool = True, eof_terminates: bool = True):
        super().__init__()
        self.terminators = terminators
        self.write_terminator = write_terminator
        self.eof_terminates = eof_terminates

    def serialize(self, val, writer: BufferWriter, ctx):
        writer.write_bytes(val)
        if self.write_terminator:
            writer.write_bytes(self.terminators[0])

    def deserialize(self, reader: Reader, ctx, to_bytes=True):
        orig_pos = reader.tell()
        num_bytes = 0
        had_term = False
        while reader:
            byte = reader.read_bytes(1, to_bytes=False)
            if byte in self.terminators:
                had_term = True
                break
            num_bytes += 1

        # Hit EOF before a terminator, error!
        if not self.eof_terminates and not had_term:
            raise ValueError(f"EOF before terminating {self.terminators!r}s found!")

        reader.seek(orig_pos)
        val = reader.read_bytes(num_bytes, to_bytes=to_bytes)

        if reader:
            # need to skip past the terminator
            reader.seek(reader.tell() + 1)

        return val


class CStr(SerializableBase):
    def __init__(self, encoding="utf8", terminators: Sequence[bytes] = (b"\x00",),
                 write_terminator: bool = True, eof_terminates: bool = True):
        self._bytes_tmpl = BytesTerminated(
            terminators=terminators, write_terminator=write_terminator, eof_terminates=eof_terminates
        )
        self._encoding = encoding

    def serialize(self, val, writer: BufferWriter, ctx):
        self._bytes_tmpl.serialize(val.encode(self._encoding), writer, ctx)

    def deserialize(self, reader: Reader, ctx):
        return self._bytes_tmpl.deserialize(reader, ctx).decode(self._encoding)

    def default_value(self) -> Any:
        return ""


class UUID(SerializableBase):
    @classmethod
    def calc_size(cls):
        return 16

    @classmethod
    def serialize(cls, instance, writer: BufferWriter, ctx):
        if isinstance(instance, str):
            instance = dtypes.UUID(instance)
        writer.write_bytes(instance.bytes)

    @classmethod
    def deserialize(cls, reader: Reader, ctx):
        val = dtypes.UUID(bytes=reader.read_bytes(16))
        if cls.need_pod(reader):
            return str(val)
        return val

    @classmethod
    def default_value(cls) -> Any:
        return dtypes.UUID


class Tuple(SerializableBase):
    def __init__(self, *args: SERIALIZABLE_TYPE):
        super().__init__()
        self._prim_seq: Tuple[SERIALIZABLE_TYPE] = tuple(args)

    def calc_size(self):
        return sum(p.calc_size() for p in self._prim_seq)

    def serialize(self, vals, writer: BufferWriter, ctx: Optional[ParseContext]):
        ctx = ParseContext(vals, parent=ctx)
        assert len(vals) == len(self._prim_seq)
        for p, v in zip(self._prim_seq, vals):
            writer.write(p, v, ctx=ctx)

    def deserialize(self, reader: Reader, ctx: Optional[ParseContext]):
        entries = []
        ctx = ParseContext(entries, ctx)
        for p in self._prim_seq:
            entries.append(reader.read(p, ctx=ctx))
        return entries


class Collection(SerializableBase):
    def __init__(self, length: Union[None, int, SerializableBase], entry_ser):
        self._entry_ser = entry_ser
        self._len_spec = None
        self._length = None
        if isinstance(length, SerializableBase):
            self._len_spec = length
        elif isinstance(length, int):
            self._length = length

    def serialize(self, entries, writer: BufferWriter, ctx):
        if self._len_spec:
            max_len = getattr(self._len_spec, 'max_val', None)
            if max_len is not None and max_len < len(entries):
                raise ValueError(f"{len(entries)} is wider than {max_len}")
        elif self._length:
            if len(entries) != self._length:
                raise ValueError(f"Need exactly {self._length} entries, got {len(entries)}")

        ctx = ParseContext(entries, parent=ctx)

        if self._len_spec:
            writer.write(self._len_spec, len(entries), ctx=ctx)

        for entry in entries:
            writer.write(self._entry_ser, entry, ctx=ctx)

    def deserialize(self, reader: Reader, ctx):
        entries = []
        ctx = ParseContext(entries, parent=ctx)
        if self._len_spec or self._length:
            if self._len_spec:
                size = reader.read(self._len_spec, ctx=ctx)
            else:
                size = self._length

            for _ in range(size):
                entries.append(reader.read(self._entry_ser, ctx=ctx))
        else:
            # Greedy, try to consume entries until we run out of data
            while reader:
                entries.append(reader.read(self._entry_ser, ctx=ctx))
        return entries

    def default_value(self) -> Any:
        return list


class QuantizedFloatBase(Adapter, abc.ABC):
    """
    Base class for endpoint (and optionally midpoint) preserving quantized floats

    Doesn't interpret floats 100% the same as LL's implementation, but
    encode(decode(val)) will never change the original binary representation.
    """

    __slots__ = ("zero_median", "prim_min", "step_mag")
    _child_spec: SerializablePrimitive

    def __init__(self, prim_spec: SerializablePrimitive, zero_median: bool):
        super().__init__(prim_spec)
        self.zero_median = zero_median
        self.prim_min = prim_spec.min_val
        self.step_mag = 1.0 / (prim_spec.max_val - prim_spec.min_val)

    def _quantized_to_float(self, val: int, lower: float, upper: float):
        delta = upper - lower
        max_error = delta * self.step_mag

        # Convert to unsigned if it was signed
        val -= self.prim_min
        val *= self.step_mag
        val *= delta
        val += lower

        # Zero is in the middle of the range and we're pretty close. Round towards it.
        # This works because if 0 is directly in the middle then values next to `0` will be
        # a half step away from 0.0. This means that there will be two values for which
        # math.fabs(val) < max_error. This leads to 0.0 being slightly over-represented, but
        # that's preferable to not having an exact representation of 0.0
        if self.zero_median and math.fabs(val) < max_error:
            if val < 0.0:
                # Use -0 so we know to use the lower of the two values
                # that can represent 0 when we re-serialize. Kind of a stupid hack,
                # but takes advantage of that fact that 0.0 == -0.0
                val = -0.0
            else:
                val = 0.0

        return val

    def _float_to_quantized(self, val: float, lower: float, upper: float):
        delta = upper - lower
        if delta == 0.0:
            return self.prim_min

        val = min(max(val, lower), upper)

        # Zero is in the exact middle and we have exactly 0. Invoke special
        # rounding mode to treat 0.0 and -0.0 differently.
        nudge = 0.0
        if self.zero_median and val == 0.0:
            # Only change the value a tiny bit so the rounding is biased
            # towards the correct value
            nudge = delta * self.step_mag * 0.5
            nudge = math.copysign(nudge, val)

        val += nudge
        val -= lower
        val /= delta
        val /= self.step_mag
        val = int(round(val))
        return val + self.prim_min


class QuantizedFloat(QuantizedFloatBase):
    __slots__ = ("lower", "upper")

    def __init__(self, prim_spec: SerializablePrimitive, lower: float, upper: float,
                 zero_median: Optional[bool] = None):
        super().__init__(prim_spec, zero_median=False)
        self.lower = lower
        self.upper = upper
        # We know the range in `QuantizedFloat` when it's constructed,  so we can infer
        # whether or not we should round towards zero in __init__
        max_error = (upper - lower) * self.step_mag
        midpoint = (upper + lower) / 2.0
        # Rounding behaviour wasn't specified and the distance of the midpoint is
        # smaller than the size of each floating point step. Round towards 0.
        if zero_median is None and math.fabs(midpoint) < max_error:
            self.zero_median = True

    def encode(self, val: Any, ctx: Optional[ParseContext]) -> int:
        return self._float_to_quantized(val, self.lower, self.upper)

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        return self._quantized_to_float(val, self.lower, self.upper)

    def default_value(self) -> Any:
        if self.zero_median:
            return 0.0
        return (self.upper + self.lower) / 2.0


class TupleCoord(SerializableBase):
    ELEM_SPEC: SerializablePrimitive
    NUM_ELEMS: int
    COORD_CLS: Type[dtypes.TupleCoord]

    @classmethod
    def calc_size(cls):
        return cls.ELEM_SPEC.calc_size() * cls.NUM_ELEMS

    @classmethod
    def _vals_to_tuple(cls, vals):
        if isinstance(vals, dtypes.TupleCoord):
            vals = vals.data(cls.NUM_ELEMS)
        elif len(vals) != cls.NUM_ELEMS:
            vals = cls.COORD_CLS(*vals).data(cls.NUM_ELEMS)

        if len(vals) != cls.NUM_ELEMS:
            raise ValueError(f"Expected {cls.NUM_ELEMS} elems, got {vals!r}")
        return vals

    @classmethod
    def serialize(cls, vals, writer: BufferWriter, ctx):
        vals = cls._vals_to_tuple(vals)
        for comp in vals:
            writer.write(cls.ELEM_SPEC, comp, ctx=ctx)

    @classmethod
    def deserialize(cls, reader: Reader, ctx):
        vals = (reader.read(cls.ELEM_SPEC, ctx=ctx) for _ in range(cls.NUM_ELEMS))
        val = cls.COORD_CLS(*vals)
        if cls.need_pod(reader):
            return val.data()
        return val

    @classmethod
    def default_value(cls) -> Any:
        return cls.COORD_CLS


class EncodedTupleCoord(TupleCoord, abc.ABC):
    _elem_specs: Sequence[SERIALIZABLE_TYPE]

    def serialize(self, vals, writer: BufferWriter, ctx):
        vals = self._vals_to_tuple(vals)
        for spec, val in zip(self._elem_specs, vals):
            writer.write(spec, val, ctx=ctx)

    def deserialize(self, reader: Reader, ctx):
        vals = (reader.read(spec, ctx=ctx) for spec in self._elem_specs)
        val = self.COORD_CLS(*vals)
        if self.need_pod(reader):
            return tuple(val)
        return val


class QuantizedTupleCoord(EncodedTupleCoord):
    def __init__(self, lower=None, upper=None, component_scales=None):
        super().__init__()
        if component_scales:
            self._elem_specs = tuple(
                QuantizedFloat(self.ELEM_SPEC, lower, upper)
                for lower, upper in component_scales
            )
        else:
            assert lower is not None and upper is not None
            self._elem_specs = tuple(
                QuantizedFloat(self.ELEM_SPEC, lower, upper)
                for _ in range(self.NUM_ELEMS)
            )
        assert len(self._elem_specs) == self.NUM_ELEMS


class FixedPointTupleCoord(EncodedTupleCoord):
    def __init__(self, int_bits: int, frac_bits: int, signed: bool):
        super().__init__()
        self._elem_specs = tuple(
            FixedPoint(self.ELEM_SPEC, int_bits, frac_bits, signed)
            for _ in range(self.NUM_ELEMS)
        )


class Vector3(TupleCoord):
    ELEM_SPEC = F32
    NUM_ELEMS = 3
    COORD_CLS = dtypes.Vector3


TUPLECOORD_TYPE = Union[TupleCoord, Type[TupleCoord]]


# Assumes X, Y, Z(, W)? ranged from -1.0 to 1.0
class PackedQuat(Adapter):
    _child_spec: TUPLECOORD_TYPE

    def __init__(self, coord_spec: TUPLECOORD_TYPE):
        super().__init__(coord_spec)

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        if pod:
            return val
        return dtypes.Quaternion(*val)

    def encode(self, val: Any, ctx: Optional[ParseContext]) -> Any:
        if not isinstance(val, dtypes.TupleCoord):
            val = dtypes.Quaternion(*val).data(self._child_spec.NUM_ELEMS)
        return val

    @classmethod
    def default_value(cls) -> Any:
        return dtypes.Quaternion


class Vector4(TupleCoord):
    ELEM_SPEC = F32
    NUM_ELEMS = 4
    COORD_CLS = dtypes.Vector4


class Vector3D(TupleCoord):
    ELEM_SPEC = F64
    NUM_ELEMS = 3
    COORD_CLS = dtypes.Vector3


class Vector3U16(QuantizedTupleCoord):
    ELEM_SPEC = U16
    NUM_ELEMS = 3
    COORD_CLS = dtypes.Vector3


class Vector2U16(QuantizedTupleCoord):
    ELEM_SPEC = U16
    NUM_ELEMS = 2
    COORD_CLS = dtypes.Vector2


class Vector4U16(QuantizedTupleCoord):
    ELEM_SPEC = U16
    NUM_ELEMS = 4
    COORD_CLS = dtypes.Vector4


class Vector3U8(QuantizedTupleCoord):
    ELEM_SPEC = U8
    NUM_ELEMS = 3
    COORD_CLS = dtypes.Vector3


class Vector4U8(QuantizedTupleCoord):
    ELEM_SPEC = U8
    NUM_ELEMS = 4
    COORD_CLS = dtypes.Vector4


class FixedPointVector3U16(FixedPointTupleCoord):
    ELEM_SPEC = U16
    NUM_ELEMS = 3
    COORD_CLS = dtypes.Vector3


class OptionalPrefixed(SerializableBase):
    """Field prefixed by a U8 indicating whether or not it's present"""
    OPTIONAL = True

    def __init__(self, ser_spec: SERIALIZABLE_TYPE):
        self._ser_spec = ser_spec

    def serialize(self, val, writer: BufferWriter, ctx):
        writer.write(U8, val is not None, ctx=ctx)
        if val is not None:
            writer.write(self._ser_spec, val, ctx=ctx)

    def deserialize(self, reader: Reader, ctx):
        present = reader.read(U8, ctx=ctx)
        if present:
            return reader.read(self._ser_spec, ctx=ctx)
        return None


class OptionalFlagged(SerializableBase):
    OPTIONAL = True

    def __init__(self, flag_field: str, flag_spec: "IntFlag",
                 flag_val: int, ser_spec: SERIALIZABLE_TYPE):
        self._flag_field = flag_field
        self._flag_spec = flag_spec
        self._flag_val = int(flag_val)
        self._ser_spec = ser_spec

    def _normalize_flag_val(self, ctx):
        flag_val = ctx[self._flag_field]
        if isinstance(self._flag_spec, SerializablePrimitive):
            return int(flag_val)
        return int(self._flag_spec.encode(flag_val, ctx=None))

    def serialize(self, val, writer: BufferWriter, ctx):
        if self._normalize_flag_val(ctx) & self._flag_val:
            writer.write(self._ser_spec, val, ctx=ctx)

    def deserialize(self, reader: Reader, ctx):
        if self._normalize_flag_val(ctx) & self._flag_val:
            return reader.read(self._ser_spec, ctx=ctx)
        return None


class LengthSwitch(SerializableBase):
    """Switch on bytes left in the reader"""
    def __init__(self, choice_specs: Dict[Optional[int], SERIALIZABLE_TYPE]):
        self._choice_specs = choice_specs
        super().__init__()

    def serialize(self, val, writer: BufferWriter, ctx):
        if val[0] not in self._choice_specs and None in self._choice_specs:
            choice_spec = self._choice_specs[None]
        else:
            choice_spec = self._choice_specs[val[0]]

        writer.write(choice_spec, val[1], ctx=ctx)

    def deserialize(self, reader: Reader, ctx):
        size = len(reader)
        if size not in self._choice_specs and None in self._choice_specs:
            choice_spec = self._choice_specs[None]
        else:
            choice_spec = self._choice_specs[size]
        val = size, reader.read(choice_spec, ctx=ctx)
        if reader.pod:
            return val
        return dtypes.TaggedUnion(*val)


class IntEnum(Adapter):
    """Tries to (de)serialize an enum as its str form, falling back to int"""
    def __init__(self, enum_cls: Type[enum.IntEnum],
                 enum_spec: Optional[SerializablePrimitive] = None, strict=False):
        super().__init__(enum_spec)
        self.enum_cls = enum_cls
        self._strict = strict

    def encode(self, val: Any, ctx: Optional[ParseContext]) -> Any:
        if isinstance(val, str):
            val = int(self.enum_cls[val])
        return val

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        if val in iter(self.enum_cls):
            val = self.enum_cls(val)
            if pod:
                return val.name
            return val
        elif self._strict:
            raise ValueError(f"{val} is not a valid {self.enum_cls}")
        # Doesn't exist in the enum, just return an int...
        return val

    def default_value(self) -> Any:
        return lambda: self.enum_cls(0)


class IntFlag(Adapter):
    def __init__(self, flag_cls: Type[enum.IntFlag],
                 flag_spec: Optional[SerializablePrimitive] = None):
        super().__init__(flag_spec)
        self.flag_cls = flag_cls

    def encode(self, val: Union[int, Iterable], ctx: Optional[ParseContext]) -> Any:
        if isinstance(val, int):
            return val

        # Must be an iterable of strings or enum vals then
        new_val = 0
        for v in val:
            if isinstance(v, str):
                v = self.flag_cls[v]
            new_val |= v
        return new_val

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        if pod:
            return dtypes.flags_to_pod(self.flag_cls, val)
        return self.flag_cls(val)

    def default_value(self) -> Any:
        return lambda: self.flag_cls(0)


class EnumSwitch(SerializableBase):
    def __init__(self, enum_spec: IntEnum, choice_specs: Dict[enum.IntEnum, SERIALIZABLE_TYPE]):
        self._enum_spec = enum_spec
        self._choice_specs = choice_specs
        super().__init__()

    def serialize(self, val, writer: BufferWriter, ctx):
        flag, val = val
        writer.write(self._enum_spec, flag, ctx=ctx)
        if isinstance(flag, str):
            flag = self._enum_spec.enum_cls[flag]
        writer.write(self._choice_specs[flag], val, ctx=ctx)

    def deserialize(self, reader: Reader, ctx):
        flag = reader.read(self._enum_spec, ctx=ctx)
        choice_flag = flag
        # POD mode, need to get the actual enum val to do the lookup
        if isinstance(flag, str):
            choice_flag = self._enum_spec.enum_cls[choice_flag]
        val = flag, reader.read(self._choice_specs[choice_flag], ctx=ctx)
        if reader.pod:
            return val
        return dtypes.TaggedUnion(*val)


class FlagSwitch(SerializableBase):
    def __init__(self, flag_spec: IntFlag, choice_specs: Dict[enum.IntFlag, SERIALIZABLE_TYPE]):
        self._flag_spec = flag_spec
        self._choice_specs = choice_specs
        super().__init__()

    def serialize(self, vals: Dict[Union[str, int], Any], writer: BufferWriter, ctx):
        writer.write(self._flag_spec, vals.keys(), ctx=ctx)
        for flag, choice_spec in self._choice_specs.items():
            if flag in vals:
                writer.write(choice_spec, vals[flag], ctx=ctx)
            elif flag.name in vals:
                writer.write(choice_spec, vals[flag.name], ctx=ctx)

    def deserialize(self, reader: Reader, ctx):
        # We need this as an int regardless of whether we're in POD mode
        with reader.scoped_pod(pod=False):
            flags = int(self._flag_spec.deserialize(reader, ctx=ctx))
        # deserialize the choices for any set flags
        return {
            choice_flag.name if self.need_pod(reader) else choice_flag:
                reader.read(choice_spec, ctx=ctx)
            for choice_flag, choice_spec in self._choice_specs.items()
            if flags & choice_flag.value
        }


class ContextMixin(Generic[_T]):
    _fun: Callable
    _options: Dict

    def _choose_option(self, ctx: Optional[ParseContext]) -> _T:
        idx = self._fun(ctx)
        if idx not in self._options:
            if dataclasses.MISSING not in self._options:
                raise KeyError(f"{idx!r} not found in {self._options!r}")
            idx = dataclasses.MISSING
        return self._options[idx]


class ContextAdapter(Adapter, ContextMixin[Adapter]):
    def __init__(self, fun: Callable[[ParseContext], Any], child_spec: Optional[SERIALIZABLE_TYPE],
                 options: Dict[Any, Adapter]):
        super().__init__(child_spec)
        self._fun = fun
        self._options = options

    def encode(self, val: Any, ctx: Optional[ParseContext]) -> Any:
        return self._choose_option(ctx).encode(val, ctx=ctx)

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        return self._choose_option(ctx).decode(val, ctx=ctx, pod=pod)


class ContextSwitch(SerializableBase, ContextMixin[SERIALIZABLE_TYPE]):
    def __init__(self, fun: Callable[[ParseContext], Any], options: Dict[Any, SERIALIZABLE_TYPE]):
        super().__init__()
        self._fun = fun
        self._options = options

    def deserialize(self, reader: Reader, ctx: Optional[ParseContext]):
        return reader.read(self._choose_option(ctx), ctx=ctx)

    def serialize(self, val, writer: BufferWriter, ctx: Optional[ParseContext]):
        writer.write(self._choose_option(ctx), val, ctx=ctx)


class Null(SerializableBase):
    @classmethod
    def serialize(cls, val, writer: BufferWriter, ctx):
        pass

    @classmethod
    def deserialize(cls, reader: Reader, ctx):
        return None

    @classmethod
    def default_value(cls) -> Any:
        return None


@dataclasses.dataclass
class BitfieldEntry:
    bits: int
    adapter: Optional[Adapter]


BITFIELD_ENTRY_SPEC = Union[int, BitfieldEntry]


class BitField(Adapter):
    def __init__(self, prim_spec: Optional[SerializablePrimitive],
                 schema: Dict[str, BITFIELD_ENTRY_SPEC], shift: bool = True):
        super().__init__(prim_spec)

        # helpers.BitField only understands bit counts, so pick those out
        bitfield_schema = {}
        adapter_schema = {}
        for k, v in schema.items():
            if isinstance(v, BitfieldEntry):
                bitfield_schema[k] = v.bits
                adapter_schema[k] = v
            else:
                bitfield_schema[k] = v
                adapter_schema[k] = BitfieldEntry(bits=v, adapter=IdentityAdapter())

        self._bitfield = helpers.BitField(bitfield_schema, shift=shift)
        self._schema = adapter_schema

    def encode(self, val: Union[dict, int], ctx: Optional[ParseContext]) -> Any:
        # Already packed
        if isinstance(val, int):
            return val
        val = {
            k: self._schema[k].adapter.encode(v, ctx=ctx)
            for k, v in val.items()
        }
        return self._bitfield.pack(val)

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        val = self._bitfield.unpack(val)
        return {
            k: self._schema[k].adapter.decode(v, ctx=ctx, pod=pod)
            for k, v in val.items()
        }

    def default_value(self) -> Any:
        return dict


class TypedBytesBase(SerializableBase, abc.ABC):
    _bytes_tmpl: BytesBase

    def __init__(self, spec, empty_is_none=False, check_trailing_bytes=True, lazy=False):
        super().__init__()
        self._lazy = lazy
        self._spec: SerializableBase = spec
        self._empty_is_none = empty_is_none
        self._check_trailing_bytes = check_trailing_bytes

    def serialize(self, val, writer: BufferWriter, ctx):
        if val is None and self._empty_is_none:
            buf = b""
        else:
            inner_writer = BufferWriter(writer.endianness)
            inner_writer.write(self._spec, val, ctx=ctx)
            buf = inner_writer.buffer
        return self._bytes_tmpl.serialize(buf, writer, ctx=ctx)

    def deserialize(self, reader: Reader, ctx):
        buf = self._bytes_tmpl.deserialize(reader, ctx=ctx, to_bytes=False)
        if self._empty_is_none and not buf:
            return None
        endianness = reader.endianness
        pod = reader.pod
        if self._lazy and not pod:
            return lazy_object_proxy.Proxy(
                self._lazy_deserialize_inner(endianness, pod, buf))
        return self._deserialize_inner(endianness, pod, buf, ctx)

    def _lazy_deserialize_inner(self, endianness, pod, buf):
        def _deserialize_later():
            # No context allowed, we don't want to keep any referenced objects alive
            return self._deserialize_inner(endianness, pod, buf, ctx=None)
        return _deserialize_later

    def _deserialize_inner(self, endianness, pod, buf, ctx):
        inner_reader = BufferReader(endianness, buf, pod=pod)
        val = inner_reader.read(self._spec, ctx=ctx)
        if self._check_trailing_bytes and len(inner_reader):
            raise ValueError(f"{len(inner_reader)} trailing bytes after {val}")
        return val

    def default_value(self) -> Any:
        return self._spec.default_value()


class TypedByteArray(TypedBytesBase):
    def __init__(self, len_spec, spec, empty_is_none=False, check_trailing_bytes=True, lazy=False):
        self._bytes_tmpl = ByteArray(len_spec)
        super().__init__(spec, empty_is_none, check_trailing_bytes, lazy=lazy)


class TypedBytesFixed(TypedBytesBase):
    def __init__(self, length, spec, empty_is_none=False, check_trailing_bytes=True, lazy=False):
        self._bytes_tmpl = BytesFixed(length)
        super().__init__(spec, empty_is_none, check_trailing_bytes, lazy=lazy)


class TypedBytesTerminated(TypedBytesBase):
    def __init__(self, spec, terminators: Sequence[bytes], empty_is_none=False,
                 check_trailing_bytes=True, lazy=False):
        self._bytes_tmpl = BytesTerminated(terminators)
        self._empty_is_none = empty_is_none
        super().__init__(spec, empty_is_none, check_trailing_bytes, lazy=lazy)

    def serialize(self, val, writer: BufferWriter, ctx):
        # Don't write a terminator at all if we got `None`
        if val is None and self._empty_is_none:
            return
        super().serialize(val, writer, ctx)


class IfPresent(SerializableBase):
    """Only write if non-None, or read if there are bytes left"""
    def __init__(self, ser_spec):
        self._ser_spec = ser_spec

    def serialize(self, val, writer: BufferWriter, ctx):
        if val is None:
            return
        writer.write(self._ser_spec, val, ctx=ctx)

    def deserialize(self, reader: Reader, ctx):
        if len(reader):
            return reader.read(self._ser_spec, ctx=ctx)
        return None


class DictAdapter(Adapter):
    """
    Transformer for key -> value mappings where order is important
    """
    def encode(self, val: Union[Sequence, dict], ctx: Optional[ParseContext]) -> Any:
        if isinstance(val, dict):
            val = val.items()
        return tuple(val)

    def decode(self, val: Sequence, ctx: Optional[ParseContext], pod: bool = False):
        return dict(val)

    def default_value(self) -> Any:
        return dict


class MultiDictAdapter(Adapter):
    """
    Same as DictAdapter, but allows multiple values per key.

    Useful for structures that are best represented as dicts, but whose
    serialization formats would technically allow for duplicate keys, even
    if those duplicate keys would be meaningless.
    """
    def encode(self, val: Union[Sequence, dict], ctx: Optional[ParseContext]) -> Any:
        if isinstance(val, OrderedMultiDict):
            val = val.items(multi=True)
        elif isinstance(val, dict):
            val = val.items()
        return tuple(val)

    def decode(self, val: Sequence, ctx: Optional[ParseContext], pod: bool = False):
        return OrderedMultiDict(val)

    def default_value(self) -> Any:
        return OrderedMultiDict


class StringEnumAdapter(Adapter):
    def __init__(self, enum_cls: Type, child_spec: SERIALIZABLE_TYPE):
        self._enum_cls = enum_cls
        super().__init__(child_spec)

    def encode(self, val: dtypes.StringEnum, ctx: Optional[ParseContext]) -> Any:
        return str(val)

    def decode(self, val: str, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        if pod:
            return val
        return self._enum_cls(val)


class FixedPoint(SerializableBase):
    def __init__(self, ser_spec, int_bits, frac_bits, signed=False):
        # Should never be used due to how this handles signs :/
        assert(not ser_spec.is_signed)

        self._ser_spec: SerializablePrimitive = ser_spec
        self._signed = signed
        self._frac_bits = frac_bits

        required_bits = int_bits + frac_bits + int(signed)
        self._min_val = ((1 << int_bits) * -1) if signed else 0
        self._max_val = 1 << int_bits

        assert(required_bits == (ser_spec.calc_size() * 8))

    def deserialize(self, reader: Reader, ctx):
        fixed_val = float(self._ser_spec.deserialize(reader, ctx))
        fixed_val /= (1 << self._frac_bits)
        if self._signed:
            fixed_val -= self._max_val
        return fixed_val

    def serialize(self, val: float, writer: BufferWriter, ctx):
        val = min(max(val, self._min_val), self._max_val)
        if self._signed:
            val += self._max_val
        val *= 1 << self._frac_bits
        return self._ser_spec.serialize(round(val), writer, ctx)

    def calc_size(self):
        return self._ser_spec.calc_size()

    def default_value(self) -> Any:
        return 0.0


def _make_undefined_raiser():
    def f():
        raise ValueError(f"{f.field.name if f.field else 'field'} must be specified!")
    f.field = None
    return f


def dataclass_field(spec: Union[SERIALIZABLE_TYPE, Callable], *, default=dataclasses.MISSING,
                    default_factory=dataclasses.MISSING, init=True, repr=True,  # noqa
                    hash=None, compare=True) -> dataclasses.Field:  # noqa
    enrich_factory = False
    # Lambda, need to defer evaluation of spec until it's actually used.
    if isinstance(spec, types.FunctionType):
        spec = ForwardSerializable(spec)

    if all(x is dataclasses.MISSING for x in (default, default_factory)):
        spec_default = spec.default_value()
        if spec_default is dataclasses.MISSING:
            enrich_factory = True
            default_factory = _make_undefined_raiser()
        else:
            if callable(spec_default):
                default_factory = spec_default
            else:
                default = spec_default
    field = dataclasses.field(
        metadata={"spec": spec}, default=default, default_factory=default_factory, init=init,
        repr=repr, hash=hash, compare=compare
    )
    # Need to stuff this on so it knows which field went unspecified.
    if enrich_factory:
        default_factory.field = field
    return field


class DataclassAdapter(Adapter):
    def __init__(self, data_cls: Type, child_spec: SERIALIZABLE_TYPE):
        super().__init__(child_spec)
        self._data_cls = data_cls

    def encode(self, val: Any, ctx: Optional[ParseContext]) -> Any:
        if isinstance(val, lazy_object_proxy.Proxy):
            # Have to unwrap these or the dataclass check will fail
            val = val.__wrapped__
        if dataclasses.is_dataclass(val):
            val = dataclasses.asdict(val)
        return val

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        if pod:
            return val
        return self._data_cls(**val)

    def default_value(self) -> Any:
        return self._data_cls


class Dataclass(SerializableBase):
    def __init__(self, data_cls: Type):
        super().__init__()
        self._data_cls = data_cls

        if not dataclasses.is_dataclass(data_cls):
            raise ValueError("data_cls must be a dataclass")

        self.template = self._build_inner_spec(data_cls)
        self._wrapped_spec = DataclassAdapter(self._data_cls, self.template)

    def _build_inner_spec(self, data_cls: Type):
        template = {}
        for field in dataclasses.fields(data_cls):  # noqa: no dataclass type annotation!
            field: dataclasses.Field = field
            if "spec" not in field.metadata:
                raise ValueError(f"Dataclass fields must be serialization-aware: {field!r}")
            template[field.name] = field.metadata["spec"]
        return Template(template)

    def serialize(self, val, writer: BufferWriter, ctx: Optional[ParseContext]):
        writer.write(self._wrapped_spec, val, ctx=ctx)

    def deserialize(self, reader: Reader, ctx: Optional[ParseContext]):
        return reader.read(self._wrapped_spec, ctx=ctx)

    def default_value(self) -> Any:
        return self._data_cls


def bitfield_field(bits: int, *, adapter: Optional[Adapter] = None, default=0, init=True, repr=True,  # noqa
                   hash=None, compare=True) -> dataclasses.Field:  # noqa
    return dataclasses.field(
        metadata={"bits": bits, "adapter": adapter}, default=default, init=init,
        repr=repr, hash=hash, compare=compare
    )


class BitfieldDataclass(DataclassAdapter):
    def __init__(self, data_cls: Type,
                 prim_spec: Optional[SerializablePrimitive] = None, shift: bool = True):
        super().__init__(data_cls, prim_spec)
        self._shift = shift
        self._bitfield_spec = self._build_bitfield(data_cls)

    def _build_bitfield(self, data_cls: Type):
        template = {}
        for field in dataclasses.fields(data_cls):  # noqa: no dataclass type annotation!
            field: dataclasses.Field = field
            bits = field.metadata.get("bits")
            adapter = field.metadata.get("adapter")
            if bits is None:
                raise ValueError(f"Dataclass fields must be bitfield serialization-aware: {field!r}")

            if adapter is not None:
                template[field.name] = BitfieldEntry(bits=bits, adapter=adapter)
            else:
                template[field.name] = field.metadata["bits"]
        return BitField(self._child_spec, template, self._shift)

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        val = self._bitfield_spec.decode(val, ctx=ctx, pod=pod)
        return super().decode(val, ctx=ctx, pod=pod)

    def encode(self, val: Any, ctx: Optional[ParseContext]) -> Any:
        val = super().encode(val, ctx)
        return self._bitfield_spec.encode(val, ctx)


class ExprAdapter(Adapter):
    def __init__(self, child_spec: SERIALIZABLE_TYPE, decode_func: Callable, encode_func: Callable):
        super().__init__(child_spec)
        self._decode_func = decode_func
        self._encode_func = encode_func

    def encode(self, val: Any, ctx: Optional[ParseContext]) -> Any:
        return self._encode_func(val)

    def decode(self, val: Any, ctx: Optional[ParseContext], pod: bool = False) -> Any:
        return self._decode_func(val)


class BufferedLLSDBinaryParser(llsd.HippoLLSDBinaryParser):
    def __init__(self):
        super().__init__()
        self._buffer: Optional[Reader] = None

    def _parse_array(self):
        val = super()._parse_array()
        # _parse_array() checks but doesn't skip the closing ']', do it ourselves.
        self._getc(1)
        return val

    def _error(self, message, offset=0):
        with self._buffer.scoped_seek(offset, SEEK_CUR):
            try:
                byte = self._getc()[0]
            except IndexError:
                byte = None
        raise llsd.LLSDParseError("%s at byte %d: %s" % (message, self._index + offset, byte))

    def _getc(self, num=1):
        return self._buffer.read_bytes(num)

    def _peek(self, num=1):
        return self._buffer.read_bytes(num, peek=True)


class BinaryLLSD(SerializableBase):
    @classmethod
    def deserialize(cls, reader: Reader, ctx):
        parser = BufferedLLSDBinaryParser()
        return parser.parse(reader)

    @classmethod
    def serialize(cls, val, writer: BufferWriter, ctx):
        writer.write_bytes(llsd.format_binary(val, with_header=False))


def subfield_serializer(msg_name, block_name, var_name):
    def f(orig_cls):
        global SUBFIELD_SERIALIZERS
        SUBFIELD_SERIALIZERS[(msg_name, block_name, var_name)] = orig_cls
        return orig_cls
    return f


_ENUM_TYPE = TypeVar("_ENUM_TYPE", bound=Type[dtypes.IntEnum])
_FLAG_TYPE = TypeVar("_FLAG_TYPE", bound=Type[dtypes.IntFlag])


def enum_field_serializer(msg_name, block_name, var_name):
    def f(orig_cls: _ENUM_TYPE) -> _ENUM_TYPE:
        if not issubclass(orig_cls, dtypes.IntEnum):
            raise ValueError(f"{orig_cls} must be a subclass of Hippolyzer's IntEnum class")
        wrapper = subfield_serializer(msg_name, block_name, var_name)
        wrapper(IntEnumSubfieldSerializer(orig_cls))
        return orig_cls
    return f


def flag_field_serializer(msg_name, block_name, var_name):
    def f(orig_cls: _FLAG_TYPE) -> _FLAG_TYPE:
        if not issubclass(orig_cls, dtypes.IntFlag):
            raise ValueError(f"{orig_cls!r} must be a subclass of Hippolyzer's IntFlag class")
        wrapper = subfield_serializer(msg_name, block_name, var_name)
        wrapper(IntFlagSubfieldSerializer(orig_cls))
        return orig_cls
    return f


class BaseSubfieldSerializer(abc.ABC):
    CHECK_TRAILING_BYTES = True
    ENDIANNESS = "<"
    ORIG_INLINE = False
    AS_HEX = False

    @classmethod
    def _serialize_template(cls, template, vals):
        w = BufferWriter(cls.ENDIANNESS)
        w.write(template, vals)
        return w.copy_buffer()

    @classmethod
    def _deserialize_template(cls, template, buf, pod=False):
        if template is UNSERIALIZABLE:
            return UNSERIALIZABLE
        r = BufferReader(cls.ENDIANNESS, buf, pod=pod)
        read = r.read(template)
        if cls.CHECK_TRAILING_BYTES and r:
            raise BufferError(f"{len(r)} trailing bytes left in buffer")
        return read

    @classmethod
    @abc.abstractmethod
    def serialize(cls, ctx_obj, vals):
        pass

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, ctx_obj, val, pod=False):
        pass

    @classmethod
    def _template_sizes_match(cls, temp: Template, val: bytes):
        return temp.calc_size() == len(val)

    @classmethod
    def _template_keys_match(cls, temp: Template, val: Dict):
        return set(temp.keys()) == set(val.keys())

    @classmethod
    def _fuzzy_guess_template(cls, templates: Iterable[Union[Template, Dataclass]],
                              val: Union[bytes, Dict, Any]):
        """Guess at which template a val might correspond to"""
        if dataclasses.is_dataclass(val):
            val = dataclasses.asdict(val)  # noqa
        if isinstance(val, (bytes, bytearray)):
            template_checker = cls._template_sizes_match
        elif isinstance(val, dict):
            template_checker = cls._template_keys_match
        else:
            raise ValueError(f"Unknown val type {val!r}")

        for template in templates:
            if isinstance(template, Dataclass):
                template = template.template
            if template is UNSERIALIZABLE:
                continue
            if template_checker(template, val):
                return template
        return None


class EnumSwitchedSubfieldSerializer(BaseSubfieldSerializer):
    ENUM_FIELD = None
    TEMPLATES = None
    # If False then we check if any of the possible templates
    # looks like it matches if the flagged one doesn't work.
    STRICT = True

    @classmethod
    def _try_all_templates(cls, func, block, val, **kwargs):
        try:
            return func(cls.TEMPLATES[block[cls.ENUM_FIELD]], val, **kwargs)
        except Exception:
            # Try all other templates if the expected template doesn't work
            template = cls._fuzzy_guess_template(cls.TEMPLATES.values(), val)
            if not template:
                raise
            return func(template, val, **kwargs)

    @classmethod
    def deserialize(cls, ctx_obj, val, pod=False):
        if cls.STRICT:
            return cls._deserialize_template(cls.TEMPLATES[ctx_obj[cls.ENUM_FIELD]], val, pod)
        else:
            return cls._try_all_templates(cls._deserialize_template, ctx_obj, val, pod=pod)

    @classmethod
    def serialize(cls, ctx_obj, val):
        if cls.STRICT:
            return cls._serialize_template(cls.TEMPLATES[ctx_obj[cls.ENUM_FIELD]], val)
        else:
            return cls._try_all_templates(cls._serialize_template, ctx_obj, val)


class FlagSwitchedSubfieldSerializer(BaseSubfieldSerializer):
    FLAG_FIELD: str
    TEMPLATES: Dict[enum.IntFlag, SerializableBase]

    @classmethod
    def _build_template(cls, flag_val):
        template_dict = {}
        for flag, template in cls.TEMPLATES.items():
            if flag_val & flag.value:
                template_dict[flag.name] = template
        return Template(template_dict)

    @classmethod
    def deserialize(cls, ctx_obj, val, pod=False):
        return cls._deserialize_template(cls._build_template(ctx_obj[cls.FLAG_FIELD]), val, pod)

    @classmethod
    def serialize(cls, ctx_obj, val):
        return cls._serialize_template(cls._build_template(ctx_obj[cls.FLAG_FIELD]), val)


class SimpleSubfieldSerializer(BaseSubfieldSerializer):
    TEMPLATE: SerializableBase
    EMPTY_IS_NONE = False

    @classmethod
    def deserialize(cls, ctx_obj, val, pod=False):
        if val == b"" and cls.EMPTY_IS_NONE:
            return None
        return cls._deserialize_template(cls.TEMPLATE, val, pod)

    @classmethod
    def serialize(cls, ctx_obj, vals):
        if cls.EMPTY_IS_NONE and vals is None:
            return b""
        return cls._serialize_template(cls.TEMPLATE, vals)


class AdapterSubfieldSerializer(BaseSubfieldSerializer, abc.ABC):
    ADAPTER: Adapter

    @classmethod
    def serialize(cls, ctx_obj, val):
        return cls.ADAPTER.encode(val, ctx=ParseContext(ctx_obj))

    @classmethod
    def deserialize(cls, ctx_obj, val, pod=False):
        return cls.ADAPTER.decode(val, ctx=ParseContext(ctx_obj), pod=pod)


class AdapterInstanceSubfieldSerializer(BaseSubfieldSerializer, abc.ABC):
    def __init__(self, adapter: Adapter):
        self._adapter = adapter

    def serialize(self, ctx_obj, val):
        return self._adapter.encode(val, ctx=ParseContext(ctx_obj))

    def deserialize(self, ctx_obj, val, pod=False):
        return self._adapter.decode(val, ctx=ParseContext(ctx_obj), pod=pod)


class IntEnumSubfieldSerializer(AdapterInstanceSubfieldSerializer):
    ORIG_INLINE = True

    def __init__(self, enum_cls: Type[enum.IntEnum]):
        super().__init__(IntEnum(enum_cls))

    def deserialize(self, ctx_obj, val, pod=False):
        val = super().deserialize(ctx_obj, val, pod=pod)
        # Don't pretend we were able to deserialize this if we
        # had to fall through to the `int` case.
        if pod and type(val) == int:
            return UNSERIALIZABLE
        return val


class IntFlagSubfieldSerializer(AdapterInstanceSubfieldSerializer):
    ORIG_INLINE = True
    AS_HEX = True

    def __init__(self, flag_cls: Type[enum.IntFlag]):
        super().__init__(IntFlag(flag_cls))


def http_serializer(msg_name):
    def f(orig_cls):
        global HTTP_SERIALIZERS
        HTTP_SERIALIZERS[msg_name] = orig_cls
        return orig_cls
    return f


class BaseHTTPSerializer(abc.ABC):
    @classmethod
    def serialize_req_body(cls, method: str, body: Any) -> Union[bytes, _Unserializable]:
        return UNSERIALIZABLE

    @classmethod
    def deserialize_req_body(cls, method: str, body: bytes) -> Union[Any, _Unserializable]:
        return UNSERIALIZABLE

    @classmethod
    def serialize_resp_body(cls, method: str, body: Any) -> Union[bytes, _Unserializable]:  # noqa
        return UNSERIALIZABLE

    @classmethod
    def deserialize_resp_body(cls, method: str, body: bytes) -> Union[Any, _Unserializable]:
        return UNSERIALIZABLE
