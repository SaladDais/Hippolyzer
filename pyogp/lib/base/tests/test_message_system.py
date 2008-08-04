#standard libraries
import unittest, doctest
import pprint

from pyogp.lib.base.registration import init

#local libraries
from pyogp.lib.base.message.message_system import MessageSystem
from pyogp.lib.base.message.message_types import MsgType
from pyogp.lib.base.message.circuitdata import Host

class TestMessageSystem(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        init()
        self.message_system = MessageSystem(80)
        self.host = Host(0x101210120, 80)
        
    def test_init(self):
        assert self.message_system.message_dict.get_message_flavor('UseCircuitCode') \
                   == 'template', "Parsing message.xml failed"
        
    def test_find_circuit(self):
        host  = Host(0x101010101, 80)
        host2 = Host(0x010101010, 80)
        message_system = MessageSystem(80)
        assert len(message_system.circuit_manager.circuit_map) == 0, \
               "Circuit map has incorrect circuits"
        circuit1 = message_system.find_circuit(host)
        assert len(message_system.circuit_manager.circuit_map) == 1, \
               "Circuit map has incorrect circuits 2"
        circuit2 = message_system.find_circuit(host2)
        assert len(message_system.circuit_manager.circuit_map) == 2, \
               "Circuit map has incorrect circuits 3"
        circuit3 = message_system.find_circuit(host2)
        assert circuit2 == circuit3, "Didn't save circuit"
        assert len(message_system.circuit_manager.circuit_map) == 2, \
               "Circuit map has incorrect circuits 4"
        

    def test_send_variable(self):
        self.message_system.new_message('PacketAck')

        assert self.message_system.builder == \
               self.message_system.template_builder, "Builder incorrect"
        self.message_system.next_block('Packets')
        self.message_system.add_data('ID', 0x00000003, MsgType.MVT_U32)
        self.message_system.send_message(self.host)
        assert self.message_system.send_buffer == \
               '\x00' + '\x00\x00\x00\x01' + '\x00' + '\xff\xff\xff\xfb' + \
               '\x01' + '\x00\x00\x00\x03', \
               'Received: ' + repr(self.message_system.send_buffer) + '  ' + \
               'Expected: ' + repr('\x00' + '\x00\x00\x00\x01' + '\x00' + \
                            '\xff\xff\xff\xfb' + '\x01' + '\x00\x00\x00\x03')

    def test_send_same_host(self):
        self.message_system.new_message('PacketAck')

        self.message_system.next_block('Packets')
        self.message_system.add_data('ID', 0x00000003, MsgType.MVT_U32)
        self.message_system.send_message(self.host)
        test_str = '\x00' + '\x00\x00\x00\x01' + '\x00' + '\xff\xff\xff\xfb' + \
               '\x01' + '\x00\x00\x00\x03'

        self.message_system.new_message('PacketAck')
        self.message_system.next_block('Packets')
        self.message_system.add_data('ID', 0x00000003, MsgType.MVT_U32)
        self.message_system.send_message(self.host)
        test_str = '\x00' + '\x00\x00\x00\x02' + '\x00' + '\xff\xff\xff\xfb' + \
               '\x01' + '\x00\x00\x00\x03'

        assert self.message_system.send_buffer == \
               test_str, \
               'Received: ' + repr(self.message_system.send_buffer) + '  ' + \
               'Expected: ' + repr(test_str)
                
    def test_send_reliable(self):
        assert self.message_system.builder == None, "Has builder already"
        
        self.message_system.new_message('PacketAck')

        assert self.message_system.builder == \
               self.message_system.template_builder, "Builder incorrect"
        self.message_system.next_block('Packets')
        self.message_system.add_data('ID', 0x00000003, MsgType.MVT_U32)
        host = Host(0x000000011, 80)
        self.message_system.send_reliable(host, 10)
        test_str = '\x40' + '\x00\x00\x00\x01' + '\x00' + '\xff\xff\xff\xfb' + \
               '\x01' + '\x00\x00\x00\x03'
        assert self.message_system.send_buffer == \
               test_str ,\
               'Received: ' + repr(self.message_system.send_buffer) + '  ' + \
               'Expected: ' + repr(test_str)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMessageSystem))
    return suite
