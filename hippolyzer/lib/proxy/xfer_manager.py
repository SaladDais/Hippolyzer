"""
Managers for inbound and outbound xfer as well as the AssetUploadRequest flow
"""
from __future__ import annotations

import asyncio
import enum
import random
from typing import *

from hippolyzer.lib.base.datatypes import UUID, RawBytes
from hippolyzer.lib.base.helpers import proxify
from hippolyzer.lib.base.message.data_packer import TemplateDataPacker
from hippolyzer.lib.base.message.message import Block
from hippolyzer.lib.base.message.msgtypes import MsgType
from hippolyzer.lib.proxy.message import ProxiedMessage
from hippolyzer.lib.proxy.templates import XferPacket, XferFilePath, AssetType, XferError

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion

_XFER_MESSAGES = {"AbortXfer", "ConfirmXferPacket", "RequestXfer", "SendXferPacket"}


class Xfer:
    def __init__(self, xfer_id: Optional[int] = None):
        super().__init__()
        self.xfer_id: Optional[int] = xfer_id
        self.chunks: Dict[int, bytes] = {}
        self.expected_size: Optional[int] = None
        self.size_known = asyncio.Future()
        self.error_code: Union[int, XferError] = 0
        self._future: asyncio.Future[Xfer] = asyncio.Future()

    def reassemble_chunks(self) -> bytes:
        assembled = bytearray()
        for _, data in sorted(self.chunks.items()):
            assembled.extend(data)
        return assembled

    def mark_done(self):
        self._future.set_result(self)

    def done(self) -> bool:
        return self._future.done()

    def cancelled(self) -> bool:
        return self._future.cancelled()

    def is_our_message(self, message):
        return message["XferID"]["ID"] == self.xfer_id

    def cancel(self) -> bool:
        if not self.size_known.done():
            self.size_known.cancel()
        return self._future.cancel()

    def set_exception(self, exc: Union[type, BaseException]) -> None:
        if not self.size_known.done():
            self.size_known.set_exception(exc)
        return self._future.set_exception(exc)

    def __await__(self) -> Generator[Any, None, Xfer]:
        return self._future.__await__()


class UploadStrategy(enum.IntEnum):
    XFER = enum.auto()
    ASSET_UPLOAD_REQUEST = enum.auto()


class XferManager:
    def __init__(self, region: ProxiedRegion):
        self._region: ProxiedRegion = proxify(region)

    def request(
            self, xfer_id: Optional[int] = None,
            file_name: Union[bytes, str, None] = None,
            file_path: Optional[Union[XferFilePath, int]] = None,
            vfile_id: Optional[UUID] = None,
            vfile_type: Optional[Union[AssetType, int]] = None,
            use_big_packets: bool = False,
            delete_on_completion: bool = False,
    ) -> Xfer:
        xfer_id = xfer_id if xfer_id is not None else random.getrandbits(64)
        self._region.circuit.send_message(ProxiedMessage(
            'RequestXfer',
            Block(
                'XferID',
                ID=xfer_id,
                Filename=file_name or b'',
                FilePath=file_path or XferFilePath.NONE,
                DeleteOnCompletion=delete_on_completion,
                UseBigPackets=use_big_packets,
                VFileID=vfile_id or UUID(),
                VFileType=vfile_type or AssetType.NONE,
            ),
        ))
        xfer = Xfer(xfer_id)
        asyncio.create_task(self._pump_xfer_replies(xfer))
        return xfer

    async def _pump_xfer_replies(self, xfer: Xfer):
        with self._region.message_handler.subscribe_async(
            _XFER_MESSAGES,
            predicate=xfer.is_our_message
        ) as get_msg:
            while not xfer.done():
                try:
                    msg: ProxiedMessage = await asyncio.wait_for(get_msg(), 5.0)
                except asyncio.exceptions.TimeoutError as e:
                    xfer.set_exception(e)
                    return

                if xfer.cancelled():
                    # AbortXfer doesn't seem to work on in-progress Xfers.
                    # Just let any new packets drop on the floor.
                    return

                if msg.name == "SendXferPacket":
                    self._handle_send_xfer_packet(msg, xfer)
                elif msg.name == "AbortXfer":
                    xfer.error_code = msg["XferID"][0].deserialize_var("Result")
                    xfer.set_exception(
                        ConnectionAbortedError(f"Xfer failed with {xfer.error_code!r}")
                    )

    def _handle_send_xfer_packet(self, msg: ProxiedMessage, xfer: Xfer):
        # Received a SendXfer for an Xfer we sent ourselves
        packet_id: XferPacket = msg["XferID"][0].deserialize_var("Packet")
        packet_data = msg["DataPacket"]["Data"]
        # First 4 bytes are expected total data length
        if packet_id.PacketID == 0:
            # Yes, S32. Only used as a hint so buffers can be pre-allocated,
            # EOF bit determines when the data actually ends.
            xfer.expected_size = TemplateDataPacker.unpack(packet_data[:4], MsgType.MVT_S32)
            # Don't re-set if we get a resend of packet 0
            if not xfer.size_known.done():
                xfer.size_known.set_result(xfer.expected_size)
            packet_data = packet_data[4:]

        self._region.circuit.send_message(ProxiedMessage(
            "ConfirmXferPacket",
            Block("XferID", ID=xfer.xfer_id, Packet=packet_id.PacketID),
        ))

        xfer.chunks[packet_id.PacketID] = packet_data
        if packet_id.IsEOF and not xfer.done():
            xfer.mark_done()

    def upload_asset(
            self,
            asset_type: AssetType,
            data: bytes,
            store_local: bool = False,
            temp_file: bool = False,
            transaction_id: Optional[UUID] = None,
            upload_strategy: Optional[UploadStrategy] = None,
    ) -> asyncio.Future[UUID]:
        """Upload an asset through the Xfer upload path"""
        if not transaction_id:
            transaction_id = UUID.random()

        # Small amounts of data can be sent inline, decide based on size
        if upload_strategy is None:
            if len(data) >= 1150:
                upload_strategy = UploadStrategy.XFER
            else:
                upload_strategy = UploadStrategy.ASSET_UPLOAD_REQUEST

        xfer = None
        inline_data = b''
        if upload_strategy == UploadStrategy.XFER:
            # Prepend the expected length field to the first chunk
            if not isinstance(data, RawBytes):
                data = TemplateDataPacker.pack(len(data), MsgType.MVT_S32) + data
            xfer = Xfer()
            chunk_num = 0
            while data:
                xfer.chunks[chunk_num] = data[:1150]
                data = data[1150:]
        else:
            inline_data = data

        self._region.circuit.send_message(ProxiedMessage(
            "AssetUploadRequest",
            Block(
                "AssetBlock",
                TransactionID=transaction_id,
                Type=asset_type,
                Tempfile=temp_file,
                StoreLocal=store_local,
                AssetData=inline_data,
            )
        ))
        fut = asyncio.Future()
        asyncio.create_task(self._pump_asset_upload(xfer, transaction_id, fut))
        return fut

    async def _pump_asset_upload(self, xfer: Optional[Xfer], transaction_id: UUID, fut: asyncio.Future):
        message_handler = self._region.message_handler
        # We'll receive an Xfer request for the asset we're uploading.
        # asset ID is determined by hashing secure session ID with chosen transaction ID.
        asset_id: UUID = self._region.session().tid_to_assetid(transaction_id)
        try:
            # Only need to do this if we're using the xfer upload strategy, otherwise all the
            # data was already sent in the AssetUploadRequest and we don't expect a RequestXfer.
            if xfer is not None:
                def request_predicate(request_msg: ProxiedMessage):
                    return request_msg["XferID"]["VFileID"] == asset_id
                msg = await message_handler.wait_for(
                    'RequestXfer', predicate=request_predicate, timeout=5000)
                xfer.xfer_id = msg["XferID"]["ID"]

                packet_id = 0
                # TODO: No resend yet. If it's lost, it's lost.
                while xfer.chunks:
                    chunk = xfer.chunks.pop(packet_id)
                    # EOF if there are no chunks left
                    packet_val = XferPacket(PacketID=packet_id, IsEOF=not bool(xfer.chunks))
                    self._region.circuit.send_message(ProxiedMessage(
                        "SendXferPacket",
                        Block("XferID", ID=xfer.xfer_id, Packet_=packet_val),
                        Block("DataPacket", Data=chunk),
                    ))
                    # Don't care about the value, just want to know it was confirmed.
                    await message_handler.wait_for(
                        "ConfirmXferPacket", predicate=xfer.is_our_message, timeout=5000)
                    packet_id += 1

            def complete_predicate(complete_msg: ProxiedMessage):
                return complete_msg["AssetBlock"]["UUID"] == asset_id
            msg = await message_handler.wait_for('AssetUploadComplete', predicate=complete_predicate)
            if msg["AssetBlock"]["Success"] == 1:
                fut.set_result(asset_id)
            else:
                fut.set_exception(RuntimeError(f"Xfer for transaction {transaction_id} failed"))

        except asyncio.TimeoutError as e:
            fut.set_exception(e)
