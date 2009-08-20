
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
from pyogp.lib.base.event_system import AppEventsHandler, AppEvent
from pyogp.lib.base.utilities.helpers import Wait
from pyogp.lib.base.exc import DataParsingError

# pyogp tests
import pyogp.lib.base.tests.config 

class TestEvents(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):

        pass

    def test_event_handler_no_timeout(self):

        mock = MockEvent(1)

        eventshandler = AppEventsHandler()

        handler = eventshandler.register('MockEvent')
        handler.subscribe(self.onEvent, mock)

        eventshandler.handle(mock)

    def test_event_handler_timeout(self):

        mock = MockEvent(1)

        eventshandler = AppEventsHandler()

        handler = eventshandler.register('MockEvent', 2)
        handler.subscribe(self.onEvent, None)

        Wait(3)

    def test_event_handler_invalid_timeout_param(self):

        mock = MockEvent(1)

        eventshandler = AppEventsHandler()

        self.assertRaises(DataParsingError, eventshandler.register, 'MockEvent', 'two')

    def test_AppEvent_payload(self):

        event_content = AppEvent('test', {1:'one', 2:'two'})

        self.assertEquals(event_content.name, 'test')
        self.assertEquals(event_content.payload, {1:'one', 2:'two'})

    def test_AppEvent_kwdargs(self):

        kwdargs = {'thingone':'one', 'thingtwo':'two'}

        event_content = AppEvent('test', thingone = 'one', thingtwo = 'two')

        self.assertEquals(event_content.name, 'test')

        for key in kwdargs:
            self.assertEquals(event_content.payload[key], kwdargs[key])

    def onEvent(self, event, expected):

        self.assertEquals(event, expected)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEvents))
    return suite

class MockEvent(object):
    """ mock event class for event system testing """

    def __init__(self, data):

        self.name = 'MockEvent'
        self.data = data



