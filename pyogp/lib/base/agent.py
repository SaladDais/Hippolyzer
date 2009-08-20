
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
import sys
import signal
import sets
import struct

#related
from eventlet import api

# pyogp
from pyogp.lib.base.login import Login, LegacyLoginParams, OGPLoginParams
from pyogp.lib.base.datatypes import  Quaternion, Vector3, UUID
from pyogp.lib.base.exc import LoginError
from pyogp.lib.base.region import Region
from pyogp.lib.base.inventory import AIS, UDP_Inventory
from pyogp.lib.base.groups import GroupManager, Group
from pyogp.lib.base.event_system import AppEventsHandler, AppEvent
from pyogp.lib.base.appearance import AppearanceManager
from pyogp.lib.base.assets import AssetManager

# pyogp messaging
from pyogp.lib.base.message.message import Message, Block

# pyogp utilities
from pyogp.lib.base.utilities.helpers import Helpers
from pyogp.lib.base.utilities.enums import ImprovedIMDialogue, MoneyTransactionType, TransactionFlags, AgentState, AgentUpdateFlags, AgentControlFlags

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

    def __init__(self, settings = None, firstname = '', lastname = '', password = '', agent_id = None, events_handler = None, handle_signals=True):
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
            self.events_handler = AppEventsHandler()

        # signal handler to capture erm signals
        if handle_signals:
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
        self.active_group_powers = None
        self.active_group_name = None
        self.active_group_title = None
        self.active_group_id = None
        self.health = None
        self._login_params = None
        self.circuit_code = None

        # other storage containers
        self.inventory_host = None
        self.agent_access = None
        self.udp_blacklist = None
        self.home = None
        self.inventory = None
        self.start_location = None
        self.group_manager = GroupManager(self, self.settings)
        self.asset_manager = AssetManager(self, self.settings)

        # additional attributes
        self.login_response = None
        self.connected = False
        self.grid_type = None
        self.running = True
        self.helpers = Helpers()

        # data we store as it comes in from the grid
        self.Position = Vector3()     # this will get updated later, but seed it with 000
        self.LookAt = Vector3()
        self.ActiveGroupID = UUID()

        # populated via ObjectUpdates
        self.FootCollisionPlane = Quaternion() 
        self.Velocity = Vector3()
        self.Acceleration = Vector3()
        self.Rotation = Vector3()
        self.AngularVelocity = Vector3()

        # movement
        self.state = AgentState.Null # typing, editing
        self.control_flags = 0
        self.agent_update_flags = AgentUpdateFlags.Null


        # should we include these here?
        self.agentdomain = None     # the agent domain the agent is connected to if an OGP context
        self.child_regions = []     # all neighboring regions
        self._pending_child_regions = []    # neighbor regions an agent may connect to
        self.region = None          # the host simulation for the agent

        # init AppearanceManager()
        self.appearance = AppearanceManager(self, self.settings)

        # Cache of region name->handle; per-agent to prevent information leaks
        self.region_name_map = {}

        # Cache of agent_id->(first_name, last_name); per agent to prevent info leaks
        self.agent_id_map = {}

        if self.settings.LOG_VERBOSE: 
            log(DEBUG, 'Initializing agent: %s' % (self))

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

                self._login_params = self._get_login_params(self.firstname, self.lastname, self.password)

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
            [region.kill_coroutines() for region in self.child_regions]

            if self.region.logout():
                self.connected = False

        # zero out the password in case we dump it somewhere
        self.password = ''

    def _get_login_params(self, firstname, lastname, password):
        """ get the proper login parameters of the legacy or ogp enabled grid """

        if self.grid_type == 'OGP':

            login_params = OGPLoginParams(firstname, lastname, password)

        elif self.grid_type == 'Legacy':

            login_params = LegacyLoginParams(firstname, lastname, password)

        return login_params

    def _parse_login_response(self):
        """ evaluates the login response and propagates data to the Agent() attributes. enables InventoryManager() if settings dictate """

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
            self.start_location = self.login_response['start_location']

            if self.login_response.has_key('home'): 
                self.home = Home(self.login_response['home'])

        elif self.grid_type == 'OGP':

            pass

    def _enable_current_region(self, region_x = None, region_y = None, seed_capability = None, udp_blacklist = None, sim_ip = None, sim_port = None, circuit_code = None):
        """ enables and connects udp and event queue for an agent's current region """

        if self.login_response.has_key('circuit_code'):
            self.circuit_code = self.login_response['circuit_code']

        region_x = region_x or self.login_response['region_x']
        region_y = region_y or self.login_response['region_y']
        seed_capability = seed_capability or self.login_response['seed_capability']
        udp_blacklist = udp_blacklist or self.login_response['udp_blacklist']
        sim_ip = sim_ip or self.login_response['sim_ip']
        sim_port = sim_port or self.login_response['sim_port']
        circuit_code = circuit_code or self.login_response['circuit_code']

        # enable the current region, setting connect = True
        self.region = Region(region_x, region_y, seed_capability, udp_blacklist, sim_ip, sim_port, circuit_code, self, settings = self.settings, events_handler = self.events_handler)

        self.region.is_host_region = True        

        # start the simulator udp and event queue connections
        if self.settings.LOG_COROUTINE_SPAWNS: 
            log(INFO, "Spawning a coroutine for connecting to the agent's host region.")

        api.spawn(self.region.connect)

        self.enable_callbacks()



    def _enable_child_region(self, region_params):
        """ enables a child region. eligible simulators are sent in EnableSimulator over the event queue, and routed through the packet handler """

        # if this is the sim we are already connected to, skip it
        if self.region.sim_ip == region_params['IP'] and self.region.sim_port == region_params['Port']:
            #self.region.sendCompleteAgentMovement()
            log(DEBUG, "Not enabling a region we are already connected to: %s" % (str(region_params['IP']) + ":" + str(region_params['Port'])))
            return

        child_region = Region(circuit_code = self.circuit_code, 
                            sim_ip = region_params['IP'], 
                            sim_port = region_params['Port'], 
                            handle = region_params['Handle'], 
                            agent = self, 
                            settings = self.settings, 
                            events_handler = self.events_handler)

        self.child_regions.append(child_region)

        log(INFO, "Enabling a child region with ip:port of %s" % (str(region_params['IP']) + ":" + str(region_params['Port'])))

        if self.settings.LOG_COROUTINE_SPAWNS: 
            log(INFO, "Spawning a coroutine for connecting to a neighboring region.")

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

        region = [region for region in self.child_regions if message.blocks['Message_Data'][0].get_variable('sim-ip-and-port').data == str(region.sim_ip) + ":" + str(region.sim_port)]

        if region != []:

            region[0]._set_seed_capability(message.blocks['Message_Data'][0].get_variable('seed-capability').data)

            region[0]._get_region_capabilities()

            log(DEBUG, 'Spawning neighboring region event queue connection')
            region[0]._startEventQueue()

    def enable_callbacks(self):
        """ enable the Agents() callback handlers for packet received events """
        # TODO oopify

        if self.settings.ENABLE_INVENTORY_MANAGEMENT:
            while self.region.capabilities == {}:

                api.sleep(0)

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

        if self.settings.ENABLE_APPEARANCE_MANAGEMENT:
            self.appearance.enable_callbacks()
        if self.settings.ENABLE_GROUP_CHAT:
            self.group_manager.enable_callbacks()
        if self.settings.MULTIPLE_SIM_CONNECTIONS:

            onEnableSimulator_received = self.region.message_handler.register('EnableSimulator')
            onEnableSimulator_received.subscribe(self.onEnableSimulator)

            onEstablishAgentCommunication_received = self.region.message_handler.register('EstablishAgentCommunication')
            onEstablishAgentCommunication_received.subscribe(self.onEstablishAgentCommunication)

        if self.settings.HANDLE_PACKETS:

            onAlertMessage_received = self.region.message_handler.register('AlertMessage')
            onAlertMessage_received.subscribe(self.onAlertMessage)

            onAgentDataUpdate_received = self.region.message_handler.register('AgentDataUpdate')
            onAgentDataUpdate_received.subscribe(self.onAgentDataUpdate)

            onAgentMovementComplete_received = self.region.message_handler.register('AgentMovementComplete')
            onAgentMovementComplete_received.subscribe(self.onAgentMovementComplete)

            onHealthMessage_received = self.region.message_handler.register('HealthMessage')
            onHealthMessage_received.subscribe(self.onHealthMessage)

            onImprovedInstantMessage_received = self.region.message_handler.register('ImprovedInstantMessage')
            onImprovedInstantMessage_received.subscribe(self.onImprovedInstantMessage)

            self.region.message_handler.register('TeleportStart').subscribe(self.simple_callback('Info'))
            self.region.message_handler.register('TeleportProgress').subscribe(self.simple_callback('Info'))
            self.region.message_handler.register('TeleportFailed').subscribe(self.simple_callback('Info'))
            self.region.message_handler.register('TeleportFinish').subscribe(self.onTeleportFinish)

            self.region.message_handler.register('OfflineNotification').subscribe(self.simple_callback('AgentBlock'))
            self.region.message_handler.register('OnlineNotification').subscribe(self.simple_callback('AgentBlock'))

            self.region.message_handler.register('MoneyBalanceReply').subscribe(self.simple_callback('MoneyData'))
            self.region.message_handler.register('RoutedMoneyBalanceReply').subscribe(self.simple_callback('MoneyData'))

            if self.settings.ENABLE_COMMUNICATIONS_TRACKING:
                onChatFromSimulator_received = self.region.message_handler.register('ChatFromSimulator')
                onChatFromSimulator_received.subscribe(self.onChatFromSimulator)


    def simple_callback(self, blockname):
        """Generic callback creator for single-block packets."""

        def repack(packet, blockname):
            """Repack a single block packet into an AppEvent"""
            payload = {}
            block = packet.blocks[blockname][0]
            for var in block.var_list:
                payload[var] = block.get_variable(var).data

            return AppEvent(packet.name, payload=payload)

        return lambda p: self.events_handler.handle(repack(p, blockname))


    def send_AgentDataUpdateRequest(self):
        """ queues a packet requesting an agent data update """

        packet = Message('AgentDataUpdateRequest', 
                        Block('AgentData', 
                            AgentID = self.agent_id, 
                            SessionID = self.session_id))

        self.region.enqueue_message(packet)

    # ~~~~~~~~~~~~~~
    # Communications
    # ~~~~~~~~~~~~~~

    # Chat

    def say(self, 
            _Message, 
            Type = 1, 
            Channel = 0):
        """ queues a packet to send open chat via ChatFromViewer

        Channel: 0 is open chat
        Type: 0 = Whisper
              1 = Say
              2 = Shout
        """

        packet = Message('ChatFromViewer', 
                        Block('AgentData', 
                            AgentID = self.agent_id, 
                            SessionID = self.session_id), 
                        Block('ChatData', 
                            Message = _Message, 
                            Type = Type, 
                            Channel = Channel))

        self.region.enqueue_message(packet)

    # Instant Message (im, group chat)

    def instant_message(self, 
                        ToAgentID = None, 
                        _Message = None, 
                        _ID = None):
        """ sends an instant message to another avatar, wrapping Agent().send_ImprovedInstantMessage() with some handy defaults """

        if ToAgentID != None and _Message != None:

            if _ID == None: 
                _ID = self.agent_id

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
            _Message = _Message
            _BinaryBucket = ''

            self.send_ImprovedInstantMessage(_AgentID, 
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

        else:

            log(INFO, "Please specify an agentid and message to send in agent.instant_message")

    def send_ImprovedInstantMessage(self, 
                                    AgentID = None, 
                                    SessionID = None, 
                                    FromGroup = None, 
                                    ToAgentID = None, 
                                    ParentEstateID = None, 
                                    RegionID = None, 
                                    Position = None, 
                                    Offline = None, 
                                    Dialog = None, 
                                    _ID = None, 
                                    Timestamp = None, 
                                    FromAgentName = None, 
                                    _Message = None, 
                                    BinaryBucket = None):
        """ sends an instant message packet to ToAgentID. this is a multi-purpose message for inventory offer handling, im, group chat, and more """

        packet = Message('ImprovedInstantMessage', 
                        Block('AgentData', 
                            AgentID = AgentID, 
                            SessionID = SessionID), 
                        Block('MessageBlock', 
                            FromGroup = FromGroup, 
                            ToAgentID = ToAgentID, 
                            ParentEstateID = ParentEstateID, 
                            RegionID = RegionID, 
                            Position = Position, 
                            Offline = Offline, 
                            Dialog = Dialog, 
                            ID = UUID(str(_ID)), 
                            Timestamp = Timestamp, 
                            FromAgentName = FromAgentName, 
                            Message = _Message, 
                            BinaryBucket = BinaryBucket))

        self.region.enqueue_message(packet, True)

    def send_RetrieveInstantMessages(self):
        """ asks simulator for instant messages stored while agent was offline """

        packet = Message('RetrieveInstantMessages', 
                        Block('AgentData', 
                            AgentID = self.agent_id, 
                            SessionID = self.session_id))

        self.region.enqueue_message(packet())


    def sigint_handler(self, signal_sent, frame):
        """ catches terminal signals (Ctrl-C) to kill running client instances """

        log(INFO, "Caught signal... %d. Stopping" % signal_sent)
        self.logout()

    def __repr__(self):
        """ returns a representation of the agent """

        if self.firstname == None:
            return 'A new agent instance'
        else:
            return self.Name()

    def onAgentDataUpdate(self, packet):
        """ callback handler for received AgentDataUpdate messages which populates various Agent() attributes """

        if self.agent_id == None:
            self.agent_id = packet.blocks['AgentData'][0].get_variable('AgentID').data

        if self.firstname == None:
            self.firstname = packet.blocks['AgentData'][0].get_variable('FirstName').data

        if self.lastname == None:
            self.firstname = packet.blocks['AgentData'][0].get_variable('LastName').data

        self.active_group_title = packet.blocks['AgentData'][0].get_variable('GroupTitle').data

        self.active_group_id = packet.blocks['AgentData'][0].get_variable('ActiveGroupID').data

        self.active_group_powers = packet.blocks['AgentData'][0].get_variable('GroupPowers').data

        self.active_group_name = packet.blocks['AgentData'][0].get_variable('GroupName').data

    def onAgentMovementComplete(self, packet):
        """ callback handler for received AgentMovementComplete messages which populates various Agent() and Region() attributes """

        self.Position = packet.blocks['Data'][0].get_variable('Position').data
        if self.Position == None:
            log(WARNING, "agent.position is None agent.py")
        self.LookAt = packet.blocks['Data'][0].get_variable('LookAt').data

        self.region.RegionHandle = packet.blocks['Data'][0].get_variable('RegionHandle').data

        #agent.Timestamp = packet.blocks['Data'][0].get_variable('Timestamp')

        self.region.ChannelVersion = packet.blocks['SimData'][0].get_variable('ChannelVersion').data

        # Raise a plain-vanilla AppEvent
        self.simple_callback('Data')(packet)

    def sendDynamicsUpdate(self):
        """Called when an ObjectUpdate is received for the agent; raises
        an app event."""
        payload = {}
        payload['Position'] = self.Position
        payload['FootCollisionPlane'] = self.FootCollisionPlane
        payload['Velocity'] = self.Velocity
        payload['Acceleration'] = self.Acceleration
        payload['Rotation'] = self.Rotation
        payload['AngularVelocity'] = self.AngularVelocity
        self.events_handler.handle(AppEvent("AgentDynamicsUpdate", payload=payload))

    def onHealthMessage(self, packet):
        """ callback handler for received HealthMessage messages which populates Agent().health """

        self.health = packet.blocks['HealthData'][0].get_variable('Health').data

    def onAgentGroupDataUpdate(self, packet):
        """ callback handler for received AgentGroupDataUpdate messages which updates stored group instances in the group_manager """

        # AgentData block
        # AgentID = packet.blocks['AgentData'][0].get_variable('AgentID').data

        # GroupData block
        for GroupData_block in packet.blocks['GroupData']:

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

            group = Group(AcceptNotices, GroupPowers, GroupID, GroupName, ListInProfile, Contribution, GroupInsigniaID )

            self.group_manager.store_group(group)

    def onChatFromSimulator(self, packet):
        """ callback handler for received ChatFromSimulator messages which parses and fires a ChatReceived event. """

        FromName = packet.blocks['ChatData'][0].get_variable('FromName').data
        SourceID = packet.blocks['ChatData'][0].get_variable('SourceID').data
        OwnerID = packet.blocks['ChatData'][0].get_variable('OwnerID').data
        SourceType = packet.blocks['ChatData'][0].get_variable('SourceType').data
        ChatType = packet.blocks['ChatData'][0].get_variable('ChatType').data
        Audible = packet.blocks['ChatData'][0].get_variable('Audible').data
        Position = packet.blocks['ChatData'][0].get_variable('Position').data
        _Message = packet.blocks['ChatData'][0].get_variable('Message').data 

        message = AppEvent('ChatReceived', 
                            FromName = FromName, 
                            SourceID = SourceID, 
                            OwnerID = OwnerID, 
                            SourceType = SourceType, 
                            ChatType = ChatType, 
                            Audible = Audible, 
                            Position = Position, 
                            Message = _Message)

        log(INFO, "Received chat from %s: %s" % (FromName, _Message))

        self.events_handler.handle(message)

    def onImprovedInstantMessage(self, packet):
        """ callback handler for received ImprovedInstantMessage messages. much is passed in this message, and handling the data is only partially implemented """

        Dialog = packet.blocks['MessageBlock'][0].get_variable('Dialog').data
        FromAgentID = packet.blocks['AgentData'][0].get_variable('AgentID').data

        if Dialog == ImprovedIMDialogue.InventoryOffered:

            self.inventory.handle_inventory_offer(packet)

        elif Dialog == ImprovedIMDialogue.InventoryAccepted:

            if str(FromAgentID) != str(self.agent_id):

                FromAgentName = packet.blocks['MessageBlock'][0].get_variable('FromAgentName').data
                InventoryName = packet.blocks['MessageBlock'][0].get_variable('Message').data

                log(INFO, "Agent %s accepted the inventory offer." % (FromAgentName))

        elif Dialog == ImprovedIMDialogue.InventoryDeclined:

            if str(FromAgentID) != str(self.agent_id):

                FromAgentName = packet.blocks['MessageBlock'][0].get_variable('FromAgentName').data
                InventoryName = packet.blocks['MessageBlock'][0].get_variable('Message').data

                log(INFO, "Agent %s declined the inventory offer." % (FromAgentName))

        elif Dialog == ImprovedIMDialogue.FromAgent:

            RegionID = packet.blocks['MessageBlock'][0].get_variable('RegionID').data
            Position = packet.blocks['MessageBlock'][0].get_variable('Position').data
            ID = packet.blocks['MessageBlock'][0].get_variable('ID').data
            FromAgentName = packet.blocks['MessageBlock'][0].get_variable('FromAgentName').data
            _Message = packet.blocks['MessageBlock'][0].get_variable('Message').data

            message = AppEvent('InstantMessageReceived', FromAgentID = FromAgentID, RegionID = RegionID, Position = Position, ID = ID, FromAgentName = FromAgentName, Message = _Message)

            log(INFO, "Received instant message from %s: %s" % (FromAgentName, _Message))

            self.events_handler.handle(message)

        else:

            self.helpers.log_packet(packet, self)

    def onAlertMessage(self, packet):
        """ callback handler for received AlertMessage messages. logs and raises an event """

        AlertMessage = packet.blocks['AlertData'][0].get_variable('Message').data

        message = AppEvent('AlertMessage', AlertMessage = AlertMessage)

        log(WARNING, "AlertMessage from simulator: %s" % (AlertMessage))

        self.events_handler.handle(message)

    def onEnableSimulator(self, packet):
        """ callback handler for received EnableSimulator messages. stores the region data for later connections """

        IP = [ord(x) for x in packet.blocks['SimulatorInfo'][0].get_variable('IP').data]
        IP = '.'.join([str(x) for x in IP])

        Port = packet.blocks['SimulatorInfo'][0].get_variable('Port').data

        # not sure what this is, but pass it up
        Handle = [ord(x) for x in packet.blocks['SimulatorInfo'][0].get_variable('Handle').data]

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

        log(INFO, 'Received EstablishAgentCommunication for %s' % (message.blocks['Message_Data'][0].get_variable('sim-ip-and-port').data))

        is_running = False

        # don't enable the event queue when we already have it running
        for region in self.child_regions:
            if (str(region.sim_ip) + ":" + str(region.sim_port) == message.blocks['Message_Data'][0].get_variable('sim-ip-and-port').data) and region.event_queue != None:
                if region.event_queue._running:
                    is_running = True

        # start the event queue
        if not is_running:
            self._start_EQ_on_neighboring_region(message)


    def teleport(self,
                 region_name=None,
                 region_handle=None,
                 region_id=None,
                 position=Vector3(X=128, Y=128, Z=128),
                 look_at=Vector3(X=128, Y=128, Z=128)):
        """Initiate a teleport to the specified location. When passing a region name
        it may be necessary to request the destination region handle from the current sim
        before the teleport can start."""

        log(INFO, 'teleport name=%s handle=%s id=%s', str(region_name), str(region_handle), str(region_id))

        # Handle intra-region teleports even by name
        if not region_id and region_name and region_name.lower() == self.region.SimName.lower():
            region_id = self.region.RegionID

        if not region_id and not region_handle and region_name and \
               region_name.lower() in self.region_name_map:
            region_handle = self.region_name_map[region_name.lower()]

        if region_id:

            log(INFO, 'sending TP request packet')

            packet = Message('TeleportRequest', 
                            Block('AgentData', 
                                AgentID = self.agent_id, 
                                SessionID = self.session_id),
                            Block('Info',
                                RegionID = region_id,
                                Position = position,
                                LookAt = look_at))

            self.region.enqueue_message(packet)

        elif region_handle:

            log(INFO, 'sending TP location request packet')

            packet = Message('TeleportLocationRequest', 
                            Block('AgentData', 
                                AgentID = self.agent_id, 
                                SessionID = self.session_id),
                            Block('Info',
                                RegionHandle = region_handle,
                                Position = position,
                                LookAt = look_at))

            self.region.enqueue_message(packet)

        else:
            log(INFO, "Target region's handle not known, sending map name request")
            # do a region_name to region_id lookup and then request the teleport
            self.send_MapNameRequest(
                region_name,
                lambda handle: self.teleport(region_handle=handle, position=position, look_at=look_at))


    def send_MapNameRequest(self, region_name, callback):
        """ sends a MapNameRequest message to the host simulator """

        handler = self.region.message_handler.register('MapBlockReply')

        def onMapBlockReplyPacket(packet):
            """ handles the MapBlockReply message from a simulator """

            log(INFO, 'MapBlockReplyPacket received')

            for block in packet.blocks['Data']:

                if block.get_variable('Name').data.lower() == region_name.lower():

                    handler.unsubscribe(onMapBlockReplyPacket)

                    x = block.get_variable('X').data
                    y = block.get_variable('Y').data
                    region_handle = Region.xy_to_handle(x, y)

                    if region_handle:
                        self.region_name_map[region_name.lower()] = region_handle
                        callback(region_handle)
                    else:
                        # *TODO: May get a region_handle of 0 if region
                        # is offline/unknown. Should callback handle it?
                        log(WARNING, 'Got null region_handle for %s', region_name)
                    return

            # Leave it registered, as the event may come later

        # Register a handler for the response        
        handler.subscribe(onMapBlockReplyPacket)

        # ...and make the request
        log(INFO, 'sending MapNameRequestPacket')

        packet = Message('MapNameRequest', 
                        Block('AgentData', 
                            AgentID = self.agent_id, 
                            SessionID = self.session_id,
                            Flags = 0,
                            EstateID = 0,
                            Godlike = False),
                        Block('NameData',
                            Name = region_name.lower()))

        self.region.enqueue_message(packet) 

    def onTeleportFinish(self, packet):
        """Handle the end of a successful teleport"""

        log(INFO, "Teleport finished, taking care of details...")

        # Raise a plain-vanilla AppEvent for the Info block
        self.simple_callback('Info')(packet)

        # packed binary U64 to integral x, y
        region_handle = packet.blocks['Info'][0].get_variable('RegionHandle').data        
        region_x, region_y = Region.handle_to_xy(region_handle) 

        # packed binary to dotted-octet
        sim_ip = packet.blocks['Info'][0].get_variable('SimIP').data
        sim_ip = '.'.join(map(str, struct.unpack('BBBB', sim_ip))) 

        # *TODO: Make this more graceful
        log(INFO, "Disconnecting from old region")
        [region.kill_coroutines() for region in self.child_regions]
        self.region.kill_coroutines()

        self.region = None
        self.child_regions = []
        self._pending_child_regions = []

        log(INFO, "Enabling new region")
        self._enable_current_region(
            region_x = region_x,
            region_y = region_y,
            seed_capability = packet.blocks['Info'][0].get_variable('SeedCapability').data,
            sim_ip = sim_ip,
            sim_port = packet.blocks['Info'][0].get_variable('SimPort').data
            )

    def request_agent_names(self, agent_ids, callback):
        """Request agent names. When all names are known, callback
        will be called with a list of tuples (agent_id, first_name,
        last_name). If all names are known, callback will be called
        immediately."""

        def _fire_callback(_):
            cbdata = [(agent_id,
                       self.agent_id_map[agent_id][0],
                       self.agent_id_map[agent_id][1])
                      for agent_id in agent_ids]
            callback(cbdata)

        names_to_request = [ agent_id
                             for agent_id in agent_ids
                             if agent_id not in self.agent_id_map ]
        if names_to_request:
            self.send_UUIDNameRequest(names_to_request, _fire_callback)
        else:
            _fire_callback([])            


    def send_UUIDNameRequest(self, agent_ids, callback):
        """ sends a UUIDNameRequest message to the host simulator """

        handler = self.region.message_handler.register('UUIDNameReply')

        def onUUIDNameReply(packet):
            """ handles the UUIDNameReply message from a simulator """
            log(INFO, 'UUIDNameReplyPacket received')

            cbdata = []
            for block in packet.blocks['UUIDNameBlock']:
                agent_id = str(block.get_variable('ID').data)
                first_name = block.get_variable('FirstName').data
                last_name = block.get_variable('LastName').data
                self.agent_id_map[agent_id] = (first_name, last_name)
                cbdata.append((agent_id, first_name, last_name))

            # Fire the callback only when all names are received
            missing = [ agent_id
                        for agent_id in agent_ids
                        if agent_id not in self.agent_id_map ]
            if not missing:
                handler.unsubscribe(onUUIDNameReply)
                callback(cbdata)
            else:
                log(INFO, 'Still waiting on %d names in send_UUIDNameRequest', len(missing))

        handler.subscribe(onUUIDNameReply)

        log(INFO, 'sending UUIDNameRequest')

        packet = Message('UUIDNameRequest', 
                        [Block('UUIDNameBlock', ID = UUID(agent_id)) for agent_id in agent_ids])

        self.region.enqueue_message(packet)

        # *TODO: Should use this instead, but somehow it fails ?!?
        #self.region.sendUUIDNameRequest(agent_ids=agent_ids)

    def request_balance(self, callback):
        """Request the current agent balance."""
        handler = self.region.message_handler.register('MoneyBalanceReply')

        def onMoneyBalanceReply(packet):
            """ handles the MoneyBalanceReply message from a simulator """
            log(INFO, 'MoneyBalanceReply received')
            handler.unsubscribe(onMoneyBalanceReply) # One-shot handler
            balance = packet.blocks['MoneyData'][0].get_variable('MoneyBalance').data
            callback(balance)

        handler.subscribe(onMoneyBalanceReply)

        log(INFO, 'sending MoneyBalanceRequest')

        packet = Message('MoneyBalanceRequest',
                        Block('AgentData',
                            AgentID = self.agent_id,
                            SessionID = self.session_id),
                        Block('MoneyData',
                            TransactionID = UUID()))

        self.region.enqueue_message(packet)

    def give_money(self, target_id, amount,
                   description='',
                   transaction_type=MoneyTransactionType.Gift,
                   flags=TransactionFlags.Null):
        """Give money to another agent"""

        log(INFO, 'sending MoneyTransferRequest')

        packet = Message('MoneyTransferRequest',
                        Block('AgentData',
                            AgentID = self.agent_id,
                            SessionID = self.session_id),
                        Block('MoneyData',
                            SourceID = self.agent_id,
                            DestID = UUID(target_id),
                            Flags = flags,
                            Amount = amount,
                            AggregatePermNextOwner = 0,
                            AggregatePermInventory = 0,
                            TransactionType = transaction_type,
                            Description = description))

        self.region.enqueue_message(packet) 

    def sit_on_ground(self):
        """Sit on the ground at the agent's current location"""

        self.control_flags |= AgentControlFlags.SitOnGround
        self._send_update()

    def stand(self):
        """Stand up from sitting"""

        # Start standing...
        self.control_flags &= ~AgentControlFlags.SitOnGround
        self.control_flags |= AgentControlFlags.StandUp
        self._send_update()

        # And finish standing
        self.control_flags &= ~AgentControlFlags.StandUp
        self._send_update()


    def fly(self, flying=True):
        """Start or stop flying"""

        if flying:
            self.control_flags |= AgentControlFlags.Fly
        else:            
            self.control_flags &= ~AgentControlFlags.Fly

        self._send_update()

    def _send_update(self):
        """ force a send of an AgentUpdate message to the host simulator """

        log(INFO, 'sending AgentUpdate')

        self.region.sendAgentUpdate(self.agent_id, self.session_id,
            State=self.state,
            ControlFlags=self.control_flags,
            Flags=self.agent_update_flags,

            CameraAtAxis = self.settings.DEFAULT_CAMERA_AT_AXIS,
            CameraLeftAxis = self.settings.DEFAULT_CAMERA_LEFT_AXIS,
            CameraUpAxis = self.settings.DEFAULT_CAMERA_UP_AXIS,
            Far = self.settings.DEFAULT_CAMERA_DRAW_DISTANCE
            )


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

        # convert the position and lookat to a Vector3 instance
        self.look_at = Vector3(X=self.look_at[0], Y=self.look_at[1], Z=self.look_at[2])
        self.position = Vector3(X=self.position[0], Y=self.position[1], Z=self.position[2])


