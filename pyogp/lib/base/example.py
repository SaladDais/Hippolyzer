#!/usr/bin/python
"""
@file example.py
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

import uuid
from threading import Thread
import signal
import time

from agentdomain import AgentDomain, EventQueue
from regiondomain import Region
from agent import Agent
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.circuit import Host
from pyogp.lib.base.message.types import MsgType


#from pyogp.lib.base.interfaces import IPlaceAvatar, IEventQueueGet
#from pyogp.lib.base.interfaces import IEventQueueGet

from message.udpdispatcher import UDPDispatcher
from message.message import Message, Block
#from message.circuit import Host
from message.types import MsgType

import getpass, sys, logging
from optparse import OptionParser

Running = None

def login():
    """login an agent and place it on a region""" 

    global Running
    RUNNING = True
        
    # would be nice to be able to kill threads with Ctrl-C now wouldnt it?
    # i have yet to see this actually kill a thread tho....

    #signal.signal(signal.SIGINT, sigint_handler) 
       
    #registration.init()
    parser = OptionParser()
    
    logger = logging.getLogger("pyogp.lib.base.example")

    parser.add_option("-l", "--loginuri", dest="loginuri", default="https://login1.aditi.lindenlab.com/cgi-bin/auth.cgi",
                      help="URI of Agent Domain")
    parser.add_option("-r", "--region", dest="regionuri", default="https://sim1.vaak.lindenlab.com:12043/cap/05917fe9-3347-72d2-cb30-b19c995af1c6",
                      help="URI of Region to connect to")
#http://ec2-75-101-203-98.compute-1.amazonaws.com:9000
    parser.add_option("-q", "--quiet", dest="verbose", default=True, action="store_false",
                    help="enable verbose mode")
                      

    (options, args) = parser.parse_args()
    
    if options.verbose:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG) # seems to be a no op, set it for the logger
        formatter = logging.Formatter('%(name)-30s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        # setting the level for the handler above seems to be a no-op
        # it needs to be set for the logger, here the root logger
        # otherwise it is NOTSET(=0) which means to log nothing.
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        print "Attention: This script will print nothing if you use -q. So it might be boring to use it like that ;-)"

    # example from a pure agent perspective

    #grab a password!
    password = getpass.getpass()

    # initialize the agent
    agent = Agent()

    # establish agent credentials
    agent.firstname = args[0]
    agent.lastname = args[1]
    agent.password = password

    # let's log in an agent to the agentdomain shall we
    agent.login(options.loginuri, options.regionuri)

    print "got agentdomain info: %s" % agent.agentdomain.__dict__
    print "got region details: %s" % agent.region.details
    
    # now get an event_queue_get cap
    eqg = EventQueue(agent.agentdomain)
    logger.info("received an event queue cap: %s", eqg.cap)
    
    # spawn the AD event queue thread
    eventQueueGet(eqg, logger).start()
    
    # establish sim presence
    logger.debug("kinda need to establish sim presence here, so let's try")

    # kinda hacking this together, REALLY should update it as it's bad but functional
    messenger = UDPDispatcher()
    agent_id = agent.region.details['agent_id']
    session_id = agent.region.details['session_id']

    #begin UDP communication
    host = Host((agent.region.details['sim_ip'],
                agent.region.details['sim_port']))

    #SENDS UseCircuitCode
    msg = Message('UseCircuitCode',
                  Block('CircuitCode', Code=agent.region.details['circuit_code'],
                        SessionID=uuid.UUID(session_id),
                        ID=uuid.UUID(agent_id)))
    messenger.send_reliable(msg, host, 0)

    time.sleep(1)

    #SENDS CompleteAgentMovement
    msg = Message('CompleteAgentMovement',
                  Block('AgentData', AgentID=uuid.UUID(agent_id),
                        SessionID=uuid.UUID(session_id),
                        CircuitCode=agent.region.details['circuit_code']))
    messenger.send_reliable(msg, host, 0)

    #SENDS UUIDNameRequest
    msg = Message('UUIDNameRequest',
                  Block('UUIDNameBlock', ID=uuid.UUID(agent_id)
                        )
                  )
    messenger.send_message(msg, host)

    send_agent_update(agent_id, session_id, messenger, host)

    #print "Entering loop"
    last_ping = 0
    start = time.time()
    now = start
    packets = {}
        
    # run for 45 seonds
    while ((now - start) < 45):
        msg_buf, msg_size = messenger.udp_client.receive_packet(messenger.socket)
        packet = messenger.receive_check(messenger.udp_client.get_sender(),
                                        msg_buf, msg_size)
        if packet != None:
            #print 'Received: ' + packet.name + ' from  ' + self.messenger.udp_client.sender.ip + ":" + \
                                              #str(self.messenger.udp_client.sender.port)

            #MESSAGE HANDLERS
            if packet.name == 'RegionHandshake':
                send_region_handshake_reply(agent_id, session_id, messenger, host)
            elif packet.name == 'StartPingCheck':
                send_complete_ping_check(last_ping, messenger, host)
                last_ping += 1
                   
            if packet.name not in packets:
                packets[packet.name] = 1
            else: 
                packets[packet.name] += 1                   
                
        else:
            #print 'No message'
            pass
                
        now = time.time()
                
        if messenger.has_unacked():
            #print 'Acking'
            messenger.process_acks()
            send_agent_update(agent_id, session_id, messenger, host)

class eventQueueGet(Thread):
    """ spawns a thread in which to run the eventqueueget """
    
    def __init__ (self, eqg, logger):
        
        self.eqg = eqg
        self.logger = logger
        Thread.__init__(self)
        
    def run(self):

        self.logger.debug("spawning agent domain event queue thread")
        
        for i in range(1,4):
            self.logger.debug("calling EQG cap")
            result = self.eqg()
            self.logger.debug("it returned: %s", result)   

def send_agent_update(agent_id, session_id, messenger, host):
    msg = Message('AgentUpdate',
                  Block('AgentData', AgentID=uuid.UUID(agent_id),
                        SessionID=uuid.UUID(session_id),
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

    messenger.send_message(msg, host)

def send_region_handshake_reply(agent_id, session_id, messenger, host):
    msg = Message('RegionHandshakeReply',
                  [Block('AgentData', AgentID=uuid.UUID(agent_id),
                        SessionID=uuid.UUID(session_id)),
                        Block('RegionInfo', Flags=0x00)])

    messenger.send_message(msg, host)
    
def send_complete_ping_check(ping, messenger, host):
    msg = Message('CompletePingCheck',
                  Block('PingID', PingID=ping))

    messenger.send_message(msg, host)

def sigint_handler(signal, frame):
    global RUNNING
    RUNNING = False
    print
    print "Caught signal... %d" % signal
    sys.exit(1)        

def main():
    return login()    

if __name__=="__main__":
    main()
