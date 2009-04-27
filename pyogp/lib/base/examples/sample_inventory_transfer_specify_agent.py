# standard
import re
import getpass, sys, logging
from optparse import OptionParser
import time

# related
from eventlet import api

# pyogp
from pyogp.lib.base.agent import Agent
from pyogp.lib.base.agentmanager import AgentManager
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.utilities.helpers import Wait


def login():
    """ login an to a login endpoint """ 

    parser = OptionParser()

    logger = logging.getLogger("pyogp.lib.base.example")

    parser.add_option("-l", "--loginuri", dest="loginuri", default="https://login.aditi.lindenlab.com/cgi-bin/login.cgi",
                      help="specified the target loginuri")
    parser.add_option("-r", "--region", dest="region", default=None,
                      help="specifies the region (regionname/x/y/z) to connect to")
    parser.add_option("-q", "--quiet", dest="verbose", default=True, action="store_false",
                    help="enable verbose mode")
    parser.add_option("-t", "--to_agent_id", dest="to_agent_id", default='', help="agent id to offer inventory to")
    parser.add_option("-s", "--search", dest="search", default=None, help = "name of inventory item to search for and transfer to account number 2")

    (options, args) = parser.parse_args()

    if options.to_agent_id == '':
        print "a target agent id is required. stopping"
        sys.exit()

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

    # prep instance settings
    settings = Settings()

    settings.ENABLE_INVENTORY_MANAGEMENT = True
    settings.ENABLE_COMMUNICATIONS_TRACKING = False
    settings.ENABLE_OBJECT_TRACKING = False
    settings.ENABLE_UDP_LOGGING =True
    settings.ENABLE_EQ_LOGGING = True
    settings.ENABLE_CAPS_LOGGING = True
    settings.MULTIPLE_SIM_CONNECTIONS = False

    #grab a password!
    password = getpass.getpass()

    #First, initialize the agent
    client = Agent(settings = settings)

    api.spawn(client.login, options.loginuri, args[0], args[1], password, start_location = options.region, connect_region = True)

    # wait for the agent to connect to it's region
    while client.connected == False:
        api.sleep(0)

    while client.region.connected == False:
        api.sleep(0)

############ WORKING HERE

    # for folders whose parent = root folder aka My Inventory, request their contents
    [client.inventory._request_folder_contents(folder.FolderID) for folder in client.inventory.folders if folder.ParentID == client.inventory.inventory_root.FolderID]

    #while client.running:
        #api.sleep(0)

    # next, let's wait 5 seconds and FetchInventory for items we know about
    Wait(10)

    if options.search != None:
        # and next, let's search the inventory by name
        matches = client.inventory.search_inventory(name = options.search)

        # now, if we have a match, let's try and rez the first matching object
        item_to_give = matches[0]

        print ''
        print ''
        print ''
        print ''
        print "Found item to give to another agent: %s" % (str(item_to_give.__dict__))
        print ''
        print ''
        print ''
        print ''

        client.inventory.give_inventory(item_to_give.ItemID, options.to_agent_id)

    while client.running:
        api.sleep(0)


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

