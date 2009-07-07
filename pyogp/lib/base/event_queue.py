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
from pyogp.lib.base.exc import Deprecated, RegionCapNotAvailable

# messaging
from pyogp.lib.base.message.message_handler import MessageHandler
from pyogp.lib.base.message.message import Message
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

    def __init__(self, capability = None, settings = None, message_handler = None, region = None):
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
        # otherwise, let's just use our own
        if message_handler != None:
            self.message_handler = message_handler
        else:
            self.message_handler = MessageHandler()

        self.region = region

        self.cap = capability
        #self.type = eq_type    # specify 'agentdomain' or 'region'
        self.type = 'typeNotSpecified'
        
        self._running = False     # this class controls this value
        self.stopped = False     # client can pause the event queue
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

                if self.settings.LOG_COROUTINE_SPAWNS: log(INFO, "Spawning a coroutine for event queue in the agent domain context.")

                self._processADEventQueue()

                return True

            elif self.cap.name == 'EventQueueGet':

                if self.settings.LOG_COROUTINE_SPAWNS: log(INFO, "Spawning a coroutine for event queue in the simulator context for %s." % (str(self.region.sim_ip) + ':' + str(self.region.sim_port)))

                self._processRegionEventQueue()

                return True

            else:

                # ToDo handle this as an exception

                log(WARNING, 'Unable to start event queue polling due to %s' % ('unknown queue type'))
                return False

        except Exception, error:

            log(ERROR, "Problem starting event queue for %s with cap of %s" % (str(self.region.sim_ip) + ':' + str(self.region.sim_port), str(self.cap)))

            return False

    def stop(self):

        log(INFO, "Stopping event queue.")

        self.stopped = True

        def stop_monitor(self, interval, times):
            for i in range(0,times):
                api.sleep(interval)
                if self._running == False:
                    log(INFO,
                        "Stopped event queue processing for %s",
                        self.region.SimName)
                    return
            log(WARNING,
                "Failed to stop event queue for %s after %s seconds",
                self.region.SimName,
                str(interval * times))
            
        api.spawn(stop_monitor, self, self.settings.REGION_EVENT_QUEUE_POLL_INTERVAL, 10)

    def _handle(self, data):
        """ essentially a case statement to pass packets to event notifiers in the form of self attributes """

        try:
            # Handle the event queue result if we have subscribers
            if len(self.subscribers) > 0:
                #log(DEBUG, 'Handling event queue results')
                handler(data)

        except AttributeError:
            #log(INFO, "Received an unhandled packet: %s" % (packet.name))
            pass

    def _processRegionEventQueue(self):

        if self.cap.name != 'EventQueueGet':
            raise RegionCapNotAvailable('EventQueueGet')
            # well then get it...?
        else:

            self._running = True

            while not self.stopped:

                try:
                    api.sleep(self.settings.REGION_EVENT_QUEUE_POLL_INTERVAL)

                    self.data = {}
                    if self.last_id != -1:
                        self.data = {'ack':self.last_id}

                    if self.settings.ENABLE_EQ_LOGGING: 
                        if self.settings.ENABLE_HOST_LOGGING:
                            host_string = ' to (%s)' % (str(self.region.sim_ip) + ':' + str(self.region.sim_port))
                        else:
                            host_string = ''
                        log(DEBUG, 'Posting to the event queue%s: %s' % (host_string, self.data))

                    try:
                        self.result = self.cap.POST(self.data)
                    except Exception, error:
                        if self.settings.ENABLE_HOST_LOGGING:
                            host_string = ' from (%s)' % (str(self.region.sim_ip) + ':' + str(self.region.sim_port))
                        else:
                            host_string = ''
                        log(INFO, "Received an error we ought not care about%s: %s" % (host_string, error))
                        pass

                    if self.result != None: 
                        self.last_id = self.result['id']
                    else:
                        self.last_id = -1

                    self._parse_result(self.result)

                except Exception, error:
                    log(WARNING, "Error in a post to the event queue. Error was: %s" % (error))
                #finally:
                    #log(CRITICAL, "Why am i here?")
                    
            if self.last_id != -1:
                # Need to ack the last message received, otherwise it will be
                # resent if we re-connect to the same queue
                self.data = {'ack':self.last_id, 'done':True}
                self.cap.POST(self.data)

            if self.last_id != -1:
                # Need to ack the last message received, otherwise it will be
                # resent if we re-connect to the same queue
                self.data = {'ack':self.last_id, 'done':True}
                self.cap.POST(self.data)

            self._running = False

            log(DEBUG, "Stopped event queue processing for %s" % (self.region.SimName))

    def _processADEventQueue(self):

        if self.cap.name != 'event_queue':
            raise RegionCapNotAvailable('event_queue')
            # change the exception here (add a new one)
        else:
            self._running = True
            while not self.stopped:

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

                    if self.settings.ENABLE_EQ_LOGGING:
                        if self.settings.ENABLE_HOST_LOGGING:
                            host_string = ' from (%s)' % (str(self.region.sim_ip) + ':' + str(self.region.sim_port))
                        else:
                            host_string = ''
                        log(DEBUG, 'Event Queue result%s: %s' % (host_string, data))

                    # if we are handling packets, handle the packet so any subscribers can get the data
                    if self.settings.HANDLE_PACKETS:

                        # this returns packets
                        parsed_data = self._decode_eq_result(data)

                        for packet in parsed_data:
                            self.message_handler._handle(packet)

            except Exception, error:
                traceback.print_exc()
                if self.settings.ENABLE_HOST_LOGGING:
                    host_string = ' from (%s)' % (str(self.region.sim_ip) + ':' + str(self.region.sim_port))
                else:
                    host_string = ''
                log(WARNING, "Error parsing even queue results%s. Error: %s. Data was: %s" % (host_string, error, data))

    def _decode_eq_result(self, data=None):
        """ parse the event queue data, return a list of packets

        the building of packets borrows absurdly much from UDPDeserializer.__decode_data()
        """

        # ToDo: this is returning packets, but perhaps we want to return packet class instances?
        if data != None:

            messages = []

            if data.has_key('events'):

                for i in data:

                    if i == 'id':

                        #last_id = data[i]
                        pass

                    else:

                        for message in data[i]:

                            # move this to a proper solution, for now, append to some list eq events
                            # or some dict mapping name to action to take
                            '''
                            if message['message'] == 'ChatterBoxInvitation':

                                message['name'] = message['message']
                                group_chat = ChatterBoxInvitation_Message(ChatterBoxInvitation_Data = message['body'])

                                self.message_handler._handle(group_chat)

                            elif message['message'] == 'ChatterBoxSessionEventReply':

                                message['name'] = message['message']

                                chat_response = ChatterBoxSessionEventReply_Message(message['body'])
                                self.message_handler._handle(chat_response)

                            elif message['message'] == 'ChatterBoxSessionAgentListUpdates':

                                message['name'] = message['message']

                                group_agent_update = ChatterBoxSessionAgentListUpdates_Message(message['body'])
                                self.message_handler._handle(group_agent_update)

                            elif message['message'] == 'ChatterBoxSessionStartReply':

                                message['name'] = message['message']

                                group_chat_session_data = ChatterBoxSessionStartReply_Message(message['body'])
                                self.message_handler._handle(group_chat_session_data)

                            elif message['message'] == 'EstablishAgentCommunication':

                                #message['name'] == message['message']
                                establish_agent_communication_data = EstablishAgentCommunication_Message(message['body'])
                                self.message_handler._handle(establish_agent_communication_data)
                            '''
                            in_template = self.template_dict.get_template(message['message'])
                            
                            if in_template:
                                # this is a message found in the message_template
                                
                                #self.current_template = self.template_dict.get_template(message['message'])
                                new_message = Message(message['message'])
                                new_message.event_queue_id = self.last_id
                                new_message.host = self.region.host

                                for block_name in message['body']:

                                    # block_data keys off of block.name, which here is the body attribute
                                    block_data = MsgBlockData(block_name)

                                    new_message.add_block(block_data)

                                    for items in message['body'][block_name]:                                       

                                        for variable in items:

                                            var_data = MsgVariableData(variable, items[variable], -1)
                                            block_data.add_variable(var_data)

                                #packet.blocks = message.blocks
                                messages.append(new_message)

                            else:

                                # this is e.g. EstablishAgentCommunication or ChatterBoxInvitation, etc

                                new_message = Message(message['message'])
                                new_message.event_queue_id = self.last_id
                                new_message.host = self.region.host

                                # faux block
                                block_data = MsgBlockData('Message_Data')
                                new_message.add_block(block_data)
                                
                                for var in message['body']:

                                    var_data = MsgVariableData(var, message['body'][var], -1)
                                    block_data.add_variable(var_data)
 
                                messages.append(new_message)                                   

            return messages
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

