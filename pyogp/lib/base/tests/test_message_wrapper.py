#standard libraries
import unittest, doctest
from uuid import UUID

#local libraries
from pyogp.lib.base.data import msg_tmpl
from pyogp.lib.base.message.message_types import MsgType
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.interfaces import IDeserialization
from pyogp.lib.base.registration import init

class TestMessage(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        init()

    def test_block(self):
        print 'Test block'
        block = Block('CircuitCode', ID=1234,Code=531)
        
    def test_build(self):
        msg = Message('TestPacket',
                      Block('CircuitCode', ID=1234,Code=531)
                      )
                
        assert msg.blocks['CircuitCode'][0].vars['ID'].data == 1234, \
               "Incorrect data in block ID"
        assert msg.blocks['CircuitCode'][0].vars['Code'].data == 531, \
               "Incorrect data in block Code"

    def test_build_multiple(self):
        msg = Message('TestPacket',
                      Block('CircuitCode', ID=1234,Code=789),
                      Block('CircuitCode', ID=5678,Code=456),
                      Block('Test', ID=9101,Code=123)
                      )

        assert msg.blocks['CircuitCode'][0].vars['ID'].data == 1234, \
               "Incorrect data in block ID"
        assert msg.blocks['CircuitCode'][1].vars['ID'].data == 5678, \
               "Incorrect data in block 2 ID"
        
        assert msg.blocks['CircuitCode'][0].vars['Code'].data == 789, \
               "Incorrect data in block Code"
        assert msg.blocks['CircuitCode'][1].vars['Code'].data == 456, \
               "Incorrect data in block 2 Code"
        
        assert msg.blocks['Test'][0].vars['ID'].data == 9101, \
               "Incorrect data in block Test ID"
        assert msg.blocks['Test'][0].vars['Code'].data == 123, \
               "Incorrect data in block Test ID"
            
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMessage))
    return suite
