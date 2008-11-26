"""
@file interfaces.py
@date 2008-09-16
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

# preserving contents as comments
pass

'''
from zope.interface import Interface, Attribute

class IUDPClient(Interface):
    """ a way to send and receive UDP messages """
    sender = Attribute("""sender host information""")

    def get_sender():
        """ returns the sender in the form of a Host. """
        
    def start_udp_connection():
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
        
    
'''
