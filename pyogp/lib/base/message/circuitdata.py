from pyogp.lib.base.message.packet import Packet

class Host(object):
    def __init__(self, ip_addr, port):
        self.ip = ip_addr
        self.port = port

    def set_host_by_name(self, hostname):
        pass

class Circuit(object):
    """ This is used to keep track of a given circuit. It keeps statistics
        as well as circuit information. """
    """ Some statistics things we may need: bytes/packets in, bytes/packets out,
        unacked packet count/bytes, acked packet count/bytes"""
    
    def __init__(self, host, circuit_code, secure_session_id):
        self.host = host
        self.circuit_code = circuit_code
        self.secure_session_id = secure_session_id
        self.is_alive = True
        self.is_blocked = False
        self.allow_timeout = True
        self.last_packet_out_id  = 0  #id of the packet we last sent
        self.last_packet_in_id   = 0  #id of the packet we last received
        #packets waiting to be acked, can be resent
        self.unacked_packets     = {} #map of packet_id to packet
        self.unack_packet_count  = 0
        self.unack_packet_bytes  = 9
        #packets waiting to be acked, can't be resent
        self.final_retry_packets = {} #map of packet_id to packet
        self.final_packet_count  = 0
        
    def next_packet_id(self):
        self.last_packet_out_id += 1
        return self.last_packet_out_id

    def ack_reliable_packet(self, packet_id):
        #go through the packets waiting to be acked, and set them as acked
        pass

    def add_reliable_packet(self, sock, message_buffer, buffer_length, **kwds):
        packet = Packet(sock, message_buffer, buffer_length, kwds)
        self.unack_packet_count += 1
        self.unack_packet_bytes += buffer_length
        #if it can be resent/retried (not final) add it to the unack list
        if 'retries' in kwds:
            self.unacked_packets[packet.packet_id] = packet
        #otherwise, it can't be resent to get acked
        else:
            self.final_retry_packets[packet.packet_id] = packet

class CircuitManager(object):
    """ Manages a collection of circuits and provides some higher-level
        functionality to do so. """
    def __init__(self):
        self.circuit_map = {}

    def get_unacked_circuits(self):
        #go through circuits, if it has any unacked packets waiting ack, add
        #to a list
        pass

    
    def add_circuit(self, host, packet_in_id):
        circuit = Circuit(host, packet_in_id)
        
        self.circuit_map[host] = circuit
        
    def remove_circuit_data(self, host):
        pass

    def is_circuit_alive(self, host):
        if host not in self.circuit_map:
            return False

        circuit = self.circuit_map[host]
        return circuit.is_alive
