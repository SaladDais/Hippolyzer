from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

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
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session
from hippolyzer.lib.proxy.test_utils import BaseProxyTest


class MockAddon(BaseAddon):
    bazquux: str = SessionProperty()
    another: str = SessionProperty("default")

    @handle_command(bar=str)
    async def foobar(self, _session: Session, _region: ProxiedRegion, bar: str):
        self.bazquux = bar
        self.another = bar
        send_chat(bar)
        show_message(bar)


PARENT_ADDON_SOURCE = """
from hippolyzer.lib.proxy.addon_utils import BaseAddon, GlobalProperty

class ParentAddon(BaseAddon):
    baz = None
    quux: int = GlobalProperty(0)

    @classmethod
    def foo(cls):
        cls.baz = 1

addons = [ParentAddon()]
"""

CHILD_ADDON_SOURCE = """
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.addons import AddonManager

import parent_addon

AddonManager.hot_reload(parent_addon)

class ChildAddon(BaseAddon):
    def handle_init(self, session_manager):
        parent_addon.ParentAddon.foo()

addons = [ChildAddon()]
"""


class AddonIntegrationTests(BaseProxyTest):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.addon = MockAddon()
        AddonManager.init([], self.session_manager, [self.addon], swallow_addon_exceptions=False)
        self.temp_dir = TemporaryDirectory(prefix="addon_test_sources")
        self.child_path = Path(self.temp_dir.name) / "child_addon.py"
        self.parent_path = Path(self.temp_dir.name) / "parent_addon.py"

    def tearDown(self) -> None:
        AddonManager.shutdown()
        self.temp_dir.cleanup()

    def _fake_command(self, command: str) -> None:
        msg = Message(
            "ChatFromViewer",
            Block("AgentData", AgentID=self.session.agent_id, SessionID=self.session.id),
            Block("ChatData", Message=command, Channel=AddonManager.COMMAND_CHANNEL, fill_missing=True),
        )
        packet = self._msg_to_packet(msg, src=self.client_addr, dst=self.region_addr)
        self.protocol.handle_proxied_packet(packet)

    async def test_simple_command_setting_params(self):
        self._setup_default_circuit()
        self._fake_command("foobar baz")
        await self._wait_drained()
        self.assertEqual(self.session.addon_ctx["MockAddon"]["bazquux"], "baz")

        # In session context these should be equivalent
        with addon_ctx.push(new_session=self.session):
            self.assertEqual(self.session.addon_ctx["MockAddon"]["bazquux"], self.addon.bazquux)
            self.assertEqual(self.session.addon_ctx["MockAddon"]["another"], "baz")

        # Outside session context it should raise
        with self.assertRaises(AttributeError):
            self.assertEqual(self.addon.bazquux, "baz")
        # Even if there's a default value
        with self.assertRaises(AttributeError):
            self.assertEqual(self.addon.another, "baz")

        self.session.addon_ctx.clear()
        with addon_ctx.push(new_session=self.session):
            # This has no default so it should fail
            with self.assertRaises(AttributeError):
                _something = self.addon.bazquux
            # This has a default
            self.assertEqual(self.addon.another, "default")
        # Should have sent out the two injected packets for inbound and outbound chat
        # But not the original chatfromviewer from our command.
        self.assertEqual(len(self.transport.packets), 2)

    async def test_loading_addons(self):
        with open(self.parent_path, "w") as f:
            f.write(PARENT_ADDON_SOURCE)
        with open(self.child_path, "w") as f:
            f.write(CHILD_ADDON_SOURCE)
        AddonManager.load_addon_from_path(str(self.parent_path), reload=True)
        AddonManager.load_addon_from_path(str(self.child_path), reload=True)
        # Wait for the init hooks to run
        await asyncio.sleep(0.001)
        # Should be able to import this by name now
        import parent_addon  # noqa
        # ChildAddon calls a classmethod that mutates this
        self.assertEqual(1, parent_addon.ParentAddon.baz)

    async def test_unloading_addons(self):
        with open(self.parent_path, "w") as f:
            f.write(PARENT_ADDON_SOURCE)
        AddonManager.load_addon_from_path(str(self.parent_path), reload=True)
        # Wait for the init hooks to run
        await asyncio.sleep(0.001)
        # Should be able to import this by name now
        AddonManager.unload_addon_from_path(str(self.parent_path), reload=True)
        await asyncio.sleep(0.001)
        self.assertNotIn('hippolyzer.user_addon_parent_addon', sys.modules)

    async def test_global_property_access_and_set(self):
        with open(self.parent_path, "w") as f:
            f.write(PARENT_ADDON_SOURCE)
        AddonManager.load_addon_from_path(str(self.parent_path), reload=True)
        # Wait for the init hooks to run
        await asyncio.sleep(0.001)
        self.assertFalse("quux" in self.session_manager.addon_ctx["ParentAddon"])
        parent_addon_mod = AddonManager.FRESH_ADDON_MODULES['hippolyzer.user_addon_parent_addon']
        self.assertEqual(0, parent_addon_mod.ParentAddon.quux)
        self.assertEqual(0, self.session_manager.addon_ctx["ParentAddon"]["quux"])
        parent_addon_mod.ParentAddon.quux = 1
        self.assertEqual(1, self.session_manager.addon_ctx["ParentAddon"]["quux"])
