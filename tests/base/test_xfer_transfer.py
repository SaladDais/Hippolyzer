import asyncio
import dataclasses
import unittest
from typing import *

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.message.circuit import ConnectionHolder
from hippolyzer.lib.base.templates import (
    AssetType,
    EstateAssetType,
    TransferSourceType,
    TransferRequestParamsSimEstate,
    TransferChannelType,
    TransferTargetType,
    TransferStatus,
)
from hippolyzer.lib.proxy.circuit import ProxiedCircuit
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.base.transfer_manager import TransferManager, Transfer
from hippolyzer.lib.base.xfer_manager import XferManager


class MockHandlingCircuit(ProxiedCircuit):
    def __init__(self, handler: MessageHandler[Message, str]):
        super().__init__(("127.0.0.1", 1), ("127.0.0.1", 2), None)
        self.handler = handler

    def _send_prepared_message(self, message: Message, transport=None):
        asyncio.get_event_loop().call_soon(self.handler.handle, message)


class MockConnectionHolder(ConnectionHolder):
    def __init__(self, circuit, message_handler):
        self.circuit = circuit
        self.message_handler = message_handler


class BaseTransferTests(unittest.IsolatedAsyncioTestCase):
    SMALL_PAYLOAD = b"foobar"
    LARGE_PAYLOAD = b"foobar" * 500

    def setUp(self) -> None:
        self.server_message_handler: MessageHandler[Message, str] = MessageHandler()
        self.client_message_handler: MessageHandler[Message, str] = MessageHandler()
        # The client side should send messages to the server side's message handler
        # and vice-versa
        self.client_circuit = MockHandlingCircuit(self.server_message_handler)
        self.server_circuit = MockHandlingCircuit(self.client_message_handler)
        self.server_connection = MockConnectionHolder(self.server_circuit, self.server_message_handler)
        self.client_connection = MockConnectionHolder(self.client_circuit, self.client_message_handler)


class XferManagerTests(BaseTransferTests):
    def setUp(self) -> None:
        super().setUp()
        self.secure_session_id = UUID.random()
        self.xfer_manager = XferManager(self.client_connection, self.secure_session_id)
        self.received_bytes: Optional[bytes] = None

    async def _handle_vfile_upload(self):
        msg = await self.server_message_handler.wait_for(('AssetUploadRequest',), timeout=0.01)
        asset_block = msg["AssetBlock"]
        transaction_id = asset_block["TransactionID"]
        asset_id = UUID.combine(transaction_id, self.secure_session_id)
        if asset_block["AssetData"]:
            self.received_bytes = asset_block["AssetData"]
        else:
            manager = XferManager(self.server_connection)
            xfer = await manager.request(vfile_id=asset_id, vfile_type=AssetType.BODYPART)
            self.received_bytes = xfer.reassemble_chunks()
        self.server_circuit.send_message(Message(
            "AssetUploadComplete",
            Block("AssetBlock", UUID=asset_id, Type=asset_block["Type"], Success=True),
            direction=Direction.IN,
        ))

    async def test_small_xfer_upload(self):
        asyncio.create_task(self._handle_vfile_upload())
        await asyncio.wait_for(self.xfer_manager.upload_asset(
            AssetType.BODYPART, self.SMALL_PAYLOAD
        ), timeout=0.1)
        self.assertEqual(self.received_bytes, self.SMALL_PAYLOAD)

    async def test_large_xfer_upload(self):
        # Larger payloads take a different path
        asyncio.create_task(self._handle_vfile_upload())
        await asyncio.wait_for(self.xfer_manager.upload_asset(
            AssetType.BODYPART, self.LARGE_PAYLOAD
        ), timeout=0.1)
        self.assertEqual(self.received_bytes, self.LARGE_PAYLOAD)


class TestTransferManager(BaseTransferTests):
    def setUp(self) -> None:
        super().setUp()
        self.transfer_manager = TransferManager(
            self.client_connection,
            UUID.random(),
            UUID.random(),
        )

    async def _handle_covenant_download(self):
        msg = await self.server_message_handler.wait_for(('TransferRequest',), timeout=0.01)
        self.assertEqual(TransferSourceType.SIM_ESTATE, msg["TransferInfo"]["SourceType"])
        tid = msg["TransferInfo"]["TransferID"]
        params: TransferRequestParamsSimEstate = msg["TransferInfo"][0].deserialize_var("Params")
        self.assertEqual(EstateAssetType.COVENANT, params.EstateAssetType)
        data = self.LARGE_PAYLOAD

        self.server_circuit.send_message(Message(
            'TransferInfo',
            Block(
                'TransferInfo',
                TransferID=tid,
                ChannelType=TransferChannelType.MISC,
                TargetType_=TransferTargetType.UNKNOWN,
                Status=TransferStatus.OK,
                Size=len(self.LARGE_PAYLOAD),
                Params_=dataclasses.asdict(params),
            ),
        ))
        packet_num = 0
        while True:
            chunk = data[:1000]
            data = data[1000:]
            self.server_circuit.send_message(Message(
                'TransferPacket',
                Block(
                    'TransferData',
                    TransferID=tid,
                    ChannelType=TransferChannelType.MISC,
                    Packet=packet_num,
                    Status=TransferStatus.OK if data else TransferStatus.DONE,
                    Data=chunk,
                )
            ))
            if not data:
                break
            packet_num += 1

    async def test_simple_transfer(self):
        asyncio.create_task(self._handle_covenant_download())
        transfer: Transfer = await asyncio.wait_for(self.transfer_manager.request(
            source_type=TransferSourceType.SIM_ESTATE,
            params=TransferRequestParamsSimEstate(
                EstateAssetType=EstateAssetType.COVENANT,
            ),
        ), 0.1)
        self.assertEqual(len(self.LARGE_PAYLOAD), transfer.expected_size)
        self.assertEqual(self.LARGE_PAYLOAD, transfer.reassemble_chunks())
