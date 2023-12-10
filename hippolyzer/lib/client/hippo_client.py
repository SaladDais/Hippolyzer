from __future__ import annotations

import asyncio
import hashlib
from importlib.metadata import version
import logging
import uuid
import weakref
import xmlrpc.client
from typing import *

import aiohttp
import multidict

from hippolyzer.lib.base.helpers import proxify
from hippolyzer.lib.base.message.circuit import Circuit
from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.message.message_dot_xml import MessageDotXML
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.network.caps_client import CapsClient
from hippolyzer.lib.base.network.transport import ADDR_TUPLE, Direction, SocketUDPTransport
from hippolyzer.lib.base.settings import Settings
from hippolyzer.lib.base.templates import RegionHandshakeReplyFlags
from hippolyzer.lib.base.transfer_manager import TransferManager
from hippolyzer.lib.base.xfer_manager import XferManager
from hippolyzer.lib.client.asset_uploader import AssetUploader
from hippolyzer.lib.client.object_manager import ClientObjectManager, ClientWorldObjectManager
from hippolyzer.lib.client.state import BaseClientSession, BaseClientRegion, BaseClientSessionManager


LOG = logging.getLogger(__name__)


class HippoCapsClient(CapsClient):
    def _request_fixups(self, cap_or_url: str, headers: Dict, proxy: Optional[bool], ssl: Any):
        headers["User-Agent"] = f"Hippolyzer/v{version('hippolyzer')}"


class HippoClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, session: HippoClientSession):
        self.session = session
        self.transport: Optional[SocketUDPTransport] = None
        self.message_xml = MessageDotXML()
        self.deserializer = UDPMessageDeserializer(
            settings=self.session.session_manager.settings,
        )
        loop = asyncio.get_event_loop_policy().get_event_loop()
        self.resend_task = loop.create_task(self.attempt_resends())

    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = SocketUDPTransport(transport)

    def datagram_received(self, data, source_addr: ADDR_TUPLE):
        region = self.session.region_by_circuit_addr(source_addr)
        if not region:
            logging.warning("Received packet from invalid address %s", source_addr)
            return

        message = self.deserializer.deserialize(data)
        message.direction = Direction.IN
        message.sender = source_addr

        if not self.message_xml.validate_udp_msg(message.name):
            LOG.warning(
                f"Received {message.name!r} over UDP, when it should come over the event queue. Discarding."
            )
            raise PermissionError(f"UDPBanned message {message.name}")

        region.circuit.collect_acks(message)

        try:
            self.session.message_handler.handle(message)
        except:
            LOG.exception("Failed in region message handler")
        region.message_handler.handle(message)

    async def attempt_resends(self):
        while True:
            await asyncio.sleep(0.1)
            if self.session is None:
                continue
            for region in self.session.regions:
                if not region.circuit or not region.circuit.is_alive:
                    continue
                region.circuit.resend_unacked()

    def close(self):
        logging.info("Closing UDP transport")
        self.transport.close()
        self.session = None
        self.resend_task.cancel()


class HippoClientRegion(BaseClientRegion):
    def __init__(self, circuit_addr, seed_cap: str, session: HippoClientSession, handle=None):
        super().__init__()
        self.caps = multidict.MultiDict()
        self.message_handler = MessageHandler()
        self.circuit_addr = circuit_addr
        self.handle = handle
        if seed_cap:
            self.caps["Seed"] = seed_cap
        self.session: Callable[[], HippoClientSession] = weakref.ref(session)
        self.caps_client = HippoCapsClient(self.caps, session.http_session)
        self.xfer_manager = XferManager(proxify(self), self.session().secure_session_id)
        self.transfer_manager = TransferManager(proxify(self), session.agent_id, session.id)
        self.asset_uploader = AssetUploader(proxify(self))
        self.objects = ClientObjectManager(proxify(self))

    def update_caps(self, caps: Mapping[str, str]) -> None:
        self.caps.update(caps)

    @property
    def cap_urls(self) -> multidict.MultiDict:
        return self.caps.copy()


class HippoClientSession(BaseClientSession):
    """Represents a client's view of a remote session"""
    REGION_CLS = HippoClientRegion

    region_by_handle: Callable[[int], Optional[HippoClientRegion]]
    region_by_circuit_addr: Callable[[ADDR_TUPLE], Optional[HippoClientRegion]]
    session_manager: HippoClient

    def __init__(self, id, secure_session_id, agent_id, circuit_code, session_manager: Optional[HippoClient] = None,
                 login_data=None):
        super().__init__(id, secure_session_id, agent_id, circuit_code, session_manager, login_data=login_data)
        self.http_session = session_manager.http_session
        self.objects = ClientWorldObjectManager(proxify(self), session_manager.settings, None)
        self.protocol: Optional[HippoClientProtocol] = None

    def register_region(self, circuit_addr: Optional[ADDR_TUPLE] = None, seed_url: Optional[str] = None,
                        handle: Optional[int] = None) -> HippoClientRegion:
        return super().register_region(circuit_addr, seed_url, handle)  # type:ignore

    def open_circuit(self, circuit_addr):
        for region in self.regions:
            if region.circuit_addr == circuit_addr:
                valid_circuit = False
                if not region.circuit or not region.circuit.is_alive:
                    region.circuit = Circuit(("127.0.0.1", 0), circuit_addr, self.protocol.transport)
                    region.circuit.is_alive = False
                    valid_circuit = True
                if region.circuit and region.circuit.is_alive:
                    # Whatever, already open
                    logging.debug("Tried to re-open circuit for %r" % (circuit_addr,))
                    valid_circuit = True

                if valid_circuit:
                    # TODO: This is a little bit crap, we need to know if a UseCircuitCode was ever ACKed
                    #  before we can start sending other packets, otherwise we might have a race.
                    region.circuit.send_reliable(
                        Message(
                            "UseCircuitCode",
                            Block("CircuitCode", Code=self.circuit_code, SessionID=self.id, ID=self.agent_id),
                        )
                    )
                    # TODO: set this in a callback for UseCircuitCode ACK
                    region.circuit.is_alive = True
                return valid_circuit
        return False


class HippoClient(BaseClientSessionManager):
    SUPPORTED_CAPS: Set[str] = {
        "AbuseCategories",
        "AcceptFriendship",
        "AcceptGroupInvite",
        "AgentPreferences",
        "AgentProfile",
        "AgentState",
        "AttachmentResources",
        "AvatarPickerSearch",
        "AvatarRenderInfo",
        "CharacterProperties",
        "ChatSessionRequest",
        "CopyInventoryFromNotecard",
        "CreateInventoryCategory",
        "DeclineFriendship",
        "DeclineGroupInvite",
        "DispatchRegionInfo",
        "DirectDelivery",
        "EnvironmentSettings",
        "EstateAccess",
        "DispatchOpenRegionSettings",
        "EstateChangeInfo",
        "EventQueueGet",
        "ExtEnvironment",
        "FetchLib2",
        "FetchLibDescendents2",
        "FetchInventory2",
        "FetchInventoryDescendents2",
        "IncrementCOFVersion",
        "InventoryAPIv3",
        "LibraryAPIv3",
        "InterestList",
        "InventoryThumbnailUpload",
        "GetDisplayNames",
        "GetExperiences",
        "AgentExperiences",
        "FindExperienceByName",
        "GetExperienceInfo",
        "GetAdminExperiences",
        "GetCreatorExperiences",
        "ExperiencePreferences",
        "GroupExperiences",
        "UpdateExperience",
        "IsExperienceAdmin",
        "IsExperienceContributor",
        "RegionExperiences",
        "ExperienceQuery",
        "GetMesh",
        "GetMesh2",
        "GetMetadata",
        "GetObjectCost",
        "GetObjectPhysicsData",
        "GetTexture",
        "GroupAPIv1",
        "GroupMemberData",
        "GroupProposalBallot",
        "HomeLocation",
        "LandResources",
        "LSLSyntax",
        "MapLayer",
        "MapLayerGod",
        "MeshUploadFlag",
        "NavMeshGenerationStatus",
        "NewFileAgentInventory",
        "ObjectAnimation",
        "ObjectMedia",
        "ObjectMediaNavigate",
        "ObjectNavMeshProperties",
        "ParcelPropertiesUpdate",
        "ParcelVoiceInfoRequest",
        "ProductInfoRequest",
        "ProvisionVoiceAccountRequest",
        "ReadOfflineMsgs",
        "RegionObjects",
        "RemoteParcelRequest",
        "RenderMaterials",
        "RequestTextureDownload",
        "ResourceCostSelected",
        "RetrieveNavMeshSrc",
        "SearchStatRequest",
        "SearchStatTracking",
        "SendPostcard",
        "SendUserReport",
        "SendUserReportWithScreenshot",
        "ServerReleaseNotes",
        "SetDisplayName",
        "SimConsoleAsync",
        "SimulatorFeatures",
        "StartGroupProposal",
        "TerrainNavMeshProperties",
        "TextureStats",
        "UntrustedSimulatorMessage",
        "UpdateAgentInformation",
        "UpdateAgentLanguage",
        "UpdateAvatarAppearance",
        "UpdateGestureAgentInventory",
        "UpdateGestureTaskInventory",
        "UpdateNotecardAgentInventory",
        "UpdateNotecardTaskInventory",
        "UpdateScriptAgent",
        "UpdateScriptTask",
        "UpdateSettingsAgentInventory",
        "UpdateSettingsTaskInventory",
        "UploadAgentProfileImage",
        "UploadBakedTexture",
        "UserInfo",
        "ViewerAsset",
        "ViewerBenefits",
        "ViewerMetrics",
        "ViewerStartAuction",
        "ViewerStats",
    }

    DEFAULT_OPTIONS = {
        "inventory-root",
        "inventory-skeleton",
        "inventory-lib-root",
        "inventory-lib-owner",
        "inventory-skel-lib",
        "initial-outfit",
        "gestures",
        "display_names",
        "event_notifications",
        "classified_categories",
        "adult_compliant",
        "buddy-list",
        "newuser-config",
        "ui-config",
        "advanced-mode",
        "max-agent-groups",
        "map-server-url",
        "voice-config",
        "tutorial_setting",
        "login-flags",
        "global-textures",
        # Not an official option, just so this can be tracked.
        "pyogp-client",
    }

    DEFAULT_LOGIN_URI = "https://login.agni.lindenlab.com/cgi-bin/login.cgi"

    def __init__(self, options: Optional[Set[str]] = None):
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._mac = uuid.getnode()
        self._options = options if options is not None else self.DEFAULT_OPTIONS
        self.http_session = aiohttp.ClientSession()
        self.session: Optional[HippoClientSession] = None
        self.settings = Settings()

    async def aclose(self):
        try:
            await self.logout()
        finally:
            await self.http_session.close()

    async def login(
            self,
            username: str,
            password: str,
            login_uri: Optional[str] = "",
            agree_to_tos: bool = False,
            start_location: str = "home"
    ):
        if self.session:
            raise RuntimeError("Already logged in!")

        if not login_uri:
            login_uri = self.DEFAULT_LOGIN_URI

        split_username = username.split(" ")
        if len(split_username) < 2:
            first_name = split_username[0]
            last_name = "Resident"
        else:
            first_name, last_name = split_username

        payload = {
            "address_size": 64,
            "agree_to_tos": int(agree_to_tos),
            "channel": "Hippolyzer",
            "extended_errors": 1,
            "first": first_name,
            "last": last_name,
            "host_id": "",
            "id0": hashlib.md5(str(self._mac).encode("ascii")).hexdigest(),
            "mac": hashlib.md5(str(self._mac).encode("ascii")).hexdigest(),
            "mfa_hash": "",
            "passwd": "$1$" + hashlib.md5(str(password).encode("ascii")).hexdigest(),
            # TODO: actually get these
            "platform": "lnx",
            "platform_string": "Linux 6.6",
            # TODO: What is this?
            "platform_version": "2.38.0",
            "read_critical": 0,
            "start": start_location,
            "token": "",
            "version": version("hippolyzer"),
            "options": list(self._options),
        }
        rpc_payload = xmlrpc.client.dumps((payload,), "login_to_simulator")
        async with self.http_session.post(login_uri, data=rpc_payload, headers={"Content-Type": "text/xml"}) as resp:
            resp.raise_for_status()
            login_data = xmlrpc.client.loads((await resp.read()).decode("utf8"))[0][0]
        self.session = HippoClientSession.from_login_data(login_data, self)

        loop = asyncio.get_event_loop_policy().get_event_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: HippoClientProtocol(self.session),
            local_addr=('0.0.0.0', 0))
        self.session.protocol = protocol
        protocol.transport = SocketUDPTransport(transport)
        assert self.session.open_circuit(self.session.regions[-1].circuit_addr)
        region = self.session.regions[-1]
        self.session.main_region = region

        # Register first so we can handle it even if the ack happens after the message is sent
        region_handshake_fut = region.message_handler.wait_for(("RegionHandshake",))
        await region.circuit.send_reliable(
            Message(
                "CompleteAgentMovement",
                Block(
                    "AgentData",
                    AgentID=self.session.agent_id,
                    SessionID=self.session.id,
                    CircuitCode=self.session.circuit_code
                ),
            )
        )
        region.name = str((await region_handshake_fut)["RegionInfo"][0]["SimName"])
        await region.circuit.send_reliable(
            Message(
                "RegionHandshakeReply",
                Block("AgentData", AgentID=self.session.agent_id, SessionID=self.session.id),
                Block(
                    "RegionInfo",
                    Flags=(
                        RegionHandshakeReplyFlags.SUPPORTS_SELF_APPEARANCE
                        | RegionHandshakeReplyFlags.VOCACHE_IS_EMPTY
                    )
                )
            )
        )
        await region.circuit.send_reliable(
            Message(
                "AgentThrottle",
                Block(
                    "AgentData",
                    AgentID=self.session.agent_id,
                    SessionID=self.session.id,
                    CircuitCode=self.session.circuit_code,
                ),
                Block(
                    "Throttle",
                    GenCounter=0,
                    # Reasonable defaults, I guess
                    Throttles_=[207360.0, 165376.0, 33075.19921875, 33075.19921875, 682700.75, 682700.75, 269312.0],
                )
            )
        )

    async def logout(self):
        if not self.session:
            return
        session = self.session
        self.session = None
        if not session.main_region or not session.main_region.is_alive:
            # Nothing to do
            return
        # Don't need to send reliably, there's a good chance the server won't ACK anyway.
        session.main_region.circuit.send(
            Message(
                "LogoutRequest",
                Block("AgentData", AgentID=session.agent_id, SessionID=session.id),
            )
        )
