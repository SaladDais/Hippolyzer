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

class PCode(object):
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

"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

 