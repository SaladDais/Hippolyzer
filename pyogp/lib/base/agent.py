# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import re
import sys
import signal
import uuid
import sets

#related
from eventlet import api

# pyogp
from pyogp.lib.base.login import Login, LegacyLoginParams, OGPLoginParams
from pyogp.lib.base.datatypes import *
from pyogp.lib.base.exc import LoginError
from pyogp.lib.base.region import Region
from pyogp.lib.base.inventory import *
from pyogp.lib.base.groups import *
from pyogp.lib.base.event_system import *
# from pyogp.lib.base.appearance import Appearance

# pyogp messaging
from pyogp.lib.base.event_queue import EventQueueHandler

from pyogp.lib.base.message.packets import *

# pyogp utilities
from pyogp.lib.base.utilities.helpers import Helpers
from pyogp.lib.base.utilities.enums import ImprovedIMDialogue

# initialize logging
logger = getLogger('pyogp.lib.base.agent')
log = logger.log

class Agent(object):
    """ The Agent class is a container for agent specific data.

    Example, of login via the agent class:
    Initialize the login class

    >>> client = Agent()
    >>> client.login('https://login.agni.lindenlab.com/cgi-bin/login.cgi', 'firstname', 'lastname', 'secret', start_location = 'last')

    Sample implementations: examples/sample_agent_login.py
    Tests: tests/login.txt, tests/test_agent.py

    """

    def __init__(self, settings = None, firstname = '', lastname = '', password = '', agent_id = None, events_handler = None):
        """ initialize this agent """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        # allow the eventhandler to be passed in
        # so that applications running multiple avatars
        # may use the same eventhandler

        # otherwise, let's just use our own
        if events_handler != None:
            self.events_handler = events_handler
        else:
            self.events_handler = EventsHandler()

        # signal handler to capture erm signals
        self.signal_handler = signal.signal(signal.SIGINT, self.sigint_handler)

        # storage containers for agent attributes
        # we overwrite with what the grid tells us, rather than what
        # is passed in and stored in Login()
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.agent_id = None
        self.session_id = None
        self.secure_session_id = None
        self.name = self.Name()

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
        #self.packet_handler = PacketHandler(self.settings)
        self.event_queue_handler = EventQueueHandler(self.settings)
        self.helpers = Helpers()

        # data we store as it comes in from the grid
        self.Position = Vector3()     # this will get updated later, but seed it with 000
        self.ActiveGroupID = UUID()

        # should we include these here?
        self.agentdomain = None     # the agent domain the agent is connected to if an OGP context
        self.child_regions = []     # all neighboring regions
        self._pending_child_regions = []    # neighbor regions an agent may connect to
        self.region = None          # the host simulation for the agent

        # init Appearance()
        # self.appearance = Appearance(self.settings, self)

        if self.settings.LOG_VERBOSE: log(DEBUG, 'Initializing agent: %s' % (self))

    def Name(self):
        """ returns a concatenated firstname + ' ' + lastname"""

        return self.firstname + ' ' + self.lastname

    def login(self, loginuri, firstname=None, lastname=None, password=None, login_params = None, start_location=None, handler=None, connect_region = True):
        """ login to a login endpoint using the Login() class """

        if (re.search('auth.cgi$', loginuri)):

            self.grid_type = 'OGP'

        elif (re.search('login.cgi$', loginuri)):

            self.grid_type = 'Legacy'

        else:
            log(WARNING, 'Unable to identify the loginuri schema. Stopping')
            sys.exit(-1)

        if firstname != None:
            self.firstname = firstname
        if lastname != None:
            self.lastname = lastname
        if password != None:
            self.password = password

        # handle either login params passed in, or, account info
        if login_params == None:

            if (self.firstname == '') or (self.lastname == '') or (self.password == ''):

                raise LoginError('Unable to login an unknown agent.')

            else:

                self._login_params = self._get_login_params(loginuri, self.firstname, self.lastname, self.password)

        else:

            self._login_params = login_params

        # login and parse the response
        login = Login(settings = self.settings)

        self.login_response = login.login(loginuri, self._login_params, start_location, handler = handler)
        self._parse_login_response()

        # ToDo: what to do with self.login_response['look_at']?

        if self.settings.MULTIPLE_SIM_CONNECTIONS:
            api.spawn(self._monitor_for_new_regions)

        if connect_region:
            self._enable_current_region()

    def logout(self):
        """ logs an agent out of the current region. calls Region()._kill_coroutines() for all child regions, and Region().logout() for the host region """

        if not self.connected:
            log(INFO, 'Agent is not logged into the grid. Stopping.')
            sys.exit()

        self.running = False

        if self.region == None:
            return
        else:

            # kill udp and or event queue for child regions
            [region._kill_coroutines() for region in self.child_regions]

            if self.region.logout():
                self.connected = False

        # zero out the password in case we dump it somewhere
        self.password = ''

    def _get_login_params(self, loginuri, firstname, lastname, password):
        """ get the proper login parameters of the legacy or ogp enabled grid """

        if self.grid_type == 'OGP':

            login_params = OGPLoginParams(firstname, lastname, password)

        elif self.grid_type == 'Legacy':

            login_params = LegacyLoginParams(firstname, lastname, password)

        return login_params

    def _parse_login_response(self):
        """ evaluates the login response and propagates data to the Agent() attributes. enables Inventory() if settings dictate """

        if self.grid_type == 'Legacy':

            self.firstname = re.sub(r'\"', '', self.login_response['first_name'])
            self.lastname = self.login_response['last_name']
            self.agent_id = UUID(self.login_response['agent_id'])
            self.session_id = UUID(self.login_response['session_id'])
            self.secure_session_id = UUID(self.login_response['secure_session_id'])

            self.connected = bool(self.login_response['login'])
            self.inventory_host = self.login_response['inventory_host']
            self.agent_access = self.login_response['agent_access']
            self.udp_blacklist = self.login_response['udp_blacklist']

            if self.login_response.has_key('home'): self.home = Home(self.login_response['home'])

        elif self.grid_type == 'OGP':

            pass

    def _enable_current_region(self, region_x = None, region_y = None, seed_capability = None, udp_blacklist = None, sim_ip = None, sim_port = None, circuit_code = None):
        """ enables and connects udp and event queue for an agent's current region """

        if self.login_response.has_key('circuit_code'):
            self.circuit_code = self.login_response['circuit_code']

        # enable the current region, setting connect = True
        self.region = Region(self.login_response['region_x'], self.login_response['region_y'], self.login_response['seed_capability'], self.login_response['udp_blacklist'], self.login_response['sim_ip'], self.login_response['sim_port'], self.login_response['circuit_code'], self, settings = self.settings, event_queue_handler = self.event_queue_handler, events_handler = self.events_handler)

        self.region.is_host_region = True

        self._enable_callbacks()

        # start the simulator udp and event queue connections
        if self.settings.LOG_COROUTINE_SPAWNS: log(INFO, "Spawning a coroutine for connecting to the agent's host region.")

        api.spawn(self.region.connect)

        while self.region.capabilities == {}:

            api.sleep(0)

        if self.settings.ENABLE_INVENTORY_MANAGEMENT:

            inventory_caps = ['FetchInventory', 'WebFetchInventoryDescendents', 'FetchLib', 'FetchLibDescendents']

            if sets.Set(self.region.capabilities.keys()).intersection(inventory_caps):

                caps = dict([(capname, self.region.capabilities[capname]) for capname in inventory_caps])

                log(INFO, "Using the capability based inventory management mechanism")

                self.inventory = AIS(self, caps)

            else:

                log(INFO, "Using the UDP based inventory management mechanism")

                self.inventory = UDP_Inventory(self)

            self.inventory._parse_folders_from_login_response()            
            self.inventory.enable_callbacks()

    def _enable_child_region(self, region_params):
        """ enables a child region. eligible simulators are sent in EnableSimulator over the event queue, and routed through the packet handler """

        # if this is the sim we are already connected to, skip it
        if self.region.sim_ip == region_params['IP'] and self.region.sim_port == region_params['Port']:
            #self.region.sendCompleteAgentMovement()
            log(DEBUG, "Not enabling a region we are already connected to: %s" % (str(region_params['IP']) + ":" + str(region_params['Port'])))
            return

        child_region = Region(circuit_code = self.circuit_code, sim_ip = region_params['IP'], sim_port = region_params['Port'], handle = region_params['Handle'], agent = self, settings = self.settings, event_queue_handler = self.event_queue_handler, events_handler = self.events_handler)

        self.child_regions.append(child_region)

        log(INFO, "Enabling a child region with ip:port of %s" % (str(region_params['IP']) + ":" + str(region_params['Port'])))

        if self.settings.LOG_COROUTINE_SPAWNS: log(INFO, "Spawning a coroutine for connecting to a neighboring region.")

        api.spawn(child_region.connect_child)

    def _monitor_for_new_regions(self):
        """ enable connections to neighboring regions found in the pending queue """

        while self.running:

            if len(self._pending_child_regions) > 0:

                for region_params in self._pending_child_regions:
                    
                    self._enable_child_region(region_params)
                    self._pending_child_regions.remove(region_params)

            api.sleep(0)

    def _start_EQ_on_neighboring_region(self, message):
        """ enables the event queue on an agent's neighboring region """

        region = [region for region in self.child_regions if message.sim_ip_and_port == str(region.sim_ip) + ":" + str(region.sim_port)]

        if region != []:

            region[0]._set_seed_capability(message.seed_capability_url)

            region[0]._get_region_capabilities()

            log(DEBUG, 'Spawning neighboring region event queue connection')
            region[0]._startEventQueue()

    def _enable_callbacks(self):
        """ enable the Agents() callback handlers for packet received events """

        if self.settings.ENABLE_INVENTORY_MANAGEMENT and self.inventory != None:
            self.inventory.enable_callbacks()

        if self.settings.ENABLE_GROUP_CHAT:
            self.group_manager = GroupManager(self, self.settings)

        if self.settings.MULTIPLE_SIM_CONNECTIONS:

            onEnableSimulator_received = self.event_queue_handler._register('EnableSimulator')
            onEnableSimulator_received.subscribe(self.onEnableSimulator)

            onEstablishAgentCommunication_received = self.event_queue_handler._register('EstablishAgentCommunication')
            onEstablishAgentCommunication_received.subscribe(self.onEstablishAgentCommunication)

        if self.settings.HANDLE_PACKETS:

            onAlertMessage_received = self.region.packet_handler._register('AlertMessage')
            onAlertMessage_received.subscribe(self.onAlertMessage)

            onAgentDataUpdate_received = self.region.packet_handler._register('AgentDataUpdate')
            onAgentDataUpdate_received.subscribe(self.onAgentDataUpdate)

            onAgentMovementComplete_received = self.region.packet_handler._register('AgentMovementComplete')
            onAgentMovementComplete_received.subscribe(self.onAgentMovementComplete)

            onHealthMessage_received = self.region.packet_handler._register('HealthMessage')
            onHealthMessage_received.subscribe(self.onHealthMessage)

            onImprovedInstantMessage_received = self.region.packet_handler._register('ImprovedInstantMessage')
            onImprovedInstantMessage_received.subscribe(self.onImprovedInstantMessage)

            if self.settings.ENABLE_COMMUNICATIONS_TRACKING:

                onChatFromSimulator_received = self.region.packet_handler._register('ChatFromSimulator')
                onChatFromSimulator_received.subscribe(self.helpers.log_packet, self)

    def send_AgentDataUpdateRequest(self):
        """ queues a packet requesting an agent data update """

        packet = AgentDataUpdateRequestPacket()

        packet.AgentData['AgentID'] = self.agent_id
        packet.AgentData['SessionID'] = self.session_id

        self.region.enqueue_message(packet())

    # ~~~~~~~~~~~~~~
    # Communications
    # ~~~~~~~~~~~~~~

    # Chat

    def say(self, Message, Type = 1, Channel = 0):
        """ queues a packet to send open chat via ChatFromViewer

        Channel: 0 is open chat
        Type: 0 = Whisper
              1 = Say
              2 = Shout
        """

        packet = ChatFromViewerPacket()

        packet.AgentData['AgentID'] = self.agent_id
        packet.AgentData['SessionID'] = self.session_id

        packet.ChatData['Message'] = Message + '\x00' # Message needs a terminator. Arnold was busy as gov...
        packet.ChatData['Type'] = Type
        packet.ChatData['Channel'] = Channel

        self.region.enqueue_message(packet())

    # Instant Message (im, group chat)

    def instant_message(self, ToAgentID = None, Message = None, _ID = None):
        """ sends an instant message to another avatar, wrapping Agent().send_ImprovedInstantMessage() with some handy defaults """

        if ToAgentID != None and Message != None:

            if _ID == None: _ID = self.agent_id

            _AgentID = self.agent_id
            _SessionID = self.session_id
            _FromGroup = False
            _ToAgentID = UUID(str(ToAgentID))
            _ParentEstateID = 0
            _RegionID = UUID()
            _Position = self.Position
            _Offline = 0
            _Dialog = ImprovedIMDialogue.FromAgent
            _ID = _ID
            _Timestamp = 0
            _FromAgentName = self.firstname + ' ' + self.lastname
            _Message = Message
            _BinaryBucket = ''

            self.send_ImprovedInstantMessage(_AgentID, _SessionID, _FromGroup, _ToAgentID, _ParentEstateID, _RegionID, _Position, _Offline, _Dialog, _ID, _Timestamp, _FromAgentName, _Message, _BinaryBucket)

        else:

            log(INFO, "Please specify an agentid and message to send in agent.instant_message")

    def send_ImprovedInstantMessage(self, AgentID = None, SessionID = None, FromGroup = None, ToAgentID = None, ParentEstateID = None, RegionID = None, Position = None, Offline = None, Dialog = None, _ID = None, Timestamp = None, FromAgentName = None, Message = None, BinaryBucket = None, AgentDataBlock = {}, MessageBlockBlock = {}):
        """ sends an instant message packet to ToAgentID. this is a multi-purpose message for inventory offer handling, im, group chat, and more """

        packet = ImprovedInstantMessagePacket()

        if AgentDataBlock == {}:
            packet.AgentData['AgentID'] = AgentID
            packet.AgentData['SessionID'] = SessionID            
        else:
            packet.AgentData = AgentDataBlock

        if FromAgentName == None:
            FromAgentName = self.Name()

        # ha! when scripting out packets.py, never considered a block named *block
        if MessageBlockBlock == {}:

            packet.MessageBlock['FromGroup'] = FromGroup                   # Bool
            packet.MessageBlock['ToAgentID'] = UUID(str(ToAgentID))   # LLUUID
            packet.MessageBlock['ParentEstateID'] = ParentEstateID         # U32
            packet.MessageBlock['RegionID'] = UUID(str(RegionID))     # LLUUID
            packet.MessageBlock['Position'] = Position()                     # LLVector3
            packet.MessageBlock['Offline'] = Offline                       # U8
            packet.MessageBlock['Dialog'] = Dialog                         # U8 IM Type
            packet.MessageBlock['ID'] = UUID(str(_ID))                # LLUUID
            packet.MessageBlock['Timestamp'] = Timestamp                   # U32
            packet.MessageBlock['FromAgentName'] = FromAgentName           # Variable 1
            packet.MessageBlock['Message'] = Message                       # Variable 2
            packet.MessageBlock['BinaryBucket'] = BinaryBucket             # Variable 2

        self.region.enqueue_message(packet(), True)

        def send_RetrieveInstantMessages(self):
            """ asks simulator for instant messages stored while agent was offline """

            packet = RetrieveInstantMessagesPackets()

            packet.AgentDataBlock['AgentID'] = self.agent_id
            packet.AgentDataBlock['SessionID'] = self.session_id

            self.region.enqueue_message(packet())

    def sigint_handler(self, signal, frame):
        """ catches terminal signals (Ctrl-C) to kill running client instances """

        log(INFO, "Caught signal... %d. Stopping" % signal)
        #self.running = False
        self.logout()
        #sys.exit(0)

    def __repr__(self):
        """ returns a representation of the agent """

        if self.firstname == None:
            return 'A new agent instance'
        else:
            return self.Name()

    def onAgentDataUpdate(self, packet):
        """ callback handler for received AgentDataUpdate messages which populates various Agent() attributes """

        if self.agent_id == None:
            self.agent_id = packet.message_data.blocks['AgentData'][0].get_variable('AgentID').data

        if self.firstname == None:
            self.firstname = packet.message_data.blocks['AgentData'][0].get_variable('FirstName').data

        if self.lastname == None:
            self.firstname = packet.message_data.blocks['AgentData'][0].get_variable('LastName').data

        self.GroupTitle = packet.message_data.blocks['AgentData'][0].get_variable('GroupTitle').data

        self.ActiveGroupID = packet.message_data.blocks['AgentData'][0].get_variable('ActiveGroupID').data

        self.GroupPowers = packet.message_data.blocks['AgentData'][0].get_variable('GroupPowers').data

        self.GroupName = packet.message_data.blocks['AgentData'][0].get_variable('GroupName').data

    def onAgentMovementComplete(self, packet):
        """ callback handler for received AgentMovementComplete messages which populates various Agent() and Region() attributes """

        self.Position = packet.message_data.blocks['Data'][0].get_variable('Position').data

        self.LookAt = packet.message_data.blocks['Data'][0].get_variable('LookAt').data

        self.region.RegionHandle = packet.message_data.blocks['Data'][0].get_variable('RegionHandle').data

        #agent.Timestamp = packet.message_data.blocks['Data'][0].get_variable('Timestamp')

        self.region.ChannelVersion = packet.message_data.blocks['SimData'][0].get_variable('ChannelVersion').data

    def onHealthMessage(self, packet):
        """ callback handler for received HealthMessage messages which populates Agent().health """

        self.health = packet.message_data.blocks['HealthData'][0].get_variable('Health').data

    def onAgentGroupDataUpdate(self, packet):
        """ callback handler for received AgentGroupDataUpdate messages which updates stored group instances in the group_manager """

        # AgentData block
        AgentID = packet.message_data.blocks['AgentData'][0].get_variable('AgentID').data

        # GroupData block
        for GroupData_block in packet.message_data.blocks['GroupData']:

            AcceptNotices = GroupData_block.get_variable('AcceptNotices').data
            GroupPowers = GroupData_block.get_variable('GroupPowers').data
            GroupID = GroupData_block.get_variable('GroupID').data
            GroupName = GroupData_block.get_variable('GroupName').data
            ListInProfile = GroupData_block.get_variable('ListInProfile').data
            Contribution = GroupData_block.get_variable('Contribution').data
            GroupInsigniaID = GroupData_block.get_variable('GroupInsigniaID').data

            # make sense of group powers
            GroupPowers = [ord(x) for x in GroupPowers]
            GroupPowers = ''.join([str(x) for x in GroupPowers])

            group = Group(AcceptNotices, GroupPowers, GroupID, GroupName, ListInProfile, Contribution,GroupInsigniaID )

            self.group_manager.store_group(group)

    def onChatFromSimulator(self, packet):
        """ callback handler for received ChatFromSimulator messages which parses and fires a ChatReceived event. (not implemented """

        # ToDo: implement firing an event when this is called

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

    def onImprovedInstantMessage(self, packet):
        """ callback handler for received ImprovedInstantMessage messages. much is passed in this message, and handling the data is only partially implemented """

        log(INFO, "Working on parsing ImprovedInstantMessage messages....")

        Dialog = packet.message_data.blocks['MessageBlock'][0].get_variable('Dialog').data
        FromAgentID = packet.message_data.blocks['AgentData'][0].get_variable('AgentID').data

        if Dialog == ImprovedIMDialogue.InventoryOffered:

            self.inventory.handle_inventory_offer(packet)

        elif Dialog == ImprovedIMDialogue.InventoryAccepted:

            if str(FromAgentID) != str(self.agent_id):

                FromAgentName = packet.message_data.blocks['MessageBlock'][0].get_variable('FromAgentName').data
                InventoryName = packet.message_data.blocks['MessageBlock'][0].get_variable('Message').data

                log(INFO, "Agent %s accepted the inventory offer." % (FromAgentName))

        elif Dialog == ImprovedIMDialogue.InventoryDeclined:

            if str(FromAgentID) != str(self.agent_id):

                FromAgentName = packet.message_data.blocks['MessageBlock'][0].get_variable('FromAgentName').data
                InventoryName = packet.message_data.blocks['MessageBlock'][0].get_variable('Message').data

                log(INFO, "Agent %s declined the inventory offer." % (FromAgentName))

        elif Dialog == ImprovedIMDialogue.FromAgent:

            RegionID = packet.message_data.blocks['MessageBlock'][0].get_variable('RegionID').data
            Position = packet.message_data.blocks['MessageBlock'][0].get_variable('Position').data
            ID = packet.message_data.blocks['MessageBlock'][0].get_variable('ID').data
            FromAgentName = packet.message_data.blocks['MessageBlock'][0].get_variable('FromAgentName').data
            Message = packet.message_data.blocks['MessageBlock'][0].get_variable('Message').data

            message = InstantMessageReceived(FromAgentID, RegionID, Position, ID, FromAgentName, Message)

            log(INFO, "Received instant message from %s: %s" % (FromAgentName, Message))

            self.events_handler._handle(message)

        else:

            self.helpers.log_packet(packet, self)

    def onAlertMessage(self, packet):
        """ callback handler for received AlertMessage messages. logs and raises an event """

        # ToDo: raise an event when this is received

        AlertMessage = packet.message_data.blocks['AlertData'][0].get_variable('Message').data

        log(WARNING, "AlertMessage from simulator: %s" % (AlertMessage))

    def onEnableSimulator(self, packet):
        """ callback handler for received EnableSimulator messages. stores the region data for later connections """

        IP = [ord(x) for x in packet.message_data.blocks['SimulatorInfo'][0].get_variable('IP').data]
        IP = '.'.join([str(x) for x in IP])

        Port = packet.message_data.blocks['SimulatorInfo'][0].get_variable('Port').data

        # not sure what this is, but pass it up
        Handle = [ord(x) for x in packet.message_data.blocks['SimulatorInfo'][0].get_variable('Handle').data]

        region_params = {'IP': IP, 'Port': Port, 'Handle': Handle}

        log(INFO, 'Received EnableSimulator for %s' % (str(IP) + ":" + str(Port)))

        # are we already prepping to connect to the sim?
        if region_params not in self._pending_child_regions:

            # are we already connected to the sim?
            known_region = False

            # don't append to the list if we already know about this region
            for region in self.child_regions:
                if region.sim_ip == region_params['IP'] and region.sim_port == region_params['Port']:
                    known_region = True

            #agent._enable_child_region(IP, Port, Handle)
            if not known_region:
                self._pending_child_regions.append(region_params)

    def onEstablishAgentCommunication(self, message):
        """ callback handler for received EstablishAgentCommunication messages. try to enable the event queue for a neighboring region based on the data received """

        log(INFO, 'Received EstablishAgentCommunication for %s' % (message.sim_ip_and_port))

        is_running = False

        # don't enable the event queue when we already have it running
        for region in self.child_regions:
            if (str(region.sim_ip) + ":" + str(region.sim_port) == message.sim_ip_and_port) and region.event_queue != None:
                if region.event_queue._running:
                    is_running = True

        # start the event queue
        if is_running == False:
            self._start_EQ_on_neighboring_region(message)

class Home(object):
    """ contains the parameters describing an agent's home location as returned in login_response['home'] """

    def __init__(self, params):
        """ initialize the Home object by parsing the data passed in """

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
