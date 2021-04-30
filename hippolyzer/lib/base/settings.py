"""
Copyright 2009, Linden Research, Inc.
  See NOTICE.md for previous contributors
Copyright 2021, Salad Dais
All Rights Reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""


class Settings:
    def __init__(self, quiet_logging=False, spammy_logging=False, log_tests=True):
        """ some lovely configurable settings 

        These are applied application wide, and can be
        overridden at any time in a specific instance
        
        quiet_logging overrides spammy_logging
        """

        self.quiet_logging = quiet_logging
        self.spammy_logging = spammy_logging

        # toggle handling udp packets
        self.HANDLE_PACKETS = True
        self.HANDLE_OUTGOING_PACKETS = False

        # toggle parsing all/handled packets
        self.ENABLE_DEFERRED_PACKET_PARSING = True

        # ~~~~~~~~~~~~~~~~~~
        # Logging behaviors
        # ~~~~~~~~~~~~~~~~~~
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
        self.PROXY_LOGGING = False

        # allow disabling logging of certain packets
        self.DISABLE_SPAMMERS = True
        self.UDP_SPAMMERS = ['PacketAck', 'AgentUpdate']

        # toggle handling a region's event queue
        self.ENABLE_REGION_EVENT_QUEUE = True

        # how many seconds to wait between polling
        # a region's event queue
        self.REGION_EVENT_QUEUE_POLL_INTERVAL = 1

        if self.spammy_logging:
            self.ENABLE_BYTES_TO_HEX_LOGGING = True
            self.ENABLE_CAPS_LLSD_LOGGING = True
            self.DISABLE_SPAMMERS = False

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
            self.DISABLE_SPAMMERS = True

        # ~~~~~~~~~~~~~~~~~~~~~~
        # Test related settings
        # ~~~~~~~~~~~~~~~~~~~~~~

        if log_tests:
            self.ENABLE_LOGGING_IN_TESTS = True
        else:
            self.ENABLE_LOGGING_IN_TESTS = False
