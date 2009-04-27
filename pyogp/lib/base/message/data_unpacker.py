# standard python libs
import struct
import binascii
import array

# pyogp
from pyogp.lib.base.exc import *
from pyogp.lib.base.datatypes import *

# pygop messaging
from types import MsgType, EndianType, sizeof

class DataUnpacker(object):
    def __init__(self):
        self.unpacker = {}
        self.unpacker[MsgType.MVT_FIXED]          = ('<',self.__unpack_fixed)  #LDE 230ct2008 handler for MVT_FIXED
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
                return unpack(endian, data, var_size)
            else:
                try:
                    return struct.unpack(endian + unpack, data)[0]
                except struct.error, error:
                    #print error
                    raise DataUnpackingError(data, error)

        return None

    def __unpack_tuple(self, endian, tup, tp, var_size=None):
        size = len(tup) / struct.calcsize(tp)
        return struct.unpack(endian + str(size) + tp, tup)

    def __unpack_vector3(self, endian, vec, var_size=None):
        #return self.__unpack_tuple(endian, vec, 'f')
        return Vector3(vec, 0)

    def __unpack_vector3d(self, endian, vec, var_size=None):
        return self.__unpack_tuple(endian, vec, 'd')

    def __unpack_vector4(self, endian, vec, var_size=None):
        return self.__unpack_tuple(endian, vec, 'f')

    def __unpack_quat(self, endian, quat, var_size=None):
        #first, pack to vector3
        #print "WARNING: UNPACKING A QUAT...."
        #vec = quat_to_vec3(quat)
        return Quaternion(quat, 0)

    def __unpack_uuid(self, endian, uuid_data, var_size=None):
        # return datatypes.UUID
        return UUID(bytes=uuid_data, offset = 0)

    def __unpack_string(self, endian, pack_string, var_size):
        return pack_string.rstrip() # strip trailing null 

    def __unpack_fixed(self, endian, data, var_size): #LDE 23oct2008 handler for MVT_FIXED
        return data

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

