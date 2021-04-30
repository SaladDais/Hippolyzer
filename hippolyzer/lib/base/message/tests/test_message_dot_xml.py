
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

#standard libraries
import unittest, doctest
from uuid import UUID

#local libraries
from pyogp.lib.base.message.message_dot_xml import MessageDotXML

class TestMessageDotXML(unittest.TestCase):

    def setUp(self):

        # use the embedded messae.xml in message/data/ for tests
        self.message_xml = MessageDotXML()

    def tearDown(self):
        pass

    def test_constructor(self):

        self.assert_(self.message_xml.serverDefaults)
        self.assert_(self.message_xml.messages)
        self.assert_(self.message_xml.capBans)
        self.assert_(self.message_xml.maxQueuedEvents)
        self.assert_(self.message_xml.messageBans)

    def test_validate_udp_msg_false(self):

        self.assertEquals(self.message_xml.validate_udp_msg('ParcelProperties'), False)

    def test_validate_udp_msg_true(self):

        self.assertEquals(self.message_xml.validate_udp_msg('OpenCircuit'), True)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMessageDotXML))
    return suite



