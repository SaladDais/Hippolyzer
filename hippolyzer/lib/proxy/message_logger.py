from __future__ import annotations

import abc
import ast
import collections
import copy
import fnmatch
import gzip
import io
import logging
import pickle
import re
import typing
import weakref

from defusedxml import minidom

from hippolyzer.lib.base import serialization as se, llsd
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.datatypes import TaggedUnion, UUID, TupleCoord
from hippolyzer.lib.base.helpers import bytes_escape
from hippolyzer.lib.base.message.message_formatting import HumanMessageSerializer
from hippolyzer.lib.proxy.message_filter import MetaFieldSpecifier, compile_filter, BaseFilterNode, MessageFilterNode, \
    EnumFieldSpecifier, MatchResult
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.caps import CapType, SerializedCapData

if typing.TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion
    from hippolyzer.lib.proxy.sessions import Session

LOG = logging.getLogger(__name__)


class BaseMessageLogger:
    paused: bool

    def log_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if self.paused:
            return False
        return self.add_log_entry(LLUDPMessageLogEntry(message, region, session))

    def log_http_response(self, flow: HippoHTTPFlow):
        if self.paused:
            return False
        # These are huge, let's not log them for now.
        if flow.cap_data and flow.cap_data.asset_server_cap:
            return False
        return self.add_log_entry(HTTPMessageLogEntry(flow))

    def log_eq_event(self, session: Session, region: ProxiedRegion, event: dict):
        if self.paused:
            return False
        return self.add_log_entry(EQMessageLogEntry(event, region, session))

    @abc.abstractmethod
    def add_log_entry(self, entry: AbstractMessageLogEntry):
        pass


class FilteringMessageLogger(BaseMessageLogger):
    def __init__(self, maxlen=2000):
        BaseMessageLogger.__init__(self)
        self._raw_entries = collections.deque(maxlen=maxlen)
        self._filtered_entries: typing.List[AbstractMessageLogEntry] = []
        self.paused = False
        self.filter: BaseFilterNode = compile_filter("")

    def __iter__(self) -> typing.Iterator[AbstractMessageLogEntry]:
        return iter(self._filtered_entries)

    def set_filter(self, filter_str: str):
        self.filter = compile_filter(filter_str)
        self._begin_reset()
        # Keep any entries that've aged out of the raw entries list that
        # match the new filter
        self._filtered_entries = [
            m for m in self._filtered_entries if
            m not in self._raw_entries and self.filter.match(m)
        ]
        self._filtered_entries.extend((m for m in self._raw_entries if self.filter.match(m)))
        self._end_reset()

    def set_paused(self, paused: bool):
        self.paused = paused

    # Hooks that Qt models will want to implement
    def _begin_insert(self, insert_idx: int):
        pass

    def _end_insert(self):
        pass

    def _begin_reset(self):
        pass

    def _end_reset(self):
        pass

    def add_log_entry(self, entry: AbstractMessageLogEntry):
        try:
            # Paused, throw it away.
            if self.paused:
                return False
            self._raw_entries.append(entry)
            if self.filter.match(entry):
                next_idx = len(self._filtered_entries)
                self._begin_insert(next_idx)
                self._filtered_entries.append(entry)
                self._end_insert()
                return True
        except Exception:
            LOG.exception("Failed to filter queued message")
        return False

    def clear(self):
        self._begin_reset()
        self._filtered_entries.clear()
        self._raw_entries.clear()
        self._end_reset()


class WrappingMessageLogger(BaseMessageLogger):
    def __init__(self):
        self.loggers: typing.List[BaseMessageLogger] = []

    @property
    def paused(self):
        return all(x.paused for x in self.loggers)

    def add_log_entry(self, entry: AbstractMessageLogEntry):
        logged = False
        for logger in self.loggers:
            if logger.add_log_entry(entry):
                logged = True
        # At least one logger ended up keeping the message around, so let's
        # cache the summary before we freeze the message.
        if logged:
            entry.cache_summary()
        entry.freeze()


class AbstractMessageLogEntry(abc.ABC):
    region: typing.Optional[ProxiedRegion]
    session: typing.Optional[Session]
    name: str
    type: str

    __slots__ = ["_region", "_session", "_region_name", "_agent_id", "_summary", "meta"]

    def __init__(self, region: typing.Optional[ProxiedRegion], session: typing.Optional[Session]):
        if region and not isinstance(region, weakref.ReferenceType):
            region = weakref.ref(region)
        if session and not isinstance(session, weakref.ReferenceType):
            session = weakref.ref(session)

        self._region: typing.Optional[weakref.ReferenceType] = region
        self._session: typing.Optional[weakref.ReferenceType] = session
        self._region_name = None
        self._agent_id = None
        self._summary = None
        if self.region:
            self._region_name = self.region.name
        if self.session:
            self._agent_id = self.session.agent_id

        agent_obj = None
        if self.region is not None:
            agent_obj = self.region.objects.lookup_fullid(self.agent_id)
        self.meta = {
            "RegionName": self.region_name,
            "AgentID": self.agent_id,
            "SessionID": self.session.id if self.session else None,
            "AgentLocal": agent_obj.LocalID if agent_obj is not None else None,
            "Method": self.method,
            "Type": self.type,
            "SelectedLocal": self._current_selected_local(),
            "SelectedFull": self._current_selected_full(),
        }

    def to_dict(self) -> dict:
        meta = self.meta.copy()

        def _dehydrate_meta_uuid(key: str):
            if meta[key]:
                meta[key] = str(meta[key])

        _dehydrate_meta_uuid("AgentID")
        _dehydrate_meta_uuid("SelectedFull")
        _dehydrate_meta_uuid("SessionID")

        return {
            "type": self.type,
            "region_name": self.region_name,
            "agent_id": str(self.agent_id) if self.agent_id is not None else None,
            "summary": self.summary,
            "meta": meta,
        }

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, val: dict):
        pass

    def apply_dict(self, val: dict) -> None:
        self._region_name = val['region_name']
        self._agent_id = UUID(val['agent_id']) if val['agent_id'] else None
        self._summary = val['summary']
        meta = val['meta'].copy()

        def _hydrate_meta_uuid(key: str):
            if meta[key]:
                meta[key] = UUID(meta[key])

        _hydrate_meta_uuid("AgentID")
        _hydrate_meta_uuid("SelectedFull")
        _hydrate_meta_uuid("SessionID")
        self.meta.update(meta)

    def freeze(self):
        pass

    def cache_summary(self):
        self._summary = self.summary

    def _current_selected_local(self):
        if self.session:
            return self.session.selected.object_local
        return None

    def _current_selected_full(self):
        selected_local = self._current_selected_local()
        if selected_local is None or self.region is None:
            return None
        obj = self.region.objects.lookup_localid(selected_local)
        return obj and obj.FullID

    def _get_meta(self, name: str) -> typing.Any:
        # Slight difference in semantics. Filters are meant to return the same
        # thing no matter when they're run, so SelectedLocal and friends resolve
        # to the selected items _at the time the message was logged_. To handle
        # the case where we want to match on the selected object at the time the
        # filter is evaluated, we resolve these here.
        if name == "CurrentSelectedLocal":
            return self._current_selected_local()
        elif name == "CurrentSelectedFull":
            return self._current_selected_full()
        return self.meta.get(name)

    @property
    def region(self) -> typing.Optional[ProxiedRegion]:
        if self._region:
            return self._region()
        return None

    @property
    def session(self) -> typing.Optional[Session]:
        if self._session:
            return self._session()
        return None

    @property
    def region_name(self) -> str:
        region = self.region
        if region:
            self._region_name = region.name
            return self._region_name
        # Region may die after a message is logged, need to keep this around.
        if self._region_name:
            return self._region_name

        return ""

    @property
    def agent_id(self) -> typing.Optional[UUID]:
        if self._agent_id:
            return self._agent_id

        session = self.session
        if session:
            self._agent_id = session.agent_id
            return self._agent_id
        return None

    @property
    def host(self) -> str:
        region_name = self.region_name
        if not region_name:
            return ""
        session_str = ""
        agent_id = self.agent_id
        if agent_id:
            session_str = f" ({agent_id})"
        return region_name + session_str

    def request(self, beautify=False, replacements=None):
        return None

    def response(self, beautify=False):
        return None

    def _packet_root_matches(self, pattern):
        if fnmatch.fnmatchcase(self.name, pattern):
            return True
        if fnmatch.fnmatchcase(self.type, pattern):
            return True
        return False

    def _val_matches(self, operator, val, expected):
        if isinstance(expected, MetaFieldSpecifier):
            if len(expected) != 1:
                raise ValueError(f"Can only support single-level Meta specifiers, not {expected!r}")
            expected = self._get_meta(str(expected[0]))
            if not isinstance(expected, (int, float, bytes, str, type(None), tuple)):
                if callable(expected):
                    expected = expected()
                else:
                    expected = str(expected)
        elif isinstance(expected, EnumFieldSpecifier):
            # Local import so we get a fresh copy of the templates module
            from hippolyzer.lib.proxy import templates
            enum_cls = getattr(templates, expected.enum_name)
            expected = enum_cls[expected.field_name]
        elif expected is not None:
            # Unbox the expected value
            expected = expected.value
        if not isinstance(val, (int, float, bytes, str, type(None), tuple, TupleCoord)):
            val = str(val)

        if not operator:
            return bool(val)
        elif operator == "==":
            return val == expected
        elif operator == "!=":
            return val != expected
        elif operator == "^=":
            if val is None:
                return False
            return val.startswith(expected)
        elif operator == "$=":
            if val is None:
                return False
            return val.endswith(expected)
        elif operator == "~=":
            if val is None:
                return False
            return expected in val
        elif operator == "<":
            return val < expected
        elif operator == "<=":
            return val <= expected
        elif operator == ">":
            return val > expected
        elif operator == ">=":
            return val >= expected
        elif operator == "&":
            return val & expected
        else:
            raise ValueError(f"Unexpected operator {operator!r}")

    def _base_matches(self, matcher: "MessageFilterNode") -> typing.Optional[bool]:
        if len(matcher.selector) == 1:
            # Comparison operators would make no sense here
            if matcher.value or matcher.operator:
                return False
            return self._packet_root_matches(matcher.selector[0])
        if matcher.selector[0] == "Meta":
            if len(matcher.selector) == 2:
                return self._val_matches(matcher.operator, self._get_meta(matcher.selector[1]), matcher.value)
            elif len(matcher.selector) == 3:
                meta_dict = self._get_meta(matcher.selector[1])
                if not meta_dict or not hasattr(meta_dict, 'get'):
                    return False
                return self._val_matches(matcher.operator, meta_dict.get(matcher.selector[2]), matcher.value)
        return None

    def matches(self, matcher: "MessageFilterNode", short_circuit=True) -> "MatchResult":
        return MatchResult(self._base_matches(matcher) or False, [])

    @property
    def seq(self):
        return ""

    @property
    def method(self):
        return ""

    @property
    def summary(self):
        return ""

    @staticmethod
    def _format_llsd(parsed):
        xmlified = llsd.format_pretty_xml(parsed)
        # dedent <key> by 1 for easier visual scanning
        xmlified = re.sub(rb" <key>", b"<key>", xmlified)
        return xmlified.decode("utf8", errors="replace")

    @staticmethod
    def _format_xml(content):
        beautified = minidom.parseString(content).toprettyxml(indent="  ")
        # kill blank lines. will break cdata sections. meh.
        beautified = re.sub(r'\n\s*\n', '\n', beautified, flags=re.MULTILINE)
        return re.sub(r'<([\w]+)>\s*</\1>', r'<\1></\1>',
                      beautified, flags=re.MULTILINE)


class HTTPMessageLogEntry(AbstractMessageLogEntry):
    __slots__ = ["flow"]

    def __init__(self, flow: HippoHTTPFlow):
        self.flow: HippoHTTPFlow = flow
        cap_data = self.flow.cap_data
        region = cap_data and cap_data.region
        session = cap_data and cap_data.session

        super().__init__(region, session)
        # This was a request the proxy made through itself
        self.meta["Synthetic"] = flow.request_injected

    @property
    def type(self):
        return "HTTP"

    @property
    def name(self):
        cap_data = self.flow.cap_data
        name = cap_data and cap_data.cap_name
        if name:
            return name
        return self.flow.request.url

    @property
    def method(self):
        return self.flow.request.method

    def _format_http_message(self, want_request, beautify):
        message = self.flow.request if want_request else self.flow.response
        method = self.flow.request.method
        buf = io.StringIO()
        cap_data = self.flow.cap_data
        cap_name = cap_data and cap_data.cap_name
        base_url = cap_name and cap_data.base_url
        temporary_cap = cap_data and cap_data.type == CapType.TEMPORARY
        beautify_url = (beautify and base_url and cap_name
                        and not temporary_cap and self.session and want_request)
        if want_request:
            buf.write(message.method)
            buf.write(" ")
            if beautify_url:
                buf.write(f"[[{cap_name}]]{message.url[len(base_url):]}")
            else:
                buf.write(message.url)
            buf.write(" ")
            buf.write(message.http_version)
        else:
            buf.write(message.http_version)
            buf.write(" ")
            buf.write(str(message.status_code))
            buf.write(" ")
            buf.write(message.reason)
        buf.write("\r\n")
        if beautify_url:
            buf.write("# ")
            buf.write(message.url)
            buf.write("\r\n")

        headers = copy.deepcopy(message.headers)
        for key in tuple(headers.keys()):
            if key.lower().startswith("x-hippo-"):
                LOG.warning(f"Internal header {key!r} leaked out?")
                # If this header actually came from somewhere untrusted, we can't
                # include it. It may change the meaning of the message when replayed.
                headers[f"X-Untrusted-{key}"] = headers[key]
                headers.pop(key)
        beautified = None
        if beautify and message.content:
            try:
                serializer = se.HTTP_SERIALIZERS.get(cap_name)
                if serializer:
                    if want_request:
                        beautified = serializer.deserialize_req_body(method, message.content)
                    else:
                        beautified = serializer.deserialize_resp_body(method, message.content)

                    if beautified is se.UNSERIALIZABLE:
                        beautified = None
                    else:
                        beautified = self._format_llsd(beautified)
                        headers["X-Hippo-Beautify"] = "1"

                if not beautified:
                    content_type = self._guess_content_type(message)
                    if content_type.startswith("application/llsd"):
                        try:
                            beautified = self._format_llsd(llsd.parse(message.content))
                        except llsd.LLSDParseError:
                            # Sometimes LL sends plain XML with a Content-Type of application/llsd+xml.
                            # Try to detect that case and work around it
                            if content_type == "application/llsd+xml" and message.content.startswith(b'<'):
                                beautified = self._format_xml(message.content)
                            else:
                                raise
                    elif any(content_type.startswith(x) for x in ("application/xml", "text/xml")):
                        beautified = self._format_xml(message.content)
            except:
                LOG.exception("Failed to beautify message")

        message_body = beautified or message.content
        if isinstance(message_body, bytes):
            try:
                decoded = message.text
                # Valid in many codecs, but unprintable.
                if "\x00" in decoded:
                    raise ValueError("Embedded null")
                message_body = decoded
            except (UnicodeError, ValueError):
                # non-printable characters, return the escaped version.
                headers["X-Hippo-Escaped-Body"] = "1"
                message_body = bytes_escape(message_body).decode("utf8")

        buf.write(bytes(headers).decode("utf8", errors="replace"))
        buf.write("\r\n")

        buf.write(message_body)
        return buf.getvalue()

    def request(self, beautify=False, replacements=None):
        return self._format_http_message(want_request=True, beautify=beautify)

    def response(self, beautify=False):
        return self._format_http_message(want_request=False, beautify=beautify)

    @property
    def summary(self):
        if self._summary is not None:
            return self._summary
        msg = self.flow.response
        self._summary = f"{msg.status_code}: "
        if not msg.content:
            return self._summary
        if len(msg.content) > 1000000:
            self._summary += "[too large...]"
            return self._summary
        content_type = self._guess_content_type(msg)
        if content_type.startswith("application/llsd"):
            notation = llsd.format_notation(llsd.parse(msg.content))
            self._summary += notation.decode("utf8")[:500]
        return self._summary

    def _guess_content_type(self, message):
        content_type = message.headers.get("Content-Type", "")
        if not message.content or content_type.startswith("application/llsd"):
            return content_type
        # Sometimes gets sent with `text/plain` or `text/html`. Cool.
        if message.content.startswith(rb'<?xml version="1.0" ?><llsd>'):
            return "application/llsd+xml"
        if message.content.startswith(rb'<llsd>'):
            return "application/llsd+xml"
        if message.content.startswith(rb'<?xml '):
            return "application/xml"
        return content_type

    def _get_meta(self, name: str) -> typing.Any:
        lower_name = name.lower()
        if lower_name == "url":
            return self.flow.request.url
        elif lower_name == "reqheaders":
            return self.flow.request.headers
        elif lower_name == "respheaders":
            return self.flow.response.headers
        elif lower_name == "host":
            return self.flow.request.host.lower()
        elif lower_name == "status":
            return self.flow.response.status_code
        return super()._get_meta(name)

    def to_dict(self):
        val = super().to_dict()
        val['flow'] = self.flow.get_state()
        cap_data = val['flow'].get('metadata', {}).get('cap_data_ser')
        if cap_data is not None:
            # Have to convert this from a namedtuple to a dict to make
            # it importable
            cap_dict = cap_data._asdict()  # noqa
            val['flow']['metadata']['cap_data_ser'] = cap_dict
        return val

    @classmethod
    def from_dict(cls, val: dict):
        cap_data = val['flow'].get('metadata', {}).get('cap_data_ser')
        if cap_data:
            val['flow']['metadata']['cap_data_ser'] = SerializedCapData(**cap_data)
        ev = cls(HippoHTTPFlow.from_state(val['flow'], None))
        ev.apply_dict(val)
        return ev


class EQMessageLogEntry(AbstractMessageLogEntry):
    __slots__ = ["event"]

    def __init__(self, event, region, session):
        super().__init__(region, session)
        self.event = event

    @property
    def type(self):
        return "EQ"

    def request(self, beautify=False, replacements=None):
        return f'EQ {self.event["message"]}\n\n{self._format_llsd(self.event["body"])}'

    @property
    def name(self):
        return self.event["message"]

    @property
    def summary(self):
        if self._summary is not None:
            return self._summary
        self._summary = ""
        self._summary = llsd.format_notation(self.event["body"]).decode("utf8")[:500]
        return self._summary

    def to_dict(self) -> dict:
        val = super().to_dict()
        val['event'] = llsd.format_notation(self.event)
        return val

    @classmethod
    def from_dict(cls, val: dict):
        ev = cls(llsd.parse_notation(val['event']), None, None)
        ev.apply_dict(val)
        return ev


class LLUDPMessageLogEntry(AbstractMessageLogEntry):
    __slots__ = ["_message", "_name", "_direction", "_frozen_message", "_seq", "_deserializer"]

    def __init__(self, message: Message, region, session):
        self._message: Message = message
        self._deserializer = None
        self._name = message.name
        self._direction = message.direction
        self._frozen_message: typing.Optional[bytes] = None
        self._seq = message.packet_id
        super().__init__(region, session)

    _MESSAGE_META_ATTRS = {
        "Synthetic", "Dropped", "Extra", "Resent", "Zerocoded", "Acks", "Reliable",
    }

    def _get_meta(self, name: str):
        # These may change between when the message is logged and when we
        # actually filter on it, since logging happens before addons.
        msg = self.message
        if name in self._MESSAGE_META_ATTRS:
            return getattr(msg, name.lower(), None)
        msg_meta = getattr(msg, "meta", None)
        if msg_meta is not None:
            if name in msg_meta:
                return msg_meta[name]
        return super()._get_meta(name)

    @property
    def message(self) -> Message:
        if self._message:
            return self._message
        elif self._frozen_message:
            message = pickle.loads(self._frozen_message)
            message.deserializer = self._deserializer
            return message
        else:
            raise ValueError("Didn't have a fresh or frozen message somehow")

    def freeze(self):
        message = self.message
        message.invalidate_caches()
        # These are expensive to keep around. pickle them and un-pickle on
        # an as-needed basis.
        self._deserializer = self.message.deserializer
        message.deserializer = None
        try:
            self._frozen_message = pickle.dumps(self._message, protocol=pickle.HIGHEST_PROTOCOL)
        finally:
            message.deserializer = self._deserializer
        self._message = None

    @property
    def type(self):
        return "LLUDP"

    @property
    def name(self):
        if self._message:
            self._name = self._message.name
        return self._name

    @property
    def method(self):
        if self._message:
            self._direction = self._message.direction
        return self._direction.name if self._direction is not None else ""

    def request(self, beautify=False, replacements=None):
        return HumanMessageSerializer.to_human_string(self.message, replacements, beautify)

    def matches(self, matcher, short_circuit=True) -> "MatchResult":
        base_matched = self._base_matches(matcher)
        if base_matched is not None:
            return MatchResult(base_matched, [])

        if not self._packet_root_matches(matcher.selector[0]):
            return MatchResult(False, [])

        message = self.message

        selector_len = len(matcher.selector)
        # name, block_name, var_name(, subfield_name)?
        if selector_len not in (3, 4):
            return MatchResult(False, [])
        found_field_keys = []
        for block_name in message.blocks:
            if not fnmatch.fnmatchcase(block_name, matcher.selector[1]):
                continue
            for block_num, block in enumerate(message[block_name]):
                for var_name in block.vars.keys():
                    if not fnmatch.fnmatchcase(var_name, matcher.selector[2]):
                        continue
                    # So we know where the match happened
                    field_key = (message.name, block_name, block_num, var_name)
                    if selector_len == 3:
                        # We're just matching on the var existing, not having any particular value
                        if matcher.value is None:
                            found_field_keys.append(field_key)
                        elif self._val_matches(matcher.operator, block[var_name], matcher.value):
                            found_field_keys.append(field_key)
                    # Need to invoke a special unpacker
                    elif selector_len == 4:
                        try:
                            deserialized = block.deserialize_var(var_name)
                        except KeyError:
                            continue
                        # Discard the tag if this is a tagged union, we only want the value
                        if isinstance(deserialized, TaggedUnion):
                            deserialized = deserialized.value
                        if not isinstance(deserialized, dict):
                            continue
                        for key in deserialized.keys():
                            if fnmatch.fnmatchcase(str(key), matcher.selector[3]):
                                if matcher.value is None:
                                    # Short-circuiting checking individual subfields is fine since
                                    # we only highlight fields anyway.
                                    found_field_keys.append(field_key)
                                    break
                                elif self._val_matches(matcher.operator, deserialized[key], matcher.value):
                                    found_field_keys.append(field_key)
                                    break

                    if short_circuit and found_field_keys:
                        return MatchResult(True, found_field_keys)
        return MatchResult(bool(found_field_keys), found_field_keys)

    @property
    def summary(self):
        if self._summary is None:
            self._summary = self.message.to_summary()[:500]
        return self._summary

    @property
    def seq(self):
        if self._message:
            self._seq = self._message.packet_id
        return self._seq

    def to_dict(self):
        val = super().to_dict()
        val['message'] = llsd.format_notation(self.message.to_dict(extended=True))
        return val

    @classmethod
    def from_dict(cls, val: dict):
        ev = cls(Message.from_dict(llsd.parse_notation(val['message'])), None, None)
        ev.apply_dict(val)
        return ev


def export_log_entries(entries: typing.Iterable[AbstractMessageLogEntry]) -> bytes:
    return gzip.compress(repr([e.to_dict() for e in entries]).encode("utf8"))


_TYPE_CLASSES = {
    "HTTP": HTTPMessageLogEntry,
    "LLUDP": LLUDPMessageLogEntry,
    "EQ": EQMessageLogEntry,
}


def import_log_entries(data: bytes) -> typing.List[AbstractMessageLogEntry]:
    entries = ast.literal_eval(gzip.decompress(data).decode("utf8"))
    return [_TYPE_CLASSES[e['type']].from_dict(e) for e in entries]
