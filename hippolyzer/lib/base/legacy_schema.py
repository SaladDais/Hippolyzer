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


class SchemaDate(SchemaFieldSerializer[dt.datetime]):
    @classmethod
    def deserialize(cls, val: str) -> dt.datetime:
        return dt.datetime.utcfromtimestamp(int(val))

    @classmethod
    def serialize(cls, val: dt.datetime) -> str:
        return str(calendar.timegm(val.utctimetuple()))


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
                 repr=True, hash=None, compare=True) -> dataclasses.Field:  # noqa
    """Describe a field in the inventory schema and the shape of its value"""
    return dataclasses.field(
        metadata={"spec": spec}, default=default, init=init, repr=repr, hash=hash, compare=compare
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
    def _fields_dict(cls):
        return {f.name: f for f in dataclasses.fields(cls)}

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

    def to_bytes(self) -> bytes:
        return self.to_str().encode("utf8")

    def to_str(self) -> str:
        writer = StringIO()
        self.to_writer(writer)
        writer.seek(0)
        return writer.read()

    @abc.abstractmethod
    def to_writer(self, writer: StringIO):
        pass

    @classmethod
    def _obj_from_dict(cls, obj_dict: Dict):
        return cls(**obj_dict)  # type: ignore
