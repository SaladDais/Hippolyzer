from __future__ import annotations

import asyncio
import logging
import multiprocessing
import queue
from typing import *
import urllib.parse
import weakref
import xmlrpc.client

import defusedxml.ElementTree
import defusedxml.xmlrpc
import mitmproxy.http

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.message.llsd_msg_serializer import LLSDMessageSerializer
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.region import ProxiedRegion, CapType
from hippolyzer.lib.proxy.sessions import SessionManager, CapData, Session
from hippolyzer.lib.proxy.http_proxy import HTTPFlowContext


def apply_security_monkeypatches():
    defusedxml.xmlrpc.monkey_patch()
    llsd.fromstring = defusedxml.ElementTree.fromstring


apply_security_monkeypatches()


class MITMProxyEventManager:
    """
    Handles HTTP request and response events from the mitmproxy process
    """

    UPLOAD_CREATING_CAPS = {
        "NewFileAgentInventory", "UpdateGestureAgentInventory", "UpdateGestureTaskInventory",
        "UpdateNotecardAgentInventory", "UpdateNotecardTaskInventory",
        "UpdateScriptAgent", "UpdateScriptTask",
        "UpdateSettingsAgentInventory", "UpdateSettingsTaskInventory",
        "UploadBakedTexture",
    }

    def __init__(self, session_manager: SessionManager, flow_context: HTTPFlowContext):
        self.session_manager: SessionManager = weakref.proxy(session_manager)
        self.from_proxy_queue: multiprocessing.Queue = flow_context.from_proxy_queue
        self.to_proxy_queue: multiprocessing.Queue = flow_context.to_proxy_queue
        self.shutdown_signal: multiprocessing.Event = flow_context.shutdown_signal
        self.llsd_message_serializer = LLSDMessageSerializer()
        self._asset_server_proxied = False

    async def run(self):
        while not self.shutdown_signal.is_set():
            try:
                await self.pump_proxy_event()
            except:
                logging.exception("Exploded when handling parsed packets")

    async def pump_proxy_event(self):
        try:
            event_type, flow_state = self.from_proxy_queue.get(False)
        except queue.Empty:
            await asyncio.sleep(0.001)
            return

        flow = HippoHTTPFlow.from_state(flow_state, self.session_manager)
        try:
            if event_type == "request":
                self._handle_request(flow)
                # A response was injected early in the cycle, we won't get a response
                # callback from mitmproxy so just log it now.
                message_logger = self.session_manager.message_logger
                if message_logger and flow.response_injected:
                    message_logger.log_http_response(flow)
            elif event_type == "response":
                self._handle_response(flow)
            else:
                raise Exception(f"Unknown mitmproxy event type {event_type}")
        finally:
            # If someone has taken this request out of the regular callback flow,
            # they'll manually send a callback at some later time.
            if not flow.taken:
                self.to_proxy_queue.put(("callback", flow.id, flow.get_state()))

    def _handle_request(self, flow: HippoHTTPFlow):
        url = flow.request.url
        cap_data = self.session_manager.resolve_cap(url)
        flow.cap_data = cap_data
        # Don't do anything special with the proxy's own requests,
        # we only pass it through for logging purposes.
        if flow.request_injected:
            return

        # The local asset repo gets first bite at the apple
        if cap_data and cap_data.asset_server_cap:
            if self.session_manager.asset_repo.try_serve_asset(flow):
                print(f"Served asset for {flow.request.pretty_url}")
                return

        AddonManager.handle_http_request(flow)
        if cap_data and cap_data.cap_name.endswith("ProxyWrapper"):
            orig_cap_name = cap_data.cap_name.rsplit("ProxyWrapper", 1)[0]
            orig_cap_url = cap_data.region().caps[orig_cap_name]
            split_orig_url = urllib.parse.urlsplit(orig_cap_url)
            orig_cap_host = split_orig_url[1]

            # Not a req we want to handle, so redirect to the original, unproxied URL
            split_req_url = list(urllib.parse.urlsplit(flow.request.url))
            split_req_url[1] = orig_cap_host
            redir_url = urllib.parse.urlunsplit(split_req_url)

            # We can't redirect because the URL we redirect to will be proxied as well.
            # Don't make them eat the cost of the redirect too, just rewrite the URL
            # we'll make the request to.
            # We also need to do this if an addon indicated the response shouldn't be streamed
            # because it needs to inspect or mutate it.
            if not flow.can_stream or self._asset_server_proxied:
                flow.request.url = redir_url
            else:
                flow.response = mitmproxy.http.HTTPResponse.make(
                    307,
                    # Can't provide explanation in the body because this results in failing Range requests under
                    # mitmproxy that return garbage data. Chances are there's weird interactions
                    # between HTTP/1.x pipelining and range requests under mitmproxy that no other
                    # applications have hit. If that's a concern then Connection: close should be used.
                    b"",
                    {
                        "Connection": "keep-alive",
                        "Location": redir_url,
                    }
                )
        elif cap_data and cap_data.asset_server_cap:
            # Both the wrapper request and the actual asset server request went through
            # the proxy
            self._asset_server_proxied = True
            logging.warning("noproxy not used, switching to URI rewrite strategy")
        elif not cap_data:
            if self._is_login_request(flow):
                # Not strictly a Cap, but makes it easier to filter on.
                flow.cap_data = CapData(cap_name="LoginRequest")

        if cap_data and cap_data.type == CapType.PROXY_ONLY:
            # A proxy addon was supposed to respond itself, but it didn't.
            if not flow.taken and not flow.response_injected:
                flow.response = mitmproxy.http.HTTPResponse.make(
                    500,
                    b"Proxy didn't handle proxy-only Cap correctly",
                    {
                        "Content-Type": "text/plain",
                        "Connection": "close",
                    }
                )

    @classmethod
    def _is_login_request(cls, flow: HippoHTTPFlow):
        """LoginURI independent login request sniffer"""
        # Probably a request from the internal browser
        if flow.from_browser:
            return False
        # Could it potentially be an XML-RPC POST?
        if flow.request.headers.get("Content-Type") not in ("text/xml", "application/xml"):
            return False
        if flow.request.method != "POST" or not flow.request.content:
            return False
        # Probably SL login, allow without trying to sniff XML-RPC request body
        if flow.request.pretty_url.endswith("/login.cgi"):
            return True
        if flow.request.content.startswith(
                b'<?xml version="1.0"?><methodCall><methodName>login_to_simulator'):
            return True
        return False

    def _handle_response(self, flow: HippoHTTPFlow):
        message_logger = self.session_manager.message_logger
        if message_logger:
            message_logger.log_http_response(flow)

        # Don't handle responses for requests injected by the proxy
        if flow.request_injected:
            return

        if AddonManager.handle_http_response(flow):
            return

        status = flow.response.status_code
        cap_data: Optional[CapData] = flow.metadata["cap_data"]

        if cap_data:
            if status != 200:
                return

            if cap_data.cap_name == "LoginRequest":
                self._handle_login_flow(flow)
                return
            try:
                session = cap_data.session and cap_data.session()
                if not session:
                    return
                session.http_message_handler.handle(flow)

                region = cap_data.region and cap_data.region()
                if not region:
                    return

                region.http_message_handler.handle(flow)

                if cap_data.cap_name == "Seed":
                    parsed = llsd.parse_xml(flow.response.content)
                    logging.debug("Got seed cap for %r : %r" % (cap_data, parsed))
                    region.update_caps(parsed)

                    # On LL's grid these URIs aren't unique across sessions or regions,
                    # so we get request attribution by replacing them with a unique
                    # alias URI.
                    logging.debug("Replacing GetMesh caps with wrapped versions")
                    wrappable_caps = {"GetMesh2", "GetMesh", "GetTexture", "ViewerAsset"}
                    for cap_name in wrappable_caps:
                        if cap_name in parsed:
                            parsed[cap_name] = region.register_wrapper_cap(cap_name)
                    flow.response.content = llsd.format_pretty_xml(parsed)
                elif cap_data.cap_name == "EventQueueGet":
                    parsed_eq_resp = llsd.parse_xml(flow.response.content)
                    if parsed_eq_resp:
                        old_events = parsed_eq_resp["events"]
                        new_events = []
                        for event in old_events:
                            if not self._handle_eq_event(cap_data.session(), region, event):
                                new_events.append(event)
                        # Add on any fake events that've been queued by addons
                        eq_manager = cap_data.region().eq_manager
                        new_events.extend(eq_manager.take_events())
                        parsed_eq_resp["events"] = new_events
                        if old_events and not new_events:
                            # Need at least one event or the viewer will refuse to ack!
                            new_events.append({"message": "NOP", "body": {}})
                    flow.response.content = llsd.format_pretty_xml(parsed_eq_resp)
                elif cap_data.cap_name in self.UPLOAD_CREATING_CAPS:
                    if not region:
                        return
                    parsed = llsd.parse_xml(flow.response.content)
                    if "uploader" in parsed:
                        region.register_temporary_cap(cap_data.cap_name + "Uploader", parsed["uploader"])
            except:
                logging.exception("OOPS, blew up in HTTP proxy!")

    def _handle_login_flow(self, flow: HippoHTTPFlow):
        resp = xmlrpc.client.loads(flow.response.content)[0][0]  # type: ignore
        sess = self.session_manager.create_session(resp)
        AddonManager.handle_session_init(sess)
        flow.cap_data = CapData("LoginRequest", session=weakref.ref(sess))

    def _handle_eq_event(self, session: Session, region: ProxiedRegion, event: Dict[str, Any]):
        logging.debug("Event received on %r: %r" % (self, event))
        message_logger = self.session_manager.message_logger
        if message_logger:
            message_logger.log_eq_event(session, region, event)
        handle_event = AddonManager.handle_eq_event(session, region, event)
        if handle_event is True:
            # Addon handled the event and didn't want it sent to the viewer
            return True

        msg = None
        # Handle events that inform us about new regions
        sim_addr, sim_handle, sim_seed = None, None, None
        if self.llsd_message_serializer.can_handle(event["message"]):
            msg = self.llsd_message_serializer.deserialize(event)
        # Sim is asking us to talk to a neighbour
        if event["message"] == "EstablishAgentCommunication":
            ip_split = event["body"]["sim-ip-and-port"].split(":")
            sim_addr = (ip_split[0], int(ip_split[1]))
            sim_seed = event["body"]["seed-capability"]
        # We teleported or cross region, opening comms to new sim
        elif msg and msg.name in ("TeleportFinish", "CrossedRegion"):
            sim_block = msg.get_block("RegionData", msg.get_block("Info"))[0]
            sim_addr = (sim_block["SimIP"], sim_block["SimPort"])
            sim_handle = sim_block["RegionHandle"]
            sim_seed = sim_block["SeedCapability"]
        # Sim telling us about a neighbour
        elif msg and msg.name == "EnableSimulator":
            sim_block = msg["SimulatorInfo"][0]
            sim_addr = (sim_block["IP"], sim_block["Port"])
            sim_handle = sim_block["Handle"]

        # Register a region if this message was telling us about a new one
        if sim_addr is not None:
            session.register_region(sim_addr, handle=sim_handle, seed_url=sim_seed)
        return False
