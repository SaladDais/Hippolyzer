"""
@file settings.py
@date 2008-09-22
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

class Settings(object):

    def __init__(self):
        """ some lovely configurable settings 

        These are applied application wide, and can be
        overridden at any time in a specific instance
        """

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Application behavior settings
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # default start location to use in login
        self.DEFAULT_START_LOCATION = 'last'

        # toggle handling udp packets
        self.HANDLE_PACKETS = True

        #~~~~~~~~~~~~~~~~~~~
        # Simulator specific
        #~~~~~~~~~~~~~~~~~~~

        # toggle handling a region's event queue
        self.ENABLE_REGION_EVENT_QUEUE = True

        # how many seconds to wait between polling
        # a region's event queue
        self.REGION_EVENT_QUEUE_POLL_INTERVAL = 1

        # allow connecting to multiple simulators
        self.MULTIPLE_SIM_CONNECTIONS = True      

        #~~~~~~~~~~~~~~~~~~~~~~
        # Agent Domain specific
        #~~~~~~~~~~~~~~~~~~~~~~

        # toggle handling an agent domain's event queue
        self.ENABLE_AGENTDOMAIN_EVENT_QUEUE = True
        # how many seconds to wait between polling
        # a agent doamins's event queue
        self.AGENT_DOMAIN_EVENT_QUEUE_POLL_INTERVAL = 15

        #~~~~~~~~~~~~~~~~~~
        # Logging behaviors
        #~~~~~~~~~~~~~~~~~~
        # being a test tool, and an immature one at that,
        # enable fine granularity in the logging, but
        # make sure we can tone it down as well

        self.LOG_VERBOSE = True
        self.ENABLE_BYTES_TO_HEX_LOGGING = False
        self.ENABLE_CAPS_LOGGING = False
        self.ENABLE_CAPS_LLSD_LOGGING = False
        self.ENABLE_EQ_LOGGING = False
        self.ENABLE_UDP_LOGGING = True

        # allow disabling logging of certain packets
        self.DISABLE_SPAMMERS = False
        self.UDP_SPAMMERS = ['PacketAck', 'AgentUpdate']

        #~~~~~~~~~~~~~~~~~~~~~~
        # Test related settings
        #~~~~~~~~~~~~~~~~~~~~~~

        self.ENABLE_LOGGING_IN_TESTS = True

    # parameters for xmplrpc login
    def get_default_xmlrpc_login_parameters(self):
        """ returns some default login params """

        params = {   
            'major': '1',
            'minor': '22',
            'patch': '9',
            'build': '1',
            'platform': 'Win',
            'options': [],
            'user-agent': 'pyogp 0.1',
            'id0': '',
            'viewer_digest': '09d93740-8f37-c418-fbf2-2a78c7b0d1ea',
            'version': 'pyogp 0.1',
            'channel': 'pyogp',
            'mac': '',
            'agree_to_tos': True,
            'read_critical': True
        }

        return params
