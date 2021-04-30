"""
Parse the horrible legacy inventory format

It's typically only used for object contents now.
"""
from __future__ import annotations

import abc
import dataclasses
import datetime as dt
import itertools
import logging
import re
import weakref
from typing import *

from hippolyzer.lib.base.datatypes import UUID

LOG = logging.getLogger(__name__)
MAGIC_ID = UUID("3c115e51-04f4-523c-9fa6-98aff1034730")


def _parse_str(val: str):
    return val.rstrip("|")


def _int_from_hex(val: str):
    return int(val, 16)


def _parse_date(val: str):
    return dt.datetime.utcfromtimestamp(int(val))


class InventoryParsingError(Exception):
    pass


def _inv_field(spec: Union[Callable, Type], *, default=dataclasses.MISSING, init=True, repr=True,  # noqa
                   hash=None, compare=True) -> dataclasses.Field:  # noqa
    """Describe a field in the inventory schema and the shape of its value"""
    return dataclasses.field(
        metadata={"spec": spec}, default=default, init=init,
        repr=repr, hash=hash, compare=compare
    )


# The schema is meant to allow multi-line strings, but in practice
# it does not due to scanf() shenanigans. This is fine.
_INV_TOKEN_RE = re.compile(r'\A\s*([^\s]+)(\s+([^\t\r\n]+))?$')


def _parse_inv_line(line: str):
    g = _INV_TOKEN_RE.search(line)
    if not g:
        raise InventoryParsingError("%r doesn't match the token regex" % line)
    return g.group(1), g.group(3)


def _yield_inv_tokens(line_iter: Iterator[str]):
    in_bracket = False
    for line in line_iter:
        line = line.strip()
        if not line:
            continue
        try:
            key, val = _parse_inv_line(line)
        except InventoryParsingError:
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
            in_bracket = False
            break
        yield key, val
    if in_bracket:
        raise LOG.warning("Reached EOF while inside a bracket")


class InventoryModel:
    def __init__(self):
        self.containers: Dict[UUID, InventoryContainerBase] = {}
        self.items: Dict[UUID, InventoryItem] = {}
        self.root: Optional[InventoryContainerBase] = None

    @classmethod
    def from_str(cls, text: str):
        return cls.from_iter(iter(text.splitlines()))

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls.from_str(data.decode("utf8"))

    @classmethod
    def from_iter(cls, line_iter: Iterator[str]) -> InventoryModel:
        model = cls()
        for key, value in _yield_inv_tokens(line_iter):
            if key == "inv_object":
                obj = InventoryObject.from_iter(line_iter)
                if obj is not None:
                    model.add_container(obj)
            elif key == "inv_category":
                cat = InventoryCategory.from_iter(line_iter)
                if cat is not None:
                    model.add_container(cat)
            elif key == "inv_item":
                item = InventoryItem.from_iter(line_iter)
                if item is not None:
                    model.add_item(item)
            else:
                LOG.warning("Unknown key {0}".format(key))
        model.reparent_nodes()
        return model

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
class InventoryBase(abc.ABC):
    @classmethod
    def _fields_dict(cls):
        return {f.name: f for f in dataclasses.fields(cls)}

    @classmethod
    def from_iter(cls, line_iter: Iterator[str]):
        fields = cls._fields_dict()
        obj = {}
        for key, val in _yield_inv_tokens(line_iter):
            if key in fields:
                field: dataclasses.Field = fields[key]
                spec = field.metadata.get("spec")
                # Not a real key, an internal var on our dataclass
                if not spec:
                    LOG.warning(f"Internal key {key!r}")
                    continue
                # some kind of nested structure like sale_info
                if isinstance(spec, type) and issubclass(spec, InventoryBase):
                    obj[key] = spec.from_iter(line_iter)
                else:
                    obj[key] = spec(val)
            else:
                LOG.warning(f"Unknown key {key!r}")

        # Bad entry, ignore
        # TODO: Check on these. might be symlinks or something.
        if obj.get("type") == "-1":
            LOG.warning(f"Skipping bad object with type == -1: {obj!r}")
            return None
        return cls(**obj)  # type: ignore


@dataclasses.dataclass
class InventoryPermissions(InventoryBase):
    base_mask: int = _inv_field(_int_from_hex)
    owner_mask: int = _inv_field(_int_from_hex)
    group_mask: int = _inv_field(_int_from_hex)
    everyone_mask: int = _inv_field(_int_from_hex)
    next_owner_mask: int = _inv_field(_int_from_hex)
    creator_id: UUID = _inv_field(UUID)
    owner_id: UUID = _inv_field(UUID)
    last_owner_id: UUID = _inv_field(UUID)
    group_id: UUID = _inv_field(UUID)


@dataclasses.dataclass
class InventorySaleInfo(InventoryBase):
    sale_type: str = _inv_field(str)
    sale_price: int = _inv_field(int)


@dataclasses.dataclass
class InventoryNodeBase(InventoryBase):
    ID_ATTR: ClassVar[str]
    parent_id: Optional[UUID] = _inv_field(UUID)
    model: Optional[InventoryModel] = dataclasses.field(default=None, init=False)

    @property
    def node_id(self) -> UUID:
        return getattr(self, self.ID_ATTR)

    @property
    def parent(self):
        return self.model.containers.get(self.parent_id)


@dataclasses.dataclass
class InventoryContainerBase(InventoryNodeBase):
    type: str = _inv_field(str)
    name: str = _inv_field(_parse_str)
    children: List[InventoryNodeBase] = dataclasses.field(default_factory=list, init=False)


@dataclasses.dataclass
class InventoryObject(InventoryContainerBase):
    ID_ATTR: ClassVar[str] = "obj_id"
    obj_id: UUID = _inv_field(UUID)


@dataclasses.dataclass
class InventoryCategory(InventoryContainerBase):
    ID_ATTR: ClassVar[str] = "cat_id"
    cat_id: UUID = _inv_field(UUID)
    pref_type: str = _inv_field(str)
    owner_id: UUID = _inv_field(UUID)
    version: int = _inv_field(int)


@dataclasses.dataclass
class InventoryItem(InventoryNodeBase):
    ID_ATTR: ClassVar[str] = "item_id"
    item_id: UUID = _inv_field(UUID)
    type: str = _inv_field(str)
    inv_type: str = _inv_field(str)
    flags: int = _inv_field(_int_from_hex)
    name: str = _inv_field(_parse_str)
    desc: str = _inv_field(_parse_str)
    creation_date: dt.datetime = _inv_field(_parse_date)
    permissions: InventoryPermissions = _inv_field(InventoryPermissions)
    sale_info: InventorySaleInfo = _inv_field(InventorySaleInfo)
    asset_id: Optional[UUID] = _inv_field(UUID, default=None)
    shadow_id: Optional[UUID] = _inv_field(UUID, default=None)

    @property
    def true_asset_id(self) -> UUID:
        if self.asset_id is not None:
            return self.asset_id
        return self.shadow_id ^ MAGIC_ID
