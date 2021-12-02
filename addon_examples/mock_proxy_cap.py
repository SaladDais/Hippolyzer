"""
Example of proxy-provided caps

Useful for mocking out a cap that isn't actually implemented by the server
while developing the viewer-side pieces of it.

Implements a cap that accepts an `obj_id` UUID query parameter and returns
the name of the object.
"""

import asyncio

from mitmproxy import http

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager


class MockProxyCapExampleAddon(BaseAddon):
    def handle_region_registered(self, session: Session, region: ProxiedRegion):
        # Register a fake URL for our cap. This will add the cap URL to the Seed
        # response that gets sent back to the client if that cap name was requested.
        if "GetObjectNameExample" not in region.cap_urls:
            region.register_proxy_cap("GetObjectNameExample")

    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        if flow.cap_data.cap_name != "GetObjectNameExample":
            return
        if flow.request.method != "GET":
            return
        # This request may take a while to generate a response for, take it out of the normal
        # HTTP handling flow and handle it in a async task.
        # TODO: Make all HTTP handling hooks async so this isn't necessary
        self._schedule_task(self._handle_request(flow.take()))

    async def _handle_request(self, flow: HippoHTTPFlow):
        try:
            obj_id = UUID(flow.request.query['obj_id'])
            obj_mgr = flow.cap_data.region().objects
            obj = obj_mgr.lookup_fullid(obj_id)
            if not obj:
                flow.response = http.Response.make(
                    status_code=404,
                    content=f"Couldn't find {obj_id!r}".encode("utf8"),
                    headers={"Content-Type": "text/plain"},
                )
                flow.release()
                return

            try:
                await asyncio.wait_for(obj_mgr.request_object_properties(obj)[0], 1.0)
            except asyncio.TimeoutError:
                flow.response = http.Response.make(
                    status_code=404,
                    content=f"Timed out requesting {obj_id!r}".encode("utf8"),
                    headers={"Content-Type": "text/plain"},
                )
                flow.release()
                return

            flow.response = http.Response.make(
                content=obj.Name.encode("utf8"),
                headers={"Content-Type": "text/plain"},
            )
            flow.release()
        except:
            flow.response = http.Response.make(
                status_code=500,
                content=b"The server is on fire",
                headers={"Content-Type": "text/plain"},
            )
            flow.release()


addons = [MockProxyCapExampleAddon()]
