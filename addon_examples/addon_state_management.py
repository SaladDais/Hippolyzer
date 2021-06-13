"""
Demonstrates how addon state can be tied to sessions and survive
across reloads using the GlobalProperty and SessionProperty ClassVars
"""

from hippolyzer.lib.proxy.commands import handle_command, Parameter
from hippolyzer.lib.proxy.addon_utils import BaseAddon, SessionProperty, GlobalProperty, send_chat
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class AddonStateHelloWorldAddon(BaseAddon):
    # How to say hello, value shared across sessions and will be the same
    # regardless of which session is active when accessed.
    # "hello_greeting" is added to session_manager.addon_ctx's dict and will survive reloads
    # be mindful of conflicting with other addons' variables, other addons' variables
    # can be accessed manually through the session_manager.addon_ctx dict since
    # there isn't currently any namespacing.
    hello_greeting: str = GlobalProperty(default="Hello")
    # Who to say hello to, value specific to each session
    # Value will be different depending on which session is having its event
    # handled when the property is accessed.
    # "hello_person" is added to session.addon_ctx's dict and will survive reloads
    hello_person: str = SessionProperty(default="World")

    def __init__(self):
        # Tied to the addon instance.
        # Shared across sessions and will die if the addon is reloaded
        self.hello_punctuation = "!"

    @handle_command(
        # Use the longer-form `Parameter()` for declaring this because
        # this field should be greedy and take the rest of the message (no separator.)
        greeting=Parameter(str, sep=None),
    )
    async def set_hello_greeting(self, _session: Session, _region: ProxiedRegion, greeting: str):
        """Set the person to say hello to"""
        self.hello_greeting = greeting

    @handle_command(person=Parameter(str, sep=None))
    async def set_hello_person(self, _session: Session, _region: ProxiedRegion, person: str):
        """Set the person to say hello to"""
        self.hello_person = person

    @handle_command(
        # Punctuation should have no whitespace, so using a simple parameter is OK.
        punctuation=str,
    )
    async def set_hello_punctuation(self, _session: Session, _region: ProxiedRegion, punctuation: str):
        """Set the punctuation to use for saying hello"""
        self.hello_punctuation = punctuation

    @handle_command()
    async def say_hello(self, _session: Session, _region: ProxiedRegion):
        """Say hello using the configured hello variables"""
        # These aren't instance properties, they can be accessed via the class as well.
        hello_person = AddonStateHelloWorldAddon.hello_person
        send_chat(f"{self.hello_greeting} {hello_person}{self.hello_punctuation}")


addons = [AddonStateHelloWorldAddon()]
