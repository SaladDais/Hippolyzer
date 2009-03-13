"""
@file events_system.py
@date 2009-01-29
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

class Event(object):
    """ an object containing data which will be passed out to all subscribers """

    def __init__(self):

        self.subscribers = []

    def subscribe(self, handler, *args, **kwargs):
        """ establish the subscribers (handlers) to this event """

        self.subscribers.append( ( handler, args, kwargs) )

        return self

    def unsubscribe(self, handler, *args, **kwargs):
        """ remove the subscriber (handler) to this event """

        try:

            self.subscribers.remove((handler, args, kwargs))

        except:
            raise ValueError("Handler is not subscribed to this event.")

        return self

    def notify(self, args):

        for instance, inner_args, kwargs in self.subscribers:
            instance(args, *inner_args, **kwargs)

    def getSubscriberCount(self):

        return len(self.subscribers)

    def clearSubscribers(self):

        self.subscribers.clear()
        return self

    def getSubscribers(self):

        return self.subscribers

    __iadd__ = subscribe
    __isub__ = unsubscribe
    __call__ = notify
    __len__  = getSubscriberCount