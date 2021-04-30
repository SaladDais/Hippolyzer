
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

# standard python libs
import unittest

# pyogp
from pyogp.lib.base.settings import Settings

# pyogp tests
import pyogp.lib.base.tests.config 

class TestEvents(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):

        pass

    def test_base_settings(self):

        settings = Settings()

        self.assertEquals(settings.quiet_logging, False)
        self.assertEquals(settings.HANDLE_PACKETS, True)
        self.assertEquals(settings.LOG_VERBOSE, True)
        self.assertEquals(settings.ENABLE_BYTES_TO_HEX_LOGGING, False)
        self.assertEquals(settings.ENABLE_CAPS_LOGGING, True)
        self.assertEquals(settings.ENABLE_CAPS_LLSD_LOGGING, False)
        self.assertEquals(settings.ENABLE_EQ_LOGGING, True)
        self.assertEquals(settings.ENABLE_UDP_LOGGING, True)
        self.assertEquals(settings.ENABLE_OBJECT_LOGGING, True)
        self.assertEquals(settings.LOG_SKIPPED_PACKETS, True)
        self.assertEquals(settings.ENABLE_HOST_LOGGING, True)
        self.assertEquals(settings.LOG_COROUTINE_SPAWNS, True)
        self.assertEquals(settings.DISABLE_SPAMMERS, True)
        self.assertEquals(settings.UDP_SPAMMERS, ['PacketAck', 'AgentUpdate'])

    def test_quiet_settings(self):

        settings = Settings(True)

        self.assertEquals(settings.quiet_logging, True)
        self.assertEquals(settings.HANDLE_PACKETS, True)
        self.assertEquals(settings.LOG_VERBOSE, False)
        self.assertEquals(settings.ENABLE_BYTES_TO_HEX_LOGGING, False)
        self.assertEquals(settings.ENABLE_CAPS_LOGGING, False)
        self.assertEquals(settings.ENABLE_CAPS_LLSD_LOGGING, False)
        self.assertEquals(settings.ENABLE_EQ_LOGGING, False)
        self.assertEquals(settings.ENABLE_UDP_LOGGING, False)
        self.assertEquals(settings.ENABLE_OBJECT_LOGGING, False)
        self.assertEquals(settings.LOG_SKIPPED_PACKETS, False)
        self.assertEquals(settings.ENABLE_HOST_LOGGING, False)
        self.assertEquals(settings.LOG_COROUTINE_SPAWNS, False)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEvents))
    return suite



