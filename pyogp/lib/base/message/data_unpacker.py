import struct
from uuid import UUID

from pyogp.lib.base.message.message_types import MsgType, sizeof

class DataUnpacker(object):
    def __init__(self):
        self.unpacker = {}
        self.unpacker[MsgType.MVT_VARIABLE]     = self.__unpack_string
        self.unpacker[MsgType.MVT_U8]           = '>B'
        self.unpacker[MsgType.MVT_U16]          = '>H'
        self.unpacker[MsgType.MVT_U32]          = '>I'
        self.unpacker[MsgType.MVT_U64]          = '>Q'
        self.unpacker[MsgType.MVT_S8]           = '>b'
        self.unpacker[MsgType.MVT_S16]          = '>h'
        self.unpacker[MsgType.MVT_S32]          = '>i'
        self.unpacker[MsgType.MVT_S64]          = '>q'
        self.unpacker[MsgType.MVT_F32]          = '>f'
        self.unpacker[MsgType.MVT_F64]          = '>d'
        self.unpacker[MsgType.MVT_LLVector3]    = self.__unpack_vector3
        self.unpacker[MsgType.MVT_LLVector3d]   = self.__unpack_vector3d
        self.unpacker[MsgType.MVT_LLVector4]    = self.__unpack_vector4
        self.unpacker[MsgType.MVT_LLQuaternion] = self.__unpack_quat
        self.unpacker[MsgType.MVT_LLUUID]       = self.__unpack_uuid
        self.unpacker[MsgType.MVT_BOOL]         = '>B'
        self.unpacker[MsgType.MVT_IP_ADDR]      = self.__unpack_string
        self.unpacker[MsgType.MVT_IP_PORT]      = '>H'    

    def unpack_data(self, data, data_type, start_index=0, var_size=0):
        if start_index != 0:
            if var_size != 0:
                data = data[start_index:start_index+var_size]
            else:
                data = data[start_index:start_index+sizeof(data_type)]
            
        if data_type in self.unpacker:
            unpack = self.unpacker[data_type]
            if callable(unpack):
                return unpack(data)
            else:
                return struct.unpack(unpack, data)[0]

        return None

    def __unpack_tuple(self, tup, tp):
        size = len(tup) / struct.calcsize(tp)
        return struct.unpack('>' + str(size) + tp, tup)

    def __unpack_vector3(self, vec):
        return __unpack_tuple(vec, 'f')

    def __unpack_vector3d(self, vec):
        return __unpack_tuple(vec, 'd')

    def __unpack_vector4(self, vec):
        return __unpack_tuple(vec, 'f')

    def __unpack_quat(self, quat):
        #first, pack to vector3
        vec = quat_to_vec3(quat)
        return __unpack_vector3(vec)

    def __unpack_uuid(self, uuid_data):
        return UUID(bytes=uuid_data)

    def __unpack_string(self, pack_string):
        return pack_string
