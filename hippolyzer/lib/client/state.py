"""
Base classes for common session-related state shared between clients and proxies
"""
from __future__ import annotations

import abc
import logging
import weakref
from typing import *

import multidict

from hippolyzer.lib.base.datatypes import UUID, Vector3
from hippolyzer.lib.base.message.circuit import ConnectionHolder, Circuit
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.network.caps_client import CapsClient
from hippolyzer.lib.base.network.transport import ADDR_TUPLE
from hippolyzer.lib.base.objects import handle_to_global_pos

from hippolyzer.lib.client.object_manager import ClientObjectManager, ClientWorldObjectManager


class BaseClientRegion(ConnectionHolder, abc.ABC):
    """Represents a client's view of a remote region"""
    handle: Optional[int]
    # Actually a weakref
    session: Callable[[], BaseClientSession]
    objects: ClientObjectManager
    caps_client: CapsClient
    cap_urls: multidict.MultiDict[str]
    circuit_addr: ADDR_TUPLE
    circuit: Optional[Circuit]
    _name: Optional[str]

    def __init__(self):
        self._name = None
        self.circuit = None

    @abc.abstractmethod
    def update_caps(self, caps: Mapping[str, str]) -> None:
        pass

    @property
    def name(self):
        if self._name:
            return self._name
        return "Pending %r" % (self.circuit_addr,)

    @name.setter
    def name(self, val):
        self._name = val

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

    def mark_dead(self):
        logging.info("Marking %r dead" % self)
        if self.circuit:
            self.circuit.is_alive = False
        self.objects.clear()

    def __repr__(self):
        return "<%s %s (%r)>" % (self.__class__.__name__, self.name, self.handle)


class BaseClientSessionManager:
    pass


class BaseClientSession(abc.ABC):
    """Represents a client's view of a remote session"""
    id: UUID
    agent_id: UUID
    secure_session_id: UUID
    active_group: UUID
    groups: Set[UUID]
    message_handler: MessageHandler[Message, str]
    regions: MutableSequence[BaseClientRegion]
    region_by_handle: Callable[[int], Optional[BaseClientRegion]]
    region_by_circuit_addr: Callable[[ADDR_TUPLE], Optional[BaseClientRegion]]
    objects: ClientWorldObjectManager
    login_data: Dict[str, Any]
    REGION_CLS = Type[BaseClientRegion]

    def __init__(self, id, secure_session_id, agent_id, circuit_code,
                 session_manager: Optional[BaseClientSessionManager], login_data=None):
        self.login_data = login_data or {}
        self.pending = True
        self.id: UUID = id
        self.secure_session_id: UUID = secure_session_id
        self.agent_id: UUID = agent_id
        self.circuit_code = circuit_code
        self.global_caps = {}
        self.session_manager = session_manager
        self.active_group: UUID = UUID.ZERO
        self.groups: Set[UUID] = set()
        self.regions = []
        self._main_region = None
        self.message_handler: MessageHandler[Message, str] = MessageHandler()
        super().__init__()

    @classmethod
    def from_login_data(cls, login_data, session_manager):
        sess = cls(
            id=UUID(login_data["session_id"]),
            secure_session_id=UUID(login_data["secure_session_id"]),
            agent_id=UUID(login_data["agent_id"]),
            circuit_code=int(login_data["circuit_code"]),
            session_manager=session_manager,
            login_data=login_data,
        )
        appearance_service = login_data.get("agent_appearance_service")
        map_image_service = login_data.get("map-server-url")
        if appearance_service:
            sess.global_caps["AppearanceService"] = appearance_service
        if map_image_service:
            sess.global_caps["MapImageService"] = map_image_service
        # Login data also has details about the initial sim
        sess.register_region(
            circuit_addr=(login_data["sim_ip"], login_data["sim_port"]),
            handle=(login_data["region_x"] << 32) | login_data["region_y"],
            seed_url=login_data["seed_capability"],
        )
        return sess

    def register_region(self, circuit_addr: Optional[ADDR_TUPLE] = None, seed_url: Optional[str] = None,
                        handle: Optional[int] = None) -> BaseClientRegion:
        if not any((circuit_addr, seed_url)):
            raise ValueError("One of circuit_addr and seed_url must be defined!")

        for region in self.regions:
            if region.circuit_addr == circuit_addr:
                if seed_url and region.cap_urls.get("Seed") != seed_url:
                    region.update_caps({"Seed": seed_url})
                if handle:
                    region.handle = handle
                return region
            if seed_url and region.cap_urls.get("Seed") == seed_url:
                return region

        if not circuit_addr:
            raise ValueError("Can't create region without circuit addr!")

        logging.info("Registering region for %r" % (circuit_addr,))
        region = self.REGION_CLS(circuit_addr, seed_url, self, handle=handle)
        self.regions.append(region)
        return region

    @property
    def main_region(self) -> Optional[BaseClientRegion]:
        if self._main_region and self._main_region() in self.regions:
            return self._main_region()
        return None

    @main_region.setter
    def main_region(self, val: BaseClientRegion):
        self._main_region = weakref.ref(val)

    def transaction_to_assetid(self, transaction_id: UUID):
        return UUID.combine(transaction_id, self.secure_session_id)

    def region_by_circuit_addr(self, circuit_addr) -> Optional[BaseClientRegion]:
        for region in self.regions:
            if region.circuit_addr == circuit_addr and region.circuit:
                return region
        return None

    def region_by_handle(self, handle: int) -> Optional[BaseClientRegion]:
        for region in self.regions:
            if region.handle == handle:
                return region
        return None

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.id)
