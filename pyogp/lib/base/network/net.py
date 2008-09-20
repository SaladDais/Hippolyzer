"""
@file net.py
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
        #print "Sending to " + str(host.ip) + ":" + str(host.port)
        if send_buffer == None:
            raise Exception("No data specified")
        bytes = sock.sendto(send_buffer, (host.ip, host.port))
    
    def receive_packet(self, sock):
        buf = 10000
        try:
            data, addr = sock.recvfrom(buf)
            #print "Received data: " + repr(data)
        except:
            return '', 0
        #print self.sender
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
