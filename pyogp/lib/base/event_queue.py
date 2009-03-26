"""
@file event_queue.py
@date 2009-02-09
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
import sys, traceback

# related
from eventlet import api, util
# the following makes socket calls nonblocking. magic
util.wrap_socket_with_coroutine_socket()

# pyogp
from pyogp.lib.base.utilities.events import Event
from pyogp.lib.base.groups import *

# messaging
from pyogp.lib.base.message.packet import UDPPacket
from pyogp.lib.base.message.template_dict import TemplateDictionary
from pyogp.lib.base.message.template import MsgData, MsgBlockData, MsgVariableData

# initialize logging
logger = getLogger('pyogp.lib.base.event_queue')
log = logger.log

class EventQueueClient(object):
    """ handles an event queue of either an agent domain or a simulator 

    Initialize the event queue client class
    >>> client = EventQueueClient()

    The event queue client requires an event queue capability
    >>> from pyogp.lib.base.caps import Capability
    >>> cap = Capability('EventQueue', http://localhost:12345/cap)

    >>> event_queue = EventQueueClient(cap)
    >>> event_queue.start()

    Sample implementations: region.py
    Tests: tests/test_event_queue.py
    """

    def __init__(self, capability = None, settings = None, packet_handler = None, region = None, event_queue_handler = None):
        """ set up the event queue attributes """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        # allow the packet_handler to be passed in
        # otherwise, grab the defaults
        if packet_handler != None:
            self.packet_handler = packet_handler
        elif self.settings.HANDLE_PACKETS:
            from pyogp.lib.base.message.packethandler import PacketHandler
            self.packet_handler = PacketHandler(settings = self.settings)

        # allow the event_queue_handler to be passed in
        # otherwise, grab the defaults
        if event_queue_handler != None:
            self.event_queue_handler = event_queue_handler
        elif self.settings.HANDLE_EVENT_QUEUE_DATA:
            self.event_queue_handler = EventQueueHandler(settings = self.settings)

        self.region = region

        self.cap = capability
        #self.type = eq_type    # specify 'agentdomain' or 'region'

        self._running = False     # this class controls this value
        self.stop = False     # client can pause the event queue
        self.last_id = -1

        # if applicable, initialize data to post to the event queue
        self.data = {}

        # stores the result of the post to the event queue capability
        self.result = None

        # enables proper packet parsing in event queue responses
        self.template_dict = TemplateDictionary()
        self.current_template = None

    def start(self):

        try:
            if self.cap.name == 'event_queue':
                api.spawn(self._processADEventQueue)
                return True
            elif self.cap.name == 'EventQueueGet':
                api.spawn(self._processRegionEventQueue)
                return True
            else:
                # ToDo handle this as an exception
                log(WARNING, 'Unable to start event queue polling due to %s' % ('unknown queue type'))
                return False
        except:
            return False

    def stop(self):

        log(INFO, "Stopping %s event queue." % (self.type))

        self.stop = True

        # ToDo: turn this into a timeout
        for i in range(1,10):
            if self._running == False: return True

        # well, we failed to stop. let's log it and get outta here
        log(WARNING, "Failed to stop %s event queue." % (self.type))
        self.stop = False
        return False

    def _handle(self, data):
        """ essentially a case statement to pass packets to event notifiers in the form of self attributes """

        try:
            # Handle the event queue result if we have subscribers
            if len(self.subscribers) > 0:
                log(DEBUG, 'Handling event queue results')
                handler(data)

        except AttributeError:
            #log(INFO, "Received an unhandled packet: %s" % (packet.name))
            pass

    def _processRegionEventQueue(self):

        if self.cap.name != 'EventQueueGet':
            raise exc.RegionCapNotAvailable('EventQueueGet')
            # well then get it...?
        else:

            self._running = True

            while self.stop != True:

                api.sleep(self.settings.REGION_EVENT_QUEUE_POLL_INTERVAL)

                if self.last_id != -1:
                    self.data = {'ack':self.last_id, 'done':False}

                if self.settings.ENABLE_EQ_LOGGING: log(DEBUG, 'Posting to the event queue: %s' % (self.data))

                try:
                    self.result = self.cap.POST(self.data)
                except Exception, error:
                    log(INFO, "Received an error we ought not care about: %s" % (error))
                    pass

                if self.result != None: 
                    self.last_id = self.result['id']
                else:
                    self.last_id = -1

                self._parse_result(self.result)

            self._running = False

            log(DEBUG, "Stopped event queue processing for %s" % (self.region.SimName))

    def _processADEventQueue(self):

        if self.cap.name != 'event_queue':
            raise RegionCapNotAvailable('event_queue')
            # change the exception here (add a new one)
        else:
            self._running = True
            while not self.stop:

                api.sleep(self.settings.agentdomain_event_queue_interval)

                self.result = self.capabilities['event_queue'].POST(self.data)

                if self.result != None: self.last_id = self.result['id']

                self._parse_result(self.result)

            self._running = False

    def _parse_result(self, data):

        # if there are subscribers to the event queue and packet handling is enabled
        if self.settings.HANDLE_PACKETS: # and (len(self.handler) > 0):

            try:

                if data != None:

                    if self.settings.ENABLE_EQ_LOGGING: log(DEBUG, 'Event Queue result: %s' % (data))

                    # if we are handling packets, handle the packet so any subscribers can get the data
                    if self.settings.HANDLE_PACKETS:

                        # this returns packets
                        parsed_data = self._decode_eq_result(data)

                        for packet in parsed_data:
                            self.event_queue_handler._handle(packet)

            except Exception, error:

                log(WARNING, "Error parsing even queue results. Error: %s. Data was: %s" % (error, data))

    def _decode_eq_result(self, data=None):
        """ parse the event queue data, return a list of packets

        the building of packets borrows absurdly much from UDPDeserializer.__decode_data()
        """

        # ToDo: this is returning packets, but perhaps we want to return packet class instances?
        if data != None:

            packets = []

            if data.has_key('events'):

                for i in data:

                    if i == 'id':

                        last_id = data[i]

                    else:

                        for message in data[i]:

                            # move this to a proper solution, for now, append to some list eq events
                            # or some dict mapping name to action to take
                            if message['message'] == 'ChatterBoxInvitation':

                                message['name'] = message['message']
                                group_chat = ChatterBoxInvitation_Message(ChatterBoxInvitation_Data = message['body'])

                                self.event_queue_handler._handle(group_chat)

                            elif message['message'] == 'ChatterBoxSessionEventReply':

                                message['name'] = message['message']

                                chat_response = ChatterBoxSessionEventReply_Message(message['body'])
                                self.event_queue_handler._handle(chat_response)

                            elif message['message'] == 'ChatterBoxSessionAgentListUpdates':

                                message['name'] = message['message']

                                group_agent_update = ChatterBoxSessionAgentListUpdates_Message(message['body'])
                                self.event_queue_handler._handle(group_agent_update)

                            elif message['message'] == 'ChatterBoxSessionStartReply':

                                message['name'] = message['message']

                                group_chat_session_data = ChatterBoxSessionStartReply_Message(message['body'])
                                self.event_queue_handler._handle(group_chat_session_data)

                            else:
                                # this is a UDP packet sent over the event queue 
                                
                                self.current_template = self.template_dict.get_template(message['message'])
                                message_data = MsgData(self.current_template.name)

                                # treat this like a UDPPacket
                                # in some cases, we will be creating UDPPacket instances
                                # where there is no corresponding entry in the message_template
                                # hence the try: except:
                                # there must be a better solution
                                packet = UDPPacket(message_data)
                                packet.name = self.current_template.name

                                # irrelevant packet attributes since it's from the EQ
                                '''
                                packet.send_flags
                                packet.packet_id
                                packet.add_ack
                                packet.reliable
                                '''

                                for block_name in message['body']:

                                    for items in message['body'][block_name]:

                                        # block_data keys off of block.name, which here is the body attribute
                                        block_data = MsgBlockData(block_name)

                                        message_data.add_block(block_data)                                        

                                        for variable in items:

                                            var_data = MsgVariableData(variable, items[variable], -1)
                                            block_data.add_variable(var_data)

                                packet.message_data = message_data
                                packets.append(packet)
            return packets


class EventQueueHandler(object):
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

    def _register(self, name):

        if self.settings.LOG_VERBOSE: log(DEBUG, 'Creating a monitor for %s' % (name))

        return self.handlers.setdefault(name, EventQueueReceivedNotifier(name, self.settings))

    def is_packet_handled(self, name):
        """ if the data is being monitored, return True, otherwise, return False 

        this can allow us to skip parsing inbound packets if no one is watching a particular one
        """

        try:

            handler = self.handlers[name]
            return True

        except KeyError:

            return False

    def _handle(self, data):
        """ essentially a case statement to pass packets to event notifiers in the form of self attributes """

        try:

            handler = self.handlers[data.name]

            # Handle the packet if we have subscribers
            # Conveniently, this will also enable verbose packet logging
            if len(handler) > 0:
                if self.settings.LOG_VERBOSE: log(DEBUG, 'Handling event queue data : %s' % (data.name))
                handler(data)

        except KeyError:
            #log(INFO, "Received an unhandled packet: %s" % (packet.name))
            pass

class EventQueueReceivedNotifier(object):
    """ received TestMessage packet """

    def __init__(self, name, settings):
        self.event = Event()
        self.name = name
        self.settings = settings

    def subscribe(self, *args, **kwdargs):
        self.event.subscribe(*args, **kwdargs)

    def received(self, data):

        self.event(data)

    def unsubscribe(self, *args, **kwdargs):
        self.event.unsubscribe(*args, **kwdargs)

        if self.settings.LOG_VERBOSE: log(DEBUG, "Removed the monitor for %s by %s" % (args, kwdargs))

    def __len__(self):

        return len(self.event)

    __call__ = received

