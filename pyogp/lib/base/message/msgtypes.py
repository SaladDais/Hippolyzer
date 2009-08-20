
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

#represents how much of a message is taken up by packet ID things, such as
#the packet flags and the sequence number. After the ID, then comes the header
#NOTE: This will be moved into a messaging system eventually
class PacketLayout(object):
    PACKET_ID_LENGTH = 6
    PHL_FLAGS = 0
    PHL_PACKET_ID = 1 #length of 4
    PHL_OFFSET = 5
    PHL_NAME = 6
    #1 byte flags, 4 bytes sequence, 1 byte offset + 1 byte message name (high)
    MINIMUM_VALID_PACKET_SIZE = PACKET_ID_LENGTH + 1

class EndianType(object):
    LITTLE  = '<'
    BIG     = '>'
    NETWORK = '!'
    NONE    = ''

class MsgBlockType(object):
    MBT_SINGLE, \
    MBT_MULTIPLE, \
    MBT_VARIABLE = range(3)
    #LDE 230ct2008 added string array and class method for display of vartypes 
    MBT_String_List = [ 'Single', 'Multiple', 'Variable']
    @classmethod
    def MBT_as_string(cls,typenum):
        if typenum == None:
            return "None"
        return cls.MBT_String_List[typenum]


class PackFlags(object):
    LL_ZERO_CODE_FLAG = 0x80
    LL_RELIABLE_FLAG  = 0x40
    LL_RESENT_FLAG    = 0x20
    LL_ACK_FLAG       = 0x10
    LL_NONE           = 0x00

#frequency for messages
#= '\xFF\xFF\xFF'
#= '\xFF\xFF'
#= '\xFF'
#= ''
class MsgFrequency(object):
    FIXED_FREQUENCY_MESSAGE  = -1 #marking it
    LOW_FREQUENCY_MESSAGE    = 4
    MEDIUM_FREQUENCY_MESSAGE = 2
    HIGH_FREQUENCY_MESSAGE   = 1

class MsgTrust(object):
    LL_TRUSTED, \
    LL_NOTRUST = range(2)

class MsgEncoding(object):
    LL_UNENCODED, \
    LL_ZEROCODED = range(2)

class MsgDeprecation(object):
    LL_DEPRECATED, \
    LL_UDPDEPRECATED, \
    LL_UDPBLACKLISTED, \
    LL_NOTDEPRECATED = range(4)

#message variable types
class MsgType(object):
    #these are variables that aren't used because they can't be added to the
    #builder
    #MVT_NULL, \
    #MVT_U16Vec3, \
    #MVT_U16Quat, \
    #MVT_S16Array, \
    #MVT_EOL, \
    MVT_FIXED, \
    MVT_VARIABLE, \
    MVT_U8, \
    MVT_U16, \
    MVT_U32, \
    MVT_U64, \
    MVT_S8, \
    MVT_S16, \
    MVT_S32, \
    MVT_S64, \
    MVT_F32, \
    MVT_F64, \
    MVT_LLVector3, \
    MVT_LLVector3d, \
    MVT_LLVector4, \
    MVT_LLQuaternion, \
    MVT_LLUUID, \
    MVT_BOOL, \
    MVT_IP_ADDR, \
    MVT_IP_PORT = range(20)
    #LDE 23oct2008 added string array and class method to output more readable version of MVT var type.
    MVT_String_List = [ 'MVT_FIXED', 'MVT_VARIABLE', 'MVT_U8', 'MVT_U16', 'MVT_U32', 'MVT_U64',\
                 'MVT_S8', 'MVT_S16', 'MVT_S32', 'MVT_S64', 'MVT_F32', 'MVT_F64',\
                 'MVT_LLVector3', 'MVT_LLVector3d', 'MVT_LLVector4', 'MVT_LLQuaternion', 'MVT_LLUUID', \
                 'MVT_BOOL', 'MVT_IP_ADDR', 'MVT_IP_PORT' ]
    @classmethod
    def MVT_as_string(cls,typenum):
        return cls.MVT_String_List[typenum]



#TODO should this be changed? Less switch-style and more object-style?
def sizeof(var):
    if var == MsgType.MVT_FIXED:
        return -1
    elif var == MsgType.MVT_VARIABLE:
        return -1
    elif var == MsgType.MVT_U8:
        return 1
    elif var == MsgType.MVT_U16:
        return 2
    elif var == MsgType.MVT_U32:
        return 4
    elif var == MsgType.MVT_U64:
        return 8
    elif var == MsgType.MVT_S8:
        return 1
    elif var == MsgType.MVT_S16:
        return 2
    elif var == MsgType.MVT_S32:
        return 4
    elif var == MsgType.MVT_S64:
        return 8
    elif var == MsgType.MVT_F32:
        return 4
    elif var == MsgType.MVT_F64:
        return 8
    elif var == MsgType.MVT_LLVector3:
        return 12
    elif var == MsgType.MVT_LLVector3d:
        return 24
    elif var == MsgType.MVT_LLVector4:
        return 16
    elif var == MsgType.MVT_LLQuaternion:
        return 12
    elif var == MsgType.MVT_LLUUID:
        return 16
    elif var == MsgType.MVT_BOOL:
        return 1
    elif var == MsgType.MVT_IP_ADDR:
        return 4
    elif var == MsgType.MVT_IP_PORT:
        return 2



