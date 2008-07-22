class MsgBlockType():
    MBT_SINGLE, \
    MBT_MULTIPLE, \
    MBT_VARIABLE = range(3)

#pack flags
class PackFlags():
    LL_ZERO_CODE_FLAG = '\x80'
    LL_RELIABLE_FLAG  = '\x40'
    LL_RESENT_FLAG    = '\x20'
    LL_ACK_FLAG       = '\x10'
    LL_NONE           = '\x00'

#frequency for messages
class MsgFrequency():
    FIXED_FREQUENCY_MESSAGE  = '\xFF\xFF\xFF'
    LOW_FREQUENCY_MESSAGE    = '\xFF\xFF'
    MEDIUM_FREQUENCY_MESSAGE = '\xFF'
    HIGH_FREQUENCY_MESSAGE   = ''

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
