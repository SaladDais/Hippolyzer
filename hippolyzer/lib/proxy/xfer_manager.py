"""
Outbound Xfer only.

sim->viewer Xfer is only legitimately used for terrain so not worth implementing.
"""
from __future__ import annotations

import asyncio
import random
from typing import *

from hippolyzer.lib.base.datatypes import UUID
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
    def __init__(self, xfer_id: int):
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
        if packet_id.IsEOF:
            xfer.mark_done()
