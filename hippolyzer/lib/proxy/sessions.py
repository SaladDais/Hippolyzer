from __future__ import annotations

import dataclasses
import datetime
import functools
import logging
import multiprocessing
import weakref
from typing import *
from weakref import ref

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.client.state import BaseClientSession
from hippolyzer.lib.proxy.circuit import ProxiedCircuit
from hippolyzer.lib.proxy.http_asset_repo import HTTPAssetRepo
from hippolyzer.lib.proxy.http_proxy import HTTPFlowContext, is_asset_server_cap_name, SerializedCapData
from hippolyzer.lib.proxy.namecache import ProxyNameCache
from hippolyzer.lib.proxy.object_manager import ProxyWorldObjectManager
from hippolyzer.lib.proxy.region import ProxiedRegion, CapType

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.message_logger import BaseMessageLogger
    from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow


class Session(BaseClientSession):
    def __init__(self, session_id, secure_session_id, agent_id, circuit_code,
                 login_data=None, session_manager: Optional[SessionManager] = None):
        self.login_data = login_data or {}
        self.pending = True
        self.id: UUID = session_id
        self.secure_session_id: UUID = secure_session_id
        self.agent_id: UUID = agent_id
        self.circuit_code = circuit_code
        self.global_caps = {}
        # Bag of arbitrary data addons can use to persist data across addon reloads
        self.addon_ctx = {}
        self.session_manager: SessionManager = session_manager or None
        self.selected: SelectionModel = SelectionModel()
        self.regions: List[ProxiedRegion] = []
        self.started_at = datetime.datetime.now()
        self.message_handler: MessageHandler[Message] = MessageHandler()
        self.http_message_handler: MessageHandler[HippoHTTPFlow] = MessageHandler()
        self.objects = ProxyWorldObjectManager(self, session_manager.name_cache)
        self._main_region = None

    @property
    def global_addon_ctx(self):
        if not self.session_manager:
            return {}
        return self.session_manager.addon_ctx

    @classmethod
    def from_login_data(cls, login_data, session_manager):
        sess = Session(
            session_id=UUID(login_data["session_id"]),
            secure_session_id=UUID(login_data["secure_session_id"]),
            agent_id=UUID(login_data["agent_id"]),
            circuit_code=int(login_data["circuit_code"]),
            login_data=login_data,
            session_manager=session_manager,
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

    @property
    def main_region(self) -> Optional[ProxiedRegion]:
        if self._main_region and self._main_region() in self.regions:
            return self._main_region()
        return None

    @main_region.setter
    def main_region(self, val: ProxiedRegion):
        self._main_region = weakref.ref(val)

    def register_region(self, circuit_addr: Optional[Tuple[str, int]] = None,
                        seed_url: Optional[str] = None,
                        handle: Optional[int] = None) -> ProxiedRegion:
        if not any((circuit_addr, seed_url)):
            raise ValueError("One of circuit_addr and seed_url must be defined!")

        for region in self.regions:
            if region.circuit_addr == circuit_addr:
                if seed_url and region.caps.get("Seed") != seed_url:
                    region.update_caps({"Seed": seed_url})
                if handle:
                    region.handle = handle
                return region
            if seed_url and region.caps.get("Seed") == seed_url:
                return region

        if not circuit_addr:
            raise ValueError("Can't create region without circuit addr!")

        logging.info("Registering region for %r" % (circuit_addr,))
        region = ProxiedRegion(circuit_addr, seed_url, self, handle=handle)
        self.regions.append(region)
        return region

    def region_by_circuit_addr(self, circuit_addr) -> Optional[ProxiedRegion]:
        for region in self.regions:
            if region.circuit_addr == circuit_addr and region.circuit:
                return region
        return None

    def region_by_handle(self, handle: int) -> Optional[ProxiedRegion]:
        for region in self.regions:
            if region.handle == handle:
                return region
        return None

    def open_circuit(self, near_addr, circuit_addr, transport):
        for region in self.regions:
            if region.circuit_addr == circuit_addr:
                if not region.circuit or not region.circuit.is_alive:
                    logging_hook = None
                    if self.session_manager.message_logger:
                        logging_hook = functools.partial(
                            self.session_manager.message_logger.log_lludp_message,
                            self,
                            region,
                        )
                    region.circuit = ProxiedCircuit(
                        near_addr, circuit_addr, transport, logging_hook=logging_hook)
                    return True
                if region.circuit and region.circuit.is_alive:
                    # Whatever, already open
                    logging.debug("Tried to re-open circuit for %r" % (circuit_addr,))
                    return True
        return False

    def resolve_cap(self, url: str) -> Optional[CapData]:
        for cap_name, cap_url in self.global_caps.items():
            if url.startswith(cap_url):
                return CapData(
                    cap_name, None, None, cap_url
                )
        for region in self.regions:
            resolved_cap = region.resolve_cap(url)
            if resolved_cap:
                cap_name, base_url, cap_type = resolved_cap
                # GetMesh and friends can't be tied to a specific session or region
                # (at least on agni) unless we go through a proxy wrapper, since every
                # region just points at the global asset CDN.
                if is_asset_server_cap_name(cap_name) and cap_type != CapType.WRAPPER:
                    return CapData(cap_name, None, None, base_url, cap_type)
                return CapData(cap_name, ref(region), ref(self), base_url, cap_type)
        return None

    def tid_to_assetid(self, transaction_id: UUID):
        return UUID.combine(transaction_id, self.secure_session_id)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.id)


class SessionManager:
    def __init__(self):
        self.sessions: List[Session] = []
        self.shutdown_signal = multiprocessing.Event()
        self.flow_context = HTTPFlowContext()
        self.asset_repo = HTTPAssetRepo()
        self.message_logger: Optional[BaseMessageLogger] = None
        self.addon_ctx: Dict[str, Any] = {}
        self.name_cache = ProxyNameCache()
        self.use_viewer_object_cache: bool = False

    def create_session(self, login_data) -> Session:
        session = Session.from_login_data(login_data, self)
        self.name_cache.create_subscriptions(
            session.message_handler,
            session.http_message_handler,
        )
        self.sessions.append(session)
        logging.info("Created %r" % session)
        return session

    def claim_session(self, session_id) -> Optional[Session]:
        for session in self.sessions:
            if session.pending and session.id == session_id:
                logging.info("Claimed %r" % session)
                session.pending = False
                return session
        return None

    def close_session(self, session: Session):
        logging.info("Closed %r" % session)
        session.objects.clear()
        self.sessions.remove(session)

    def resolve_cap(self, url: str) -> Optional["CapData"]:
        for session in self.sessions:
            cap_data = session.resolve_cap(url)
            if cap_data:
                return cap_data
        return CapData()

    def deserialize_cap_data(self, ser_cap_data: "SerializedCapData") -> "CapData":
        cap_session = None
        cap_region = None
        if ser_cap_data.session_id:
            for session in self.sessions:
                if ser_cap_data.session_id == str(session.id):
                    cap_session = session
        if cap_session and ser_cap_data.region_addr:
            for region in cap_session.regions:
                if ser_cap_data.region_addr == str(region.circuit_addr):
                    cap_region = region
        return CapData(
            cap_name=ser_cap_data.cap_name,
            region=ref(cap_region) if cap_region else None,
            session=ref(cap_session) if cap_session else None,
            base_url=ser_cap_data.base_url,
            type=CapType[ser_cap_data.type],
        )


class CapData(NamedTuple):
    cap_name: Optional[str] = None
    # Actually they're weakrefs but the type sigs suck.
    region: Optional[Callable[[], Optional[ProxiedRegion]]] = None
    session: Optional[Callable[[], Optional[Session]]] = None
    base_url: Optional[str] = None
    type: CapType = CapType.NORMAL

    def __bool__(self):
        return bool(self.cap_name or self.session)

    def serialize(self) -> "SerializedCapData":
        return SerializedCapData(
            cap_name=self.cap_name,
            region_addr=str(self.region().circuit_addr) if self.region and self.region() else None,
            session_id=str(self.session().id) if self.session and self.session() else None,
            base_url=self.base_url,
            type=self.type.name,
        )

    @property
    def asset_server_cap(self) -> bool:
        return is_asset_server_cap_name(self.cap_name)


@dataclasses.dataclass
class SelectionModel:
    object_local: Optional[int] = None
    object_locals: Sequence[int] = dataclasses.field(default_factory=list)
    object_full: Optional[UUID] = None
    parcel_local: Optional[int] = None
    parcel_full: Optional[UUID] = None
    script_item: Optional[UUID] = None
    task_item: Optional[UUID] = None
