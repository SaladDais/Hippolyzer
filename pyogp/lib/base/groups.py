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
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
from datatypes import *
import re

# related
from eventlet import api

# for MockChatInterface
import sys
import select
import tty
import termios

# pyogp
from pyogp.lib.base.datatypes import *
from pyogp.lib.base.exc import DataParsingError
from pyogp.lib.base.utilities.helpers import Helpers, Wait

# pyogp messaging
from pyogp.lib.base.message.packets import *

# initialize logging
logger = getLogger('pyogp.lib.base.groups')
log = logger.log

class GroupManager(object):
    """ a storage bin for groups

    also, a functional area for group creation operations
    """

    def __init__(self, agent, settings = None):
        """ initialize the group manager """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        self.agent = agent

        # the group store consists of a list
        # of Group() instances
        self.group_store = []

        # ~~~~~~~~~
        # Callbacks
        # ~~~~~~~~~
        if self.settings.HANDLE_PACKETS:
            onAgentGroupDataUpdate_received = self.agent.region.event_queue_handler._register("AgentGroupDataUpdate")
            onAgentGroupDataUpdate_received.subscribe(onAgentGroupDataUpdate, self)

            onChatterBoxInvitation_received = self.agent.region.event_queue_handler._register('ChatterBoxInvitation')
            onChatterBoxInvitation_received.subscribe(onChatterBoxInvitation_Message, self)

            onChatterBoxSessionEventReply_received = self.agent.region.event_queue_handler._register('ChatterBoxSessionEventReply')
            onChatterBoxSessionEventReply_received.subscribe(onChatterBoxSessionEventReply, self)

            onChatterBoxSessionAgentListUpdates_received = self.agent.region.event_queue_handler._register('ChatterBoxSessionAgentListUpdates')
            onChatterBoxSessionAgentListUpdates_received.subscribe(onChatterBoxSessionAgentListUpdates, self)

            onChatterBoxSessionStartReply_received = self.agent.region.event_queue_handler._register('ChatterBoxSessionStartReply')
            onChatterBoxSessionStartReply_received.subscribe(onChatterBoxSessionStartReply, self)

        if self.settings.LOG_VERBOSE: log(DEBUG, "Initialized the Group Manager")

    def handle_group_chat(self, message):
        """ process a ChatterBoxInvitation_Message instance"""

        group = [group for group in self.group_store if str(message._id) == str(group.GroupID)]

        if group != []:
            group[0].handle_inbound_chat(message)
        else:
            log(WARNING, "Received group chat message from unknown group. Group: %s. Agent: %s. Message: %s" % (message.session_name, message.from_name, message.message))

    def store_group(self, _group):
        """ append to or replace a group in self.group_store """

        # replace an existing list member, else, append

        try:

            index = [self.group_store.index(_object_) for _group_ in self.group_store if _group_.ID == _group.GroupID]

            self.group_store[index[0]] = _group

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Replacing a stored group: \'%s\'' % (_group.GroupID))

        except:

            self.group_store.append(_group)

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Stored a new group: \'%s\'' % (_group.GroupID))

    def update_group(self, group_data):
        """ accepts a dictionary of group data and creates/updates a group """

        group = [group for group in self.group_store if str(group_data['GroupID']) == str(group.GroupID)]

        if group != []:
            group[0].update_properties(group_data)
            if self.settings.LOG_VERBOSE: log(DEBUG, 'Updating a stored group: \'%s\'' % (group[0].GroupID))
        else:
            group = Group(GroupID = group_data['GroupID'], GroupPowers = group_data['GroupPowers'], AcceptNotices = group_data['AcceptNotices'], GroupInsigniaID = group_data['GroupInsigniaID'], Contribution = group_data['Contribution'], GroupName = group_data['GroupName'])

            self.store_group(group)

    def update_group_by_name(self, group_data, name):
        """ accepts a dictionary of group data and creates/updates a group """

        pattern = re.compile(name)

        group = [group for group in self.group_store if pattern.match(group.GroupName)]

        if group != []:
            group[0].update_properties(group_data)
            if self.settings.LOG_VERBOSE: log(DEBUG, 'Updating a stored group: \'%s\'' % (group[0].GroupName))
        else:
            log(INFO, "Received an update for an unknown group for name: %s" % (name))

    def update_group_by_session_id(self, group_data):
        """ accepts a dictionary of group data and creates/updates a group """

        group = [group for group in self.group_store if str(group.session_id) == str(group_data['session_id'])]

        if group != []:
            group[0].update_properties(group_data)
            if self.settings.LOG_VERBOSE: log(DEBUG, 'Updating a stored group: \'%s\'' % (group[0].GroupName))
        else:
            log(INFO, "Received an update for an unknown group with a session id of: %s" % (str(group_data['session_id'])))

    def create_group(self, AgentID = None, SessionID = None, Name = None, Charter = '', ShowInList = True, InsigniaID = UUID(), MembershipFee = 0, OpenEnrollment = False, AllowPublish = False, MaturePublish = False):
        """ sends a message to the agent's current region requesting to create a group

        enables a callback (which should be unsubscribed from once we get a response)
        """

        if Name != None:

            log(INFO, "Sending a request to create group with a name of \'%s\'" % (Name))

            if AgentID == None: AgentID = self.agent.agent_id
            if SessionID == None: SessionID = self.agent.session_id

            packet = CreateGroupRequestPacket()

            # populate the AgentData block
            packet.AgentData['AgentID'] = UUID(string = str(AgentID))       # MVT_LLUUID
            packet.AgentData['SessionID'] = UUID(string = str(SessionID)) # MVT_LLUUID

            # populate the GroupData block
            packet.GroupData['Name'] = Name    # MVT_VARIABLE
            packet.GroupData['Charter'] = Charter    # MVT_VARIABLE
            packet.GroupData['ShowInList'] = ShowInList    # MVT_BOOL
            packet.GroupData['InsigniaID'] = UUID(str(string = InsigniaID))    # MVT_LLUUID
            packet.GroupData['MembershipFee'] = MembershipFee    # MVT_S32
            packet.GroupData['OpenEnrollment'] = OpenEnrollment    # MVT_BOOL
            packet.GroupData['AllowPublish'] = AllowPublish    # MVT_BOOL
            packet.GroupData['MaturePublish'] = MaturePublish    # MVT_BOOL

            self.agent.region.enqueue_message(packet(), True)

            if self.settings.HANDLE_PACKETS:
                # enable the callback to watch for the CreateGroupReply packet
                self.onCreateGroupReply_received = self.agent.region.packet_handler._register('CreateGroupReply')
                self.onCreateGroupReply_received.subscribe(onCreateGroupReply, self)
        else:

            raise DataParsingError('Failed to create a group, please specify a name')

    def get_group(self, GroupID = None):
        """ searches the store and returns group if stored, None otherwise """

        group = [group for group in self.group_store if str(group.GroupID) == str(GroupID)]

        if group == []:
            return None
        else:
            return group[0]

    def join_group(self, group_id):
        """ sends a JoinGroupRequest packet for the specified uuid """

        group_id = UUID(string = str(group_id))

        packet = JoinGroupRequestPacket()

        packet.AgentData['AgentID'] = UUID(string = str(self.agent.agent_id))       # MVT_LLUUID
        packet.AgentData['SessionID'] = UUID(string = str(self.agent.session_id)) # MVT_LLUUID

        packet.GroupData['GroupID'] = group_id

        # set up the callback
        self.onJoinGroupReply_received = self.agent.packet_handler._register('JoinGroupReply')
        self.onJoinGroupReply_received.subscribe(onJoinGroupReply, self)

        self.agent.region.enqueue_message(packet(), True)

    def activate_group(self, group_id):
        """ set a particular group as active """

        group_id = UUID(string = str(group_id))

        packet = ActivateGroupPacket()

        packet.AgentData['AgentID'] = UUID(string = str(self.agent.agent_id))       # MVT_LLUUID
        packet.AgentData['SessionID'] = UUID(string = str(self.agent.session_id)) # MVT_LLUUID
        packet.AgentData['GroupID'] = group_id

        self.agent.region.enqueue_message(packet())

class Group(object):
    """ representation of a group """

    def __init__(self, AcceptNotices = None, GroupPowers = None, GroupID = None, GroupName = None, ListInProfile = None, Contribution = None, GroupInsigniaID = None, agent = None):

        self.AcceptNotices = AcceptNotices
        self.GroupPowers = GroupPowers
        self.GroupID = UUID(string = str(GroupID))
        self.GroupName = GroupName
        self.ListInProfile = ListInProfile
        self.Contribution = Contribution
        self.GroupInsigniaID = UUID(string = str(GroupInsigniaID))

        self.agent = agent

        # store a history of ChatterBoxInvitation messages, and outgoing packets
        self.chat_history = []
        self.session_id = None

    def activate_group(self):
        """ set this group as active """

        packet = ActivateGroupPacket()

        packet.AgentData['AgentID'] = UUID(string = str(self.agent.agent_id))       # MVT_LLUUID
        packet.AgentData['SessionID'] = UUID(string = str(self.agent.session_id)) # MVT_LLUUID
        packet.AgentData['SessionID'] = self.GroupID

        self.agent.region.enqueue_message(packet())

    def update_properties(self, properties):
        """ takes a dictionary of attribute:value and makes it so """

        for attribute in properties:

            setattr(self, attribute, properties[attribute])

    def request_join_group_chat(self):
        """ sends an ImprovedInstantMessage packet with the atributes necessary to join a group chat """

        log(INFO, "Requesting to join group chat session for \'%s\'" % (self.GroupName))

        _AgentID = self.agent.agent_id
        _SessionID = self.agent.session_id
        _FromGroup = False
        _ToAgentID = self.GroupID
        _ParentEstateID = 0
        _RegionID = UUID()
        _Position = Vector3()
        _Offline = 0
        _Dialog = 15                 # Dialog type 1 = instant message
        _ID = self.GroupID
        _Timestamp = 0
        _FromAgentName = self.agent.Name()
        _Message = 'Message'''
        _BinaryBucket = ''

        self.agent.send_ImprovedInstantMessage(_AgentID, _SessionID, _FromGroup, _ToAgentID, _ParentEstateID, _RegionID, _Position, _Offline, _Dialog, _ID, _Timestamp, _FromAgentName, _Message, _BinaryBucket)

    def chat(self, Message = None):
        """ sends an instant message to another avatar

        wraps send_ImprovedInstantMessage with some handy defaults """

        if self.session_id == None:
            self.request_join_group_chat()

            Wait(5)

        if self.session_id == None:
            log(WARNING, "Failed to start chat session with group %s. Please try again later." % (self.GroupName))
            return

        if Message != None:

            _ID = self.GroupID
            _AgentID = self.agent.agent_id
            _SessionID = self.agent.session_id
            _FromGroup = False
            _ToAgentID = self.GroupID
            _ParentEstateID = 0
            _RegionID = UUID()
            _Position = Vector3()       # don't send position, send uuid zero
            _Offline = 0
            _Dialog = 17                 # Dialog type 1 = instant message
            _ID = self.GroupID
            _Timestamp = 0
            _FromAgentName = self.agent.Name() + "\x00" #struct.pack(">" + str(len(self.agent.Name)) + "c", *(self.agent.Name()))
            _Message = Message + "\x00" #struct.pack(">" + str(len(Message)) + "c", *(Message))
            _BinaryBucket = "\x00" # self.GroupName #struct.pack(">" + str(len(self.GroupName)) + "c", *(self.GroupName))

            self.agent.send_ImprovedInstantMessage(_AgentID, _SessionID, _FromGroup, _ToAgentID, _ParentEstateID, _RegionID, _Position, _Offline, _Dialog, _ID, _Timestamp, _FromAgentName, _Message, _BinaryBucket)

    def handle_inbound_chat(self, message):

        session_id = message._id

        self.chat_history.append(message)

        log(INFO, "Group chat received.\n    Group: %s\n    From: %s\n    Message: %s" % (message.session_name, message.from_name, message.message))

class MockChatInterface(object):
    """ a super simple chat interface for testing"""

    def __init__(self, agent, chat_handler):

        self.agent = agent
        self.chat_handler = chat_handler
        self.old_settings = termios.tcgetattr(sys.stdin)

        self.message = ''

    def data_watcher(self):

        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def start(self):

        self.message = ''

        try:
            tty.setcbreak(sys.stdin.fileno())

            while self.agent.running:

                if self.data_watcher():
                    c = sys.stdin.read(1)
                    #print c
                    if c == '\x1b':
                        self.message = self.get_and_send_input()
                    #if c == '\x1b':         # x1b is ESC
                        #self.chat_handler(c)
                        #break
                    #else:
                        #self.message += c
                api.sleep()
        except:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        #finally:
        #    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

        if self.agent.running:
            self.start()

    def get_and_send_input(self):

        print "This is blocking in this implementation. Go fast, else get disconnected..."

        self.message = raw_input("Enter Message to group")
        self.chat_handler(self.message)


class ChatterBoxInvitation_Message(object):
    """ a group chat message sent over the event queue """

    def __init__(self, session_name = None, from_name = None, session_id = None, _type = None, region_id = None, offline = None, timestamp = None, ttl = None, to_id = None, source = None, from_group = None, position = None, parent_estate_id = None, message = None, binary_bucket = None, _id = None, god_level = None, limited_to_estate = None, check_estate = None, agent_id = None, from_id = None, ChatterBoxInvitation_Data = None):

        if ChatterBoxInvitation_Data != None:

            self.session_name = ChatterBoxInvitation_Data['session_name']
            self.from_name = ChatterBoxInvitation_Data['from_name']
            self.session_id = UUID(string = str(ChatterBoxInvitation_Data['session_id']))
            #self.from_name = ChatterBoxInvitation_Data['session_name']
            self._type = ChatterBoxInvitation_Data['instantmessage']['message_params']['type']
            self.region_id = UUID(string = str(ChatterBoxInvitation_Data['instantmessage']['message_params']['region_id']))
            self.offline = ChatterBoxInvitation_Data['instantmessage']['message_params']['offline']
            self.timestamp = ChatterBoxInvitation_Data['instantmessage']['message_params']['timestamp']
            self.ttl = ChatterBoxInvitation_Data['instantmessage']['message_params']['ttl']
            self.to_id = UUID(string = str(ChatterBoxInvitation_Data['instantmessage']['message_params']['to_id']))
            self.source = ChatterBoxInvitation_Data['instantmessage']['message_params']['source']
            self.from_group = ChatterBoxInvitation_Data['instantmessage']['message_params']['from_group']
            self.position = ChatterBoxInvitation_Data['instantmessage']['message_params']['position']
            self.parent_estate_id = ChatterBoxInvitation_Data['instantmessage']['message_params']['parent_estate_id']
            self.message = ChatterBoxInvitation_Data['instantmessage']['message_params']['message']
            self.binary_bucket = ChatterBoxInvitation_Data['instantmessage']['message_params']['data']['binary_bucket']
            self._id = UUID(string = str(ChatterBoxInvitation_Data['instantmessage']['message_params']['id']))
            #self.from_id = ChatterBoxInvitation_Data['instantmessage']['message_params']['from_id']
            self.god_level = ChatterBoxInvitation_Data['instantmessage']['agent_params']['god_level']
            self.limited_to_estate = ChatterBoxInvitation_Data['instantmessage']['agent_params']['limited_to_estate']
            self.check_estate = ChatterBoxInvitation_Data['instantmessage']['agent_params']['check_estate']
            self.agent_id = UUID(string = str(ChatterBoxInvitation_Data['instantmessage']['agent_params']['agent_id']))
            self.from_id = UUID(string = str(ChatterBoxInvitation_Data['from_id']))
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

class ChatterBoxSessionEventReply_Message(object):

    def __init__(self, message_data):
        
        self.success = message_data['success']
        self.event = message_data['event']
        self.session_id = UUID(string = str(message_data['session_id']))
        self.error = message_data['error']
        
        self.name = 'ChatterBoxSessionEventReply'

class ChatterBoxSessionAgentListUpdates_Message(object):
    """ incomplete implementation"""

    def __init__(self, message_data):

        self.agent_updates = message_data['agent_updates']
        self.session_id = UUID(string = str(message_data['session_id']))
        
        self.name = 'ChatterBoxSessionAgentListUpdates'

        #{'body': {'agent_updates': {'a517168d-1af5-4854-ba6d-672c8a59e439': {'info': {'can_voice_chat': True, 'is_moderator': False}}}, 'session_id': '4dd70b7f-8b3a-eef9-fc2f-909151d521f6', 'updates': {}}, 'message': 'ChatterBoxSessionAgentListUpdates'}]


class ChatterBoxSessionStartReply_Message(object):
    """ incomplete implementation"""

    def __init__(self, message_data):

        self.temp_session_id = UUID(string = str(message_data['temp_session_id']))
        self.success = message_data['success']
        self.session_id = UUID(string = str(message_data['session_id']))
        self.session_info = message_data['session_info']

        self.name = "ChatterBoxSessionStartReply"
        #{'body': {'temp_session_id': 4dd70b7f-8b3a-eef9-fc2f-909151d521f6, 'success': True, 'session_id': 4dd70b7f-8b3a-eef9-fc2f-909151d521f6, 'session_info': {'voice_enabled': True, 'session_name': "Enus' Construction Crew", 'type': 0, 'moderated_mode': {'voice': False}}}, 'message': 'ChatterBoxSessionStartReply'}],

# ~~~~~~~~~~~~~~~~~~
# Callback functions
# ~~~~~~~~~~~~~~~~~~

def onCreateGroupReply(packet, group_manager):
    """ when we get a CreateGroupReply packet, log Success, and if True, request the group details. remove the callback in any case """

    # remove the monitor
    group_manager.onCreateGroupReply_received.unsubscribe(onCreateGroupReply, group_manager)

    AgentID = packet.message_data.blocks['AgentData'][0].get_variable('AgentID').data
    GroupID = packet.message_data.blocks['ReplyData'][0].get_variable('GroupID').data
    Success = packet.message_data.blocks['ReplyData'][0].get_variable('Success').data
    Message = packet.message_data.blocks['ReplyData'][0].get_variable('Message').data

    if Success:
        log(INFO, "Created group %s. Message data is: %s" % (GroupID, Message))
        log(WARNING, "We now need to request the group data...")
    else:
        log(WARNING, "Failed to create group due to: %s" % (Message))

def onJoinGroupReply(packet, group_manager):
    """ the simulator tells us if joining a group was a success. """

    group_manager.onJoinGroupReply_received.unsubscribe(onJoinGroupReply, group_manager)

    AgentID = packet.message_data.blocks['AgentData'][0].get_variable('AgentID').data
    GroupID = packet.message_data.blocks['GroupData'][0].get_variable('GroupID').data
    Success = packet.message_data.blocks['GroupData'][0].get_variable('Success').data

    if Success:
        log(INFO, "Joined group %s" % (GroupID))
    else:
        log(WARNING, "Failed to join group %s" % (GroupID))

def onAgentGroupDataUpdate(packet, group_manager):
    """ deal with the data that comes in over the event queue """

    group_data = {}

    AgentID = packet.message_data.blocks['AgentData'][0].get_variable('AgentID').data

    # GroupData block
    for GroupData_block in packet.message_data.blocks['GroupData']:

        group_data['GroupID'] = GroupData_block.get_variable('GroupID').data
        group_data['GroupPowers'] = GroupData_block.get_variable('GroupPowers').data
        group_data['AcceptNotices'] = GroupData_block.get_variable('AcceptNotices').data
        group_data['GroupInsigniaID'] = GroupData_block.get_variable('GroupInsigniaID').data
        group_data['Contribution'] = GroupData_block.get_variable('Contribution').data
        group_data['GroupName'] = GroupData_block.get_variable('GroupName').data

        # make sense of group powers
        group_data['GroupPowers'] = [ord(x) for x in group_data['GroupPowers']]
        group_data['GroupPowers'] = ''.join([str(x) for x in group_data['GroupPowers']])

        group_manager.update_group(group_data)

def onChatterBoxInvitation_Message(message, group_manager):
    """ handle a group chat message from the event queue """

    group_manager.handle_group_chat(message)

def onChatterBoxSessionEventReply(message, group_manager):
    """ handle a response from the simulator re: a message we sent to a group chat """

    group_manager.agent.helpers.log_event_queue_data(message, group_manager)

def onChatterBoxSessionAgentListUpdates(message, group_manager):
    """ parse teh response to a request to join a group chat and propagate data out """

    data = {}
    data['session_id'] = message.session_id
    data['agent_updates'] = message.agent_updates

    group_manager.update_group_by_session_id(data)

def onChatterBoxSessionStartReply(message, group_manager):

    data = {}
    data['temp_session_id'] = message.temp_session_id
    data['success'] = message.success
    data['session_id'] = message.session_id
    data['session_info'] = message.session_info

    group_manager.update_group_by_name(data, data['session_info']['session_name'])

'''
Groups related messages:

//-----------------------------------------------------------------------------
// Group messages
//-----------------------------------------------------------------------------

                        // CreateGroupRequest
                        // viewer -> simulator
                        // simulator -> dataserver
                        // reliable
                        {
                        	CreateGroupRequest Low 339 NotTrusted Zerocoded
                        	{
                        		AgentData		Single
                        		{	AgentID			LLUUID	}
                        		{	SessionID		LLUUID	}
                        	}
                        	{
                        		GroupData		Single
                        		{	Name			Variable	1	}	// string
                        		{	Charter			Variable	2	}	// string
                        		{	ShowInList		BOOL	}
                        		{	InsigniaID		LLUUID	}
                        		{	MembershipFee	S32				}	// S32		
                        		{	OpenEnrollment	BOOL			}   // BOOL (U8)
                        		{	AllowPublish	BOOL		}	// whether profile is externally visible or not
                        		{	MaturePublish	BOOL		}	// profile is "mature"
                        	}
                        }

                        // CreateGroupReply
                        // dataserver -> simulator
                        // simulator -> viewer
                        // reliable
                        {
                        	CreateGroupReply Low 340 Trusted Unencoded
                        	{
                        		AgentData		Single
                        		{	AgentID			LLUUID	}
                        	}
                        	{
                        		ReplyData		Single
                        		{	GroupID			LLUUID	}
                        		{	Success			BOOL	}
                        		{	Message			Variable	1	}	// string
                        	}
                        }

// UpdateGroupInfo
// viewer -> simulator
// simulator -> dataserver
// reliable
{
	UpdateGroupInfo Low 341 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID			LLUUID	}
		{	Charter			Variable	2	}	// string
		{	ShowInList		BOOL			}
		{	InsigniaID		LLUUID	}
		{	MembershipFee	S32				}
		{	OpenEnrollment	BOOL			}
		{	AllowPublish	BOOL	}
		{	MaturePublish	BOOL	}
	}
}

// GroupRoleChanges
// viewer -> simulator -> dataserver
// reliable
{
	GroupRoleChanges	Low	342 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID	LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		RoleChange	Variable
		{	RoleID		LLUUID	}
		{	MemberID	LLUUID	}
		{	Change		U32		}
	}
}

// JoinGroupRequest
// viewer -> simulator -> dataserver
// reliable
{
	JoinGroupRequest Low 343 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID		LLUUID	}
	}
}

// JoinGroupReply
// dataserver -> simulator -> viewer
{
	JoinGroupReply Low 344 Trusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID		LLUUID	}
		{	Success		BOOL	}
	}
}


// EjectGroupMemberRequest
// viewer -> simulator -> dataserver
// reliable
{
	EjectGroupMemberRequest Low 345 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
	}
	{
		EjectData		Variable
		{	EjecteeID	LLUUID	}
	}
}

// EjectGroupMemberReply
// dataserver -> simulator -> viewer
// reliable
{
	EjectGroupMemberReply Low 346 Trusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
	}
	{
		EjectData		Single
		{	Success		BOOL	}
	}
}

// LeaveGroupRequest
// viewer -> simulator -> dataserver
// reliable
{
	LeaveGroupRequest Low 347 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
	}
}

// LeaveGroupReply
// dataserver -> simulator -> viewer
{
	LeaveGroupReply Low 348 Trusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID		LLUUID	}
		{	Success		BOOL	}
	}
}

// InviteGroupRequest
// viewer -> simulator -> dataserver
// reliable
{
	InviteGroupRequest Low 349 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}	// UUID of inviting agent
		{	SessionID	LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID		LLUUID	}
	}
	{
		InviteData	Variable
		{	InviteeID	LLUUID	}
		{	RoleID		LLUUID	}
	}
}

// InviteGroupResponse
// simulator -> dataserver
// reliable
{
	InviteGroupResponse	Low	350 Trusted	Unencoded
	{
		InviteData	Single
		{	AgentID		LLUUID	}
		{	InviteeID	LLUUID	}
		{	GroupID			LLUUID	}
		{	RoleID		LLUUID	}
		{	MembershipFee S32	}
	}
}

// GroupProfileRequest
// viewer-> simulator -> dataserver
// reliable
{
	GroupProfileRequest Low 351 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID	LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID			LLUUID			}
	}
}

// GroupProfileReply
// dataserver -> simulator -> viewer
// reliable
{
	GroupProfileReply Low 352 Trusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
	}
	{
		GroupData		Single
		{	GroupID			LLUUID			}
		{	Name			Variable	1	}	// string
		{	Charter			Variable	2	}	// string
		{	ShowInList		BOOL	}
		{	MemberTitle		Variable	1	}	// string
		{	PowersMask		U64	}	// U32 mask
		{	InsigniaID		LLUUID			}
		{	FounderID		LLUUID			}
		{	MembershipFee	S32				}
		{	OpenEnrollment	BOOL			}   // BOOL (U8)
		{	Money			S32	}
		{	GroupMembershipCount	S32	}
		{	GroupRolesCount			S32	}
		{	AllowPublish	BOOL	}
		{	MaturePublish	BOOL	}
		{	OwnerRole		LLUUID	}
	}
}

// CurrentInterval = 0  =>  this period (week, day, etc.)
// CurrentInterval = 1  =>  last period
// viewer -> simulator -> dataserver
// reliable
{
	GroupAccountSummaryRequest Low 353 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID		LLUUID	}
		{	GroupID			LLUUID	}
	}
	{
		MoneyData			Single
		{	RequestID		LLUUID	}
		{	IntervalDays	S32	}
		{	CurrentInterval	S32	}
	}
}


// dataserver -> simulator -> viewer
// Reliable
{
	GroupAccountSummaryReply Low 354 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	GroupID			LLUUID		}
	}
	{
		MoneyData			Single
		{	RequestID			LLUUID	}
		{	IntervalDays		S32	}
		{	CurrentInterval		S32	}
		{	StartDate			Variable	1	}	// string
		{	Balance				S32	}
		{	TotalCredits		S32	}
		{	TotalDebits			S32	}
		{	ObjectTaxCurrent	S32	}
		{	LightTaxCurrent		S32	}
		{	LandTaxCurrent		S32	}
		{	GroupTaxCurrent		S32	}
		{	ParcelDirFeeCurrent	S32	}
		{	ObjectTaxEstimate	S32	}
		{	LightTaxEstimate	S32	}
		{	LandTaxEstimate		S32	}
		{	GroupTaxEstimate	S32	}
		{	ParcelDirFeeEstimate	S32	}
		{	NonExemptMembers	S32	}
		{	LastTaxDate			Variable	1	}	// string
		{	TaxDate				Variable	1	}	// string
	}
}


// Reliable
{
	GroupAccountDetailsRequest Low 355 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
		{	GroupID			LLUUID	}
	}
	{
		MoneyData			Single
		{	RequestID		LLUUID	}
		{	IntervalDays	S32	}
		{	CurrentInterval	S32	}
	}
}

// Reliable
{
	GroupAccountDetailsReply Low 356 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	GroupID			LLUUID		}
	}
	{
		MoneyData			Single
		{	RequestID		LLUUID	}
		{	IntervalDays	S32	}
		{	CurrentInterval	S32	}
		{	StartDate		Variable	1	}	// string
	}
	{
		HistoryData			Variable
		{	Description		Variable	1	}	// string
		{	Amount			S32	}
	}
}


// Reliable
{
	GroupAccountTransactionsRequest Low 357 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
		{	GroupID			LLUUID		}
	}
	{
		MoneyData			Single
		{	RequestID		LLUUID	}
		{	IntervalDays	S32	}
		{	CurrentInterval	S32	}
	}
}

// Reliable
{
	GroupAccountTransactionsReply Low 358 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	GroupID			LLUUID		}
	}
	{
		MoneyData			Single
		{	RequestID		LLUUID	}
		{	IntervalDays	S32	}
		{	CurrentInterval	S32	}
		{	StartDate		Variable	1	}	// string
	}
	{
		HistoryData			Variable
		{	Time			Variable	1	}	// string
		{	User			Variable	1	}	// string
		{	Type			S32	}
		{	Item			Variable	1	}	// string
		{	Amount			S32	}
	}
}

// GroupActiveProposalsRequest
// viewer -> simulator -> dataserver
//reliable
{
	GroupActiveProposalsRequest Low 359 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID		LLUUID			}
	}
	{
		GroupData	Single
		{	GroupID			LLUUID			}
	}
	{
		TransactionData Single
		{	TransactionID	LLUUID	}
	}
}

// GroupActiveProposalItemReply
// dataserver -> simulator -> viewer
// reliable
{
	GroupActiveProposalItemReply Low 360 Trusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	GroupID			LLUUID			}
	}
	{
		TransactionData Single
		{	TransactionID	LLUUID	}
		{	TotalNumItems	U32		}
	}
	{
		ProposalData	Variable
		{	VoteID			LLUUID			}
		{	VoteInitiator	LLUUID			}
		{	TerseDateID		Variable	1	} // string
		{	StartDateTime	Variable	1	}	// string
		{	EndDateTime		Variable	1	}	// string
		{	AlreadyVoted	BOOL			}
		{	VoteCast		Variable	1	}	// string
		{	Majority	F32		}
		{	Quorum		S32		}
		{	ProposalText	Variable	1	}	// string
	}
}

// GroupVoteHistoryRequest
// viewer -> simulator -> dataserver
//reliable
{
	GroupVoteHistoryRequest Low 361 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID		LLUUID			}
	}
	{
		GroupData	Single
		{	GroupID			LLUUID			}
	}
	{
		TransactionData Single
		{	TransactionID	LLUUID	}
	}
}

// GroupVoteHistoryItemReply
// dataserver -> simulator -> viewer
// reliable
{
	GroupVoteHistoryItemReply Low 362 Trusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	GroupID			LLUUID			}
	}
	{
		TransactionData Single
		{	TransactionID	LLUUID	}
		{	TotalNumItems	U32		}
	}
	{
		HistoryItemData	Single
		{	VoteID			LLUUID			}
		{	TerseDateID		Variable	1	} // string
		{	StartDateTime	Variable	1	}	// string
		{	EndDateTime		Variable	1	}	// string
		{	VoteInitiator	LLUUID			}
		{	VoteType		Variable	1	}	// string
		{	VoteResult		Variable	1	}	// string
		{	Majority	F32		}
		{	Quorum		S32		}
		{	ProposalText	Variable	2	}	// string
	}
	{
		VoteItem	Variable
		{	CandidateID		LLUUID		}
		{	VoteCast		Variable	1	}	// string
		{	NumVotes		S32		}
	}
}

// StartGroupProposal
// viewer -> simulator -> dataserver
// reliable
{
	StartGroupProposal Low 363 NotTrusted Zerocoded UDPDeprecated
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ProposalData		Single
		{	GroupID			LLUUID			}
		{	Quorum			S32				}
		{	Majority		F32				}	// F32
		{	Duration		S32				}	// S32, seconds
		{	ProposalText	Variable	1	}	// string
	}
}

// GroupProposalBallot
// viewer -> simulator -> dataserver
// reliable
{
	GroupProposalBallot Low 364 NotTrusted Unencoded UDPDeprecated
	{
		AgentData		Single
		{	AgentID		LLUUID			}
		{	SessionID	LLUUID	}
	}
	{
		ProposalData		Single
		{	ProposalID		LLUUID			}
		{	GroupID			LLUUID			}
		{	VoteCast		Variable	1	}	// string
	}
}

// TallyVotes userserver -> dataserver
// reliable
{
	TallyVotes	Low	365 Trusted Unencoded
}



// GroupMembersRequest
// get the group members
// simulator -> dataserver
// reliable
{
	GroupMembersRequest Low 366 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
		{   RequestID	LLUUID	}
	}
}

// GroupMembersReply
// list of uuids for the group members
// dataserver -> simulator
// reliable
{
	GroupMembersReply Low 367 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
		{   RequestID	LLUUID	}
		{	MemberCount	S32		}
	}
	{
		MemberData		Variable
		{	AgentID		LLUUID	}
		{	Contribution	S32	}
		{	OnlineStatus	Variable	1	}	// string
		{	AgentPowers		U64	}
		{	Title			Variable	1	}	// string
		{	IsOwner			BOOL	}
	}
}

// used to switch an agent's currently active group.
// viewer -> simulator -> dataserver -> AgentDataUpdate...
{
	ActivateGroup	Low	368 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
}

// viewer -> simulator -> dataserver
{
	SetGroupContribution Low 369 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		Data	Single
		{	GroupID		LLUUID	}
		{	Contribution	S32	}
	}
}

// viewer -> simulator -> dataserver
{
	SetGroupAcceptNotices Low 370 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		Data	Single
		{	GroupID		LLUUID	}
		{	AcceptNotices	BOOL	}
	}
	{
		NewData				Single
		{	ListInProfile	BOOL	}
	}
}

// GroupRoleDataRequest
// viewer -> simulator -> dataserver
{
	GroupRoleDataRequest Low	371 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID		LLUUID	}
		{	RequestID	LLUUID	}
	}
}


// GroupRoleDataReply
// All role data for this group
// dataserver -> simulator -> agent
{
	GroupRoleDataReply Low	372 Trusted	Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
	}
	{
		GroupData		Single
		{	GroupID			LLUUID	}
		{	RequestID	LLUUID	}
		{	RoleCount	S32		}
	}
	{
		RoleData	Variable
		{	RoleID		LLUUID	}
		{	Name		Variable	1	}
		{	Title		Variable	1	}
		{	Description	Variable	1	}
		{	Powers		U64		}
		{	Members		U32		}
	}
}

// GroupRoleMembersRequest
// viewer -> simulator -> dataserver
{
	GroupRoleMembersRequest Low	373 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID	LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
		{	RequestID	LLUUID	}
	}
}

// GroupRoleMembersReply
// All role::member pairs for this group.
// dataserver -> simulator -> agent
{
	GroupRoleMembersReply Low	374 Trusted	Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	GroupID		LLUUID	}
		{	RequestID	LLUUID	}
		{	TotalPairs	U32		}
	}
	{
		MemberData		Variable
		{	RoleID		LLUUID	}
		{	MemberID	LLUUID	}
	}
}

// GroupTitlesRequest
// viewer -> simulator -> dataserver
{
	GroupTitlesRequest Low	375 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
		{	RequestID	LLUUID	}
	}
}


// GroupTitlesReply
// dataserver -> simulator -> viewer
{
	GroupTitlesReply Low 376 Trusted	Zerocoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	GroupID		LLUUID	}
		{	RequestID	LLUUID	}
	}
	{
		GroupData	Variable
		{	Title		Variable	1	} // string
		{	RoleID		LLUUID			}
		{	Selected	BOOL			}
	}
}

// GroupTitleUpdate
// viewer -> simulator -> dataserver
{
	GroupTitleUpdate	Low	377 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
		{	TitleRoleID	LLUUID	}
	}
}

// GroupRoleUpdate
// viewer -> simulator -> dataserver
{
	GroupRoleUpdate		Low	378 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		RoleData	Variable
		{	RoleID		LLUUID	}
		{	Name		Variable	1	}
		{	Description	Variable	1	}
		{	Title		Variable	1	}
		{	Powers		U64		}
		{	UpdateType	U8		}
	}
}
			


// Request the members of the live help group needed for requesting agent.
// userserver -> dataserver
{
	LiveHelpGroupRequest Low 379 Trusted Unencoded
	{
		RequestData 	Single
		{	RequestID	LLUUID	}
		{	AgentID		LLUUID	}
	}
}

// Send down the group
// dataserver -> userserver
{
	LiveHelpGroupReply Low 380 Trusted Unencoded
	{
		ReplyData	 	Single
		{	RequestID	LLUUID	}
		{	GroupID		LLUUID	}
		{	Selection	Variable 	1	} // selection criteria all or active
	}
}

'''
