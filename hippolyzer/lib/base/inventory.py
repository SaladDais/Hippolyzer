"""
Parse the horrible legacy inventory-related format.

It's typically only used for object contents now.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import logging
import struct
import typing
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


class SchemaFlagField(SchemaHexInt):
    """Like a hex int, but must be serialized as bytes in LLSD due to being a U32"""
    @classmethod
    def from_llsd(cls, val: Any) -> int:
        return struct.unpack("!I", val)[0]

    @classmethod
    def to_llsd(cls, val: int) -> Any:
        return struct.pack("!I", val)


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

        fields = cls._get_fields_dict()
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
        for field_name, field in self._get_fields_dict().items():
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


class InventoryDifferences(typing.NamedTuple):
    changed: List[InventoryNodeBase]
    removed: List[InventoryNodeBase]


class InventoryModel(InventoryBase):
    def __init__(self):
        self.nodes: Dict[UUID, InventoryNodeBase] = {}
        self.root: Optional[InventoryContainerBase] = None

    @classmethod
    def from_reader(cls, reader: StringIO, read_header=False) -> InventoryModel:
        model = cls()
        for key, value in _yield_schema_tokens(reader):
            if key == "inv_object":
                obj = InventoryObject.from_reader(reader)
                if obj is not None:
                    model.add(obj)
            elif key == "inv_category":
                cat = InventoryCategory.from_reader(reader)
                if cat is not None:
                    model.add(cat)
            elif key == "inv_item":
                item = InventoryItem.from_reader(reader)
                if item is not None:
                    model.add(item)
            else:
                LOG.warning("Unknown key {0}".format(key))
        return model

    @classmethod
    def from_llsd(cls, llsd_val: List[Dict]) -> InventoryModel:
        model = cls()
        for obj_dict in llsd_val:
            if InventoryCategory.ID_ATTR in obj_dict:
                if (obj := InventoryCategory.from_llsd(obj_dict)) is not None:
                    model.add(obj)
            elif InventoryObject.ID_ATTR in obj_dict:
                if (obj := InventoryObject.from_llsd(obj_dict)) is not None:
                    model.add(obj)
            elif InventoryItem.ID_ATTR in obj_dict:
                if (obj := InventoryItem.from_llsd(obj_dict)) is not None:
                    model.add(obj)
            else:
                LOG.warning(f"Unknown object type {obj_dict!r}")
        return model

    @property
    def ordered_nodes(self) -> Iterable[InventoryNodeBase]:
        yield from self.all_containers
        yield from self.all_items

    @property
    def all_containers(self) -> Iterable[InventoryContainerBase]:
        for node in self.nodes.values():
            if isinstance(node, InventoryContainerBase):
                yield node

    @property
    def all_items(self) -> Iterable[InventoryItem]:
        for node in self.nodes.values():
            if not isinstance(node, InventoryContainerBase):
                yield node

    def __eq__(self, other):
        if not isinstance(other, InventoryModel):
            return False
        return set(self.nodes.values()) == set(other.nodes.values())

    def to_writer(self, writer: StringIO):
        for node in self.ordered_nodes:
            node.to_writer(writer)

    def to_llsd(self):
        return list(node.to_llsd() for node in self.ordered_nodes)

    def add(self, node: InventoryNodeBase):
        if node.node_id in self.nodes:
            raise KeyError(f"{node.node_id} already exists in the inventory model")

        self.nodes[node.node_id] = node
        if isinstance(node, InventoryContainerBase):
            if node.parent_id == UUID.ZERO:
                self.root = node
        node.model = weakref.proxy(self)

    def unlink(self, node: InventoryNodeBase) -> Sequence[InventoryNodeBase]:
        """Unlink a node and its descendants from the tree, returning the removed nodes"""
        assert node.model == self
        if node == self.root:
            self.root = None
        unlinked = [node]
        if isinstance(node, InventoryContainerBase):
            for child in node.children:
                unlinked.extend(self.unlink(child))
        self.nodes.pop(node.node_id, None)
        node.model = None
        return unlinked

    def get_differences(self, other: InventoryModel) -> InventoryDifferences:
        # Includes modified things with the same ID
        changed_in_other = []
        removed_in_other = []

        other_keys = set(other.nodes.keys())
        our_keys = set(self.nodes.keys())

        # Removed
        for key in our_keys - other_keys:
            removed_in_other.append(self.nodes[key])

        # Updated
        for key in other_keys.intersection(our_keys):
            other_node = other.nodes[key]
            if other_node != self.nodes[key]:
                changed_in_other.append(other_node)

        # Added
        for key in other_keys - our_keys:
            changed_in_other.append(other.nodes[key])
        return InventoryDifferences(
            changed=changed_in_other,
            removed=removed_in_other,
        )


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

    name: str

    parent_id: Optional[UUID] = schema_field(SchemaUUID)
    model: Optional[InventoryModel] = dataclasses.field(
        default=None, init=False, hash=False, compare=False, repr=False
    )

    @property
    def node_id(self) -> UUID:
        return getattr(self, self.ID_ATTR)

    @node_id.setter
    def node_id(self, val: UUID):
        setattr(self, self.ID_ATTR, val)

    @property
    def parent(self) -> Optional[InventoryContainerBase]:
        return self.model.nodes.get(self.parent_id)

    def unlink(self) -> Sequence[InventoryNodeBase]:
        return self.model.unlink(self)

    @classmethod
    def _obj_from_dict(cls, obj_dict):
        # Bad entry, ignore
        # TODO: Check on these. might be symlinks or something.
        if obj_dict.get("type") == "-1":
            LOG.warning(f"Skipping bad object with type == -1: {obj_dict!r}")
            return None
        return super()._obj_from_dict(obj_dict)

    def __hash__(self):
        return hash(self.node_id)

    def __iter__(self) -> Iterator[InventoryNodeBase]:
        return iter(())

    def __contains__(self, item) -> bool:
        return item in tuple(self)


@dataclasses.dataclass
class InventoryContainerBase(InventoryNodeBase):
    type: str = schema_field(SchemaStr)
    name: str = schema_field(SchemaMultilineStr)

    @property
    def children(self) -> Sequence[InventoryNodeBase]:
        return tuple(
            x for x in self.model.nodes.values()
            if x.parent_id == self.node_id
        )

    def __getitem__(self, item: Union[int, str]) -> InventoryNodeBase:
        if isinstance(item, int):
            return self.children[item]

        for child in self.children:
            if child.name == item:
                return child
        raise KeyError(f"{item!r} not found in children")

    def __iter__(self) -> Iterator[InventoryNodeBase]:
        return iter(self.children)

    def get_or_create_subcategory(self, name: str) -> InventoryCategory:
        for child in self:
            if child.name == name and isinstance(child, InventoryCategory):
                return child
        child = InventoryCategory(
            name=name,
            cat_id=UUID.random(),
            parent_id=self.node_id,
            type="category",
            pref_type="-1",
            owner_id=getattr(self, 'owner_id', UUID.ZERO),
            version=1,
        )
        self.model.add(child)
        return child

    # So autogenerated __hash__ doesn't kill our inherited one
    __hash__ = InventoryNodeBase.__hash__


@dataclasses.dataclass
class InventoryObject(InventoryContainerBase):
    SCHEMA_NAME: ClassVar[str] = "inv_object"
    ID_ATTR: ClassVar[str] = "obj_id"

    obj_id: UUID = schema_field(SchemaUUID)

    __hash__ = InventoryNodeBase.__hash__


@dataclasses.dataclass
class InventoryCategory(InventoryContainerBase):
    ID_ATTR: ClassVar[str] = "cat_id"
    SCHEMA_NAME: ClassVar[str] = "inv_category"

    cat_id: UUID = schema_field(SchemaUUID)
    pref_type: str = schema_field(SchemaStr, llsd_name="preferred_type")
    owner_id: UUID = schema_field(SchemaUUID)
    version: int = schema_field(SchemaInt)

    __hash__ = InventoryNodeBase.__hash__


@dataclasses.dataclass
class InventoryItem(InventoryNodeBase):
    SCHEMA_NAME: ClassVar[str] = "inv_item"
    ID_ATTR: ClassVar[str] = "item_id"

    item_id: UUID = schema_field(SchemaUUID)
    type: str = schema_field(SchemaStr)
    inv_type: str = schema_field(SchemaStr)
    flags: int = schema_field(SchemaFlagField)
    name: str = schema_field(SchemaMultilineStr)
    desc: str = schema_field(SchemaMultilineStr)
    creation_date: dt.datetime = schema_field(SchemaDate, llsd_name="created_at")
    permissions: InventoryPermissions = schema_field(InventoryPermissions)
    sale_info: InventorySaleInfo = schema_field(InventorySaleInfo)
    asset_id: Optional[UUID] = schema_field(SchemaUUID, default=None)
    shadow_id: Optional[UUID] = schema_field(SchemaUUID, default=None)

    __hash__ = InventoryNodeBase.__hash__

    @property
    def true_asset_id(self) -> UUID:
        if self.asset_id is not None:
            return self.asset_id
        return self.shadow_id ^ MAGIC_ID
