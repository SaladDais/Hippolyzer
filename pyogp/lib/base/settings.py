
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

        # toggle handling udp packets
        self.HANDLE_PACKETS = True

        #~~~~~~~~~~~~~~~~~~
        # Logging behaviors
        #~~~~~~~~~~~~~~~~~~
        # being a test tool, and an immature one at that,
        # enable fine granularity in the logging, but
        # make sure we can tone it down as well

        self.LOG_VERBOSE = True
        self.ENABLE_BYTES_TO_HEX_LOGGING = True
        self.ENABLE_CAPS_LOGGING = True
        self.ENABLE_CAPS_LLSD_LOGGING = True
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



