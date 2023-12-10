from __future__ import annotations

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
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.network.caps_client import CapsClient
from hippolyzer.lib.base.network.transport import ADDR_TUPLE
from hippolyzer.lib.base.transfer_manager import TransferManager
from hippolyzer.lib.base.xfer_manager import XferManager
from hippolyzer.lib.client.asset_uploader import AssetUploader
from hippolyzer.lib.client.object_manager import ClientObjectManager
from hippolyzer.lib.client.state import BaseClientSession, BaseClientRegion, BaseClientSessionManager


class HippoCapsClient(CapsClient):
    def _request_fixups(self, cap_or_url: str, headers: Dict, proxy: Optional[bool], ssl: Any):
        headers["User-Agent"] = f"Hippolyzer/v{version('hippolyzer')}"


class HippoClientRegion(BaseClientRegion):
    def __init__(self, circuit_addr, seed_cap: str, session: HippoClientSession, handle=None):
        super().__init__()
        self.caps = multidict.MultiDict()
        self.objects = ClientObjectManager(proxify(self))
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

    def __init__(self, id, secure_session_id, agent_id, circuit_code, client: Optional[HippoClient] = None,
                 login_data=None):
        super().__init__(id, secure_session_id, agent_id, circuit_code, client, login_data=login_data)
        self.http_session = client.http_session

    def register_region(self, circuit_addr: Optional[ADDR_TUPLE] = None, seed_url: Optional[str] = None,
                        handle: Optional[int] = None) -> HippoClientRegion:
        return super().register_region(circuit_addr, seed_url, handle)  # type:ignore

    def open_circuit(self, near_addr, circuit_addr, transport):
        for region in self.regions:
            if region.circuit_addr == circuit_addr:
                if not region.circuit or not region.circuit.is_alive:
                    region.circuit = Circuit(near_addr, circuit_addr, transport)
                    return True
                if region.circuit and region.circuit.is_alive:
                    # Whatever, already open
                    logging.debug("Tried to re-open circuit for %r" % (circuit_addr,))
                    return True
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

    async def aclose(self):
        await self.http_session.close()

    async def login(self, username: str, password: str, login_uri: Optional[str] = "", agree_to_tos: bool = False):
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
            "start": "home",
            "token": "",
            "version": version("hippolyzer"),
            "options": list(self._options),
        }
        rpc_payload = xmlrpc.client.dumps((payload,), "login_to_simulator")
        async with self.http_session.post(login_uri, data=rpc_payload, headers={"Content-Type": "text/xml"}) as resp:
            resp.raise_for_status()
            print(await resp.read())
