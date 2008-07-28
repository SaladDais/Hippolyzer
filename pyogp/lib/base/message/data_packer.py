import struct

from pyogp.lib.base.message.message_types import MsgType

class DataPacker(object):
    def __init__(self):
        self.packer = {}
        self.packer[MsgType.MVT_VARIABLE]       = self.__pack_string
        self.packer[MsgType.MVT_U8]             = '>B'
        self.packer[MsgType.MVT_U16]            = '>H'
        self.packer[MsgType.MVT_U32]            = '>I'
        self.packer[MsgType.MVT_U64]            = '>Q'
        self.packer[MsgType.MVT_S8]             = '>b'
        self.packer[MsgType.MVT_S16]            = '>h'
        self.packer[MsgType.MVT_S32]            = '>i'
        self.packer[MsgType.MVT_S64]            = '>q'
        self.packer[MsgType.MVT_F32]            = '>f'
        self.packer[MsgType.MVT_F64]            = '>d'
        self.packer[MsgType.MVT_LLVector3]      = self.__pack_vector3
        self.packer[MsgType.MVT_LLVector3d]     = self.__pack_vector3d
        self.packer[MsgType.MVT_LLVector4]      = self.__pack_vector4
        self.packer[MsgType.MVT_LLQuaternion]   = self.__pack_quat
        self.packer[MsgType.MVT_LLUUID]         = self.__pack_uuid
        self.packer[MsgType.MVT_BOOL]           = '>B'
        self.packer[MsgType.MVT_IP_ADDR]        = self.__pack_string
        self.packer[MsgType.MVT_IP_PORT]        = self.__pack_string

    def pack_data(self, data, data_type):
        if data_type in self.packer:
            pack = self.packer[data_type]
            if callable(pack):
                return pack(data)
            else:
                return struct.pack(pack, data)

        return None

    def __pack_tuple(self, tup, tp):
        size = len(tup)
        return struct.pack('>' + str(size) + tp, *tup)

    def __pack_vector3(self, vec):
        return __pack_tuple(vec, 'f')

    def __pack_vector3d(self, vec):
        return __pack_tuple(vec, 'd')

    def __pack_vector4(self, vec):
        return __pack_tuple(vec, 'f')

    def __pack_quat(self, quat):
        #first, pack to vector3
        vec = quat_to_vec3(quat)
        return __pack_vector3(vec)

    def __pack_uuid(self, uuid):
        return uuid.bytes

    def __pack_string(self, pack_string):
        return pack_string
