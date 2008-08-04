import socket
import random

from zope.interface import implements

from pyogp.lib.base.network.interfaces import IUDPClient
from pyogp.lib.base.message.circuitdata import Host

#returns true if packet was sent successfully
class MockupUDPClient(object):
    implements(IUDPClient)

    def __init__(self):
        self.rec = {}
        self.sender = None

    def get_sender(self):
        return Host(1, 1)
    
    def set_response(self, socket, response):
        self.rec[socket] = response

    def send_packet(self, sock, send_buffer, host):
        #print 'Sent: ' + repr(send_buffer)
        return True
    
    def receive_packet(self, socket):
        data = ''
        
        if socket in self.rec:
            data = self.rec[socket]
            del self.rec[socket]

        #print 'Receiving data: ' + repr(data)
        return data, len(data)

    def start_udp_connection(self, port):
        """ Starts a udp connection, returning socket and port. """
        sock = random.randint(0,80)
        return sock
