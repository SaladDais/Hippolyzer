
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
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

# related
from indra.base import llsd

# pyogp
from pyogp.lib.base.settings import Settings

# pyogp messaging
from pyogp.lib.base.message.data import msg_details

# initialize logging
logger = getLogger('...message.message_dot_xml')
log = logger.log

class MessageDotXML(object):
    """ storage class for a python representation of the llsd message.xml """

    def __init__(self, settings = None):
        """ parse message.xml and store a representation of the map """

        self.raw_llsd = msg_details
        self.parsed_llsd = llsd.parse(self.raw_llsd)

        self.serverDefaults = self.parsed_llsd['serverDefaults']
        self.messages = self.parsed_llsd['messages']
        self.capBans = self.parsed_llsd['capBans']
        self.maxQueuedEvents = self.parsed_llsd['maxQueuedEvents']
        self.messageBans = self.parsed_llsd['messageBans']



