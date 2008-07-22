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

#message variable types
class MsgTypes():
    #these are variables that aren't used because they can't be added to the
    #builder
    #MVT_NULL, \
    #MVT_FIXED, \
    #MVT_VARIABLE, \
    #MVT_U16Vec3, \
    #MVT_U16Quat, \
    #MVT_S16Array, \
    #MVT_EOL, \
    #MVT_S64, \
    MVT_BOOL, \
    MVT_S8, \
    MVT_U8, \
    MVT_S16, \
    MVT_U16, \
    MVT_F32, \
    MVT_S32, \
    MVT_U32, \
    MVT_U64, \
    MVT_F64, \
    MVT_LLVector3, \
    MVT_LLVector4, \
    MVT_LLVector3d, \
    MVT_LLQuaternion, \
    MVT_LLUUID, \
    MVT_IP_ADDR, \
    MVT_IP_PORT = range(17)
