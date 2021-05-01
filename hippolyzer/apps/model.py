import collections
import codecs
import copy
import enum
import fnmatch
import io
import logging
import pickle
import queue
import re
import typing
import weakref

from defusedxml import minidom
from PySide2 import QtCore, QtGui

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import *
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.region import ProxiedRegion, CapType
import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.sessions import Session, BaseMessageLogger

from .message_filter import compile_filter, BaseFilterNode, MessageFilterNode, MetaFieldSpecifier

LOG = logging.getLogger(__name__)


def bytes_unescape(val: bytes) -> bytes:
    # Only in CPython. bytes -> bytes with escape decoding.
    # https://stackoverflow.com/a/23151714
    return codecs.escape_decode(val)[0]  # type: ignore


def bytes_escape(val: bytes) -> bytes:
    # Try to keep newlines as-is
    return re.sub(rb"(?<!\\)\\n", b"\n", codecs.escape_encode(val)[0])  # type: ignore


class MessageLogHeader(enum.IntEnum):
    Host = 0
    Type = enum.auto()
    Method = enum.auto()
    Name = enum.auto()
    Summary = enum.auto()


class AbstractMessageLogEntry:
    region: typing.Optional[ProxiedRegion]
    session: typing.Optional[Session]
    name: str
    type: str

    __slots__ = ["_region", "_session", "_region_name", "_agent_id", "_summary", "meta"]

    def __init__(self, region, session):
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

    def _get_meta(self, name: str):
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
            expected = self._get_meta(str(expected))
            if not isinstance(expected, (int, float, bytes, str, type(None), tuple)):
                if callable(expected):
                    expected = expected()
                else:
                    expected = str(expected)
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
        else:
            raise ValueError(f"Unexpected operator {operator!r}")

    def _base_matches(self, matcher: "MessageFilterNode") -> typing.Optional[bool]:
        if len(matcher.selector) == 1:
            # Comparison operators would make no sense here
            if matcher.value or matcher.operator:
                return False
            return self._packet_root_matches(matcher.selector[0])
        if len(matcher.selector) == 2 and matcher.selector[0] == "Meta":
            return self._val_matches(matcher.operator, self._get_meta(matcher.selector[1]), matcher.value)
        return None

    def matches(self, matcher: "MessageFilterNode"):
        return self._base_matches(matcher) or False

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


class LLUDPMessageLogEntry(AbstractMessageLogEntry):
    __slots__ = ["_message", "_name", "_direction", "_frozen_message", "_seq", "_deserializer"]

    def __init__(self, message: ProxiedMessage, region, session):
        self._message: ProxiedMessage = message
        self._deserializer = None
        self._name = message.name
        self._direction = message.direction
        self._frozen_message: typing.Optional[bytes] = None
        self._seq = message.packet_id
        super().__init__(region, session)

    _MESSAGE_META_ATTRS = {
        "Injected", "Dropped", "Extra", "Resent", "Zerocoded", "Acks", "Reliable",
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
    def message(self):
        if self._message:
            return self._message
        elif self._frozen_message:
            message = pickle.loads(self._frozen_message)
            message.deserializer = self._deserializer
            return message
        else:
            raise ValueError("Didn't have a fresh or frozen message somehow")

    def freeze(self):
        self.message.invalidate_caches()
        # These are expensive to keep around. pickle them and un-pickle on
        # an as-needed basis.
        self._deserializer = self.message.deserializer
        self.message.deserializer = None
        self._frozen_message = pickle.dumps(self._message, protocol=pickle.HIGHEST_PROTOCOL)
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
        return self.message.to_human_string(replacements, beautify)

    def matches(self, matcher):
        base_matched = self._base_matches(matcher)
        if base_matched is not None:
            return base_matched

        if not self._packet_root_matches(matcher.selector[0]):
            return False

        message = self.message

        selector_len = len(matcher.selector)
        # name, block_name, var_name(, subfield_name)?
        if selector_len not in (3, 4):
            return False
        for block_name in message.blocks:
            if not fnmatch.fnmatchcase(block_name, matcher.selector[1]):
                continue
            for block in message[block_name]:
                for var_name in block.vars.keys():
                    if not fnmatch.fnmatchcase(var_name, matcher.selector[2]):
                        continue
                    if selector_len == 3:
                        if matcher.value is None:
                            return True
                        if self._val_matches(matcher.operator, block[var_name], matcher.value):
                            return True
                    elif selector_len == 4:
                        try:
                            deserialized = block.deserialize_var(var_name)
                        except KeyError:
                            continue
                        # Discard the tag if this is a tagged union, we only want the value
                        if isinstance(deserialized, TaggedUnion):
                            deserialized = deserialized.value
                        if not isinstance(deserialized, dict):
                            return False
                        for key in deserialized.keys():
                            if fnmatch.fnmatchcase(str(key), matcher.selector[3]):
                                if matcher.value is None:
                                    return True
                                if self._val_matches(matcher.operator, deserialized[key], matcher.value):
                                    return True

        return False

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


class EQMessageLogEntry(AbstractMessageLogEntry):
    __slots__ = ["event"]

    def __init__(self, event, region, session):
        super().__init__(region, session)
        self.event = event

    @property
    def type(self):
        return "EQ"

    def request(self, beautify=False, replacements=None):
        return self._format_llsd(self.event["body"])

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


class HTTPMessageLogEntry(AbstractMessageLogEntry):
    __slots__ = ["flow"]

    def __init__(self, flow: HippoHTTPFlow):
        self.flow: HippoHTTPFlow = flow
        cap_data = self.flow.cap_data
        region = cap_data and cap_data.region
        session = cap_data and cap_data.session

        super().__init__(region, session)
        # This was a request the proxy made through itself
        self.meta["Injected"] = flow.request_injected

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
        beautify_url = (beautify and base_url and cap_name and
                        not temporary_cap and self.session and want_request)
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
                        beautified = self._format_llsd(llsd.parse(message.content))
                    elif any(content_type.startswith(x) for x in ("application/xml", "text/xml")):
                        beautified = minidom.parseString(message.content).toprettyxml(indent="  ")
                        # kill blank lines. will break cdata sections. meh.
                        beautified = re.sub(r'\n\s*\n', '\n', beautified, flags=re.MULTILINE)
                        beautified = re.sub(r'<([\w]+)>\s*</\1>', r'<\1></\1>',
                                            beautified, flags=re.MULTILINE)
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


class MessageLogModel(QtCore.QAbstractTableModel, BaseMessageLogger):
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        BaseMessageLogger.__init__(self)
        self._raw_entries = collections.deque(maxlen=2000)
        self._queued_entries = queue.Queue()
        self._filtered_entries = []
        self._paused = False
        self.filter: typing.Optional[BaseFilterNode] = None

    def setFilter(self, filter_str: str):
        self.filter = compile_filter(filter_str)
        self.beginResetModel()
        # Keep any entries that've aged out of the raw entries list that
        # match the new filter
        self._filtered_entries = [
            m for m in self._filtered_entries if
            m not in self._raw_entries and self.filter.match(m)
        ]
        self._filtered_entries.extend((m for m in self._raw_entries if self.filter.match(m)))
        self.endResetModel()

    def setPaused(self, paused: bool):
        self._paused = paused

    def log_lludp_message(self, session: Session, region: ProxiedRegion, message: ProxiedMessage):
        if self._paused:
            return
        self.queueLogEntry(LLUDPMessageLogEntry(message, region, session))

    def log_http_response(self, flow: HippoHTTPFlow):
        if self._paused:
            return
        # These are huge, let's not log them for now.
        if flow.cap_data and flow.cap_data.asset_server_cap:
            return
        self.queueLogEntry(HTTPMessageLogEntry(flow))

    def log_eq_event(self, session: Session, region: ProxiedRegion, event: dict):
        if self._paused:
            return
        self.queueLogEntry(EQMessageLogEntry(event, region, session))

    def appendQueuedEntries(self):
        while not self._queued_entries.empty():
            entry: AbstractMessageLogEntry = self._queued_entries.get(block=False)
            # Paused, throw it away.
            if self._paused:
                continue
            self._raw_entries.append(entry)
            try:
                if self.filter.match(entry):
                    next_idx = len(self._filtered_entries)
                    self.beginInsertRows(QtCore.QModelIndex(), next_idx, next_idx)
                    self._filtered_entries.append(entry)
                    self.endInsertRows()

                    entry.cache_summary()
                # In the common case we don't need to keep around the serialization
                # caches anymore. If the filter changes, the caches will be repopulated
                # as necessary.
                entry.freeze()
            except Exception:
                LOG.exception("Failed to filter queued message")

    def queueLogEntry(self, entry: AbstractMessageLogEntry):
        self._queued_entries.put(entry, block=False)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._filtered_entries)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(MessageLogHeader)

    def data(self, index, role=None):
        if not index.isValid():
            return None
        entry = self._filtered_entries[index.row()]
        if role == QtCore.Qt.UserRole:
            return entry
        if role != QtCore.Qt.DisplayRole:
            return None

        col = index.column()
        val = None

        if col == MessageLogHeader.Host:
            val = entry.host
        elif col == MessageLogHeader.Method:
            val = entry.method
        elif col == MessageLogHeader.Type:
            val = entry.type
        elif col == MessageLogHeader.Name:
            val = entry.name
        elif col == MessageLogHeader.Summary:
            val = entry.summary
        return val

    def headerData(self, col, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return MessageLogHeader(col).name

    def clear(self):
        self.beginResetModel()
        self._filtered_entries.clear()
        while not self._queued_entries.empty():
            self._queued_entries.get(block=False)
        self._raw_entries.clear()
        self.endResetModel()


class RegionListModel(QtCore.QAbstractListModel):
    def __init__(self, parent, session_manager):
        super().__init__(parent)
        self.sessionManager = session_manager
        session_manager.regionAdded.connect(self.regionAdded)
        session_manager.regionRemoved.connect(self.regionRemoved)
        self.regions: typing.List[ProxiedRegion] = session_manager.all_regions

    @QtCore.Slot(ProxiedRegion)  # noqa
    def regionAdded(self, region: ProxiedRegion):
        if region in self.regions:
            return

        num_regions = len(self.regions)
        self.beginInsertRows(QtCore.QModelIndex(), num_regions, num_regions)
        self.regions.append(region)
        self.endInsertRows()

    @QtCore.Slot(ProxiedRegion)  # noqa
    def regionRemoved(self, region: ProxiedRegion):
        try:
            region_idx = self.regions.index(region)
        except ValueError:
            return

        self.beginRemoveRows(QtCore.QModelIndex(), region_idx, region_idx)
        self.regions.remove(region)
        self.endRemoveRows()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.regions)

    def columnCount(self, parent: QtCore.QModelIndex) -> int:
        return 1

    def data(self, index, role=None):
        if not index.isValid():
            return None
        cur_region = self.regions[index.row()]
        if role == QtCore.Qt.UserRole:
            return cur_region
        elif role == QtCore.Qt.FontRole:
            for session in self.sessionManager.sessions:
                if cur_region == session.main_region:
                    font = QtGui.QFont()
                    font.setBold(True)
                    # Main region in "default" session
                    if session == self.sessionManager.sessions[-1]:
                        font.setItalic(True)
                    return font
        if role != QtCore.Qt.DisplayRole:
            return None

        col = index.column()
        val = None

        if col == 0:
            if cur_region and cur_region.session():
                val = f"{cur_region.name} ({cur_region.session().agent_id})"
            # Can happen if the weakref becomes invalid
            else:
                val = "<Dead Region>"
        return val

    def headerData(self, col, orientation, role=None):
        return None

    def clear(self):
        self.beginResetModel()
        self.regions = []
        self.endResetModel()