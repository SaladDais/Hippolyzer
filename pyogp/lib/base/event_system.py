
"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""

# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import time

# related
from eventlet import api

# pyogp
from pyogp.lib.base.utilities.events import Event
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.exc import DataParsingError

# initialize logging
logger = getLogger('event_system')
log = logger.log

class AppEventsHandler(object):
    """ general class handling individual events """

    def __init__(self, settings = None):
        """ initialize the AppEventsHandler """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        self.handlers = {}

    def register(self, event_name, timeout = 0):
        """ create a watcher for a specific event in this event system. the timeout is optional, and defaults to no timeout """

        if self.settings.LOG_VERBOSE: log(DEBUG, 'Creating a monitor for %s' % (event_name))

        return self.handlers.setdefault(event_name, AppEventNotifier(event_name, self.settings, timeout))

    def is_event_handled(self, event_name):
        """ if the event is being monitored, return True, otherwise, return False """

        try:

            handler = self.handlers[event_name]
            return True

        except KeyError:

            return False

    def handle(self, event):
        """ essentially a case statement to pass event data to notifiers """

        try:

            handler = self.handlers[event.name]

            # Handle the packet if we have subscribers
            if len(handler) > 0:
                if self.settings.LOG_VERBOSE: log(DEBUG, 'Handling event: %s' % (event.name))

                handler(event)

        except KeyError:
            #log(INFO, "Received an unhandled packet: %s" % (packet.name))
            pass

class AppEventNotifier(object):
    """ access points for subscribing to application wide events. timeout = 0 for no timeout """

    def __init__(self, event_name, settings, timeout = 0):
        """ initialize an event notifier by name, with an optional timeout """

        self.event = Event()
        self.event_name = event_name
        self.settings = settings

        if type(timeout) == int:
            self.timeout = timeout
        else:
            raise DataParsingError("Timeout must be an integer creating an event watcher for %s" % (event_name))

    def subscribe(self, *args, **kwdargs):
        """ register a callback handler for a specific event, starting the timer if != 0, otherwise it will watch until forced to unsubscribe by the caller """

        self.args = args
        self.kwdargs = kwdargs

        self.event.subscribe(*args, **kwdargs)

        if self.timeout != 0:
            self._start_timer()

    def received(self, event):
        """ notifies subscribers about an event firing and passes along the data """

        self.event(event)

    def unsubscribe(self, *args, **kwdargs):
        """ stop watching this event """

        self.event.unsubscribe(*args, **kwdargs)

        if self.settings.LOG_VERBOSE: log(DEBUG, "Removed the monitor for %s by %s" % (args, kwdargs))

    def _start_timer(self):
        """ begins the timer when a timeout value is specified. returns None when the timer expires, then unsubscribes """

        now = time.time()
        start = now

        # spawn an empty coroutine for the duration of the timeout
        while now - start < self.timeout:

            api.sleep()
            now = time.time()

        # once the timeout has expired...
        if self.settings.LOG_VERBOSE: log(DEBUG, "Timing out the monitor for %s by %s" % (self.args, self.kwdargs))

        # return None to the callback handler
        self.received(None)

        # unsubscribe the watcher due to the timeout
        self.unsubscribe(*self.args, **self.kwdargs)

    def __len__(self):

        return len(self.event)

    __call__ = received

##########################
# Application Level Events
##########################

class AppEvent(object):
    """ container for an event payload. 
    
    name = name of the event, to which applications will subscribe. 
    payload = dict of the contents of the event (key:value)
    **kwdargs = key:value pairs
    
    either payload or **kwdargs should be used, not both
    """

    def __init__(self, name, payload = None, llsd = None, **kwargs):
        """ initialize the AppEvent contents """

        self.name = name
        self.payload = {}

        if payload != None and len(kwargs) > 0 and llsd != None:
            
            raise DataParsingError("AppEvent cannot parse both an explicit payload and a kwdargs representation of a payload")
            return

        if payload != None:
            
            if type(payload) == dict:
                
                self.payload = payload
                
            else:
                
                raise DataParsingError("AppEvent payload must be a dict. A %s was passed in." % (type(payload)))
                return
                
        elif len(kwargs) > 0:

            for key in kwargs.keys():

                self.payload[key] = kwargs[key]

        elif llsd != None:

            self.from_llsd(llsd)

        else:

            raise DataParsingError("AppEvent needs a payload or kwdargs, none were provided for %s." % (self.name))
            return

    def to_llsd(self):
        """ transform the event payload into llsd """

        raise NotImplemented("AppEvent().to_llsd() has not yet been written")

    def from_llsd(self):
        """ transform llsd into an event payload """

        raise NotImplemented("AppEvent().from_llsd() has not yet been written")

class AppEventEnum(object):
    """ enumeration of application level events and their keys"""

    InstantMessageReceived = ['FromAgentID', 'RegionID', 'Position', 'ID', 'FromAgentName', 'Message']
    ChatReceived  = ['FromName', 'SourceID', 'OwnerID', 'SourceType', 'ChatType', 'Audible', 'Position', 'Message']



