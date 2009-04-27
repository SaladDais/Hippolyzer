# standard python libs
import unittest

# pyogp
from pyogp.lib.base.event_system import EventsHandler
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

        eventshandler = EventsHandler()

        handler = eventshandler._register('MockEvent')
        handler.subscribe(self.onEvent, mock)

        eventshandler._handle(mock)

    def test_event_handler_timeout(self):

        mock = MockEvent(1)

        eventshandler = EventsHandler()

        handler = eventshandler._register('MockEvent', 2)
        handler.subscribe(self.onEvent, None)

        Wait(3)

    def test_event_handler_invalid_timeout_param(self):

        mock = MockEvent(1)

        eventshandler = EventsHandler()

        self.assertRaises(DataParsingError, eventshandler._register, 'MockEvent', 'two')

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

