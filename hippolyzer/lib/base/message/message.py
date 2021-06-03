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

import ast
import base64
import copy
import enum
import itertools
import logging
import math
import os
import re
import uuid
from typing import *

import hippolyzer.lib.base.datatypes
from hippolyzer.lib.base.datatypes import *
import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.helpers import HippoPrettyPrinter
import hippolyzer.lib.base.templates as templates
from hippolyzer.lib.base.message.msgtypes import MsgBlockType, PacketFlags
from hippolyzer.lib.base.message.template import MessageTemplate
from hippolyzer.lib.base.network.transport import Direction


BLOCK_DICT = Dict[str, "MsgBlockList"]
VAR_TYPE = Union[TupleCoord, bytes, str, float, int, Tuple, UUID]

_TEMPLATES_MTIME = os.stat(templates.__file__).st_mtime


def _maybe_reload_templates():
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

    def __init__(self, name, /, *, fill_missing=False, **kwargs):
        self.name = name
        self.size = 0
        self.message_name: Optional[str] = None
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
    __slots__ = ("name", "send_flags", "_packet_id", "acks", "body_boundaries", "queued",
                 "offset", "raw_extra", "raw_body", "deserializer", "_blocks", "finalized",
                 "direction", "meta", "injected", "dropped")

    def __init__(self, name, *args, packet_id=None, flags=0, acks=None, direction=None):
        # TODO: Do this on a timer or something.
        _maybe_reload_templates()

        self.name = name
        self.send_flags = flags
        self._packet_id: Optional[int] = packet_id  # aka, sequence number

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
        self.injected = False
        self.dropped = False

        self.add_blocks(args)

    @property
    def packet_id(self) -> Optional[int]:
        return self._packet_id

    @packet_id.setter
    def packet_id(self, val: Optional[int]):
        self._packet_id = val
        # Changing packet ID clears the finalized flag
        self.finalized = False

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

    def to_dict(self):
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

        return base_repr

    @classmethod
    def from_dict(cls, dict_val):
        msg = cls(dict_val['message'])
        for block_type, blocks in dict_val['body'].items():
            msg.create_block_list(block_type)
            for block in blocks:
                msg.add_block(Block(block_type, **block))
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
        self.queued = True

        # Original was dropped so let's make sure we have clean acks and packet id
        message_copy.acks = tuple()
        message_copy.send_flags &= ~PacketFlags.ACK
        message_copy.packet_id = None
        return message_copy

    def to_human_string(self, replacements=None, beautify=False,
                        template: Optional[MessageTemplate] = None) -> SpannedString:
        replacements = replacements or {}
        _maybe_reload_templates()
        spans: SpanDict = {}
        string = ""
        if self.direction is not None:
            string += f'{self.direction.name} '
        string += self.name
        if self.packet_id is not None:
            string += f'\n# {self.packet_id}: {PacketFlags(self.send_flags)!r}'
            string += f'{", DROPPED" if self.dropped else ""}{", INJECTED" if self.injected else ""}'
        if self.extra:
            string += f'\n# EXTRA: {self.extra!r}'
        string += '\n\n'

        for block_name, block_list in self.blocks.items():
            block_suffix = ""
            if template and template.get_block(block_name).block_type == MsgBlockType.MBT_VARIABLE:
                block_suffix = '  # Variable'
            for block_num, block in enumerate(block_list):
                string += f"[{block_name}]{block_suffix}\n"
                for var_name, val in block.items():
                    start_len = len(string)
                    string += self._format_var(block, var_name, val, replacements, beautify)
                    end_len = len(string)
                    # Store the spans for each var so we can highlight specific matches
                    spans[(self.name, block_name, block_num, var_name)] = (start_len, end_len)
                    string += "\n"
        spanned = SpannedString(string)
        spanned.spans = spans
        return spanned

    def _format_var(self, block, var_name, var_val, replacements, beautify=False):
        string = ""
        # Check if we have a more human-readable way to present this field
        ser_key = (self.name, block.name, var_name)
        serializer = se.SUBFIELD_SERIALIZERS.get(ser_key)
        field_prefix = ""
        if isinstance(var_val, VerbatimHumanVal):
            var_data = var_val
        elif isinstance(var_val, (uuid.UUID, TupleCoord)):
            var_data = str(var_val)
        elif isinstance(var_val, (str, bytes)) and not serializer:
            var_data = self._multi_line_pformat(var_val)
        else:
            var_data = repr(var_val)
        if serializer and beautify and not isinstance(var_val, VerbatimHumanVal):
            try:
                pretty_data = serializer.deserialize(block, var_val, pod=True)
                if pretty_data is not se.UNSERIALIZABLE:
                    string += f"  {var_name} =| {self._multi_line_pformat(pretty_data)}"
                    if serializer.AS_HEX and isinstance(var_val, int):
                        var_data = hex(var_val)
                    if serializer.ORIG_INLINE:
                        string += f" #{var_data}"
                        return string
                    else:
                        string += "\n"
                    # Human-readable version should be used, orig data is commented out
                    field_prefix = "#"
            except:
                logging.exception(f"Failed in subfield serializer {ser_key!r}")
        if beautify:
            if block.name == "AgentData":
                if var_name == "AgentID" and var_val == replacements.get("AGENT_ID"):
                    var_data = "[[AGENT_ID]]"
                elif var_name == "SessionID" and var_val == replacements.get("SESSION_ID"):
                    var_data = "[[SESSION_ID]]"
            if "CircuitCode" in var_name or ("Code" in var_name and "Circuit" in block.name):
                if var_val == replacements.get("CIRCUIT_CODE"):
                    var_data = "[[CIRCUIT_CODE]]"
        string += f"  {field_prefix}{var_name} = {var_data}"
        return string

    @staticmethod
    def _multi_line_pformat(val):
        printer = HippoPrettyPrinter(width=100)
        val = printer.pformat(val)
        newstr = ""
        # Now we need to rebuild this to add in the appropriate
        # line continuations.
        lines = list(val.splitlines())
        first_line = True
        while lines:
            line = lines.pop(0)
            prefix = ""
            suffix = ""
            if first_line:
                first_line = False
            else:
                prefix = "    "

            if lines:
                suffix = " \\\n"
            newstr += f"{prefix}{line}{suffix}"
        return newstr

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

    @classmethod
    def from_human_string(cls, string, replacements=None, env=None, safe=True):
        _maybe_reload_templates()
        replacements = replacements or {}
        env = env or {}
        first_line = True
        cur_block = None
        msg = None
        lines = [x.strip() for x in string.split("\n") if x.strip()]
        while lines:
            line = lines.pop(0)
            # Ignore comment / blank lines
            if re.match(r"^\s*(#.*)?$", line):
                continue

            if first_line:
                direction, message_name = line.split(" ", 1)
                msg = cls(message_name)
                msg.direction = Direction[direction.upper()]
                first_line = False
                continue

            if line.startswith("["):
                cur_block = Block(re.search(r"\w+", line).group(0))
                msg.add_block(cur_block)
            else:
                expr_match = re.match(r"^\s*(\w+)\s*(=[|$]*)\s*(.*)$", line)
                var_name, operator, var_val = expr_match.groups()
                # Multiline, eat all the line continuations
                while var_val.endswith("\\"):
                    var_val = var_val[:-1].rstrip()
                    if lines:
                        var_val += lines.pop(0)

                plain = operator == "="
                packed = "|" in operator
                evaled = "$" in operator

                if evaled and safe:
                    raise ValueError("Can't use eval operator in safe mode")

                if plain:
                    replacement_match = re.match(r"\[\[(\w+)]]", var_val)
                    if replacement_match:
                        replacement_name = replacement_match.group(1)
                        var_val = replacements.get(replacement_name)
                        if var_val is None:
                            raise ValueError("Tried to use undefined replacement %s" % replacement_name)
                        if callable(var_val):
                            var_val = var_val()
                    # alternate way of specifying a vector or quat
                    elif var_val.startswith("<"):
                        var_val = re.sub(r"[<>]", "", var_val)
                        var_val = tuple(float(x) for x in var_val.split(","))
                    # UUID-ish
                    elif re.match(r"\A\w+-\w+-.*", var_val):
                        var_val = UUID(var_val)
                    else:
                        var_val = ast.literal_eval(var_val)

                # Normally gross, but necessary for expressiveness in built messages
                # unless a metalanguage is added.
                if evaled:
                    var_val = subfield_eval(
                        var_val,
                        globals_={**env, **replacements},
                        locals_={"block": cur_block}
                    )
                # Using an packer specific to this message
                if packed:
                    if not evaled:
                        var_val = ast.literal_eval(var_val)
                    ser_key = (msg.name, cur_block.name, var_name)
                    serializer = se.SUBFIELD_SERIALIZERS.get(ser_key)
                    if not serializer:
                        raise KeyError(f"No subfield serializer for {ser_key!r}")
                    var_val = serializer.serialize(cur_block, var_val)

                cur_block[var_name] = var_val
        return msg

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


class VerbatimHumanVal(str):
    pass


def _filtered_exports(mod):
    return {k: getattr(mod, k) for k in mod.__all__}


def subfield_eval(eval_str: str, globals_=None, locals_=None):
    return eval(
        eval_str,
        {
            "llsd": llsd,
            "base64": base64,
            "math": math,
            **_filtered_exports(hippolyzer.lib.base.datatypes),
            **(globals_ or {})},
        locals_
    )


TextSpan = Tuple[int, int]
SpanDict = Dict[Tuple[Union[str, int], ...], TextSpan]


class SpannedString(str):
    spans: SpanDict = {}
