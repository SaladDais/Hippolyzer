"""
Body parts and linden clothing layers
"""

from __future__ import annotations

import dataclasses
import enum
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
DEFAULT_WEARABLE_TEX = UUID("c228d1cf-4b5d-4ba8-84f4-899a0796aa97")


class AvatarTEIndex(enum.IntEnum):
    """From llavatarappearancedefines.h"""
    HEAD_BODYPAINT = 0
    UPPER_SHIRT = enum.auto()
    LOWER_PANTS = enum.auto()
    EYES_IRIS = enum.auto()
    HAIR = enum.auto()
    UPPER_BODYPAINT = enum.auto()
    LOWER_BODYPAINT = enum.auto()
    LOWER_SHOES = enum.auto()
    HEAD_BAKED = enum.auto()
    UPPER_BAKED = enum.auto()
    LOWER_BAKED = enum.auto()
    EYES_BAKED = enum.auto()
    LOWER_SOCKS = enum.auto()
    UPPER_JACKET = enum.auto()
    LOWER_JACKET = enum.auto()
    UPPER_GLOVES = enum.auto()
    UPPER_UNDERSHIRT = enum.auto()
    LOWER_UNDERPANTS = enum.auto()
    SKIRT = enum.auto()
    SKIRT_BAKED = enum.auto()
    HAIR_BAKED = enum.auto()
    LOWER_ALPHA = enum.auto()
    UPPER_ALPHA = enum.auto()
    HEAD_ALPHA = enum.auto()
    EYES_ALPHA = enum.auto()
    HAIR_ALPHA = enum.auto()
    HEAD_TATTOO = enum.auto()
    UPPER_TATTOO = enum.auto()
    LOWER_TATTOO = enum.auto()
    HEAD_UNIVERSAL_TATTOO = enum.auto()
    UPPER_UNIVERSAL_TATTOO = enum.auto()
    LOWER_UNIVERSAL_TATTOO = enum.auto()
    SKIRT_TATTOO = enum.auto()
    HAIR_TATTOO = enum.auto()
    EYES_TATTOO = enum.auto()
    LEFT_ARM_TATTOO = enum.auto()
    LEFT_LEG_TATTOO = enum.auto()
    AUX1_TATTOO = enum.auto()
    AUX2_TATTOO = enum.auto()
    AUX3_TATTOO = enum.auto()
    LEFTARM_BAKED = enum.auto()
    LEFTLEG_BAKED = enum.auto()
    AUX1_BAKED = enum.auto()
    AUX2_BAKED = enum.auto()
    AUX3_BAKED = enum.auto()

    @property
    def is_baked(self) -> bool:
        return self.name.endswith("_BAKED")


@dataclasses.dataclass
class VisualParam:
    id: int
    name: str
    value_min: float
    value_max: float
    value_default: float
    # These might be `None` if the param isn't meant to be directly edited
    edit_group: Optional[str]
    wearable: Optional[str]


class VisualParams(List[VisualParam]):
    def __init__(self, lad_path):
        super().__init__()
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
                value_default=float(param.attrib.get("value_default", 0.0))
            ))

    def by_name(self, name: str) -> VisualParam:
        return [x for x in self if x.name == name][0]

    def by_edit_group(self, edit_group: str) -> List[VisualParam]:
        return [x for x in self if x.edit_group == edit_group]

    def by_wearable(self, wearable: str) -> List[VisualParam]:
        return [x for x in self if x.wearable == wearable]

    def by_id(self, vparam_id: int) -> VisualParam:
        return [x for x in self if x.id == vparam_id][0]


VISUAL_PARAMS = VisualParams(get_resource_filename("lib/base/data/avatar_lad.xml"))


# See `llpaneleditwearable.cpp`, which TE slots should be set for each wearable type is hardcoded
# in the viewer.
WEARABLE_TEXTURE_SLOTS: Dict[WearableType, Sequence[AvatarTEIndex]] = {
    WearableType.SHAPE: (),
    WearableType.SKIN: (AvatarTEIndex.HEAD_BODYPAINT, AvatarTEIndex.UPPER_BODYPAINT, AvatarTEIndex.LOWER_BODYPAINT),
    WearableType.HAIR: (AvatarTEIndex.HAIR,),
    WearableType.EYES: (AvatarTEIndex.EYES_IRIS,),
    WearableType.SHIRT: (AvatarTEIndex.UPPER_SHIRT,),
    WearableType.PANTS: (AvatarTEIndex.LOWER_PANTS,),
    WearableType.SHOES: (AvatarTEIndex.LOWER_SHOES,),
    WearableType.SOCKS: (AvatarTEIndex.LOWER_SOCKS,),
    WearableType.JACKET: (AvatarTEIndex.UPPER_JACKET, AvatarTEIndex.LOWER_JACKET),
    WearableType.GLOVES: (AvatarTEIndex.UPPER_GLOVES,),
    WearableType.UNDERSHIRT: (AvatarTEIndex.UPPER_UNDERSHIRT,),
    WearableType.UNDERPANTS: (AvatarTEIndex.LOWER_UNDERPANTS,),
    WearableType.SKIRT: (AvatarTEIndex.SKIRT,),
    WearableType.ALPHA: (AvatarTEIndex.LOWER_ALPHA, AvatarTEIndex.UPPER_ALPHA,
                         AvatarTEIndex.HEAD_ALPHA, AvatarTEIndex.EYES_ALPHA, AvatarTEIndex.HAIR_ALPHA),
    WearableType.TATTOO: (AvatarTEIndex.LOWER_TATTOO, AvatarTEIndex.UPPER_TATTOO, AvatarTEIndex.HEAD_TATTOO),
    WearableType.UNIVERSAL: (AvatarTEIndex.HEAD_UNIVERSAL_TATTOO, AvatarTEIndex.UPPER_UNIVERSAL_TATTOO,
                             AvatarTEIndex.LOWER_UNIVERSAL_TATTOO, AvatarTEIndex.SKIRT_TATTOO,
                             AvatarTEIndex.HAIR_TATTOO, AvatarTEIndex.EYES_TATTOO, AvatarTEIndex.LEFT_ARM_TATTOO,
                             AvatarTEIndex.LEFT_LEG_TATTOO, AvatarTEIndex.AUX1_TATTOO, AvatarTEIndex.AUX2_TATTOO,
                             AvatarTEIndex.AUX3_TATTOO),
    WearableType.PHYSICS: (),
}


@dataclasses.dataclass
class Wearable(SchemaBase):
    name: str
    wearable_type: WearableType
    permissions: InventoryPermissions
    sale_info: InventorySaleInfo
    # VisualParam ID -> val
    parameters: Dict[int, float]
    # TextureEntry ID -> texture UUID
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

    @classmethod
    def make_default(cls, w_type: WearableType) -> Self:
        instance = cls(
            name="New " + w_type.name.replace("_", " ").title(),
            permissions=InventoryPermissions.make_default(),
            sale_info=InventorySaleInfo.make_default(),
            parameters={},
            textures={},
            wearable_type=w_type,
        )

        for te_idx in WEARABLE_TEXTURE_SLOTS[w_type]:
            instance.textures[te_idx] = DEFAULT_WEARABLE_TEX

        for param in VISUAL_PARAMS.by_wearable(w_type.name.lower()):
            instance.parameters[param.id] = param.value_default

        return instance
