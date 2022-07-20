from __future__ import annotations

import logging
import hashlib
import uuid
import weakref
from typing import *
import urllib.parse

import multidict

from hippolyzer.lib.base.datatypes import Vector3, UUID
from hippolyzer.lib.base.helpers import proxify
from hippolyzer.lib.base.message.llsd_msg_serializer import LLSDMessageSerializer
from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.objects import handle_to_global_pos
from hippolyzer.lib.client.state import BaseClientRegion
from hippolyzer.lib.proxy.caps_client import ProxyCapsClient
from hippolyzer.lib.proxy.circuit import ProxiedCircuit
from hippolyzer.lib.proxy.caps import CapType
from hippolyzer.lib.proxy.object_manager import ProxyObjectManager
from hippolyzer.lib.base.transfer_manager import TransferManager
from hippolyzer.lib.base.xfer_manager import XferManager

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.sessions import Session
    from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow


class CapsMultiDict(multidict.MultiDict[Tuple[CapType, str]]):
    # TODO: Make a view object for this that's just name -> URL
    #  deriving from MultiMapping[_T] so we don't have to do
    #  so many copies for consumers that aren't expecting the
    #  CapType tag.
    def add(self, key, value) -> None:
        # Prepend rather than append when adding caps.
        # Necessary so the most recent for a region URI is returned
        # when doing lookups by name.
        vals = [value] + self.popall(key, [])
        for val in vals:
            super().add(key, val)


class ProxiedRegion(BaseClientRegion):
    def __init__(self, circuit_addr, seed_cap: str, session: Session, handle=None):
        # A client may make a Seed request twice, and may get back two (valid!) sets of
        # Cap URIs. We need to be able to look up both, so MultiDict is necessary.
        self.handle: Optional[int] = handle
        self._name: Optional[str] = None
        # TODO: when does this change?
        self.cache_id: Optional[UUID] = None
        self.circuit: Optional[ProxiedCircuit] = None
        self.circuit_addr = circuit_addr
        self.caps = CapsMultiDict()
        # Reverse lookup for URL -> cap data
        self._caps_url_lookup: Dict[str, Tuple[CapType, str]] = {}
        if seed_cap:
            self.caps["Seed"] = (CapType.NORMAL, seed_cap)
        self.session: Callable[[], Session] = weakref.ref(session)
        self.message_handler: MessageHandler[Message, str] = MessageHandler()
        self.http_message_handler: MessageHandler[HippoHTTPFlow, str] = MessageHandler()
        self.eq_manager = EventQueueManager(self)
        settings = session.session_manager.settings
        self.caps_client = ProxyCapsClient(settings, proxify(self))
        self.objects: ProxyObjectManager = ProxyObjectManager(self, may_use_vo_cache=True)
        self.xfer_manager = XferManager(proxify(self), self.session().secure_session_id)
        self.transfer_manager = TransferManager(proxify(self), session.agent_id, session.id)
        self._recalc_caps()

    @property
    def name(self):
        if self._name:
            return self._name
        return "Pending %r" % (self.circuit_addr,)

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def cap_urls(self) -> multidict.MultiDict[str, str]:
        return multidict.MultiDict((x, y[1]) for x, y in self.caps.items())

    @property
    def global_pos(self) -> Vector3:
        if self.handle is None:
            raise ValueError("Can't determine global region position without handle")
        return handle_to_global_pos(self.handle)

    @property
    def is_alive(self):
        if not self.circuit:
            return False
        return self.circuit.is_alive

    def update_caps(self, caps: Mapping[str, str]):
        for cap_name, cap_url in caps.items():
            if isinstance(cap_url, str) and cap_url.startswith('http'):
                self.caps.add(cap_name, (CapType.NORMAL, cap_url))
                self._recalc_caps()

    def _recalc_caps(self):
        self._caps_url_lookup.clear()
        for name, cap_info in self.caps.items():
            cap_type, cap_url = cap_info
            self._caps_url_lookup[cap_url] = (cap_type, name)

    def register_wrapper_cap(self, name: str):
        """
        Wrap an existing, non-unique cap with a unique URL

        caps like ViewerAsset may be the same globally and wouldn't let us infer
        which session / region the request was related to without a wrapper URL
        that we inject into the seed response sent to the viewer.
        """
        parsed = list(urllib.parse.urlsplit(self.caps[name][1]))
        seed_id = self.caps["Seed"][1].split("/")[-1].encode("utf8")
        # Give it a unique domain tied to the current Seed URI
        parsed[1] = f"{name.lower()}-{hashlib.sha256(seed_id).hexdigest()[:16]}.hippo-proxy.localhost"
        # Force the URL to HTTP, we're going to handle the request ourselves so it doesn't need
        # to be secure. This should save on expensive TLS context setup for each req.
        parsed[0] = "http"
        wrapper_url = urllib.parse.urlunsplit(parsed)
        # Register it with "ProxyWrapper" appended so we don't shadow the real cap URL
        # in our own view of the caps
        self.register_cap(name + "ProxyWrapper", wrapper_url, CapType.WRAPPER)
        return wrapper_url

    def register_proxy_cap(self, name: str):
        """Register a cap to be completely handled by the proxy"""
        if name in self.caps:
            # If we have an existing cap then we should just use that.
            cap_data = self.caps[name]
            if cap_data[1] == CapType.PROXY_ONLY:
                return cap_data[0]
        cap_url = f"http://{uuid.uuid4()!s}.caps.hippo-proxy.localhost"
        self.register_cap(name, cap_url, CapType.PROXY_ONLY)
        return cap_url

    def register_cap(self, name: str, cap_url: str, cap_type: CapType = CapType.NORMAL):
        self.caps.add(name, (cap_type, cap_url))
        self._recalc_caps()

    def resolve_cap(self, url: str, consume=True) -> Optional[Tuple[str, str, CapType]]:
        for cap_url in self._caps_url_lookup.keys():
            if url.startswith(cap_url):
                cap_type, name = self._caps_url_lookup[cap_url]
                if cap_type == CapType.TEMPORARY and consume:
                    # Resolving a temporary cap pops it out of the dict
                    temporary_caps = self.caps.popall(name)
                    temporary_caps.remove((cap_type, cap_url))
                    self.caps.extend((name, x) for x in temporary_caps)
                    self._recalc_caps()
                return name, cap_url, cap_type
        return None

    def mark_dead(self):
        logging.info("Marking %r dead" % self)
        if self.circuit:
            self.circuit.is_alive = False
        self.objects.clear()
        self.eq_manager.clear()

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.name)


class EventQueueManager:
    def __init__(self, region: ProxiedRegion):
        # TODO: Per-EQ InjectionTracker so we can inject fake responses on 499
        self._queued_events = []
        self._region = weakref.proxy(region)
        self._last_ack: Optional[int] = None
        self._last_payload: Optional[Any] = None
        self.llsd_message_serializer = LLSDMessageSerializer()

    def inject_message(self, message: Message):
        self.inject_event(self.llsd_message_serializer.serialize(message, True))

    def inject_event(self, event: dict):
        self._queued_events.append(event)
        if self._region:
            circuit: ProxiedCircuit = self._region.circuit
            session: Session = self._region.session()
            # Inject an outbound PlacesQuery message so we can trigger an inbound PlacesReply
            # over the EQ. That will allow us to shove our own event onto the response once it comes in,
            # otherwise we have to wait until the EQ legitimately returns 200 due to a new event.
            # May or may not work in OpenSim.
            circuit.send_message(Message(
                'PlacesQuery',
                Block('AgentData', AgentID=session.agent_id, SessionID=session.id, QueryID=UUID()),
                Block('TransactionData', TransactionID=UUID()),
                Block('QueryData', QueryText=b'', QueryFlags=64, Category=-1, SimName=b''),
            ))

    def take_injected_events(self):
        events = self._queued_events
        self._queued_events = []
        return events

    def cache_last_poll_response(self, req_ack: int, payload: Any):
        self._last_ack = req_ack
        self._last_payload = payload

    def get_cached_poll_response(self, req_ack: Optional[int]) -> Optional[Any]:
        if self._last_ack == req_ack:
            return self._last_payload
        return None

    def clear(self):
        self._queued_events.clear()
        self._last_ack = None
        self._last_payload = None
