
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
from logging import getLogger, WARNING, INFO, DEBUG
import re

# related
from eventlet import api

# for MockChatInterface
import sys
import select
import tty
import termios

# pyogp
from pyogp.lib.base.datatypes import UUID, Vector3
from pyogp.lib.base.exc import DataParsingError
from pyogp.lib.base.utilities.helpers import Wait
from pyogp.lib.base.datamanager import DataManager

# pyogp messaging
from pyogp.lib.base.message.message import Message, Block

# pyogp utilities
from pyogp.lib.base.utilities.enums import ImprovedIMDialogue

# initialize logging
logger = getLogger('pyogp.lib.base.groups')
log = logger.log

class GroupManager(DataManager):
    """ a storage bin for groups

    also, a functional area for group creation operations
    """

    def __init__(self, agent, settings = None):
        """ initialize the group manager """
        super(GroupManager, self).__init__(agent, settings)
        # the group store consists of a list
        # of Group() instances
        self.group_store = []

        if self.settings.LOG_VERBOSE:
            log(DEBUG, "Initialized the Group Manager")

    def enable_callbacks(self):
        """enables the callback handlers for this GroupManager"""
        if self.settings.HANDLE_PACKETS:
            onAgentGroupDataUpdate_received = self.agent.region.message_handler.register("AgentGroupDataUpdate")
            onAgentGroupDataUpdate_received.subscribe(self.onAgentGroupDataUpdate)

            onChatterBoxInvitation_received = self.agent.region.message_handler.register('ChatterBoxInvitation')
            onChatterBoxInvitation_received.subscribe(self.onChatterBoxInvitation_Message)

            onChatterBoxSessionEventReply_received = self.agent.region.message_handler.register('ChatterBoxSessionEventReply')
            onChatterBoxSessionEventReply_received.subscribe(self.onChatterBoxSessionEventReply)

            onChatterBoxSessionAgentListUpdates_received = self.agent.region.message_handler.register('ChatterBoxSessionAgentListUpdates')
            onChatterBoxSessionAgentListUpdates_received.subscribe(self.onChatterBoxSessionAgentListUpdates)

            onChatterBoxSessionStartReply_received = self.agent.region.message_handler.register('ChatterBoxSessionStartReply')
            onChatterBoxSessionStartReply_received.subscribe(self.onChatterBoxSessionStartReply)

    
    def handle_group_chat(self, message):
        """ process a ChatterBoxInvitation_Message instance"""

        group = [group for group in self.group_store if str(message.blocks['Message_Data'][0].get_variable('instantmessage').data['message_params']['id']) == str(group.GroupID)]

        if group != []:
            group[0].handle_inbound_chat(message)
        else:
            log(WARNING, "Received group chat message from unknown group. Group: %s. Agent: %s. Message: %s" % (message.blocks['Message_Data'][0].get_variable('session_name').data, message.blocks['Message_Data'][0].get_variable('from_name').data, message.blocks['Message_Data'][0].get_variable('message').data))

    def store_group(self, _group):
        """ append to or replace a group in self.group_store """

        # replace an existing list member, else, append

        try:

            index = [self.group_store.index(_group_) for _group_ in self.group_store if _group_.ID == _group.GroupID]

            self.group_store[index[0]] = _group

            if self.settings.LOG_VERBOSE:
                log(DEBUG, 'Replacing a stored group: \'%s\'' % (_group.GroupID))

        except:

            self.group_store.append(_group)

            if self.settings.LOG_VERBOSE:
                log(DEBUG, 'Stored a new group: \'%s\'' % (_group.GroupID))

    def update_group(self, group_data):
        """ accepts a dictionary of group data and creates/updates a group """

        group = [group for group in self.group_store if str(group_data['GroupID']) == str(group.GroupID)]

        if group != []:
            group[0].update_properties(group_data)
            if self.settings.LOG_VERBOSE:
                log(DEBUG, 'Updating a stored group: \'%s\'' % (group[0].GroupID))
        else:
            group = Group(GroupID = group_data['GroupID'], 
                        GroupPowers = group_data['GroupPowers'], 
                        AcceptNotices = group_data['AcceptNotices'], 
                        GroupInsigniaID = group_data['GroupInsigniaID'], 
                        Contribution = group_data['Contribution'], 
                        GroupName = group_data['GroupName'])

            self.store_group(group)

    def update_group_by_name(self, group_data, name):
        """ accepts a dictionary of group data and creates/updates a group """

        pattern = re.compile(name)

        group = [group for group in self.group_store if pattern.match(group.GroupName)]

        if group != []:
            group[0].update_properties(group_data)
            if self.settings.LOG_VERBOSE:
                log(DEBUG, 'Updating a stored group: \'%s\'' % (group[0].GroupName))
        else:
            log(INFO, "Received an update for an unknown group for name: %s" % (name))

    def update_group_by_session_id(self, group_data):
        """ accepts a dictionary of group data and creates/updates a group """

        group = [group for group in self.group_store if str(group.session_id) == str(group_data['session_id'])]

        if group != []:
            group[0].update_properties(group_data)
            if self.settings.LOG_VERBOSE:
                log(DEBUG, 'Updating a stored group: \'%s\'' % (group[0].GroupName))
        else:
            log(INFO, "Received an update for an unknown group with a session id of: %s" % (str(group_data['session_id'])))

    def create_group(self,
                    AgentID = None,
                    SessionID = None,
                    Name = None,
                    Charter = '',
                    ShowInList = True,
                    InsigniaID = UUID(),
                    MembershipFee = 0,
                    OpenEnrollment = False,
                    AllowPublish = False,
                    MaturePublish = False):
        """ sends a message to the agent's current region requesting to create a group

        enables a callback (which should be unsubscribed from once we get a response)
        """

        if Name != None:

            log(INFO, "Sending a request to create group with a name of \'%s\'" % (Name))

            if AgentID == None:
                AgentID = self.agent.agent_id
            if SessionID == None:
                SessionID = self.agent.session_id

            packet = Message('CreateGroupRequest',
                                Block('AgentData',
                                        AgentID = AgentID,
                                        SessionID = SessionID),
                                Block('GroupData',
                                        Name = Name,
                                        Charter = Charter,
                                        ShowInList = ShowInList,
                                        InsigniaID = InsigniaID,
                                        MembershipFee = MembershipFee,
                                        OpenEnrollment = OpenEnrollment,
                                        AllowPublish = AllowPublish,
                                        MaturePublish = MaturePublish))

            self.agent.region.enqueue_message(packet, True)

            if self.settings.HANDLE_PACKETS:
                # enable the callback to watch for the CreateGroupReply packet
                self.onCreateGroupReply_received = self.agent.region.message_handler.register('CreateGroupReply')
                self.onCreateGroupReply_received.subscribe(self.onCreateGroupReply)
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

        # set up the callback
        self.onJoinGroupReply_received = self.agent.message_handler.register('JoinGroupReply')
        self.onJoinGroupReply_received.subscribe(self.onJoinGroupReply)

        self.send_JoinGroupRequest(self.agent.agent_id, self.agent.session_id, group_id)

    def send_JoinGroupRequest(self, agent_id, session_id, group_id):
        """ sends a JoinGroupRequest message to the hsot simulator """

        packet = Message('JoinGroupRequest',
                        Block('AgentData',
                                AgentID = AgentID,
                                SessionID = SessionID),
                            Block('GroupData',
                                GroupID = group_id))

        self.agent.region.enqueue_message(packet, True)

    def activate_group(self, group_id):
        """ set a particular group as active """

        self.send_ActivateGroup(self.agent.agent_id, self.agent.session_id, group_id)

    def send_ActivateGroup(self, agent_id, session_id, group_id):
        """ sends an ActivateGroup message to the host simulator """

        packet = Message('ActivateGroup',
                        Block('AgentData',
                                AgentID = agent_id,
                                SessionID = session_id,
                                GroupID = group_id))

        self.agent.region.enqueue_message(packet)

    # ~~~~~~~~~~~~~~~~~~
    # Callback functions
    # ~~~~~~~~~~~~~~~~~~

    def onCreateGroupReply(self, packet):
        """ when we get a CreateGroupReply packet, log Success, and if True, request the group details. remove the callback in any case """

        # remove the monitor
        self.onCreateGroupReply_received.unsubscribe(self.onCreateGroupReply)

        AgentID = packet.blocks['AgentData'][0].get_variable('AgentID').data
        GroupID = packet.blocks['ReplyData'][0].get_variable('GroupID').data
        Success = packet.blocks['ReplyData'][0].get_variable('Success').data
        _Message = packet.blocks['ReplyData'][0].get_variable('Message').data

        if Success:
            log(INFO, "Created group %s. Message data is: %s" % (GroupID, _Message))
            log(WARNING, "We now need to request the group data...")
        else:
            log(WARNING, "Failed to create group due to: %s" % (_Message))

    def onJoinGroupReply(self, packet):
        """ the simulator tells us if joining a group was a success. """

        self.onJoinGroupReply_received.unsubscribe(self.onJoinGroupReply)

        AgentID = packet.blocks['AgentData'][0].get_variable('AgentID').data
        GroupID = packet.blocks['GroupData'][0].get_variable('GroupID').data
        Success = packet.blocks['GroupData'][0].get_variable('Success').data

        if Success:
            log(INFO, "Joined group %s" % (GroupID))
        else:
            log(WARNING, "Failed to join group %s" % (GroupID))

    def onAgentGroupDataUpdate(self, packet):
        """ deal with the data that comes in over the event queue """

        group_data = {}

        AgentID = packet.blocks['AgentData'][0].get_variable('AgentID').data

        # GroupData block
        for GroupData_block in packet.blocks['GroupData']:

            group_data['GroupID'] = GroupData_block.get_variable('GroupID').data
            group_data['GroupPowers'] = GroupData_block.get_variable('GroupPowers').data
            group_data['AcceptNotices'] = GroupData_block.get_variable('AcceptNotices').data
            group_data['GroupInsigniaID'] = GroupData_block.get_variable('GroupInsigniaID').data
            group_data['Contribution'] = GroupData_block.get_variable('Contribution').data
            group_data['GroupName'] = GroupData_block.get_variable('GroupName').data

            # make sense of group powers
            group_data['GroupPowers'] = [ord(x) for x in group_data['GroupPowers']]
            group_data['GroupPowers'] = ''.join([str(x) for x in group_data['GroupPowers']])

            self.update_group(group_data)

    def onChatterBoxInvitation_Message(self, message):
        """ handle a group chat message from the event queue """

        self.handle_group_chat(message)

    def onChatterBoxSessionEventReply(self, message):
        """ handle a response from the simulator re: a message we sent to a group chat """

        self.agent.helpers.log_event_queue_data(message, self)

    def onChatterBoxSessionAgentListUpdates(self, message):
        """ parse teh response to a request to join a group chat and propagate data out """

        data = {}
        data['session_id'] = message.blocks['Message_Data'][0].get_variable('session_id').data
        data['agent_updates'] = message.blocks['Message_Data'][0].get_variable('agent_updates').data

        self.update_group_by_session_id(data)

    def onChatterBoxSessionStartReply(self, message):

        data = {}
        data['temp_session_id'] = message.blocks['Message_Data'][0].get_variable('temp_session_id').data
        data['success'] = message.blocks['Message_Data'][0].get_variable('success').data
        data['session_id'] = message.blocks['Message_Data'][0].get_variable('session_id').data
        data['session_info'] = message.blocks['Message_Data'][0].get_variable('session_info').data

        self.update_group_by_name(data, data['session_info']['session_name'])


class Group(object):
    """ representation of a group """

    def __init__(self, AcceptNotices = None, GroupPowers = None, GroupID = None, GroupName = None, ListInProfile = None, Contribution = None, GroupInsigniaID = None, agent = None):

        self.AcceptNotices = AcceptNotices
        self.GroupPowers = GroupPowers
        self.GroupID = UUID(str(GroupID))
        self.GroupName = GroupName
        self.ListInProfile = ListInProfile
        self.Contribution = Contribution
        self.GroupInsigniaID = UUID(str(GroupInsigniaID))

        self.agent = agent

        # store a history of ChatterBoxInvitation messages, and outgoing packets
        self.chat_history = []
        self.session_id = None

    def activate_group(self):
        """ set this group as active """

        self.send_ActivateGroup(self.agent.agent_id, self.agent.session_id, self.GroupID)

    def send_ActivateGroup(self, agent_id, session_id, group_id):
        """ send an ActivateGroup message to the host simulator """

        packet = Message('ActivateGroup',
                            Block('AgentData',
                                    AgentID = agent_id,
                                    SessionID = session_id,
                                    GroupID = group_id))

        self.agent.region.enqueue_message(packet)

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
        _Dialog = ImprovedIMDialogue.SessionGroupStart
        _ID = self.GroupID
        _Timestamp = 0
        _FromAgentName = self.agent.Name()
        _Message = 'Message'''
        _BinaryBucket = ''

        self.agent.send_ImprovedInstantMessage(_AgentID,
                                                _SessionID,
                                                _FromGroup,
                                                _ToAgentID,
                                                _ParentEstateID,
                                                _RegionID,
                                                _Position,
                                                _Offline,
                                                _Dialog,
                                                _ID,
                                                _Timestamp,
                                                _FromAgentName,
                                                _Message,
                                                _BinaryBucket)

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
            _Dialog = ImprovedIMDialogue.SessionSend
            _ID = self.GroupID
            _Timestamp = 0
            _FromAgentName = self.agent.Name() + "\x00" #struct.pack(">" + str(len(self.agent.Name)) + "c", *(self.agent.Name()))
            _Message = Message + "\x00" #struct.pack(">" + str(len(Message)) + "c", *(Message))
            _BinaryBucket = "\x00" # self.GroupName #struct.pack(">" + str(len(self.GroupName)) + "c", *(self.GroupName))

            self.agent.send_ImprovedInstantMessage(_AgentID,
                                                    _SessionID,
                                                    _FromGroup,
                                                    _ToAgentID,
                                                    _ParentEstateID,
                                                    _RegionID,
                                                    _Position,
                                                    _Offline,
                                                    _Dialog,
                                                    _ID,
                                                    _Timestamp,
                                                    _FromAgentName,
                                                    _Message,
                                                    _BinaryBucket)

    def handle_inbound_chat(self, message):
        """ parses an incoming chat message from a group """

        session_id = message.blocks['Message_Data'][0].get_variable('session_id').data
        session_name = message.blocks['Message_Data'][0].get_variable('session_name').data
        from_name = message.blocks['Message_Data'][0].get_variable('from_name').data
        _message = message.blocks['Message_Data'][0].get_variable('instantmessage').data['message_params']['message']

        self.chat_history.append(message)

        # Todo: raise an app level event
        log(INFO, "Group chat received. Group: %s From: %s Message: %s" % (session_name, from_name, _message))

class MockChatInterface(object):
    """ a super simple chat interface for testing group chat in a console """

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

'''
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
'''



