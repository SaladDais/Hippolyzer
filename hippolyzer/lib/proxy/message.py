import ast
import base64
import importlib
import logging
import math
import os
import re
import typing
import uuid
from typing import *

import hippolyzer.lib.base.datatypes
from hippolyzer.lib.base.datatypes import *
import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.helpers import HippoPrettyPrinter
from hippolyzer.lib.base.message.message import Message, Block, PacketFlags
import hippolyzer.lib.proxy.templates as templates
from hippolyzer.lib.base.message.msgtypes import MsgBlockType
from hippolyzer.lib.base.message.template import MessageTemplate
from hippolyzer.lib.proxy.packets import Direction

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


def proxy_eval(eval_str: str, globals_=None, locals_=None):
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


class ProxiedMessage(Message):
    __slots__ = ("meta", "injected", "dropped", "direction")

    def __init__(self, *args, direction=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.direction = direction if direction is not None else Direction.OUT
        self.meta = {}
        self.injected = False
        self.dropped = False
        _maybe_reload_templates()

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
                msg = ProxiedMessage(message_name)
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
                    var_val = proxy_eval(
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

    def _args_repr(self, pretty=False):
        base = super()._args_repr(pretty=pretty)
        return f"{base}, direction=Direction.{self.direction.name}"
