#standard libraries
import unittest, doctest
import pprint

from pyogp.lib.base.registration import init

#local libraries
from pyogp.lib.base.message.message_system import MessageSystem
from pyogp.lib.base.message.message_types import MsgType
from pyogp.lib.base.message.circuitdata import Host
from pyogp.lib.base.network.mockup_net import MockupUDPServer

class TestMessageSystem(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        init()
        self.message_system = MessageSystem(80)
        self.host = Host(MockupUDPServer(), 80)
        
    def test_init(self):
        assert self.message_system.message_dict.get_message_flavor('UseCircuitCode') \
                   == 'template', "Parsing message.xml failed"
        
    def test_find_circuit(self):
        host  = Host(MockupUDPServer(), 80)
        host2 = Host(MockupUDPServer(), 80)
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
               '\x01' + '\x03\x00\x00\x00', \
               'Received: ' + repr(self.message_system.send_buffer) + '  ' + \
               'Expected: ' + repr('\x00' + '\x00\x00\x00\x01' + '\x00' + \
                            '\xff\xff\xff\xfb' + '\x01' + '\x03\x00\x00\x00')

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
               '\x01' + '\x03\x00\x00\x00'

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
        host = Host(MockupUDPServer(), 80)
        self.message_system.send_reliable(host, 10)
        test_str = '\x40' + '\x00\x00\x00\x01' + '\x00' + '\xff\xff\xff\xfb' + \
               '\x01' + '\x03\x00\x00\x00'
        assert self.message_system.send_buffer == \
               test_str ,\
               'Received: ' + repr(self.message_system.send_buffer) + '  ' + \
               'Expected: ' + repr(test_str)

    def test_receive(self):
        out_message = '\x00' + '\x00\x00\x00\x01' + '\x00' + \
            '\xff\xff\xff\xfb' + '\x01' + '\x01\x00\x00\x00'
        server = MockupUDPServer()
        server.send_message(self.message_system.udp_client, out_message)
        
        self.message_system.receive_check()
        msg = self.message_system.get_received_message()
        assert msg.name == 'PacketAck'
        data = self.message_system.get_data('Packets', 'ID', MsgType.MVT_U32)
        assert data == 1, "ID Data incorrect: " + str(data)
        
    def test_receive_zero(self):
        out_message = '\x80' + '\x00\x00\x00\x01' + '\x00' + \
            '\xff\xff\xff\xfb' + '\x01' + '\x01\x00\x03'
        server = MockupUDPServer()
        server.send_message(self.message_system.udp_client, out_message)

        self.message_system.receive_check()
        msg = self.message_system.get_received_message()
        assert msg.name == 'PacketAck'
        data = self.message_system.get_data('Packets', 'ID', MsgType.MVT_U32)
        assert data == 1, "ID Data incorrect: " + str(data)

    def test_receive_reliable(self):
        out_message = '\x40' + '\x00\x00\x00\x05' + '\x00' + \
            '\xff\xff\xff\xfb' + '\x01' + '\x01\x00\x00\x00'
        server = MockupUDPServer()
        server.send_message(self.message_system.udp_client, out_message)

        self.message_system.receive_check()
        sender_host = self.message_system.udp_client.get_sender()
        circuit = self.message_system.circuit_manager.get_circuit(sender_host)
        assert len(circuit.acks) == 1, "Ack not collected"
        assert circuit.acks[0] == 5, "Ack ID not correct, got " + str(circuit.acks[0])
        
    def test_acks(self):
        out_message = '\x40' + '\x00\x00\x00\x05' + '\x00' + \
            '\xff\xff\xff\xfb' + '\x01' + '\x00\x00\x00\x01'
        server = MockupUDPServer()
        server.send_message(self.message_system.udp_client, out_message)

        self.message_system.receive_check()
        assert server.rec_buffer == '', "ERROR: server has message without " + \
                    "receiving one"
        self.message_system.process_acks()
        assert server.rec_buffer != '', "Ack not sent"
        test_msg = '\x00' + '\x00\x00\x00\x01' + '\x00' + \
            '\xff\xff\xff\xfb' + '\x01' + '\x05\x00\x00\x00'
        assert server.rec_buffer == test_msg, "Ack received incorrect, got " + \
               repr(server.rec_buffer)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMessageSystem))
    return suite
