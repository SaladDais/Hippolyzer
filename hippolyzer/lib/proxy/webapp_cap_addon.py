import abc

from mitmproxy.addons import asgiapp
from mitmproxy.controller import DummyReply

from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager


async def serve(app, flow: HippoHTTPFlow):
    """Serve a request based on a Hippolyzer HTTP flow using a provided app"""
    # Shove this on mitmproxy's flow object so asgiapp doesn't explode when it tries
    # to commit the flow reply. Our take / commit semantics are different than mitmproxy
    # proper, so we ignore what mitmproxy sets here anyhow.
    flow.flow.reply = DummyReply()
    flow.flow.reply.take()
    await asgiapp.serve(app, flow.flow)
    flow.flow.reply = None
    # Send the modified flow object back to mitmproxy
    flow.resume()


class WebAppCapAddon(BaseAddon, abc.ABC):
    """
    Addon that provides a cap via an ASGI webapp

    Handles all registration of the cap URL and routing of the request.
    """
    CAP_NAME: str
    APP: any

    def handle_region_registered(self, session: Session, region: ProxiedRegion):
        # Register a fake URL for our cap. This will add the cap URL to the Seed
        # response that gets sent back to the client if that cap name was requested.
        if self.CAP_NAME not in region.cap_urls:
            region.register_proxy_cap(self.CAP_NAME)

    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        if flow.cap_data.cap_name != self.CAP_NAME:
            return
        # This request may take a while to generate a response for, take it out of the normal
        # HTTP handling flow and handle it in a async task.
        # TODO: Make all HTTP handling hooks async so this isn't necessary
        self._schedule_task(serve(self.APP, flow.take()))
