# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

# pyogp
from pyogp.lib.base.utilities.events import Event
from pyogp.lib.base.settings import Settings

# initialize logging
logger = getLogger('...message.packethandler')
log = logger.log

class PacketHandler(object):
    """ general class handling individual packets """

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

    def _register(self, packet_name):

        if self.settings.LOG_VERBOSE: log(DEBUG, 'Creating a monitor for %s' % (packet_name))

        return self.handlers.setdefault(packet_name, PacketReceivedNotifier(packet_name, self.settings))

    def is_packet_handled(self, packet_name):
        """ if the packet is being monitored, return True, otherwise, return False 

        this can allow us to skip parsing inbound packets if no one is watching a particular one
        """

        try:

            handler = self.handlers[packet_name]
            return True

        except KeyError:

            return False

    def _handle(self, packet):
        """ essentially a case statement to pass packets to event notifiers in the form of self attributes """

        try:

            handler = self.handlers[packet.name]

            # Handle the packet if we have subscribers
            # Conveniently, this will also enable verbose packet logging
            if len(handler) > 0:
                if self.settings.LOG_VERBOSE and not (self.settings.UDP_SPAMMERS and self.settings.DISABLE_SPAMMERS): log(DEBUG, 'Handling packet : %s' % (packet.name))

                handler(packet)

        except KeyError:
            #log(INFO, "Received an unhandled packet: %s" % (packet.name))
            pass

class PacketReceivedNotifier(object):
    """ received TestMessage packet """

    def __init__(self, packet_name, settings):
        self.event = Event()
        self.packet_name = packet_name
        self.settings = settings

    def subscribe(self, *args, **kwdargs):
        self.event.subscribe(*args, **kwdargs)

    def received(self, packet):

        self.event(packet)

    def unsubscribe(self, *args, **kwdargs):
        self.event.unsubscribe(*args, **kwdargs)

        if self.settings.LOG_VERBOSE: log(DEBUG, "Removed the monitor for %s by %s" % (args, kwdargs))

    def __len__(self):

        return len(self.event)

    __call__ = received

"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

