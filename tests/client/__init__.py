from typing import Mapping, Optional

import multidict

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.network.caps_client import CapsClient
from hippolyzer.lib.base.test_utils import MockHandlingCircuit
from hippolyzer.lib.client.hippo_client import ClientSettings
from hippolyzer.lib.client.object_manager import ClientWorldObjectManager
from hippolyzer.lib.client.state import BaseClientRegion, BaseClientSession, BaseClientSessionManager


class MockClientRegion(BaseClientRegion):
    def __init__(self, caps_urls: Optional[dict] = None):
        super().__init__()
        self.handle = None
        self.circuit_addr = ("127.0.0.1", 1)
        self.message_handler: MessageHandler[Message, str] = MessageHandler(take_by_default=False)
        self.circuit = MockHandlingCircuit(self.message_handler)
        self._name = "Test"
        self.cap_urls = multidict.MultiDict()
        if caps_urls:
            self.cap_urls.update(caps_urls)
        self.caps_client = CapsClient(self.cap_urls)

    def session(self):
        return MockClientSession(UUID.ZERO, UUID.ZERO, UUID.ZERO, 0, None)

    def update_caps(self, caps: Mapping[str, str]) -> None:
        pass


class MockClientSession(BaseClientSession):
    def __init__(self, id, secure_session_id, agent_id, circuit_code,
                 session_manager: Optional[BaseClientSessionManager]):
        super().__init__(id, secure_session_id, agent_id, circuit_code, session_manager)
        self.objects = ClientWorldObjectManager(self, ClientSettings(), None)
