
"""
message_manager.py
Implements the MessageManager class which faciliates the sending and receiving
of messages between a simulator through either the UDP or Capability message
paths.

Contributors: http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright (c) 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt
$/LicenseInfo$
"""
#stdlib
from logging import getLogger

# pyogp.lib.base
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.message_handler import MessageHandler
from pyogp.lib.base.message.message_dot_xml import MessageDotXML
from pyogp.lib.base.event_queue import EventQueueClient
from pyogp.lib.base.settings import Settings

# related
from eventlet import api

# initialize logging
logger = getLogger('pyogp.lib.base.message_manager')

class MessageManager(object):
    """ 
    This object serves as a consolidation point for all messaging related
    functionality in the base/message directory.
    """

    def __init__(self, host, message_handler=None, capabilities={},
                 settings=None, start_monitors=False, message_template = None, message_xml = None):
        """ 
        Initialize the MessageManager, applying custom settings and dedicated 
        message_handler if needed 
        """

        logger.debug("Initializing the Message Manager ")        

        self.host = host

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            self.settings = Settings()

        # allow the message_handler to be passed in
        # otherwise, grab the defaults
        if message_handler != None:
            self.message_handler = message_handler
        elif self.settings.HANDLE_PACKETS:
            self.message_handler = MessageHandler()

        # allow the passing in of message_template.msg as a file handle
        if not message_template:
            self.message_template = None
        else:
            if isinstance(message_template, file):
                self.message_template = message_template
            else:
                log.warning("%s parameter is expected to be a filehandle, it is a %s. \
                        Using the embedded message_template.msg" % (message_template, type(message_template)))

                from pyogp.lib.base.data import msg_tmpl
                self.message_template = msg_tmpl

        # allow the passing in of message.xml as a file handle
        # mapped to MessageDotXML()
        if not message_xml:
            self.message_xml = MessageDotXML()
        else:
            if isinstance(message_xml, file):
                self.message_xml = MessageDotXML(message_xml = message_xml.read())
            else:
                log.warning("%s parameter is expected to be a filehandle, it is a %s. \
                        Using the embedded message.xml" % (message_xml, type(message_xml)))
                self.message_xml = MessageDotXML()

        # initialize the manager's base attributes
        #self.builder = MessageBuilder()

        self._is_running = False

        #event queue-related attributes
        self.capabilities = capabilities
        if self.capabilities.has_key('EventQueueGet'):
            self.event_queue = EventQueueClient(self.capabilities['EventQueueGet'], 
                                                message_handler = self.message_handler, 
                                                host = self.host)
        else:
            self.event_queue = None

        #UDP-related attributes
        #NOTE udpdispatcher can already multiplex hosts 
        self.incoming_queue = []
        self.outgoing_queue = []

        self.udp_dispatcher = UDPDispatcher(settings = self.settings,
                                            message_handler = self.message_handler,
                                            message_template = self.message_template)

        # if start parameter = True, kick off the queue monitors
        if start_monitors:
            self.start_monitors()

    def start_monitors(self):
        """ spawn queue monitoring coroutines """

        self._is_running = True

        logger.debug('Spawning region UDP connection')

        api.spawn(self._udp_dispatcher)

        if self.event_queue != None:
            logger.debug('Spawning region event queue connection')
            api.spawn(self.event_queue.start)

        #api.spawn(self.monitor_outgoing_queue)
        #api.spawn(self.monitor_incoming_queue)

    def stop_monitors(self):
        """ stops monitoring coroutines """

        #stops udp_dispatcher

        self._is_running = False

        #stops event_queue

        if self.event_queue._running:
            self.event_queue.stop()        

    def monitor_outgoing_queue(self):
        """  """
        pass

    def enqueue_message(self, message, reliable = False,
                        now = False):
        """ enqueues a Message() in the outgoing_queue """

        # ToDo: should a reliable flag parameter be required here?
        if now:
            self.outgoing_queue.insert(0, (message, reliable))
        else:
            self.outgoing_queue.append((message, reliable))

    def send_message(self):
        """  """
        pass

    def new_message(self, name):
        pass

    def _udp_dispatcher(self):
        """
        Sends and receives UDP messages.
        """
        logger.debug('Spawning region UDP connection')
        while self._is_running:
            api.sleep(0)
            msg_buf, msg_size = self.udp_dispatcher.udp_client.receive_packet(self.udp_dispatcher.socket)
            recv_packet = self.udp_dispatcher.receive_check(self.udp_dispatcher.udp_client.get_sender(),
                                                            msg_buf, 
                                                            msg_size)
            #self.incoming_queue.append(recv_packet)
            if self.udp_dispatcher.has_unacked():
                self.udp_dispatcher.process_acks()

            while len(self.outgoing_queue) > 0:                
                (packet, reliable) = self.outgoing_queue.pop(0)
                self.send_udp_message(packet, reliable)

        logger.debug("Stopped the UDP connection for %s" % (self.host))

    def send_udp_message(self, packet, reliable=False):
        """
        Immediately sends an udp message to host
        """
        if reliable:
            return self.udp_dispatcher.send_reliable(packet, self.host, 0)
        else:
            return self.udp_dispatcher.send_message(packet, self.host)

