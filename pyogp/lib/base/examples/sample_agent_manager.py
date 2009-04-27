# standard
import re
import sys
import getpass, sys, logging
from optparse import OptionParser

# related
from eventlet import api

# pyogp
from pyogp.lib.base.agentmanager import AgentManager
from pyogp.lib.base.agent import Agent
from pyogp.lib.base.settings import Settings


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
    parser.add_option("-f", "--file", dest="file", default='', help="csv formatted file containing first, last,pass for multi agent login")
    parser.add_option("-c", "--count", dest="count", default=0, help="number of agents to login")


    (options, args) = parser.parse_args()

    options.count = int(options.count)

    if options.file == '':
        print '-f is a required parameter for logging in multiple agents'
        return

    try:
        f = open(options.file, 'r')
        data = f.readlines()
        f.close()
    except IOError, error:
        print 'File not found. Stopping. Error: %s' % (error)
        return

    clients = []

    line_count = 0

    for line in data:
        line_count += 1

    if options.count > 0:
        if options.count > line_count:
            print "The count parameter requests more agents (%s) than you have in your data file (%s). Logging in max available."  % (options.count, line_count)

    counter = 0

    for line in data:

        counter += 1

        if len(line.strip().split(',')) != 3:
            print 'We expect a line with 3 comma separated parameters, we got %s' % (line.strip().split(','))
            print 'Stopping.'

        clients.append(line.strip().split(','))

        if counter >= options.count:
            break

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

    settings.ENABLE_INVENTORY_MANAGEMENT = False
    settings.ENABLE_COMMUNICATIONS_TRACKING = False
    settings.ENABLE_OBJECT_TRACKING = False
    settings.ENABLE_UDP_LOGGING =True
    settings.ENABLE_EQ_LOGGING = True
    settings.ENABLE_CAPS_LOGGING = True
    settings.MULTIPLE_SIM_CONNECTIONS = False

    agents = []

    # Now let's prime the accounts for login
    for params in clients:
        #First, initialize the agent
        agents.append(Agent(settings, params[0], params[1], params[2]))

    agentmanager = AgentManager()
    agentmanager.initialize(agents)

    #print 'Storing agents:'
    #for agent in agentmanager.agents:
        #print '\t' + agentmanager.agents[agent].Name()

    # log them in
    for key in agentmanager.agents:
        agentmanager.login(key, options.loginuri, options.region)

    while agentmanager.has_agents_running():
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

