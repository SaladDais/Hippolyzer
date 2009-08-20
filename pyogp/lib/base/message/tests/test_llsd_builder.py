
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

#third party
from indra.base import llsd

#local libraries
from pyogp.lib.base.message.llsd_builder import LLSDMessageBuilder
from pyogp.lib.base.message.msgtypes import MsgType

class TestLLSDBuilder(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        pass

    def test_builder(self):
        builder = LLSDMessageBuilder()
        builder.new_message('TestMessage')

        builder.next_block('TestBlock1')
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)

        builder.next_block('TestBlock1')
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)

        builder.next_block('NeighborBlock')
        builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)

        builder.next_block('NeighborBlock')
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)

        builder.next_block('NeighborBlock')
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)

        builder.next_block('TestBlock2')
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)

        msg, size = builder.build_message()

        try:
            assert len(msg['NeighborBlock']) == 3, "Multiple blocks not" + \
                   " correct"
        except:
            assert False, "Message not set up properly"

        try:
            msg = llsd.format_xml(msg)
        except:
            assert False, "Message not built correctly so it can be formatted"

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLLSDBuilder))
    return suite



