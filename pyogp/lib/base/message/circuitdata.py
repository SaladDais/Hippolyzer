from pyogp.lib.base.message.packet import Packet

class Host(object):
    def __init__(self, ip_addr, port):
        self.ip = ip_addr
        self.port = port

    def is_ok(self):
        if self.ip == None or self.port == None or \
           self.ip == 0 or self.port == 0:
            return False

        return True

    def set_host_by_name(self, hostname):
        pass

class Circuit(object):
    """ This is used to keep track of a given circuit. It keeps statistics
        as well as circuit information. """
    """ Some statistics things we may need: bytes/packets in, bytes/packets out,
        unacked packet count/bytes, acked packet count/bytes"""
    
    def __init__(self, host, pack_in_id):
        self.host = host
        self.circuit_code = 0
        self.session_id = 0
        self.is_alive = True
        self.is_trusted = False
        self.is_blocked = False
        self.allow_timeout = True
        self.last_packet_out_id  = 0  #id of the packet we last sent
        self.last_packet_in_id   = pack_in_id

        self.acks                = [] #packets we need to ack (ids)       
        self.unacked_packets     = {} #packets we want acked, can be resent
        self.unack_packet_count  = 0
        self.unack_packet_bytes  = 0
        self.final_retry_packets = {} #packets we want acked, can't be resent
        self.final_packet_count  = 0
        
    def next_packet_id(self):
        self.last_packet_out_id += 1
        return self.last_packet_out_id

    def ack_reliable_packet(self, packet_id):
        #go through the packets waiting to be acked, and set them as acked
        if packet_id in self.unacked_packets:
            del self.unacked_packets[packet_id]
            self.unack_packet_count -= 1
        
        if packet_id in self.final_retry_packets:
            del self.final_retry_packets[packet_id]
            self.final_packet_count -= 1

    def collect_ack(self, packet_id):
        """ set a packet_id that this circuit needs to eventually ack
            (need to send ack out)"""
        self.acks.append(packet_id)
        
    def add_reliable_packet(self, sock, message_buffer, buffer_length, params):
        """ add a packet that we want to be acked
            (want an incoming ack) """
        packet = Packet(sock, message_buffer, buffer_length, params)
        self.unack_packet_count += 1
        self.unack_packet_bytes += buffer_length
        #if it can be resent/retried (not final) add it to the unack list
        if 'retries' in params:
            packet.retries = params['retries']
            self.unacked_packets[packet.packet_id] = packet
        #otherwise, it can't be resent to get acked
        else:
            self.final_retry_packets[packet.packet_id] = packet

class CircuitManager(object):
    """ Manages a collection of circuits and provides some higher-level
        functionality to do so. """
    def __init__(self):
        self.circuit_map = {}
        self.unacked_circuits = {}
        
    def get_unacked_circuits(self):
        #go through circuits, if it has any unacked packets waiting ack, add
        #to a list
        pass

    def get_circuit(self, host):
        if (host.ip, host.port) in self.circuit_map:
            return self.circuit_map[(host.ip, host.port)]

        return None
    
    def add_circuit(self, host, packet_in_id):
        circuit = Circuit(host, packet_in_id)
        
        self.circuit_map[(host.ip, host.port)] = circuit
        return circuit
        
    def remove_circuit_data(self, host):
        if (host.ip, host.port) in self.circuit_map:
            del self.circuit_map[(host.ip, host.port)]

    def is_circuit_alive(self, host):
        if (host.ip, host.port) not in self.circuit_map:
            return False

        circuit = self.circuit_map[(host.ip, host.port)]
        return circuit.is_alive
