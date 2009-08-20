
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
from pyogp.lib.base.utilities.helpers import Helpers, ListLLSDSerializer, DictLLSDSerializer, LLSDDeserializer
from pyogp.lib.base.exc import DataParsingError

# pyogp tests
import pyogp.lib.base.tests.config 

class TestHelpers(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):

        pass

    def test_ListLLSDSerializer(self):

        input_data = ['ChatSessionRequest', 0]

        serializer = ListLLSDSerializer(input_data)

        self.assertEquals(input_data, serializer.context)
        self.assertEquals('<?xml version="1.0" ?><llsd><array><string>ChatSessionRequest</string><integer>0</integer></array></llsd>', serializer.serialize())

    def test_DictLLSDSerializer(self):

        input_data = {'foo':'bar', 'test':1234}

        serializer = ListLLSDSerializer(input_data)

        self.assertEquals(input_data, serializer.context)
        self.assertEquals('<?xml version="1.0" ?><llsd><map><key>test</key><integer>1234</integer><key>foo</key><string>bar</string></map></llsd>', serializer.serialize())

    def test_LLSDDeserializer_deserialize(self):

        string = '<?xml version="1.0" ?><llsd><map><key>test</key><integer>1234</integer><key>foo</key><string>bar</string></map></llsd>'

        deserializer = LLSDDeserializer()

        self.assertEquals({'test': 1234, 'foo': 'bar'}, deserializer.deserialize(string))

    def test_LLSDDeserializer_deserialize_string(self):

        string = '<?xml version="1.0" ?><llsd><map><key>test</key><integer>1234</integer><key>foo</key><string>bar</string></map></llsd>'

        deserializer = LLSDDeserializer()

        self.assertEquals({'test': 1234, 'foo': 'bar'}, deserializer.deserialize(string))

    def test_LLSDDeserializer_deserialize_nonsense(self):

        data = ['<?xml version="1.0" ?><llsd><map><key>test</key><integer>1234</integer><key>foo</key><string>bar</string></map></llsd>']

        deserializer = LLSDDeserializer()

        self.assertEquals(None, deserializer.deserialize(data))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestHelpers))
    return suite



