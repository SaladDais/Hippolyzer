# standard
import re
import getpass, sys, logging
from optparse import OptionParser

# related
from eventlet import api

# pyogp
from pyogp.lib.base.agent import Agent
from pyogp.lib.base.settings import Settings


def login():
    """ login an to a login endpoint """ 

    parser = OptionParser(usage="usage: %prog [options] firstname lastname")

    logger = logging.getLogger("pyogp.lib.base.example")

    parser.add_option("-l", "--loginuri", dest="loginuri", default="https://login.aditi.lindenlab.com/cgi-bin/login.cgi",
                      help="specified the target loginuri")
    parser.add_option("-r", "--region", dest="region", default=None,
                      help="specifies the region (regionname/x/y/z) to connect to")
    parser.add_option("-u", "--uuid", dest="uuid", default = "00000000-0000-0000-0000-000000000000", help="uuid of the agent to send an instant message to")
    parser.add_option("-q", "--quiet", dest="verbose", default=True, action="store_false",
                    help="enable verbose mode")


    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("Expected arguments: firstname lastname")
        
    if options.verbose:
        console = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)-30s%(name)-30s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        print "Attention: This script will print nothing if you use -q. So it might be boring to use it like that ;-)"

    # example from a pure agent perspective

    #grab a password!
    password = getpass.getpass()

    # let's disable inventory handling for this example
    settings = Settings()
    settings.ENABLE_INVENTORY_MANAGEMENT = False
    settings.ENABLE_OBJECT_TRACKING = False

    #First, initialize the agent
    client = Agent(settings = settings)

    # Now let's log it in
    api.spawn(client.login, options.loginuri, args[0], args[1], password, start_location = options.region, connect_region = True)

    # wait for the agent to connect
    while client.connected == False:
        api.sleep(0)

    # let things settle down
    while client.Position == None:
        api.sleep(0)

    # do sample script specific stuff here
    
    # set up callbacks if they come in handy
    im_handler = client.events_handler._register('InstantMessageReceived')
    im_handler.subscribe(chat_handler)

    client.say("Hi, I'm a bot!")

    client.instant_message(options.uuid, "Look, I can even speak to you in IM-ese")
    client.instant_message(options.uuid, "I can even send 2 messages!")


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
    print 'Region attributes:'
    for attr in client.region.__dict__:
        print attr, ':\t\t\t',  client.region.__dict__[attr]

def main():
    return login()    

def chat_handler(message_info):

    print ''
    print 'OMG, I got an instant message!!!!!!!'
    print ''

    for key in message_info.__dict__:
        print key + ": " + str(message_info.__dict__[key])

    print ''

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

