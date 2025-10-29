"""
Try and diagnose very slow avatar appearance loads when the avatars first come on the scene

I guess use LEAP or something to detect when things _actually_ declouded.
"""
from typing import *

import dataclasses
import datetime as dt

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.base.templates import PCode
from hippolyzer.lib.proxy.addon_utils import BaseAddon, GlobalProperty
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager


@dataclasses.dataclass
class AvatarBakeRequest:
    requested: dt.datetime
    received: Optional[dt.datetime] = None


@dataclasses.dataclass
class AvatarAppearanceRecord:
    object_received: dt.datetime
    """When we learned about the agent as an object"""
    appearance_received: Optional[dt.datetime] = None
    """When AvatarAppearance was first received"""
    bake_requests: Dict[str, AvatarBakeRequest] = dataclasses.field(default_factory=dict)
    """Layer name -> request / response details"""


class AppearanceDelayTrackerAddon(BaseAddon):
    # Should be able to access this in the REPL
    # Normally we'd use a session property, but we may not have a proper session context for some requests
    av_appearance_data: Dict[UUID, AvatarAppearanceRecord] = GlobalProperty(dict)

    def handle_object_updated(self, session: Session, region: ProxiedRegion,
                              obj: Object, updated_props: Set[str], msg: Optional[Message]):
        if obj.PCode == PCode.AVATAR and obj.FullID not in self.av_appearance_data:
            self.av_appearance_data[obj.FullID] = AvatarAppearanceRecord(object_received=dt.datetime.now())

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if message.name != "AvatarAppearance":
            return
        agent_id = message["Sender"]["ID"]
        appearance_data = self.av_appearance_data.get(agent_id)
        if not appearance_data:
            print(f"Got appearance for {agent_id} without knowing about object?")
            return

        if appearance_data.appearance_received:
            return
        appearance_data.appearance_received = dt.datetime.now()

    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        if not flow.cap_data:
            return
        if flow.cap_data.cap_name != "AppearanceService":
            return

        agent_id = UUID(flow.request.url.split('/')[-3])
        slot_name = flow.request.url.split('/')[-2]
        appearance_data = self.av_appearance_data.get(agent_id)
        if not appearance_data:
            print(f"Got AppearanceService req for {agent_id} without knowing about object?")
            return
        if slot_name in appearance_data.bake_requests:
            # We already requested this slot before
            return
        appearance_data.bake_requests[slot_name] = AvatarBakeRequest(requested=dt.datetime.now())

    def handle_http_response(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        if not flow.cap_data:
            return
        if flow.cap_data.cap_name != "AppearanceService":
            return

        agent_id = UUID(flow.request.url.split('/')[-3])
        slot_name = flow.request.url.split('/')[-2]
        appearance_data = self.av_appearance_data.get(agent_id)
        if not appearance_data:
            return
        slot_details = appearance_data.bake_requests.get(slot_name)
        if not slot_details:
            return
        slot_details.received = dt.datetime.now()


addons = [AppearanceDelayTrackerAddon()]
