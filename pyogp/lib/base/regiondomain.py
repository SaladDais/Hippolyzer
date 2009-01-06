"""
@file regiondomain.py
@date 2008-09-16
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

# std lib
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import re
from urllib import quote
from urlparse import urlparse, urljoin
import time
import uuid
import os
import threading

# eventlet
import sys
lib_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'src/lib'))
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

#from eventlet import api, coros

try:
    from eventlet import api, coros
except ImportError:
    print "Error importing eventlet"
    sys.exit()

# related
from indra.base import llsd

# pyogp
from pyogp.lib.base.caps import Capability
from network.stdlib_client import StdLibClient, HTTPError
import exc

# messaging
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.circuit import Host
from pyogp.lib.base.message.types import MsgType

# initialize logging
logger = getLogger('pyogp.lib.base.regiondomain')
log = logger.log

class Region(object):
    """models a region endpoint"""

    def __init__(self, uri=None, regionname=None):
        """initialize the region with the region uri"""
        
        if (uri != None): self.region_uri = self.parse_region_uri(uri)
        self.regionname = regionname
        self.seed_cap_url = ''
        self.seed_cap = None
        self.details = {}
        
        self.actor = None

        log(DEBUG, 'initializing region domain: %s' %self)

    def set_seed_cap_url(self, url):
    
        self.seed_cap_url = url
        self.seed_cap = RegionSeedCapability('seed_cap', self.seed_cap_url)
        
        log(DEBUG, 'setting region domain seed cap: %s' % (self.seed_cap_url))
    
    def parse_region_uri(self, uri):     
        """ parse a region uri and returns one formatted appropriately """
        
        region_uri = urljoin(uri, quote(urlparse(uri)[2]))

        # test if it is a lindenlab.com domain name
        '''
        if (re.search('lindenlab', urlparse(uri)[1])):
            if (re.search('lindenlab\.com/public_seed$', uri)):
                region_uri = uri
            else:
                region_uri = uri + '/public_seed'
        else:
            # this is a crappy test to see if it's already been urlencoded, it only checkes for spaces
            if re.search('%20', urlparse(uri)[2]):
                region_uri = uri
            else:
                region_uri = urljoin(uri, quote(urlparse(uri)[2]))
        '''
        
        return region_uri

    def get_region_public_seed(self,custom_headers={'Accept' : 'application/llsd+xml'}):
        """call this capability, return the parsed result"""
        
        log(DEBUG, 'Getting region public_seed %s' %(self.region_uri))

        try:
            restclient = StdLibClient()
            response = restclient.GET(self.region_uri, custom_headers)
        except HTTPError, e:
            if e.code==404:
                raise exc.ResourceNotFound(self.region_uri)
            else:
                raise exc.ResourceError(self.region_uri, e.code, e.msg, e.fp.read(), method="GET")

        data = llsd.parse(response.body)

        log(DEBUG, 'Get of cap %s response is: %s' % (self.region_uri, data))        
        
        return data

    def connect(self):
        """ connect to the udp circuit code """
        
        self.messenger = UDPDispatcher()
        self.host = None

        self.host = Host((self.details['sim_ip'],
                    self.details['sim_port']))

        msg = Message('UseCircuitCode',
                      Block('CircuitCode', Code=self.details['circuit_code'],
                            SessionID=uuid.UUID(self.details['session_id']),
                            ID=uuid.UUID(self.details['agent_id'])))
        self.messenger.send_reliable(msg, self.host, 0)

        time.sleep(1)

        #SENDS CompleteAgentMovement
        msg = Message('CompleteAgentMovement',
                      Block('AgentData', AgentID=uuid.UUID(self.details['agent_id']),
                            SessionID=uuid.UUID(self.details['session_id']),
                            CircuitCode=self.details['circuit_code']))
        self.messenger.send_reliable(msg, self.host, 0)

        #SENDS UUIDNameRequest
        msg = Message('UUIDNameRequest',
                      Block('UUIDNameBlock', ID=uuid.UUID(self.details['agent_id'])
                            )
                      )
        self.messenger.send_message(msg, self.host)

        msg = Message('AgentUpdate',
              Block('AgentData', AgentID=uuid.UUID(self.details['agent_id']),
                    SessionID=uuid.UUID(self.details['session_id']),
                    BodyRotation=(0.0,0.0,0.0,0.0),
                    HeadRotation=(0.0,0.0,0.0,0.0),
                    State=0x00,
                    CameraCenter=(0.0,0.0,0.0),
                    CameraAtAxis=(0.0,0.0,0.0),
                    CameraLeftAxis=(0.0,0.0,0.0),
                    CameraUpAxis=(0.0,0.0,0.0),
                    Far=0,
                    ControlFlags=0x00,
                    Flags=0x00))

        self.messenger.send_message(msg, self.host)

        self.last_ping = 0
        self.start = time.time()
        self.now = self.start
        self.packets = {}
        
        log(DEBUG, 'Spawning region UDP connection')
        api.spawn(self._processUDP)

        #ToDo: lots to do. work with the eventqueue via eventlet coros, object model clieanup, all that jazz

    def _processUDP(self):

        while True:
            
            # free up resources for other stuff to happen
            api.sleep(0)

            msg_buf, msg_size = self.messenger.udp_client.receive_packet(self.messenger.socket)
            packet = self.messenger.receive_check(self.messenger.udp_client.get_sender(),
                                            msg_buf, msg_size)
            if packet != None:
                #print 'Received: ' + packet.name + ' from  ' + self.messenger.udp_client.sender.ip + ":" + \
                                                  #str(self.messenger.udp_client.sender.port)

                #MESSAGE HANDLERS
                if packet.name == 'RegionHandshake':

                    msg = Message('RegionHandshakeReply',
                      [Block('AgentData', AgentID=uuid.UUID(self.details['agent_id']),
                            SessionID=uuid.UUID(self.details['session_id'])),
                       Block('RegionInfo', Flags=0x00)])

                    self.messenger.send_message(msg, self.host)

                elif packet.name == 'StartPingCheck':
                    msg = Message('CompletePingCheck',
                      Block('PingID', PingID=self.last_ping))

                    self.messenger.send_message(msg, self.host)
                    self.last_ping += 1
                
                # ToDo: REMOVE ME: self.packets will jsut grow and grow, this is here for testing purposes
                if packet.name not in self.packets:
                    self.packets[packet.name] = 1
                else: 
                    self.packets[packet.name] += 1                   
                
            else:
                #print 'No message'
                pass
                
            self.now = time.time()
                
            if self.messenger.has_unacked():
                #print 'Acking'
                self.messenger.process_acks()
                msg = Message('AgentUpdate',
                      Block('AgentData', AgentID=uuid.UUID(self.details['agent_id']),
                            SessionID=uuid.UUID(self.details['session_id']),
                            BodyRotation=(0.0,0.0,0.0,0.0),
                            HeadRotation=(0.0,0.0,0.0,0.0),
                            State=0x00,
                            CameraCenter=(0.0,0.0,0.0),
                            CameraAtAxis=(0.0,0.0,0.0),
                            CameraLeftAxis=(0.0,0.0,0.0),
                            CameraUpAxis=(0.0,0.0,0.0),
                            Far=0,
                            ControlFlags=0x00,
                            Flags=0x00))

                self.messenger.send_message(msg, self.host)

    def _processEventQueue(self):


class RegionSeedCapability(Capability):
    """ a seed capability which is able to retrieve other capabilities """

    def get(self, names=[]):
        """if this is a seed cap we can retrieve other caps here"""
        
        log(INFO, 'requesting from the region domain the following caps: %s' % (names))
        
        payload = names
        parsed_result = self.POST(payload)  #['caps']
        log(INFO, 'request for caps returned: %s' % (names))
        
        caps = {}
        for name in names:
            # TODO: some caps might be seed caps, how do we know? 
            caps[name]=Capability(name, parsed_result[name])
            #log(INFO, 'got cap: %s' % (name))
            
        return caps
                     
    def __repr__(self):
        return "<RegionSeedCapability for %s>" %self.public_url
    

class EventQueueGet(Region):
    """ an event queue capability 

    this is a temporary solution. ideally we'd have a generic event queue object
    that would be integrated into the ad and region separately
    """

    def __init__(self, context):
        """initialize this adapter"""
        
        self.context = context
        self.last_id = -1
        
        # let's retrieve the cap we need
        self.seed_cap = self.context.seed_cap
        
        log(DEBUG, 'intitializing region domain event queue via the seed cap: %s' % (self.seed_cap))
        
        self.cap = self.seed_cap.get(['EventQueueGet'])['EventQueueGet']
        
        if self.cap == {}:
            raise exc.RegionCapNotAvailable('EventQueueGet')
        else:
            log(DEBUG, 'region event queue cap is: %s' % (self.cap.public_url))

        
    def __call__(self, data = {}):
        """initiate the event queue get request"""
        
        if self.last_id != -1:
            data = {'ack':self.last_id, 'done':False}
            
        result = self.cap.POST(data)
        
        self.last_id = result['id']
        
        log(DEBUG, 'region event queue cap called, returned id: %s' % (self.last_id))
        
        return result
