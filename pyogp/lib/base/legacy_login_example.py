#!/usr/bin/python
"""
@file legacy_login_example.py
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

from credentials import PlainPasswordCredential
from legacy_login import LegacyLogin
from regiondomain import Region
from agent import Agent

from message.udpdispatcher import UDPDispatcher
from message.message import Message, Block
from message.circuit import Host
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
       
    parser = OptionParser()
    
    logger = logging.getLogger("pyogp.lib.base.example")

    parser.add_option("-l", "--loginuri", dest="loginuri", default="https://login.aditi.lindenlab.com/cgi-bin/login.cgi",
                      help="URI of Agent Domain")
    parser.add_option("-r", "--region", dest="region", default="Ahern",
                      help="Name of Region to connect to")
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
    #agent.credentials = PlainPasswordCredential(agent.firstname, agent.lastname, agent.password)

    # let's log in an agent to the agentdomain shall we
    agent.login(options.loginuri, regionname=options.region)

    print "got region details: %s" % agent.region.details
    
    # now get an event_queue_get cap
    #eqg = EventQueue(agent.agentdomain)
    #logger.info("received an event queue cap: %s", eqg.cap)
    
    # spawn the AD event queue thread
    #eventQueueGet(eqg, logger).start()
    
    # establish sim presence
    logger.debug("kinda need to establish sim presence here")

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
