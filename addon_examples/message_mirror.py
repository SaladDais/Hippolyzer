"""
Message Mirror

Re-routes messages through the circuit of another agent running through this proxy,
rewriting the messages to use the credentials tied to that circuit.

Useful if you need to quickly QA authorization checks on a message handler or script.
Or if you want to chat as two people at once. Whatever.
Also shows some advanced ways of managing / rerouting Messages and HTTP flows.

Fiddle with the values of `SEND_NORMALLY` and `MIRROR` to change how and which
messages get moved to other circuits.

Usage: /524 mirror_to <mirror_agent_uuid>
To Disable: /524 mirror_to
"""

import weakref
from typing import Optional

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.message.template_dict import DEFAULT_TEMPLATE_DICT
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.proxy.addon_utils import BaseAddon, SessionProperty, show_message
from hippolyzer.lib.proxy.commands import handle_command, Parameter, parse_bool
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.caps import CapData, CapType
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager

# Things that make no sense to mirror, or will make everything explode if mirrored.
SEND_NORMALLY = {
    'StartPingCheck', 'CompletePingCheck', 'PacketAck', 'SimulatorViewerTimeMessage', 'SimStats',
    'SoundTrigger', 'EventQueueGet', 'GetMesh', 'GetMesh2', 'ParcelDwellRequest', 'ViewerEffect', 'ViewerStats',
    'ParcelAccessListRequest', 'FirestormBridge', 'AvatarRenderInfo', 'ParcelPropertiesRequest', 'GetObjectCost',
    'RequestMultipleObjects', 'GetObjectPhysicsData', 'GetExperienceInfo', 'RequestTaskInventory', 'AgentRequestSit',
    'MuteListRequest', 'UpdateMuteListEntry', 'RemoveMuteListEntry', 'RequestImage',
    'AgentThrottle', 'UseCircuitCode', 'AgentWearablesRequest', 'AvatarPickerRequest', 'CloseCircuit',
    'CompleteAgentMovement', 'RegionHandshakeReply', 'LogoutRequest', 'ParcelPropertiesRequest',
    'ParcelPropertiesRequestByID', 'MapBlockRequest', 'MapLayerRequest', 'MapItemRequest', 'MapNameRequest',
    'ParcelAccessListRequest', 'AvatarPropertiesRequest', 'DirFindQuery',
    'SetAlwaysRun', 'GetDisplayNames', 'ViewerMetrics', 'AgentResume', 'AgentPause',
    'ViewerAsset', 'GetTexture', 'UUIDNameRequest', 'AgentUpdate', 'AgentAnimation'
    # Would just be confusing for everyone
    'ImprovedInstantMessage',
    # Xfer system isn't authed to begin with, and duping Xfers can lead to premature file deletion. Skip.
    'RequestXfer', 'ConfirmXferPacket', 'AbortXfer', 'SendXferPacket',
}

# Messages that _must_ be sent normally, but are worth mirroring onto the target session to see how
# they would respond
MIRROR = {
    'RequestObjectPropertiesFamily', 'ObjectSelect', 'RequestObjectProperties', 'TransferRequest',
    'RequestMultipleObjects', 'RequestTaskInventory', 'FetchInventory2', 'ScriptDialogReply',
    'ObjectDeselect', 'GenericMessage', 'ChatFromViewer'
}

for msg_name in DEFAULT_TEMPLATE_DICT.message_templates.keys():
    # There are a lot of these.
    if msg_name.startswith("Group") and msg_name.endswith("Request"):
        MIRROR.add(msg_name)


class MessageMirrorAddon(BaseAddon):
    mirror_target_agent: Optional[UUID] = SessionProperty(None)
    mirror_use_target_session: bool = SessionProperty(True)
    mirror_use_target_agent: bool = SessionProperty(True)

    @handle_command(target_agent=Parameter(UUID, optional=True))
    async def mirror_to(self, session: Session, _region, target_agent: Optional[UUID] = None):
        """
        Send this session's outbound messages over another proxied agent's circuit
        """
        if target_agent:
            if target_agent == session.agent_id:
                show_message("Can't mirror our own session")
                target_agent = None
            elif not any(s.agent_id == target_agent for s in session.session_manager.sessions):
                show_message(f"No active proxied session for agent {target_agent}")
                target_agent = None

        self.mirror_target_agent = target_agent
        if target_agent:
            show_message(f"Mirroring to {target_agent}")
        else:
            show_message("Message mirroring disabled")

    @handle_command(enabled=parse_bool)
    async def set_mirror_use_target_session(self, _session, _region, enabled):
        """Replace the original session ID with the target session's ID when mirroring"""
        self.mirror_use_target_session = enabled

    @handle_command(enabled=parse_bool)
    async def set_mirror_use_target_agent(self, _session, _region, enabled):
        """Replace the original agent ID with the target agent's ID when mirroring"""
        self.mirror_use_target_agent = enabled

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if message.direction != Direction.OUT:
            return

        if not self.mirror_target_agent:
            return

        if message.name in SEND_NORMALLY:
            return

        target_session = None
        for poss_session in session.session_manager.sessions:
            if poss_session.agent_id == self.mirror_target_agent:
                target_session = poss_session

        if not target_session:
            print("Couldn't find target session?")
            return

        target_region = None
        for poss_region in target_session.regions:
            if poss_region.circuit_addr == region.circuit_addr:
                target_region = poss_region

        if not target_region:
            print("Couldn't find equivalent target region?")
            return

        # Send the message normally first if we're mirroring
        if message.name in MIRROR:
            region.circuit.send(message)

        # We're going to send the message on a new circuit, we need to take
        # it so we get a new packet ID and clean ACKs
        message = message.take()

        self._lludp_fixups(target_session, message)
        target_region.circuit.send(message)
        return True

    def _lludp_fixups(self, target_session: Session, message: Message):
        if "AgentData" in message:
            agent_block = message["AgentData"][0]
            if "AgentID" in agent_block and self.mirror_use_target_agent:
                agent_block["AgentID"] = target_session.agent_id
            if "SessionID" in agent_block and self.mirror_use_target_session:
                agent_block["SessionID"] = target_session.id

        if message.name == "TransferRequest":
            transfer_block = message["TransferInfo"][0]
            # This is a duplicated message so we need to give it a new ID
            transfer_block["TransferID"] = UUID.random()
            params = transfer_block.deserialize_var("Params")
            # This kind of Transfer might not even use agent credentials
            if self.mirror_use_target_agent and hasattr(params, 'AgentID'):
                params.AgentID = target_session.agent_id
            if self.mirror_use_target_session and hasattr(params, 'SessionID'):
                params.SessionID = target_session.id
            transfer_block.serialize_var("Params", params)

    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        # Already mirrored, ignore.
        if flow.is_replay:
            return

        cap_data = flow.cap_data
        if not cap_data:
            return
        if cap_data.cap_name in SEND_NORMALLY:
            return

        if cap_data.asset_server_cap:
            return
        # Likely doesn't have an exact equivalent in the target session, this is a temporary
        # cap like an uploader URL or a stats URL.
        if cap_data.type == CapType.TEMPORARY:
            return

        session: Optional[Session] = cap_data.session and cap_data.session()
        if not session:
            return

        region: Optional[ProxiedRegion] = cap_data.region and cap_data.region()
        if not region:
            return

        # Session-scoped, so we need to know if we have a session before checking
        if not self.mirror_target_agent:
            return

        target_session: Optional[Session] = None
        for poss_session in session.session_manager.sessions:
            if poss_session.agent_id == self.mirror_target_agent:
                target_session = poss_session
        if not target_session:
            return

        caps_source = target_session
        target_region: Optional[ProxiedRegion] = None
        if region:
            target_region = None
            for poss_region in target_session.regions:
                if poss_region.circuit_addr == region.circuit_addr:
                    target_region = poss_region

            if not target_region:
                print("No region in cap?")
                return
            caps_source = target_region

        new_base_url = caps_source.cap_urls.get(cap_data.cap_name)
        if not new_base_url:
            print("No equiv cap?")
            return

        if cap_data.cap_name in MIRROR:
            flow = flow.copy()

        # Have the cap data reflect the new URL we're pointing at
        flow.metadata["cap_data"] = CapData(
            cap_name=cap_data.cap_name,
            region=weakref.ref(target_region) if target_region else None,
            session=weakref.ref(target_session),
            base_url=new_base_url,
        )

        # Tack any params onto the new base URL for the cap
        new_url = new_base_url + flow.request.url[len(cap_data.base_url):]
        flow.request.url = new_url

        if cap_data.cap_name in MIRROR:
            self._replay_flow(flow, session.session_manager)

    def _replay_flow(self, flow: HippoHTTPFlow, session_manager: SessionManager):
        # Work around mitmproxy bug, changing the URL updates the Host header, which may
        # cause it to drop the port even when it shouldn't have. Fix the host header.
        if flow.request.port not in (80, 443) and ":" not in flow.request.host_header:
            flow.request.host_header = f"{flow.request.host}:{flow.request.port}"
        # Should get repopulated when it goes back through the MITM addon
        flow.metadata.pop("cap_data_ser", None)
        flow.metadata.pop("cap_data", None)
        proxy_queue = session_manager.flow_context.to_proxy_queue
        proxy_queue.put_nowait(("replay", None, flow.get_state()))


addons = [MessageMirrorAddon()]
