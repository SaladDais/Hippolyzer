"""
Copyright 2009, Linden Research, Inc.
  See NOTICE.md for previous contributors
Copyright 2021, Salad Dais
All Rights Reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
from __future__ import annotations

import dataclasses
import logging
import struct
from typing import *

import lazy_object_proxy
import recordclass

from hippolyzer.lib.base.datatypes import Vector3, Quaternion, Vector4, UUID, TaggedUnion
from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.namevalue import NameValueCollection
import hippolyzer.lib.base.serialization as se
import hippolyzer.lib.base.templates as tmpls


class Object(recordclass.datatuple):  # type: ignore
    __options__ = {
        "use_weakref": True,
    }
    __weakref__: Any

    LocalID: Optional[int] = None
    State: Optional[int] = None
    FullID: Optional[UUID] = None
    CRC: Optional[int] = None
    PCode: Optional[tmpls.PCode] = None
    Material: Optional[tmpls.MCode] = None
    ClickAction: Optional[int] = None
    Scale: Optional[Vector3] = None
    ParentID: Optional[int] = None
    # Actually contains a weakref proxy
    Parent: Optional[Object] = None
    UpdateFlags: Optional[int] = None
    PathCurve: Optional[int] = None
    ProfileCurve: Optional[int] = None
    PathBegin: Optional[int] = None
    PathEnd: Optional[int] = None
    PathScaleX: Optional[int] = None
    PathScaleY: Optional[int] = None
    PathShearX: Optional[int] = None
    PathShearY: Optional[int] = None
    PathTwist: Optional[int] = None
    PathTwistBegin: Optional[int] = None
    PathRadiusOffset: Optional[int] = None
    PathTaperX: Optional[int] = None
    PathTaperY: Optional[int] = None
    PathRevolutions: Optional[int] = None
    PathSkew: Optional[int] = None
    ProfileBegin: Optional[int] = None
    ProfileEnd: Optional[int] = None
    ProfileHollow: Optional[int] = None
    TextureEntry: Optional[tmpls.TextureEntryCollection] = None
    TextureAnim: Optional[tmpls.TextureAnim] = None
    NameValue: Optional[Any] = None
    Data: Optional[Any] = None
    Text: Optional[str] = None
    TextColor: Optional[bytes] = None
    MediaURL: Optional[str] = None
    PSBlock: Optional[Dict] = None
    ExtraParams: Optional[Dict[tmpls.ExtraParamType, Any]] = None
    Sound: Optional[UUID] = None
    OwnerID: Optional[UUID] = None
    SoundGain: Optional[float] = None
    SoundFlags: Optional[int] = None
    SoundRadius: Optional[float] = None
    JointType: Optional[int] = None
    JointPivot: Optional[int] = None
    JointAxisOrAnchor: Optional[int] = None
    TreeSpecies: Optional[int] = None
    ScratchPad: Optional[bytes] = None
    ObjectCosts: Optional[Dict] = None
    ChildIDs: Optional[List[int]] = None
    # Same as parent, contains weakref proxies.
    Children: Optional[List[Object]] = None

    FootCollisionPlane: Optional[Vector4] = None
    Position: Optional[Vector3] = None
    Velocity: Optional[Vector3] = None
    Acceleration: Optional[Vector3] = None
    Rotation: Optional[Quaternion] = None
    AngularVelocity: Optional[Vector3] = None

    # from ObjectProperties
    CreatorID: Optional[UUID] = None
    GroupID: Optional[UUID] = None
    CreationDate: Optional[int] = None
    BaseMask: Optional[int] = None
    OwnerMask: Optional[int] = None
    GroupMask: Optional[int] = None
    EveryoneMask: Optional[int] = None
    NextOwnerMask: Optional[int] = None
    OwnershipCost: Optional[int] = None
    # TaxRate
    SaleType: Optional[int] = None
    SalePrice: Optional[int] = None
    AggregatePerms: Optional[int] = None
    AggregatePermTextures: Optional[int] = None
    AggregatePermTexturesOwner: Optional[int] = None
    Category: Optional[int] = None
    InventorySerial: Optional[int] = None
    ItemID: Optional[UUID] = None
    FolderID: Optional[UUID] = None
    FromTaskID: Optional[UUID] = None
    LastOwnerID: Optional[UUID] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    TouchName: Optional[str] = None
    SitName: Optional[str] = None
    TextureID: Optional[List[UUID]] = None
    RegionHandle: Optional[int] = None

    def __init__(self, **_kwargs):
        """ set up the object attributes """
        self.ExtraParams = self.ExtraParams or {}  # Variable 1
        self.ObjectCosts = self.ObjectCosts or {}
        self.ChildIDs = []
        # Same as parent, contains weakref proxies.
        self.Children: List[Object] = []

    @property
    def GlobalPosition(self) -> Vector3:
        return handle_to_global_pos(self.RegionHandle) + self.RegionPosition

    @property
    def RegionPosition(self) -> Vector3:
        if not self.ParentID:
            return self.Position

        if not self.Parent:
            raise ValueError("Can't calculate an orphan's RegionPosition")

        # TODO: Cache this and dirty cache if ancestor updates pos?
        return self.Parent.RegionPosition + (self.Position.rotated(self.Parent.RegionRotation))

    @property
    def RegionRotation(self) -> Quaternion:
        if not self.ParentID:
            return self.Rotation

        if not self.Parent:
            raise ValueError("Can't calculate an orphan's RegionRotation")

        # TODO: Cache this and dirty cache if ancestor updates rot?
        return self.Rotation * self.Parent.RegionRotation

    @property
    def AncestorsKnown(self) -> bool:
        obj = self
        while obj.ParentID:
            if not obj.Parent:
                return False
            obj = obj.Parent
        return True

    def update_properties(self, properties: Dict[str, Any]) -> Set[str]:
        """ takes a dictionary of attribute:value and makes it so """
        updated_properties = set()
        for key, val in properties.items():
            if hasattr(self, key):
                old_val = getattr(self, key, dataclasses.MISSING)
                # Don't check equality if we're using a lazy proxy,
                # parsing is deferred until we actually use it.
                if any(isinstance(x, lazy_object_proxy.Proxy) for x in (old_val, val)):
                    # TODO: be smarter about this. Can we store the raw bytes and
                    #  compare those if it's an unparsed object?
                    is_updated = old_val is not val
                else:
                    is_updated = old_val != val
                if is_updated:
                    updated_properties.add(key)
                setattr(self, key, val)
        return updated_properties

    def to_dict(self):
        val = recordclass.asdict(self)
        del val["Children"]
        del val["Parent"]
        return val


def handle_to_gridxy(handle: int) -> Tuple[int, int]:
    return (handle >> 32) // 256, (handle & 0xFFffFFff) // 256


def gridxy_to_handle(x: int, y: int):
    return ((x * 256) << 32) | (y * 256)


def handle_to_global_pos(handle: int) -> Vector3:
    return Vector3(handle >> 32, handle & 0xFFffFFff)


def normalize_object_update(block: Block, handle: int):
    object_data = {
        "RegionHandle": handle,
        "FootCollisionPlane": None,
        "SoundFlags": block["Flags"],
        "SoundGain": block["Gain"],
        "SoundRadius": block["Radius"],
        **dict(block.items()),
        "TextureEntry": block.deserialize_var("TextureEntry", make_copy=False),
        "NameValue": block.deserialize_var("NameValue", make_copy=False),
        "TextureAnim": block.deserialize_var("TextureAnim", make_copy=False),
        "ExtraParams": block.deserialize_var("ExtraParams", make_copy=False) or {},
        "PSBlock": block.deserialize_var("PSBlock", make_copy=False).value,
        "UpdateFlags": block.deserialize_var("UpdateFlags", make_copy=False),
        "State": block.deserialize_var("State", make_copy=False),
        **block.deserialize_var("ObjectData", make_copy=False).value,
    }
    object_data["LocalID"] = object_data.pop("ID")
    # Empty == not updated
    if not object_data["TextureEntry"]:
        object_data.pop("TextureEntry")
    # OwnerID is only set in this packet if a sound is playing. Don't allow
    # ObjectUpdates to clobber _real_ OwnerIDs we had from ObjectProperties
    # with a null UUID.
    if object_data["OwnerID"] == UUID():
        del object_data["OwnerID"]
    del object_data["Flags"]
    del object_data["Gain"]
    del object_data["Radius"]
    del object_data["ObjectData"]
    return object_data


def normalize_terse_object_update(block: Block, handle: int):
    object_data = {
        **block.deserialize_var("Data", make_copy=False),
        **dict(block.items()),
        "TextureEntry": block.deserialize_var("TextureEntry", make_copy=False),
        "RegionHandle": handle,
    }
    object_data["LocalID"] = object_data.pop("ID")
    object_data.pop("Data")
    # Empty == not updated
    if object_data["TextureEntry"] is None:
        object_data.pop("TextureEntry")
    return object_data


def normalize_object_update_compressed_data(data: bytes):
    # Shared by ObjectUpdateCompressed and VOCache case
    compressed = FastObjectUpdateCompressedDataDeserializer.read(data)
    # TODO: ObjectUpdateCompressed doesn't provide a default value for unused
    #  fields, whereas ObjectUpdate and friends do (TextColor, etc.)
    #  need some way to normalize ObjectUpdates so they won't appear to have
    #  changed just because an ObjectUpdate got sent with a default value
    # Only used for determining which sections are present
    del compressed["Flags"]

    # Unlike other ObjectUpdate types, a null value in an ObjectUpdateCompressed
    # always means that there is no value, not that the value hasn't changed
    # from the client's view. Use the default value when that happens.
    ps_block = compressed.pop("PSBlockNew", None)
    if ps_block is None:
        ps_block = compressed.pop("PSBlock", None)
    if ps_block is None:
        ps_block = TaggedUnion(0, None)
    compressed.pop("PSBlock", None)
    if compressed["NameValue"] is None:
        compressed["NameValue"] = NameValueCollection()
    if compressed["Text"] is None:
        compressed["Text"] = b""
        compressed["TextColor"] = b""
    if compressed["MediaURL"] is None:
        compressed["MediaURL"] = b""
    if compressed["AngularVelocity"] is None:
        compressed["AngularVelocity"] = Vector3()
    if compressed["SoundFlags"] is None:
        compressed["SoundFlags"] = 0
        compressed["SoundGain"] = 0.0
        compressed["SoundRadius"] = 0.0
        compressed["Sound"] = UUID()
    if compressed["TextureEntry"] is None:
        compressed["TextureEntry"] = tmpls.TextureEntryCollection()

    object_data = {
        "PSBlock": ps_block.value,
        # Parent flag not set means explicitly un-parented
        "ParentID": compressed.pop("ParentID", None) or 0,
        "LocalID": compressed.pop("ID"),
        **compressed,
    }
    # Don't clobber OwnerID in case the object has a proper one from
    # a previous ObjectProperties. OwnerID isn't expected to be populated
    # on ObjectUpdates unless an attached sound is playing.
    if object_data["OwnerID"] == UUID():
        del object_data["OwnerID"]
    return object_data


def normalize_object_update_compressed(block: Block, handle: int):
    compressed = normalize_object_update_compressed_data(block["Data"])
    compressed["UpdateFlags"] = block.deserialize_var("UpdateFlags", make_copy=False)
    compressed["RegionHandle"] = handle
    return compressed


class SimpleStructReader(se.BufferReader):
    def read_struct(self, spec: struct.Struct, peek=False) -> Tuple[Any, ...]:
        val = spec.unpack_from(self._buffer, self._pos)
        if not peek:
            self._pos += spec.size
        return val

    def read_bytes_null_term(self) -> bytes:
        old_offset = self._pos
        while self._buffer[self._pos] != 0:
            self._pos += 1
        val = self._buffer[old_offset:self._pos]
        self._pos += 1
        return val


class FastObjectUpdateCompressedDataDeserializer:
    HEADER_STRUCT = struct.Struct("<16sIBBIBB3f3f3fI16s")
    ANGULAR_VELOCITY_STRUCT = struct.Struct("<3f")
    PARENT_ID_STRUCT = struct.Struct("<I")
    TREE_SPECIES_STRUCT = struct.Struct("<B")
    DATAPACKER_LEN = struct.Struct("<I")
    COLOR_ADAPTER = tmpls.Color4()
    PARTICLES_OLD = se.TypedBytesFixed(86, tmpls.PSBLOCK_TEMPLATE)
    SOUND_STRUCT = struct.Struct("<16sfBf")
    PRIM_PARAMS_STRUCT = struct.Struct("<BBHHBBBBbbbbbBbHHH")
    ATTACHMENT_STATE_ADAPTER = tmpls.AttachmentStateAdapter(None)

    @classmethod
    def read(cls, data: bytes) -> Dict:
        reader = SimpleStructReader("<", data)
        foo = reader.read_struct(cls.HEADER_STRUCT)
        full_id, local_id, pcode, state, crc, material, click_action, \
            scalex, scaley, scalez, posx, posy, posz, rotx, roty, rotz, \
            flags, owner_id = foo
        scale = Vector3(scalex, scaley, scalez)
        full_id = UUID(bytes=full_id)
        pcode = tmpls.PCode(pcode)
        if pcode == tmpls.PCode.AVATAR:
            state = tmpls.AgentState(state)
        elif pcode == tmpls.PCode.PRIMITIVE:
            state = cls.ATTACHMENT_STATE_ADAPTER.decode(state, None)
        pos = Vector3(posx, posy, posz)
        rot = Quaternion(rotx, roty, rotz)
        owner_id = UUID(bytes=owner_id)
        ang_vel = None
        if flags & tmpls.CompressedFlags.ANGULAR_VELOCITY.value:
            ang_vel = Vector3(*reader.read_struct(cls.ANGULAR_VELOCITY_STRUCT))
        parent_id = None
        if flags & tmpls.CompressedFlags.PARENT_ID.value:
            parent_id = reader.read_struct(cls.PARENT_ID_STRUCT)[0]
        tree_species = None
        if flags & tmpls.CompressedFlags.TREE.value:
            tree_species = reader.read_struct(cls.TREE_SPECIES_STRUCT)[0]
        scratchpad = None
        if flags & tmpls.CompressedFlags.SCRATCHPAD.value:
            scratchpad = reader.read_bytes(reader.read_struct(cls.DATAPACKER_LEN)[0])
        text = None
        text_color = None
        if flags & tmpls.CompressedFlags.TEXT.value:
            text = reader.read_bytes_null_term().decode("utf8")
            text_color = cls.COLOR_ADAPTER.decode(reader.read_bytes(4), ctx=None)
        media_url = None
        if flags & tmpls.CompressedFlags.MEDIA_URL.value:
            media_url = reader.read_bytes_null_term().decode("utf8")
        psblock = None
        if flags & tmpls.CompressedFlags.PARTICLES.value:
            psblock = reader.read(cls.PARTICLES_OLD)
        extra_params = reader.read(tmpls.EXTRA_PARAM_COLLECTION)
        sound, sound_gain, sound_flags, sound_radius = None, None, None, None
        if flags & tmpls.CompressedFlags.SOUND.value:
            sound, sound_gain, sound_flags, sound_radius = reader.read_struct(cls.SOUND_STRUCT)
            sound = UUID(bytes=sound)
            sound_flags = tmpls.SoundFlags(sound_flags)
        name_value = None
        if flags & tmpls.CompressedFlags.NAME_VALUES.value:
            name_value = reader.read(tmpls.NAMEVALUES_TERMINATED_TEMPLATE)
        path_curve, profile_curve, path_begin, path_end, path_scale_x, path_scale_y, \
            path_shear_x, path_shear_y, path_twist, path_twist_begin, path_radius_offset, \
            path_taper_x, path_taper_y, path_revolutions, path_skew, profile_begin, \
            profile_end, profile_hollow = reader.read_struct(cls.PRIM_PARAMS_STRUCT)
        texture_entry = reader.read(tmpls.DATA_PACKER_TE_TEMPLATE)
        texture_anim = None
        if flags & tmpls.CompressedFlags.TEXTURE_ANIM.value:
            texture_anim = reader.read(se.TypedByteArray(se.U32, tmpls.TA_TEMPLATE))
        psblock_new = None
        if flags & tmpls.CompressedFlags.PARTICLES_NEW.value:
            psblock_new = reader.read(tmpls.PSBLOCK_TEMPLATE)

        if len(reader):
            logging.warning(f"{len(reader)} bytes left at end of buffer for compressed {data!r}")

        return {
            "FullID": full_id,
            "ID": local_id,
            "PCode": pcode,
            "State": state,
            "CRC": crc,
            "Material": material,
            "ClickAction": click_action,
            "Scale": scale,
            "Position": pos,
            "Rotation": rot,
            "Flags": flags,
            "OwnerID": owner_id,
            "AngularVelocity": ang_vel,
            "ParentID": parent_id,
            "TreeSpecies": tree_species,
            "ScratchPad": scratchpad,
            "Text": text,
            "TextColor": text_color,
            "MediaURL": media_url,
            "PSBlock": psblock,
            "ExtraParams": extra_params,
            "Sound": sound,
            "SoundGain": sound_gain,
            "SoundFlags": sound_flags,
            "SoundRadius": sound_radius,
            "NameValue": name_value,
            "PathCurve": path_curve,
            "ProfileCurve": profile_curve,
            "PathBegin": path_begin,  # 0 to 1, quanta = 0.01
            "PathEnd": path_end,  # 0 to 1, quanta = 0.01
            "PathScaleX": path_scale_x,  # 0 to 1, quanta = 0.01
            "PathScaleY": path_scale_y,  # 0 to 1, quanta = 0.01
            "PathShearX": path_shear_x,  # -.5 to .5, quanta = 0.01
            "PathShearY": path_shear_y,  # -.5 to .5, quanta = 0.01
            "PathTwist": path_twist,  # -1 to 1, quanta = 0.01
            "PathTwistBegin": path_twist_begin,  # -1 to 1, quanta = 0.01
            "PathRadiusOffset": path_radius_offset,  # -1 to 1, quanta = 0.01
            "PathTaperX": path_taper_x,  # -1 to 1, quanta = 0.01
            "PathTaperY": path_taper_y,  # -1 to 1, quanta = 0.01
            "PathRevolutions": path_revolutions,  # 0 to 3, quanta = 0.015
            "PathSkew": path_skew,  # -1 to 1, quanta = 0.01
            "ProfileBegin": profile_begin,  # 0 to 1, quanta = 0.01
            "ProfileEnd": profile_end,  # 0 to 1, quanta = 0.01
            "ProfileHollow": profile_hollow,  # 0 to 1, quanta = 0.01
            "TextureEntry": texture_entry,
            "TextureAnim": texture_anim,
            "PSBlockNew": psblock_new,
        }
