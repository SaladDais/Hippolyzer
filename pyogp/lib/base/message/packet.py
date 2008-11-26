"""
@file packet.py
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

from types import PackFlags

class UDPPacket(object):
    """a UDP packet"""

    def __init__(self, context):
        self.name = context.name
        self.send_flags         = PackFlags.LL_NONE
        self.packet_id          = 0 #aka, sequence number

        self.message_data       = context
        self.acks               = [] #may change
        self.num_acks           = 0

        self.trusted            = False
        self.reliable           = False
        self.resent             = False
        
        self.socket             = 0
        self.retries            = 1 #by default
        self.host               = None
        self.expiration_time    = 0

    def add_ack(self, packet_id):
        self.acks.append(packet_id)
        self.num_acks += 1
