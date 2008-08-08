import socket
import random

from zope.interface import implements

from pyogp.lib.base.network.interfaces import IUDPClient
from pyogp.lib.base.message.circuitdata import Host

class MockupUDPServer(object):
    def __init__(self):
        self.rec_buffer = ''
        self.ip = 'MockupUDPServer'
        
    def receive_message(self, client, receive_buffer):
        #print 'SERVER receive'
        self.rec_buffer = receive_buffer

    def send_message(self, client, send_message):
        #print 'SERVER send'
        client.rec = send_message
        client.sender = self
        
#returns true if packet was sent successfully
class MockupUDPClient(object):
    implements(IUDPClient)

    def __init__(self):
        self.rec = ''
        self.sender = None

    def get_sender(self):
        return Host(self.sender, 1)
    
    def set_response(self, socket, response):
        self.rec[socket] = response

    def send_packet(self, sock, send_buffer, host):
        #host is a mockup server
        #print 'CLIENT send'
        host.ip.receive_message(self, send_buffer)
        return True
    
    def receive_packet(self, socket):
        #print 'CLIENT receive'
        data = self.rec
        self.rec = ''
        
        if len(data) > 0:
            return data, len(data)
        
        return '', 0

    def start_udp_connection(self, port):
        """ Starts a udp connection, returning socket and port. """
        sock = random.randint(0,80)
        return sock
