import abc

from mitmproxy.addons import asgiapp

from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager


async def serve(app, flow: HippoHTTPFlow):
    """Serve a request based on a Hippolyzer HTTP flow using a provided app"""
    await asgiapp.serve(app, flow.flow)
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
        region.register_proxy_cap(self.CAP_NAME)

    def handle_session_init(self, session: Session):
        for region in session.regions:
            region.register_proxy_cap(self.CAP_NAME)

    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        if flow.cap_data.cap_name != self.CAP_NAME:
            return
        # This request may take a while to generate a response for, take it out of the normal
        # HTTP handling flow and handle it in a async task.
        # TODO: Make all HTTP handling hooks async so this isn't necessary
        self._schedule_task(serve(self.APP, flow.take()))
