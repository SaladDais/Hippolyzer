from __future__ import annotations

import asyncio
import math

import aioresponses
from mitmproxy.net import http
from mitmproxy.test import tflow, tutils
from mitmproxy.http import HTTPFlow
from yarl import URL

from hippolyzer.lib.base.datatypes import Vector3
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.http_event_manager import MITMProxyEventManager
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.http_proxy import SerializedCapData
from hippolyzer.lib.proxy.message_logger import FilteringMessageLogger
from hippolyzer.lib.proxy.sessions import SessionManager

from .. import BaseProxyTest


class MockAddon(BaseAddon):
    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        flow.metadata["touched_addon"] = True

    def handle_http_response(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        flow.metadata["touched_addon"] = True


class SimpleMessageLogger(FilteringMessageLogger):
    @property
    def entries(self):
        return self._filtered_entries


class HTTPIntegrationTests(BaseProxyTest):
    def setUp(self) -> None:
        super().setUp()
        self.addon = MockAddon()
        AddonManager.init([], self.session_manager, [self.addon])
        self.flow_context = self.session_manager.flow_context
        self.http_event_manager = MITMProxyEventManager(self.session_manager, self.flow_context)
        self._setup_default_circuit()

    async def _pump_one_event(self):
        # If we don't yield then the new entry won't end up in the queue
        await asyncio.sleep(0.001)
        await self.http_event_manager.pump_proxy_event()
        await asyncio.sleep(0.001)

    async def test_http_flow_request(self):
        # mimic a request coming in from mitmproxy over the queue
        fake_flow = tflow.tflow(req=tutils.treq(host="example.com"))
        fake_flow.metadata["cap_data_ser"] = SerializedCapData()
        self.flow_context.from_proxy_queue.put(("request", fake_flow.get_state()), True)
        await self._pump_one_event()
        self.assertTrue(self.flow_context.from_proxy_queue.empty())
        self.assertFalse(self.flow_context.to_proxy_queue.empty())
        flow_state = self.flow_context.to_proxy_queue.get(True)[2]
        mitm_flow: HTTPFlow = HTTPFlow.from_state(flow_state)
        # The response sent back to mitmproxy should have been our modified version
        self.assertEqual(True, mitm_flow.metadata["touched_addon"])

    async def test_http_flow_response(self):
        # mimic a request coming in from mitmproxy over the queue
        fake_flow = tflow.tflow(req=tutils.treq(host="example.com"), resp=tutils.tresp())
        fake_flow.metadata["cap_data_ser"] = SerializedCapData()
        self.flow_context.from_proxy_queue.put(("response", fake_flow.get_state()), True)
        await self._pump_one_event()
        self.assertTrue(self.flow_context.from_proxy_queue.empty())
        self.assertFalse(self.flow_context.to_proxy_queue.empty())
        flow_state = self.flow_context.to_proxy_queue.get(True)[2]
        mitm_flow: HTTPFlow = HTTPFlow.from_state(flow_state)
        # The response sent back to mitmproxy should have been our modified version
        self.assertEqual(True, mitm_flow.metadata["touched_addon"])

    async def test_firestorm_bridge_avatar_z_pos(self):
        # Simulate an avatar with a non-finite Z pos in a coarselocation
        self.session.main_region.objects.state.coarse_locations.update({
            self.session.agent_id: Vector3(1, 2, math.inf),
        })
        self.session.objects._rebuild_avatar_objects()
        # GuessedZ should be picked up for the avatar based on the bridge request
        fake_flow = tflow.tflow(
            req=tutils.treq(host="example.com", content=b'<llsd><string>getZOffsets|'),
            resp=tutils.tresp(
                headers=http.Headers((
                    (b"X-SecondLife-Object-Name", b"#Firestorm LSL Bridge v99999"),
                    (b"X-SecondLife-Owner-Key", str(self.session.agent_id).encode("utf8")),
                )),
                content=f"<llsd><string>{self.session.agent_id}, 2000.0</string></llsd>".encode("utf8")
            ),
        )
        fake_flow.metadata["cap_data_ser"] = SerializedCapData("FirestormBridge")
        fake_flow.metadata["from_browser"] = False
        self.session_manager.flow_context.from_proxy_queue.put(("response", fake_flow.get_state()), True)
        await self._pump_one_event()
        av = tuple(self.session.objects.all_avatars)[0]
        self.assertEqual(Vector3(1, 2, 2000.0), av.RegionPosition)


class TestCapsClient(BaseProxyTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_default_circuit()
        self.caps = {}
        self.caps_client = self.session.main_region.caps_client

    async def test_requests_proxied_by_default(self):
        with aioresponses.aioresponses() as m:
            m.get("http://example.com/", body=b"foo")
            async with self.caps_client.get("http://example.com/") as resp:
                self.assertEqual(await resp.read(), b"foo")
            kwargs = m.requests[("GET", URL("http://example.com/"))][0].kwargs
        # Request should have been proxied, with a header marking it
        self.assertEqual(kwargs['headers']["X-Hippo-Injected"], "1")
        self.assertEqual(kwargs['proxy'], "http://127.0.0.1:9062")
