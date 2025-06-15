"""
Parse the horrible legacy inventory-related format.

It's typically only used for object contents now.
"""

# TODO: Maybe handle CRC calculation? Does anything care about that?
#  I don't think anything in the viewer actually looks at the result
#  of the CRC check for UDP stuff.

from __future__ import annotations

import abc
import asyncio
import dataclasses
import datetime as dt
import inspect
import logging
import secrets
import struct
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
    SchemaLLSD,
    SchemaMultilineStr,
    SchemaParsingError,
    SchemaStr,
    SchemaUUID,
    schema_field,
)
from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.templates import SaleType, InventoryType, LookupIntEnum, AssetType, FolderType

MAGIC_ID = UUID("3c115e51-04f4-523c-9fa6-98aff1034730")
LOG = logging.getLogger(__name__)
_T = TypeVar("_T")


class SchemaFlagField(SchemaHexInt):
    """Like a hex int, but must be serialized as bytes in LLSD due to being a U32"""
    @classmethod
    def from_llsd(cls, val: Any, flavor: str) -> int:
        # Sometimes values in S32 range will just come through normally
        if isinstance(val, int):
            return val

        if flavor == "legacy":
            return struct.unpack("!I", val)[0]
        return val

    @classmethod
    def to_llsd(cls, val: int, flavor: str) -> Any:
        if flavor == "legacy":
            return struct.pack("!I", val)
        return val


class SchemaEnumField(SchemaStr, Generic[_T]):
    def __init__(self, enum_cls: Type[LookupIntEnum]):
        super().__init__()
        self._enum_cls = enum_cls

    def deserialize(self, val: str) -> _T:
        return self._enum_cls.from_lookup_name(val)

    def serialize(self, val: _T) -> str:
        return self._enum_cls(val).to_lookup_name()

    def from_llsd(self, val: Union[str, int], flavor: str) -> _T:
        if flavor == "legacy":
            return self.deserialize(val)
        return self._enum_cls(val)

    def to_llsd(self, val: _T, flavor: str) -> Union[int, str]:
        if flavor == "legacy":
            return self.serialize(val)
        return int(val)


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

                spec_cls = spec
                if not inspect.isclass(spec_cls):
                    spec_cls = spec_cls.__class__
                # some kind of nested structure like sale_info
                if issubclass(spec_cls, SchemaBase):
                    obj_dict[key] = spec.from_reader(reader)
                elif issubclass(spec_cls, SchemaFieldSerializer):
                    obj_dict[key] = spec.deserialize(val)
                else:
                    raise ValueError(f"Unsupported spec for {key!r}, {spec!r}")
            else:
                LOG.warning(f"Unknown key {key!r}")
        return cls._obj_from_dict(obj_dict)

    def to_writer(self, writer: StringIO):
        writer.write(f"\t{self.SCHEMA_NAME}")
        if self.SCHEMA_NAME == "permissions":
            writer.write(" 0\n")
        else:
            writer.write("\t0\n")
        writer.write("\t{\n")

        # Make sure the ID field always comes first, if there is one.
        fields_dict: Dict[str, dataclasses.Field] = {}
        if hasattr(self, "ID_ATTR"):
            fields_dict = {getattr(self, "ID_ATTR"): dataclasses.field()}
        # update()ing will put all fields that aren't yet in the dict after the ID attr.
        fields_dict.update(self._get_fields_dict())

        for field_name, field in fields_dict.items():
            spec = field.metadata.get("spec")
            # Not meant to be serialized
            if not spec:
                continue
            if field.metadata.get("llsd_only"):
                continue

            val = getattr(self, field_name)
            if val is None and not field.metadata.get("include_none"):
                continue

            spec_cls = spec
            if not inspect.isclass(spec_cls):
                spec_cls = spec_cls.__class__
            # Some kind of nested structure like sale_info
            if isinstance(val, SchemaBase):
                val.to_writer(writer)
            elif issubclass(spec_cls, SchemaFieldSerializer):
                writer.write(f"\t\t{field_name}\t{spec.serialize(val)}\n")
            else:
                raise ValueError(f"Bad inventory spec {spec!r}")
        writer.write("\t}\n")


class InventoryDifferences(NamedTuple):
    changed: List[InventoryNodeBase]
    removed: List[InventoryNodeBase]


class InventoryModel(InventoryBase):
    def __init__(self):
        self.nodes: Dict[UUID, InventoryNodeBase] = {}
        self.root: Optional[InventoryContainerBase] = None
        self.any_dirty = asyncio.Event()

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
    def from_llsd(cls, llsd_val: List[Dict], flavor: str = "legacy") -> Self:
        model = cls()
        for obj_dict in llsd_val:
            obj = None
            for inv_type in INVENTORY_TYPES:
                if inv_type.ID_ATTR in obj_dict:
                    if (obj := inv_type.from_llsd(obj_dict, flavor)) is not None:
                        model.add(obj)
                    break
            if obj is None:
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
    def dirty_categories(self) -> Iterable[InventoryCategory]:
        for node in self.nodes:
            if isinstance(node, InventoryCategory) and node.version == InventoryCategory.VERSION_NONE:
                yield node

    @property
    def all_items(self) -> Iterable[InventoryItem]:
        for node in self.nodes.values():
            if not isinstance(node, InventoryContainerBase):
                yield node  # type: ignore

    def __eq__(self, other):
        if not isinstance(other, InventoryModel):
            return False
        return set(self.nodes.values()) == set(other.nodes.values())

    def to_writer(self, writer: StringIO):
        for node in self.ordered_nodes:
            node.to_writer(writer)

    def to_llsd(self, flavor: str = "legacy"):
        return list(node.to_llsd(flavor) for node in self.ordered_nodes)

    def add(self, node: InventoryNodeBase):
        if node.node_id in self.nodes:
            raise KeyError(f"{node.node_id} already exists in the inventory model")

        self.nodes[node.node_id] = node
        if isinstance(node, InventoryContainerBase):
            if node.parent_id == UUID.ZERO:
                self.root = node
        node.model = weakref.proxy(self)
        return node

    def update(self, node: InventoryNodeBase, update_fields: Optional[Iterable[str]] = None) -> InventoryNodeBase:
        """Update an existing node, optionally only updating specific fields"""
        if node.node_id not in self.nodes:
            raise KeyError(f"{node.node_id} not in the inventory model")

        orig_node = self.nodes[node.node_id]
        if node.__class__ != orig_node.__class__:
            raise ValueError(f"Tried to update {orig_node!r} from non-matching {node!r}")

        if not update_fields:
            # Update everything but the model parameter
            update_fields = node.get_field_names()
        for field_name in update_fields:
            setattr(orig_node, field_name, getattr(node, field_name))
        return orig_node

    def upsert(self, node: InventoryNodeBase, update_fields: Optional[Iterable[str]] = None) -> InventoryNodeBase:
        """Add or update a node"""
        if node.node_id in self.nodes:
            return self.update(node, update_fields)
        return self.add(node)

    def unlink(self, node: InventoryNodeBase, single_only: bool = False) -> Sequence[InventoryNodeBase]:
        """Unlink a node and its descendants from the tree, returning the removed nodes"""
        assert node.model == self
        if node == self.root:
            self.root = None
        unlinked = [node]
        if isinstance(node, InventoryContainerBase) and not single_only:
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

    def flag_if_dirty(self):
        if any(self.dirty_categories):
            self.any_dirty.set()

    def __getitem__(self, item: UUID) -> InventoryNodeBase:
        return self.nodes[item]

    def __contains__(self, item: UUID):
        return item in self.nodes

    def get(self, key: UUID) -> Optional[InventoryNodeBase]:
        return self.nodes.get(key)

    def get_category(self, key: UUID) -> InventoryCategory:
        node = self.get(key)
        if not isinstance(node, InventoryCategory):
            raise ValueError(f"{node!r} is not a category")
        return node

    def get_item(self, key: UUID) -> InventoryItem:
        node = self.get(key)
        if not isinstance(node, InventoryItem):
            raise ValueError(f"{node!r} is not an item")
        return node


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
    # Nothing actually cares about this, but it could be there.
    # It's kind of redundant since it just means owner_id == NULL_KEY && group_id != NULL_KEY.
    is_owner_group: Optional[int] = schema_field(SchemaInt, default=None, llsd_only=True)

    @classmethod
    def make_default(cls) -> Self:
        return cls(
            base_mask=0xFFffFFff,
            owner_mask=0xFFffFFff,
            group_mask=0,
            everyone_mask=0,
            next_owner_mask=0x82000,
            creator_id=UUID.ZERO,
            owner_id=UUID.ZERO,
            last_owner_id=UUID.ZERO,
            group_id=UUID.ZERO,
            is_owner_group=None
        )


@dataclasses.dataclass
class InventorySaleInfo(InventoryBase):
    SCHEMA_NAME: ClassVar[str] = "sale_info"

    sale_type: SaleType = schema_field(SchemaEnumField(SaleType))
    sale_price: int = schema_field(SchemaInt)

    @classmethod
    def make_default(cls) -> Self:
        return cls(sale_type=SaleType.NOT, sale_price=10)


class _HasBaseNodeAttrs(abc.ABC):
    """
    Only exists so that we can assert that all subclasses should have this without forcing
    a particular serialization order, as would happen if this was present on InventoryNodeBase.
    """
    name: str
    type: AssetType


@dataclasses.dataclass
class InventoryNodeBase(InventoryBase, _HasBaseNodeAttrs):
    ID_ATTR: ClassVar[str]

    parent_id: Optional[UUID] = schema_field(SchemaUUID)

    model: Optional[InventoryModel] = dataclasses.field(
        default=None, init=False, hash=False, compare=False, repr=False
    )

    @classmethod
    def get_field_names(cls) -> Set[str]:
        return set(cls._get_fields_dict().keys()) - {"model"}

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
    type: AssetType = schema_field(SchemaEnumField(AssetType))

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
            type=AssetType.CATEGORY,
            pref_type=FolderType.NONE,
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
    name: str = schema_field(SchemaMultilineStr)
    metadata: Optional[Dict[str, Any]] = schema_field(SchemaLLSD, default=None, include_none=True)

    __hash__ = InventoryNodeBase.__hash__


@dataclasses.dataclass
class InventoryCategory(InventoryContainerBase):
    ID_ATTR: ClassVar[str] = "cat_id"
    # AIS calls this something else...
    ID_ATTR_AIS: ClassVar[str] = "category_id"
    SCHEMA_NAME: ClassVar[str] = "inv_category"
    VERSION_NONE: ClassVar[int] = -1

    cat_id: UUID = schema_field(SchemaUUID)
    pref_type: FolderType = schema_field(SchemaEnumField(FolderType), llsd_name="preferred_type")
    name: str = schema_field(SchemaMultilineStr)
    owner_id: Optional[UUID] = schema_field(SchemaUUID, default=None)
    version: int = schema_field(SchemaInt, default=VERSION_NONE, llsd_only=True)
    metadata: Optional[Dict[str, Any]] = schema_field(SchemaLLSD, default=None, include_none=False)

    def to_folder_data(self) -> Block:
        return Block(
            "FolderData",
            FolderID=self.cat_id,
            ParentID=self.parent_id,
            CallbackID=0,
            Type=self.pref_type,
            Name=self.name,
        )

    @classmethod
    def from_folder_data(cls, block: Block):
        return cls(
            cat_id=block["FolderID"],
            parent_id=block["ParentID"],
            pref_type=block["Type"],
            name=block["Name"],
            type=AssetType.CATEGORY,
        )

    @classmethod
    def from_llsd(cls, inv_dict: Dict, flavor: str = "legacy") -> Self:
        if flavor == "ais" and "type" not in inv_dict:
            inv_dict = inv_dict.copy()
            inv_dict["type"] = AssetType.CATEGORY
        return super().from_llsd(inv_dict, flavor)

    def to_llsd(self, flavor: str = "legacy"):
        payload = super().to_llsd(flavor)
        if flavor == "ais":
            # AIS already knows the inventory type is category
            payload.pop("type", None)
        return payload

    @classmethod
    def _get_fields_dict(cls, llsd_flavor: Optional[str] = None):
        fields = super()._get_fields_dict(llsd_flavor)
        if llsd_flavor == "ais":
            # These have different names though
            fields["type_default"] = fields.pop("preferred_type")
            fields["agent_id"] = fields.pop("owner_id")
            fields["category_id"] = fields.pop("cat_id")
        return fields

    __hash__ = InventoryNodeBase.__hash__


@dataclasses.dataclass
class InventoryItem(InventoryNodeBase):
    SCHEMA_NAME: ClassVar[str] = "inv_item"
    ID_ATTR: ClassVar[str] = "item_id"

    item_id: UUID = schema_field(SchemaUUID)
    permissions: InventoryPermissions = schema_field(InventoryPermissions)
    asset_id: Optional[UUID] = schema_field(SchemaUUID, default=None)
    shadow_id: Optional[UUID] = schema_field(SchemaUUID, default=None)
    type: Optional[AssetType] = schema_field(SchemaEnumField(AssetType), default=None)
    inv_type: Optional[InventoryType] = schema_field(SchemaEnumField(InventoryType), default=None)
    flags: Optional[int] = schema_field(SchemaFlagField, default=None)
    sale_info: Optional[InventorySaleInfo] = schema_field(InventorySaleInfo, default=None)
    name: Optional[str] = schema_field(SchemaMultilineStr, default=None)
    desc: Optional[str] = schema_field(SchemaMultilineStr, default=None)
    metadata: Optional[Dict[str, Any]] = schema_field(SchemaLLSD, default=None, include_none=True)
    creation_date: Optional[dt.datetime] = schema_field(SchemaDate, llsd_name="created_at", default=None)

    __hash__ = InventoryNodeBase.__hash__

    @property
    def true_asset_id(self) -> UUID:
        if self.asset_id is not None:
            return self.asset_id
        return self.shadow_id ^ MAGIC_ID

    def to_inventory_data(self, block_name: str = "InventoryData") -> Block:
        return Block(
            block_name,
            ItemID=self.item_id,
            FolderID=self.parent_id,
            CallbackID=0,
            CreatorID=self.permissions.creator_id,
            OwnerID=self.permissions.owner_id,
            GroupID=self.permissions.group_id,
            BaseMask=self.permissions.base_mask,
            OwnerMask=self.permissions.owner_mask,
            GroupMask=self.permissions.group_mask,
            EveryoneMask=self.permissions.everyone_mask,
            NextOwnerMask=self.permissions.next_owner_mask,
            GroupOwned=self.permissions.owner_id == UUID.ZERO and self.permissions.group_id != UUID.ZERO,
            AssetID=self.true_asset_id,
            Type=self.type,
            InvType=self.inv_type,
            Flags=self.flags,
            SaleType=self.sale_info.sale_type,
            SalePrice=self.sale_info.sale_price,
            Name=self.name,
            Description=self.desc,
            CreationDate=SchemaDate.to_llsd(self.creation_date, "legacy"),
            # Meaningless here
            CRC=secrets.randbits(32),
        )

    @classmethod
    def from_inventory_data(cls, block: Block):
        return cls(
            item_id=block["ItemID"],
            # Might be under one of two names
            parent_id=block.get("ParentID", block["FolderID"]),
            permissions=InventoryPermissions(
                creator_id=block["CreatorID"],
                owner_id=block["OwnerID"],
                # Unknown, not sent in this schema
                last_owner_id=block.get("LastOwnerID", UUID.ZERO),
                group_id=block["GroupID"],
                base_mask=block["BaseMask"],
                owner_mask=block["OwnerMask"],
                group_mask=block["GroupMask"],
                everyone_mask=block["EveryoneMask"],
                next_owner_mask=block["NextOwnerMask"],
            ),
            # May be missing in UpdateInventoryItem
            asset_id=block.get("AssetID"),
            type=AssetType(block["Type"]),
            inv_type=InventoryType(block["InvType"]),
            flags=block["Flags"],
            sale_info=InventorySaleInfo(
                sale_type=SaleType(block["SaleType"]),
                sale_price=block["SalePrice"],
            ),
            name=block["Name"],
            desc=block["Description"],
            creation_date=SchemaDate.from_llsd(block["CreationDate"], "legacy"),
        )

    def to_llsd(self, flavor: str = "legacy"):
        val = super().to_llsd(flavor=flavor)
        if flavor == "ais":
            # There's little chance this differs from owner ID, just place it.
            val["agent_id"] = val["permissions"]["owner_id"]
            if val["type"] == AssetType.LINK:
                # For link items, there is no asset, only a linked ID.
                val["linked_id"] = val.pop("asset_id")
                # These don't exist either
                val.pop("permissions", None)
                val.pop("sale_info", None)
        return val

    @classmethod
    def from_llsd(cls, inv_dict: Dict, flavor: str = "legacy") -> Self:
        if flavor == "ais" and "linked_id" in inv_dict:
            # Links get represented differently than other items for whatever reason.
            # This is incredibly annoying, under *NIX there's nothing really special about symlinks.
            inv_dict = inv_dict.copy()
            # Fill this in since it needs to be there
            if "permissions" not in inv_dict:
                inv_dict["permissions"] = InventoryPermissions(
                    base_mask=0xFFffFFff,
                    owner_mask=0xFFffFFff,
                    group_mask=0xFFffFFff,
                    everyone_mask=0,
                    next_owner_mask=0xFFffFFff,
                    creator_id=UUID.ZERO,
                    owner_id=UUID.ZERO,
                    last_owner_id=UUID.ZERO,
                    group_id=UUID.ZERO,
                ).to_llsd("ais")
            if "sale_info" not in inv_dict:
                inv_dict["sale_info"] = InventorySaleInfo(
                    sale_type=SaleType.NOT,
                    sale_price=0,
                ).to_llsd("ais")
            if "type" not in inv_dict:
                inv_dict["type"] = AssetType.LINK

            # In the context of symlinks, asset id means linked item ID.
            # This is also how indra stores symlinks. Why the asymmetry in AIS if none of the
            # consumers actually want it? Who knows.
            inv_dict["asset_id"] = inv_dict.pop("linked_id")
        return super().from_llsd(inv_dict, flavor)


INVENTORY_TYPES: Tuple[Type[InventoryNodeBase], ...] = (InventoryCategory, InventoryObject, InventoryItem)
