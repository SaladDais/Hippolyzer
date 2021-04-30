import dataclasses
from typing import *

import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base.datatypes import UUID, Vector3, StringEnum
from hippolyzer.lib.base.multidict import OrderedMultiDict


class NameValueType(StringEnum):
    Null = 'NULL'
    String = 'STRING'
    F32 = 'F32'
    S32 = 'S32'
    Vector3 = 'VEC3'
    U32 = 'U32'
    CAMERA = 'CAMERA'  # Obsolete
    Asset = 'ASSET'
    U64 = 'U64'


class NameValueClass(StringEnum):
    Null = 'NULL'
    ReadOnly = 'R'
    ReadWrite = 'RW'


class NameValueSendTo(StringEnum):
    Null = 'NULL'
    Sim = 'S'
    DataSim = 'DS'
    SimViewer = 'SV'
    DataSimViewer = 'DSV'


NV_FIELD_SPEC = se.CStr(terminators=(b" ", b"\t", b"\r", b"\n"))
NV_VALUE_SPEC = se.CStr(terminators=(b"\n",), write_terminator=False)


def _string_enum_field(enum_cls: Type) -> dataclasses.Field:
    return se.dataclass_field(se.StringEnumAdapter(enum_cls, NV_FIELD_SPEC))


@dataclasses.dataclass
class NameValue:
    name: str = se.dataclass_field(NV_FIELD_SPEC)
    type: NameValueType = _string_enum_field(NameValueType)
    rw: NameValueClass = _string_enum_field(NameValueClass)
    sendto: NameValueSendTo = _string_enum_field(NameValueSendTo)
    value: str = se.dataclass_field(NV_VALUE_SPEC)

    def deserialize(self) -> Any:
        # Since the floating-point data has a string representation
        # we want to keep it in string format unless deserialization is specifically
        # requested, so we don't lose precision and change the string representation
        # when round-tripping
        return {
            NameValueType.Null: lambda x: x,
            NameValueType.String: lambda x: x,
            NameValueType.F32: lambda x: float(x),
            NameValueType.S32: lambda x: int(x),
            NameValueType.U32: lambda x: int(x),
            NameValueType.U64: lambda x: int(x),
            NameValueType.CAMERA: lambda x: x,
            NameValueType.Vector3: lambda x: Vector3.parse(x),
            NameValueType.Asset: lambda x: UUID(x),
        }[self.type](self.value)

    def serialize(self, val):
        self.value = str(val)

    def __str__(self):
        return f"{self.name} {self.type} {self.rw} {self.sendto} {self.value}"


class NameValueCollection(List[NameValue]):
    def to_dict(self) -> Dict[str, Any]:
        return OrderedMultiDict(
            (v.name, v.deserialize()) for v in self
        )

    def __str__(self):
        return "\n".join(str(x) for x in self)


class NameValueSerializer(se.Dataclass):
    def __init__(self):
        super().__init__(NameValue)

    def serialize(self, val, writer: se.BufferWriter, ctx=None):
        if isinstance(val, str):
            # POD form allows a bare string representation of a namevalue
            writer.write_bytes(val.encode("utf8"))
        else:
            super().serialize(val, writer, ctx)

    def deserialize(self, reader: se.Reader, ctx=None):
        val = super().deserialize(reader, ctx)
        if reader.pod:
            return str(NameValue(**val))
        return val


NV_SERIALIZER = NameValueSerializer()


class NameValuesSerializer(se.SerializableBase):
    @classmethod
    def serialize(cls, vals, writer: se.BufferWriter, ctx=None):
        first_elem = True
        for val in vals:
            if not first_elem:
                writer.write_bytes(b"\n")
            writer.write(NV_SERIALIZER, val, ctx=ctx)
            first_elem = False

    @classmethod
    def deserialize(cls, reader: se.Reader, ctx=None):
        entries = NameValueCollection()
        while reader:
            entries.append(reader.read(NV_SERIALIZER, ctx=ctx))
        return entries
