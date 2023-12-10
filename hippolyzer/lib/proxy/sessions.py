from __future__ import annotations

import collections
import dataclasses
import datetime
import functools
import logging
import multiprocessing
from typing import *
from weakref import ref

from outleap import LEAPClient

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.helpers import proxify
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.network.transport import ADDR_TUPLE
from hippolyzer.lib.client.state import BaseClientSession, BaseClientSessionManager
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.circuit import ProxiedCircuit
from hippolyzer.lib.proxy.http_asset_repo import HTTPAssetRepo
from hippolyzer.lib.proxy.http_proxy import HTTPFlowContext
from hippolyzer.lib.proxy.caps import is_asset_server_cap_name, CapData, CapType
from hippolyzer.lib.proxy.inventory_manager import ProxyInventoryManager
from hippolyzer.lib.proxy.namecache import ProxyNameCache
from hippolyzer.lib.proxy.object_manager import ProxyWorldObjectManager
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.settings import ProxySettings

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.message_logger import BaseMessageLogger
    from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow


class Session(BaseClientSession):
    regions: MutableSequence[ProxiedRegion]
    region_by_handle: Callable[[int], Optional[ProxiedRegion]]
    region_by_circuit_addr: Callable[[ADDR_TUPLE], Optional[ProxiedRegion]]
    main_region: Optional[ProxiedRegion]
    REGION_CLS = ProxiedRegion

    def __init__(self, id, secure_session_id, agent_id, circuit_code,
                 session_manager: Optional[SessionManager], login_data=None):
        super().__init__(
            id=id,
            secure_session_id=secure_session_id,
            agent_id=agent_id,
            circuit_code=circuit_code,
            session_manager=session_manager,
            login_data=login_data,
        )
        # Bag of arbitrary data addons can use to persist data across addon reloads
        # Each addon name gets its own separate dict within this dict
        self.addon_ctx: Dict[str, Dict[str, Any]] = collections.defaultdict(dict)
        self.session_manager: SessionManager = session_manager
        self.selected: SelectionModel = SelectionModel()
        self.started_at = datetime.datetime.now()
        self.http_message_handler: MessageHandler[HippoHTTPFlow, str] = MessageHandler()
        self.objects = ProxyWorldObjectManager(self, session_manager.settings, session_manager.name_cache)
        self.inventory = ProxyInventoryManager(proxify(self))
        self.leap_client: Optional[LEAPClient] = None
        # Base path of a newview type cache directory for this session
        self.cache_dir: Optional[str] = None

    @property
    def global_addon_ctx(self):
        if not self.session_manager:
            return {}
        return self.session_manager.addon_ctx

    def register_region(self, circuit_addr: Optional[ADDR_TUPLE] = None,
                        seed_url: Optional[str] = None,
                        handle: Optional[int] = None) -> ProxiedRegion:
        region: ProxiedRegion = super().register_region(circuit_addr, seed_url, handle)  # type: ignore
        AddonManager.handle_region_registered(self, region)
        return region

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
                    AddonManager.handle_circuit_created(self, region)
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


class SessionManager(BaseClientSessionManager):
    def __init__(self, settings: ProxySettings):
        BaseClientSessionManager.__init__(self)
        self.settings: ProxySettings = settings
        self.sessions: List[Session] = []
        self.shutdown_signal = multiprocessing.Event()
        self.flow_context = HTTPFlowContext()
        self.asset_repo = HTTPAssetRepo()
        self.message_logger: Optional[BaseMessageLogger] = None
        self.addon_ctx: Dict[str, Dict[str, Any]] = collections.defaultdict(dict)
        self.name_cache = ProxyNameCache()
        self.pending_leap_clients: List[LEAPClient] = []

    def create_session(self, login_data) -> Session:
        session = Session.from_login_data(login_data, self)
        self.name_cache.create_subscriptions(
            session.message_handler,
            session.http_message_handler,
        )
        self.sessions.append(session)
        # TODO: less crap way of tying a LEAP client to a session
        while self.pending_leap_clients:
            leap_client = self.pending_leap_clients.pop(-1)
            # Client may have gone bad since it connected
            if not leap_client.connected:
                continue
            logging.info("Assigned LEAP client to session")
            session.leap_client = leap_client
            break
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
        if session.leap_client:
            session.leap_client.disconnect()
        self.sessions.remove(session)

    def resolve_cap(self, url: str) -> Optional["CapData"]:
        for session in self.sessions:
            cap_data = session.resolve_cap(url)
            if cap_data:
                return cap_data
        return CapData()

    async def leap_client_connected(self, leap_client: LEAPClient):
        self.pending_leap_clients.append(leap_client)
        AddonManager.handle_leap_client_added(self, leap_client)


@dataclasses.dataclass
class SelectionModel:
    object_local: Optional[int] = None
    object_locals: Sequence[int] = dataclasses.field(default_factory=list)
    object_full: Optional[UUID] = None
    parcel_local: Optional[int] = None
    parcel_full: Optional[UUID] = None
    script_item: Optional[UUID] = None
    task_item: Optional[UUID] = None
