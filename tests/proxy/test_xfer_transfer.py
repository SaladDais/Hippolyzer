import asyncio
import unittest
from typing import *

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.templates import AssetType
from hippolyzer.lib.proxy.circuit import ProxiedCircuit
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.packets import Direction
from hippolyzer.lib.proxy.xfer_manager import XferManager


class MockHandlingCircuit(ProxiedCircuit):
    def __init__(self, handler: MessageHandler[ProxiedMessage]):
        super().__init__(("127.0.0.1", 1), ("127.0.0.1", 2), None)
        self.handler = handler

    def _send_prepared_message(self, message: ProxiedMessage, direction, transport=None):
        asyncio.get_event_loop().call_soon(self.handler.handle, message)


class XferManagerTests(unittest.IsolatedAsyncioTestCase):
    SMALL_PAYLOAD = b"foobar"
    LARGE_PAYLOAD = b"foobar" * 500

    def setUp(self) -> None:
        super().setUp()
        self.server_message_handler: MessageHandler[ProxiedMessage] = MessageHandler()
        self.client_message_handler: MessageHandler[ProxiedMessage] = MessageHandler()
        # The client side should send messages to the server side's message handler
        # and vice-versa
        self.client_circuit = MockHandlingCircuit(self.server_message_handler)
        self.server_circuit = MockHandlingCircuit(self.client_message_handler)

        self.secure_session_id = UUID.random()
        self.xfer_manager = XferManager(self.client_message_handler, self.client_circuit, self.secure_session_id)
        self.received_bytes: Optional[bytes] = None

    async def _handle_upload(self):
        msg = await self.server_message_handler.wait_for('AssetUploadRequest', timeout=0.01)
        asset_block = msg["AssetBlock"]
        transaction_id = asset_block["TransactionID"]
        asset_id = UUID.combine(transaction_id, self.secure_session_id)
        if asset_block["AssetData"]:
            self.received_bytes = asset_block["AssetData"]
        else:
            manager = XferManager(self.server_message_handler, self.server_circuit)
            xfer = await manager.request(vfile_id=asset_id, vfile_type=AssetType.BODYPART)
            self.received_bytes = xfer.reassemble_chunks()
        self.server_circuit.send_message(ProxiedMessage(
            "AssetUploadComplete",
            Block("AssetBlock", UUID=asset_id, Type=asset_block["Type"], Success=True),
            direction=Direction.IN,
        ))

    async def test_small_xfer_upload(self):
        asyncio.create_task(self._handle_upload())
        await asyncio.wait_for(self.xfer_manager.upload_asset(
            AssetType.BODYPART, self.SMALL_PAYLOAD
        ), timeout=0.05)
        self.assertEqual(self.received_bytes, self.SMALL_PAYLOAD)

    async def test_large_xfer_upload(self):
        # Larger payloads take a different path
        asyncio.create_task(self._handle_upload())
        await asyncio.wait_for(self.xfer_manager.upload_asset(
            AssetType.BODYPART, self.LARGE_PAYLOAD
        ), timeout=0.05)
        self.assertEqual(self.received_bytes, self.LARGE_PAYLOAD)
