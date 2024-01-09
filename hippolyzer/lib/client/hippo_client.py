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

from hippolyzer.lib.base.datatypes import Vector3, StringEnum
from hippolyzer.lib.base.helpers import proxify, get_resource_filename
from hippolyzer.lib.base.message.circuit import Circuit
from hippolyzer.lib.base.message.llsd_msg_serializer import LLSDMessageSerializer
from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.message.message_dot_xml import MessageDotXML
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.network.caps_client import CapsClient, CAPS_DICT
from hippolyzer.lib.base.network.transport import ADDR_TUPLE, Direction, SocketUDPTransport, AbstractUDPTransport
from hippolyzer.lib.base.settings import Settings, SettingDescriptor
from hippolyzer.lib.base.templates import RegionHandshakeReplyFlags, ChatType
from hippolyzer.lib.base.transfer_manager import TransferManager
from hippolyzer.lib.base.xfer_manager import XferManager
from hippolyzer.lib.client.asset_uploader import AssetUploader
from hippolyzer.lib.client.inventory_manager import InventoryManager
from hippolyzer.lib.client.object_manager import ClientObjectManager, ClientWorldObjectManager
from hippolyzer.lib.client.parcel_manager import ParcelManager
from hippolyzer.lib.client.state import BaseClientSession, BaseClientRegion, BaseClientSessionManager


LOG = logging.getLogger(__name__)


class StartLocation(StringEnum):
    LAST = "last"
    HOME = "home"


class ClientSettings(Settings):
    SSL_VERIFY: bool = SettingDescriptor(False)
    """Off by default for now, the cert validation is a big mess due to LL using an internal CA."""
    SSL_CERT_PATH: str = SettingDescriptor(get_resource_filename("lib/base/network/data/ca-bundle.crt"))
    USER_AGENT: str = SettingDescriptor(f"Hippolyzer/v{version('hippolyzer')}")
    SEND_AGENT_UPDATES: bool = SettingDescriptor(True)
    """Generally you want to send these, lots of things will break if you don't send at least one."""
    AUTO_REQUEST_PARCELS: bool = SettingDescriptor(True)
    """Automatically request all parcel details when connecting to a region"""
    AUTO_REQUEST_MATERIALS: bool = SettingDescriptor(True)
    """Automatically request all materials when connecting to a region"""


class HippoCapsClient(CapsClient):
    def __init__(
            self,
            settings: ClientSettings,
            caps: Optional[CAPS_DICT] = None,
            session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        super().__init__(caps, session)
        self._settings = settings

    def _request_fixups(self, cap_or_url: str, headers: Dict, proxy: Optional[bool], ssl: Any):
        headers["User-Agent"] = self._settings.USER_AGENT
        return cap_or_url, headers, proxy, self._settings.SSL_VERIFY


class HippoClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, session: HippoClientSession):
        self.session = proxify(session)
        self.message_xml = MessageDotXML()
        self.deserializer = UDPMessageDeserializer(
            settings=self.session.session_manager.settings,
        )

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

        should_handle = True
        if message.reliable:
            # This is a bit crap. We send an ACK immediately through a PacketAck.
            # This is pretty wasteful, we should batch them up and send them on a timer.
            # We should ACK even if it's a resend of something we've already handled, maybe
            # they never got the ACK.
            region.circuit.send_acks((message.packet_id,))
            should_handle = region.circuit.track_reliable(message.packet_id)

        try:
            if should_handle:
                self.session.message_handler.handle(message)
        except:
            LOG.exception("Failed in region message handler")
        region.message_handler.handle(message)


class HippoClientRegion(BaseClientRegion):
    def __init__(self, circuit_addr, seed_cap: Optional[str], session: HippoClientSession, handle=None):
        super().__init__()
        self.caps = multidict.MultiDict()
        self.message_handler: MessageHandler[Message, str] = MessageHandler(take_by_default=False)
        self.circuit_addr = circuit_addr
        self.handle = handle
        if seed_cap:
            self.caps["Seed"] = seed_cap
        self.session: Callable[[], HippoClientSession] = weakref.ref(session)
        self.caps_client = HippoCapsClient(session.session_manager.settings, self.caps, session.http_session)
        self.xfer_manager = XferManager(proxify(self), self.session().secure_session_id)
        self.transfer_manager = TransferManager(proxify(self), session.agent_id, session.id)
        self.asset_uploader = AssetUploader(proxify(self))
        self.parcel_manager = ParcelManager(proxify(self))
        self.objects = ClientObjectManager(self)
        self._llsd_serializer = LLSDMessageSerializer()
        self._eq_task: Optional[asyncio.Task] = None
        self.connected: asyncio.Future = asyncio.Future()

        self.message_handler.subscribe("StartPingCheck", self._handle_ping_check)

    def update_caps(self, caps: Mapping[str, str]) -> None:
        self.caps.update(caps)

    @property
    def cap_urls(self) -> multidict.MultiDict:
        return self.caps.copy()

    async def connect(self, main_region: bool = False):
        # Disconnect first if we're already connected
        if self.circuit and self.circuit.is_alive:
            self.disconnect()
        if self.connected.done():
            self.connected = asyncio.Future()

        try:
            # TODO: What happens if a circuit code is invalid, again? Does it just refuse to ACK?
            await self.circuit.send_reliable(
                Message(
                    "UseCircuitCode",
                    Block(
                        "CircuitCode",
                        Code=self.session().circuit_code,
                        SessionID=self.session().id,
                        ID=self.session().agent_id,
                    ),
                )
            )
            self.circuit.is_alive = True

            # Clear out any old caps urls except the seed URL, we're about to fetch new caps.
            seed_url = self.caps["Seed"]
            self.caps.clear()
            self.caps["Seed"] = seed_url

            # Kick this off and await it later
            seed_resp_fut = self.caps_client.post("Seed", llsd=list(self.session().session_manager.SUPPORTED_CAPS))

            # Register first so we can handle it even if the ack happens after the message is sent
            region_handshake_fut = self.message_handler.wait_for(("RegionHandshake",))

            # If we're connecting to the main region, it won't even send us a RegionHandshake until we
            # first send a CompleteAgentMovement.
            if main_region:
                await self.complete_agent_movement()

            self.name = str((await region_handshake_fut)["RegionInfo"][0]["SimName"])
            self.session().objects.track_region_objects(self.handle)
            await self.circuit.send_reliable(
                Message(
                    "RegionHandshakeReply",
                    Block("AgentData", AgentID=self.session().agent_id, SessionID=self.session().id),
                    Block(
                        "RegionInfo",
                        Flags=(
                            RegionHandshakeReplyFlags.SUPPORTS_SELF_APPEARANCE
                            | RegionHandshakeReplyFlags.VOCACHE_IS_EMPTY
                        )
                    )
                )
            )
            await self.circuit.send_reliable(
                Message(
                    "AgentThrottle",
                    Block(
                        "AgentData",
                        AgentID=self.session().agent_id,
                        SessionID=self.session().id,
                        CircuitCode=self.session().circuit_code,
                    ),
                    Block(
                        "Throttle",
                        GenCounter=0,
                        # Reasonable defaults, I guess
                        Throttles_=[207360.0, 165376.0, 33075.19921875, 33075.19921875, 682700.75, 682700.75, 269312.0],
                    )
                )
            )
            if self.session().session_manager.settings.SEND_AGENT_UPDATES:
                # Usually we want to send at least one, since lots of messages will never be sent by the sim
                # until we send at least one AgentUpdate. For example, ParcelOverlay and LayerData.
                await self.circuit.send_reliable(
                    Message(
                        "AgentUpdate",
                        Block(
                            'AgentData',
                            AgentID=self.session().agent_id,
                            SessionID=self.session().id,
                            # Don't really care about the other fields.
                            fill_missing=True,
                        )
                    )
                )

            async with seed_resp_fut as seed_resp:
                seed_resp.raise_for_status()
                self.update_caps(await seed_resp.read_llsd())

            self._eq_task = asyncio.create_task(self._poll_event_queue())

            settings = self.session().session_manager.settings
            if settings.AUTO_REQUEST_PARCELS:
                _ = asyncio.create_task(self.parcel_manager.request_dirty_parcels())
            if settings.AUTO_REQUEST_MATERIALS:
                _ = asyncio.create_task(self.objects.request_all_materials())

        except Exception as e:
            # Let consumers who were `await`ing the connected signal know there was an error
            if not self.connected.done():
                self.connected.set_exception(e)
            raise

        self.connected.set_result(None)

    def disconnect(self) -> None:
        """Simulator has gone away, disconnect. Should be synchronous"""
        if self._eq_task is not None:
            self._eq_task.cancel()
        self._eq_task = None
        self.circuit.disconnect()
        self.objects.clear()
        if self.connected.done():
            self.connected = asyncio.Future()
        # TODO: cancel XFers and Transfers and whatnot

    async def complete_agent_movement(self) -> None:
        await self.circuit.send_reliable(
            Message(
                "CompleteAgentMovement",
                Block(
                    "AgentData",
                    AgentID=self.session().agent_id,
                    SessionID=self.session().id,
                    CircuitCode=self.session().circuit_code
                ),
            )
        )
        self.session().main_region = self

    async def _poll_event_queue(self):
        ack: Optional[int] = None
        while True:
            payload = {"ack": ack, "done": False}
            async with self.caps_client.post("EventQueueGet", llsd=payload) as resp:
                if resp.status != 200:
                    await asyncio.sleep(0.1)
                    continue
                polled = await resp.read_llsd()
                for event in polled["events"]:
                    if self._llsd_serializer.can_handle(event["message"]):
                        msg = self._llsd_serializer.deserialize(event)
                    else:
                        msg = Message.from_eq_event(event)
                    msg.sender = self.circuit_addr
                    msg.direction = Direction.IN
                    self.session().message_handler.handle(msg)
                    self.message_handler.handle(msg)
                ack = polled["id"]
                await asyncio.sleep(0.001)

    async def _handle_ping_check(self, message: Message):
        self.circuit.send(
            Message(
                "CompletePingCheck",
                Block("PingID", PingID=message["PingID"]["PingID"]),
            )
        )


class HippoClientSession(BaseClientSession):
    """Represents a client's view of a remote session"""
    REGION_CLS = HippoClientRegion

    region_by_handle: Callable[[int], Optional[HippoClientRegion]]
    region_by_circuit_addr: Callable[[ADDR_TUPLE], Optional[HippoClientRegion]]
    regions: List[HippoClientRegion]
    session_manager: HippoClient
    main_region: Optional[HippoClientRegion]

    def __init__(self, id, secure_session_id, agent_id, circuit_code, session_manager: Optional[HippoClient] = None,
                 login_data=None):
        super().__init__(id, secure_session_id, agent_id, circuit_code, session_manager, login_data=login_data)
        self.http_session = session_manager.http_session
        self.objects = ClientWorldObjectManager(proxify(self), session_manager.settings, None)
        self.inventory_manager = InventoryManager(proxify(self))
        self.transport: Optional[SocketUDPTransport] = None
        self.protocol: Optional[HippoClientProtocol] = None
        self.message_handler.take_by_default = False

        for msg_name in ("DisableSimulator", "CloseCircuit"):
            self.message_handler.subscribe(msg_name, lambda msg: self.unregister_region(msg.sender))
        for msg_name in ("TeleportFinish", "CrossedRegion", "EstablishAgentCommunication"):
            self.message_handler.subscribe(msg_name, self._handle_register_region_message)

    def register_region(self, circuit_addr: Optional[ADDR_TUPLE] = None, seed_url: Optional[str] = None,
                        handle: Optional[int] = None) -> HippoClientRegion:
        return super().register_region(circuit_addr, seed_url, handle)  # type:ignore

    def unregister_region(self, circuit_addr: ADDR_TUPLE) -> None:
        for i, region in enumerate(self.regions):
            if region.circuit_addr == circuit_addr:
                self.regions[i].disconnect()
                del self.regions[i]
                return
        raise KeyError(f"No such region for {circuit_addr!r}")

    def open_circuit(self, circuit_addr: ADDR_TUPLE):
        for region in self.regions:
            if region.circuit_addr == circuit_addr:
                valid_circuit = False
                if not region.circuit or not region.circuit.is_alive:
                    region.circuit = Circuit(("127.0.0.1", 0), circuit_addr, self.transport)
                    region.circuit.is_alive = False
                    valid_circuit = True
                if region.circuit and region.circuit.is_alive:
                    # Whatever, already open
                    logging.debug("Tried to re-open circuit for %r" % (circuit_addr,))
                    valid_circuit = True
                return valid_circuit
        return False

    def _handle_register_region_message(self, msg: Message):
        # Handle events that inform us about new regions
        sim_addr, sim_handle, sim_seed = None, None, None
        moving_to_region = False
        # Sim is asking us to talk to a neighbour
        if msg.name == "EstablishAgentCommunication":
            ip_split = msg["EventData"]["sim-ip-and-port"].split(":")
            sim_addr = (ip_split[0], int(ip_split[1]))
            sim_seed = msg["EventData"]["seed-capability"]
        # We teleported or cross region, opening comms to new sim
        elif msg.name in ("TeleportFinish", "CrossedRegion"):
            sim_block = msg.get_block("RegionData", msg.get_block("Info"))[0]
            sim_addr = (sim_block["SimIP"], sim_block["SimPort"])
            sim_handle = sim_block["RegionHandle"]
            sim_seed = sim_block["SeedCapability"]
            moving_to_region = True
        # Sim telling us about a neighbour
        # elif msg.name == "EnableSimulator":
        #     sim_block = msg["SimulatorInfo"][0]
        #     sim_addr = (sim_block["IP"], sim_block["Port"])
        #     sim_handle = sim_block["Handle"]
        # TODO: EnableSimulator is a little weird. It creates a region and establishes a
        #  circuit, but with no seed cap. The viewer will send UseCircuitCode and all that,
        #  but it's totally workable to just wait for an EstablishAgentCommunication to do that,
        #  since that's when the region actually shows up. I guess EnableSimulator just gives the
        #  viewer some lead time to set up the circuit before the region is actually shown through
        #  EstablishAgentCommunication? Either way, messing around with regions that don't have seed
        #  caps is annoying, so let's just not do it.

        # Register a region if this message was telling us about a new one
        if sim_addr is not None:
            region = self.register_region(sim_addr, handle=sim_handle, seed_url=sim_seed)
            # We can't actually connect without a sim seed, mind you, when we receive and EnableSimulator
            # we have to wait for the EstablishAgentCommunication to actually connect.
            need_connect = (region.circuit and region.circuit.is_alive) or moving_to_region
            self.open_circuit(sim_addr)
            if need_connect:
                asyncio.create_task(region.connect(main_region=moving_to_region))
            elif moving_to_region:
                # No need to connect, but we do need to complete agent movement.
                asyncio.create_task(region.complete_agent_movement())


class HippoClient(BaseClientSessionManager):
    """A simple client, only connects to one region at a time currently."""

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
        self.http_session: Optional[aiohttp.ClientSession] = aiohttp.ClientSession(trust_env=True)
        self.session: Optional[HippoClientSession] = None
        self.settings = ClientSettings()
        self._resend_task: Optional[asyncio.Task] = None

    @property
    def main_region(self) -> Optional[HippoClientRegion]:
        if not self.session:
            return None
        return self.session.main_region

    @property
    def main_circuit(self) -> Optional[Circuit]:
        if not self.main_region:
            return None
        return self.main_region.circuit

    @property
    def main_caps_client(self) -> Optional[CapsClient]:
        if not self.main_region:
            return None
        return self.main_region.caps_client

    async def aclose(self):
        try:
            self.logout()
        finally:
            if self.http_session:
                await self.http_session.close()
                self.http_session = None

    def __del__(self):
        # Make sure we don't leak resources if someone was lazy.
        try:
            self.logout()
        finally:
            if self.http_session:
                try:
                    asyncio.create_task(self.http_session.close)
                except:
                    pass
                self.http_session = None

    async def _create_transport(self) -> Tuple[AbstractUDPTransport, HippoClientProtocol]:
        loop = asyncio.get_event_loop_policy().get_event_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: HippoClientProtocol(self.session),
            local_addr=('0.0.0.0', 0))
        transport = SocketUDPTransport(transport)
        return transport, protocol

    async def login(
            self,
            username: str,
            password: str,
            login_uri: Optional[str] = None,
            agree_to_tos: bool = False,
            start_location: Union[StartLocation, str, None] = StartLocation.LAST,
            connect: bool = True,
    ):
        if self.session:
            raise RuntimeError("Already logged in!")

        if not login_uri:
            login_uri = self.DEFAULT_LOGIN_URI

        if start_location is None:
            start_location = StartLocation.LAST

        # This isn't a symbolic start location and isn't a URI, must be a sim name.
        if start_location not in iter(StartLocation) and not start_location.startswith("uri:"):
            start_location = f"uri:{start_location}&128&128&128"

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
            "start": str(start_location),
            "token": "",
            "version": version("hippolyzer"),
            "options": list(self._options),
        }
        async with self.http_session.post(
                login_uri,
                data=xmlrpc.client.dumps((payload,), "login_to_simulator"),
                headers={"Content-Type": "text/xml", "User-Agent": self.settings.USER_AGENT},
                ssl=self.settings.SSL_VERIFY,
        ) as resp:
            resp.raise_for_status()
            login_data = xmlrpc.client.loads((await resp.read()).decode("utf8"))[0][0]
        self.session = HippoClientSession.from_login_data(login_data, self)

        self.session.transport, self.session.protocol = await self._create_transport()
        self._resend_task = asyncio.create_task(self._attempt_resends())
        self.session.message_handler.subscribe("AgentDataUpdate", self._handle_agent_data_update)
        self.session.message_handler.subscribe("AgentGroupDataUpdate", self._handle_agent_group_data_update)

        assert self.session.open_circuit(self.session.regions[-1].circuit_addr)
        if connect:
            region = self.session.regions[-1]
            await region.connect(main_region=True)

    def logout(self):
        if not self.session:
            return
        if self._resend_task:
            self._resend_task.cancel()
            self._resend_task = None

        if self.main_circuit and self.main_circuit.is_alive:
            # Don't need to send reliably, there's a good chance the server won't ACK anyway.
            self.main_circuit.send(
                Message(
                    "LogoutRequest",
                    Block("AgentData", AgentID=self.session.agent_id, SessionID=self.session.id),
                )
            )
        session = self.session
        self.session = None
        for region in session.regions:
            region.disconnect()
        session.transport.close()

    def send_chat(self, message: Union[bytes, str], channel: int = 0, chat_type=ChatType.NORMAL) -> asyncio.Future:
        return self.main_circuit.send_reliable(Message(
            "ChatFromViewer",
            Block("AgentData", SessionID=self.session.id, AgentID=self.session.agent_id),
            Block("ChatData", Message=message, Channel=channel, Type=chat_type),
        ))

    def teleport(self, region_handle: int, local_pos=Vector3(0, 0, 0)) -> asyncio.Future:
        """Synchronously requests a teleport, returning a Future for teleport completion"""
        teleport_fut = asyncio.Future()

        # Send request synchronously, await asynchronously.
        send_fut = self.main_circuit.send_reliable(
            Message(
                'TeleportLocationRequest',
                Block('AgentData', AgentID=self.session.agent_id, SessionID=self.session.id),
                Block('Info', RegionHandle=region_handle, Position=local_pos, fill_missing=True),
            )
        )

        async def _handle_teleport():
            # Subscribe first, we may receive an event before we receive the packet ACK.
            with self.session.message_handler.subscribe_async(
                    ("TeleportLocal", "TeleportFailed", "TeleportFinish"),
            ) as get_tp_done_msg:
                try:
                    await send_fut
                except Exception as e:
                    # Pass along error if we failed to send reliably.
                    teleport_fut.set_exception(e)
                    return

                # Wait for a message that says we're done the teleport
                msg = await get_tp_done_msg()
                if msg.name == "TeleportFailed":
                    teleport_fut.set_exception(RuntimeError("Failed to teleport"))
                elif msg.name == "TeleportLocal":
                    # Within the sim, nothing else we need to do
                    teleport_fut.set_result(None)
                elif msg.name == "TeleportFinish":
                    # Non-local TP, wait until we receive the AgentMovementComplete to
                    # set the finished signal.

                    # Region should be registered by this point, wait for it to connect
                    try:
                        # just fail if it takes longer than 30 seconds for the handshake to complete
                        await asyncio.wait_for(self.session.region_by_handle(region_handle).connected, 30)
                    except Exception as e:
                        teleport_fut.set_exception(e)
                        return
                    teleport_fut.set_result(None)

        asyncio.create_task(_handle_teleport())

        return teleport_fut

    async def _attempt_resends(self):
        while True:
            if self.session is None:
                break
            for region in self.session.regions:
                if not region.circuit.is_alive:
                    continue
                region.circuit.resend_unacked()
            await asyncio.sleep(0.5)

    def _handle_agent_data_update(self, msg: Message):
        self.session.active_group = msg["AgentData"]["ActiveGroupID"]

    def _handle_agent_group_data_update(self, msg: Message):
        self.session.groups.clear()
        for block in msg["GroupData"]:
            self.session.groups.add(block["GroupID"])
