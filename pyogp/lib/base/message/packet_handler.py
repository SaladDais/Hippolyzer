"""
@file packet_handler.py
@date 2009-02-02
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
# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

from pyogp.lib.base.utilities.events import Event

# initialize logging
logger = getLogger('...base.message.packet_handler')
log = logger.log

class PacketHandler(object):
    """ general class handling individual packets """

    def __init__(self):
        """ i do nothing """

        pass

    def _register_callback(self, packet_name):

        log(DEBUG, 'Creating a callback watcher for %s' % (packet_name))

        # create an attribute that is the event notifier (PacketReceivedNotifier)
        # TemplateDictionary.get_template_list() will provide all the proper names
        # for use here (aka packetnames)
        if not self.__dict__.has_key(packet_name + "_Received"):
            setattr(self, packet_name + "_Received", PacketReceivedNotifier(packet_name))

        # return the attribute (an instance of PacketReceivedNotifier)
        return getattr(self, packet_name + "_Received")

    def _handle(self, packet):
        """ essentially a case statement to pass packets to event notifiers in the form of self attributes """

        try:

            # get the attribute of the self object called packet.name + Received
            handler = getattr(self, packet.name + "_Received")

            # Handle the packet if we have subscribers
            # Conveniently, this will also enable verbose packet logging
            if len(handler) > 0:
                log(DEBUG, 'Handling packet: %s' % (packet.name))
                handler(packet)

        except AttributeError:
            #log(INFO, "Received an unhandled packet: %s" % (packet.name))
            pass

class PacketReceivedNotifier(object):
    """ received TestMessage packet """

    def __init__(self, packet_name):
        self.event = Event()
        self.packet_name = packet_name

    def received(self, packet):

        self.event(packet)

    def __len__(self):

        return len(self.event)

    __call__ = received

