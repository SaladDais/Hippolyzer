import struct

from pyogp.lib.base.message.message_types import MsgType, EndianType

class DataPacker(object):
    def __init__(self):
        self.packer = {}
        self.packer[MsgType.MVT_VARIABLE]       = ('>', self.__pack_string)
        self.packer[MsgType.MVT_S8]             = ('>', 'b')
        self.packer[MsgType.MVT_U8]             = ('>','B')
        self.packer[MsgType.MVT_BOOL]           = ('>','B')
        self.packer[MsgType.MVT_LLUUID]         = ('>',self.__pack_uuid)
        self.packer[MsgType.MVT_IP_ADDR]        = ('>',self.__pack_string)
        self.packer[MsgType.MVT_IP_PORT]        = ('>','H')
        self.packer[MsgType.MVT_U16]            = ('<','H')
        self.packer[MsgType.MVT_U32]            = ('<','I')
        self.packer[MsgType.MVT_U64]            = ('<','Q')
        self.packer[MsgType.MVT_S16]            = ('<','h')
        self.packer[MsgType.MVT_S32]            = ('<','i')
        self.packer[MsgType.MVT_S64]            = ('<','q')
        self.packer[MsgType.MVT_F32]            = ('<','f')
        self.packer[MsgType.MVT_F64]            = ('<','d')
        self.packer[MsgType.MVT_LLVector3]      = ('<',self.__pack_vector3)
        self.packer[MsgType.MVT_LLVector3d]     = ('<',self.__pack_vector3d)
        self.packer[MsgType.MVT_LLVector4]      = ('<',self.__pack_vector4)
        self.packer[MsgType.MVT_LLQuaternion]   = ('<',self.__pack_quat)

    def pack_data(self, data, data_type, endian_type=EndianType.NONE):
        if data_type in self.packer:
            pack_tup = self.packer[data_type]
            endian = pack_tup[0]
            #override endian
            if endian_type != EndianType.NONE:
                endian = endian_type
            
            pack = pack_tup[1]
            if callable(pack):
                return pack(endian, data)
            else:
                return struct.pack(endian + pack, data)

        return None

    def __pack_tuple(self, endian, tup, tp):
        size = len(tup)
        return struct.pack(endian + str(size) + tp, *tup)

    def __pack_vector3(self, endian, vec):
        return self.__pack_tuple(endian, vec, 'f')

    def __pack_vector3d(self, endian, vec):
        return self.__pack_tuple(endian,vec, 'd')

    def __pack_vector4(self, endian, vec):
        return self.__pack_tuple(endian, vec, 'f')

    def __pack_quat(self, endian, quat):
        #first, pack to vector3
        #vec = quat_to_vec3(quat)
        return self.__pack_vector3(endian, quat)

    def __pack_uuid(self, endian, uuid):
        return uuid.bytes

    def __pack_string(self, endian, pack_string):
        return pack_string
