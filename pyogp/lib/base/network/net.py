import socket

from zope.interface import implements

from pyogp.lib.base.network.interfaces import IUDPClient
from pyogp.lib.base.message.interfaces import IHost

#returns true if packet was sent successfully
class NetUDPClient(object):
    implements(IUDPClient)

    def __init__(self):
        self.sender = IHost((None, None))

    def get_sender(self):
        return self.sender
    
    def send_packet(self, sock, send_buffer, host):
        bytes = sock.sendto(send_buffer, (host.ip, host.port))
    
    def receive_packet(self, sock):
        buf = 10000
        try:
            data, addr = sock.recvfrom(buf)
            #print "Received data: " + repr(data)
        except:
            return '', 0
        print self.sender
        self.sender.ip = addr[0]
        self.sender.port = addr[1]
        return data, len(data)

    def start_udp_connection(self):
        """ Starts a udp connection, returning socket and port. """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10)
        #error check - make sure sock is good

        #will probably be other setup for this
        return sock
