from typing import *

import asyncio
import unittest
from unittest import mock

from hippolyzer.lib.voice.client import VoiceClient
from hippolyzer.lib.voice.connection import VivoxConnection


def _make_transport(write_func):
    transport = mock.Mock()
    transport.write.side_effect = write_func
    transport.is_closing.return_value = False
    return transport


def _make_protocol(transport: Any):
    protocol = mock.Mock(transport=transport)
    protocol._drain_helper = mock.AsyncMock()
    return protocol


class TestVivoxConnection(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._writer_buf = bytearray()
        self._transport = _make_transport(self._writer_buf.extend)
        self._protocol = _make_protocol(self._transport)
        self.reader = asyncio.StreamReader()
        self.writer = asyncio.StreamWriter(self._transport, self._protocol, self.reader, asyncio.get_event_loop())
        self.vivox_connection = VivoxConnection(self.reader, self.writer)

    async def test_read_request(self):
        self.reader.feed_data(
            b'<Request requestId="foobar" action="Aux.GetRenderDevices.1"><Foo>1</Foo></Request>\n\n\n'
        )
        self.reader.feed_eof()
        msg_type, msg_action, request_id, body = await self.vivox_connection.read_message()
        self.assertEqual("Request", msg_type)
        self.assertEqual("Aux.GetRenderDevices.1", msg_action)
        self.assertEqual("foobar", request_id)
        self.assertDictEqual({"Foo": "1"}, body)

    async def test_read_response(self):
        self.reader.feed_data(
            b'<Response requestId="foobar" action="Connector.SetLocalMicVolume.1"><ReturnCode>0</ReturnCode>'
            b'<Results><StatusCode>0</StatusCode><StatusString /></Results>'
            b'<InputXml><Request/></InputXml></Response>\n\n\n'
        )
        self.reader.feed_eof()
        msg_type, msg_action, request_id, body = await self.vivox_connection.read_message()
        self.assertEqual("Response", msg_type)
        self.assertEqual("Connector.SetLocalMicVolume.1", msg_action)
        self.assertEqual("foobar", request_id)
        self.assertDictEqual(
            {'ReturnCode': 0, 'Results': {'StatusCode': '0', 'StatusString': None}},
            body,
        )

    async def test_read_event(self):
        self.reader.feed_data(
            b'<Event type="MediaStreamUpdatedEvent"><SessionGroupHandle>4</SessionGroupHandle><SessionHandle>7'
            b'</SessionHandle><StatusCode>0</StatusCode><StatusString/>'
            b'<State>6</State><StateDescription>Connecting</StateDescription><Incoming>false</Incoming>'
            b'<DurableMediaId/></Event>\n\n\n'
        )
        self.reader.feed_eof()
        msg_type, msg_action, request_id, body = await self.vivox_connection.read_message()
        self.assertEqual("Event", msg_type)
        self.assertEqual("MediaStreamUpdatedEvent", msg_action)
        self.assertEqual(None, request_id)
        self.assertDictEqual(
            {
                'DurableMediaId': None,
                'Incoming': 'false',
                'SessionGroupHandle': '4',
                'SessionHandle': '7',
                'State': '6',
                'StateDescription': 'Connecting',
                'StatusCode': '0',
                'StatusString': None,
            },
            body,
        )

    async def test_read_messages(self):
        self.reader.feed_data(
            b'<Request requestId="foobar" action="Aux.GetRenderDevices.1"><Foo>1</Foo></Request>\n\n\n'
            b'<Request requestId="quux" action="Aux.GetRenderDevices.1"><Foo>1</Foo></Request>\n\n\n'
        )
        self.reader.feed_eof()

        i = 0
        async for msg in self.vivox_connection.read_messages():
            if i == 0:
                self.assertEqual("foobar", msg.request_id)
            else:
                self.assertEqual("quux", msg.request_id)

            self.assertEqual("Request", msg.type)
            self.assertEqual("Aux.GetRenderDevices.1", msg.action)
            self.assertDictEqual({"Foo": "1"}, msg.data)
            i += 1

    async def test_send_message(self):
        await self.vivox_connection.send_request("foo", "bar", {"baz": 1})
        self.assertEqual(
            b'<Request requestId="foo" action="bar"><baz>1</baz></Request>\n\n\n',
            self._writer_buf
        )


class TestVoiceClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._client_transport = _make_transport(
            lambda *args: asyncio.get_event_loop().call_soon(self.server_reader.feed_data, *args)
        )
        self._client_protocol = _make_protocol(self._client_transport)
        self.client_reader = asyncio.StreamReader()
        self.client_writer = asyncio.StreamWriter(
            self._client_transport,
            self._client_protocol,
            self.client_reader,
            asyncio.get_event_loop()
        )

        self._server_transport = _make_transport(
            lambda *args: asyncio.get_event_loop().call_soon(self.client_reader.feed_data, *args)
        )
        self._server_protocol = _make_protocol(self._server_transport)
        self.server_reader = asyncio.StreamReader()
        self.server_writer = asyncio.StreamWriter(
            self._server_transport,
            self._server_protocol,
            self.server_reader,
            asyncio.get_event_loop()
        )

        self.client_connection = VivoxConnection(self.client_reader, self.client_writer)
        self.server_connection = VivoxConnection(self.server_reader, self.server_writer)
        self.client = VoiceClient("127.0.0.1", 0)
        self.client.vivox_conn = self.client_connection

        def _make_request_id():
            _make_request_id.i += 1
            return str(_make_request_id.i)

        _make_request_id.i = 0

        self.client._make_request_id = _make_request_id

    async def test_connection(self):
        async def _serve_login():
            await self.server_connection.send_event(
                "VoiceServiceConnectionStateChangedEvent",
                {
                    "Connected": 1,
                    "Platform": "Linux",
                    "Version": 1,
                    "DataDirectory": "/tmp/whatever",
                }
            )
            self.assertEqual(
                ('Request', 'Aux.GetCaptureDevices.1', '1', {}),
                await self.server_connection.read_message()
            )

        serve_coro = asyncio.get_event_loop().create_task(_serve_login())
        # Await this here so we can see any exceptions
        await serve_coro
