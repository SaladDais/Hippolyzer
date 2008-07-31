import socket

#maybe put this isnt' a class

#returns true if packet was sent successfully
def send_packet(socket, send_buffer, size, ip_addr, port):
    pass

#returns message and size, or None if error
def receive_packet(socket):
    pass

def start_udp_connection(port):
    """ Starts a udp connection, returning socket and port. """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #error check - make sure sock is good

    #will probably be other setup for this
    return sock


