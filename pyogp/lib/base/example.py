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

from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region
from pyogp.lib.base import registration

from pyogp.lib.base.interfaces import IPlaceAvatar, IEventQueueGet

from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.interfaces import IHost
from pyogp.lib.base.message.types import MsgType

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
       
    registration.init()
    parser = OptionParser()
    
    logger = logging.getLogger("pyogp.lib.base.example")

    parser.add_option("-a", "--agentdomain", dest="loginuri", default="https://login1.aditi.lindenlab.com/cgi-bin/auth.cgi",
                      help="URI of Agent Domain")
    parser.add_option("-r", "--region", dest="regionuri", default="http://sim1.vaak.lindenlab.com:13000",
                      help="URI of Region to connect to")
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

    firstname = args[0]
    lastname = args[1]
    password = getpass.getpass()

    credentials = PlainPasswordCredential(firstname, lastname, password)

    agentdomain = AgentDomain(options.loginuri)
    agent = agentdomain.login(credentials)

    logger.info("logged in, we now have an agent: %s" %agent)

    place = IPlaceAvatar(agentdomain)
    region = Region(options.regionuri)

    
    logger.info("now we try to place the avatar on a region")
    avatar = place(region)
    logger.info("got region details: %s", avatar.region.details)
    
    # now get an event_queue_get cap
    eqg = IEventQueueGet(agentdomain)
    logger.info("received an event queue cap: %s", eqg.cap)
    
    # spawn the AD event queue thread
    eventQueueGet(eqg, logger).start()
    
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
