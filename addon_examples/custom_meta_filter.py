"""
Example of custom meta tags, useful for complex expressions that wouldn't work
well in the message log filter language.

Tags messages where someone said "hello", and record who they said hello to.

If you said "hello Someone", that message would be shown in the log pane when
filtering with `Meta.Greeted == "Someone"` or just `Meta.Greeted` to match any
message with a greeting.
"""

from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class CustomMetaExampleAddon(BaseAddon):
    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if not message.name.startswith("ChatFrom"):
            return

        chat = message["ChatData"]["Message"]
        if not chat:
            return

        if chat.lower().startswith("hello "):
            message.meta["Greeted"] = chat.split(" ", 1)[1]


addons = [CustomMetaExampleAddon()]
