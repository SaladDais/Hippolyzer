#standard libraries
import unittest, doctest
import pprint

#local libraries
from pyogp.lib.base.message.message_system import MessageSystem

class TestMessageSystem(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        self.message_system = MessageSystem(80)

    def test_init(self):
        assert self.message_system.message_dict.get_message_flavor('UseCircuitCode') \
                   == 'template', "Parsing message.xml failed"
             
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMessageSystem))
    return suite
