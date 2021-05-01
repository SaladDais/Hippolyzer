"""
Copyright 2009, Linden Research, Inc.
  See NOTICE.md for previous contributors
Copyright 2021, Salad Dais
All Rights Reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
import asyncio
import copy
import pickle
import unittest
import weakref
from uuid import UUID

from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer
from hippolyzer.lib.base.settings import Settings


class TestMessage(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        self.chat_msg = Message('ChatFromViewer',
                                Block('AgentData', AgentID=UUID('550e8400-e29b-41d4-a716-446655440000'),
                                      SessionID=UUID('550e8400-e29b-41d4-a716-446655440000')),
                                Block('ChatData', Message="Chatting\n", Type=1, Channel=0))
        self.serial = UDPMessageSerializer()
        settings = Settings()
        settings.ENABLE_DEFERRED_PACKET_PARSING = True
        settings.HANDLE_PACKETS = False
        self.deserial = UDPMessageDeserializer(settings=settings)

    def test_block(self):
        _block = Block('CircuitCode', ID=1234, Code=531)

    def test_build(self):
        msg = Message(
            'TestPacket',
            Block('CircuitCode', ID=1234, Code=531),
        )

        assert msg.blocks['CircuitCode'][0].vars['ID'] == 1234, \
            "Incorrect data in block ID"
        assert msg.blocks['CircuitCode'][0].vars['Code'] == 531, \
            "Incorrect data in block Code"

    def test_build_multiple(self):
        msg = Message('TestPacket',
                      Block('CircuitCode', ID=1234, Code=789),
                      Block('CircuitCode', ID=5678, Code=456),
                      Block('Test', ID=9101, Code=123)
                      )

        assert msg.blocks['CircuitCode'][0].vars['ID'] == 1234, \
            "Incorrect data in block ID"
        assert msg.blocks['CircuitCode'][1].vars['ID'] == 5678, \
            "Incorrect data in block 2 ID"

        assert msg.blocks['CircuitCode'][0].vars['Code'] == 789, \
            "Incorrect data in block Code"
        assert msg.blocks['CircuitCode'][1].vars['Code'] == 456, \
            "Incorrect data in block 2 Code"

        assert msg.blocks['Test'][0].vars['ID'] == 9101, \
            "Incorrect data in block Test ID"
        assert msg.blocks['Test'][0].vars['Code'] == 123, \
            "Incorrect data in block Test ID"

    def test_getitem_helpers(self):
        msg = Message('TestPacket',
                      Block('CircuitCode', ID=1234, Code=789),
                      Block('CircuitCode', ID=5678, Code=456),
                      Block('Test', ID=9101, Code=123)
                      )

        assert msg.blocks['CircuitCode'][0].vars['ID'] == msg['CircuitCode'][0]['ID'], \
            "Explicit blocks/vars/data doesn't match __getitem__ shortcut"
        assert msg.blocks['CircuitCode'][1].vars['ID'] == msg['CircuitCode'][1]['ID'], \
            "Explicit blocks/vars/data doesn't match __getitem__ shortcut"

        assert msg.blocks['CircuitCode'][0].vars['Code'] == msg['CircuitCode'][0]['Code'], \
            "Explicit blocks/vars/data doesn't match __getitem__ shortcut"
        assert msg.blocks['CircuitCode'][1].vars['Code'] == msg['CircuitCode'][1]['Code'], \
            "Explicit blocks/vars/data doesn't match __getitem__ shortcut"

        assert msg.blocks['Test'][0].vars['ID'] == msg['Test'][0]['ID'], \
            "Explicit blocks/vars/data doesn't match __getitem__ shortcut"
        assert msg.blocks['Test'][0].vars['Code'] == msg['Test'][0]['Code'], \
            "Explicit blocks/vars/data doesn't match __getitem__ shortcut"
        assert msg.blocks['Test'][0].vars['Code'] == msg['Test']['Code'], \
            "Explicit blocks/vars/data doesn't match __getitem__ shortcut"

    def test_build_chat(self):
        msg = self.chat_msg
        assert msg.blocks['ChatData'][0].vars['Type'] == 1, "Bad type sent"
        assert msg.blocks['ChatData'][0].vars['Channel'] == 0, "Bad Channel sent"

        serial = UDPMessageSerializer()
        _msg = serial.serialize(msg)

    def test_build_chat_bad_block(self):
        msg = self.chat_msg
        msg["Foo"] = Block("Foo", Bar="Baz")
        serial = UDPMessageSerializer()
        with self.assertRaises(KeyError):
            serial.serialize(msg)

    def test_partial_decode_pickle(self):
        msg = self.deserial.deserialize(self.serial.serialize(self.chat_msg))
        self.assertEqual(msg.deserializer(), self.deserial)
        # Have to remove the weak ref so we can pickle
        msg.deserializer = None
        msg = pickle.loads(pickle.dumps(msg, protocol=pickle.HIGHEST_PROTOCOL))

        # We should still have the raw body at this point
        self.assertIsNotNone(msg.raw_body)

        # Need to put the serializer back so we can parse
        msg.deserializer = weakref.ref(self.deserial)

        # Should trigger a parse of the body
        self.assertEqual(msg["ChatData"]["Message"], "Chatting\n")

        self.assertIsNone(msg.raw_body)
        self.assertIsNone(msg.deserializer)

    def test_todict(self):
        new_msg = Message.from_dict(self.chat_msg.to_dict())
        self.assertEqual(pickle.dumps(self.chat_msg), pickle.dumps(new_msg))

    def test_todict_multiple_blocks(self):
        chat_msg = self.chat_msg
        # If we dupe the ChatData block it should survive to_dict()
        chat_msg['ChatData'].append(copy.deepcopy(chat_msg['ChatData'][0]))
        new_msg = Message.from_dict(self.chat_msg.to_dict())
        self.assertEqual(pickle.dumps(self.chat_msg), pickle.dumps(new_msg))

    def test_extra_field(self):
        chat_msg = self.chat_msg
        chat_msg.extra = b"foobar"
        parsed_msg = self.deserial.deserialize(self.serial.serialize(chat_msg))
        self.assertEqual(parsed_msg.extra, b"foobar")
        self.assertEqual(chat_msg.to_dict(), parsed_msg.to_dict())

    def test_repr(self):
        expected_repr = r"""Message('ChatFromViewer',
  Block('AgentData', AgentID=UUID('550e8400-e29b-41d4-a716-446655440000'), SessionID=UUID('550e8400-e29b-41d4-a716-446655440000')),
  Block('ChatData', Message='Chatting\n', Type=1, Channel=0))"""
        self.assertEqual(expected_repr, repr(self.chat_msg))


class TestMessageHandlers(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.message_handler: MessageHandler[Message] = MessageHandler()

    def _fake_received_message(self, msg: Message):
        self.message_handler.handle(msg)

    async def test_subscription(self):
        with self.message_handler.subscribe_async(
                message_names=("Foo",),
                predicate=lambda m: m["Bar"]["Baz"] == 1,
        ) as get_msg:
            foo_handlers = self.message_handler.handlers['Foo']
            msg1 = Message("Foo", Block("Bar", Baz=1, Biz=1))
            # will fail predicate
            msg2 = Message("Foo", Block("Bar", Baz=2, Biz=2))
            msg3 = Message("Foo", Block("Bar", Baz=1, Biz=3))
            self._fake_received_message(msg1)
            self._fake_received_message(msg2)
            self._fake_received_message(msg3)
            received = []
            while True:
                try:
                    received.append(await asyncio.wait_for(get_msg(), 0.001))
                except asyncio.exceptions.TimeoutError:
                    break
            self.assertEqual(len(foo_handlers), 1)
        self.assertListEqual(received, [msg1, msg3])
        # The message should have been take()n, making a copy
        self.assertIsNot(msg1, received[0])
        # take() was called, so this should have been marked queued
        self.assertTrue(msg1.queued)
        # Leaving the block should have unsubscribed automatically
        self.assertEqual(len(foo_handlers), 0)

    async def test_subscription_no_take(self):
        with self.message_handler.subscribe_async("Foo", take=False) as get_msg:
            msg = Message("Foo", Block("Bar", Baz=1, Biz=1))
            self._fake_received_message(msg)
            # Should not copy
            self.assertIs(msg, await asyncio.wait_for(get_msg(), 0.001))
            # Should not have been queued
            self.assertFalse(msg.queued)

    async def test_wait_for(self):
        fut = self.message_handler.wait_for("Foo", timeout=0.001, take=False)
        foo_handlers = self.message_handler.handlers['Foo']
        # We are subscribed
        self.assertEqual(len(foo_handlers), 1)
        msg = Message("Foo", Block("Bar", Baz=1, Biz=1))
        self._fake_received_message(msg)
        # Should not copy
        self.assertIs(msg, await fut)
        # Should not have been queued
        self.assertFalse(msg.queued)
        # Receiving the message unsubscribes
        self.assertEqual(len(foo_handlers), 0)
