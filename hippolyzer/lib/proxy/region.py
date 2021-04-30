from __future__ import annotations

import enum
import logging
import hashlib
import uuid
import weakref
from typing import *
import urllib.parse

import multidict

from hippolyzer.lib.base.datatypes import Vector3
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.proxy.caps_client import CapsClient
from hippolyzer.lib.proxy.circuit import ProxiedCircuit
from hippolyzer.lib.proxy.objects import ObjectManager
from hippolyzer.lib.proxy.transfer_manager import TransferManager
from hippolyzer.lib.proxy.xfer_manager import XferManager

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.sessions import Session
    from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
    from hippolyzer.lib.proxy.message import ProxiedMessage


class CapType(enum.Enum):
    NORMAL = enum.auto()
    TEMPORARY = enum.auto()
    WRAPPER = enum.auto()
    PROXY_ONLY = enum.auto()


class CapsMultiDict(multidict.MultiDict[Tuple[CapType, str]]):
    def add(self, key, value) -> None:
        # Prepend rather than append when adding caps.
        # Necessary so the most recent for a region URI is returned
        # when doing lookups by name.
        vals = [value] + self.popall(key, [])
        for val in vals:
            super().add(key, val)


class ProxiedRegion:
    def __init__(self, circuit_addr, seed_cap: str, session, handle=None):
        # A client may make a Seed request twice, and may get back two (valid!) sets of
        # Cap URIs. We need to be able to look up both, so MultiDict is necessary.
        self.handle: Optional[int] = handle
        self._name: Optional[str] = None
        self.circuit: Optional[ProxiedCircuit] = None
        self.circuit_addr = circuit_addr
        self._caps = CapsMultiDict()
        if seed_cap:
            self._caps["Seed"] = (CapType.NORMAL, seed_cap)
        self.session: Optional[Callable[[], Session]] = weakref.ref(session)
        self.message_handler: MessageHandler[ProxiedMessage] = MessageHandler()
        self.http_message_handler: MessageHandler[HippoHTTPFlow] = MessageHandler()
        self.eq_manager = EventQueueManager(self)
        self.xfer_manager = XferManager(self)
        self.transfer_manager = TransferManager(self)
        self.caps_client = CapsClient(self)
        self.objects = ObjectManager(self)

    @property
    def name(self):
        if self._name:
            return self._name
        return "Pending %r" % (self.circuit_addr,)

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def caps(self):
        return multidict.MultiDict((x, y[1]) for x, y in self._caps.items())

    @property
    def global_pos(self):
        if self.handle is None:
            raise ValueError("Can't determine global region position without handle")
        return Vector3(self.handle >> 32, self.handle & 0xFFffFFff)

    @property
    def is_alive(self):
        if not self.circuit:
            return False
        return self.circuit.is_alive

    def update_caps(self, caps: Mapping[str, str]):
        for cap_name, cap_url in caps.items():
            if isinstance(cap_url, str) and cap_url.startswith('http'):
                self._caps.add(cap_name, (CapType.NORMAL, cap_url))

    def register_wrapper_cap(self, name: str):
        """
        Wrap an existing, non-unique cap with a unique URL

        caps like ViewerAsset may be the same globally and wouldn't let us infer
        which session / region the request was related to without a wrapper
        """
        parsed = list(urllib.parse.urlsplit(self._caps[name][1]))
        seed_id = self._caps["Seed"][1].split("/")[-1].encode("utf8")
        # Give it a unique domain tied to the current Seed URI
        parsed[1] = f"{name}-{hashlib.sha256(seed_id).hexdigest()[:16]}.hippo-proxy.localhost"
        wrapper_url = urllib.parse.urlunsplit(parsed)
        self._caps.add(name + "ProxyWrapper", (CapType.WRAPPER, wrapper_url))
        return wrapper_url

    def register_proxy_cap(self, name: str):
        """
        Register a cap to be completely handled by the proxy
        """
        cap_url = f"https://caps.hippo-proxy.localhost/cap/{uuid.uuid4()!s}"
        self._caps.add(name, (CapType.PROXY_ONLY, cap_url))
        return cap_url

    def register_temporary_cap(self, name: str, cap_url: str):
        """Register a Cap that only has meaning the first time it's used"""
        self._caps.add(name, (CapType.TEMPORARY, cap_url))

    def resolve_cap(self, url: str, consume=True) -> Optional[Tuple[str, str, CapType]]:
        for name, cap_info in self._caps.items():
            cap_type, cap_url = cap_info
            if url.startswith(cap_url):
                if cap_type == CapType.TEMPORARY and consume:
                    # Resolving a temporary cap pops it out of the dict
                    temporary_caps = self._caps.popall(name)
                    temporary_caps.remove(cap_info)
                    self._caps.extend((name, x) for x in temporary_caps)
                return name, cap_url, cap_type
        return None

    def mark_dead(self):
        logging.info("Marking %r dead" % self)
        if self.circuit:
            self.circuit.is_alive = False
        self.objects.clear()

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.name)


class EventQueueManager:
    def __init__(self, region: ProxiedRegion):
        # TODO: Per-EQ InjectionTracker so we can inject fake responses on 499
        self._queued_events = []
        self._region = weakref.proxy(region)

    def queue_event(self, event: dict):
        self._queued_events.append(event)

    def take_events(self):
        events = self._queued_events
        self._queued_events = []
        return events
