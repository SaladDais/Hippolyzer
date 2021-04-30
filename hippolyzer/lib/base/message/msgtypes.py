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

import enum


# represents how much of a message is taken up by packet ID things, such as
# the packet flags and the sequence number. After the ID, then comes the header
# NOTE: This will be moved into a messaging system eventually

class PacketLayout:
    PACKET_ID_LENGTH = 6
    PHL_FLAGS = 0
    PHL_PACKET_ID = 1  # length of 4
    PHL_OFFSET = 5
    PHL_NAME = 6
    # 1 byte flags, 4 bytes sequence, 1 byte offset + 1 byte message name (high)
    MINIMUM_VALID_PACKET_SIZE = PACKET_ID_LENGTH + 1


class EndianType:
    LITTLE = '<'
    BIG = '>'
    NETWORK = '!'
    NONE = ''


class MsgBlockType:
    MBT_SINGLE = 0
    MBT_MULTIPLE = 1
    MBT_VARIABLE = 2
    MBT_String_List = ['Single', 'Multiple', 'Variable']


class PacketFlags(enum.IntFlag):
    ZEROCODED = 0x80
    RELIABLE = 0x40
    RESENT = 0x20
    ACK = 0x10


# frequency for messages
# = '\xFF\xFF\xFF'
# = '\xFF\xFF'
# = '\xFF'
# = ''
class MsgFrequency:
    FIXED_FREQUENCY_MESSAGE = -1  # marking it
    LOW_FREQUENCY_MESSAGE = 4
    MEDIUM_FREQUENCY_MESSAGE = 2
    HIGH_FREQUENCY_MESSAGE = 1


class MsgTrust:
    LL_NOTRUST = 0
    LL_TRUSTED = 1


class MsgEncoding:
    LL_UNENCODED = 0
    LL_ZEROCODED = 1


class MsgDeprecation:
    LL_DEPRECATED = 0
    LL_UDPDEPRECATED = 1
    LL_UDPBLACKLISTED = 2
    LL_NOTDEPRECATED = 3


# message variable types
class MsgType(enum.Enum):
    MVT_FIXED = 0
    MVT_VARIABLE = enum.auto()
    MVT_U8 = enum.auto()
    MVT_U16 = enum.auto()
    MVT_U32 = enum.auto()
    MVT_U64 = enum.auto()
    MVT_S8 = enum.auto()
    MVT_S16 = enum.auto()
    MVT_S32 = enum.auto()
    MVT_S64 = enum.auto()
    MVT_F32 = enum.auto()
    MVT_F64 = enum.auto()
    MVT_LLVector3 = enum.auto()
    MVT_LLVector3d = enum.auto()
    MVT_LLVector4 = enum.auto()
    MVT_LLQuaternion = enum.auto()
    MVT_LLUUID = enum.auto()
    MVT_BOOL = enum.auto()
    MVT_IP_ADDR = enum.auto()
    MVT_IP_PORT = enum.auto()

    @property
    def is_int(self):
        return any(self == x for x in (
            self.MVT_U8,
            self.MVT_U16,
            self.MVT_U32,
            self.MVT_U64,
            self.MVT_S8,
            self.MVT_S16,
            self.MVT_S32,
            self.MVT_S64,
            self.MVT_IP_PORT,
        ))

    @property
    def is_float(self):
        return any(self == x for x in (
            self.MVT_F32,
            self.MVT_F64,
        ))

    @property
    def size(self):
        return TYPE_SIZES[self]


TYPE_SIZES = {
    MsgType.MVT_FIXED: -1,
    MsgType.MVT_VARIABLE: -1,
    MsgType.MVT_U8: 1,
    MsgType.MVT_U16: 2,
    MsgType.MVT_U32: 4,
    MsgType.MVT_U64: 8,
    MsgType.MVT_S8: 1,
    MsgType.MVT_S16: 2,
    MsgType.MVT_S32: 4,
    MsgType.MVT_S64: 8,
    MsgType.MVT_F32: 4,
    MsgType.MVT_F64: 8,
    MsgType.MVT_LLVector3: 12,
    MsgType.MVT_LLVector3d: 24,
    MsgType.MVT_LLVector4: 16,
    MsgType.MVT_LLQuaternion: 12,
    MsgType.MVT_LLUUID: 16,
    MsgType.MVT_BOOL: 1,
    MsgType.MVT_IP_ADDR: 4,
    MsgType.MVT_IP_PORT: 2,
}
