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

from logging import getLogger

logger = getLogger('utilities.events')


class Event:
    """ an object containing data which will be passed out to all subscribers """

    def __init__(self):
        self.subscribers = []

    def subscribe(self, handler, *args, one_shot=False, predicate=None, **kwargs):
        """ establish the subscribers (handlers) to this event """
        handler_tup = (handler, args, kwargs, one_shot, predicate)
        assert handler_tup not in self.subscribers
        self.subscribers.append(handler_tup)

        return self

    def _handler_key(self, handler):
        return handler[:3]

    def unsubscribe(self, handler, *args, **kwargs):
        """ remove the subscriber (handler) to this event """
        did_remove = False
        for registered in reversed(self.subscribers):
            if self._handler_key(registered) == (handler, args, kwargs):
                self.subscribers.remove(registered)
                did_remove = True
        if not did_remove:
            raise ValueError(f"Handler {handler!r} is not subscribed to this event.")
        return self

    def notify(self, args):
        for handler in self.subscribers[:]:
            instance, inner_args, kwargs, one_shot, predicate = handler
            if predicate and not predicate(args):
                continue
            if one_shot:
                self.unsubscribe(instance, *inner_args, **kwargs)
            if instance(args, *inner_args, **kwargs):
                self.unsubscribe(instance, *inner_args, **kwargs)

    def get_subscriber_count(self):
        return len(self.subscribers)

    def clear_subscribers(self):
        self.subscribers.clear()
        return self

    __iadd__ = subscribe
    __isub__ = unsubscribe
    __call__ = notify
    __len__ = get_subscriber_count
