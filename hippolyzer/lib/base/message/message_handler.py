"""
Copyright 2009, Linden Research, Inc.
  See NOTICE.md for previous contributors
Copyright 2021, Salad Dais
All Rights Reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import asyncio
import contextlib
import logging
from typing import *

from hippolyzer.lib.base.events import Event

LOG = logging.getLogger(__name__)
_T = TypeVar("_T")
_K = TypeVar("_K", bound=Hashable)
MESSAGE_HANDLER = Callable[[_T], Any]
PREDICATE = Callable[[_T], bool]
MESSAGE_NAMES = Iterable[_K]


class MessageHandler(Generic[_T, _K]):
    def __init__(self, take_by_default: bool = True):
        self.handlers: Dict[_K, Event] = {}
        self.take_by_default = take_by_default

    def register(self, message_name: _K) -> Event:
        LOG.debug('Creating a monitor for %s' % message_name)
        return self.handlers.setdefault(message_name, Event())

    def subscribe(self, message_name: _K, handler: MESSAGE_HANDLER) -> Event:
        notifier = self.register(message_name)
        notifier.subscribe(handler)
        return notifier

    def _subscribe_all(self, message_names: MESSAGE_NAMES, handler: MESSAGE_HANDLER,
                       predicate: Optional[PREDICATE] = None) -> List[Event]:
        notifiers = [self.register(name) for name in message_names]
        for n in notifiers:
            n.subscribe(handler, predicate=predicate)
        return notifiers

    @contextlib.contextmanager
    def subscribe_async(self, message_names: MESSAGE_NAMES, predicate: Optional[PREDICATE] = None,
                        take: Optional[bool] = None) -> ContextManager[Callable[[], Awaitable[_T]]]:
        """
        Subscribe to a set of message matching predicate while within a block

        Defaults to taking the message out of the usual flow, and any matching messages will
        not be automatically be forwarded through to the client, allowing the subscriber coroutine
        time to modify or drop the message. Taken messages must be manually sent to the client by
        subscribers if desired.

        If a subscriber is just an observer that will never drop or modify a message, take=False
        may be used and messages will be sent as usual.
        """
        if take is None:
            take = self.take_by_default
        msg_queue = asyncio.Queue()

        def _handler_wrapper(message: _T):
            # Consider this message owned by one of the async handlers, drop it
            if take:
                message = message.take()
            msg_queue.put_nowait(message)

        notifiers = self._subscribe_all(message_names, _handler_wrapper, predicate=predicate)

        async def _get_wrapper():
            msg = await msg_queue.get()
            # Consumption is completion
            msg_queue.task_done()
            return msg

        try:
            yield _get_wrapper
        finally:
            for n in notifiers:
                n.unsubscribe(_handler_wrapper)

    def wait_for(self, message_names: MESSAGE_NAMES, predicate: Optional[PREDICATE] = None,
                 timeout: Optional[float] = None, take: Optional[bool] = None) -> Awaitable[_T]:
        """
        Wait for a single instance one of message_names matching predicate

        Any packets matching predicate will be considered owned by the caller and will be
        automatically dropped unless `take=False`. This should not be used if waiting for a
        sequence of packets, since multiple packets may come in after the future has already
        been marked completed, causing some to be missed.
        """
        if take is None:
            take = self.take_by_default
        notifiers = [self.register(name) for name in message_names]

        loop = asyncio.get_event_loop_policy().get_event_loop()
        fut = loop.create_future()
        timeout_task = None

        async def _canceller():
            await asyncio.sleep(timeout)
            if not fut.done():
                fut.set_exception(asyncio.exceptions.TimeoutError("Timed out waiting for packet"))
            for n in notifiers:
                n.unsubscribe(_handler)

        if timeout:
            timeout_task = asyncio.create_task(_canceller())

        def _handler(message: _T):
            if timeout_task:
                timeout_task.cancel()
            # Whatever was awaiting this future now owns this message
            if take:
                message = message.take()
            if not fut.done():
                fut.set_result(message)
            # Make sure to unregister this handler for all message types
            for n in notifiers:
                n.unsubscribe(_handler)

        for notifier in notifiers:
            notifier.subscribe(_handler, predicate=predicate)
        return fut

    def is_handled(self, message_name: _K):
        return message_name in self.handlers

    def handle(self, message: _T):
        self._handle_type(message.name, message)
        # Always try to call wildcard handlers
        self._handle_type('*', message)

    def _handle_type(self, name: _K, message: _T):
        handler = self.handlers.get(name)
        if not handler:
            return

        if len(handler) > 0:
            LOG.debug('Handling message : %s' % name)
            handler(message)
