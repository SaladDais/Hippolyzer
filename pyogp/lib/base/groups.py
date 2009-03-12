"""
@file groups.py
@date 2009-03-12
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

# standard python libs
import uuid

class Group(object):
    
    pass

class ChatterBoxInvitation_Message(object):
    """ a group chat message sent over the event queue """

    def __init__(self, session_name = None, from_name = None, session_id = None, _type = None, region_id = None, offline = None, timestamp = None, ttl = None, to_id = None, source = None, from_group = None, position = None, parent_estate_id = None, message = None, binary_bucket = None, _id = None, god_level = None, limited_to_estate = None, check_estate = None, agent_id = None, from_id = None, ChatterBoxInvitation_Data = None):

        if ChatterBoxInvitation_Data != None:

            self.session_name = ChatterBoxInvitation_Data['session_name']
            self.from_name = ChatterBoxInvitation_Data['from_name']
            self.session_id = uuid.UUID(str(ChatterBoxInvitation_Data['session_id']))
            #self.from_name = ChatterBoxInvitation_Data['session_name']
            self._type = ChatterBoxInvitation_Data['instantmessage']['message_params']['type']
            self.region_id = uuid.UUID(str(ChatterBoxInvitation_Data['instantmessage']['message_params']['region_id']))
            self.offline = ChatterBoxInvitation_Data['instantmessage']['message_params']['offline']
            self.timestamp = ChatterBoxInvitation_Data['instantmessage']['message_params']['timestamp']
            self.ttl = ChatterBoxInvitation_Data['instantmessage']['message_params']['ttl']
            self.to_id = uuid.UUID(str(ChatterBoxInvitation_Data['instantmessage']['message_params']['to_id']))
            self.source = ChatterBoxInvitation_Data['instantmessage']['message_params']['source']
            self.from_group = ChatterBoxInvitation_Data['instantmessage']['message_params']['from_group']
            self.position = ChatterBoxInvitation_Data['instantmessage']['message_params']['position']
            self.parent_estate_id = ChatterBoxInvitation_Data['instantmessage']['message_params']['parent_estate_id']
            self.message = ChatterBoxInvitation_Data['instantmessage']['message_params']['message']
            self.binary_bucket = ChatterBoxInvitation_Data['instantmessage']['message_params']['data']['binary_bucket']
            self._id = uuid.UUID(str(ChatterBoxInvitation_Data['instantmessage']['message_params']['id']))
            #self.from_id = ChatterBoxInvitation_Data['instantmessage']['message_params']['from_id']
            self.god_level = ChatterBoxInvitation_Data['instantmessage']['agent_params']['god_level']
            self.limited_to_estate = ChatterBoxInvitation_Data['instantmessage']['agent_params']['limited_to_estate']
            self.check_estate = ChatterBoxInvitation_Data['instantmessage']['agent_params']['check_estate']
            self.agent_id = uuid.UUID(str(ChatterBoxInvitation_Data['instantmessage']['agent_params']['agent_id']))
            self.from_id = uuid.UUID(str(ChatterBoxInvitation_Data['from_id']))
            #self.message = ChatterBoxInvitation_Data['message']

            self.name = 'ChatterBoxInvitation'

        else:

            self.session_name = session_name
            self.from_name = from_name
            self.session_id = session_id
            #self.from_name = from_name
            self._type = _type
            self.region_id = region_id
            self.offline = offline
            self.timestamp = timestamp
            self.ttl = ttl
            self.to_id = to_id
            self.source = source
            self.from_group = from_group
            self.position = position
            self.parent_estate_id = parent_estate_id
            self.message = message
            self.binary_bucket = binary_bucket
            self._id = _id
            #self.from_id = from_id
            self.god_level = god_level
            self.limited_to_estate = limited_to_estate
            self.check_estate = check_estate
            self.agent_id = agent_id
            self.from_id = from_id
            #self.message = message

            self.name = 'ChatterBoxInvitation'
