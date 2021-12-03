"""
Body parts and linden clothing layers
"""

from __future__ import annotations

import dataclasses
import logging
from io import StringIO
from typing import *

from xml.etree.ElementTree import parse as parse_etree

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.helpers import get_resource_filename
from hippolyzer.lib.base.inventory import InventorySaleInfo, InventoryPermissions
from hippolyzer.lib.base.legacy_schema import SchemaBase, parse_schema_line, SchemaParsingError
from hippolyzer.lib.base.templates import WearableType

LOG = logging.getLogger(__name__)
_T = TypeVar("_T")

WEARABLE_VERSION = "LLWearable version 22"


@dataclasses.dataclass
class VisualParam:
    id: int
    name: str
    value_min: float
    value_max: float
    # These might be `None` if the param isn't meant to be directly edited
    edit_group: Optional[str]
    wearable: Optional[str]


class VisualParams(List[VisualParam]):
    def __init__(self):
        super().__init__()
        lad_path = get_resource_filename("lib/base/data/avatar_lad.xml")
        with open(lad_path, "rb") as f:
            doc = parse_etree(f)
        for param in doc.findall(".//param"):
            self.append(VisualParam(
                id=int(param.attrib["id"]),
                name=param.attrib["name"],
                edit_group=param.get("edit_group"),
                wearable=param.get("wearable"),
                value_min=float(param.attrib["value_min"]),
                value_max=float(param.attrib["value_max"]),
            ))

    def by_name(self, name: str) -> VisualParam:
        return [x for x in self if x.name == name][0]

    def by_edit_group(self, edit_group: str) -> List[VisualParam]:
        return [x for x in self if x.edit_group == edit_group]

    def by_wearable(self, wearable: str) -> List[VisualParam]:
        return [x for x in self if x.wearable == wearable]


VISUAL_PARAMS = VisualParams()


@dataclasses.dataclass
class Wearable(SchemaBase):
    name: str
    wearable_type: WearableType
    permissions: InventoryPermissions
    sale_info: InventorySaleInfo
    # VisualParam ID -> val
    parameters: Dict[int, float]
    # TextureEntry ID -> texture ID
    textures: Dict[int, UUID]

    @classmethod
    def _skip_to_next_populated_line(cls, reader: StringIO):
        old_pos = reader.tell()
        while peeked_data := reader.readline():
            # Read until we find a non-blank line
            if peeked_data.lstrip("\n"):
                break
            old_pos = reader.tell()
        # Reading an empty string means EOF
        if not peeked_data:
            raise SchemaParsingError("Premature EOF")
        reader.seek(old_pos)

    @classmethod
    def _read_and_parse_line(cls, reader: StringIO):
        cls._skip_to_next_populated_line(reader)
        return parse_schema_line(reader.readline())

    @classmethod
    def _read_expected_key(cls, reader: StringIO, expected_key: str) -> str:
        key, val = cls._read_and_parse_line(reader)
        if key != expected_key:
            raise ValueError(f"Expected {expected_key} not found, {(key, val)!r}")
        return val

    @classmethod
    def from_reader(cls, reader: StringIO) -> Wearable:
        cls._skip_to_next_populated_line(reader)
        version_str = reader.readline().rstrip()
        if version_str != WEARABLE_VERSION:
            raise ValueError(f"Bad wearable version {version_str!r}")
        cls._skip_to_next_populated_line(reader)
        name = reader.readline().rstrip()

        permissions = InventoryPermissions.from_reader(reader, read_header=True)
        sale_info = InventorySaleInfo.from_reader(reader, read_header=True)

        wearable_type = WearableType(int(cls._read_expected_key(reader, "type")))
        num_params = int(cls._read_expected_key(reader, "parameters"))
        params = {}
        for _ in range(num_params):
            param_id, param_val = cls._read_and_parse_line(reader)
            if param_val == ".":
                param_val = "0.0"
            params[int(param_id)] = float(param_val)

        num_textures = int(cls._read_expected_key(reader, "textures"))
        textures = {}
        for _ in range(num_textures):
            te_id, texture_id = cls._read_and_parse_line(reader)
            textures[int(te_id)] = UUID(texture_id)
        return Wearable(
            name=name,
            wearable_type=wearable_type,
            permissions=permissions,
            sale_info=sale_info,
            parameters=params,
            textures=textures
        )

    def to_writer(self, writer: StringIO):
        writer.write(f"{WEARABLE_VERSION}\n")
        writer.write(f"{self.name}\n\n")
        self.permissions.to_writer(writer)
        self.sale_info.to_writer(writer)
        writer.write(f"type {int(self.wearable_type)}\n")
        writer.write(f"parameters {len(self.parameters)}\n")
        for param_id, param_val in self.parameters.items():
            writer.write(f"{param_id} {param_val}\n")
        writer.write(f"textures {len(self.textures)}\n")
        for te_id, texture_id in self.textures.items():
            writer.write(f"{te_id} {texture_id}\n")
