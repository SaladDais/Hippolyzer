from zope.interface import Interface, Attribute

class IUDPClient(Interface):
    """ a way to send and receive UDP messages """
    def start_udp_connection(port):
        """ creates a socket for the udp connection and returns it """
        
    def receive_packet(socket):
        """ checks the socket for any messages that are waiting """
        
    def send_packet(sock, send_buffer, host):
        """ sends a message on the socket to the host """
        
class IRESTClient(Interface):
    """a RESTful client"""
    
    def GET(url, headers={}):
        """send a GET request to the resource identified by url
        
        optionally you can pass headers in which get added to the header list
        (or overwritten if they are already defined)
        
        returns a webob.Response object
        
        """

    def POST(url, data, headers={}):
        """POST data to a resource identified by url.
        
        optionally you can pass headers in which get added to the header list
        (or overwritten if they are already defined)
        
        returns a webob.Response object
        """
        
    def PUT(url, data, headers={}):
        """PUT data to a resource identified by url.
        
        optionally you can pass headers in which get added to the header list
        (or overwritten if they are already defined)
        
        returns a webob.Response object
        """

    def DELETE(url, headers={}):
        """DELETE the resource identified by url.
        
        optionally you can pass headers in which get added to the header list
        (or overwritten if they are already defined)
        
        returns a webob.Response object
        """
        
    
