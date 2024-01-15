from __future__ import annotations

import asyncio
import math
import multiprocessing
from urllib.parse import urlparse

import aioresponses
from mitmproxy.test import tflow, tutils
from mitmproxy.http import HTTPFlow, Headers
from yarl import URL

from hippolyzer.apps.proxy import run_http_proxy_process
from hippolyzer.lib.base.datatypes import Vector3
from hippolyzer.lib.base.helpers import create_logged_task
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.http_event_manager import MITMProxyEventManager
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.caps import SerializedCapData
from hippolyzer.lib.proxy.sessions import SessionManager
from hippolyzer.lib.proxy.test_utils import BaseProxyTest


class MockAddon(BaseAddon):
    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        flow.metadata["touched_addon"] = True

    def handle_http_response(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        flow.metadata["touched_addon"] = True


class HTTPIntegrationTests(BaseProxyTest):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
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
                headers=Headers((
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

    async def test_asset_server_proxy_wrapper_caps(self):
        # We support "wrapper caps" that disambiguate otherwise ambiguous caps.
        # The URL provided by the sim may not be unique across regions or sessions,
        # in the case of ViewerAsset on agni, so we generate a random hostname
        # as an alias and send that to the viewer instead.
        region = self.session.main_region
        region.update_caps({
            "ViewerAsset": "http://assets.local/foo",
        })
        wrapper_url = region.register_wrapper_cap("ViewerAsset")
        parsed = urlparse(wrapper_url)
        fake_flow = tflow.tflow(req=tutils.treq(
            host=parsed.hostname,
            path="/foo/baz?asset_id=bar",
            port=80,
        ))
        fake_flow.metadata["cap_data_ser"] = SerializedCapData()
        self.flow_context.from_proxy_queue.put(("request", fake_flow.get_state()), True)
        await self._pump_one_event()
        flow_state = self.flow_context.to_proxy_queue.get(True)[2]
        mitm_flow: HTTPFlow = HTTPFlow.from_state(flow_state)
        self.assertIsNotNone(mitm_flow.response)
        self.assertEqual(307, mitm_flow.response.status_code)
        self.assertEqual(
            "http://assets.local/foo/baz?asset_id=bar",
            mitm_flow.response.headers["Location"],
        )


class TestCapsClient(BaseProxyTest):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._setup_default_circuit()
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


class TestMITMProxy(BaseProxyTest):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._setup_default_circuit()
        self.caps_client = self.session.main_region.caps_client
        proxy_port = 9905
        self.session_manager.settings.HTTP_PROXY_PORT = proxy_port

        self.http_proc = multiprocessing.Process(
            target=run_http_proxy_process,
            args=("127.0.0.1", proxy_port, self.session_manager.flow_context),
            daemon=True,
        )
        self.http_proc.start()
        self.session_manager.flow_context.mitmproxy_ready.wait(1.0)

        self.http_event_manager = MITMProxyEventManager(
            self.session_manager,
            self.session_manager.flow_context
        )

    def test_mitmproxy_works(self):
        async def _request_example_com():
            # Pump callbacks from mitmproxy
            _ = create_logged_task(self.http_event_manager.run())
            try:
                async with self.caps_client.get("http://example.com/", timeout=0.5) as resp:
                    self.assertIn(b"Example Domain", await resp.read())
                async with self.caps_client.get("https://example.com/", timeout=0.5) as resp:
                    self.assertIn(b"Example Domain", await resp.read())
            finally:
                # Tell the event pump and mitmproxy they need to shut down
                self.session_manager.flow_context.shutdown_signal.set()
        asyncio.run(_request_example_com())
        self.http_proc.join()
