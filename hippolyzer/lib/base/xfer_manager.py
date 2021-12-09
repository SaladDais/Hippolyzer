"""
Managers for inbound and outbound xfer as well as the AssetUploadRequest flow
"""
from __future__ import annotations

import asyncio
import enum
import random
from typing import *

from hippolyzer.lib.base.datatypes import UUID, RawBytes
from hippolyzer.lib.base.message.data_packer import TemplateDataPacker
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.message.msgtypes import MsgType
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.base.message.circuit import ConnectionHolder
from hippolyzer.lib.base.templates import XferPacket, XferFilePath, AssetType, XferError

_XFER_MESSAGES = {"AbortXfer", "ConfirmXferPacket", "RequestXfer", "SendXferPacket"}


MAX_CHUNK_SIZE = 1150
ACK_AHEAD_MAX = 10


class Xfer:
    def __init__(
            self,
            xfer_id: Optional[int] = None,
            direction: Direction = Direction.OUT,
            data: Optional[bytes] = None,
            turbo: bool = False,
    ):
        self.xfer_id: Optional[int] = xfer_id
        self.chunks: Dict[int, bytes] = {}
        self.expected_size: Optional[int] = None
        self.size_known = asyncio.Future()
        self.error_code: Union[int, XferError] = 0
        self.next_ackable = 0
        self.turbo = turbo
        self.direction: Direction = direction
        self.expected_chunks: Optional[int] = None
        self._future: asyncio.Future[Xfer] = asyncio.Future()

        if data is not None:
            # Prepend the expected length field to the first chunk
            if not isinstance(data, RawBytes):
                data = TemplateDataPacker.pack(len(data), MsgType.MVT_S32) + data
            chunk_num = 0
            while data:
                self.chunks[chunk_num] = data[:MAX_CHUNK_SIZE]
                data = data[MAX_CHUNK_SIZE:]
                chunk_num += 1

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
    def __init__(
            self,
            connection_holder: ConnectionHolder,
            secure_session_id: Optional[UUID] = None,
    ):
        self._connection_holder = connection_holder
        self._secure_session_id = secure_session_id

    def request(
            self, xfer_id: Optional[int] = None,
            file_name: Union[bytes, str, None] = None,
            file_path: Optional[Union[XferFilePath, int]] = None,
            vfile_id: Optional[UUID] = None,
            vfile_type: Optional[Union[AssetType, int]] = None,
            use_big_packets: bool = False,
            delete_on_completion: bool = True,
            turbo: bool = False,
            direction: Direction = Direction.OUT,
    ) -> Xfer:
        xfer_id = xfer_id if xfer_id is not None else random.getrandbits(64)
        self._connection_holder.circuit.send(Message(
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
            direction=direction,
        ))
        xfer = Xfer(xfer_id, direction=direction, turbo=turbo)
        asyncio.create_task(self._pump_xfer_replies(xfer))
        return xfer

    async def _pump_xfer_replies(self, xfer: Xfer):
        with self._connection_holder.message_handler.subscribe_async(
                _XFER_MESSAGES,
                predicate=xfer.is_our_message,
        ) as get_msg:
            while not xfer.done():
                try:
                    msg: Message = await asyncio.wait_for(get_msg(), 5.0)
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

    def _handle_send_xfer_packet(self, msg: Message, xfer: Xfer):
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

        to_ack = (packet_id.PacketID,)
        if xfer.turbo:
            # ACK the next few packets we expect to be sent, if we haven't already
            ack_max = packet_id.PacketID + ACK_AHEAD_MAX
            to_ack = range(xfer.next_ackable, ack_max)
            xfer.next_ackable = ack_max
        for ack_id in to_ack:
            self._connection_holder.circuit.send(Message(
                "ConfirmXferPacket",
                Block("XferID", ID=xfer.xfer_id, Packet=ack_id),
                direction=xfer.direction,
            ))

        xfer.chunks[packet_id.PacketID] = packet_data
        # We may be waiting on other packets so we can't end immediately.
        if packet_id.IsEOF:
            xfer.expected_chunks = packet_id.PacketID + 1
        if not xfer.done() and len(xfer.chunks) == xfer.expected_chunks:
            xfer.mark_done()

    def upload_asset(
            self,
            asset_type: AssetType,
            data: Union[bytes, str],
            store_local: bool = False,
            temp_file: bool = False,
            transaction_id: Optional[UUID] = None,
            upload_strategy: Optional[UploadStrategy] = None,
    ) -> asyncio.Future[UUID]:
        """Upload an asset through the Xfer upload path"""
        if not transaction_id:
            transaction_id = UUID.random()
        if isinstance(data, str):
            data = data.encode("utf8")

        # Small amounts of data can be sent inline, decide based on size
        if upload_strategy is None:
            if len(data) >= MAX_CHUNK_SIZE:
                upload_strategy = UploadStrategy.XFER
            else:
                upload_strategy = UploadStrategy.ASSET_UPLOAD_REQUEST

        xfer = None
        inline_data = b''
        if upload_strategy == UploadStrategy.XFER:
            xfer = Xfer(data=data)
        else:
            inline_data = data

        self._connection_holder.circuit.send(Message(
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
        message_handler = self._connection_holder.message_handler
        # We'll receive an Xfer request for the asset we're uploading.
        # asset ID is determined by hashing secure session ID with chosen transaction ID.
        asset_id: UUID = UUID.combine(transaction_id, self._secure_session_id)
        try:
            # Only need to do this if we're using the xfer upload strategy, otherwise all the
            # data was already sent in the AssetUploadRequest and we don't expect a RequestXfer.
            def request_predicate(request_msg: Message):
                return request_msg["XferID"]["VFileID"] == asset_id
            if xfer is not None:
                await self.serve_inbound_xfer_request(xfer, request_predicate)

            def complete_predicate(complete_msg: Message):
                return complete_msg["AssetBlock"]["UUID"] == asset_id
            msg = await message_handler.wait_for(('AssetUploadComplete',), predicate=complete_predicate)
            if msg["AssetBlock"]["Success"] == 1:
                fut.set_result(asset_id)
            else:
                fut.set_exception(RuntimeError(f"Xfer for transaction {transaction_id} failed"))

        except asyncio.TimeoutError as e:
            fut.set_exception(e)

    async def serve_inbound_xfer_request(
            self,
            xfer: Xfer,
            request_predicate: Callable[[Message], bool],
            wait_for_confirm: bool = True
    ):
        message_handler = self._connection_holder.message_handler
        request_msg = await message_handler.wait_for(
            ('RequestXfer',), predicate=request_predicate, timeout=5.0)
        xfer.xfer_id = request_msg["XferID"]["ID"]

        packet_id = 0
        # TODO: No resend yet. If it's lost, it's lost.
        while xfer.chunks:
            chunk = xfer.chunks.pop(packet_id)
            # EOF if there are no chunks left
            packet_val = XferPacket(PacketID=packet_id, IsEOF=not bool(xfer.chunks))
            self._connection_holder.circuit.send(Message(
                "SendXferPacket",
                Block("XferID", ID=xfer.xfer_id, Packet_=packet_val),
                Block("DataPacket", Data=chunk),
                # Send this towards the sender of the RequestXfer
                direction=~request_msg.direction,
            ))
            # Don't care about the value, just want to know it was confirmed.
            if wait_for_confirm:
                await message_handler.wait_for(
                    ("ConfirmXferPacket",), predicate=xfer.is_our_message, timeout=5.0)
            packet_id += 1
