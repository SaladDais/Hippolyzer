#!/usr/bin/python
"""
@file sample_object_create_edit.py
@date 2009-03-05
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

# pyogp utilites
from pyogp.lib.base.utilities.helpers import Wait

object_names = ['A','B','C','D','E','F']

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

    # let's disable inventory handling for this example
    settings = Settings()
    settings.ENABLE_INVENTORY_MANAGEMENT = False
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

    # do sample script specific stuff here
    # in this case we create a box

    waiter = Wait(5)

    for i in range(len(object_names)):
        client.region.objects.create_default_box(GroupID = client.ActiveGroupID, relative_position = ((i+1),0,0))

    waiter = Wait(5)

    # let's see what's nearby
    objects_nearby = client.region.objects.find_objects_within_radius(20)

    for item in objects_nearby:
        item.select(client)

    waiter = Wait(15)

    my_objects = client.region.objects.my_objects()

    print 'Hey! Will try to set object names'
    print 'Hey! Will try to set permissions.'

    i = 0
    for item in my_objects:
        fixed_name = object_names[i]
        print ' for LocalID %s : %s ' % (item.LocalID, fixed_name)
        item.set_object_name(client,fixed_name)
        if fixed_name == 'A':
            item.set_object_transfer_only_permissions(client)
        elif fixed_name == 'B':
            item.set_object_copy_transfer_permissions(client)
        elif fixed_name == 'C':
            item.set_object_mod_transfer_permissions(client)
        elif fixed_name == 'D':
            item.set_object_full_permissions(client)
        elif fixed_name == 'E':
            item.set_object_copy_only_permissions(client)
        elif fixed_name == 'F':
            item.set_object_copy_mod_permissions(client)
        else:
            print "Name Does Not Match!"
        i = i + 1

    waiter = Wait(30)

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
    print 'Objects being tracked: %s' % len(client.region.objects.object_store)
    print ''
    print ''
    states = {}
    for _object in client.region.objects.object_store:
        if _object.State == 0:
            #items = _object.__dict__.items()
            #items.sort()
            print 'Object attributes'
            for attr in _object.__dict__:
                print '\t\t%s:\t\t%s' % (attr, _object.__dict__[attr])
            print ''
        else:
            if states.has_key(_object.State):
                states[_object.State]+=1
            else:
                states[_object.State] = 1
    print ''
    print 'Object states I don\'t care about atm'
    for state in states:
        print '\t State: ', state, '\tFrequency: ', states[state]
    print ''
    print ''
    for _avatar in client.region.objects.avatar_store:
        print 'LocalID:', _avatar.LocalID, '\tUUID: ', _avatar.FullID , '\tNameValue: ', _avatar.NameValue, '\tPosition: ', _avatar.Position
    print ''
    print ''
    print 'Region attributes:'
    for attr in client.region.__dict__:
        print attr, ':\t\t\t',  client.region.__dict__[attr]

def main():
    return login()    

if __name__=="__main__":
    main()
