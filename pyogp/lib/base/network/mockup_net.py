import socket
from zope.interface import implements
from pyogp.lib.base.network.interfaces import IUDPClient
import random

#returns true if packet was sent successfully
class MockupUDPClient(object):
    implements(IUDPClient)

    def __init__(self):
        self.rec = {}
    
    def set_response(self, socket, response):
        self.rec[socket] = response

    def send_packet(self, sock, send_buffer, host):
        #print 'Sent: ' + repr(send_buffer)
        return True
    
    def receive_packet(self, socket):
        data = self.rec[socket]
        return data, len(data)

    def start_udp_connection(self, port):
        """ Starts a udp connection, returning socket and port. """
        sock = random.randint(0,80)
        return sock
