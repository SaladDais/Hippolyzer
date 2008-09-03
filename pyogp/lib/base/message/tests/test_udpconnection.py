#standard libraries
import unittest, doctest
import pprint

from zope.component import getUtility

from pyogp.lib.base.registration import init

#local libraries
#from pyogp.lib.base.message.udp_connection import MessageSystem
from pyogp.lib.base.message.types import MsgType
from pyogp.lib.base.network.mockup_net import MockupUDPServer
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.interfaces import IHost
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher

class TestUDPConnection(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        init()
        
        self.udp_connection = UDPDispatcher()
        self.host = IHost( (MockupUDPServer(), 80) )
        
    def test_find_circuit(self):
        host  = IHost((MockupUDPServer(), 80))
        host2 = IHost((MockupUDPServer(), 80))
        udp_connection = UDPDispatcher()
        assert len(udp_connection.circuit_manager.circuit_map) == 0, \
               "Circuit map has incorrect circuits"
        circuit1 = udp_connection.find_circuit(host)
        assert len(udp_connection.circuit_manager.circuit_map) == 1, \
               "Circuit map has incorrect circuits 2"
        circuit2 = udp_connection.find_circuit(host2)
        assert len(udp_connection.circuit_manager.circuit_map) == 2, \
               "Circuit map has incorrect circuits 3"
        circuit3 = udp_connection.find_circuit(host2)
        assert circuit2 == circuit3, "Didn't save circuit"
        assert len(udp_connection.circuit_manager.circuit_map) == 2, \
               "Circuit map has incorrect circuits 4"
        

    def test_send_variable(self):
        msg = Message('PacketAck',
                      Block('Packets', ID=0x00000003)
                      )
        buf = self.udp_connection.send_message(msg, self.host)
        assert buf == \
               '\x00' + '\x00\x00\x00\x01' + '\x00' + '\xff\xff\xff\xfb' + \
               '\x01' + '\x03\x00\x00\x00', \
               'Received: ' + repr(buf) + '  ' + \
               'Expected: ' + repr('\x00' + '\x00\x00\x00\x01' + '\x00' + \
                            '\xff\xff\xff\xfb' + '\x01' + '\x03\x00\x00\x00')

    def test_send_same_host(self):
        msg = Message('PacketAck',
                      Block('Packets', ID=0x00000003)
                      )
        ret1 = self.udp_connection.send_message(msg, self.host)

        msg2 = Message('PacketAck',
                      Block('Packets', ID=0x00000003)
                      )
        ret2 = self.udp_connection.send_message(msg2, self.host)
        
        #strings to test for
        test_str = '\x00' + '\x00\x00\x00\x01' + '\x00' + '\xff\xff\xff\xfb' + \
               '\x01' + '\x03\x00\x00\x00'
        test_str2 = '\x00' + '\x00\x00\x00\x02' + '\x00' + '\xff\xff\xff\xfb' + \
               '\x01' + '\x03\x00\x00\x00'

        assert ret1 == \
               test_str, \
               'Received: ' + repr(ret1) + '  ' + \
               'Expected: ' + repr(test_str)

        assert ret2 == \
               test_str2, \
               'Received: ' + repr(ret2) + '  ' + \
               'Expected: ' + repr(test_str2)
                
    def test_send_reliable(self):
        msg = Message('PacketAck',
                      Block('Packets', ID=0x00000003)
                      )
        host = IHost((MockupUDPServer(), 80))
        ret_msg = self.udp_connection.send_reliable(msg, host, 10)
        test_str = '\x40' + '\x00\x00\x00\x01' + '\x00' + '\xff\xff\xff\xfb' + \
               '\x01' + '\x03\x00\x00\x00'
        assert ret_msg == \
               test_str ,\
               'Received: ' + repr(msg) + '  ' + \
               'Expected: ' + repr(test_str)

    def test_receive(self):
        out_message = '\x00' + '\x00\x00\x00\x01' + '\x00' + \
            '\xff\xff\xff\xfb' + '\x01' + '\x01\x00\x00\x00'
        server = MockupUDPServer()
        server.send_message(self.udp_connection.udp_client, out_message)

        data, data_size = self.udp_connection.udp_client.receive_packet(0)
        packet = self.udp_connection.receive_check(self.udp_connection.udp_client.sender,
                                          data, data_size)
        assert packet.name == 'PacketAck'
        data = packet.message_data.blocks['Packets'][0].vars['ID'].data
        assert data == 1, "ID Data incorrect: " + str(data)
        
    def test_receive_zero(self):
        out_message = '\x80' + '\x00\x00\x00\x01' + '\x00' + \
            '\xff\xff\xff\xfb' + '\x01' + '\x01\x00\x03'
        server = MockupUDPServer()
        server.send_message(self.udp_connection.udp_client, out_message)

        data, data_size = self.udp_connection.udp_client.receive_packet(0)
        packet = self.udp_connection.receive_check(self.udp_connection.udp_client.sender,
                                          data, data_size)
        assert packet.name == 'PacketAck'
        data = packet.message_data.blocks['Packets'][0].vars['ID'].data
        assert data == 1, "ID Data incorrect: " + str(data)

    def test_receive_reliable(self):
        out_message = '\x40' + '\x00\x00\x00\x05' + '\x00' + \
            '\xff\xff\xff\xfb' + '\x01' + '\x01\x00\x00\x00'
        server = MockupUDPServer()
        server.send_message(self.udp_connection.udp_client, out_message)

        data, data_size = self.udp_connection.udp_client.receive_packet(0)
        packet = self.udp_connection.receive_check(self.udp_connection.udp_client.sender,
                                          data, data_size)
        sender_host = self.udp_connection.udp_client.get_sender()
        circuit = self.udp_connection.circuit_manager.get_circuit(sender_host)
        assert len(circuit.acks) == 1, "Ack not collected"
        assert circuit.acks[0] == 5, "Ack ID not correct, got " + str(circuit.acks[0])
        
    def test_acks(self):
        out_message = '\x40' + '\x00\x00\x00\x05' + '\x00' + \
            '\xff\xff\xff\xfb' + '\x01' + '\x00\x00\x00\x01'
        server = MockupUDPServer()
        server.send_message(self.udp_connection.udp_client, out_message)

        data, data_size = self.udp_connection.udp_client.receive_packet(0)
        packet = self.udp_connection.receive_check(self.udp_connection.udp_client.sender,
                                          data, data_size)
        assert server.rec_buffer == '', "ERROR: server has message without " + \
                    "receiving one"
        self.udp_connection.process_acks()
        assert server.rec_buffer != '', "Ack not sent"
        test_msg = '\x00' + '\x00\x00\x00\x01' + '\x00' + \
            '\xff\xff\xff\xfb' + '\x01' + '\x05\x00\x00\x00'
        assert server.rec_buffer == test_msg, "Ack received incorrect, got " + \
               repr(server.rec_buffer)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUDPConnection))
    return suite
