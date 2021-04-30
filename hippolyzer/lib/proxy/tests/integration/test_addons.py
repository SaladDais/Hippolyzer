from __future__ import annotations

from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.proxy import addon_ctx
from hippolyzer.lib.proxy.addon_utils import BaseAddon, SessionProperty
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.packets import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session
from hippolyzer.lib.proxy.tests.integration import BaseIntegrationTest


class MockAddon(BaseAddon):
    bazquux: str = SessionProperty()
    another: str = SessionProperty("default")

    @handle_command(bar=str)
    async def foobar(self, _session: Session, _region: ProxiedRegion, bar: str):
        self.bazquux = bar
        self.another = bar


class AddonIntegrationTests(BaseIntegrationTest):
    def setUp(self) -> None:
        super().setUp()
        self.addon = MockAddon()
        AddonManager.init([], self.session_manager, [self.addon])

    def _fake_command(self, command: str) -> None:
        msg = ProxiedMessage(
            "ChatFromViewer",
            Block("AgentData", AgentID=self.session.agent_id, SessionID=self.session.id),
            Block("ChatData", Message=command, Channel=AddonManager.COMMAND_CHANNEL, fill_missing=True),
        )
        packet = self._msg_to_datagram(msg, src=self.client_addr,
                                       dst=self.region_addr, direction=Direction.OUT)
        self.protocol.datagram_received(packet, self.client_addr)

    async def test_simple_command_setting_params(self):
        self._setup_circuit()
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
