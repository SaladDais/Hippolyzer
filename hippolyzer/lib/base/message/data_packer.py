"""
Copyright 2009, Linden Research, Inc.
  See NOTICE.md for previous contributors
Copyright 2021, Salad Dais
All Rights Reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import socket
import struct
from typing import *

from hippolyzer.lib.base.datatypes import *
from hippolyzer.lib.base.message.msgtypes import MsgType


PACKER = Callable[[Any], bytes]
UNPACKER = Callable[[bytes], Any]
SPEC = Tuple[UNPACKER, PACKER]


def _pack_string(pack_string):
    """Return the string UTF-8 encoded and null terminated."""
    if pack_string is None:
        return b''
    elif isinstance(pack_string, str):
        return pack_string.encode('utf-8') + b'\x00'
    else:
        return bytes(pack_string)


def _make_struct_spec(struct_fmt: str) -> SPEC:
    struct_obj = struct.Struct(struct_fmt)
    return (lambda x: struct_obj.unpack(x)[0]), struct_obj.pack


def _make_tuplecoord_spec(typ: Type[TupleCoord], struct_fmt: str,
                          needed_elems: Optional[int] = None) -> SPEC:
    struct_obj = struct.Struct(struct_fmt)
    if needed_elems is None:
        # Number of elems needed matches the number in the coord type
        def _packer(x):
            return struct_obj.pack(*x)
    else:
        # Special case, we only want to pack some of the components.
        # Mostly for Quaternion since we don't actually need to send W.
        def _packer(x):
            if isinstance(x, TupleCoord):
                x = x.data()
            return struct_obj.pack(*x[:needed_elems])
    return lambda x: typ(*struct_obj.unpack(x)), _packer


def _unpack_specs(cls):
    cls.UNPACKERS = {k: v[0] for (k, v) in cls.SPECS.items()}
    cls.PACKERS = {k: v[1] for (k, v) in cls.SPECS.items()}
    return cls


@_unpack_specs
class TemplateDataPacker:
    SPECS: Dict[MsgType, SPEC] = {
        MsgType.MVT_FIXED: (bytes, _pack_string),
        MsgType.MVT_VARIABLE: (bytes, _pack_string),
        MsgType.MVT_S8: _make_struct_spec('b'),
        MsgType.MVT_U8: _make_struct_spec('B'),
        MsgType.MVT_BOOL: _make_struct_spec('B'),
        MsgType.MVT_LLUUID: (lambda x: UUID(bytes=bytes(x)), lambda x: x.bytes),
        MsgType.MVT_IP_ADDR: (socket.inet_ntoa, socket.inet_aton),
        MsgType.MVT_IP_PORT: _make_struct_spec('!H'),
        MsgType.MVT_U16: _make_struct_spec('<H'),
        MsgType.MVT_U32: _make_struct_spec('<I'),
        MsgType.MVT_U64: _make_struct_spec('<Q'),
        MsgType.MVT_S16: _make_struct_spec('<h'),
        MsgType.MVT_S32: _make_struct_spec('<i'),
        MsgType.MVT_S64: _make_struct_spec('<q'),
        MsgType.MVT_F32: _make_struct_spec('<f'),
        MsgType.MVT_F64: _make_struct_spec('<d'),
        MsgType.MVT_LLVector3: _make_tuplecoord_spec(Vector3, "<3f"),
        MsgType.MVT_LLVector3d: _make_tuplecoord_spec(Vector3, "<3d"),
        MsgType.MVT_LLVector4: _make_tuplecoord_spec(Vector4, "<4f"),
        MsgType.MVT_LLQuaternion: _make_tuplecoord_spec(Quaternion, "<3f", needed_elems=3)
    }
    UNPACKERS: Dict[MsgType, UNPACKER] = {}
    PACKERS: Dict[MsgType, PACKER] = {}

    @classmethod
    def unpack(cls, data, data_type):
        return cls.UNPACKERS[data_type](data)

    @classmethod
    def pack(cls, data, data_type):
        return cls.PACKERS[data_type](data)


@_unpack_specs
class LLSDDataPacker(TemplateDataPacker):
    # Some template var types aren't directly representable in LLSD, so they
    # get encoded to binary fields.
    SPECS = {
        MsgType.MVT_IP_ADDR: (socket.inet_ntoa, socket.inet_aton),
        # LLSD ints are technically bound to S32 range.
        MsgType.MVT_U32: _make_struct_spec('!I'),
        MsgType.MVT_U64: _make_struct_spec('!Q'),
        MsgType.MVT_S64: _make_struct_spec('!q'),
    }
