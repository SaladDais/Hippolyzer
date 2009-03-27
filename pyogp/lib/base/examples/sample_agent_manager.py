#!/usr/bin/python
"""
@file sample_multi_agent_login.py
@date 2009-02-16
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


    (options, args) = parser.parse_args()

    if options.file == '':
        print '-f is a required parameter for logging in multiple agents'
        return

    try:
        f = open(options.file, 'r')
    except IOError, error:
        print 'File not found. Stopping. Error: %s' % (error)
        return

    clients = []

    for line in f:

        if len(line.strip().split(',')) != 3:
            print 'We expect a line with 3 comma separated parameters, we got %s' % (line.strip().split(','))
            print 'Stopping.'

        clients.append(line.strip().split(','))

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
    #password = getpass.getpass()
    clients = [['EnusBot1', 'LLQABot', '0MGbotsRC00l'], ['EnusBot2', 'LLQABot', '0MGbotsRC00l'], ['EnusBot3', 'LLQABot', '0MGbotsRC00l'], ['EnusBot4', 'LLQABot', '0MGbotsRC00l'], ['EnusBot5', 'LLQABot', '0MGbotsRC00l'], ['EnusBot6', 'LLQABot', '0MGbotsRC00l'], ['EnusBot7', 'LLQABot', '0MGbotsRC00l'], ['EnusBot8', 'LLQABot', '0MGbotsRC00l'], ['EnusBot9', 'LLQABot', '0MGbotsRC00l'], ['EnusBot10', 'LLQABot', '0MGbotsRC00l'], ['EnusBot11', 'LLQABot', '0MGbotsRC00l'], ['EnusBot12', 'LLQABot', '0MGbotsRC00l'], ['EnusBot13', 'LLQABot', '0MGbotsRC00l'], ['EnusBot14', 'LLQABot', '0MGbotsRC00l'], ['EnusBot15', 'LLQABot', '0MGbotsRC00l'], ['EnusBot16', 'LLQABot', '0MGbotsRC00l'], ['EnusBot17', 'LLQABot', '0MGbotsRC00l'], ['EnusBot18', 'LLQABot', '0MGbotsRC00l'], ['EnusBot19', 'LLQABot', '0MGbotsRC00l'], ['EnusBot20', 'LLQABot', '0MGbotsRC00l']]

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
