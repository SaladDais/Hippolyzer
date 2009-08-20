
"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""

# std python libs
import socket

from pyogp.lib.base.message.circuit import Host

#returns true if packet was sent successfully
class NetUDPClient(object):

    def __init__(self):
        self.sender = Host((None, None))

    def get_sender(self):
        return self.sender

    def send_packet(self, sock, send_buffer, host):
        #print "Sending to " + str(host.ip) + ":" + str(host.port) + ":" + send_buffer
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
        
        # 24-Mar-2009 settimeout is not needed since we wrap the socket for coroutines.
        # However, we may need to check eventlet/greenlet versions in the future and call this if needed.
        # sock.settimeout(10)
        #error check - make sure sock is good

        #will probably be other setup for this
        return sock

    def __repr__(self):
        
        return self.sender.__repr__

"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$

"""