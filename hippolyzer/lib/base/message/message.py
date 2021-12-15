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
from __future__ import annotations

import copy
import enum
import importlib
import itertools
import logging
import os
import uuid
from typing import *

from hippolyzer.lib.base.datatypes import *
import hippolyzer.lib.base.serialization as se
import hippolyzer.lib.base.templates as templates
from hippolyzer.lib.base.datatypes import Pretty
from hippolyzer.lib.base.message.msgtypes import PacketFlags
from hippolyzer.lib.base.network.transport import Direction, ADDR_TUPLE

BLOCK_DICT = Dict[str, "MsgBlockList"]
VAR_TYPE = Union[TupleCoord, bytes, str, float, int, Tuple, UUID]

_TEMPLATES_MTIME = os.stat(templates.__file__).st_mtime


def maybe_reload_templates():
    # Templates may be modified at runtime during development, check
    # if they've changed since startup and reload if they have.
    global _TEMPLATES_MTIME
    templates_mtime = os.stat(templates.__file__).st_mtime

    if _TEMPLATES_MTIME is None or _TEMPLATES_MTIME < templates_mtime:
        print("Reloading templates")
        try:
            importlib.reload(templates)  # type: ignore
            _TEMPLATES_MTIME = templates_mtime
        except:
            logging.exception("Failed to reload templates!")


class Block:
    """
    base representation of a block
    Block expects a name, and kwargs for variables (var_name = value)
    """
    __slots__ = ('name', 'size', 'vars', 'message_name', '_ser_cache', 'fill_missing',)
    PARENT_MESSAGE_NAME: ClassVar[Optional[str]] = None

    def __init__(self, name, /, *, fill_missing=False, **kwargs):
        self.name = name
        self.size = 0
        self.message_name: Optional[str] = self.PARENT_MESSAGE_NAME
        self.vars: Dict[str, VAR_TYPE] = {}
        self._ser_cache: Dict[str, Any] = {}
        self.fill_missing = fill_missing
        for var_name, val in kwargs.items():
            self[var_name] = val

    def get_variable(self, var_name):
        return self.vars.get(var_name)

    def __contains__(self, item):
        return item in self.vars

    def __getitem__(self, name):
        return self.vars[name]

    def __setitem__(self, key, value):
        if isinstance(value, Pretty):
            return self.serialize_var(key, value.value)

        # These don't pickle well since they're likely to get hot-reloaded
        if isinstance(value, (enum.IntEnum, enum.IntFlag)):
            value = int(value)

        self.vars[key] = value
        # Invalidate the serialization cache if we manually changed the value
        if key in self._ser_cache:
            self._ser_cache.pop(key)

    def get_serializer(self, var_name) -> se.BaseSubfieldSerializer:
        serializer_key = (self.message_name, self.name, var_name)
        serializer = se.SUBFIELD_SERIALIZERS.get(serializer_key)
        if not serializer:
            raise KeyError(f"No serializer for {serializer_key!r}")
        return serializer

    def deserialize_var(self, var_name, make_copy=True):
        """
        Deserialize a var, using a cached version if available

        Does a deepcopy() of the value from the cache by default, so
        callers don't accidentally mutate the cached version. Allows
        opting out as otherwise deepcopy() can dominate runtime if
        you don't expect mutations.
        """
        if var_name in self._ser_cache:
            val = self._ser_cache[var_name]
            return copy.deepcopy(val) if make_copy else val
        serializer = self.get_serializer(var_name)
        deser = serializer.deserialize(self, self[var_name], pod=False)
        self._ser_cache[var_name] = deser
        return copy.deepcopy(deser) if make_copy else deser

    def serialize_var(self, var_name, val):
        serializer = self.get_serializer(var_name)
        serialized = serializer.serialize(self, val)
        self[var_name] = serialized
        self._ser_cache[var_name] = val

    def invalidate_caches(self):
        self._ser_cache.clear()

    def items(self):
        return self.vars.items()

    def finalize(self):
        # Stupid hack around the fact that blocks don't know how to
        # invoke field-specific serializers until they're added to a message.
        # Can do `Block("FooBlock", Baz_={"someserializedval": 1})` to set
        # "Baz" to a serialized val without having to first construct a message.
        for name in tuple(self.vars.keys()):
            if not name.endswith("_"):
                continue
            val = self.vars.pop(name)
            self.serialize_var(name.rstrip("_"), val)

    def repr(self, pretty=False):
        block_vars = {}
        if pretty:
            if not self.message_name:
                raise ValueError("Can't give pretty representation of block outside a message")
            for key in tuple(self.vars.keys()):
                try:
                    self.get_serializer(key)
                except KeyError:
                    block_vars[key] = repr(self.vars[key])
                    continue
                # We have a serializer, include the pretty output in the repr,
                # using the _ suffix so the builder knows it needs to be serialized.
                block_vars[f"{key}_"] = repr(self.deserialize_var(key))
        else:
            block_vars = self.vars

        kws = ", ".join((f"{k}={v if pretty else repr(v)}" for k, v in block_vars.items()))
        if kws:
            kws = ", " + kws
        return f"{self.__class__.__name__}({self.name!r}{kws})"

    def __repr__(self):
        return self.repr()


class MsgBlockList(List["Block"]):
    __slots__ = ()

    def __getitem__(self, item) -> Union["Block", VAR_TYPE]:
        if isinstance(item, str):
            return super().__getitem__(0)[item]
        return super().__getitem__(item)

    def __setitem__(self, item: Union[str, int, slice], val):
        if isinstance(item, str):
            self[0][item] = val
        else:
            super().__setitem__(item, val)


class Message:
    __slots__ = ("name", "send_flags", "packet_id", "acks", "body_boundaries", "queued",
                 "offset", "raw_extra", "raw_body", "deserializer", "_blocks", "finalized",
                 "direction", "meta", "synthetic", "dropped", "sender")

    def __init__(self, name, *args, packet_id=None, flags=0, acks=None, direction=None):
        # TODO: Do this on a timer or something.
        maybe_reload_templates()

        self.name = name
        self.send_flags = flags
        self.packet_id: Optional[int] = packet_id  # aka, sequence number

        self.acks = acks if acks is not None else tuple()
        self.body_boundaries = (-1, -1)
        self.offset = 0
        self.raw_extra = b""
        self.direction: Direction = direction if direction is not None else Direction.OUT
        # For lazy deserialization
        self.raw_body = None
        self.deserializer = None
        # should be set once a packet is sent / dropped to prevent accidental
        # re-sending or re-dropping
        self.finalized = False
        # Whether message is owned by the queue or should be sent immediately
        self.queued: bool = False
        self._blocks: BLOCK_DICT = {}
        self.meta = {}
        self.synthetic = packet_id is None
        self.dropped = False
        self.sender: Optional[ADDR_TUPLE] = None

        self.add_blocks(args)

    def add_blocks(self, block_list):
        # can have a list of blocks if it is multiple or variable
        for block in block_list:
            if type(block) == list:
                for bl in block:
                    self.add_block(bl)
            else:
                self.add_block(block)

    @property
    def extra(self) -> bytes:
        return self.raw_extra

    @extra.setter
    def extra(self, val: bytes):
        # Make sure this message is fully parsed if it wasn't already,
        # changing `.extra` requires re-serializing the message body.
        self.ensure_parsed()
        self.raw_extra = val
        self.offset = len(val)

    @property
    def blocks(self) -> BLOCK_DICT:
        self.ensure_parsed()
        return self._blocks

    @blocks.setter
    def blocks(self, val: BLOCK_DICT):
        self._blocks = val

        # block list was clobbered, so we don't care about any unparsed data
        self.raw_body = None
        self.deserializer = None

    def create_block_list(self, block_name: str):
        # There's a slight semantic difference between a missing block list
        # and a present block list with 0 length. This helps us distinguish.
        if block_name not in self.blocks:
            self.blocks[block_name] = MsgBlockList()

    def add_block(self, block: Block):
        self.create_block_list(block.name)

        self.blocks[block.name].append(block)
        block.message_name = self.name
        block.finalize()

    def get_block(self, block_name: str, default=None, /) -> Optional[Block]:
        return self.blocks.get(block_name, default)

    @property
    def reliable(self):
        # int() because otherwise this causes an alloc
        return self.send_flags & int(PacketFlags.RELIABLE)

    @property
    def has_acks(self):
        return self.send_flags & int(PacketFlags.ACK)

    @property
    def zerocoded(self):
        return self.send_flags & int(PacketFlags.ZEROCODED)

    @property
    def resent(self):
        return self.send_flags & int(PacketFlags.RESENT)

    def ensure_parsed(self):
        # This is a little magic, think about whether we want this.
        if self.raw_body and self.deserializer():
            self.deserializer().parse_message_body(self)

    def to_dict(self, extended=False):
        """ A dict representation of a message.

        This is the form used for templated messages sent via EQ.
        """
        self.ensure_parsed()
        base_repr = {'message': self.name, 'body': {}}

        for block_type in self.blocks:
            dict_blocks = base_repr['body'].setdefault(block_type, [])
            for block in self.blocks[block_type]:
                new_vars = {}
                for var_name, val in block.items():
                    new_vars[var_name] = val
                dict_blocks.append(new_vars)

        if extended:
            base_repr.update({
                "packet_id": self.packet_id,
                "meta": self.meta.copy(),
                "dropped": self.dropped,
                "synthetic": self.synthetic,
                "direction": self.direction.name,
                "send_flags": int(self.send_flags),
                "extra": self.extra,
                "acks": self.acks,
            })

        return base_repr

    @classmethod
    def from_dict(cls, dict_val):
        msg = cls(dict_val['message'])
        for block_type, blocks in dict_val['body'].items():
            msg.create_block_list(block_type)
            for block in blocks:
                msg.add_block(Block(block_type, **block))

        if 'packet_id' in dict_val:
            # extended format
            msg.packet_id = dict_val['packet_id']
            msg.meta = dict_val['meta']
            msg.dropped = dict_val['dropped']
            msg.synthetic = dict_val['synthetic']
            msg.direction = Direction[dict_val['direction']]
            msg.send_flags = dict_val['send_flags']
            msg.extra = dict_val['extra']
            msg.acks = dict_val['acks']
        return msg

    def invalidate_caches(self):
        # Don't have any caches if we haven't even parsed
        if self.raw_body:
            return
        for blocks in self.blocks.values():
            for block in blocks:
                block.invalidate_caches()

    def __getitem__(self, item):
        return self.blocks[item]

    def __setitem__(self, key: str, value):
        if not isinstance(value, (list, tuple)):
            value = (value,)
        if not isinstance(value, MsgBlockList):
            value = MsgBlockList(value)
        self.blocks[key] = value

    def __contains__(self, item):
        return item in self.blocks

    def _args_repr(self, pretty=False):
        sep = ",\n  "
        block_reprs = sep.join(x.repr(pretty=pretty) for x in itertools.chain(*self.blocks.values()))
        if block_reprs:
            block_reprs = sep + block_reprs
        return f"{self.name!r}{block_reprs}, direction=Direction.{self.direction.name}"

    def repr(self, pretty=False):
        self.ensure_parsed()
        return f"{self.__class__.__name__}({self._args_repr(pretty=pretty)})"

    def take(self):
        message_copy = copy.deepcopy(self)

        # Set the queued flag so the original will be dropped and acks will be sent
        if not self.finalized:
            self.queued = True

        # Original was dropped so let's make sure we have clean acks and packet id
        message_copy.acks = tuple()
        message_copy.send_flags &= ~PacketFlags.ACK
        message_copy.packet_id = None
        message_copy.dropped = False
        message_copy.finalized = False
        message_copy.queued = False
        return message_copy

    def to_summary(self):
        string = ""
        for block_name, block_list in self.blocks.items():
            for block in block_list:
                for var_name, val in block.items():
                    if block.name == "AgentData" and var_name in ("AgentID", "SessionID"):
                        continue
                    if string:
                        string += ", "
                    string += f"{var_name}={_trunc_repr(val, 10)}"
        return string

    def __repr__(self):
        return self.repr()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.to_dict() == other.to_dict()


def _trunc_repr(val, max_len):
    if isinstance(val, (uuid.UUID, TupleCoord)):
        val = str(val)
    repr_val = repr(val)
    if isinstance(val, str):
        repr_val = repr_val[1:-1]
    if isinstance(val, bytes):
        repr_val = repr_val[2:-1]
    if len(repr_val) > max_len:
        return repr_val[:max_len] + "…"
    return repr_val
