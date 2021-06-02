"""
Parse the horrible legacy inventory-related format.

It's typically only used for object contents now.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import itertools
import logging
import weakref
from io import StringIO
from typing import *

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.legacy_schema import (
    parse_schema_line,
    SchemaBase,
    SchemaDate,
    SchemaFieldSerializer,
    SchemaHexInt,
    SchemaInt,
    SchemaMultilineStr,
    SchemaParsingError,
    SchemaStr,
    SchemaUUID,
    schema_field,
)

MAGIC_ID = UUID("3c115e51-04f4-523c-9fa6-98aff1034730")
LOG = logging.getLogger(__name__)
_T = TypeVar("_T")


def _yield_schema_tokens(reader: StringIO):
    in_bracket = False
    # empty str == EOF in Python
    while line := reader.readline():
        line = line.strip()
        # Whitespace-only lines are automatically skipped
        if not line:
            continue
        try:
            key, val = parse_schema_line(line)
        except SchemaParsingError:
            # Can happen if there's a malformed multi-line string, just
            # skip by it.
            LOG.warning(f"Found invalid inventory line {line!r}")
            continue
        if key == "{":
            if in_bracket:
                LOG.warning("Found multiple opening brackets inside structure, "
                            "was a nested structure not handled?")
            in_bracket = True
            continue
        if key == "}":
            if not in_bracket:
                LOG.warning("Unexpected closing bracket")
            in_bracket = False
            break
        yield key, val
    if in_bracket:
        LOG.warning("Reached EOF while inside a bracket")


class InventoryBase(SchemaBase):
    SCHEMA_NAME: ClassVar[str]

    @classmethod
    def from_reader(cls, reader: StringIO, read_header=False) -> InventoryBase:
        tok_iter = _yield_schema_tokens(reader)
        # Someone else hasn't already read the header for us
        if read_header:
            schema_name, _ = next(tok_iter)
            if schema_name != cls.SCHEMA_NAME:
                raise ValueError(f"Expected schema name {schema_name!r} to be {cls.SCHEMA_NAME!r}")

        fields = cls._fields_dict()
        obj_dict = {}
        for key, val in tok_iter:
            if key in fields:
                field: dataclasses.Field = fields[key]
                spec = field.metadata.get("spec")
                # Not a real key, an internal var on our dataclass
                if not spec:
                    LOG.warning(f"Internal key {key!r}")
                    continue
                # some kind of nested structure like sale_info
                if issubclass(spec, SchemaBase):
                    obj_dict[key] = spec.from_reader(reader)
                elif issubclass(spec, SchemaFieldSerializer):
                    obj_dict[key] = spec.deserialize(val)
                else:
                    raise ValueError(f"Unsupported spec for {key!r}, {spec!r}")
            else:
                LOG.warning(f"Unknown key {key!r}")
        return cls._obj_from_dict(obj_dict)

    def to_writer(self, writer: StringIO):
        writer.write(f"\t{self.SCHEMA_NAME}\t0\n")
        writer.write("\t{\n")
        for field_name, field in self._fields_dict().items():
            spec = field.metadata.get("spec")
            # Not meant to be serialized
            if not spec:
                continue

            val = getattr(self, field_name)
            if val is None:
                continue

            # Some kind of nested structure like sale_info
            if isinstance(val, SchemaBase):
                val.to_writer(writer)
            elif issubclass(spec, SchemaFieldSerializer):
                writer.write(f"\t\t{field_name}\t{spec.serialize(val)}\n")
            else:
                raise ValueError(f"Bad inventory spec {spec!r}")
        writer.write("\t}\n")


class InventoryModel(InventoryBase):
    def __init__(self):
        self.containers: Dict[UUID, InventoryContainerBase] = {}
        self.items: Dict[UUID, InventoryItem] = {}
        self.root: Optional[InventoryContainerBase] = None

    @classmethod
    def from_reader(cls, reader: StringIO, read_header=False) -> InventoryModel:
        model = cls()
        for key, value in _yield_schema_tokens(reader):
            if key == "inv_object":
                obj = InventoryObject.from_reader(reader)
                if obj is not None:
                    model.add_container(obj)
            elif key == "inv_category":
                cat = InventoryCategory.from_reader(reader)
                if cat is not None:
                    model.add_container(cat)
            elif key == "inv_item":
                item = InventoryItem.from_reader(reader)
                if item is not None:
                    model.add_item(item)
            else:
                LOG.warning("Unknown key {0}".format(key))
        model.reparent_nodes()
        return model

    def to_writer(self, writer: StringIO):
        for container in self.containers.values():
            container.to_writer(writer)
        for item in self.items.values():
            item.to_writer(writer)

    def add_container(self, container: InventoryContainerBase):
        self.containers[container.node_id] = container
        container.model = weakref.proxy(self)

    def add_item(self, item: InventoryItem):
        self.items[item.item_id] = item
        item.model = weakref.proxy(self)

    def reparent_nodes(self):
        self.root = None
        for container in self.containers.values():
            container.children.clear()
            if container.parent_id == UUID():
                self.root = container
        for obj in itertools.chain(self.items.values(), self.containers.values()):
            if not obj.parent_id or obj.parent_id == UUID():
                continue
            parent_container = self.containers.get(obj.parent_id)
            if not parent_container:
                LOG.warning("{0} had an invalid parent {1}".format(obj, obj.parent_id))
                continue
            parent_container.children.append(obj)


@dataclasses.dataclass
class InventoryPermissions(InventoryBase):
    SCHEMA_NAME: ClassVar[str] = "permissions"

    base_mask: int = schema_field(SchemaHexInt)
    owner_mask: int = schema_field(SchemaHexInt)
    group_mask: int = schema_field(SchemaHexInt)
    everyone_mask: int = schema_field(SchemaHexInt)
    next_owner_mask: int = schema_field(SchemaHexInt)
    creator_id: UUID = schema_field(SchemaUUID)
    owner_id: UUID = schema_field(SchemaUUID)
    last_owner_id: UUID = schema_field(SchemaUUID)
    group_id: UUID = schema_field(SchemaUUID)


@dataclasses.dataclass
class InventorySaleInfo(InventoryBase):
    SCHEMA_NAME: ClassVar[str] = "sale_info"

    sale_type: str = schema_field(SchemaStr)
    sale_price: int = schema_field(SchemaInt)


@dataclasses.dataclass
class InventoryNodeBase(InventoryBase):
    ID_ATTR: ClassVar[str]

    parent_id: Optional[UUID] = schema_field(SchemaUUID)
    model: Optional[InventoryModel] = dataclasses.field(default=None, init=False)

    @property
    def node_id(self) -> UUID:
        return getattr(self, self.ID_ATTR)

    @property
    def parent(self):
        return self.model.containers.get(self.parent_id)

    @classmethod
    def _obj_from_dict(cls, obj_dict):
        # Bad entry, ignore
        # TODO: Check on these. might be symlinks or something.
        if obj_dict.get("type") == "-1":
            LOG.warning(f"Skipping bad object with type == -1: {obj_dict!r}")
            return None
        return super()._obj_from_dict(obj_dict)


@dataclasses.dataclass
class InventoryContainerBase(InventoryNodeBase):
    type: str = schema_field(SchemaStr)
    name: str = schema_field(SchemaMultilineStr)
    children: List[InventoryNodeBase] = dataclasses.field(default_factory=list, init=False)


@dataclasses.dataclass
class InventoryObject(InventoryContainerBase):
    SCHEMA_NAME: ClassVar[str] = "inv_object"
    ID_ATTR: ClassVar[str] = "obj_id"

    obj_id: UUID = schema_field(SchemaUUID)


@dataclasses.dataclass
class InventoryCategory(InventoryContainerBase):
    ID_ATTR: ClassVar[str] = "cat_id"
    SCHEMA_NAME: ClassVar[str] = "inv_object"

    cat_id: UUID = schema_field(SchemaUUID)
    pref_type: str = schema_field(SchemaStr)
    owner_id: UUID = schema_field(SchemaUUID)
    version: int = schema_field(SchemaInt)


@dataclasses.dataclass
class InventoryItem(InventoryNodeBase):
    SCHEMA_NAME: ClassVar[str] = "inv_item"
    ID_ATTR: ClassVar[str] = "item_id"

    item_id: UUID = schema_field(SchemaUUID)
    type: str = schema_field(SchemaStr)
    inv_type: str = schema_field(SchemaStr)
    flags: int = schema_field(SchemaHexInt)
    name: str = schema_field(SchemaMultilineStr)
    desc: str = schema_field(SchemaMultilineStr)
    creation_date: dt.datetime = schema_field(SchemaDate)
    permissions: InventoryPermissions = schema_field(InventoryPermissions)
    sale_info: InventorySaleInfo = schema_field(InventorySaleInfo)
    asset_id: Optional[UUID] = schema_field(SchemaUUID, default=None)
    shadow_id: Optional[UUID] = schema_field(SchemaUUID, default=None)

    @property
    def true_asset_id(self) -> UUID:
        if self.asset_id is not None:
            return self.asset_id
        return self.shadow_id ^ MAGIC_ID
