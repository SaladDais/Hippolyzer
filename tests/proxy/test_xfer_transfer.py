import asyncio
from typing import *

from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.templates import AssetType, XferFilePath, XferPacket
from hippolyzer.lib.proxy.circuit import ProxiedCircuit
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.packets import Direction

from . import BaseProxyTest


class MockHandlingCircuit(ProxiedCircuit):
    def __init__(self, transport, handler):
        super().__init__(("127.0.0.1", 1), ("127.0.0.1", 2), transport)
        self.handler = handler

    def _send_prepared_message(self, message: ProxiedMessage, direction, transport=None):
        asyncio.get_event_loop().call_soon(self.handler.handle, message)
        return super()._send_prepared_message(message, direction, transport)


class XferManagerTests(BaseProxyTest):
    SMALL_PAYLOAD = b"foobar"
    LARGE_PAYLOAD = b"foobar" * 500

    def setUp(self) -> None:
        super().setUp()
        self._setup_default_circuit()
        self.message_handler: MessageHandler[ProxiedMessage] = MessageHandler()
        self.circuit = MockHandlingCircuit(self.transport, self.message_handler)
        self.session.main_region.circuit = self.circuit
        self.xfer_manager = self.session.main_region.xfer_manager
        self.received_bytes: Optional[bytes] = None

    async def _handle_upload(self):
        msg = await self.message_handler.wait_for('AssetUploadRequest', timeout=0.01)
        asset_block = msg["AssetBlock"]
        transaction_id = asset_block["TransactionID"]
        asset_id = self.session.tid_to_assetid(transaction_id)
        client_handler = self.session.main_region.message_handler
        if asset_block["AssetData"]:
            self.received_bytes = asset_block["AssetData"]
        else:
            with self.message_handler.subscribe_async(("SendXferPacket",)) as get_msgs:
                client_handler.handle(ProxiedMessage(
                    'RequestXfer',
                    Block(
                        'XferID',
                        ID=2,
                        Filename=b'',
                        FilePath=XferFilePath.NONE,
                        DeleteOnCompletion=False,
                        UseBigPackets=False,
                        VFileID=asset_id,
                        VFileType=AssetType.BODYPART,
                    ),
                    direction=Direction.IN,
                ))
                self.received_bytes = b""
                while True:
                    msg = await asyncio.wait_for(get_msgs(), 0.005)
                    packet_id: XferPacket = msg["XferID"][0].deserialize_var("Packet")
                    data = msg["DataPacket"]["Data"]
                    # First 4 bytes are expected len
                    if packet_id.PacketID == 0:
                        data = data[4:]
                    self.received_bytes += data
                    client_handler.handle(ProxiedMessage(
                        "ConfirmXferPacket",
                        Block("XferID", ID=2, Packet=packet_id.PacketID),
                        direction=Direction.IN,
                    ))
                    if packet_id.IsEOF:
                        break
        await asyncio.sleep(0.005)
        client_handler.handle(ProxiedMessage(
            "AssetUploadComplete",
            Block("AssetBlock", UUID=asset_id, Type=asset_block["Type"], Success=True),
            direction=Direction.IN,
        ))

    async def test_small_xfer_upload(self):
        asyncio.create_task(self._handle_upload())
        xfer = asyncio.wait_for(self.xfer_manager.upload_asset(
            AssetType.BODYPART, self.SMALL_PAYLOAD
        ), timeout=0.05)
        await xfer
        self.assertEqual(self.received_bytes, self.SMALL_PAYLOAD)

    async def test_large_xfer_upload(self):
        # Larger payloads take a different path
        asyncio.create_task(self._handle_upload())
        xfer = asyncio.wait_for(self.xfer_manager.upload_asset(
            AssetType.BODYPART, self.LARGE_PAYLOAD
        ), timeout=0.05)
        await xfer
        self.assertEqual(self.received_bytes, self.LARGE_PAYLOAD)
