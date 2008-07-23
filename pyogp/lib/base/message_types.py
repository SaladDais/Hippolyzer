class MsgBlockType():
    MBT_SINGLE, \
    MBT_MULTIPLE, \
    MBT_VARIABLE = range(3)

#pack flags
#= '\x80'
#= '\x80'
#= '\x40'
#= '\x20'
#= '\x10'
#= '\x00'
class PackFlags():
    LL_ZERO_CODE_FLAG, \
    LL_RELIABLE_FLAG, \
    LL_RESENT_FLAG, \
    LL_ACK_FLAG, \
    LL_NONE = range(5)   

#frequency for messages
#= '\xFF\xFF\xFF'
#= '\xFF\xFF'
#= '\xFF'
#= ''
class MsgFrequency():
    FIXED_FREQUENCY_MESSAGE, \
    LOW_FREQUENCY_MESSAGE, \
    MEDIUM_FREQUENCY_MESSAGE, \
    HIGH_FREQUENCY_MESSAGE = range(4) 

class MsgTrust():
    LL_TRUSTED, \
    LL_NOTRUST = range(2)

class MsgEncoding():
    LL_UNENCODED, \
    LL_ZEROCODED = range(2)

class MsgDeprecation():
    LL_DEPRECATED, \
    LL_UDPDEPRECATED, \
    LL_NOTDEPRECATED = range(3)

#message variable types
class MsgType():
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
