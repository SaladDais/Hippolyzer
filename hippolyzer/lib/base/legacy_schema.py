"""
Legacy line-oriented schema parser base classes

Used for task inventory and wearables.
"""
from __future__ import annotations

import abc
import calendar
import dataclasses
import datetime as dt
import logging
import re
from io import StringIO
from typing import *

from hippolyzer.lib.base.datatypes import UUID

LOG = logging.getLogger(__name__)
_T = TypeVar("_T")


class SchemaFieldSerializer(abc.ABC, Generic[_T]):
    @classmethod
    @abc.abstractmethod
    def deserialize(cls, val: str) -> _T:
        pass

    @classmethod
    @abc.abstractmethod
    def serialize(cls, val: _T) -> str:
        pass

    @classmethod
    def from_llsd(cls, val: Any) -> _T:
        return val

    @classmethod
    def to_llsd(cls, val: _T) -> Any:
        return val


class SchemaDate(SchemaFieldSerializer[dt.datetime]):
    @classmethod
    def deserialize(cls, val: str) -> dt.datetime:
        return dt.datetime.utcfromtimestamp(int(val))

    @classmethod
    def serialize(cls, val: dt.datetime) -> str:
        return str(calendar.timegm(val.utctimetuple()))

    @classmethod
    def from_llsd(cls, val: Any) -> dt.datetime:
        return dt.datetime.utcfromtimestamp(val)

    @classmethod
    def to_llsd(cls, val: dt.datetime):
        return calendar.timegm(val.utctimetuple())


class SchemaHexInt(SchemaFieldSerializer[int]):
    @classmethod
    def deserialize(cls, val: str) -> int:
        return int(val, 16)

    @classmethod
    def serialize(cls, val: int) -> str:
        return "%08x" % val


class SchemaInt(SchemaFieldSerializer[int]):
    @classmethod
    def deserialize(cls, val: str) -> int:
        return int(val)

    @classmethod
    def serialize(cls, val: int) -> str:
        return str(val)


class SchemaMultilineStr(SchemaFieldSerializer[str]):
    @classmethod
    def deserialize(cls, val: str) -> str:
        # llinventory claims that it will parse multiple lines until it finds
        # an "|" terminator. That's not true. Use llinventory's _actual_ behaviour.
        return val.partition("|")[0]

    @classmethod
    def serialize(cls, val: str) -> str:
        return val + "|"


class SchemaStr(SchemaFieldSerializer[str]):
    @classmethod
    def deserialize(cls, val: str) -> str:
        return val

    @classmethod
    def serialize(cls, val: str) -> str:
        return val


class SchemaUUID(SchemaFieldSerializer[UUID]):
    @classmethod
    def deserialize(cls, val: str) -> UUID:
        return UUID(val)

    @classmethod
    def serialize(cls, val: UUID) -> str:
        return str(val)


def schema_field(spec: Type[Union[SchemaBase, SchemaFieldSerializer]], *, default=dataclasses.MISSING, init=True,
                 repr=True, hash=None, compare=True, llsd_name=None) -> dataclasses.Field:  # noqa
    """Describe a field in the inventory schema and the shape of its value"""
    return dataclasses.field(
        metadata={"spec": spec, "llsd_name": llsd_name}, default=default,
        init=init, repr=repr, hash=hash, compare=compare,
    )


class SchemaParsingError(Exception):
    pass


# The schema is meant to allow multi-line strings, but in practice
# it does not due to scanf() shenanigans. This is fine.
_SCHEMA_LINE_TOKENS_RE = re.compile(r'\A\s*([^\s]+)(\s+([^\t\r\n]+))?$')


def parse_schema_line(line: str):
    g = _SCHEMA_LINE_TOKENS_RE.search(line)
    if not g:
        raise SchemaParsingError(f"{line!r} doesn't match the token regex")
    return g.group(1), g.group(3)


@dataclasses.dataclass
class SchemaBase(abc.ABC):
    @classmethod
    def _get_fields_dict(cls, llsd=False):
        fields_dict = {}
        for field in dataclasses.fields(cls):
            field_name = field.name
            if llsd:
                field_name = field.metadata.get("llsd_name") or field_name
            fields_dict[field_name] = field
        return fields_dict

    @classmethod
    def from_str(cls, text: str):
        return cls.from_reader(StringIO(text))

    @classmethod
    @abc.abstractmethod
    def from_reader(cls: Type[_T], reader: StringIO) -> _T:
        pass

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls.from_str(data.decode("utf8"))

    @classmethod
    def from_llsd(cls, inv_dict: Dict):
        fields = cls._get_fields_dict(llsd=True)
        obj_dict = {}
        for key, val in inv_dict.items():
            if key in fields:
                field: dataclasses.Field = fields[key]
                key = field.name
                spec = field.metadata.get("spec")
                # Not a real key, an internal var on our dataclass
                if not spec:
                    LOG.warning(f"Internal key {key!r}")
                    continue
                # some kind of nested structure like sale_info
                if issubclass(spec, SchemaBase):
                    obj_dict[key] = spec.from_llsd(val)
                elif issubclass(spec, SchemaFieldSerializer):
                    obj_dict[key] = spec.from_llsd(val)
                else:
                    raise ValueError(f"Unsupported spec for {key!r}, {spec!r}")
            else:
                LOG.warning(f"Unknown key {key!r}")
        return cls._obj_from_dict(obj_dict)

    def to_bytes(self) -> bytes:
        return self.to_str().encode("utf8")

    def to_str(self) -> str:
        writer = StringIO()
        self.to_writer(writer)
        writer.seek(0)
        return writer.read()

    def to_llsd(self):
        obj_dict = {}
        for field_name, field in self._get_fields_dict(llsd=True).items():
            spec = field.metadata.get("spec")
            # Not meant to be serialized
            if not spec:
                continue

            val = getattr(self, field.name)
            if val is None:
                continue

            # Some kind of nested structure like sale_info
            if isinstance(val, SchemaBase):
                val = val.to_llsd()
            elif issubclass(spec, SchemaFieldSerializer):
                val = spec.to_llsd(val)
            else:
                raise ValueError(f"Bad inventory spec {spec!r}")
            obj_dict[field_name] = val
        return obj_dict

    @abc.abstractmethod
    def to_writer(self, writer: StringIO):
        pass

    @classmethod
    def _obj_from_dict(cls, obj_dict: Dict):
        return cls(**obj_dict)  # type: ignore
