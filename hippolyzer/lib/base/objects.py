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

from typing import *

import lazy_object_proxy
import recordclass

from hippolyzer.lib.base.datatypes import Vector3, Quaternion, Vector4, UUID


class Object(recordclass.datatuple):  # type: ignore
    __options__ = {
        "fast_new": False,
        "use_weakref": True,
    }
    __weakref__: Any

    LocalID: Optional[int] = None
    State: Optional[int] = None
    FullID: Optional[UUID] = None
    CRC: Optional[int] = None
    PCode: Optional[int] = None
    Material: Optional[int] = None
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
    TextureEntry: Optional[Any] = None
    TextureAnim: Optional[Any] = None
    NameValue: Optional[Any] = None
    Data: Optional[Any] = None
    Text: Optional[str] = None
    TextColor: Optional[bytes] = None
    MediaURL: Optional[Any] = None
    PSBlock: Optional[Any] = None
    ExtraParams: Optional[Any] = None
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
    TextureID: Optional[Any] = None

    def __init__(self, *, LocalID=None, State=None, FullID=None, CRC=None, PCode=None, Material=None,
                 ClickAction=None, Scale=None, ParentID=None, UpdateFlags=None, PathCurve=None, ProfileCurve=None,
                 PathBegin=None, PathEnd=None, PathScaleX=None, PathScaleY=None, PathShearX=None, PathShearY=None,
                 PathTwist=None, PathTwistBegin=None, PathRadiusOffset=None, PathTaperX=None, PathTaperY=None,
                 PathRevolutions=None, PathSkew=None, ProfileBegin=None, ProfileEnd=None, ProfileHollow=None,
                 TextureEntry=None, TextureAnim=None, NameValue=None, Data=None, Text=None, TextColor=None,
                 MediaURL=None, PSBlock=None, ExtraParams=None, Sound=None, OwnerID=None, SoundGain=None,
                 SoundFlags=None, SoundRadius=None, JointType=None, JointPivot=None, JointAxisOrAnchor=None,
                 FootCollisionPlane=None, Position=None, Velocity=None, Acceleration=None, Rotation=None,
                 AngularVelocity=None, TreeSpecies=None, ObjectCosts=None, ScratchPad=None):
        """ set up the object attributes """

        self.LocalID = LocalID  # U32
        self.State = State  # U8
        self.FullID = FullID  # LLUUID
        self.CRC = CRC  # U32 // TEMPORARY HACK FOR JAMES
        self.PCode = PCode  # U8
        self.Material = Material  # U8
        self.ClickAction = ClickAction  # U8
        self.Scale = Scale  # LLVector3
        self.ParentID = ParentID  # U32
        # Actually contains a weakref proxy
        self.Parent: Optional[Object] = None
        self.UpdateFlags = UpdateFlags  # U32 // U32, see object_flags.h
        self.PathCurve = PathCurve  # U8
        self.ProfileCurve = ProfileCurve  # U8
        self.PathBegin = PathBegin  # U16 // 0 to 1, quanta = 0.01
        self.PathEnd = PathEnd  # U16 // 0 to 1, quanta = 0.01
        self.PathScaleX = PathScaleX  # U8 // 0 to 1, quanta = 0.01
        self.PathScaleY = PathScaleY  # U8 // 0 to 1, quanta = 0.01
        self.PathShearX = PathShearX  # U8 // -.5 to .5, quanta = 0.01
        self.PathShearY = PathShearY  # U8 // -.5 to .5, quanta = 0.01
        self.PathTwist = PathTwist  # S8 // -1 to 1, quanta = 0.01
        self.PathTwistBegin = PathTwistBegin  # S8 // -1 to 1, quanta = 0.01
        self.PathRadiusOffset = PathRadiusOffset  # S8 // -1 to 1, quanta = 0.01
        self.PathTaperX = PathTaperX  # S8 // -1 to 1, quanta = 0.01
        self.PathTaperY = PathTaperY  # S8 // -1 to 1, quanta = 0.01
        self.PathRevolutions = PathRevolutions  # U8 // 0 to 3, quanta = 0.015
        self.PathSkew = PathSkew  # S8 // -1 to 1, quanta = 0.01
        self.ProfileBegin = ProfileBegin  # U16 // 0 to 1, quanta = 0.01
        self.ProfileEnd = ProfileEnd  # U16 // 0 to 1, quanta = 0.01
        self.ProfileHollow = ProfileHollow  # U16 // 0 to 1, quanta = 0.01
        self.TextureEntry = TextureEntry  # Variable 2
        self.TextureAnim = TextureAnim  # Variable 1
        self.NameValue = NameValue  # Variable 2
        self.Data = Data  # Variable 2
        self.Text = Text  # Variable 1 // llSetText() hovering text
        self.TextColor = TextColor  # Fixed 4 // actually, a LLColor4U
        self.MediaURL = MediaURL  # Variable 1 // URL for web page, movie, etc.
        self.PSBlock = PSBlock  # Variable 1
        self.ExtraParams = ExtraParams or {}  # Variable 1
        self.Sound = Sound  # LLUUID
        self.OwnerID = OwnerID  # LLUUID // HACK object's owner id, only set if non-null sound, for muting
        self.SoundGain = SoundGain  # F32
        self.SoundFlags = SoundFlags  # U8
        self.SoundRadius = SoundRadius  # F32 // cutoff radius
        self.JointType = JointType  # U8
        self.JointPivot = JointPivot  # LLVector3
        self.JointAxisOrAnchor = JointAxisOrAnchor  # LLVector3
        self.TreeSpecies = TreeSpecies
        self.ScratchPad = ScratchPad
        self.ObjectCosts = ObjectCosts or {}
        self.ChildIDs = []
        # Same as parent, contains weakref proxies.
        self.Children: List[Object] = []

        # from ObjectUpdateCompressed
        self.FootCollisionPlane: Optional[Vector4] = FootCollisionPlane
        self.Position: Optional[Vector3] = Position
        self.Velocity: Optional[Vector3] = Velocity
        self.Acceleration: Optional[Vector3] = Acceleration
        self.Rotation: Optional[Quaternion] = Rotation
        self.AngularVelocity: Optional[Vector3] = AngularVelocity

        # from ObjectProperties
        self.CreatorID = None
        self.GroupID = None
        self.CreationDate = None
        self.BaseMask = None
        self.OwnerMask = None
        self.GroupMask = None
        self.EveryoneMask = None
        self.NextOwnerMask = None
        self.OwnershipCost = None
        # TaxRate
        self.SaleType = None
        self.SalePrice = None
        self.AggregatePerms = None
        self.AggregatePermTextures = None
        self.AggregatePermTexturesOwner = None
        self.Category = None
        self.InventorySerial = None
        self.ItemID = None
        self.FolderID = None
        self.FromTaskID = None
        self.LastOwnerID = None
        self.Name = None
        self.Description = None
        self.TouchName = None
        self.SitName = None
        self.TextureID = None

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

    def update_properties(self, properties: Dict[str, Any]) -> Set[str]:
        """ takes a dictionary of attribute:value and makes it so """
        updated_properties = set()
        for key, val in properties.items():
            if hasattr(self, key):
                old_val = getattr(self, key, val)
                # Don't check equality if we're using a lazy proxy,
                # parsing is deferred until we actually use it.
                is_proxy = isinstance(val, lazy_object_proxy.Proxy)
                if is_proxy or old_val != val:
                    updated_properties.add(key)
                setattr(self, key, val)
        return updated_properties

    def to_dict(self):
        return recordclass.asdict(self)
