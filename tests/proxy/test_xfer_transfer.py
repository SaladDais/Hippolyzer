import asyncio
from typing import *

from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.templates import AssetType
from hippolyzer.lib.proxy.circuit import ProxiedCircuit
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.packets import Direction
from hippolyzer.lib.proxy.xfer_manager import XferManager

from . import BaseProxyTest


class MockHandlingCircuit(ProxiedCircuit):
    def __init__(self, transport, handler):
        super().__init__(("127.0.0.1", 1), ("127.0.0.1", 2), transport)
        self.handler = handler

    def _send_prepared_message(self, message: ProxiedMessage, direction, transport=None):
        asyncio.get_event_loop().call_soon(self.handler.handle, message)
        return super()._send_prepared_message(message, direction, transport)


class XferManagerTests(BaseProxyTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_default_circuit()
        self.message_handler: MessageHandler[ProxiedMessage] = MessageHandler()
        self.circuit = MockHandlingCircuit(self.transport, self.message_handler)
        self.session.main_region.circuit = self.circuit
        self.xfer_manager = XferManager(self.session.main_region)
        self.received_bytes: Optional[bytes] = None

    async def _handle_upload(self):
        msg = await self.message_handler.wait_for('AssetUploadRequest', timeout=0.01)
        asset_block = msg["AssetBlock"]
        transaction_id = asset_block["TransactionID"]
        asset_id = self.session.tid_to_assetid(transaction_id)
        if asset_block["AssetData"]:
            self.received_bytes = asset_block["AssetData"]
            self.session.main_region.message_handler.handle(ProxiedMessage(
                "AssetUploadComplete",
                Block("AssetBlock", UUID=asset_id, Type=asset_block["Type"], Success=True),
                direction=Direction.IN,
            ))
        else:
            pass

    async def test_short_xfer_upload(self):
        asyncio.create_task(self._handle_upload())
        xfer = asyncio.wait_for(self.xfer_manager.upload_asset(
            AssetType.BODYPART, b"foobar"
        ), timeout=0.05)
        await xfer
        self.assertEqual(self.received_bytes, b"foobar")
