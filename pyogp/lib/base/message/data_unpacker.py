import struct
from uuid import UUID

from pyogp.lib.base.message.message_types import MsgType, EndianType, sizeof

class DataUnpacker(object):
    def __init__(self):
        self.unpacker = {}
        self.unpacker[MsgType.MVT_VARIABLE]       = ('>', self.__unpack_string)
        self.unpacker[MsgType.MVT_S8]             = ('>', 'b')
        self.unpacker[MsgType.MVT_U8]             = ('>','B')
        self.unpacker[MsgType.MVT_BOOL]           = ('>','B')
        self.unpacker[MsgType.MVT_LLUUID]         = ('>',self.__unpack_uuid)
        self.unpacker[MsgType.MVT_IP_ADDR]        = ('>',self.__unpack_string)
        self.unpacker[MsgType.MVT_IP_PORT]        = ('>','H')
        self.unpacker[MsgType.MVT_U16]            = ('<','H')
        self.unpacker[MsgType.MVT_U32]            = ('<','I')
        self.unpacker[MsgType.MVT_U64]            = ('<','Q')
        self.unpacker[MsgType.MVT_S16]            = ('<','h')
        self.unpacker[MsgType.MVT_S32]            = ('<','i')
        self.unpacker[MsgType.MVT_S64]            = ('<','q')
        self.unpacker[MsgType.MVT_F32]            = ('<','f')
        self.unpacker[MsgType.MVT_F64]            = ('<','d')
        self.unpacker[MsgType.MVT_LLVector3]      = ('<',self.__unpack_vector3)
        self.unpacker[MsgType.MVT_LLVector3d]     = ('<',self.__unpack_vector3d)
        self.unpacker[MsgType.MVT_LLVector4]      = ('<',self.__unpack_vector4)
        self.unpacker[MsgType.MVT_LLQuaternion]   = ('<',self.__unpack_quat)

    def unpack_data(self, data, data_type, start_index=-1, \
                    var_size=-1, endian_type=EndianType.NONE):
        if start_index != -1:
            if var_size != -1:
                data = data[start_index:start_index+var_size]
            else:
                data = data[start_index:start_index+sizeof(data_type)]
            
        if data_type in self.unpacker:
            unpack_tup = self.unpacker[data_type]
            endian = unpack_tup[0]
            #override endian
            if endian_type != EndianType.NONE:
                endian = endian_type
            
            unpack = unpack_tup[1]
            if callable(unpack):
                return unpack(endian, data)
            else:
                return struct.unpack(endian + unpack, data)[0]

        return None

    def __unpack_tuple(self, endian, tup, tp):
        size = len(tup) / struct.calcsize(tp)
        return struct.unpack(endian + str(size) + tp, tup)

    def __unpack_vector3(self, endian, vec):
        return self.__unpack_tuple(endian, vec, 'f')

    def __unpack_vector3d(self, endian, vec):
        return self.__unpack_tuple(endian, vec, 'd')

    def __unpack_vector4(self, endian, vec):
        return self.__unpack_tuple(endian, vec, 'f')

    def __unpack_quat(self, endian, quat):
        #first, pack to vector3
        #print "WARNING: UNPACKING A QUAT...."
        #vec = quat_to_vec3(quat)
        return self.__unpack_vector3(endian, quat)

    def __unpack_uuid(self, endian, uuid_data):
        return UUID(bytes=uuid_data)

    def __unpack_string(self, endian, pack_string):
        return pack_string
