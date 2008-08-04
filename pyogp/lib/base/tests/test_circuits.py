#standard libraries
import unittest, doctest
import pprint

#local libraries
from pyogp.lib.base.message.circuitdata import Host, CircuitManager, Circuit

class TestHost(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        pass

    def test(self):
        host = Host(0x00000001, 80)
        assert host.is_ok() == True, "Good host thinks it is bad"

    def test_fail(self):
        host = Host(None, 80)
        assert host.is_ok() == False, "Bad host thinks it is good"

class TestCircuit(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        self.host = Host(0x00000001, 80)

    def test(self):
        circuit = Circuit(self.host, 1)
        assert circuit.next_packet_id() == 1, "Wrong next id"
        assert circuit.next_packet_id() == 2, "Wrong next id 2"

    def test_add_reliable(self):
        circuit = Circuit(self.host, 1)
        assert circuit.unack_packet_count == 0, "Has incorrect unack count"
        assert len(circuit.unacked_packets) == 0, "Has incorrect unack"
        assert len(circuit.final_retry_packets) == 0, "Has incorrect final unacked"
        circuit.add_reliable_packet(90, 'we are only testing', 10, \
                                    {'retries':1, 'host':self.host})
        assert circuit.unack_packet_count == 1, "Has incorrect unack count"
        assert len(circuit.unacked_packets) == 1, "Has incorrect unack"
        assert len(circuit.final_retry_packets) == 0, "Has incorrect final unacked"

class TestCircuitManager(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        self.host = Host(0x00000001, 80)

    def test_(self):
        manager = CircuitManager()
        assert len(manager.circuit_map) == 0, "Circuit list incorrect"
        manager.add_circuit(self.host, 1)
        assert len(manager.circuit_map) == 1, "Circuit list incorrect 2"
        host = Host(0x00000011, 80)
        manager.add_circuit(host, 10)
        assert len(manager.circuit_map) == 2, "Circuit list incorrect 4"
        circuit = manager.get_circuit(self.host)
        assert circuit.last_packet_in_id == 1, "Got wrong circuit"
        circuit = manager.get_circuit(host)
        assert circuit.last_packet_in_id == 10, "Got wrong circuit 1"

        assert manager.is_circuit_alive(self.host) == True, \
               "Incorrect circuit alive state"
        assert manager.is_circuit_alive(host) == True, \
               "Incorrect circuit alive state 2"
                
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCircuit))
    suite.addTest(makeSuite(TestCircuitManager))
    suite.addTest(makeSuite(TestHost))
    return suite
