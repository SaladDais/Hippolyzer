import unittest

from mitmproxy.test import tflow, tutils

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.http_proxy import SerializedCapData
from hippolyzer.lib.proxy.message_logger import HTTPMessageLogEntry
from hippolyzer.lib.proxy.sessions import SessionManager


class TestHTTPFlows(unittest.TestCase):
    def setUp(self) -> None:
        self.session_manager = SessionManager()
        self.session = self.session = self.session_manager.create_session({
            "session_id": UUID.random(),
            "secure_session_id": UUID.random(),
            "agent_id": UUID.random(),
            "circuit_code": 0,
            "sim_ip": "127.0.0.1",
            "sim_port": "1",
            "seed_capability": "https://test.localhost:4/foo",
        })

    def test_request_formatting(self):
        req = tutils.treq(host="example.com", port=80)
        resp = tutils.tresp()
        fake_flow = tflow.tflow(req=req, resp=resp)
        fake_flow.metadata["cap_data_ser"] = SerializedCapData(
            cap_name="FakeCap",
            session_id=str(self.session.id),
            base_url="http://example.com",
        )
        flow = HippoHTTPFlow.from_state(fake_flow.get_state(), self.session_manager)
        entry = HTTPMessageLogEntry(flow)
        self.assertEqual(entry.request(beautify=True), """GET [[FakeCap]]/path HTTP/1.1\r
# http://example.com/path\r
header: qvalue\r
content-length: 7\r
\r
content""")
