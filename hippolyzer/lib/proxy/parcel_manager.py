from typing import *

from hippolyzer.lib.base.helpers import proxify
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.client.parcel_manager import ParcelManager
if TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion


class ProxyParcelManager(ParcelManager):
    def __init__(self, region: "ProxiedRegion"):
        super().__init__(proxify(region))
        # Handle ParcelProperties messages that we didn't specifically ask for
        self._region.message_handler.subscribe("ParcelProperties", self._handle_parcel_properties)

    def _handle_parcel_properties(self, msg: Message):
        self._process_parcel_properties(msg)
        return None
