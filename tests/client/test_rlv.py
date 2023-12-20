import unittest

from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.templates import ChatType
from hippolyzer.lib.client.rlv import RLVParser, RLVCommand


class TestRLV(unittest.TestCase):
    def test_is_rlv_command(self):
        msg = Message(
            "ChatFromSimulator",
            Block("ChatData", Message="@foobar", ChatType=ChatType.OWNER)
        )
        self.assertTrue(RLVParser.is_rlv_message(msg))
        msg["ChatData"]["ChatType"] = ChatType.NORMAL
        self.assertFalse(RLVParser.is_rlv_message(msg))

    def test_rlv_parse_single_command(self):
        cmd = RLVParser.parse_chat("@foo:bar;baz=quux")[0]
        self.assertEqual("foo", cmd.behaviour)
        self.assertListEqual(["bar", "baz"], cmd.options)
        self.assertEqual("quux", cmd.param)

    def test_rlv_parse_multiple_commands(self):
        cmds = RLVParser.parse_chat("@foo:bar;baz=quux,bazzy")
        self.assertEqual("foo", cmds[0].behaviour)
        self.assertListEqual(["bar", "baz"], cmds[0].options)
        self.assertEqual("quux", cmds[0].param)
        self.assertEqual("bazzy", cmds[1].behaviour)

    def test_rlv_format_commands(self):
        chat = RLVParser.format_chat([
            RLVCommand("foo", "quux", ["bar", "baz"]),
            RLVCommand("bazzy", "", [])
        ])
        self.assertEqual("@foo:bar;baz=quux,bazzy", chat)
