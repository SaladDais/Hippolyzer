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

# eventlet
import sys
lib_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'src/lib'))
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

from pyogp.lib.base.utilities.events import Event

# initialize logging
logger = getLogger('pyogp.lib.base.event_queue')
log = logger.log

class EventQueueHandler(object):
    """ handles an event queue of either an agent domain or a simulator"""

    def __init__(self, capability, eq_type, settings = None):
        """ set up the event queue attributes """

        self.cap = capability
        #self.type = eq_type    # specify 'agentdomain' or 'region'

        self._running = False     # this class controls this value
        self.stop = False     # client can pause the event queue
        self.last_id = -1

        # if applicable, initialize data to post to the event queue
        self.data = {}

        # stores the result of the post to the event queue capability
        self.result = None

        self.handler = EventQueueNotifier()
        self.settings = settings

    def start(self):

        if self.settings == None:
            # grab default settings if we haven't passed any in
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        if self.cap.name == 'event_queue':
            self._processADEventQueue()
        elif self.cap.name == 'EventQueueGet':
            self._processRegionEventQueue()
        else:
            # ToDo handle this as an exception
            log(WARNING, 'Unable to start event queue polling due to %s' % (unknown queue type))

    def stop(self):
        self.stop = True

        # ToDo: turn this into a timeout
        for 1 in range(1,10):
            if not self._running: return

        # well, we failed to stop. let's log it and get outta here
        log(WARNING, "Failed to stop %s event queue." % (self.type))
        self.stop = False
        return

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

        self.last_id = -1
        
        if self.cap.name != 'EventQueueGet':
            raise exc.RegionCapNotAvailable('EventQueueGet')
            # well then get it...?
        else:

            self._running = True

            while not self.stop:

                # need to be able to pull data from a queue somewhere
                data = {}
                api.sleep(self.settings.region_event_queue_interval)

                if self.last_id != -1:
                    self.data = {'ack':self.last_id, 'done':True}

                # ToDo: this is blocking, we need to break this
                self.result = self.cap.POST(data)

                self._parse_result(result)

    def _processADEventQueue(self):

        if self.cap.name != 'event_queue':
            raise RegionCapNotAvailable('event_queue')
            # change the exception here (add a new one)
        else:
            self._running = True
            while not self.stop:

                api.sleep(self.settings.agentdomain_event_queue_interval)

                self.result = self.capabilities['event_queue'].POST(self.data)

                self._parse_result(result)

    def _parse_result(self, data):

        # if there are subscribers to the event queue and packet handling is enabled
        if self.settings.HANDLE_PACKETS and (len(self.handler) > 0):
            try:
                if result != None:
                    self.last_id = result['id']
                    parsed_data = self._decode_eq_result(data)
                    if self.settings.ENABLE_EQ_LOGGING: log(DEBUG, 'AgentDomain EventQueueGet result: %s' % (result))
                    if self.settings.HANDLE_PACKETS:
                        self.handler(parsed_data)
            except Exception:
                raise Exception

    def _decode_eq_result(self, data=None):
        """ parse the event queue response and return a list of packets """

        data = ###

class EventQueueNotifier(object):
    """ received TestMessage packet """

    def __init__(self):
        self.event = Event()

    def received(self, data):

        self.event(data)

    def __len__(self):

        return len(self.event)

    __call__ = received
