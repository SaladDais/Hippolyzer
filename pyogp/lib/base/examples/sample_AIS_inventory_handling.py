# standard
import re
import getpass, sys, logging
from optparse import OptionParser
import time

# related
from eventlet import api

# pyogp
from pyogp.lib.base.agent import Agent
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.utilities.helpers import Wait


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
    parser.add_option("-s", "--search", dest="search", default=None,
                    help="inventory item to search for an rez (optional)")

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

    #grab a password!
    password = getpass.getpass()

    # let's disable object tracking for this example
    settings = Settings()
    settings.ENABLE_OBJECT_TRACKING = False

    #First, initialize the agent
    client = Agent(settings = settings)

    # Now let's log it in
    api.spawn(client.login, options.loginuri, args[0], args[1], password, start_location = options.region, connect_region = True)

    # wait for the agent to connect to it's region
    while client.connected == False:
        api.sleep(0)

    while client.region.connected == False:
        api.sleep(0)

    print ''
    print ''
    print'++++++++++++++++'
    print ''
    print ''

    # for folders whose parent = root folder aka My Inventory, request their contents
    [client.inventory._request_folder_contents(folder.FolderID) for folder in client.inventory.folders if str(folder.ParentID) == str(client.inventory.inventory_root.FolderID)]

    # for folders whose parent = library root folder aka Library, request their contents
    [client.inventory._request_folder_contents(folder.FolderID, 'library') for folder in client.inventory.library_folders if str(folder.ParentID) == str(client.inventory.library_root.FolderID)]

    Wait(10)

    [client.inventory.sendFetchInventoryRequest(item.ItemID) for item in client.inventory.search_inventory(name = options.search)]

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
    print 'Inventory: %s folders' % len(client.inventory.folders)
    for inv_folder in client.inventory.folders:
        print 'Inventory Folder', ':\t\t\t',  inv_folder.Name
        for item in inv_folder.inventory:
            print '    ', item.Name
    print ''
    print ''
    print 'Library: %s folders' % len(client.inventory.library_folders)
    for inv_folder in client.inventory.library_folders:
        print 'Inventory Folder', ':\t\t\t',  inv_folder.Name
        for item in inv_folder.inventory:
            print '    ', item.Name

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

