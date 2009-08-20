
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

# pyogp
from pyogp.lib.base.utilities.events import Event
from pyogp.lib.base.settings import Settings

# initialize logging
logger = getLogger('...message.message_handler')
log = logger.log

class MessageHandler(object):
    """ general class handling individual messages """

    def __init__(self, settings = None):
        """ i do nothing """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        self.handlers = {}

    def register(self, message_name):

        if self.settings.LOG_VERBOSE: log(DEBUG, 'Creating a monitor for %s' % (message_name))

        return self.handlers.setdefault(message_name, MessageHandledNotifier(message_name, self.settings))

    def is_message_handled(self, message_name):
        """ if the message is being monitored, return True, otherwise, return False 

        this can allow us to skip parsing inbound messages if no one is watching a particular one
        """

        try:

            handler = self.handlers[message_name]
            return True

        except KeyError:

            return False

    def handle(self, message):
        """ essentially a case statement to pass messages to event notifiers in the form of self attributes """

        try:

            handler = self.handlers[message.name]

            # Handle the message if we have subscribers
            # Conveniently, this will also enable verbose message logging
            if len(handler) > 0:
                if self.settings.LOG_VERBOSE and not (self.settings.UDP_SPAMMERS and self.settings.DISABLE_SPAMMERS): log(DEBUG, 'Handling message : %s' % (message.name))

                handler(message)

        except KeyError:
            #log(INFO, "Received an unhandled message: %s" % (message.name))
            pass

class MessageHandledNotifier(object):
    """ pseudo subclassing the Event class to treat the message like an event """

    def __init__(self, message_name, settings):
        self.event = Event()
        self.message_name = message_name
        self.settings = settings

    def subscribe(self, *args, **kwdargs):
        self.event.subscribe(*args, **kwdargs)

    def received(self, message):

        self.event(message)

    def unsubscribe(self, *args, **kwdargs):
        self.event.unsubscribe(*args, **kwdargs)

        if self.settings.LOG_VERBOSE: log(DEBUG, "Removed the monitor for %s by %s" % (args, kwdargs))

    def __len__(self):

        return len(self.event)

    __call__ = received



