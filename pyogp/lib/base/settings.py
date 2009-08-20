
"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""

class Settings(object):

    def __init__(self, quiet_logging = False):
        """ some lovely configurable settings 

        These are applied application wide, and can be
        overridden at any time in a specific instance
        """

        self.quiet_logging = quiet_logging

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Application behavior settings
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # default start location to use in login
        self.DEFAULT_START_LOCATION = 'last'

        # toggle handling udp packets
        self.HANDLE_PACKETS = True

        # Inventory related

        # enable inventory management
        self.ENABLE_INVENTORY_MANAGEMENT = True

        # enable accepting inventory offers
        self.ACCEPT_INVENTORY_OFFERS = False

        # enable library
        self.ENABLE_LIBRARY = True

        # enable object tracking
        self.ENABLE_OBJECT_TRACKING = True

        # enable communications monitoring
        self.ENABLE_COMMUNICATIONS_TRACKING = True

        # toggle parsing all/handled packets
        self.ENABLE_DEFERRED_PACKET_PARSING = True

        # toggle group chat handling
        self.ENABLE_GROUP_CHAT = True

        # enable the appearance manager
        self.ENABLE_APPEARANCE_MANAGEMENT = True
        
        # ~~~~~~
        # Camera
        # ~~~~~~

        # these defaults are for facing due east
        self.DEFAULT_CAMERA_DRAW_DISTANCE = 128
        self.DEFAULT_CAMERA_AT_AXIS = (1.0, 0.0, 0.0)
        self.DEFAULT_CAMERA_LEFT_AXIS = (0.0, 1.0, 0.0)
        self.DEFAULT_CAMERA_UP_AXIS = (0.0, 0.0, 1.0)

        #~~~~~~~~~~~~~~~~~~~~~~~
        # Extended Login Options
        #~~~~~~~~~~~~~~~~~~~~~~~

        # self.ENABLE_INVENTORY_MANAGEMENT is set above, and triggers the use of these options in the login params
        self.INVENTORY_LOGIN_OPTIONS = ["inventory-root", "inventory-skeleton", "inventory-skel-lib"]

        # self.ENABLE_LIBRARY is set above, and triggers the use of these options in the login params
        self.LIBRARY_LOGIN_OPTIONS = ["inventory-lib-root", "inventory-lib-owner"]

        self.ALEXANDRIA_LINDEN = 'ba2a564a-f0f1-4b82-9c61-b7520bfcd09f'

        # ToDo: handle this!
        self.ENABLE_EXTENDED_LOGIN_OPTIONS = False
        self.EXTENDED_LOGIN_OPTIONS = ["gestures", "event_categories", "event_notifications", "classified_categories", "buddy-list", "ui-config", "login-flags", "global-textures" ]

        #~~~~~~~~~~~~~~~~~~~
        # Simulator specific
        #~~~~~~~~~~~~~~~~~~~

        # toggle handling a region's event queue
        self.ENABLE_REGION_EVENT_QUEUE = True

        # shall we handle the eq data?
        self.HANDLE_EVENT_QUEUE_DATA = True

        # how many seconds to wait between polling
        # a region's event queue
        self.REGION_EVENT_QUEUE_POLL_INTERVAL = 1

        # allow connecting to multiple simulators
        self.MULTIPLE_SIM_CONNECTIONS = False

        # enabled the tracking of region parcels
        self.ENABLE_PARCEL_TRACKING = True

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
        self.ENABLE_CAPS_LOGGING = True
        self.ENABLE_CAPS_LLSD_LOGGING = False
        self.ENABLE_EQ_LOGGING = True
        self.ENABLE_UDP_LOGGING = True
        self.ENABLE_OBJECT_LOGGING = True
        self.LOG_SKIPPED_PACKETS = True
        self.ENABLE_HOST_LOGGING = True
        self.LOG_COROUTINE_SPAWNS = True

        # allow disabling logging of certain packets
        self.DISABLE_SPAMMERS = True
        self.UDP_SPAMMERS = ['PacketAck', 'AgentUpdate']

        # override the defaults
        if self.quiet_logging:
            self.LOG_VERBOSE = False
            self.ENABLE_BYTES_TO_HEX_LOGGING = False
            self.ENABLE_CAPS_LOGGING = False
            self.ENABLE_CAPS_LLSD_LOGGING = False
            self.ENABLE_EQ_LOGGING = False
            self.ENABLE_UDP_LOGGING = False
            self.LOG_SKIPPED_PACKETS = False
            self.ENABLE_OBJECT_LOGGING = False
            self.ENABLE_HOST_LOGGING = False
            self.LOG_COROUTINE_SPAWNS = False

        #~~~~~~~~~~~~~~~~~~~~~~
        # Test related settings
        #~~~~~~~~~~~~~~~~~~~~~~

        self.ENABLE_LOGGING_IN_TESTS = True

    # parameters for xmplrpc login
    def get_default_xmlrpc_login_parameters(self):
        """ returns some default login params """

        login_options = []

        if self.ENABLE_INVENTORY_MANAGEMENT:
            for option in self.INVENTORY_LOGIN_OPTIONS:
                login_options.append(option)

        if self.ENABLE_LIBRARY:
            for option in self.LIBRARY_LOGIN_OPTIONS:
                login_options.append(option)

        if self.ENABLE_EXTENDED_LOGIN_OPTIONS:
            for option in self.EXTENDED_LOGIN_OPTIONS:
                login_options.append(option)

        params = {   
            'major': '1',
            'minor': '22',
            'patch': '9',
            'build': '1',
            'platform': 'Win',
            'options': login_options,
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



