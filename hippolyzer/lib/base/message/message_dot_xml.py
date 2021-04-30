"""
Copyright 2009, Linden Research, Inc.
  See NOTICE.md for previous contributors
Copyright 2021, Salad Dais
All Rights Reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
from logging import getLogger

from llbase import llsd

from hippolyzer.lib.base.message.data import msg_details

logger = getLogger('...message.message_dot_xml')


class MessageDotXML:
    """ storage class for a python representation of the llsd message.xml """
    def __init__(self, message_xml=None):
        """ parse message.xml and store a representation of the map """
        self.raw_llsd = message_xml or msg_details
        self.parsed_llsd = llsd.parse(self.raw_llsd)

        self.serverDefaults = self.parsed_llsd['serverDefaults']
        self.messages = self.parsed_llsd['messages']
        self.capBans = self.parsed_llsd['capBans']
        self.maxQueuedEvents = self.parsed_llsd['maxQueuedEvents']
        self.messageBans = self.parsed_llsd['messageBans']

    def validate_udp_msg(self, msg_name):
        """ checks whether a message is allowed over UDP or not """

        if msg_name in self.messages:
            if self.messages[msg_name]['flavor'] == 'template':
                return True
            else:
                return False
        else:
            return True
