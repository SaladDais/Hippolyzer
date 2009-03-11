"""
@file agent.py
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

# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import re
import sys
import signal
import uuid

#related
from eventlet import api

# pyogp
from pyogp.lib.base.login import Login, LegacyLoginParams, OGPLoginParams
from pyogp.lib.base.exc import LoginError
from pyogp.lib.base.region import Region
from pyogp.lib.base.inventory import Inventory
# from pyogp.lib.base.appearance import Appearance

# pyogp messaging
from pyogp.lib.base.message.packethandler import PacketHandler
from pyogp.lib.base.message.packets import *

# pyogp utilities
from pyogp.lib.base.utilities.helpers import Helpers

# initialize logging
logger = getLogger('pyogp.lib.base.agent')
log = logger.log

class Agent(object):
    """ an agent container

    The Agent class is a container for agent specific data.
    It is also a nice place for convenience code.

    Example, of login via the agent class:

    Initialize the login class
    >>> client = Agent()

    >>> client.login('https://login.agni.lindenlab.com/cgi-bin/login.cgi', 'firstname', 'lastname', 'secret', start_location = 'last')

    Sample implementations: examples/sample_agent_login.py
    Tests: tests/login.txt, tests/test_agent.py

    """

    def __init__(self, settings = None):
        """ initialize this agent """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        # signal handler to capture erm signals
        self.signal_handler = signal.signal(signal.SIGINT, self.sigint_handler)

        # storage containers for agent attributes
        # we store what the grid tells us, rather than what
        # is passed in and stored in Login()
        self.firstname = None
        self.lastname = None
        self.agent_id = None
        self.session_id = None
        self.secure_session_id = None

        # other storage containers
        self.inventory_host = None
        self.agent_access = None
        self.udp_blacklist = None
        self.home = None
        self.inventory = None

        # additional attributes
        self.login_response = None
        self.connected = False
        self.grid_type = None
        self.running = True
        self.packet_handler = PacketHandler(self.settings)
        self.helpers = Helpers()

        # data we store as it comes in from the grid
        self.Position = None

        # should we include these here?
        self.agentdomain = None     # the agent domain the agent is connected to if an OGP context
        self.regions = []           # all known regions
        self.region = None          # the host simulation for the agent

        # init Appearance()
        # self.appearance = Appearance(self.settings, self)

        # set up callbacks (is this a decent place to do this? it's perhaps premature)
        if self.settings.HANDLE_PACKETS:

            onAgentDataUpdate_received = self.packet_handler._register('AgentDataUpdate')
            onAgentDataUpdate_received.subscribe(onAgentDataUpdate, self)

            onAgentMovementComplete_received = self.packet_handler._register('AgentMovementComplete')
            onAgentMovementComplete_received.subscribe(onAgentMovementComplete, self)

            onHealthMessage_received = self.packet_handler._register('HealthMessage')
            onHealthMessage_received.subscribe(onHealthMessage, self)

            if self.settings.ENABLE_COMMUNICATIONS_TRACKING:

                onChatFromSimulator_received = self.packet_handler._register('ChatFromSimulator')
                onChatFromSimulator_received.subscribe(self.helpers.log_packet, self)

                onImprovedInstantMessage_received = self.packet_handler._register('ImprovedInstantMessage')
                onImprovedInstantMessage_received.subscribe(self.helpers.log_packet, self)

                onChatterBoxInvitation_received = self.packet_handler._register('ChatterBoxInvitation')
                onChatterBoxInvitation_received.subscribe(self.helpers.log_packet, self)

            if self.settings.MULTIPLE_SIM_CONNECTIONS:

                pass

                '''
                onEnableSimulator_received = self.packet_handler._register('EnableSimulator')
                onEnableSimulator_received.subscribe(self.helpers.log_packet, self)
                '''

        if self.settings.LOG_VERBOSE: log(DEBUG, 'Initializing agent: %s' % (self))

    def login(self, loginuri, firstname=None, lastname=None, password=None, login_params = None, start_location=None, handler=None, connect_region = False):
        """ login to a login endpoint. this should move to a login class in time """

        if (re.search('auth.cgi$', loginuri)):

            self.grid_type = 'OGP'

        elif (re.search('login.cgi$', loginuri)):

            self.grid_type = 'Legacy'

        else:
            log(WARNING, 'Unable to identify the loginuri schema. Stopping')
            sys.exit(-1)

        # handle either login params passed in, or, account info
        if login_params == None:

            if (firstname == None) or (lastname == None) or (password == None):

                raise LoginError('Unable to login an unknown agent.')

            else:

                self._login_params = self._get_login_params(loginuri, firstname, lastname, password)

        else:

            self._login_params = login_params

        # login and parse the response
        login = Login(settings = self.settings)

        try:

            self.login_response = login.login(loginuri, self._login_params, start_location, handler = handler)
            self._parse_login_response()

        except LoginError, error:

            log(WARNING, 'Failed to login user. Stopping')
            sys.exit(-1)

        # ToDo: what to do with self.login_response['look_at']?

        if connect_region:
            self._enable_current_region()

    def logout(self):
        """ logs an agent out of the current region """

        if self.region.logout():
            self.connected = False

    def _get_login_params(self, loginuri, firstname, lastname, password):
        """ get the proper login parameters """

        if self.grid_type == 'OGP':

            login_params = OGPLoginParams(firstname, lastname, password)

        elif self.grid_type == 'Legacy':

            login_params = LegacyLoginParams(firstname, lastname, password)

        return login_params

    def _parse_login_response(self):
        """ evaluates the login response """

        if self.grid_type == 'Legacy':

            self.firstname = re.sub(r'\"', '', self.login_response['first_name'])
            self.lastname = self.login_response['last_name']
            self.agent_id = self.login_response['agent_id']
            self.session_id = self.login_response['session_id']
            self.secure_session_id = self.login_response['secure_session_id']

            self.connected = bool(self.login_response['login'])
            self.inventory_host = self.login_response['inventory_host']
            self.agent_access = self.login_response['agent_access']
            self.udp_blacklist = self.login_response['udp_blacklist']

            if self.login_response.has_key('home'): self.home = Home(self.login_response['home'])

            if self.settings.ENABLE_INVENTORY_MANAGEMENT:

                self.inventory = Inventory(self)
                self.inventory._parse_folders_from_login_response()

        elif self.grid_type == 'OGP':

            pass

    def _enable_current_region(self, region_x = None, region_y = None, seed_capability = None, udp_blacklist = None, sim_ip = None, sim_port = None, circuit_code = None):
        """ enables an agents current region """

        # enable the current region, setting connect = True
        self.region = Region(self.login_response['region_x'], self.login_response['region_y'], self.login_response['seed_capability'], self.login_response['udp_blacklist'], self.login_response['sim_ip'], self.login_response['sim_port'], self.login_response['circuit_code'], self, settings = self.settings, packet_handler = self.packet_handler)

        # start the simulator udp and event queue connections
        api.spawn(self.region.connect)
        #self.region.connect()
        while self.running:
            api.sleep(0)

    def send_AgentDataUpdateRequest(self):
        """ request an agent data update """

        packet = AgentDataUpdateRequestPacket()

        packet.AgentData['AgentID'] = uuid.UUID(str(self.agent_id))
        packet.AgentData['SessionID'] = uuid.UUID(str(self.session_id))

        self.region.enqueue_message(packet())

    # ~~~~~~~~~~~~~~
    # Communications
    # ~~~~~~~~~~~~~~

    # Chat

    def say(self, Message, Type = 1, Channel = 0):
        """ Sends ChatFromViewer

        Channel: 0 is open chat
        Type: 0 = Whisper
              1 = Say
              2 = Shout
        """

        packet = ChatFromViewerPacket()

        packet.AgentData['AgentID'] = uuid.UUID(str(self.agent_id))
        packet.AgentData['SessionID'] = uuid.UUID(str(self.session_id))

        packet.ChatData['Message'] = Message + '\x00' # Message needs a terminator. Arnold was busy as gov...
        packet.ChatData['Type'] = Type
        packet.ChatData['Channel'] = Channel

        self.region.enqueue_message(packet())

    # Instant Message (im, group chat)

    def instant_message(self, ToAgentID = None, Message = None):
        """ sends an instant message to another avatar

        wraps send_ImprovedInstantMessage with some handy defaults """

        #ToDo: this opens a new im window every time a message is sent to a viewer. why is this? fix it.

        if ToAgentID != None and Message != None:

            _AgentID = uuid.UUID(str(self.agent_id))
            _SessionID = uuid.UUID(str(self.session_id))
            _FromGroup = False
            _ToAgentID = uuid.UUID(str(ToAgentID))
            _ParentEstateID = 0
            _RegionID = uuid.UUID('00000000-0000-0000-0000-000000000000')
            _Position = self.Position
            _Offline = 0
            _Dialog = 0                 # Dialog type 1 = instant message
            _ID = uuid.uuid4()          # generate a random uuid
            _Timestamp = 0
            _FromAgentName = self.firstname + ' ' + self.lastname
            _Message = Message
            _BinaryBucket = ''

            self.send_ImprovedInstantMessage(_AgentID, _SessionID, _FromGroup, _ToAgentID, _ParentEstateID, _RegionID, _Position, _Offline, _Dialog, _ID, _Timestamp, _FromAgentName, _Message, _BinaryBucket)

        else:

            log(INFO, "Please specify an agentid and message to send in agent.instant_message")

    def send_ImprovedInstantMessage(self, AgentID = None, SessionID = None, FromGroup = None, ToAgentID = None, ParentEstateID = None, RegionID = None, Position = None, Offline = None, Dialog = None, _ID = None, Timestamp = None, FromAgentName = None, Message = None, BinaryBucket = None, AgentDataBlock = {}, MessageBlockBlock = {}):
        """ sends an instant message to ToAgentID 

        // ImprovedInstantMessage
        // This message can potentially route all over the place
        // ParentEstateID: parent estate id of the source estate
        // RegionID: region id of the source of the IM.
        // Position: position of the sender in region local coordinates
        // Dialog	see llinstantmessage.h for values
        // ID		May be used by dialog. Interpretation depends on context.
        // BinaryBucket May be used by some dialog types
        // reliable
        """

        packet = ImprovedInstantMessagePacket()

        if AgentDataBlock == {}:
            packet.AgentData['AgentID'] = uuid.UUID(str(AgentID))
            packet.AgentData['SessionID'] = uuid.UUID(str(SessionID))            
        else:
            packet.AgentData = AgentDataBlock

        if FromAgentName == None:
            FromAgentName = self.firstname + ' ' + self.lastname

        # ha! when scripting out packets.py, never considered a block named *block
        if MessageBlockBlock == {}:

            packet.MessageBlock['FromGroup'] = FromGroup                   # Bool
            packet.MessageBlock['ToAgentID'] = uuid.UUID(str(ToAgentID))   # LLUUID
            packet.MessageBlock['ParentEstateID'] = ParentEstateID         # U32
            packet.MessageBlock['RegionID'] = uuid.UUID(str(RegionID))     # LLUUID
            packet.MessageBlock['Position'] = Position                     # LLVector3
            packet.MessageBlock['Offline'] = Offline                       # U8
            packet.MessageBlock['Dialog'] = Dialog                         # U8 IM Type
            packet.MessageBlock['ID'] = uuid.UUID(str(_ID))                # LLUUID
            packet.MessageBlock['Timestamp'] = Timestamp                   # U32
            packet.MessageBlock['FromAgentName'] = FromAgentName           # Variable 1
            packet.MessageBlock['Message'] = Message                       # Variable 2
            packet.MessageBlock['BinaryBucket'] = BinaryBucket             # Variable 2

        self.region.enqueue_message(packet(), True)

        def send_RetrieveInstantMessages(self):
            """ asks simulator for instant messages stored while agent was offline """

            packet = RetrieveInstantMessagesPackets()

            packet.AgentDataBlock['AgentID'] = uuid.UUID(str(self.agent_id))
            packet.AgentDataBlock['SessionID'] = uuid.UUID(str(self.session_id))

            self.region.enqueue_message(packet())

    def sigint_handler(self, signal, frame):
        log(INFO, "Caught signal... %d. Stopping" % signal)
        self.running = False
        self.logout()
        #sys.exit(0)

    def __repr__(self):
        """ returns a representation of the agent """

        if self.firstname == None:
            return 'A new agent instance'
        else:
            return '%s %s' % (self.firstname, self.lastname)

def onAgentDataUpdate(packet, agent):

    if agent.agent_id == None:
        agent.agent_id = packet.message_data.blocks['AgentData'][0].get_variable('AgentID').data

    if agent.firstname == None:
        agent.firstname = packet.message_data.blocks['AgentData'][0].get_variable('FirstName').data

    if agent.lastname == None:
        agent.firstname = packet.message_data.blocks['AgentData'][0].get_variable('LastName').data

    agent.GroupTitle = packet.message_data.blocks['AgentData'][0].get_variable('GroupTitle').data

    agent.ActiveGroupID = packet.message_data.blocks['AgentData'][0].get_variable('ActiveGroupID').data

    agent.GroupPowers = packet.message_data.blocks['AgentData'][0].get_variable('GroupPowers').data

    agent.GroupName = packet.message_data.blocks['AgentData'][0].get_variable('GroupName').data

def onAgentMovementComplete(packet, agent):

    agent.Position = packet.message_data.blocks['Data'][0].get_variable('Position').data

    agent.LookAt = packet.message_data.blocks['Data'][0].get_variable('LookAt').data

    agent.region.RegionHandle = packet.message_data.blocks['Data'][0].get_variable('RegionHandle').data

    #agent.Timestamp = packet.message_data.blocks['Data'][0].get_variable('Timestamp')

    agent.region.ChannelVersion = packet.message_data.blocks['SimData'][0].get_variable('ChannelVersion').data

def onHealthMessage(packet, agent):

    agent.health = packet.message_data.blocks['HealthData'][0].get_variable('Health')

def onChatFromSimulator(packet, agent):

    pass
    '''
    {
        ChatFromSimulator Low 139 Trusted Unencoded
        {
                ChatData                        Single
                {       FromName                Variable 1      }
                {       SourceID                LLUUID          }       // agent id or object id
                {       OwnerID                 LLUUID          }       // object's owner
                {       SourceType              U8                      }
                {       ChatType                U8                      }
                {       Audible                 U8                      }
                {       Position                LLVector3       }
                {       Message                 Variable 2      }       // UTF-8 text
        }
    }
    '''

def onImprovedInstantMessage(packet, agent):

    pass
    '''
    // ImprovedInstantMessage
    // This message can potentially route all over the place
    // ParentEstateID: parent estate id of the source estate
    // RegionID: region id of the source of the IM.
    // Position: position of the sender in region local coordinates
    // Dialog   see llinstantmessage.h for values
    // ID               May be used by dialog. Interpretation depends on context.
    // BinaryBucket May be used by some dialog types
    // reliable
    {
        ImprovedInstantMessage Low 254 NotTrusted Zerocoded
        {
                AgentData               Single
                {   AgentID     LLUUID  }
                {       SessionID       LLUUID  }
        }
        {
                MessageBlock            Single
                {       FromGroup               BOOL    }
                {       ToAgentID               LLUUID  }
                {       ParentEstateID  U32     }
                {   RegionID            LLUUID  }
                {       Position                LLVector3       }
                {       Offline                 U8      }
                {       Dialog                  U8      }       // U8 - IM type
                {       ID                              LLUUID  }
                {       Timestamp               U32     }
                {       FromAgentName   Variable        1       }
                {       Message                 Variable        2       }
                {       BinaryBucket    Variable        2       }
        }
    }
    '''

class Home(object):
    """ contains the parameters descibing an agent's home location """

    def __init__(self, params):

        # eval(params) would be nice, but fails to parse the string the way one thinks it might
        items =  params.split(', \'')

        # this creates:
        #   self.region_handle
        #   self.look_at
        #   self.position
        for i in items:
            i = re.sub(r'[\"\{}\'"]', '', i)
            i = i.split(':')
            setattr(self, i[0], eval(re.sub('r', '', i[1])))

        self.global_x = self.region_handle[0]
        self.global_y = self.region_handle[1]

        self.local_x = self.position[0]
        self.local_y = self.position[1]
        self.local_z = self.position[2]