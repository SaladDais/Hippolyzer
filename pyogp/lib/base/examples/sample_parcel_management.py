# standard
import re
import getpass, sys, logging
from optparse import OptionParser

# related
from eventlet import api

# pyogp
from pyogp.lib.base.agent import Agent
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


    (options, args) = parser.parse_args()

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

    # prep instance settings
    settings = Settings()

    settings.ENABLE_INVENTORY_MANAGEMENT = False
    settings.ENABLE_COMMUNICATIONS_TRACKING = False
    settings.ENABLE_OBJECT_TRACKING = False
    settings.ENABLE_UDP_LOGGING =True
    settings.ENABLE_EQ_LOGGING = True
    settings.ENABLE_CAPS_LOGGING = True
    settings.MULTIPLE_SIM_CONNECTIONS = False
    settings.ENABLE_PARCEL_TRACKING = True

    #First, initialize the agent
    client = Agent(settings)

    # Now let's log it in
    api.spawn(client.login, options.loginuri, args[0], args[1], password, start_location = options.region, connect_region = True)

    # wait for the agent to connect to it's region
    while client.connected == False:
        api.sleep(0)

    while client.region.connected == False:
        api.sleep(0)

    # sample specific stuff
    # client.region.parcel_manager.request_current_parcel_properties()
    
    client.region.parcel_manager.request_all_parcel_properties()

    Wait(15)

    for parcel in client.region.parcel_manager.parcels:
        client.region.parcel_manager.request_parcel_dwell(parcel.LocalID)

    # run until killed
    while client.running:
        api.sleep(0)

    print ''
    print 'Parcel data for %s parcels' % (len(client.region.parcel_manager.parcels))
    for parcel in client.region.parcel_manager.parcels:
        print ''
        for attr in parcel.__dict__:
            print '  %s:            %s' % (attr, parcel.__dict__[attr])

    # inspect some data
    print ''
    print 'Parcel Overlay data:'
    print client.region.parcel_manager.parcel_overlay

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

