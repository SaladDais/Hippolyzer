"""
Tooling for working with the SL viewer's LEAP integration: now with 100% less eventlet

TODO: split this out into its own package
"""

from __future__ import annotations

import collections
import contextlib
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
        self._pump_listeners: Dict[str, Set[asyncio.Queue]] = collections.defaultdict(set)
        self._connection_status = ConnectionStatus.READY
        self._drain_task = None

    @property
    def connected(self) -> bool:
        return self._connection_status == ConnectionStatus.CONNECTED

    @property
    def address(self) -> Optional[Tuple]:
        return self._writer.get_extra_info('peername', None)

    async def connect(self) -> None:
        """Receive the "hello" message from the viewer and start the message pump"""
        assert self._connection_status == ConnectionStatus.READY
        self._connection_status = ConnectionStatus.CONNECTING

        try:
            welcome_message = await self._read_message()
            self._reply_pump = welcome_message['pump']
            self.cmd_pump = welcome_message['data']['command']

            self._connection_status = ConnectionStatus.CONNECTED
            self._start_message_pump()
        except:
            self.disconnect()
            raise

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

    def disconnect(self) -> None:
        """Close the connection and clean up any pending request futures"""
        if self.connected:
            logging.info('closing LEAP connection from %r' % (self.address,))
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._writer.close()

        # Clean up any pending request futures
        for fut in list(self._reply_map.values()):
            if not fut.done():
                fut.cancel()
        self._reply_map.clear()
        # TODO: Give anything that cares about disconnects a signal that it's happened
        #  keep around Task handles and cancel those instead?
        self._pump_listeners.clear()

    def sys_command(self, op: str, data: Optional[Dict] = None) -> Optional[Awaitable]:
        """Make a request to an internal LEAP method over the command pump"""
        return self.command(self.cmd_pump, op, data)

    def command(self, pump: str, op: str, data: Optional[Dict] = None) -> Optional[Awaitable]:
        """Make a request to an internal LEAP method using the standard command form (op in data)"""
        data = data.copy() if data else {}
        data['op'] = op
        return self.request(pump, data)

    def request(self, pump: str, data: Any, expect_reply: bool = True) -> Optional[Awaitable]:
        """
        Send a message with request semantics to the other side

        Sending the message is done synchronously, only waiting for the reply is done async.
        """
        assert self.connected
        # If you don't pass in a dict for data, we have nowhere to stuff `reqid`.
        # That means no reply tracking, meaning no future.
        fut = None
        if isinstance(data, dict):
            # Store some state so we can track replies
            data = data.copy()
            # Tell the viewer the pump to send replies to
            data["reply"] = self._reply_pump
            if expect_reply:
                req_id = uuid.uuid4()
                data["reqid"] = req_id

                fut = asyncio.Future()
                # The future will be cleaned up when the Future is done.
                fut.add_done_callback(self._cleanup_request_future)
                self._reply_map[req_id] = fut

        self._write_message(pump, data)
        return fut

    def _write_message(self, pump: str, data: Any) -> None:
        assert self.connected
        ser = llsd.format_notation({"pump": pump, "data": data})
        payload = bytearray(str(len(ser)).encode("utf8"))
        payload.extend(b":")
        payload.extend(ser)
        self._writer.write(payload)
        # We're in sync context, we need to schedule draining the socket,
        # which is async. If a drain is already scheduled then we don't need to reschedule.
        if not self._drain_task:
            self._drain_task = asyncio.create_task(self._drain_soon())

    async def _drain_soon(self) -> None:
        self._drain_task = None
        await self._writer.drain()

    async def _read_message(self) -> Any:
        """Read a single inbound LEAP message"""
        assert self._connection_status in (ConnectionStatus.CONNECTED, ConnectionStatus.CONNECTING)

        length = int((await self._reader.readuntil(b':')).decode("utf8").strip()[:-1])
        if length > 0xffFFff:
            raise ValueError(f"Unreasonable LEAP payload length of {length}")
        parsed = llsd.parse_notation((await self._reader.readexactly(length)).strip())
        return parsed

    @contextlib.asynccontextmanager
    async def subscribe(self, source_pump: str) -> AsyncContextManager[Callable[[], Awaitable[Any]]]:
        """Subscribe to events published on source_pump, allow awaiting them"""
        assert self.connected

        msg_queue = asyncio.Queue()

        async def _get_wrapper():
            # TODO: handle disconnection while awaiting new Queue message
            msg = await msg_queue.get()

            # Consumption is completion
            msg_queue.task_done()
            return msg

        listener_name = "PythonListener-%s" % uuid.uuid4()
        listen_params = {"listener": listener_name, "source": source_pump}

        listeners = self._pump_listeners[source_pump]
        had_listeners = bool(listeners)
        listeners.add(msg_queue)

        if not had_listeners:
            await self.sys_command("listen", listen_params)

        try:
            yield _get_wrapper
        finally:
            listeners.remove(msg_queue)
            if self.connected and not listeners:
                await self.sys_command("stoplistening", listen_params)

    def handle_message(self, message: Any) -> bool:
        """
        Handle an inbound message and try to route it to the right recipient

        TODO: Events, somehow. Maybe a catch-all event as well?
        """
        if not isinstance(message, dict):
            logging.warning(f"Received a non-map message: {message!r}")
            return False

        pump = message.get("pump")
        data = message.get("data")
        if pump == self._reply_pump:
            # This is a reply for a request
            if not isinstance(data, dict):
                logging.warning(f"Received a non-map reply over the reply pump: {message!r}")
                return False

            # reqid can tell us what future needs to be resolved, if any.
            reqid = data.get("reqid")
            fut = self._reply_map.get(reqid)
            if not fut:
                logging.warning(f"Received a reply over the reply pump with no reqid or future: {message!r}")
                return False
            # We don't actually care about the reqid, pop it off
            data.pop("reqid")
            # Notify anyone awaiting about the received data
            fut.set_result(data)
        elif (listener_set := self._pump_listeners.get(pump)) is not None:
            for listener in listener_set:
                listener.put_nowait(data)
        else:
            logging.warning(f"Received a message for unknown pump: {message!r}")
        return True

    def _cleanup_request_future(self, req_fut: asyncio.Future) -> None:
        """Remove a completed future from the reply map"""
        for key, value in self._reply_map.items():
            if value == req_fut:
                del self._reply_map[key]
                return


class LEAPBridgeServer:
    """LEAP Bridge TCP server to use with asyncio.start_server()"""

    def __init__(self, client_connected_cb: Optional[Callable[[LEAPClient]], Awaitable[Any]] = None):
        self.clients: weakref.WeakSet[LEAPClient] = weakref.WeakSet()
        self._client_connected_cb = client_connected_cb

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        client = LEAPClient(reader, writer)
        logging.info('Accepting LEAP connection from %r' % (client.address,))
        await client.connect()

        self.clients.add(client)
        if self._client_connected_cb:
            await self._client_connected_cb(client)
