"""
Tooling for working with the SL viewer's LEAP integration: now with 100% less eventlet

TODO: split this out into its own package
"""

from __future__ import annotations

from typing import *

import abc
import asyncio
import collections
import contextlib
import dataclasses
import enum
import logging
import pathlib
import uuid
import weakref

from hippolyzer.lib.base import llsd


class ConnectionStatus(enum.Enum):
    READY = enum.auto()
    CONNECTING = enum.auto()
    CONNECTED = enum.auto()
    DISCONNECTED = enum.auto()


@dataclasses.dataclass
class ListenerDetails:
    listener: Optional[str] = dataclasses.field(default_factory=lambda: "PythonListener-%s" % uuid.uuid4())
    queues: Set[asyncio.Queue] = dataclasses.field(default_factory=set)


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
        self._reply_futs: Dict[uuid.UUID, asyncio.Future] = {}
        self._pump_listeners: Dict[str, ListenerDetails] = collections.defaultdict(ListenerDetails)
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
        for fut in list(self._reply_futs.values()):
            if not fut.done():
                fut.cancel()
        self._reply_futs.clear()
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
        return self.send_message(pump, data)

    def void_command(self, pump: str, op: str, data: Optional[Dict] = None) -> None:
        """Like `command()`, but we don't expect a reply."""
        data = data.copy() if data else {}
        data['op'] = op
        self.send_message(pump, data, expect_reply=False)

    def send_message(self, pump: str, data: Any, expect_reply: bool = True) -> Optional[Awaitable]:
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

            # There are apparently some commands for which we can never expect to get a reply.
            # Don't add a reqid or reply fut map entry in that case, since it will never be resolved.
            if expect_reply:
                # Tell the viewer the pump to send replies to
                data["reply"] = self._reply_pump

                req_id = uuid.uuid4()
                data["reqid"] = req_id

                fut = asyncio.Future()
                # The future will be cleaned up when the Future is done.
                fut.add_done_callback(self._cleanup_request_future)
                self._reply_futs[req_id] = fut
        elif expect_reply:
            raise ValueError(f"Must send a dict in `data` if you want a reply, you sent {data!r}")

        self._write_message(pump, data)
        return fut

    def _write_message(self, pump: str, data: Any) -> None:
        assert self.connected
        ser = llsd.format_notation({"pump": pump, "data": data})
        payload = bytearray(str(len(ser)).encode("utf8"))
        payload.extend(b":")
        payload.extend(ser)
        self._writer.write(payload)
        # We're in sync context, we need to schedule draining the socket, which is async.
        # If a drain is already scheduled then we don't need to reschedule.
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
    async def listen_scoped(self, source_pump: str) -> AsyncContextManager[Callable[[], Awaitable[Any]]]:
        """Subscribe to events published on source_pump, allow awaiting them"""
        msg_queue = await self.listen(source_pump)

        async def _get_wrapper():
            # TODO: handle disconnection while awaiting new Queue message
            msg = await msg_queue.get()

            # Consumption is completion
            msg_queue.task_done()
            return msg

        try:
            yield _get_wrapper
        finally:
            try:
                await self.stop_listening(msg_queue)
            except KeyError:
                pass

    async def listen(self, source_pump: str) -> asyncio.Queue:
        """Start listening to `source_pump`, placing its messages in the returned asyncio Queue"""
        assert self.connected

        msg_queue = asyncio.Queue()

        listener_details = self._pump_listeners[source_pump]
        had_listeners = bool(listener_details.queues)
        listener_details.queues.add(msg_queue)

        if not had_listeners:
            # Nothing was listening to this before, need to ask for its events to be
            # sent over LEAP.
            await self.sys_command("listen", {
                "listener": listener_details.listener,
                "source": source_pump,
            })
        return msg_queue

    async def stop_listening(self, msg_queue: asyncio.Queue) -> None:
        """Stop sending a pump's messages to msg_queue, potentially removing the listen on the pump"""
        for source_pump, listener_details in self._pump_listeners.items():
            queues = listener_details.queues
            if msg_queue in queues:
                listener_details.queues.remove(msg_queue)
                if self.connected and not queues:
                    # Nobody cares about these events anymore, ask LEAP to stop sending them
                    await self.sys_command("stoplistening", {
                        "listener": listener_details.listener,
                        "source": source_pump,
                    })
                return
        raise KeyError(f"Couldn't find {msg_queue!r} in pump listeners")

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
            fut = self._reply_futs.get(reqid)
            if not fut:
                logging.warning(f"Received a reply over the reply pump with no reqid or future: {message!r}")
                return False
            # We don't actually care about the reqid, pop it off
            data.pop("reqid")
            # Notify anyone awaiting the response
            fut.set_result(data)

        # Might be related to a listener we registered
        # Don't warn if we get a message with an empty listener_details.queues because
        # We may still be receiving messages from before we stopped listening
        # The main concerning case if is we receive a message for something we _never_
        # registered a listener for.
        elif (listener_details := self._pump_listeners.get(pump)) is not None:
            for queue in listener_details.queues:
                queue.put_nowait(data)
        else:
            logging.warning(f"Received a message for unknown pump: {message!r}")
        return True

    def _cleanup_request_future(self, req_fut: asyncio.Future) -> None:
        """Remove a completed future from the reply map"""
        for key, value in self._reply_futs.items():
            if value == req_fut:
                del self._reply_futs[key]
                return


class LEAPAPIWrapper(abc.ABC):
    """Base class for classes wrapping specific LEAP APIs"""
    PUMP_NAME: Optional[str] = None

    def __init__(self, client: LEAPClient, pump_name: Optional[str] = None):
        super().__init__()
        self._client = client
        self._pump_name = pump_name or self.PUMP_NAME
        assert self._pump_name


class UIPath(pathlib.PurePosixPath):
    __slots__ = []

    @classmethod
    def for_floater(cls, floater_name: str) -> UIPath:
        return cls("/main_view/menu_stack/world_panel/Floater View") / floater_name


UI_PATH_TYPE = Optional[Union[str, UIPath]]


class LLWindowWrapper(LEAPAPIWrapper):
    PUMP_NAME = "LLWindow"

    MASK_TYPE = Optional[Collection[str]]
    KEYCODE_TYPE = Optional[int]
    KEYSYM_TYPE = Optional[str]
    CHAR_TYPE = Optional[str]
    MOUSE_COORD_TYPE: Optional[int]

    def _convert_key_payload(self, /, *, keycode: KEYCODE_TYPE, keysym: KEYSYM_TYPE, char: CHAR_TYPE,
                             mask: MASK_TYPE, path: UI_PATH_TYPE) -> Dict:
        if keycode is not None:
            payload = {"keycode": keycode}
        elif keysym is not None:
            payload = {"keysym": keysym}
        elif char is not None:
            payload = {"char": char}
        else:
            raise ValueError("Didn't have one of keycode, keysym or char")

        if path:
            payload["path"] = str(path)
        if mask:
            payload["mask"] = mask

        return payload

    def key_down(self, /, *, mask: MASK_TYPE = None, keycode: KEYCODE_TYPE = None,
                 keysym: KEYSYM_TYPE = None, char: CHAR_TYPE = None, path: UI_PATH_TYPE = None):
        """Simulate a key being pressed down"""
        payload = self._convert_key_payload(keysym=keysym, keycode=keycode, char=char, mask=mask, path=path)
        self._client.void_command(self._pump_name, "keyDown", payload)

    def key_up(self, /, *, mask: MASK_TYPE = None, keycode: KEYCODE_TYPE = None,
               keysym: KEYSYM_TYPE = None, char: CHAR_TYPE = None, path: UI_PATH_TYPE = None):
        """Simulate a key being released"""
        payload = self._convert_key_payload(keysym=keysym, keycode=keycode, char=char, mask=mask, path=path)
        self._client.void_command(self._pump_name, "keyUp", payload)

    def key_press(self, /, *, mask: MASK_TYPE = None, keycode: KEYCODE_TYPE = None,
                  keysym: KEYSYM_TYPE = None, char: CHAR_TYPE = None, path: UI_PATH_TYPE = None):
        """Simulate a key being pressed down and immediately released"""
        self.key_down(mask=mask, keycode=keycode, keysym=keysym, char=char, path=path)
        self.key_up(mask=mask, keycode=keycode, keysym=keysym, char=char, path=path)

    def text_input(self, text_input: str, path: UI_PATH_TYPE = None):
        """Simulate a user typing a string of text"""
        # TODO: Uhhhhh I can't see how the key* APIs could possibly handle i18n correctly,
        #  what with all the U8s. Maybe I'm just dumb?
        for char in text_input:
            self.key_press(char=char, path=path)

    async def get_paths(self, under: str = "") -> Dict:
        """Get all UI paths under the root, or under a path if specified"""
        return await self._client.command(self._pump_name, "getPaths", {"under": under})

    async def get_info(self, path: str) -> Dict:
        """Get info about an element specified by path"""
        return await self._client.command(self._pump_name, "getInfo", {"path": path})

    def _build_mouse_payload(self, /, *, x: MOUSE_COORD_TYPE, y: MOUSE_COORD_TYPE, path: UI_PATH_TYPE,
                             mask: MASK_TYPE, button: str = None) -> Dict:
        if path is not None:
            payload = {"path": str(path)}
        elif x is not None and y is not None:
            payload = {"x": x, "y": y}
        else:
            raise ValueError("Didn't have one of x + y or path")

        if mask:
            payload["mask"] = mask
        if button:
            payload["button"] = button

        return payload

    def mouse_down(self, /, *, x: MOUSE_COORD_TYPE = None, y: MOUSE_COORD_TYPE = None,
                   path: UI_PATH_TYPE = None, mask: MASK_TYPE = None, button: str) -> Awaitable[Dict]:
        """Simulate a mouse down event occurring at a coordinate or UI element path"""
        payload = self._build_mouse_payload(x=x, y=y, path=path, mask=mask, button=button)
        return self._client.command(self._pump_name, "mouseDown", payload)

    def mouse_up(self, /, *, x: MOUSE_COORD_TYPE = None, y: MOUSE_COORD_TYPE = None,
                 path: UI_PATH_TYPE = None, mask: MASK_TYPE = None, button: str) -> Awaitable[Dict]:
        """Simulate a mouse up event occurring at a coordinate or UI element path"""
        payload = self._build_mouse_payload(x=x, y=y, path=path, mask=mask, button=button)
        return self._client.command(self._pump_name, "mouseUp", payload)

    def mouse_click(self, /, *, x: MOUSE_COORD_TYPE = None, y: MOUSE_COORD_TYPE = None,
                    path: UI_PATH_TYPE = None, mask: MASK_TYPE = None, button: str) -> Awaitable[Dict]:
        """Simulate a mouse down and immediately following mouse up event"""
        # We're going to ignore the mouseDown response, so use void_command instead.
        # Most side effects are actually executed on mouseUp.
        self._client.void_command(self._pump_name, "mouseDown",
                                  self._build_mouse_payload(x=x, y=y, path=path, mask=mask, button=button))
        return self.mouse_up(x=x, y=y, path=path, mask=mask, button=button)

    def mouse_move(self, /, *, x: MOUSE_COORD_TYPE = None, y: MOUSE_COORD_TYPE = None,
                   path: UI_PATH_TYPE = None) -> Awaitable[Dict]:
        """Move the mouse to the coordinates or path specified"""
        payload = self._build_mouse_payload(x=x, y=y, path=path, mask=None)
        return self._client.command(self._pump_name, "mouseMove", payload)

    def mouse_scroll(self, clicks: int):
        """Act as if the scroll wheel has been moved `clicks` amount. May be negative"""
        self._client.command(self._pump_name, "mouseScroll", {"clicks": clicks})


class LLUIWrapper(LEAPAPIWrapper):
    PUMP_NAME = "UI"

    def call(self, function: str, parameter: Any = None) -> None:
        """
        Invoke the `function` operation as if from a menu or button click, passing `parameter`

        Can call most things registered through `LLUICtrl::CommitCallbackRegistry`.
        """
        self._client.void_command(self._pump_name, "call", {"function": function, "parameter": parameter})

    def get_value(self, path: UI_PATH_TYPE) -> Awaitable[Any]:
        """For the UI control identified by `path`, return the current value in `value`"""

        # We want the request to be sent immediately, without requiring `get_value()` to be `await`ed first,
        # but that means that we have to return a `Coroutine` that will pull the value out of the dict
        # rather than directly returning the `Future`.
        # TODO: extract this out into a helper function that makes "unwrapper" Coroutines that wrap a Future.
        resp_fut = self._client.command(self._pump_name, "getValue", {"path": str(path)})

        async def _wrapper():
            return (await resp_fut)['value']

        return _wrapper()


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
