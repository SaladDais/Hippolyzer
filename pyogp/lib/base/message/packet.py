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

    def get_var(self, block, variable):

        return self.message_data.blocks[block].vars[variable]

    def __repr__(self):
        """ a string representation of a packet """

        string = ''
        delim = '    '

        for k in self.__dict__:

            if k == 'name':
                string += '\nName: %s\n' % (self.name)
            if k == 'message_data':

                for ablock in self.message_data.blocks:
                    string += "%sBlock Name:%s%s\n" % (delim, delim, ablock)
                    for somevars in self.message_data.blocks[ablock]:

                        for avar in somevars.var_list:
                            zvar = somevars.get_variable(avar)
                            string += "%s%s%s:%s%s\n" % (delim, delim, zvar.name, delim, zvar)

        return string