import typing
import zlib

from llbase.llsd import *
# So we can directly reference the original wrapper funcs where necessary
import llbase.llsd

from hippolyzer.lib.base.datatypes import *


class HippoLLSDBaseFormatter(llbase.llsd.LLSDBaseFormatter):
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


class HippoLLSDXMLFormatter(llbase.llsd.LLSDXMLFormatter, HippoLLSDBaseFormatter):
    def __init__(self):
        super().__init__()


class HippoLLSDXMLPrettyFormatter(llbase.llsd.LLSDXMLPrettyFormatter, HippoLLSDBaseFormatter):
    def __init__(self):
        super().__init__()


def format_pretty_xml(val: typing.Any):
    return HippoLLSDXMLPrettyFormatter().format(val)


def format_xml(val: typing.Any):
    return HippoLLSDXMLFormatter().format(val)


class HippoLLSDNotationFormatter(llbase.llsd.LLSDNotationFormatter, HippoLLSDBaseFormatter):
    def __init__(self):
        super().__init__()


def format_notation(val: typing.Any):
    return HippoLLSDNotationFormatter().format(val)


def format_binary(val: typing.Any, with_header=True):
    val = llbase.llsd.format_binary(val)
    if not with_header:
        return val.split(b"\n", 1)[1]
    return val


class HippoLLSDBinaryParser(llbase.llsd.LLSDBinaryParser):
    def __init__(self):
        super().__init__()
        self._dispatch[ord('u')] = lambda: UUID(bytes=self._getc(16))

    def _parse_string(self):
        # LLSD's C++ API lets you stuff binary in a string field even though it's only
        # meant to be allowed in binary fields. Happens in SLM files. Handle that case.
        bytes_val = self._parse_string_raw()
        try:
            return bytes_val.decode('utf-8')
        except UnicodeDecodeError:
            pass
        return bytes_val


def parse_binary(data: bytes):
    if data.startswith(b'<?llsd/binary?>'):
        data = data.split(b'\n', 1)[1]
    return HippoLLSDBinaryParser().parse(data)


def parse_xml(data: bytes):
    return llbase.llsd.parse_xml(data)


def parse_notation(data: bytes):
    return llbase.llsd.parse_notation(data)


def zip_llsd(val: typing.Any):
    return zlib.compress(format_binary(val, with_header=False))


def unzip_llsd(data: bytes):
    return parse_binary(zlib.decompress(data))


def parse(data: bytes):
    # You always have to content-type sniff because the provided
    # content-type is usually nonsense.
    try:
        data = data.lstrip()
        if data.startswith(b'<?llsd/binary?>'):
            return parse_binary(data)
        elif data.startswith(b'<'):
            return parse_xml(data)
        else:
            return parse_notation(data)
    except KeyError as e:
        raise llbase.llsd.LLSDParseError('LLSD could not be parsed: %s' % (e,))
    except TypeError as e:
        raise llbase.llsd.LLSDParseError('Input stream not of type bytes. %s' % (e,))
