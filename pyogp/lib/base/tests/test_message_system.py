#standard libraries
import unittest, doctest
import pprint

#local libraries
from pyogp.lib.base.message.message_system import MessageSystem
from pyogp.lib.base.message.message_types import MsgType
from pyogp.lib.base.message.circuitdata import Host

class TestMessageSystem(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        self.message_system = MessageSystem(80)

    def test_init(self):
        assert self.message_system.message_dict.get_message_flavor('UseCircuitCode') \
                   == 'template', "Parsing message.xml failed"

    def test_send_message1(self):
        assert self.message_system.builder == None, "Has builder already"
        
        self.message_system.new_message('PacketAck')

        assert self.message_system.builder == \
               self.message_system.template_builder, "Builder incorrect"
        self.message_system.next_block('Packets')
        self.message_system.add_data('ID', 0x00000001, MsgType.MVT_U32)
        host = Host(0x101210120, 80)
        self.message_system.send_message(host)
        print repr(self.message_system.send_buffer)
        
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMessageSystem))
    return suite
