"""
Tooling for working with the SL viewer's LEAP integration: now with 100% less eventlet

TODO: split this out into its own package
"""

from __future__ import annotations

from typing import *

import asyncio
import enum
import logging
import uuid
import weakref

from hippolyzer.lib.base import llsd


class ConnectionStatus(enum.Enum):
    READY = enum.auto()
    CONNECTING = enum.auto()
    CONNECTED = enum.auto()
    DISCONNECTED = enum.auto()


class LEAPClient:
    # TODO: better listener creation support
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self._reader = reader
        self._writer = writer
        # Pump used for receiving replies
        self._reply_pump: Optional[str] = None
        # Pump used for sending leap meta-commands to the viewer (getAPIs, etc.)
        self.cmd_pump: Optional[str] = None
        # Map of req id -> future held by requester to send responses to
        # TODO: LRU dict with cancel on evict.
        self._reply_map: Dict[uuid.UUID, asyncio.Future] = {}
        self._connection_status = ConnectionStatus.READY

    @property
    def connected(self):
        return self._connection_status == ConnectionStatus.CONNECTED

    async def connect(self):
        """Receive the "hello" message from the viewer and start the message pump"""
        assert self._connection_status == ConnectionStatus.READY
        self._connection_status = ConnectionStatus.CONNECTING

        welcome_message = await self._read_message()
        self._reply_pump = welcome_message['pump']
        self.cmd_pump = welcome_message['data']['command']

        self._connection_status = ConnectionStatus.CONNECTED
        self._start_message_pump()

    def _start_message_pump(self) -> None:
        """Read and handle inbound messages in a background task"""
        async def _pump_messages_forever():
            try:
                while not self._writer.is_closing() and not self._reader.at_eof():
                    self.handle_message(await self._read_message())
            except asyncio.IncompleteReadError:
                pass
            finally:
                self.disconnect()

        # Should naturally stop on its own when disconnect is called by virtue of
        # the incomplete read.
        asyncio.get_event_loop().create_task(_pump_messages_forever())

    def disconnect(self):
        """Close the connection and clean up any pending request futures"""
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._writer.close()

        # Clean up any pending request futures
        for fut in list(self._reply_map.values()):
            if not fut.done():
                fut.cancel()
        self._reply_map.clear()

    async def sys_command(self, op: str, data: Optional[Dict] = None) -> Any:
        """Make a request to an internal LEAP method over the command pump"""
        return await self.command(self.cmd_pump, op, data)

    async def command(self, pump: str, op: str, data: Optional[Dict] = None) -> Any:
        """Make a request to an internal LEAP method using the standard command form (op in data)"""
        data = data.copy() if data else {}
        data['op'] = op
        return await self.request(pump, data)

    async def request(self, pump: str, data: Any) -> Any:
        """Send a message with request semantics to the other side"""
        assert self.connected
        # If you don't pass in a dict for data, we have nowhere to stuff `reqid`.
        # That means no reply tracking, meaning no future.
        fut = None
        if isinstance(data, dict):
            # Store some state so we can track replies
            data = data.copy()
            # Tell the viewer the pump to send replies to
            data["reply"] = self._reply_pump
            req_id = uuid.uuid4()
            data["reqid"] = req_id

            fut = asyncio.Future()
            # The future will be cleaned up when the Future is done.
            fut.add_done_callback(self._cleanup_request_future)
            self._reply_map[req_id] = fut

        await self._write_message(pump, data)
        return await fut

    async def _write_message(self, pump: str, data: Any):
        assert self._connection_status == ConnectionStatus.CONNECTED
        ser = llsd.format_notation({"pump": pump, "data": data})
        payload = bytearray(str(len(ser)).encode("utf8"))
        payload.extend(b":")
        payload.extend(ser)
        self._writer.write(payload)
        await self._writer.drain()

    async def _read_message(self) -> Any:
        """Read a single inbound LEAP message"""
        assert self._connection_status in (ConnectionStatus.CONNECTED, ConnectionStatus.CONNECTING)

        length = int((await self._reader.readuntil(b':')).decode("utf8").strip()[:-1])
        if length > 0xffFFff:
            raise ValueError(f"Unreasonable LEAP payload length of {length}")
        parsed = llsd.parse_notation((await self._reader.readexactly(length)).strip())
        return parsed

    def handle_message(self, message: Any) -> bool:
        """
        Handle an inbound message and try to route it to the right recipient

        TODO: Events, somehow. Maybe a catch-all event as well?
        """
        if not isinstance(message, dict):
            return False

        data = message.get("data")
        if not isinstance(data, dict):
            return False

        # reqid can tell us what future needs to be resolved, if any.
        reqid = data.get("reqid")
        fut = self._reply_map.get(reqid)
        if not fut:
            return False
        # We don't actually care about the reqid, pop it off
        data.pop("reqid")
        # Notify anyone awaiting about the received data
        fut.set_result(data)
        return True

    def _cleanup_request_future(self, req_fut: asyncio.Future) -> None:
        """Remove a completed future from the reply map"""
        for key, value in self._reply_map.items():
            if value == req_fut:
                del self._reply_map[key]
                return


class LEAPBridgeServer:
    """LEAP Bridge server to use with asyncio.start_server()"""

    def __init__(self, client_connected_cb: Optional[Callable[[LEAPClient]], Awaitable[Any]] = None):
        self.clients: weakref.WeakSet[LEAPClient] = weakref.WeakSet()
        self._client_connected_cb = client_connected_cb

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername', None)
        logging.info('Accepting LEAP connection from %r' % (addr,))

        client = LEAPClient(reader, writer)
        try:
            await client.connect()
        except:
            writer.close()
            raise

        self.clients.add(client)
        if self._client_connected_cb:
            await self._client_connected_cb(client)
