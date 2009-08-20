
"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""

class ImprovedIMDialogue(object):
    """ mappings for the values sent in an ImprovedInstantMessage packet """

    FromAgent = 0                               # an instant message from another agent
    MessageBox = 1                              # a dialogue box
    GroupInvitation = 3                         # group invite. binary bucket contains null terminated string of member status and join cost. 0 for officer M for member. n bytes for cost
    InventoryOffered = 4                        # inventory offer from another agent. binary bucket is a list of inventory uuid and type
    InventoryAccepted = 5                       # inventory offer accepted
    InventoryDeclined = 6                       # inventory offer declined
    GroupVote = 7                               # group vote. name is person who initiated the vote id is vote id
    #GroupMessageDeprecated = 8
    TaskInventoryOffered = 9                    # inventory offer from an object
    TaskInventoryAccepted = 10                  # inventory offer from object accepted
    TaskInventoryDeclined = 11                  # inventory offer from object declined
    NewUserDefault = 12
    SessionInvite = 13                          # start a friends conference
    SessionP2PInvite = 14                       # start a conference without removing offline users
    SessionGroupStart = 15                      # start a friends conference
    SessionConferenceStart = 16                 # start a conference w/o calling cards etc
    SessionSend = 17                            # message to a session
    SessionLeave = 18                           # leave a chat session
    MessageFromTask = 19                        # message from an object
    BusyAutoResponse = 20                       # response to an instant message by an agent who is set to busy
    ConsoleAndChatHistory = 21                  # show the message and chat history
    TeleportLure = 22                           # send a teleport request
    TeleportAccepted = 23                       # agent has accepted a teleport request
    TeleportDeclined = 24                       # agent has declined a teleport request
    GodTeleportLure = 25                        # send a god like teleport request
    Unused = 26
    GotoURL = 28                                # tells the user to go to a url. Text message in the message field url with a trailing \0 in the binary bucket
    FromTaskAsAlert = 31                        # alert sent from an object (not to be sent through email)
    GroupNotice = 32                            # im from user sending a group notice
    GroupNoticeInventoryAccepted = 33
    GroupNoticeInventoryDeclined = 34
    GroupInvitationAccept = 35
    GroupInvitationDecline = 36
    GroupNoticeRequested = 37                   
    FriendshipOffered = 38                      # sender has offered friendship
    FriendshipAccepted = 39                     # sender has accepted friendship offer
    FriendshipDeclined = 40                     # sender has declined friendship offer
    TypingStart = 41                            # sender has started typing
    TypingStop = 42                             # sender has stopped typing

class InventoryType(object):
    """ mappings for inventory asset type """

    Texture = 0
    Sound = 1
    Callingcard = 2
    Landmark = 3
    # Script = 4
    # Clothing = 5
    Object = 6
    Notecard = 7
    Category = 8
    Root_Category = 9
    LSL = 10
    # LSL_Bytecode = 11
    # Texture_Tga = 12
    # Bodypart = 13
    # Trash = 14
    Snapshot = 15
    # Lost_and_found = 16
    Attachment = 17
    Wearable = 18
    Animation = 19
    Gesture = 20
    Count = 21
    NONE = -1

class PCodeEnum(object):
    """ classifying the PCode of objects """

    Primitive = 9          # 0x09
    Avatar = 47            # 0x2F
    Grass = 95             # 0x5F
    NewTree = 111          # 0x6F
    ParticleSystem = 143   # 0x8F
    Tree = 255             # 0xFF

class CompressedUpdateFlags(object):
    """ map of ObjectData.Flags """

    ScratchPad = 0x01
    Tree = 0x02
    contains_Text = 0x04
    contains_Particles = 0x08
    contains_Sound = 0x10
    contains_Parent = 0x20
    TextureAnim = 0x40
    contains_AngularVelocity = 0x80
    contains_NameValues = 0x100
    MediaURL = 0x200

class ExtraParam(object):
    """ extended Object attributes buried in some packets """

    Flexible = 0x10
    Light = 0x20
    Sculpt = 0x30

class ParcelFlags(object):
    """ Parcel Flag constants """

    AllowFly = 1 << 0                   # Can start flying
    AllowOtherScripts = 1 << 1          # Scripts by others can run.
    ForSale = 1 << 2                    # Can buy this land
    ForSaleObjects = 1 << 7             # Can buy all objects on this land
    AllowLandmarks = 1 << 3
    AllowTerraform = 1 << 4
    AllowDamage = 1 << 5
    CreateObjects = 1 << 6
    UseAccessGroup = 1 << 8
    UseAccessList = 1 << 9
    UseBanList = 1 << 10
    UsePassList = 1 << 11
    ShowDirectory = 1 << 12
    AllowDeedToGroup = 1 << 13
    ContributeWithDeed = 1 << 14
    SoundLocal = 1 << 15                # Hear sounds in this parcel only
    SellParcelObjects = 1 << 16         # Objects on land are included as part of the land when the land is sold
    AllowPublish = 1 << 17              # Allow publishing of parcel information on the web
    MaturePublish = 1 << 18             # The information on this parcel is mature
    URLWebPage = 1 << 19                # The "media URL" is an HTML page
    URLRawHTML = 1 << 20                # The "media URL" is a raw HTML string like <H1>Foo</H1>
    ResrictPushObject = 1 << 21         # Restrict push object to either on agent or on scripts owned by parcel owner
    DenyAnonomous = 1 << 22             # Deny all non identified/transacted accounts
    # DenyIdentified = 1 << 23          # Deny identified accounts
    # DenyTransacted = 1 << 24          # Deny identified accounts
    AllowGroupScripts = 1 << 25         # Allow scripts owned by group
    CreateGroupObjects = 1 << 26        # Allow object creation by group members or objects
    AllowAllObjectEntry = 1 << 27       # Allow all objects to enter a parcel
    AllowGroupObjectEntry = 1 << 28     # Only allow group (and owner) objects to enter the parcel
    AllowVoiceChat = 1 << 29            # Allow residents to use voice chat on this parcel
    UseEstateVoiceChannel = 1 << 30
    DenyAgeUnverified = 1 << 31         # Prevent residents who aren't age-verified 


class MoneyTransactionType(object):
    """ Money transaction type constants """

    Null                   = 0
    
# Codes 1000-1999 reserved for one-time charges
    ObjectClaim            = 1000
    LandClaim              = 1001
    GroupCreate            = 1002
    ObjectPublicClaim      = 1003
    GroupJoin              = 1004 # May be moved to group transactions eventually
    TeleportCharge         = 1100 # FF not sure why this jumps to 1100... 
    UploadCharge           = 1101
    LandAuction            = 1102
    ClassifiedCharge       = 1103

# Codes 2000-2999 reserved for recurrent charges
    ObjectTax              = 2000
    LandTax                = 2001
    LightTax               = 2002
    ParcelDirFee           = 2003
    GroupTax               = 2004 # Taxes incurred as part of group membership
    ClassifiedRenew        = 2005

# Codes 3000-3999 reserved for inventory transactions
    GiveInventory          = 3000

# Codes 5000-5999 reserved for transfers between users
    ObjectSale             = 5000
    Gift                   = 5001
    LandSale               = 5002
    ReferBonus             = 5003
    InventorySale          = 5004
    RefundPurchase         = 5005
    LandPassSale           = 5006
    DwellBonus             = 5007
    PayObject              = 5008
    ObjectPays             = 5009

# Codes 6000-6999 reserved for group transactions
#   GroupJoin              = 6000  # reserved for future use
    GroupLandDeed          = 6001
    GroupObjectDeed        = 6002
    GroupLiability         = 6003
    GroupDividend          = 6004
    MembershipDues         = 6005

# Codes 8000-8999 reserved for one-type credits
    ObjectRelease          = 8000
    LandRelease            = 8001
    ObjectDelete           = 8002
    ObjectPublicDecay      = 8003
    ObjectPublicDelete     = 8004

# Code 9000-9099 reserved for usertool transactions
    LindenAdjustment       = 9000
    LindenGrant            = 9001
    LindenPenalty          = 9002
    EventFee               = 9003
    EventPrize             = 9004

# Codes 10000-10999 reserved for stipend credits
    StipendBasic           = 10000
    StipendDeveloper       = 10001
    StipendAlways          = 10002
    StipendDaily           = 10003
    StipendRating          = 10004
    StipendDelta           = 10005

class TransactionFlags(object):
    Null = 0
    SourceGroup = 1
    DestGroup = 2
    OwnerGroup = 4
    SimultaneousContribution = 8
    SimultaneousContributionRemoval = 16


class AgentState(object):
    Null      = 0x00 # None
    Typing    = 0x04 # Typing indication
    Editing   = 0x10 # Set when agent has objects selected


class AgentUpdateFlags(object):
    Null      = 0x00  # None
    HideTitle = 0x01


class AgentControlFlags(object):
    """ Used for the ControlFlags member of AgentUpdate packets """
    _ControlAtPosIndex               =  0
    _ControlAtNegIndex               =  1
    _ControlLeftPosIndex             =  2
    _ControlLeftNegIndex             =  3
    _ControlUpPosIndex               =  4
    _ControlUpNegIndex               =  5
    _ControlPitchPosIndex            =  6
    _ControlPitchNegIndex            =  7
    _ControlYawPosIndex              =  8
    _ControlYawNegIndex              =  9
    _ControlFastAtIndex              = 10
    _ControlFastLeftIndex            = 11
    _ControlFastUpIndex              = 12
    _ControlFlyIndex                 = 13
    _ControlStopIndex                = 14
    _ControlFinishAnimIndex          = 15
    _ControlStandUpIndex             = 16
    _ControlSitOnGroundIndex         = 17
    _ControlMouselookIndex           = 18
    _ControlNudgeAtPosIndex          = 19
    _ControlNudgeAtNegIndex          = 20
    _ControlNudgeLeftPosIndex        = 21
    _ControlNudgeLeftNegIndex        = 22
    _ControlNudgeUpPosIndex          = 23
    _ControlNudgeUpNegIndex          = 24
    _ControlTurnLeftIndex            = 25
    _ControlTurnRightIndex           = 26
    _ControlAwayIndex                = 27
    _ControlLbuttonDownIndex         = 28
    _ControlLbuttonUpIndex           = 29
    _ControlMlLbuttonDownIndex       = 30
    _ControlMlLbuttonUpIndex         = 31
    _TotalControls                   = 32
    
    AtPos                 = 0x1 << _ControlAtPosIndex            # 0x00000001
    AtNeg                 = 0x1 << _ControlAtNegIndex            # 0x00000002
    LeftPos               = 0x1 << _ControlLeftPosIndex          # 0x00000004
    LeftNeg               = 0x1 << _ControlLeftNegIndex          # 0x00000008
    UpPos                 = 0x1 << _ControlUpPosIndex            # 0x00000010
    UpNeg                 = 0x1 << _ControlUpNegIndex            # 0x00000020
    PitchPos              = 0x1 << _ControlPitchPosIndex         # 0x00000040
    PitchNeg              = 0x1 << _ControlPitchNegIndex         # 0x00000080
    YawPos                = 0x1 << _ControlYawPosIndex           # 0x00000100
    YawNeg                = 0x1 << _ControlYawNegIndex           # 0x00000200
    
    FastAt                = 0x1 << _ControlFastAtIndex           # 0x00000400
    FastLeft              = 0x1 << _ControlFastLeftIndex         # 0x00000800
    FastUp                = 0x1 << _ControlFastUpIndex           # 0x00001000
    
    Fly                   = 0x1 << _ControlFlyIndex              # 0x00002000
    Stop                  = 0x1 << _ControlStopIndex             # 0x00004000
    FinishAnim            = 0x1 << _ControlFinishAnimIndex       # 0x00008000
    StandUp               = 0x1 << _ControlStandUpIndex          # 0x00010000
    SitOnGround           = 0x1 << _ControlSitOnGroundIndex      # 0x00020000
    Mouselook             = 0x1 << _ControlMouselookIndex        # 0x00040000
    
    NudgeAtPos            = 0x1 << _ControlNudgeAtPosIndex       # 0x00080000
    NudgeAtNeg            = 0x1 << _ControlNudgeAtNegIndex       # 0x00100000
    NudgeLeftPos          = 0x1 << _ControlNudgeLeftPosIndex     # 0x00200000
    NudgeLeftNeg          = 0x1 << _ControlNudgeLeftNegIndex     # 0x00400000
    NudgeUpPos            = 0x1 << _ControlNudgeUpPosIndex       # 0x00800000
    NudgeUpNeg            = 0x1 << _ControlNudgeUpNegIndex       # 0x01000000
    TurnLeft              = 0x1 << _ControlTurnLeftIndex         # 0x02000000
    TurnRight             = 0x1 << _ControlTurnRightIndex        # 0x04000000
    
    Away                  = 0x1 << _ControlAwayIndex             # 0x08000000
    
    LbuttonDown           = 0x1 << _ControlLbuttonDownIndex      # 0x10000000
    LbuttonUp             = 0x1 << _ControlLbuttonUpIndex        # 0x20000000
    MlLbuttonDown         = 0x1 << _ControlMlLbuttonDownIndex    # 0x40000000
    MlLbuttonUp           = 0x1 << _ControlMlLbuttonUpIndex      # 0x80000000
    
    At                    = AtPos | AtNeg | NudgeAtPos | NudgeAtNeg    
    Left                  = LeftPos | LeftNeg | NudgeLeftPos | NudgeLeftNeg    
    Up                    = UpPos | UpNeg | NudgeUpPos | NudgeUpNeg    
    Horizontal            = At | Left  
    NotUsedByLsl          = Fly | Stop | FinishAnim | StandUp | SitOnGround | Mouselook | Away  
    Movement              = At | Left | Up  
    Rotation              = PitchPos | PitchNeg | YawPos | YawNeg   
    Nudge                 = NudgeAtPos | NudgeAtNeg | NudgeLeftPos | NudgeLeftNeg    

class TextureIndex(object):
    TEX_HEAD_BODYPAINT   = 0
    TEX_UPPER_SHIRT      = 1
    TEX_LOWER_PANTS      = 2
    TEX_EYES_IRIS        = 3
    TEX_HAIR             = 4
    TEX_UPPER_BODYPAINT  = 5
    TEX_LOWER_BODYPAINT  = 6
    TEX_LOWER_SHOES      = 7
    TEX_HEAD_BAKED       = 8           # Pre-composited
    TEX_UPPER_BAKED      = 9 # Pre-composited
    TEX_LOWER_BAKED      = 10       # Pre-composited
    TEX_EYES_BAKED       = 11       # Pre-composited
    TEX_LOWER_SOCKS      = 12
    TEX_UPPER_JACKET     = 13
    TEX_LOWER_JACKET     = 14
    TEX_UPPER_GLOVES     = 15
    TEX_UPPER_UNDERSHIRT = 16
    TEX_LOWER_UNDERPANTS = 17
    TEX_SKIRT            = 18
    TEX_SKIRT_BAKED      = 19        # Pre-composited
    TEX_HAIR_BAKED       = 20   # Pre-composited
    TEX_COUNT            = 21

class BakedIndex(object):
    BAKED_HEAD = 0
    BAKED_UPPER = 1
    BAKED_LOWER = 2
    BAKED_EYES = 3
    BAKED_SKIRT = 4
    BAKED_HAIR = 5
    BAKED_COUNT = 6

    def BakedToTextureIndex(self, bakedIndex):
        if bakedIndex is self.BAKED_HEAD:
            return TextureIndex.TEX_HEAD_BAKED
        elif bakedIndex is self.BAKED_UPPER:
            return TextureIndex.TEX_UPPER_BAKED
        elif bakedIndex is self.BAKED_LOWER:
            return TextureIndex.TEX_LOWER_BAKED
        elif bakedIndex is self.BAKED_EYES:
            return TextureIndex.TEX_EYES_BAKED
        elif bakedIndex is self.BAKED_SKIRT:
            return TextureIndex.TEX_SKIRT_BAKED
        elif bakedIndex is self.BAKED_HAIR:
            return TextureIndex.TEX_HAIR_BAKED
        else:
            return -1
        

class WearablesIndex(object):
    WT_SHAPE      = 0
    WT_SKIN       = 1
    WT_HAIR       = 2
    WT_EYES       = 3
    WT_SHIRT      = 4
    WT_PANTS      = 5
    WT_SHOES      = 6
    WT_SOCKS      = 7
    WT_JACKET     = 8
    WT_GLOVES     = 9
    WT_UNDERSHIRT = 10
    WT_UNDERPANTS = 11
    WT_SKIRT      = 12
    
class WearableMap(object):
    def __init__(self):
        self.map = {}
       
        self.map[BakedIndex.BAKED_HEAD] = [WearablesIndex.WT_SHAPE, WearablesIndex.WT_SKIN, WearablesIndex.WT_HAIR]
        self.map[BakedIndex.BAKED_UPPER] = [WearablesIndex.WT_SHAPE, WearablesIndex.WT_SKIN, WearablesIndex.WT_SHIRT, WearablesIndex.WT_JACKET, WearablesIndex.WT_GLOVES, WearablesIndex.WT_UNDERSHIRT]
        self.map[BakedIndex.BAKED_LOWER] = [WearablesIndex.WT_SHAPE, WearablesIndex.WT_SKIN, WearablesIndex.WT_PANTS, WearablesIndex.WT_SHOES, WearablesIndex.WT_SOCKS,  WearablesIndex.WT_JACKET, WearablesIndex.WT_UNDERPANTS]
        self.map[BakedIndex.BAKED_EYES] = [WearablesIndex.WT_EYES]
        self.map[BakedIndex.BAKED_SKIRT] = [WearablesIndex.WT_SKIRT]
        self.map[BakedIndex.BAKED_HAIR] = [WearablesIndex.WT_HAIR]


class AssetType(object):
    Texture         = 0
    Sound           = 1
    CallingCard     = 2
    Landmark        = 3
    Script          = 4
    Clothing        = 5
    Object          = 6
    NoteCard        = 7
    Category        = 8
    RootCategory    = 9
    LSLText         = 10
    LSLByteCode     = 11
    TextureTGA      = 12
    BodyPart        = 13
    Trash           = 14
    SnapshotCategory = 15
    LostAndFound    = 16
    SoundWav        = 17
    ImageTGA        = 18
    ImageJPEG       = 19
    Animation       = 20
    Gesture         = 21
    Simstate        = 22
    Count           = 23
    NONE            = -1

class TransferChannelType(object):
    Unknown    = 0
    Misc       = 1
    Asset      = 2
    NumTypes   = 3

class TransferSourceType(object):
    Unknown    = 0
    File       = 1
    Asset      = 2
    SimInvItem = 3
    SimEstate  = 4
    NumTypes   = 5

class TransferTargetType(object):
    Unknown    = 0
    File       = 1
    VFile      = 2

class TransferStatus(object):
    OK         = 0
    Done       = 1
    Skip       = 2
    Abort      = 3
    Error      = -1
    UnknownSource = -2
    InsufficientPermissions = -3



class Permissions(object):
    Transfer = 1 << 13
    Modify = 1 << 14
    Copy = 1 << 15
    Move = 1 << 19
    None_ = 0
    All = 0x7FFFFFFF
    Unrestricted = Transfer | Modify | Copy


 
