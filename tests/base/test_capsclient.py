import unittest

import aiohttp
import aioresponses
from yarl import URL

from hippolyzer.lib.base.network.caps_client import CapsClient


class TestCapsClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.caps = {}
        self.caps_client = CapsClient(self.caps)

    async def test_bare_url_works(self):
        with aioresponses.aioresponses() as m:
            m.get("https://example.com/", body=b"foo")
            async with self.caps_client.get("https://example.com/") as resp:
                self.assertEqual(await resp.read(), b"foo")

    async def test_own_session_works(self):
        with aioresponses.aioresponses() as m:
            async with aiohttp.ClientSession() as sess:
                m.get("https://example.com/", body=b"foo")
                async with self.caps_client.get("https://example.com/", session=sess) as resp:
                    self.assertEqual(await resp.read(), b"foo")

    async def test_read_llsd(self):
        with aioresponses.aioresponses() as m:
            m.get("https://example.com/", body=b"<llsd><integer>2</integer></llsd>")
            async with self.caps_client.get("https://example.com/") as resp:
                self.assertEqual(await resp.read_llsd(), 2)

    async def test_caps(self):
        self.caps.update({"Foobar": "https://example.com/"})
        with aioresponses.aioresponses() as m:
            m.post("https://example.com/baz", body=b"ok")
            data = {"hi": "hello"}
            headers = {"Foo": "bar"}
            async with self.caps_client.post("Foobar", path="baz", llsd=data, headers=headers) as resp:
                self.assertEqual(await resp.read(), b"ok")

            # Our original dict should not have been touched
            self.assertEqual(headers, {"Foo": "bar"})

            req_key = ("POST", URL("https://example.com/baz"))
            req_body = m.requests[req_key][0].kwargs['data']
            self.assertEqual(req_body, b'<?xml version="1.0" ?><llsd><map><key>hi</key><string>hello'
                                       b'</string></map></llsd>')

            with self.assertRaises(KeyError):
                with self.caps_client.get("BadCap"):
                    assert False
