from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class REPLExampleAddon(BaseAddon):
    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if message.name == "ChatFromViewer":
            chat_msg = message["ChatData"]["Message"]
            if not chat_msg:
                return
            # Intercept chat messages containing "hippolyzer_test" as an example
            if "hippolyzer_test" in chat_msg:
                if AddonManager.have_active_repl():
                    # Already intercepting, don't touch it
                    return
                # Take ownership of the message so it won't be sent by the
                # usual machinery.
                _new_msg = message.take()
                # repl will have access to `_new_msg` and can send it with
                # `region.circuit.send_message()` after it's modified.
                AddonManager.spawn_repl()
                return True
            if "hippolyzer_async_test" in chat_msg:
                if AddonManager.have_active_repl():
                    # Already intercepting, don't touch it
                    return

                async def _coro():
                    foo = 4
                    # spawn_repl() can be `await`ed, changing foo
                    # in the repl will change what's printed on exit.
                    await AddonManager.spawn_repl()
                    print("foo is", foo)

                self._schedule_task(_coro())


addons = [REPLExampleAddon()]
