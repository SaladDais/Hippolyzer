# standard
import re
import getpass, sys, logging
from optparse import OptionParser
import uuid

# related
from eventlet import api

# pyogp
from pyogp.lib.base.agent import Agent
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.groups import MockChatInterface
from pyogp.lib.base.utilities.helpers import Helpers, Wait


def login():
    """ login an to a login endpoint """ 

    parser = OptionParser(usage="usage: %prog [options] firstname lastname")

    logger = logging.getLogger("pyogp.lib.base.example")

    parser.add_option("-l", "--loginuri", dest="loginuri", default="https://login.aditi.lindenlab.com/cgi-bin/login.cgi",
                      help="specified the target loginuri")
    parser.add_option("-r", "--region", dest="region", default=None,
                      help="specifies the region (regionname/x/y/z) to connect to")
    parser.add_option("-q", "--quiet", dest="verbose", default=True, action="store_false",
                    help="enable verbose mode")


    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("Expected arguments: firstname lastname")

    if options.verbose:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG) # seems to be a no op, set it for the logger
        formatter = logging.Formatter('%(asctime)-30s%(name)-30s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        # setting the level for the handler above seems to be a no-op
        # it needs to be set for the logger, here the root logger
        # otherwise it is NOTSET(=0) which means to log nothing.
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        print "Attention: This script will print nothing if you use -q. So it might be boring to use it like that ;-)"

    # example from a pure agent perspective
    print 'we are going to try and group chat with the agent\'s active group. set one active, or get the uuid and create a new script that does it for you!'
    print ''
    print 'This only works on unix like machines ATM.'

    #grab a password!
    password = getpass.getpass()

    # let's disable inventory handling for this example
    settings = Settings()
    settings.ENABLE_INVENTORY_MANAGEMENT = False
    settings.ENABLE_OBJECT_TRACKING = False
    settings.ENABLE_COMMUNICATIONS_TRACKING = True
    settings.ENABLE_UDP_LOGGING = False
    settings.ENABLE_EQ_LOGGING = False
    settings.ENABLE_CAPS_LOGGING = False

    #First, initialize the agent
    client = Agent(settings = settings)

    # Now let's log it in
    api.spawn(client.login, options.loginuri, args[0], args[1], password, start_location = options.region, connect_region = True)

    # wait for the agent to connect to it's region
    while client.connected == False:
        api.sleep(0)

    while client.region.connected == False:
        api.sleep(0)

    # wait 10 seconds, hoping group data populates by then
    Wait(10)

    # do sample script specific stuff here

    chat_group = client.group_manager.get_group(client.ActiveGroupID)

    # until the implementation is done, add the agent to the group object
    chat_group.agent = client

    print ''
    print 'I know, this interface is not an interface, you\'ll see, just type when prompted. Saijanai, sounds like you are up for a wx application. Hit Escape to trigger the message prompt.'

    if chat_group != None:
        chaty_kathy = MockChatInterface(client, chat_group.chat)    # this object is l-a-m-e
        chaty_kathy.start()
    else:
        print "We failed to find the group to start chat session :(. Continuing"

    while client.running:
        api.sleep(0)

    print ''
    print ''
    print 'At this point, we have an Agent object, Inventory dirs, and with a Region attribute'
    print 'Agent attributes:'
    for attr in client.__dict__:
        print attr, ':\t\t\t',  client.__dict__[attr]
    print ''
    print ''
    print 'Known Groups:'
    for group in client.group_manager.group_store:
        print ':\t\t\t',  group.GroupName
        for attr in group.__dict__:
            print '\t\t\t\t', attr, ':\t', group.__dict__[attr]

def main():
    return login()    

if __name__=="__main__":
    main()

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

