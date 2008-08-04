import socket
from zope.interface import implements
from pyogp.lib.base.network.interfaces import IUDPClient

#returns true if packet was sent successfully
class NetUDPClient(object):
    implements(IUDPClient)
    
    def send_packet(self, sock, send_buffer, host):
        sock.sendto(send_buffer, (host.ip_addr, host.port))
    
    def receive_packet(self, socket):
        buf = 10000
        data, addr = socket.recvfrom(buf)
        return data, len(data)

    def start_udp_connection(self, port):
        """ Starts a udp connection, returning socket and port. """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #error check - make sure sock is good

        #will probably be other setup for this
        return sock
