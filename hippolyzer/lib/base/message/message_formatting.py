import ast
import base64
import logging
import math
import re
import uuid
from typing import *

from .. import datatypes
from .. import llsd
from .. import serialization as se
from ..helpers import HippoPrettyPrinter
from ..network.transport import Direction
from .msgtypes import PacketFlags, MsgBlockType
from .template import MessageTemplate
from .message import Message, Block, maybe_reload_templates


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
            **_filtered_exports(datatypes),
            **(globals_ or {})},
        locals_
    )


TextSpan = Tuple[int, int]
SpanDict = Dict[Tuple[Union[str, int], ...], TextSpan]


class SpannedString(str):
    spans: SpanDict = {}


class HumanMessageSerializer:
    @classmethod
    def from_human_string(cls, string, replacements=None, env=None, safe=True):
        maybe_reload_templates()
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
                first_split = [x for x in line.split(" ") if x]
                direction, message_name = first_split[:2]
                options = [x.strip("[]") for x in first_split[2:]]
                msg = Message(message_name)
                msg.direction = Direction[direction.upper()]
                for option in options:
                    if option in PacketFlags.__members__:
                        msg.send_flags |= PacketFlags[option]
                    elif re.match(r"^\d+$", option):
                        msg.send_flags |= int(option)
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
                        var_val = datatypes.UUID(var_val)
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

    @classmethod
    def to_human_string(cls, msg: Message, replacements=None, beautify=False,
                        template: Optional[MessageTemplate] = None) -> SpannedString:
        replacements = replacements or {}
        maybe_reload_templates()
        spans: SpanDict = {}
        string = ""
        if msg.direction is not None:
            string += f'{msg.direction.name} '
        string += msg.name
        flags = msg.send_flags
        for poss_flag in iter(PacketFlags):
            if flags & poss_flag:
                flags &= ~poss_flag
                string += f" [{poss_flag.name}]"
        # Make sure flags with unknown meanings don't get lost
        if flags:
            string += f" [{int(flags)}]"
        if msg.packet_id is not None:
            string += f'\n# ID: {msg.packet_id}'
            string += f'{", DROPPED" if msg.dropped else ""}{", SYNTHETIC" if msg.synthetic else ""}'
        if msg.extra:
            string += f'\n# EXTRA: {msg.extra!r}'
        string += '\n\n'

        for block_name, block_list in msg.blocks.items():
            block_suffix = ""
            if template and template.get_block(block_name).block_type == MsgBlockType.MBT_VARIABLE:
                block_suffix = '  # Variable'
            for block_num, block in enumerate(block_list):
                string += f"[{block_name}]{block_suffix}\n"
                for var_name, val in block.items():
                    start_len = len(string)
                    string += cls._format_var(msg, block, var_name, val, replacements, beautify)
                    end_len = len(string)
                    # Store the spans for each var so we can highlight specific matches
                    spans[(msg.name, block_name, block_num, var_name)] = (start_len, end_len)
                    string += "\n"
        spanned = SpannedString(string)
        spanned.spans = spans
        return spanned

    @classmethod
    def _format_var(cls, msg, block, var_name, var_val, replacements, beautify=False):
        string = ""
        # Check if we have a more human-readable way to present this field
        ser_key = (msg.name, block.name, var_name)
        serializer = se.SUBFIELD_SERIALIZERS.get(ser_key)
        field_prefix = ""
        if isinstance(var_val, VerbatimHumanVal):
            var_data = var_val
        elif isinstance(var_val, (uuid.UUID, datatypes.TupleCoord)):
            var_data = str(var_val)
        elif isinstance(var_val, (str, bytes)) and not serializer:
            var_data = cls._multi_line_pformat(var_val)
        else:
            var_data = repr(var_val)
        if serializer and beautify and not isinstance(var_val, VerbatimHumanVal):
            try:
                pretty_data = serializer.deserialize(block, var_val, pod=True)
                if pretty_data is not se.UNSERIALIZABLE:
                    string += f"  {var_name} =| {cls._multi_line_pformat(pretty_data)}"
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
