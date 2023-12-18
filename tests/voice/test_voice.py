from typing import *

import asyncio
import unittest
from unittest import mock

from hippolyzer.lib.voice.connection import VivoxConnection


def _make_transport(buf: Any):
    transport = mock.Mock()
    transport.write.side_effect = buf.extend
    transport.is_closing.return_value = False
    return transport


def _make_protocol(transport: Any):
    protocol = mock.Mock(transport=transport)
    protocol._drain_helper = mock.AsyncMock()
    return protocol


class TestVivoxConnection(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._writer_buf = bytearray()
        self._transport = _make_transport(self._writer_buf)
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
        async for msg_type, msg_action, request_id, body in self.vivox_connection.read_messages():
            if i == 0:
                self.assertEqual("foobar", request_id)
            else:
                self.assertEqual("quux", request_id)
            self.assertEqual("Request", msg_type)

            self.assertEqual("Aux.GetRenderDevices.1", msg_action)
            self.assertDictEqual({"Foo": "1"}, body)
            i += 1

    async def test_send_message(self):
        await self.vivox_connection.send_request("foo", "bar", {"baz": 1})
        self.assertEqual(
            b'<Request requestId="foo" action="bar"><baz>1</baz></Request>\n\n\n',
            self._writer_buf
        )
