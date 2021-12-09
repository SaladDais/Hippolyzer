"""
Outbound Transfer only.
"""
from __future__ import annotations

import asyncio
import dataclasses
from typing import *

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.message.circuit import ConnectionHolder
from hippolyzer.lib.base.templates import (
    TransferRequestParamsBase,
    TransferChannelType,
    TransferSourceType,
    TransferStatus,
)


_TRANSFER_MESSAGES = {"TransferInfo", "TransferPacket", "TransferAbort"}


class Transfer:
    def __init__(self, transfer_id: UUID):
        super().__init__()
        self.transfer_id: UUID = transfer_id
        self.chunks: Dict[int, bytes] = {}
        self.expected_size: Optional[int] = None
        self.size_known = asyncio.Future()
        self.error_code: Union[int] = 0
        self._future: asyncio.Future[Transfer] = asyncio.Future()

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

    def is_our_message(self, message: Message):
        if "TransferData" in message.blocks:
            transfer_block = message["TransferData"][0]
        else:
            transfer_block = message["TransferInfo"][0]
        return transfer_block["TransferID"] == self.transfer_id

    def cancel(self) -> bool:
        if not self.size_known.done():
            self.size_known.cancel()
        return self._future.cancel()

    def set_exception(self, exc: Union[type, BaseException]) -> None:
        if not self.size_known.done():
            self.size_known.set_exception(exc)
        return self._future.set_exception(exc)

    def __await__(self) -> Generator[Any, None, Transfer]:
        return self._future.__await__()


class TransferManager:
    def __init__(
            self,
            connection_holder: ConnectionHolder,
            agent_id: Optional[UUID] = None,
            session_id: Optional[UUID] = None,
    ):
        self._connection_holder = connection_holder
        self._agent_id = agent_id
        self._session_id = session_id

    def request(
            self, *,
            source_type: TransferSourceType,
            params: TransferRequestParamsBase,
            transfer_id: Optional[UUID] = None,
            channel_type: TransferChannelType = TransferChannelType.ASSET,
            priority: float = 101.0,
    ) -> Transfer:
        transfer_id = transfer_id if transfer_id is not None else UUID.random()
        params_dict = dataclasses.asdict(params)
        # Fill in any missing AgentID or SessionID attrs if the params type has them
        if params_dict.get("AgentID", dataclasses.MISSING) is None:
            params.AgentID = self._agent_id
        if params_dict.get("SessionID", dataclasses.MISSING) is None:
            params.SessionID = self._session_id

        self._connection_holder.circuit.send(Message(
            'TransferRequest',
            Block(
                'TransferInfo',
                TransferID=transfer_id,
                ChannelType=channel_type,
                SourceType=source_type,
                Priority=priority,
                Params_=params,
            ),
        ))
        transfer = Transfer(transfer_id)
        asyncio.create_task(self._pump_transfer_replies(transfer))
        return transfer

    async def _pump_transfer_replies(self, transfer: Transfer):
        # Subscribe to message related to our transfer while we're in this block
        with self._connection_holder.message_handler.subscribe_async(
                _TRANSFER_MESSAGES,
                predicate=transfer.is_our_message,
        ) as get_msg:
            while not transfer.done():
                try:
                    msg: Message = await asyncio.wait_for(get_msg(), 5.0)
                except TimeoutError as e:
                    transfer.set_exception(e)
                    return
                if transfer.cancelled():
                    # Just let any new packets drop on the floor.
                    return

                if msg.name == "TransferPacket":
                    self._handle_transfer_packet(msg, transfer)
                elif msg.name == "TransferInfo":
                    self._handle_transfer_info(msg, transfer)
                elif msg.name == "TransferAbort":
                    transfer.error_code = msg["TransferID"][0].deserialize_var("Result")
                    transfer.set_exception(
                        ConnectionAbortedError("Unknown failure")
                    )

    def _handle_transfer_packet(self, msg: Message, transfer: Transfer):
        transfer_block = msg["TransferData"][0]
        packet_id: int = transfer_block["Packet"]
        packet_data = transfer_block["Data"]
        transfer.chunks[packet_id] = packet_data
        if transfer_block["Status"] == TransferStatus.DONE and not transfer.done():
            transfer.mark_done()

    def _handle_transfer_info(self, msg: Message, transfer: Transfer):
        transfer_block = msg["TransferInfo"][0]
        transfer.expected_size = transfer_block["Size"]
        # Don't re-set if we get a resend of packet 0
        if not transfer.size_known.done():
            transfer.size_known.set_result(transfer.expected_size)
        if transfer_block["Status"] != TransferStatus.OK:
            transfer.error_code = transfer_block['Status']
            transfer.set_exception(ConnectionAbortedError(
                f"Transfer failed with {transfer_block['Status']}"))
