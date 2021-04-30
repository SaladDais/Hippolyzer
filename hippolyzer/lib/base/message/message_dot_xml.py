
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

# standard python libs
from logging import getLogger

# related
from llbase import llsd

# pyogp
from pyogp.lib.base.settings import Settings

# pyogp messaging
from pyogp.lib.base.message.data import msg_details

# initialize logging
logger = getLogger('...message.message_dot_xml')

class MessageDotXML(object):
    """ storage class for a python representation of the llsd message.xml """

    def __init__(self, message_xml = None):
        """ parse message.xml and store a representation of the map """

        if not message_xml:
            self.raw_llsd = msg_details
        else:
            self.raw_llsd = message_xml

        self.parsed_llsd = llsd.parse(self.raw_llsd)

        self.serverDefaults = self.parsed_llsd['serverDefaults']
        self.messages = self.parsed_llsd['messages']
        self.capBans = self.parsed_llsd['capBans']
        self.maxQueuedEvents = self.parsed_llsd['maxQueuedEvents']
        self.messageBans = self.parsed_llsd['messageBans']

    def validate_udp_msg(self, msg_name):
        """ checks whether a message is allowed over UDP or not """

        if self.messages.has_key(msg_name):
            if self.messages[msg_name]['flavor'] == 'template':
                return True
            else:
                return False
        else:
            return True