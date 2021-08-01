"""
Base classes for common session-related state shared between clients and proxies
"""
from __future__ import annotations

import abc
from typing import *

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.circuit import ConnectionHolder
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.network.caps_client import CapsClient
from hippolyzer.lib.base.network.transport import ADDR_TUPLE

if TYPE_CHECKING:
    from hippolyzer.lib.client.object_manager import ClientObjectManager, ClientWorldObjectManager


class BaseClientRegion(ConnectionHolder, abc.ABC):
    """Represents a client's view of a remote region"""
    handle: Optional[int]
    # Actually a weakref
    session: Callable[[], BaseClientSession]
    objects: ClientObjectManager
    caps_client: CapsClient


class BaseClientSession(abc.ABC):
    """Represents a client's view of a remote session"""
    id: UUID
    agent_id: UUID
    secure_session_id: UUID
    message_handler: MessageHandler[Message, str]
    regions: Sequence[BaseClientRegion]
    region_by_handle: Callable[[int], Optional[BaseClientRegion]]
    region_by_circuit_addr: Callable[[ADDR_TUPLE], Optional[BaseClientRegion]]
    objects: ClientWorldObjectManager
