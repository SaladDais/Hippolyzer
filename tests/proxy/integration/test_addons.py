from __future__ import annotations

from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.proxy import addon_ctx
from hippolyzer.lib.proxy.addon_utils import (
    BaseAddon,
    SessionProperty,
    send_chat,
    show_message,
)
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session

from .. import BaseProxyTest


class MockAddon(BaseAddon):
    bazquux: str = SessionProperty()
    another: str = SessionProperty("default")

    @handle_command(bar=str)
    async def foobar(self, _session: Session, _region: ProxiedRegion, bar: str):
        self.bazquux = bar
        self.another = bar
        send_chat(bar)
        show_message(bar)


class AddonIntegrationTests(BaseProxyTest):
    def setUp(self) -> None:
        super().setUp()
        self.addon = MockAddon()
        AddonManager.init([], self.session_manager, [self.addon], swallow_addon_exceptions=False)

    def tearDown(self) -> None:
        AddonManager.shutdown()

    def _fake_command(self, command: str) -> None:
        msg = Message(
            "ChatFromViewer",
            Block("AgentData", AgentID=self.session.agent_id, SessionID=self.session.id),
            Block("ChatData", Message=command, Channel=AddonManager.COMMAND_CHANNEL, fill_missing=True),
        )
        packet = self._msg_to_datagram(msg, src=self.client_addr,
                                       dst=self.region_addr, direction=Direction.OUT)
        self.protocol.datagram_received(packet, self.client_addr)

    async def test_simple_command_setting_params(self):
        self._setup_default_circuit()
        self._fake_command("foobar baz")
        await self._wait_drained()
        self.assertEqual(self.session.addon_ctx["bazquux"], "baz")

        # In session context these should be equivalent
        with addon_ctx.push(new_session=self.session):
            self.assertEqual(self.session.addon_ctx["bazquux"], self.addon.bazquux)
            self.assertEqual(self.session.addon_ctx["another"], "baz")

        # Outside session context it should raise
        with self.assertRaises(AttributeError):
            self.assertEqual(self.addon.bazquux, "baz")
        # Even if there's a default value
        with self.assertRaises(AttributeError):
            self.assertEqual(self.addon.another, "baz")

        self.session.addon_ctx.clear()
        with addon_ctx.push(new_session=self.session):
            # This has no default so should fail
            with self.assertRaises(AttributeError):
                _something = self.addon.bazquux
            # This has a default
            self.assertEqual(self.addon.another, "default")
        # Should have sent out the two injected packets for inbound and outbound chat
        # But not the original chatfromviewer from our command.
        self.assertEqual(len(self.transport.packets), 2)
