import abc
import dataclasses
import enum
import importlib
import logging
import zlib
from typing import *

import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.namevalue import NameValuesSerializer

try:
    importlib.reload(se)  # type: ignore
except:
    logging.exception("Failed to reload serialization lib")


@se.enum_field_serializer("RequestXfer", "XferID", "VFileType")
@se.enum_field_serializer("AssetUploadRequest", "AssetBlock", "Type")
@se.enum_field_serializer("AssetUploadComplete", "AssetBlock", "Type")
@se.enum_field_serializer("UpdateCreateInventoryItem", "InventoryData", "Type")
@se.enum_field_serializer("CreateInventoryItem", "InventoryBlock", "Type")
@se.enum_field_serializer("RezObject", "InventoryData", "Type")
@se.enum_field_serializer("RezScript", "InventoryBlock", "Type")
@se.enum_field_serializer("UpdateTaskInventory", "InventoryData", "Type")
class AssetType(enum.IntEnum):
    TEXTURE = 0
    SOUND = 1
    CALLINGCARD = 2
    LANDMARK = 3
    SCRIPT = 4
    CLOTHING = 5
    OBJECT = 6
    NOTECARD = 7
    CATEGORY = 8
    LSL_TEXT = 10
    LSL_BYTECODE = 11
    TEXTURE_TGA = 12
    BODYPART = 13
    SOUND_WAV = 17
    IMAGE_TGA = 18
    IMAGE_JPEG = 19
    ANIMATION = 20
    GESTURE = 21
    SIMSTATE = 22
    LINK = 24
    LINK_FOLDER = 25
    MARKETPLACE_FOLDER = 26
    WIDGET = 40
    PERSON = 45
    MESH = 49
    RESERVED_1 = 50
    RESERVED_2 = 51
    RESERVED_3 = 52
    RESERVED_4 = 53
    RESERVED_5 = 54
    RESERVED_6 = 55
    SETTINGS = 56
    UNKNOWN = 255
    NONE = -1

    @property
    def human_name(self):
        lower = self.name.lower()
        return {
            "animation": "animatn",
            "callingcard": "callcard",
            "texture_tga": "txtr_tga",
            "image_tga": "img_tga",
            "sound_wav": "snd_wav",
        }.get(lower, lower)

    @property
    def inventory_type(self):
        return {
            AssetType.TEXTURE: InventoryType.TEXTURE,
            AssetType.SOUND: InventoryType.SOUND,
            AssetType.CALLINGCARD: InventoryType.CALLINGCARD,
            AssetType.LANDMARK: InventoryType.LANDMARK,
            AssetType.SCRIPT: InventoryType.LSL,
            AssetType.CLOTHING: InventoryType.WEARABLE,
            AssetType.OBJECT: InventoryType.OBJECT,
            AssetType.NOTECARD: InventoryType.NOTECARD,
            AssetType.CATEGORY: InventoryType.CATEGORY,
            AssetType.LSL_TEXT: InventoryType.LSL,
            AssetType.LSL_BYTECODE: InventoryType.LSL,
            AssetType.TEXTURE_TGA: InventoryType.TEXTURE,
            AssetType.BODYPART: InventoryType.WEARABLE,
            AssetType.SOUND_WAV: InventoryType.SOUND,
            AssetType.ANIMATION: InventoryType.ANIMATION,
            AssetType.GESTURE: InventoryType.GESTURE,
            AssetType.WIDGET: InventoryType.WIDGET,
            AssetType.PERSON: InventoryType.PERSON,
            AssetType.MESH: InventoryType.MESH,
            AssetType.SETTINGS: InventoryType.SETTINGS,
        }.get(self, AssetType.NONE)


@se.enum_field_serializer("UpdateCreateInventoryItem", "InventoryData", "InvType")
@se.enum_field_serializer("CreateInventoryItem", "InventoryBlock", "InvType")
@se.enum_field_serializer("RezObject", "InventoryData", "InvType")
@se.enum_field_serializer("RezScript", "InventoryBlock", "InvType")
@se.enum_field_serializer("UpdateTaskInventory", "InventoryData", "InvType")
class InventoryType(enum.IntEnum):
    TEXTURE = 0
    SOUND = 1
    CALLINGCARD = 2
    LANDMARK = 3
    SCRIPT = 4
    CLOTHING = 5
    OBJECT = 6
    NOTECARD = 7
    CATEGORY = 8
    ROOT_CATEGORY = 9
    LSL = 10
    LSL_BYTECODE = 11
    TEXTURE_TGA = 12
    BODYPART = 13
    TRASH = 14
    SNAPSHOT = 15
    LOST_AND_FOUND = 16
    ATTACHMENT = 17
    WEARABLE = 18
    ANIMATION = 19
    GESTURE = 20
    MESH = 22
    WIDGET = 23
    PERSON = 24
    SETTINGS = 25
    UNKNOWN = 255
    NONE = -1

    @property
    def human_name(self):
        lower = self.name.lower()
        return {
            "callingcard": "callcard",
        }.get(lower, lower)


@se.enum_field_serializer("AgentIsNowWearing", "WearableData", "WearableType")
@se.enum_field_serializer("AgentWearablesUpdate", "WearableData", "WearableType")
@se.enum_field_serializer("CreateInventoryItem", "InventoryBlock", "WearableType")
class WearableType(enum.IntEnum):
    SHAPE = 0
    SKIN = 1
    HAIR = 2
    EYES = 3
    SHIRT = 4
    PANTS = 5
    SHOES = 6
    SOCKS = 7
    JACKET = 8
    GLOVES = 9
    UNDERSHIRT = 10
    UNDERPANTS = 11
    SKIRT = 12
    ALPHA = 13
    TATTOO = 14
    PHYSICS = 15
    UNIVERSAL = 16


def _register_permissions_flags(message_name, block_name):
    def _wrapper(flag_cls):
        for flag_type in {"EveryoneMask", "BaseMask", "OwnerMask", "GroupMask", "NextOwnerMask"}:
            se.flag_field_serializer(message_name, block_name, flag_type)(flag_cls)
        return flag_cls
    return _wrapper


@se.flag_field_serializer("ObjectPermissions", "ObjectData", "Mask")
@_register_permissions_flags("ObjectProperties", "ObjectData")
@_register_permissions_flags("UpdateCreateInventoryItem", "InventoryData")
@_register_permissions_flags("UpdateTaskInventory", "InventoryData")
@_register_permissions_flags("CreateInventoryItem", "InventoryBlock")
@_register_permissions_flags("RezObject", "RezData")
@_register_permissions_flags("RezObject", "InventoryData")
@_register_permissions_flags("RezScript", "InventoryBlock")
@_register_permissions_flags("RezMultipleAttachmentsFromInv", "ObjectData")
class Permissions(enum.IntFlag):
    TRANSFER = (1 << 13)
    MODIFY = (1 << 14)
    COPY = (1 << 15)
    # OpenSim export permission, per Firestorm. Deprecated parcel entry flag
    EXPORT_OR_PARCEL_ENTER = (1 << 16)
    # parcels, allow terraform, deprecated
    TERRAFORM = (1 << 17)
    # deprecated
    OWNER_DEBIT = (1 << 18)
    # objects, can grab/translate/rotate
    MOVE = (1 << 19)
    # parcels, avatars take damage, deprecated
    DAMAGE = (1 << 20)
    RESERVED = 1 << 31


@se.flag_field_serializer("RezObject", "RezData", "ItemFlags")
@se.flag_field_serializer("RezMultipleAttachmentsFromInv", "ObjectData", "ItemFlags")
@se.flag_field_serializer("RezObject", "InventoryData", "Flags")
@se.flag_field_serializer("UpdateCreateInventoryItem", "InventoryData", "Flags")
@se.flag_field_serializer("UpdateTaskInventory", "InventoryData", "Flags")
class InventoryItemFlags(enum.IntFlag):
    # The asset has only one reference in the system. If the
    # inventory item is deleted, or the assetid updated, then we
    # can remove the old reference.
    SHARED_SINGLE_REFERENCE = 0x40000000
    # Object permissions should have next owner perm be more
    # restrictive on rez. We bump this into the second byte of the
    # flags since the low byte is used to track attachment points.
    OBJECT_SLAM_PERM = 0x100
    # The object sale information has been changed.
    OBJECT_SLAM_SALE = 0x1000
    # Specify which permissions masks to overwrite
    # upon rez.  Normally, if no permissions slam (above) or
    # overwrite flags are set, the asset's permissions are
    # used and the inventory's permissions are ignored.  If
    # any of these flags are set, the inventory's permissions
    # take precedence.
    OBJECT_PERM_OVERWRITE_BASE = 0x010000
    OBJECT_PERM_OVERWRITE_OWNER = 0x020000
    OBJECT_PERM_OVERWRITE_GROUP = 0x040000
    OBJECT_PERM_OVERWRITE_EVERYONE = 0x080000
    OBJECT_PERM_OVERWRITE_NEXT_OWNER = 0x100000
    # Whether a returned object is composed of multiple items.
    OBJECT_HAS_MULTIPLE_ITEMS = 0x200000

    @property
    def attachment_point(self):
        return self & 0xFF


@se.enum_field_serializer("ObjectPermissions", "ObjectData", "Field")
class PermissionType(enum.IntEnum):
    BASE = 0x01
    OWNER = 0x02
    GROUP = 0x04
    EVERYONE = 0x08
    NEXT_OWNER = 0x10


@se.enum_field_serializer("TransferRequest", "TransferInfo", "SourceType")
class TransferSourceType(enum.IntEnum):
    UNKNOWN = 0
    FILE = enum.auto()
    ASSET = enum.auto()
    SIM_INV_ITEM = enum.auto()
    SIM_ESTATE = enum.auto()


class EstateAssetType(enum.IntEnum):
    NONE = -1
    COVENANT = 0


@dataclasses.dataclass
class TransferRequestParamsBase(abc.ABC):
    pass


@dataclasses.dataclass
class TransferRequestParamsFile(TransferRequestParamsBase):
    FileName: str = se.dataclass_field(se.CStr())
    Delete: bool = se.dataclass_field(se.BOOL)


@dataclasses.dataclass
class TransferRequestParamsAsset(TransferRequestParamsFile):
    AssetID: UUID = se.dataclass_field(se.UUID)
    AssetType: "AssetType" = se.dataclass_field(se.IntEnum(AssetType, se.U32))


@dataclasses.dataclass
class TransferRequestParamsSimInvItem(TransferRequestParamsBase):
    # Will never be None on the wire, just set this way so
    # code can fill them in when creating these ourselves.
    AgentID: Optional[UUID] = se.dataclass_field(se.UUID, default=None)
    SessionID: Optional[UUID] = se.dataclass_field(se.UUID, default=None)
    OwnerID: UUID = se.dataclass_field(se.UUID)
    TaskID: UUID = se.dataclass_field(se.UUID)
    ItemID: UUID = se.dataclass_field(se.UUID)
    AssetID: UUID = se.dataclass_field(se.UUID)
    AssetType: "AssetType" = se.dataclass_field(se.IntEnum(AssetType, se.U32))


@dataclasses.dataclass
class TransferRequestParamsSimEstate(TransferRequestParamsBase):
    # See above RE Optional
    AgentID: Optional[UUID] = se.dataclass_field(se.UUID, default=None)
    SessionID: Optional[UUID] = se.dataclass_field(se.UUID, default=None)
    EstateAssetType: "EstateAssetType" = se.dataclass_field(se.IntEnum(EstateAssetType, se.U32))


@se.subfield_serializer("TransferRequest", "TransferInfo", "Params")
class TransferParamsSerializer(se.EnumSwitchedSubfieldSerializer):
    ENUM_FIELD = "SourceType"
    TEMPLATES = {
        TransferSourceType.FILE: se.Dataclass(TransferRequestParamsFile),
        TransferSourceType.ASSET: se.Dataclass(TransferRequestParamsAsset),
        TransferSourceType.SIM_INV_ITEM: se.Dataclass(TransferRequestParamsSimInvItem),
        TransferSourceType.SIM_ESTATE: se.Dataclass(TransferRequestParamsSimEstate),
    }


@se.enum_field_serializer("TransferAbort", "TransferInfo", "ChannelType")
@se.enum_field_serializer("TransferPacket", "TransferData", "ChannelType")
@se.enum_field_serializer("TransferRequest", "TransferInfo", "ChannelType")
@se.enum_field_serializer("TransferInfo", "TransferInfo", "ChannelType")
class TransferChannelType(enum.IntEnum):
    UNKNOWN = 0
    MISC = enum.auto()
    ASSET = enum.auto()


@se.enum_field_serializer("TransferInfo", "TransferInfo", "TargetType")
class TransferTargetType(enum.IntEnum):
    UNKNOWN = 0
    FILE = enum.auto()
    VFILE = enum.auto()


@se.enum_field_serializer("TransferInfo", "TransferInfo", "Status")
@se.enum_field_serializer("TransferPacket", "TransferData", "Status")
class TransferStatus(enum.IntEnum):
    OK = 0
    DONE = 1
    SKIP = 2
    ABORT = 3
    ERROR = -1  # generic error
    UNKNOWN_SOURCE = -2  # not found
    INSUFFICIENT_PERMISSIONS = -3


@se.subfield_serializer("TransferInfo", "TransferInfo", "Params")
class TransferInfoSerializer(se.BaseSubfieldSerializer):
    TEMPLATES = {
        TransferTargetType.FILE: se.Template({
            "FileName": se.CStr(),
            "Delete": se.BOOL,
        }),
        TransferTargetType.VFILE: se.Template({
            "AgentID": se.UUID,
            "SessionID": se.UUID,
            "OwnerID": se.UUID,
            "TaskID": se.UUID,
            "ItemID": se.UUID,
            "AssetID": se.UUID,
            "AssetType": se.IntEnum(AssetType, se.U32),
        }),
    }

    @classmethod
    def _get_target_template(cls, block, val):
        target_type = block["TargetType"]
        if target_type != TransferTargetType.UNKNOWN:
            return cls.TEMPLATES[target_type]

        # Hard to tell what format the payload uses without tracking
        # which request this info message corresponds to. Brute force it.
        templates = TransferParamsSerializer.TEMPLATES.values()
        return cls._fuzzy_guess_template(templates, val)

    @classmethod
    def deserialize(cls, ctx_obj, val, pod=False):
        if not val:
            return se.UNSERIALIZABLE
        template = cls._get_target_template(ctx_obj, val)
        if not template:
            return se.UNSERIALIZABLE
        return cls._deserialize_template(template, val, pod)

    @classmethod
    def serialize(cls, ctx_obj, vals):
        template = cls._get_target_template(ctx_obj, vals)
        if not template:
            return se.UNSERIALIZABLE
        return cls._serialize_template(template, vals)


@se.enum_field_serializer("RequestXfer", "XferID", "FilePath")
class XferFilePath(enum.IntEnum):
    NONE = 0
    USER_SETTINGS = 1
    APP_SETTINGS = 2
    PER_SL_ACCOUNT = 3
    CACHE = 4
    CHARACTER = 5
    HELP = 6
    LOGS = 7
    TEMP = 8
    SKINS = 9
    TOP_SKIN = 10
    CHAT_LOGS = 11
    PER_ACCOUNT_CHAT_LOGS = 12
    USER_SKIN = 14
    LOCAL_ASSETS = 15
    EXECUTABLE = 16
    DEFAULT_SKIN = 17
    FONTS = 18
    DUMP = 19


@se.enum_field_serializer("AbortXfer", "XferID", "Result")
class XferError(enum.IntEnum):
    FILE_EMPTY = -44
    FILE_NOT_FOUND = -43
    CANNOT_OPEN_FILE = -42
    EOF = -39


@dataclasses.dataclass
class XferPacket(se.BitfieldDataclass):
    PacketID: int = se.bitfield_field(bits=31)
    IsEOF: bool = se.bitfield_field(bits=1, adapter=se.BoolAdapter())


@se.subfield_serializer("SendXferPacket", "XferID", "Packet")
class SendXferPacketIDSerializer(se.AdapterSubfieldSerializer):
    ORIG_INLINE = True
    ADAPTER = se.BitfieldDataclass(XferPacket)


@se.enum_field_serializer("ViewerEffect", "Effect", "Type")
class ViewerEffectType(enum.IntEnum):
    TEXT = 0
    ICON = enum.auto()
    CONNECTOR = enum.auto()
    FLEXIBLE_OBJECT = enum.auto()
    ANIMAL_CONTROLS = enum.auto()
    LOCAL_ANIMATION_OBJECT = enum.auto()
    CLOTH = enum.auto()
    EFFECT_BEAM = enum.auto()
    EFFECT_GLOW = enum.auto()
    EFFECT_POINT = enum.auto()
    EFFECT_TRAIL = enum.auto()
    EFFECT_SPHERE = enum.auto()
    EFFECT_SPIRAL = enum.auto()
    EFFECT_EDIT = enum.auto()
    EFFECT_LOOKAT = enum.auto()
    EFFECT_POINTAT = enum.auto()
    EFFECT_VOICE_VISUALIZER = enum.auto()
    NAME_TAG = enum.auto()
    EFFECT_BLOB = enum.auto()


class LookAtTarget(enum.IntEnum):
    NONE = 0
    IDLE = enum.auto()
    AUTO_LISTEN = enum.auto()
    FREELOOK = enum.auto()
    RESPOND = enum.auto()
    HOVER = enum.auto()
    CONVERSATION = enum.auto()
    SELECT = enum.auto()
    FOCUS = enum.auto()
    MOUSELOOK = enum.auto()
    CLEAR = enum.auto()


class PointAtTarget(enum.IntEnum):
    NONE = 0
    SELECT = enum.auto()
    GRAB = enum.auto()
    CLEAR = enum.auto()


@se.subfield_serializer("ViewerEffect", "Effect", "TypeData")
class ViewerEffectDataSerializer(se.EnumSwitchedSubfieldSerializer):
    ENUM_FIELD = "Type"
    # A lot of effect types that seem to have their own payload
    # actually use spiral's. Weird.
    SPIRAL_TEMPLATE = se.Template({
        "SourceID": se.UUID,
        "TargetID": se.UUID,
        "TargetPos": se.Vector3D,
    })
    TEMPLATES = {
        ViewerEffectType.EFFECT_POINTAT: se.Template({
            "SourceID": se.UUID,
            "TargetID": se.UUID,
            "TargetPos": se.Vector3D,
            "PointTargetType": se.IntEnum(PointAtTarget, se.U8),
        }),
        ViewerEffectType.EFFECT_BEAM: SPIRAL_TEMPLATE,
        ViewerEffectType.EFFECT_EDIT: SPIRAL_TEMPLATE,
        ViewerEffectType.EFFECT_SPHERE: SPIRAL_TEMPLATE,
        ViewerEffectType.EFFECT_POINT: SPIRAL_TEMPLATE,
        ViewerEffectType.EFFECT_LOOKAT: se.Template({
            "SourceID": se.UUID,
            "TargetID": se.UUID,
            "TargetPos": se.Vector3D,
            "LookTargetType": se.IntEnum(LookAtTarget, se.U8),
        }),
        ViewerEffectType.EFFECT_SPIRAL: SPIRAL_TEMPLATE,
    }


@se.enum_field_serializer("MoneyTransferRequest", "MoneyData", "TransactionType")
@se.enum_field_serializer("MoneyBalanceReply", "TransactionInfo", "TransactionType")
class MoneyTransactionType(enum.IntEnum):
    # _many_ of these codes haven't been used in decades.
    # Money transaction failure codes
    NULL = 0
    # Error conditions
    FAIL_SIMULATOR_TIMEOUT = 1
    FAIL_DATASERVER_TIMEOUT = 2
    FAIL_APPLICATION = 3
    # Everything past this is actual transaction types
    OBJECT_CLAIM = 1000
    LAND_CLAIM = 1001
    GROUP_CREATE = 1002
    OBJECT_PUBLIC_CLAIM = 1003
    GROUP_JOIN = 1004
    TELEPORT_CHARGE = 1100
    UPLOAD_CHARGE = 1101
    LAND_AUCTION = 1102
    CLASSIFIED_CHARGE = 1103
    OBJECT_TAX = 2000
    LAND_TAX = 2001
    LIGHT_TAX = 2002
    PARCEL_DIR_FEE = 2003
    GROUP_TAX = 2004
    CLASSIFIED_RENEW = 2005
    RECURRING_GENERIC = 2100
    GIVE_INVENTORY = 3000
    OBJECT_SALE = 5000
    GIFT = 5001
    LAND_SALE = 5002
    REFER_BONUS = 5003
    INVENTORY_SALE = 5004
    REFUND_PURCHASE = 5005
    LAND_PASS_SALE = 5006
    DWELL_BONUS = 5007
    PAY_OBJECT = 5008
    OBJECT_PAYS = 5009
    RECURRING_GENERIC_USER = 5100
    GROUP_JOIN_RESERVED = 6000
    GROUP_LAND_DEED = 6001
    GROUP_OBJECT_DEED = 6002
    GROUP_LIABILITY = 6003
    GROUP_DIVIDEND = 6004
    MEMBERSHIP_DUES = 6005
    OBJECT_RELEASE = 8000
    LAND_RELEASE = 8001
    OBJECT_DELETE = 8002
    OBJECT_PUBLIC_DECAY = 8003
    OBJECT_PUBLIC_DELETE = 8004
    LINDEN_ADJUSTMENT = 9000
    LINDEN_GRANT = 9001
    LINDEN_PENALTY = 9002
    EVENT_FEE = 9003
    EVENT_PRIZE = 9004
    STIPEND_BASIC = 10000
    STIPEND_DEVELOPER = 10001
    STIPEND_ALWAYS = 10002
    STIPEND_DAILY = 10003
    STIPEND_RATING = 10004
    STIPEND_DELTA = 10005


@se.flag_field_serializer("MoneyTransferRequest", "MoneyData", "Flags")
class MoneyTransactionFlags(enum.IntFlag):
    SOURCE_GROUP = 1
    DEST_GROUP = 1 << 1
    OWNER_GROUP = 1 << 2
    SIMULTANEOUS_CONTRIBUTION = 1 << 3
    SIMULTANEOUS_CONTRIBUTION_REMOVAL = 1 << 4


@se.enum_field_serializer("ImprovedInstantMessage", "MessageBlock", "Dialog")
class IMDialogType(enum.IntEnum):
    NOTHING_SPECIAL = 0
    MESSAGEBOX = 1
    GROUP_INVITATION = 3
    INVENTORY_OFFERED = 4
    INVENTORY_ACCEPTED = 5
    INVENTORY_DECLINED = 6
    GROUP_VOTE = 7
    GROUP_MESSAGE_DEPRECATED = 8
    TASK_INVENTORY_OFFERED = 9
    TASK_INVENTORY_ACCEPTED = 10
    TASK_INVENTORY_DECLINED = 11
    NEW_USER_DEFAULT = 12
    SESSION_INVITE = 13
    SESSION_P2P_INVITE = 14
    SESSION_GROUP_START = 15
    SESSION_CONFERENCE_START = 16
    SESSION_SEND = 17
    SESSION_LEAVE = 18
    FROM_TASK = 19
    DO_NOT_DISTURB_AUTO_RESPONSE = 20
    CONSOLE_AND_CHAT_HISTORY = 21
    LURE_USER = 22
    LURE_ACCEPTED = 23
    LURE_DECLINED = 24
    GODLIKE_LURE_USER = 25
    TELEPORT_REQUEST = 26
    GROUP_ELECTION_DEPRECATED = 27
    GOTO_URL = 28
    FROM_TASK_AS_ALERT = 31
    GROUP_NOTICE = 32
    GROUP_NOTICE_INVENTORY_ACCEPTED = 33
    GROUP_NOTICE_INVENTORY_DECLINED = 34
    GROUP_INVITATION_ACCEPT = 35
    GROUP_INVITATION_DECLINE = 36
    GROUP_NOTICE_REQUESTED = 37
    FRIENDSHIP_OFFERED = 38
    FRIENDSHIP_ACCEPTED = 39
    FRIENDSHIP_DECLINED_DEPRECATED = 40
    TYPING_START = 41
    TYPING_STOP = 42


@se.subfield_serializer("ImprovedInstantMessage", "MessageBlock", "BinaryBucket")
class InstantMessageBucketSerializer(se.EnumSwitchedSubfieldSerializer):
    ENUM_FIELD = "Dialog"
    # Aliases for clarity
    EMPTY_BUCKET = se.UNSERIALIZABLE
    PLAIN_STRING = se.UNSERIALIZABLE

    ACCEPTED_INVENTORY = se.Template({
        "TargetCategoryID": se.UUID,
    })
    # This is in a different, string format if it comes in through the
    # ReadOfflineMsgs Cap but we don't parse those.
    GROUP_NOTICE = se.Template({
        "HasInventory": se.BOOL,
        "AssetType": se.IntEnum(AssetType, se.U8),
        "GroupID": se.UUID,
        "ItemName": se.CStr(),
    })
    TEMPLATES = {
        IMDialogType.SESSION_GROUP_START: EMPTY_BUCKET,
        IMDialogType.INVENTORY_OFFERED: se.Template({
            "AssetType": se.IntEnum(AssetType, se.U8),
            "ItemID": se.UUID,
            # Greedy, no length field.
            "Children": se.Collection(
                None,
                se.Template({
                    "AssetType": se.IntEnum(AssetType, se.U8),
                    "ItemID": se.UUID,
                }),
            ),
        }),
        # Either binary AssetType or serialized string if from when offline. WTF?
        IMDialogType.TASK_INVENTORY_OFFERED: se.Template({
            "AssetType": se.IntEnum(AssetType, se.U8),
        }),
        IMDialogType.TASK_INVENTORY_ACCEPTED: ACCEPTED_INVENTORY,
        IMDialogType.GROUP_NOTICE_INVENTORY_ACCEPTED: ACCEPTED_INVENTORY,
        IMDialogType.INVENTORY_ACCEPTED: ACCEPTED_INVENTORY,
        IMDialogType.INVENTORY_DECLINED: EMPTY_BUCKET,
        IMDialogType.GROUP_NOTICE_INVENTORY_DECLINED: EMPTY_BUCKET,
        IMDialogType.TASK_INVENTORY_DECLINED: EMPTY_BUCKET,
        IMDialogType.NOTHING_SPECIAL: EMPTY_BUCKET,
        IMDialogType.TYPING_START: EMPTY_BUCKET,
        IMDialogType.TYPING_STOP: EMPTY_BUCKET,
        # It's a string, just read it as-is.
        IMDialogType.LURE_USER: PLAIN_STRING,
        IMDialogType.TELEPORT_REQUEST: PLAIN_STRING,
        IMDialogType.GODLIKE_LURE_USER: PLAIN_STRING,
        IMDialogType.SESSION_LEAVE: EMPTY_BUCKET,
        IMDialogType.DO_NOT_DISTURB_AUTO_RESPONSE: EMPTY_BUCKET,
        IMDialogType.FRIENDSHIP_OFFERED: EMPTY_BUCKET,
        IMDialogType.FRIENDSHIP_ACCEPTED: EMPTY_BUCKET,
        IMDialogType.FRIENDSHIP_DECLINED_DEPRECATED: EMPTY_BUCKET,
        IMDialogType.GROUP_NOTICE: GROUP_NOTICE,
        IMDialogType.GROUP_NOTICE_REQUESTED: GROUP_NOTICE,
        IMDialogType.GROUP_INVITATION: se.Template({
            "JoinCost": se.S32,
            "RoleID": se.UUID,
        }),
        # Just a string
        IMDialogType.FROM_TASK: PLAIN_STRING,
        # Session name
        IMDialogType.SESSION_SEND: PLAIN_STRING,
        # What? Is this even used?
        IMDialogType.GOTO_URL: PLAIN_STRING,
    }


@se.subfield_serializer("ObjectUpdate", "ObjectData", "ObjectData")
class ObjectUpdateDataSerializer(se.SimpleSubfieldSerializer):
    # http://wiki.secondlife.com/wiki/ObjectUpdate#ObjectData_Format
    REGION_SIZE = 256.0
    MIN_HEIGHT = -REGION_SIZE
    MAX_HEIGHT = 4096.0

    POSITION_COMPONENT_SCALES = (
        (-0.5 * REGION_SIZE, 1.5 * REGION_SIZE),
        (-0.5 * REGION_SIZE, 1.5 * REGION_SIZE),
        (MIN_HEIGHT, MAX_HEIGHT),
    )

    FLOAT_TEMPLATE = {
        "Position": se.Vector3,
        "Velocity": se.Vector3,
        "Acceleration": se.Vector3,
        "Rotation": se.PackedQuat(se.Vector3),
        "AngularVelocity": se.Vector3,
    }
    HALF_PRECISION_TEMPLATE = {
        "Position": se.Vector3U16(component_scales=POSITION_COMPONENT_SCALES),
        "Velocity": se.Vector3U16(-REGION_SIZE, REGION_SIZE),
        "Acceleration": se.Vector3U16(-REGION_SIZE, REGION_SIZE),
        "Rotation": se.PackedQuat(se.Vector4U16(-1.0, 1.0)),
        "AngularVelocity": se.Vector3U16(-REGION_SIZE, REGION_SIZE),
    }
    LOW_PRECISION_TEMPLATE = {
        "Position": se.Vector3U8(component_scales=POSITION_COMPONENT_SCALES),
        "Velocity": se.Vector3U8(-REGION_SIZE, REGION_SIZE),
        "Acceleration": se.Vector3U8(-REGION_SIZE, REGION_SIZE),
        "Rotation": se.PackedQuat(se.Vector4U8(-1.0, 1.0)),
        "AngularVelocity": se.Vector3U8(-REGION_SIZE, REGION_SIZE),
    }

    TEMPLATE = se.LengthSwitch({
        76: se.Template({"FootCollisionPlane": se.Vector4, **FLOAT_TEMPLATE}),
        60: se.Template(FLOAT_TEMPLATE),
        48: se.Template({"FootCollisionPlane": se.Vector4, **HALF_PRECISION_TEMPLATE}),
        32: se.Template(HALF_PRECISION_TEMPLATE),
        16: se.Template(LOW_PRECISION_TEMPLATE),
    })


@se.enum_field_serializer("ObjectUpdate", "ObjectData", "PCode")
@se.enum_field_serializer("ObjectAdd", "ObjectData", "PCode")
class PCode(enum.IntEnum):
    # Should actually be a bitmask, these are just some common ones.
    PRIMITIVE = 9
    AVATAR = 47
    GRASS = 95
    NEW_TREE = 111
    PARTICLE_SYSTEM = 143
    TREE = 255


@se.flag_field_serializer("ObjectUpdate", "ObjectData", "UpdateFlags")
@se.flag_field_serializer("ObjectUpdateCompressed", "ObjectData", "UpdateFlags")
@se.flag_field_serializer("ObjectUpdateCached", "ObjectData", "UpdateFlags")
@se.flag_field_serializer("ObjectAdd", "ObjectData", "AddFlags")
class ObjectUpdateFlags(enum.IntFlag):
    USE_PHYSICS = 1 << 0
    CREATE_SELECTED = 1 << 1
    OBJECT_MODIFY = 1 << 2
    OBJECT_COPY = 1 << 3
    OBJECT_ANY_OWNER = 1 << 4
    OBJECT_YOU_OWNER = 1 << 5
    SCRIPTED = 1 << 6
    HANDLE_TOUCH = 1 << 7
    OBJECT_MOVE = 1 << 8
    TAKES_MONEY = 1 << 9
    PHANTOM = 1 << 10
    INVENTORY_EMPTY = 1 << 11
    AFFECTS_NAVMESH = 1 << 12
    CHARACTER = 1 << 13
    VOLUME_DETECT = 1 << 14
    INCLUDE_IN_SEARCH = 1 << 15
    ALLOW_INVENTORY_DROP = 1 << 16
    OBJECT_TRANSFER = 1 << 17
    OBJECT_GROUP_OWNED = 1 << 18
    OBJECT_YOU_OFFICER_DEPRECATED = 1 << 19
    CAMERA_DECOUPLED = 1 << 20
    ANIM_SOURCE = 1 << 21
    CAMERA_SOURCE = 1 << 22
    CAST_SHADOWS_DEPRECATED = 1 << 23
    UNUSED_002 = 1 << 24
    UNUSED_003 = 1 << 25
    UNUSED_004 = 1 << 26
    UNUSED_005 = 1 << 27
    OBJECT_OWNER_MODIFY = 1 << 28
    TEMPORARY_ON_REZ = 1 << 29
    TEMPORARY_DEPRECATED = 1 << 30
    ZLIB_COMPRESSED_REPRECATED = 1 << 31


class AttachmentStateAdapter(se.Adapter):
    # Encoded attachment point ID for attached objects
    # nibbles are swapped around because old attachment nums only used to live
    # in the high bits, I guess.
    OFFSET = 4
    MASK = 0xF << OFFSET

    def _rotate_nibbles(self, val: int):
        return ((val & self.MASK) >> self.OFFSET) | ((val & ~self.MASK) << self.OFFSET)

    def decode(self, val: Any, ctx: Optional[se.ParseContext], pod: bool = False) -> Any:
        return self._rotate_nibbles(val)

    def encode(self, val: Any, ctx: Optional[se.ParseContext]) -> Any:
        # f(f(x)) = x
        return self._rotate_nibbles(val)


@se.flag_field_serializer("AgentUpdate", "AgentData", "State")
class AgentState(enum.IntFlag):
    TYPING = 1 << 3
    EDITING = 1 << 4


class ObjectStateAdapter(se.ContextAdapter):
    # State has a different meaning depending on PCode
    def __init__(self, child_spec: Optional[se.SERIALIZABLE_TYPE]):
        super().__init__(
            lambda ctx: ctx.PCode, child_spec, {
                PCode.AVATAR: se.IntFlag(AgentState),
                PCode.PRIMITIVE: AttachmentStateAdapter(None),
                # Other cases are probably just a number (tree species ID or something.)
                dataclasses.MISSING: se.IdentityAdapter(),
            }
        )


@se.subfield_serializer("ObjectUpdate", "ObjectData", "State")
@se.subfield_serializer("ObjectAdd", "ObjectData", "State")
class ObjectStateSerializer(se.AdapterSubfieldSerializer):
    ADAPTER = ObjectStateAdapter(None)
    ORIG_INLINE = True


@se.subfield_serializer("ImprovedTerseObjectUpdate", "ObjectData", "Data")
class ImprovedTerseObjectUpdateDataSerializer(se.SimpleSubfieldSerializer):
    TEMPLATE = se.Template({
        "ID": se.U32,
        # No inline PCode, so can't make sense of State at the message level
        "State": se.U8,
        "FootCollisionPlane": se.OptionalPrefixed(se.Vector4),
        "Position": se.Vector3,
        "Velocity": se.Vector3U16(-128.0, 128.0),
        "Acceleration": se.Vector3U16(-64.0, 64.0),
        "Rotation": se.PackedQuat(se.Vector4U16(-1.0, 1.0)),
        "AngularVelocity": se.Vector3U16(-64.0, 64.0),
    })


class ShineLevel(enum.IntEnum):
    OFF = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclasses.dataclass
class BasicMaterials:
    # Meaning is technically implementation-dependent, these are in LL data files
    Bump: int = se.bitfield_field(bits=5)
    FullBright: bool = se.bitfield_field(bits=1, adapter=se.BoolAdapter())
    Shiny: int = se.bitfield_field(bits=2, adapter=se.IntEnum(ShineLevel))


BUMP_SHINY_FULLBRIGHT = se.BitfieldDataclass(BasicMaterials, se.U8)


class TexGen(enum.IntEnum):
    DEFAULT = 0
    PLANAR = 0x2
    # These are unused / not supported
    SPHERICAL = 0x4
    CYLINDRICAL = 0x6


@dataclasses.dataclass
class MediaFlags:
    WebPage: bool = se.bitfield_field(bits=1, adapter=se.BoolAdapter())
    TexGen: "TexGen" = se.bitfield_field(bits=2, adapter=se.IntEnum(TexGen))
    # Probably unused but show it just in case
    _Unused: int = se.bitfield_field(bits=5)


# Not shifted so enum definitions can match indra
MEDIA_FLAGS = se.BitfieldDataclass(MediaFlags, se.U8, shift=False)


class Color4(se.SerializableBase):
    def __init__(self, invert_bytes=False, invert_alpha=False):
        # There's several different ways of representing colors, presumably
        # to allow for more efficient zerocoding in common cases.
        self.invert_bytes = invert_bytes
        self.invert_alpha = invert_alpha
        self._bytes_templ = se.BytesFixed(4)

    def _invert(self, val: bytes) -> bytes:
        if self.invert_bytes:
            val = bytes(~x & 0xFF for x in val)
        if self.invert_alpha:
            val = val[:3] + bytes((~val[4] & 0xFF,))
        return val

    def serialize(self, val, writer: se.BufferWriter, ctx=None):
        self._bytes_templ.serialize(self._invert(val), writer, ctx)

    def deserialize(self, reader: se.BufferReader, ctx=None):
        return self._invert(self._bytes_templ.deserialize(reader, ctx))


class TEFaceBitfield(se.SerializableBase):
    """
    Arbitrary-length bitfield of faces

    0x80 bit indicates bitfield has more bytes. Each byte can represent
    on / off for 7 faces.
    """

    @classmethod
    def deserialize(cls, reader: se.BufferReader, ctx=None):
        have_next = True
        val = 0
        while have_next:
            char = reader.read(se.U8, ctx=ctx)
            have_next = char & 0x80
            val |= char & 0x7F
            if have_next:
                val <<= 7

        # Bitfield of faces reconstructed, convert to tuple
        i = 0
        face_list = []
        while val:
            if val & 1:
                face_list.append(i)
            i += 1
            val >>= 1
        return tuple(face_list)

    @classmethod
    def serialize(cls, faces, writer: se.BufferWriter, ctx=None):
        packed = 0
        for face in faces:
            packed |= 1 << face

        char_arr = []
        while packed:
            # 7 faces per byte
            val = packed & 0x7F
            packed >>= 7
            char_arr.append(val)
        char_arr.reverse()

        while char_arr:
            val = char_arr.pop(0)
            # need a continuation
            if char_arr:
                val |= 0x80
            writer.write(se.U8, val, ctx=ctx)


class TEExceptionField(se.SerializableBase):
    """
    TextureEntry field with a "default" value and trailing "exception" values

    Each value that deviates from the default value is added as an "exception,"
    prefixed with a bitfield of face numbers it applies to. A field is terminated
    with a NUL, so long as it's not the last field. In that case, EOF implicitly
    terminates.
    """

    def __init__(self, spec, optional=False, first=False):
        self._spec = spec
        self._first = first
        self._optional = optional

    def serialize(self, vals, writer: se.BufferWriter, ctx=None):
        if self._optional and not vals:
            return

        # NUL needed to mark the start of a field if this isn't the first one
        if not self._first:
            writer.write_bytes(b"\x00")

        ctx = se.ParseContext(vals, parent=ctx)

        default = vals[None]
        writer.write(self._spec, default, ctx=ctx)
        for faces, val in vals.items():
            if faces is None:
                continue
            writer.write(TEFaceBitfield, faces, ctx=ctx)
            writer.write(self._spec, val, ctx=ctx)

    def deserialize(self, reader: se.BufferReader, ctx=None):
        # No bytes left and this is an optional field
        if self._optional and not reader:
            return None

        # Technically there's nothing preventing an implementation from
        # repeating a face bitfield. You can use a MultiDict to preserve
        # any duplicate keys if you care, but it's incredibly slow.
        vals = {}
        ctx = se.ParseContext(vals, parent=ctx)
        vals[None] = reader.read(self._spec, ctx=ctx)
        while reader:
            faces = reader.read(TEFaceBitfield, ctx=ctx)
            if not faces:
                break
            # Key will be a tuple of face numbers
            vals[faces] = reader.read(self._spec, ctx=ctx)
        return vals

    def default_value(self):
        return dict


def _te_dataclass_field(spec: se.SERIALIZABLE_TYPE, first=False, optional=False):
    return se.dataclass_field(TEExceptionField(spec, first=first, optional=optional))


_T = TypeVar("_T")
TE_FIELD_TYPE = Dict[Optional[Sequence[int]], _T]


@dataclasses.dataclass
class TextureEntry:
    Textures: TE_FIELD_TYPE[UUID] = _te_dataclass_field(se.UUID, first=True)
    # Bytes are inverted so fully opaque white is \x00\x00\x00\x00
    Color: TE_FIELD_TYPE[bytes] = _te_dataclass_field(Color4(invert_bytes=True))
    ScalesS: TE_FIELD_TYPE[float] = _te_dataclass_field(se.F32)
    ScalesT: TE_FIELD_TYPE[float] = _te_dataclass_field(se.F32)
    OffsetsS: TE_FIELD_TYPE[int] = _te_dataclass_field(se.S16)
    OffsetsT: TE_FIELD_TYPE[int] = _te_dataclass_field(se.S16)
    Rotation: TE_FIELD_TYPE[int] = _te_dataclass_field(se.S16)
    BasicMaterials: TE_FIELD_TYPE["BasicMaterials"] = _te_dataclass_field(BUMP_SHINY_FULLBRIGHT)
    MediaFlags: TE_FIELD_TYPE["MediaFlags"] = _te_dataclass_field(MEDIA_FLAGS)
    Glow: TE_FIELD_TYPE[int] = _te_dataclass_field(se.U8)
    Materials: TE_FIELD_TYPE[UUID] = _te_dataclass_field(se.UUID, optional=True)


TE_SERIALIZER = se.Dataclass(TextureEntry)


@se.subfield_serializer("ObjectUpdate", "ObjectData", "TextureEntry")
@se.subfield_serializer("AvatarAppearance", "ObjectData", "TextureEntry")
@se.subfield_serializer("AgentSetAppearance", "ObjectData", "TextureEntry")
@se.subfield_serializer("ObjectImage", "ObjectData", "TextureEntry")
class TextureEntrySubfieldSerializer(se.SimpleSubfieldSerializer):
    EMPTY_IS_NONE = True
    TEMPLATE = TE_SERIALIZER


DATA_PACKER_TE_TEMPLATE = se.TypedByteArray(
    se.U32,
    TE_SERIALIZER,
    empty_is_none=True,
    # TODO: Let Readers have lazy=False prop and let addons call
    #  out what subfield serializers should not be lazy. Lazy is way
    #  more expensive if you're going to deserialize every TE anyway
    lazy=True,
)


@se.subfield_serializer("ImprovedTerseObjectUpdate", "ObjectData", "TextureEntry")
class DPTextureEntrySubfieldSerializer(se.SimpleSubfieldSerializer):
    EMPTY_IS_NONE = True
    TEMPLATE = DATA_PACKER_TE_TEMPLATE


class TextureAnimMode(enum.IntFlag):
    ON = 0x01
    LOOP = 0x02
    REVERSE = 0x04
    PING_PONG = 0x08
    SMOOTH = 0x10
    ROTATE = 0x20
    SCALE = 0x40


@dataclasses.dataclass
class TextureAnim:
    Mode: TextureAnimMode = se.dataclass_field(se.IntFlag(TextureAnimMode, se.U8))
    Face: int = se.dataclass_field(se.S8)
    SizeX: int = se.dataclass_field(se.U8)
    SizeY: int = se.dataclass_field(se.U8)
    Start: float = se.dataclass_field(se.F32)
    Length: float = se.dataclass_field(se.F32)
    Rate: float = se.dataclass_field(se.F32)


TA_TEMPLATE = se.Dataclass(TextureAnim)


@se.subfield_serializer("ObjectUpdate", "ObjectData", "TextureAnim")
class TextureAnimSerializer(se.SimpleSubfieldSerializer):
    EMPTY_IS_NONE = True
    TEMPLATE = TA_TEMPLATE


@se.subfield_serializer("ObjectProperties", "ObjectData", "TextureID")
class TextureIDListSerializer(se.SimpleSubfieldSerializer):
    EMPTY_IS_NONE = True
    TEMPLATE = se.Collection(None, se.UUID)


class ParticleDataFlags(enum.IntFlag):
    INTERP_COLOR = 0x001
    INTERP_SCALE = 0x002
    BOUNCE = 0x004
    WIND = 0x008
    FOLLOW_SRC = 0x010
    FOLLOW_VELOCITY = 0x020
    TARGET_POS = 0x040
    TARGET_LINEAR = 0x080
    EMISSIVE = 0x100
    BEAM = 0x200
    RIBBON = 0x400
    DATA_GLOW = 0x10000
    DATA_BLEND = 0x20000


class ParticleFlags(enum.IntFlag):
    OBJECT_RELATIVE = 0x1
    USE_NEW_ANGLE = 0x2


class ParticleBlendFunc(enum.IntEnum):
    ONE = 0
    ZERO = 1
    DEST_COLOR = 2
    SOURCE_COLOR = 3
    ONE_MINUS_DEST_COLOR = 4
    ONE_MINUS_SOURCE_COLOR = 5
    DEST_ALPHA = 6
    SOURCE_ALPHA = 7
    ONE_MINUS_DEST_ALPHA = 8
    ONE_MINUS_SOURCE_ALPHA = 9


PARTDATA_FLAGS = se.IntFlag(ParticleDataFlags, se.U32)


class PartDataOption(se.OptionalFlagged):
    def __init__(self, flag_val, spec):
        super().__init__("PDataFlags", PARTDATA_FLAGS, flag_val, spec)


PDATA_BLOCK_TEMPLATE = se.Template({
    "PDataFlags": PARTDATA_FLAGS,
    "PDataMaxAge": se.FixedPoint(se.U16, 8, 8),
    "StartColor": Color4(),
    "EndColor": Color4(),
    "StartScaleX": se.FixedPoint(se.U8, 3, 5),
    "StartScaleY": se.FixedPoint(se.U8, 3, 5),
    "EndScaleX": se.FixedPoint(se.U8, 3, 5),
    "EndScaleY": se.FixedPoint(se.U8, 3, 5),
    "StartGlow": PartDataOption(ParticleDataFlags.DATA_GLOW, se.QuantizedFloat(se.U8, 0.0, 1.0)),
    "EndGlow": PartDataOption(ParticleDataFlags.DATA_GLOW, se.QuantizedFloat(se.U8, 0.0, 1.0)),
    "BlendSource": PartDataOption(ParticleDataFlags.DATA_BLEND, se.IntEnum(ParticleBlendFunc, se.U8)),
    "BlendDest": PartDataOption(ParticleDataFlags.DATA_BLEND, se.IntEnum(ParticleBlendFunc, se.U8)),
})


class PartPattern(enum.IntFlag):
    NONE = 0
    DROP = 0x1
    EXPLODE = 0x2
    ANGLE = 0x4
    ANGLE_CONE = 0x8
    ANGLE_CONE_EMPTY = 0x10


PSYS_BLOCK_TEMPLATE = se.Template({
    "CRC": se.U32,
    "PSysFlags": se.IntFlag(ParticleFlags, se.U32),
    "Pattern": se.IntFlag(PartPattern, se.U8),
    "PSysMaxAge": se.FixedPoint(se.U16, 8, 8),
    "StartAge": se.FixedPoint(se.U16, 8, 8),
    "InnerAngle": se.FixedPoint(se.U8, 3, 5),
    "OuterAngle": se.FixedPoint(se.U8, 3, 5),
    "BurstRate": se.FixedPoint(se.U16, 8, 8),
    "BurstRadius": se.FixedPoint(se.U16, 8, 8),
    "BurstSpeedMin": se.FixedPoint(se.U16, 8, 8),
    "BurstSpeedMax": se.FixedPoint(se.U16, 8, 8),
    "BurstPartCount": se.U8,
    "VelX": se.FixedPoint(se.U16, 8, 7, signed=True),
    "VelY": se.FixedPoint(se.U16, 8, 7, signed=True),
    "VelZ": se.FixedPoint(se.U16, 8, 7, signed=True),
    "AccelX": se.FixedPoint(se.U16, 8, 7, signed=True),
    "AccelY": se.FixedPoint(se.U16, 8, 7, signed=True),
    "AccelZ": se.FixedPoint(se.U16, 8, 7, signed=True),
    "Texture": se.UUID,
    "Target": se.UUID,
})

PSBLOCK_TEMPLATE = se.LengthSwitch({
    0: se.Null,
    86: se.Template({"PSys": PSYS_BLOCK_TEMPLATE, "PData": PDATA_BLOCK_TEMPLATE}),
    # Catch-all, this is a variable-length psblock
    None: se.Template({
        "PSys": se.TypedByteArray(se.S32, PSYS_BLOCK_TEMPLATE),
        "PData": se.TypedByteArray(se.S32, PDATA_BLOCK_TEMPLATE),
    })
})


@se.subfield_serializer("ObjectUpdate", "ObjectData", "PSBlock")
class PSBlockSerializer(se.SimpleSubfieldSerializer):
    TEMPLATE = PSBLOCK_TEMPLATE


@se.enum_field_serializer("ObjectExtraParams", "ObjectData", "ParamType")
class ExtraParamType(enum.IntEnum):
    FLEXIBLE = 0x10
    LIGHT = 0x20
    SCULPT = 0x30
    LIGHT_IMAGE = 0x40
    RESERVED = 0x50
    MESH = 0x60
    EXTENDED_MESH = 0x70


class ExtendedMeshFlags(enum.IntFlag):
    ANIMATED_MESH = 0x1


class SculptType(enum.IntEnum):
    NONE = 0
    SPHERE = 1
    TORUS = 2
    PLANE = 3
    CYLINDER = 4
    MESH = 5


@dataclasses.dataclass
class SculptTypeData:
    Type: SculptType = se.bitfield_field(bits=6, adapter=se.IntEnum(SculptType))
    Invert: bool = se.bitfield_field(bits=1, adapter=se.BoolAdapter())
    Mirror: bool = se.bitfield_field(bits=1, adapter=se.BoolAdapter())


EXTRA_PARAM_TEMPLATES = {
    ExtraParamType.FLEXIBLE: se.Template({
        "Tension": se.BitField(se.U8, {"Tension": 6, "Softness1": 2}),
        "Drag": se.BitField(se.U8, {"Drag": 7, "Softness2": 1}),
        "Gravity": se.U8,
        "Wind": se.U8,
        "UserForce": se.IfPresent(se.Vector3),
    }),
    ExtraParamType.LIGHT: se.Template({
       "Color": Color4(),
       "Radius": se.F32,
       "Cutoff": se.F32,
       "Falloff": se.F32,
    }),
    ExtraParamType.SCULPT: se.Template({
        "Texture": se.UUID,
        "TypeData": se.BitfieldDataclass(SculptTypeData, se.U8),
    }),
    ExtraParamType.LIGHT_IMAGE: se.Template({
        "Texture": se.UUID,
        "FOV": se.F32,
        "Focus": se.F32,
        "Ambiance": se.F32,
    }),
    ExtraParamType.MESH: se.Template({
        "Asset": se.UUID,
        "TypeData": se.BitfieldDataclass(SculptTypeData, se.U8),
    }),
    ExtraParamType.EXTENDED_MESH: se.Template({
        "Flags": se.IntFlag(ExtendedMeshFlags, se.U32),
    }),
}


@se.subfield_serializer("ObjectExtraParams", "ObjectData", "ParamData")
class ObjectExtraParamsDataSerializer(se.EnumSwitchedSubfieldSerializer):
    ENUM_FIELD = "ParamType"
    TEMPLATES = EXTRA_PARAM_TEMPLATES


EXTRA_PARAM_COLLECTION = se.DictAdapter(se.Collection(
    length=se.U8,
    entry_ser=se.EnumSwitch(se.IntEnum(ExtraParamType, se.U16), {
        t: se.TypedByteArray(se.U32, v) for t, v in EXTRA_PARAM_TEMPLATES.items()
    }),
))


@se.subfield_serializer("ObjectUpdate", "ObjectData", "ExtraParams")
class ObjectUpdateExtraParamsSerializer(se.SimpleSubfieldSerializer):
    TEMPLATE = EXTRA_PARAM_COLLECTION
    EMPTY_IS_NONE = True


@se.flag_field_serializer("ObjectUpdate", "ObjectData", "Flags")
class SoundFlags(enum.IntFlag):
    LOOP = 1 << 0
    SYNC_MASTER = 1 << 1
    SYNC_SLAVE = 1 << 2
    SYNC_PENDING = 1 << 3
    QUEUE = 1 << 4
    STOP = 1 << 5


class CompressedFlags(enum.IntFlag):
    SCRATCHPAD = 1
    TREE = 1 << 1
    TEXT = 1 << 2
    PARTICLES = 1 << 3
    SOUND = 1 << 4
    PARENT_ID = 1 << 5
    TEXTURE_ANIM = 1 << 6
    ANGULAR_VELOCITY = 1 << 7
    NAME_VALUES = 1 << 8
    MEDIA_URL = 1 << 9
    PARTICLES_NEW = 1 << 10


UPDATE_COMPRESSED_FLAGS = se.IntFlag(CompressedFlags, se.U32)


class CompressedOption(se.OptionalFlagged):
    def __init__(self, flag_val, spec):
        super().__init__("Flags", UPDATE_COMPRESSED_FLAGS, flag_val, spec)


NAMEVALUES_TERMINATED_TEMPLATE = se.TypedBytesTerminated(
    NameValuesSerializer, terminators=(b"\x00",), empty_is_none=True)


@se.subfield_serializer("ObjectUpdateCompressed", "ObjectData", "Data")
class ObjectUpdateCompressedDataSerializer(se.SimpleSubfieldSerializer):
    TEMPLATE = se.Template({
        "FullID": se.UUID,
        "ID": se.U32,
        "PCode": se.IntEnum(PCode, se.U8),
        # Meaning of State is PCode dependent. Could be a bitfield of flags + shifted attachment
        # point if an object with parents set to an avatar.
        "State": ObjectStateAdapter(se.U8),
        "CRC": se.U32,
        "Material": se.U8,
        "ClickAction": se.U8,
        "Scale": se.Vector3,
        "Position": se.Vector3,
        "Rotation": se.PackedQuat(se.Vector3),
        "Flags": UPDATE_COMPRESSED_FLAGS,
        # Only non-null if there's an attached sound
        "OwnerID": se.UUID,
        "AngularVelocity": CompressedOption(CompressedFlags.ANGULAR_VELOCITY, se.Vector3),
        # Note: missing section specifically means ParentID = 0
        "ParentID": CompressedOption(CompressedFlags.PARENT_ID, se.U32),
        # This field is strange. State == TreeSpecies in other ObjectUpdate types
        "TreeSpecies": CompressedOption(CompressedFlags.TREE, se.U8),
        # Technically only allowed if TREE not set, but I'm not convinced this is ever
        # used, or that any of the official unpackers would work correctly even if it was.
        "ScratchPad": CompressedOption(CompressedFlags.SCRATCHPAD, se.ByteArray(se.U32)),
        "Text": CompressedOption(CompressedFlags.TEXT, se.CStr()),
        "TextColor": CompressedOption(CompressedFlags.TEXT, Color4()),
        "MediaURL": CompressedOption(CompressedFlags.MEDIA_URL, se.CStr()),
        "PSBlock": CompressedOption(CompressedFlags.PARTICLES, se.TypedBytesFixed(86, PSBLOCK_TEMPLATE)),
        "ExtraParams": EXTRA_PARAM_COLLECTION,
        "Sound": CompressedOption(CompressedFlags.SOUND, se.UUID),
        "SoundGain": CompressedOption(CompressedFlags.SOUND, se.F32),
        "SoundFlags": CompressedOption(CompressedFlags.SOUND, se.U8),
        "SoundRadius": CompressedOption(CompressedFlags.SOUND, se.F32),
        "NameValue": CompressedOption(CompressedFlags.NAME_VALUES, NAMEVALUES_TERMINATED_TEMPLATE),
        # Intentionally not de-quantizing to preserve their real ranges.
        "PathCurve": se.U8,
        "ProfileCurve": se.U8,
        "PathBegin": se.U16,  # 0 to 1, quanta = 0.01
        "PathEnd": se.U16,  # 0 to 1, quanta = 0.01
        "PathScaleX": se.U8,  # 0 to 1, quanta = 0.01
        "PathScaleY": se.U8,  # 0 to 1, quanta = 0.01
        "PathShearX": se.U8,  # -.5 to .5, quanta = 0.01
        "PathShearY": se.U8,  # -.5 to .5, quanta = 0.01
        "PathTwist": se.S8,  # -1 to 1, quanta = 0.01
        "PathTwistBegin": se.S8,  # -1 to 1, quanta = 0.01
        "PathRadiusOffset": se.S8,  # -1 to 1, quanta = 0.01
        "PathTaperX": se.S8,  # -1 to 1, quanta = 0.01
        "PathTaperY": se.S8,  # -1 to 1, quanta = 0.01
        "PathRevolutions": se.U8,  # 0 to 3, quanta = 0.015
        "PathSkew": se.S8,  # -1 to 1, quanta = 0.01
        "ProfileBegin": se.U16,  # 0 to 1, quanta = 0.01
        "ProfileEnd": se.U16,  # 0 to 1, quanta = 0.01
        "ProfileHollow": se.U16,  # 0 to 1, quanta = 0.01
        "TextureEntry": DATA_PACKER_TE_TEMPLATE,
        "TextureAnim": CompressedOption(CompressedFlags.TEXTURE_ANIM, se.TypedByteArray(se.U32, TA_TEMPLATE)),
        "PSBlockNew": CompressedOption(CompressedFlags.PARTICLES_NEW, PSBLOCK_TEMPLATE),
    })


@se.flag_field_serializer("MultipleObjectUpdate", "ObjectData", "Type")
class MultipleObjectUpdateFlags(enum.IntFlag):
    POSITION = 0x01
    ROTATION = 0x02
    SCALE = 0x04
    LINKED_SETS = 0x08
    UNIFORM = 0x10


@se.subfield_serializer("MultipleObjectUpdate", "ObjectData", "Data")
class MultipleObjectUpdateDataSerializer(se.FlagSwitchedSubfieldSerializer):
    FLAG_FIELD = "Type"
    TEMPLATES = {
        MultipleObjectUpdateFlags.POSITION: se.Vector3,
        MultipleObjectUpdateFlags.ROTATION: se.PackedQuat(se.Vector3),
        MultipleObjectUpdateFlags.SCALE: se.Vector3,
    }


@se.flag_field_serializer("AgentUpdate", "AgentData", "ControlFlags")
@se.flag_field_serializer("ScriptControlChange", "Data", "Controls")
class AgentControlFlags(enum.IntFlag):
    AT_POS = 1
    AT_NEG = 1 << 1
    LEFT_POS = 1 << 2
    LEFT_NEG = 1 << 3
    UP_POS = 1 << 4
    UP_NEG = 1 << 5
    PITCH_POS = 1 << 6
    PITCH_NEG = 1 << 7
    YAW_POS = 1 << 8
    YAW_NEG = 1 << 9
    FAST_AT = 1 << 10
    FAST_LEFT = 1 << 11
    FAST_UP = 1 << 12
    FLY = 1 << 13
    STOP = 1 << 14
    FINISH_ANIM = 1 << 15
    STAND_UP = 1 << 16
    SIT_ON_GROUND = 1 << 17
    MOUSELOOK = 1 << 18
    NUDGE_AT_POS = 1 << 19
    NUDGE_AT_NEG = 1 << 20
    NUDGE_LEFT_POS = 1 << 21
    NUDGE_LEFT_NEG = 1 << 22
    NUDGE_UP_POS = 1 << 23
    NUDGE_UP_NEG = 1 << 24
    TURN_LEFT = 1 << 25
    TURN_RIGHT = 1 << 26
    AWAY = 1 << 27
    LBUTTON_DOWN = 1 << 28
    LBUTTON_UP = 1 << 29
    ML_LBUTTON_DOWN = 1 << 30
    ML_LBUTTON_UP = 1 << 31


@se.flag_field_serializer("AgentUpdate", "AgentData", "Flags")
class AgentUpdateFlags(enum.IntFlag):
    HIDE_TITLE = 1
    CLIENT_AUTOPILOT = 1 << 1


@se.enum_field_serializer("ChatFromViewer", "ChatData", "Type")
@se.enum_field_serializer("ChatFromSimulator", "ChatData", "ChatType")
class ChatType(enum.IntEnum):
    WHISPER = 0
    NORMAL = 1
    SHOUT = 2
    OOC = 3
    TYPING_START = 4
    TYPING_STOP = 5
    DEBUG_MSG = 6
    REGION = 7
    OWNER = 8
    DIRECT = 9
    IM = 10
    IM_GROUP = 11
    RADAR = 12


@se.enum_field_serializer("ChatFromSimulator", "ChatData", "SourceType")
class ChatSourceType(enum.IntEnum):
    SYSTEM = 0
    AGENT = 1
    OBJECT = 2
    UNKNOWN = 3


@se.subfield_serializer("AgentThrottle", "Throttle", "Throttles")
class AgentThrottlesSerializer(se.SimpleSubfieldSerializer):
    TEMPLATE = se.Collection(None, se.F32)


@se.subfield_serializer("ObjectUpdate", "ObjectData", "NameValue")
class NameValueSerializer(se.SimpleSubfieldSerializer):
    TEMPLATE = NAMEVALUES_TERMINATED_TEMPLATE


@se.enum_field_serializer("SetFollowCamProperties", "CameraProperty", "Type")
class CameraPropertyType(enum.IntEnum):
    PITCH = 0
    FOCUS_OFFSET = enum.auto()
    FOCUS_OFFSET_X = enum.auto()
    FOCUS_OFFSET_Y = enum.auto()
    FOCUS_OFFSET_Z = enum.auto()
    POSITION_LAG = enum.auto()
    FOCUS_LAG = enum.auto()
    DISTANCE = enum.auto()
    BEHINDNESS_ANGLE = enum.auto()
    BEHINDNESS_LAG = enum.auto()
    POSITION_THRESHOLD = enum.auto()
    FOCUS_THRESHOLD = enum.auto()
    ACTIVE = enum.auto()
    POSITION = enum.auto()
    POSITION_X = enum.auto()
    POSITION_Y = enum.auto()
    POSITION_Z = enum.auto()
    FOCUS = enum.auto()
    FOCUS_X = enum.auto()
    FOCUS_Y = enum.auto()
    FOCUS_Z = enum.auto()
    POSITION_LOCKED = enum.auto()
    FOCUS_LOCKED = enum.auto()


@se.enum_field_serializer("DeRezObject", "AgentBlock", "Destination")
class DeRezObjectDestination(enum.IntEnum):
    SAVE_INTO_AGENT_INVENTORY = 0  # deprecated, disabled
    ACQUIRE_TO_AGENT_INVENTORY = 1  # try to leave copy in world
    SAVE_INTO_TASK_INVENTORY = 2
    ATTACHMENT = 3  # deprecated
    TAKE_INTO_AGENT_INVENTORY = 4  # delete from world
    FORCE_TO_GOD_INVENTORY = 5  # force take copy
    TRASH = 6
    ATTACHMENT_TO_INV = 7  # deprecated
    ATTACHMENT_EXISTS = 8  # deprecated
    RETURN_TO_OWNER = 9  # back to owner's inventory
    RETURN_TO_LAST_OWNER = 10  # deeded object back to last owner's inventory, deprecated


@se.flag_field_serializer("RegionHandshake", "RegionInfo", "RegionFlags")
@se.flag_field_serializer("RegionHandshake", "RegionInfo4", "RegionFlagsExtended")
@se.flag_field_serializer("SimStats", "Region", "RegionFlags")
@se.flag_field_serializer("SimStats", "RegionInfo", "RegionFlagsExtended")
@se.flag_field_serializer("RegionInfo", "RegionInfo", "RegionFlags")
@se.flag_field_serializer("RegionInfo", "RegionInfo3", "RegionFlagsExtended")
class RegionFlags(enum.IntFlag):
    ALLOW_DAMAGE = 1 << 0
    ALLOW_LANDMARK = 1 << 1
    ALLOW_SET_HOME = 1 << 2
    # Do we reset the home position when someone teleports away from here?
    RESET_HOME_ON_TELEPORT = 1 << 3
    SUN_FIXED = 1 << 4  # Does the sun move?
    # Does the estate owner allow private parcels?
    ALLOW_ACCESS_OVERRIDE = 1 << 5
    BLOCK_TERRAFORM = 1 << 6
    BLOCK_LAND_RESELL = 1 << 7
    SANDBOX = 1 << 8  # All content wiped once per night
    ALLOW_ENVIRONMENT_OVERRIDE = 1 << 9
    SKIP_COLLISIONS = 1 << 12  # Pin all non agent rigid bodies
    SKIP_SCRIPTS = 1 << 13
    SKIP_PHYSICS = 1 << 14
    EXTERNALLY_VISIBLE = 1 << 15
    ALLOW_RETURN_ENCROACHING_OBJECT = 1 << 16
    ALLOW_RETURN_ENCROACHING_ESTATE_OBJECT = 1 << 17
    BLOCK_DWELL = 1 << 18
    BLOCK_FLY = 1 << 19
    ALLOW_DIRECT_TELEPORT = 1 << 20
    # Is there an administrative override on scripts in the region at the
    # moment. This is the similar skip scripts, except this flag is
    # presisted in the database on an estate level.
    ESTATE_SKIP_SCRIPTS = 1 << 21
    RESTRICT_PUSHOBJECT = 1 << 22
    DENY_ANONYMOUS = 1 << 23
    ALLOW_PARCEL_CHANGES = 1 << 26
    BLOCK_FLYOVER = 1 << 27
    ALLOW_VOICE = 1 << 28
    BLOCK_PARCEL_SEARCH = 1 << 29
    DENY_AGEUNVERIFIED = 1 << 30


@se.flag_field_serializer("RegionHandshakeReply", "RegionInfo", "Flags")
class RegionHandshakeReplyFlags(enum.IntFlag):
    VOCACHE_CULLING_ENABLED = 0x1  # ask sim to send all cacheable objects.
    VOCACHE_IS_EMPTY = 0x2  # the cache file is empty, no need to send cache probes.
    SUPPORTS_SELF_APPEARANCE = 0x4  # inbound AvatarAppearance for self is ok


@se.http_serializer("RenderMaterials")
class RenderMaterialsSerializer(se.BaseHTTPSerializer):
    @classmethod
    def deserialize_resp_body(cls, method: str, body: bytes):
        deser = llsd.unzip_llsd(llsd.parse_xml(body)["Zipped"])
        return deser

    @classmethod
    def deserialize_req_body(cls, method: str, body: bytes):
        if not body:
            return se.UNSERIALIZABLE
        deser = llsd.unzip_llsd(llsd.parse_xml(body)["Zipped"])
        return deser

    @classmethod
    def serialize_req_body(cls, method: str, body):
        if body == b"":
            return body

        return llsd.format_xml({"Zipped": llsd.zip_llsd(body)})


@se.http_serializer("RetrieveNavMeshSrc")
class RetrieveNavMeshSrcSerializer(se.BaseHTTPSerializer):
    @classmethod
    def deserialize_resp_body(cls, method: str, body: bytes):
        deser = llsd.parse_xml(body)
        # 15 bit window size, gzip wrapped
        deser["navmesh_data"] = zlib.decompress(deser["navmesh_data"], wbits=15 | 32)
        return deser


@dataclasses.dataclass
class CAPTemplate:
    cap_name: str
    method: str
    body: Any
    query: Set[str] = dataclasses.field(default_factory=set)
    path: str = ""


# Cap request templates for message builder prefills
CAP_TEMPLATES: List[CAPTemplate] = [
    CAPTemplate(cap_name='Seed', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<array>\n    <string></string>\n  </array>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='SimulatorFeatures', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='EventQueueGet', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>ack</key>\n    <undef />\n    <key>done</key>\n    <boolean></boolean>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='NavMeshGenerationStatus', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='AgentState', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='AgentPreferences', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>default_object_perm_masks</key>\n    <map>\n      <key>Everyone</key>\n      <integer></integer>\n      <key>Group</key>\n      <integer></integer>\n      <key>NextOwner</key>\n      <integer></integer>\n    </map>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='ExtEnvironment', method='GET', body=b'', query={'parcelid'}),
    CAPTemplate(cap_name='UpdateAgentLanguage', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>language</key>\n    <string>en</string>\n    <key>language_is_public</key>\n    <integer>1</integer>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='DirectDelivery', method='GET', body=b'', query=set(), path="/listings"),
    CAPTemplate(cap_name='ViewerStats', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>AgentPositionSnaps</key>\n    <real></real>\n    <key>DisplayNamesEnabled</key>\n    <integer></integer>\n    <key>DisplayNamesShowUsername</key>\n    <integer></integer>\n    <key>MinimalSkin</key>\n    <boolean></boolean>\n    <key>agent</key>\n    <map>\n      <key>agents_in_view</key>\n      <integer></integer>\n      <key>fps</key>\n      <real></real>\n      <key>language</key>\n      <string></string>\n      <key>mem_use</key>\n      <real></real>\n      <key>meters_traveled</key>\n      <real></real>\n      <key>ping</key>\n      <real></real>\n      <key>regions_visited</key>\n      <integer></integer>\n      <key>run_time</key>\n      <real></real>\n      <key>sim_fps</key>\n      <real></real>\n      <key>start_time</key>\n      <integer></integer>\n      <key>version</key>\n      <string></string>\n    </map>\n    <key>downloads</key>\n    <map>\n      <key>mesh_kbytes</key>\n      <real></real>\n      <key>object_kbytes</key>\n      <real></real>\n      <key>texture_kbytes</key>\n      <real></real>\n      <key>world_kbytes</key>\n      <real></real>\n    </map>\n    <key>misc</key>\n    <map>\n      <key>Version</key>\n      <integer></integer>\n      <key>Vertex Buffers Enabled</key>\n      <real></real>\n    </map>\n    <key>session_id</key>\n    <uuid></uuid>\n    <key>stats</key>\n    <map>\n      <key>failures</key>\n      <map>\n        <key>dropped</key>\n        <integer></integer>\n        <key>failed_resends</key>\n        <integer></integer>\n        <key>invalid</key>\n        <integer></integer>\n        <key>missing_updater</key>\n        <integer></integer>\n        <key>off_circuit</key>\n        <integer></integer>\n        <key>resent</key>\n        <integer></integer>\n        <key>send_packet</key>\n        <integer></integer>\n      </map>\n      <key>misc</key>\n      <map>\n        <key>int_1</key>\n        <integer></integer>\n        <key>int_2</key>\n        <integer></integer>\n        <key>string_1</key>\n        <string></string>\n        <key>string_2</key>\n        <string></string>\n      </map>\n      <key>net</key>\n      <map>\n        <key>in</key>\n        <map>\n          <key>compressed_packets</key>\n          <integer></integer>\n          <key>kbytes</key>\n          <real></real>\n          <key>packets</key>\n          <integer></integer>\n          <key>savings</key>\n          <real></real>\n        </map>\n        <key>out</key>\n        <map>\n          <key>compressed_packets</key>\n          <integer></integer>\n          <key>kbytes</key>\n          <real></real>\n          <key>packets</key>\n          <integer></integer>\n          <key>savings</key>\n          <real></real>\n        </map>\n      </map>\n      <key>voice</key>\n      <map>\n        <key>connect_attempts</key>\n        <integer></integer>\n        <key>connect_cycles</key>\n        <integer></integer>\n        <key>connect_time</key>\n        <real></real>\n        <key>establish_attempts</key>\n        <integer></integer>\n        <key>establish_time</key>\n        <real></real>\n        <key>provision_attempts</key>\n        <integer></integer>\n        <key>provision_time</key>\n        <real></real>\n      </map>\n    </map>\n    <key>system</key>\n    <map>\n      <key>address_size</key>\n      <integer></integer>\n      <key>cpu</key>\n      <string></string>\n      <key>gl</key>\n      <map>\n        <key>ati_offset_vertical_lines</key>\n        <integer></integer>\n        <key>ati_old_driver</key>\n        <integer></integer>\n        <key>debug_gpu</key>\n        <integer></integer>\n        <key>gl_renderer</key>\n        <string></string>\n        <key>gpu_vendor</key>\n        <string></string>\n        <key>gpu_version</key>\n        <string></string>\n        <key>has_anisotropic</key>\n        <integer></integer>\n        <key>has_arb_env_combine</key>\n        <integer></integer>\n        <key>has_ati_mem_info</key>\n        <integer></integer>\n        <key>has_blend_func_separate</key>\n        <integer></integer>\n        <key>has_compressed_textures</key>\n        <integer></integer>\n        <key>has_cube_map</key>\n        <integer></integer>\n        <key>has_debug_output</key>\n        <integer></integer>\n        <key>has_depth_clamp</key>\n        <integer></integer>\n        <key>has_draw_buffers</key>\n        <integer></integer>\n        <key>has_flush_buffer_range</key>\n        <integer></integer>\n        <key>has_fragment_shader</key>\n        <integer></integer>\n        <key>has_framebuffer_object</key>\n        <integer></integer>\n        <key>has_map_buffer_range</key>\n        <integer></integer>\n        <key>has_mip_map_generation</key>\n        <integer></integer>\n        <key>has_multitexture</key>\n        <integer></integer>\n        <key>has_nvx_mem_info</key>\n        <integer></integer>\n        <key>has_occlusion_query</key>\n        <integer></integer>\n        <key>has_occlusion_query2</key>\n        <integer></integer>\n        <key>has_pbuffer</key>\n        <integer></integer>\n        <key>has_point_parameters</key>\n        <integer></integer>\n        <key>has_requirements</key>\n        <integer></integer>\n        <key>has_separate_specular_color</key>\n        <integer></integer>\n        <key>has_shader_objects</key>\n        <integer></integer>\n        <key>has_srgb_framebuffer</key>\n        <integer></integer>\n        <key>has_srgb_texture</key>\n        <integer></integer>\n        <key>has_sync</key>\n        <integer></integer>\n        <key>has_texture_multisample</key>\n        <integer></integer>\n        <key>has_texture_rectangle</key>\n        <integer></integer>\n        <key>has_texture_srgb_decode</key>\n        <integer></integer>\n        <key>has_timer_query</key>\n        <integer></integer>\n        <key>has_transform_feedback</key>\n        <integer></integer>\n        <key>has_vertex_array_object</key>\n        <integer></integer>\n        <key>has_vertex_buffer_object</key>\n        <integer></integer>\n        <key>has_vertex_shader</key>\n        <integer></integer>\n        <key>is_ati</key>\n        <integer></integer>\n        <key>is_gf2or4mx</key>\n        <integer></integer>\n        <key>is_gf3</key>\n        <integer></integer>\n        <key>is_gf_gfx</key>\n        <integer></integer>\n        <key>is_intel</key>\n        <integer></integer>\n        <key>is_nvidia</key>\n        <integer></integer>\n        <key>max_color_texture_samples</key>\n        <integer></integer>\n        <key>max_depth_texture_samples</key>\n        <integer></integer>\n        <key>max_index_range</key>\n        <integer></integer>\n        <key>max_integer_samples</key>\n        <integer></integer>\n        <key>max_sample_mask_words</key>\n        <integer></integer>\n        <key>max_samples</key>\n        <integer></integer>\n        <key>max_texture_size</key>\n        <integer></integer>\n        <key>max_vertex_range</key>\n        <integer></integer>\n        <key>num_texture_image_units</key>\n        <integer></integer>\n        <key>num_texture_units</key>\n        <integer></integer>\n        <key>opengl_version</key>\n        <string></string>\n        <key>vram</key>\n        <integer></integer>\n      </map>\n      <key>gpu</key>\n      <string></string>\n      <key>gpu_class</key>\n      <integer></integer>\n      <key>gpu_vendor</key>\n      <string></string>\n      <key>gpu_version</key>\n      <string></string>\n      <key>mac_address</key>\n      <string></string>\n      <key>opengl_version</key>\n      <string></string>\n      <key>os</key>\n      <string></string>\n      <key>ram</key>\n      <integer></integer>\n      <key>serial_number</key>\n      <string></string>\n      <key>shader_level</key>\n      <integer></integer>\n    </map>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='GetDisplayNames', method='GET', body=b'', query={'ids'}),
    CAPTemplate(cap_name='FetchInventory2', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>agent_id</key>\n    <uuid><!HIPPOREPL[[AGENT_ID]]></uuid>\n    <key>cap_name</key>\n    <string></string>\n    <key>items</key>\n    <array>\n      <map>\n        <key>item_id</key>\n        <uuid></uuid>\n        <key>owner_id</key>\n        <uuid><!HIPPOREPL[[AGENT_ID]]></uuid>\n      </map>\n    </array>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='FetchLib2', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>agent_id</key>\n    <uuid></uuid>\n    <key>cap_name</key>\n    <string></string>\n    <key>items</key>\n    <array>\n      <map>\n        <key>item_id</key>\n        <uuid></uuid>\n        <key>owner_id</key>\n        <uuid></uuid>\n      </map>\n    </array>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='FetchInventoryDescendents2', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>folders</key>\n    <array>\n      <map>\n        <key>fetch_folders</key>\n        <boolean></boolean>\n        <key>fetch_items</key>\n        <boolean></boolean>\n        <key>folder_id</key>\n        <string></string>\n        <key>owner_id</key>\n        <uuid><!HIPPOREPL[[AGENT_ID]]></uuid>\n        <key>sort_order</key>\n        <integer></integer>\n      </map>\n    </array>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='ProvisionVoiceAccountRequest', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<undef />\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='AvatarRenderInfo', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='ReadOfflineMsgs', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='MapImageService', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='RenderMaterials', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='AvatarRenderInfo', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>agents</key>\n    <map>\n      <key><!HIPPOREPL[[AGENT_ID]]></key>\n      <map>\n        <key>tooComplex</key>\n        <boolean></boolean>\n        <key>weight</key>\n        <integer></integer>\n      </map>\n    </map>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='ParcelVoiceInfoRequest', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<undef />\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='ProductInfoRequest', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='ObjectMedia', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>object_id</key>\n    <uuid><!HIPPOREPL[[SELECTED_FULL]]></uuid>\n    <key>verb</key>\n    <string>GET</string>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='GetObjectCost', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>object_ids</key>\n    <array>\n      <uuid><!HIPPOREPL[[SELECTED_FULL]]></uuid>\n    </array>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='GetObjectPhysicsData', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>object_ids</key>\n    <array>\n      <uuid><!HIPPOREPL[[SELECTED_FULL]]></uuid>\n    </array>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='RenderMaterials', method='PUT', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>Zipped</key>\n    <binary></binary>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='RenderMaterials', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>Zipped</key>\n    <binary></binary>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='GetExperienceInfo', method='GET', body=b'', query={'public_id', 'page_size'}, path="/id/"),
    CAPTemplate(cap_name='LSLSyntax', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='GetCreatorExperiences', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='GetMetadata', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>fields</key>\n    <array>\n      <string>experience</string>\n    </array>\n    <key>item-id</key>\n    <uuid><!HIPPOREPL[[SELECTED_SCRIPT_ITEM]]></uuid>\n    <key>object-id</key>\n    <uuid><!HIPPOREPL[[SELECTED_FULL]]></uuid>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='UpdateScriptTask', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>experience</key>\n    <uuid></uuid>\n    <key>is_script_running</key>\n    <integer>1</integer>\n    <key>item_id</key>\n    <uuid><!HIPPOREPL[[SELECTED_SCRIPT_ITEM]]></uuid>\n    <key>target</key>\n    <string>mono</string>\n    <key>task_id</key>\n    <uuid><!HIPPOREPL[[SELECTED_FULL]]></uuid>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='EstateAccess', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='RegionExperiences', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='SimConsoleAsync', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<string></string>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='FindExperienceByName', method='GET', body=b'', query={'query', 'page', 'page_size'}),
    CAPTemplate(cap_name='ViewerMetrics', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>agent_id</key>\n    <uuid></uuid>\n    <key>break</key>\n    <boolean></boolean>\n    <key>duration</key>\n    <real></real>\n    <key>initial</key>\n    <boolean></boolean>\n    <key>message</key>\n    <string></string>\n    <key>nearby</key>\n    <map>\n      <key>cloud</key>\n      <integer></integer>\n      <key>downloading</key>\n      <integer></integer>\n      <key>full</key>\n      <integer></integer>\n      <key>gray</key>\n      <integer></integer>\n    </map>\n    <key>rez_status</key>\n    <string></string>\n    <key>sequence</key>\n    <integer></integer>\n    <key>session_id</key>\n    <uuid></uuid>\n    <key>timers</key>\n    <array>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n      <map>\n        <key>central_bake_version</key>\n        <integer></integer>\n        <key>completed</key>\n        <boolean></boolean>\n        <key>grid_x</key>\n        <integer></integer>\n        <key>grid_y</key>\n        <integer></integer>\n        <key>is_self</key>\n        <boolean></boolean>\n        <key>is_using_server_bakes</key>\n        <boolean></boolean>\n        <key>stats</key>\n        <map>\n          <key>count</key>\n          <integer></integer>\n          <key>max</key>\n          <real></real>\n          <key>mean</key>\n          <real></real>\n          <key>min</key>\n          <real></real>\n          <key>std_dev</key>\n          <real></real>\n        </map>\n        <key>timer_name</key>\n        <string></string>\n      </map>\n    </array>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='InventoryAPIv3', method='PATCH', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>name</key>\n    <string></string>\n  </map>\n</llsd>\n', query={'tid'}, path="/item/SOME_ID"),
    CAPTemplate(cap_name='RemoteParcelRequest', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>location</key>\n    <array>\n      <real></real>\n      <real></real>\n      <real></real>\n    </array>\n    <key>region_handle</key>\n    <binary></binary>\n    <key>region_id</key>\n    <uuid></uuid>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='ParcelPropertiesUpdate', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n  <map>\n   <key>local_id</key>\n    <integer><!HIPPOREPL[[SELECTED_PARCEL_LOCAL]]></integer>\n   <key>any_av_sounds</key>\n    <boolean>true</boolean>\n   <key>auth_buyer_id</key>\n    <uuid></uuid>\n   <key>auto_scale</key>\n    <integer>0</integer>\n   <key>category</key>\n    <integer>0</integer>\n   <key>description</key>\n    <string></string>\n   <key>flags</key>\n    <binary>AAAAAQ==</binary>\n   <key>group_av_sounds</key>\n    <boolean>true</boolean>\n   <key>group_id</key>\n    <uuid></uuid>\n   <key>landing_type</key>\n    <integer>2</integer>\n   <key>media_allow_navigate</key>\n    <integer>1</integer>\n   <key>media_current_url</key>\n    <string></string>\n   <key>media_desc</key>\n    <string></string>\n   <key>media_height</key>\n    <integer>0</integer>\n   <key>media_id</key>\n    <uuid></uuid>\n   <key>media_loop</key>\n    <integer>0</integer>\n   <key>media_prevent_camera_zoom</key>\n    <integer>0</integer>\n   <key>media_type</key>\n    <string>none/none</string>\n   <key>media_url</key>\n    <string></string>\n   <key>media_url_timeout</key>\n    <real>0.0</real>\n   <key>media_width</key>\n    <integer>0</integer>\n   <key>music_url</key>\n    <string></string>\n   <key>name</key>\n    <string></string>\n   <key>obscure_media</key>\n    <boolean>false</boolean>\n   <key>obscure_music</key>\n    <boolean>false</boolean>\n   <key>parcel_flags</key>\n    <binary>fiQASw==</binary>\n   <key>pass_hours</key>\n    <real>1.0</real>\n   <key>pass_price</key>\n    <integer>10</integer>\n   <key>sale_price</key>\n    <integer>10000</integer>\n   <key>see_avs</key>\n    <boolean>true</boolean>\n   <key>snapshot_id</key>\n    <uuid></uuid>\n   <key>user_location</key>\n    <array>\n      <real>0.0</real>\n      <real>0.0</real>\n      <real>0.0</real>\n    </array>\n   <key>user_look_at</key>\n    <array>\n      <real>0.0</real>\n      <real>0.0</real>\n      <real>0.0</real>\n    </array>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='UpdateScriptAgent', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>item_id</key>\n    <uuid></uuid>\n    <key>target</key>\n    <string>mono</string>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='NewFileAgentInventory', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>asset_type</key>\n    <string></string>\n    <key>description</key>\n    <string></string>\n    <key>everyone_mask</key>\n    <integer></integer>\n    <key>folder_id</key>\n    <uuid></uuid>\n    <key>group_mask</key>\n    <integer></integer>\n    <key>inventory_type</key>\n    <string></string>\n    <key>name</key>\n    <string></string>\n    <key>next_owner_mask</key>\n    <integer></integer>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='UpdateNotecardAgentInventory', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>item_id</key>\n    <uuid></uuid>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='UpdateNotecardTaskInventory', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>item_id</key>\n    <uuid><!HIPPOREPL[[SELECTED_TASK_ITEM]]></uuid>\n    <key>task_id</key>\n    <uuid><!HIPPOREPL[[SELECTED_FULL]]></uuid>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='UpdateGestureAgentInventory', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>item_id</key>\n    <uuid></uuid>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='UpdateGestureTaskInventory', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>item_id</key>\n    <uuid><!HIPPOREPL[[SELECTED_TASK_ITEM]]></uuid>\n    <key>task_id</key>\n    <uuid><!HIPPOREPL[[SELECTED_FULL]]></uuid>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='MeshUploadFlag', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='UntrustedSimulatorMessage', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n   <key>message</key>\n    <string>ChatFromViewer</string>\n   <key>body</key>\n    <map>\n     <key>AgentData</key>\n      <array>\n        <map>\n         <key>AgentID</key>\n          <uuid><!HIPPOREPL[[AGENT_ID]]></uuid>\n         <key>SessionID</key>\n          <uuid><!HIPPOREPL[[SESSION_ID]]></uuid>\n        </map>\n      </array>\n     <key>ChatData</key>\n      <array>\n        <map>\n         <key>Channel</key>\n          <integer>0</integer>\n         <key>Message</key>\n          <string>test <!HIPPOEVAL[[\n            1 + 1\n          ]]></string>\n         <key>Type</key>\n          <integer>1</integer>\n        </map>\n      </array>\n    </map>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='UpdateAvatarAppearance', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>cof_version</key>\n    <integer></integer>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='ServerReleaseNotes', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='UserInfo', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='SendPostcard', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>msg</key>\n    <string></string>\n    <key>name</key>\n    <string></string>\n    <key>pos-global</key>\n    <array>\n      <real></real>\n      <real></real>\n      <real></real>\n    </array>\n    <key>subject</key>\n    <string></string>\n    <key>to</key>\n    <string></string>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='GetAdminExperiences', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='GetExperiences', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='AgentExperiences', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='ExperiencePreferences', method='GET', body=b'', query={'SOME_ID'}),
    CAPTemplate(cap_name='IsExperienceAdmin', method='GET', body=b'', query={'experience_id'}),
    CAPTemplate(cap_name='UpdateExperience', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>description</key>\n    <string></string>\n    <key>extended_metadata</key>\n    <string></string>\n    <key>group_id</key>\n    <uuid></uuid>\n    <key>slurl</key>\n    <string></string>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='AttachmentResources', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='DispatchRegionInfo', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>agent_limit</key>\n    <real></real>\n    <key>allow_damage</key>\n    <integer></integer>\n    <key>allow_land_resell</key>\n    <integer></integer>\n    <key>allow_parcel_changes</key>\n    <integer></integer>\n    <key>block_fly</key>\n    <integer></integer>\n    <key>block_fly_over</key>\n    <integer></integer>\n    <key>block_parcel_search</key>\n    <integer></integer>\n    <key>block_terraform</key>\n    <integer></integer>\n    <key>prim_bonus</key>\n    <real></real>\n    <key>restrict_pushobject</key>\n    <integer></integer>\n    <key>sim_access</key>\n    <string></string>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='AvatarPickerSearch', method='GET', body=b'', query={'names', 'page_size'}),
    CAPTemplate(cap_name='LandResources', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>parcel_id</key>\n    <uuid><!HIPPOREPL[[SELECTED_PARCEL_FULL]]></uuid>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='ResourceCostSelected', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>selected_roots</key>\n    <array>\n      <uuid><!HIPPOREPL[[SELECTED_FULL]]></uuid>\n    </array>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='GroupMemberData', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>group_id</key>\n    <uuid />\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='GroupExperiences', method='GET', body=b'', query={'SOME_ID'}),
    CAPTemplate(cap_name='CopyInventoryFromNotecard', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>callback-id</key>\n    <integer></integer>\n    <key>folder-id</key>\n    <uuid></uuid>\n    <key>item-id</key>\n    <uuid></uuid>\n    <key>notecard-id</key>\n    <uuid></uuid>\n    <key>object-id</key>\n    <uuid />\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='HomeLocation', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>HomeLocation</key>\n    <map>\n      <key>LocationId</key>\n      <integer>1</integer>\n      <key>LocationLookAt</key>\n      <map>\n        <key>X</key>\n        <real></real>\n        <key>Y</key>\n        <real></real>\n        <key>Z</key>\n        <real></real>\n      </map>\n      <key>LocationPos</key>\n      <map>\n        <key>X</key>\n        <real></real>\n        <key>Y</key>\n        <real></real>\n        <key>Z</key>\n        <real></real>\n      </map>\n    </map>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='CharacterProperties', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='ObjectNavMeshProperties', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='TerrainNavMeshProperties', method='GET', body=b'', query=set()),
    CAPTemplate(cap_name='ObjectNavMeshProperties', method='PUT', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key><!HIPPOREPL[[SELECTED_FULL]]></key>\n    <map>\n      <key>A</key>\n      <integer></integer>\n      <key>B</key>\n      <integer></integer>\n      <key>C</key>\n      <integer></integer>\n      <key>D</key>\n      <integer></integer>\n      <key>navmesh_category</key>\n      <integer></integer>\n      <key>phantom</key>\n      <boolean></boolean>\n    </map>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='RetrieveNavMeshSrc', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<undef />\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='MapLayer', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<undef />\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='GroupAPIv1', method='GET', body=b'', query={'group_id'}),
    CAPTemplate(cap_name='ChatSessionRequest', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>method</key>\n    <string></string>\n    <key>session-id</key>\n    <uuid></uuid>\n  </map>\n</llsd>\n', query=set()),
    CAPTemplate(cap_name='ViewerBenefits', method='GET', body=b'', query=set(), path=''),
    CAPTemplate(cap_name='SetDisplayName', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>display_name</key>\n    <array>\n      <string>OLD_DISPLAY_NAME</string>\n      <string>NEW_DISPLAY_NAME</string>\n    </array>\n  </map>\n</llsd>\n', query=set(), path=''),
    CAPTemplate(cap_name='ObjectMediaNavigate', method='POST', body=b'<?xml version="1.0" ?>\n<llsd>\n<map>\n    <key>current_url</key>\n    <string></string>\n    <key>object_id</key>\n    <uuid><!HIPPOREPL[[SELECTED_FULL]]></uuid>\n    <key>texture_index</key>\n    <integer></integer>\n  </map>\n</llsd>\n', query=set(), path=''),
]
