from mitmproxy.test import tflow, tutils

from hippolyzer.lib.proxy.caps import CapType
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.message_logger import HTTPMessageLogEntry
from hippolyzer.lib.proxy.test_utils import BaseProxyTest


class TestHTTPFlows(BaseProxyTest):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.region = self.session.register_region(
            ("127.0.0.1", 2),
            "https://test.localhost:4/foo",
            handle=90,
        )
        self.region.update_caps({
            "FakeCap": "http://example.com",
            "ViewerAsset": "http://assets.example.com",
        })

    async def test_request_formatting(self):
        req = tutils.treq(host="example.com", port=80)
        fake_flow = tflow.tflow(req=req, resp=tutils.tresp())
        flow = HippoHTTPFlow.from_state(fake_flow.get_state(), self.session_manager)
        # Make sure cap resolution works correctly
        flow.cap_data = self.session_manager.resolve_cap(flow.request.url)
        entry = HTTPMessageLogEntry(flow)
        self.assertEqual(entry.request(beautify=True), """GET [[FakeCap]]/path HTTP/1.1\r
# http://example.com/path\r
header: qvalue\r
content-length: 7\r
\r
content""")

    async def test_binary_request_formatting(self):
        req = tutils.treq(host="example.com", port=80)
        fake_flow = tflow.tflow(req=req, resp=tutils.tresp())
        flow = HippoHTTPFlow.from_state(fake_flow.get_state(), self.session_manager)
        # This should trigger the escaped body path without changing content-length
        flow.request.content = b"c\x00ntent"
        entry = HTTPMessageLogEntry(flow)
        self.assertEqual(entry.request(beautify=True), """GET http://example.com/path HTTP/1.1\r
header: qvalue\r
content-length: 7\r
X-Hippo-Escaped-Body: 1\r
\r
c\\x00ntent""")

    async def test_llsd_response_formatting(self):
        fake_flow = tflow.tflow(req=tutils.treq(), resp=tutils.tresp())
        flow = HippoHTTPFlow.from_state(fake_flow.get_state(), self.session_manager)
        # Half the time LLSD is sent with a random Content-Type and no PI indicating
        # what flavor of LLSD it is. Make sure the sniffing works correctly.
        flow.response.content = b"<llsd><integer>1</integer></llsd>"
        entry = HTTPMessageLogEntry(flow)
        self.assertEqual(entry.response(beautify=True), """HTTP/1.1 200 OK\r
header-response: svalue\r
content-length: 33\r
\r
<?xml version="1.0" ?>
<llsd>
<integer>1</integer>
</llsd>
""")

    async def test_flow_state_serde(self):
        fake_flow = tflow.tflow(req=tutils.treq(host="example.com"), resp=tutils.tresp())
        flow = HippoHTTPFlow.from_state(fake_flow.get_state(), self.session_manager)
        # Make sure cap resolution works correctly
        flow.cap_data = self.session_manager.resolve_cap(flow.request.url)
        flow_state = flow.get_state()
        new_flow = HippoHTTPFlow.from_state(flow_state, self.session_manager)
        self.assertIs(self.session, new_flow.cap_data.session())

    async def test_http_asset_repo(self):
        asset_repo = self.session_manager.asset_repo
        asset_id = asset_repo.create_asset(b"foobar", one_shot=True)
        req = tutils.treq(host="assets.example.com", path=f"/?animatn_id={asset_id}")
        fake_flow = tflow.tflow(req=req)
        flow = HippoHTTPFlow.from_state(fake_flow.get_state(), self.session_manager)
        # Have to resolve cap data so the asset repo knows this is an asset server cap
        flow.cap_data = self.session_manager.resolve_cap(flow.request.url)
        self.assertTrue(asset_repo.try_serve_asset(flow))
        self.assertEqual(b"foobar", flow.response.content)

    async def test_temporary_cap_resolution(self):
        self.region.register_cap("TempExample", "http://not.example.com", CapType.TEMPORARY)
        self.region.register_cap("TempExample", "http://not2.example.com", CapType.TEMPORARY)
        # Resolving the cap should consume it
        cap_data = self.session_manager.resolve_cap("http://not.example.com")
        self.assertEqual(cap_data.cap_name, "TempExample")
        # A CapData object should always be returned, but the cap_name field will be None
        new_cap_data = self.session_manager.resolve_cap("http://not.example.com")
        self.assertIsNone(new_cap_data.cap_name)
        # The second temp cap with the same name should still be in there
        cap_data = self.session_manager.resolve_cap("http://not2.example.com")
        self.assertEqual(cap_data.cap_name, "TempExample")
