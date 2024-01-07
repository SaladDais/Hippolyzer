import calendar
import datetime
import struct
import typing
import uuid
import zlib

from llsd import *
# So we can directly reference the original wrapper funcs where necessary
import llsd as base_llsd
from llsd.base import is_string, is_unicode

from hippolyzer.lib.base.datatypes import *


class HippoLLSDBaseFormatter(base_llsd.base.LLSDBaseFormatter):
    UUID: callable
    ARRAY: callable

    def __init__(self):
        super().__init__()
        self.type_map[UUID] = self.UUID
        self.type_map[Vector2] = self.TUPLECOORD
        self.type_map[Vector3] = self.TUPLECOORD
        self.type_map[Vector4] = self.TUPLECOORD
        self.type_map[Quaternion] = self.TUPLECOORD

    def TUPLECOORD(self, v: TupleCoord):
        return self.ARRAY(v.data())


class HippoLLSDXMLFormatter(base_llsd.serde_xml.LLSDXMLFormatter, HippoLLSDBaseFormatter):
    def __init__(self):
        super().__init__()


class HippoLLSDXMLPrettyFormatter(base_llsd.serde_xml.LLSDXMLPrettyFormatter, HippoLLSDBaseFormatter):
    def __init__(self):
        super().__init__()


def format_pretty_xml(val: typing.Any) -> bytes:
    return HippoLLSDXMLPrettyFormatter().format(val)


def format_xml(val: typing.Any) -> bytes:
    return HippoLLSDXMLFormatter().format(val)


class HippoLLSDNotationFormatter(base_llsd.serde_notation.LLSDNotationFormatter, HippoLLSDBaseFormatter):
    def __init__(self):
        super().__init__()

    def STRING(self, v):
        # llbase's notation LLSD encoder isn't suitable for generating line-delimited
        # LLSD because the string formatter leaves \n unencoded, unlike indra's llcommon.
        # Add our own escaping rule.
        return super().STRING(v).replace(b"\n", b"\\n")


def format_notation(val: typing.Any) -> bytes:
    return HippoLLSDNotationFormatter().format(val)


def format_binary(val: typing.Any, with_header=True) -> bytes:
    val = _format_binary_recurse(val)
    if with_header:
        return b'<?llsd/binary?>\n' + val
    return val


# This is copied almost wholesale from https://bitbucket.org/lindenlab/llbase/src/master/llbase/llsd.py
# With a few minor changes to make serialization round-trip correctly. It's evil.
def _format_binary_recurse(something) -> bytes:
    """Binary formatter workhorse."""
    def _format_list(list_something):
        array_builder = [b'[' + struct.pack('!i', len(list_something))]
        for item in list_something:
            array_builder.append(_format_binary_recurse(item))
        array_builder.append(b']')
        return b''.join(array_builder)

    if something is None:
        return b'!'
    elif isinstance(something, LLSD):
        return _format_binary_recurse(something.thing)
    elif isinstance(something, bool):
        if something:
            return b'1'
        else:
            return b'0'
    elif isinstance(something, int):
        try:
            return b'i' + struct.pack('!i', something)
        except (OverflowError, struct.error) as exc:
            raise LLSDSerializationError(str(exc), something)
    elif isinstance(something, float):
        try:
            return b'r' + struct.pack('!d', something)
        except SystemError as exc:
            raise LLSDSerializationError(str(exc), something)
    elif isinstance(something, uuid.UUID):
        return b'u' + something.bytes
    elif isinstance(something, binary):
        return b'b' + struct.pack('!i', len(something)) + something
    elif is_string(something):
        if is_unicode(something):
            something = something.encode("utf8")
        return b's' + struct.pack('!i', len(something)) + something
    elif isinstance(something, uri):
        return b'l' + struct.pack('!i', len(something)) + something.encode("utf8")
    elif isinstance(something, datetime.datetime):
        return b'd' + struct.pack('<d', something.timestamp())
    elif isinstance(something, datetime.date):
        seconds_since_epoch = calendar.timegm(something.timetuple())
        return b'd' + struct.pack('<d', seconds_since_epoch)
    elif isinstance(something, (list, tuple)):
        return _format_list(something)
    elif isinstance(something, dict):
        map_builder = [b'{' + struct.pack('!i', len(something))]
        for key, value in something.items():
            if isinstance(key, str):
                key = key.encode("utf8")
            map_builder.append(b'k' + struct.pack('!i', len(key)) + key)
            map_builder.append(_format_binary_recurse(value))
        map_builder.append(b'}')
        return b''.join(map_builder)
    else:
        try:
            return _format_list(list(something))
        except TypeError:
            raise LLSDSerializationError(
                "Cannot serialize unknown type: %s (%s)" %
                (type(something), something))


class HippoLLSDBinaryParser(base_llsd.serde_binary.LLSDBinaryParser):
    def __init__(self):
        super().__init__()
        self._dispatch[ord('u')] = lambda: UUID(bytes=self._getc(16))
        self._dispatch[ord('d')] = self._parse_date

    def _parse_date(self):
        seconds = struct.unpack("<d", self._getc(8))[0]
        try:
            return datetime.datetime.fromtimestamp(seconds, tz=datetime.timezone.utc)
        except OverflowError as exc:
            # A garbage seconds value can cause utcfromtimestamp() to raise
            # OverflowError: timestamp out of range for platform time_t
            self._error(exc, -8)

    def _parse_string(self):
        # LLSD's C++ API lets you stuff binary in a string field even though it's only
        # meant to be allowed in binary fields. Happens in SLM files. Handle that case.
        bytes_val = self._parse_string_raw()
        try:
            return bytes_val.decode('utf-8')
        except UnicodeDecodeError:
            pass
        return bytes_val


# Python uses one, C++ uses the other, and everyone's unhappy.
_BINARY_HEADERS = (b'<? LLSD/Binary ?>', b'<?llsd/binary?>')


def parse_binary(data: bytes):
    if any(data.startswith(x) for x in _BINARY_HEADERS):
        data = data.split(b'\n', 1)[1]
    return HippoLLSDBinaryParser().parse(data)


def parse_xml(data: bytes):
    return base_llsd.parse_xml(data)


def parse_notation(data: bytes):
    return base_llsd.parse_notation(data)


def zip_llsd(val: typing.Any):
    return zlib.compress(format_binary(val, with_header=False), level=zlib.Z_BEST_COMPRESSION)


def unzip_llsd(data: bytes):
    return parse_binary(zlib.decompress(data))


def parse(data: bytes):
    # You always have to content-type sniff because the provided
    # content-type is usually nonsense.
    try:
        data = data.lstrip()
        if any(data.startswith(x) for x in _BINARY_HEADERS):
            return parse_binary(data)
        elif data.startswith(b'<'):
            return parse_xml(data)
        else:
            return parse_notation(data)
    except KeyError as e:
        raise base_llsd.LLSDParseError('LLSD could not be parsed: %s' % (e,))
    except TypeError as e:
        raise base_llsd.LLSDParseError('Input stream not of type bytes. %s' % (e,))
