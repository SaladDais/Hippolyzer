
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

# std lib
from logging import getLogger, ERROR, INFO, DEBUG
import time

# related
from indra.base import llsd
from eventlet import api

# pyogp
from pyogp.lib.base.caps import Capability
from pyogp.lib.base.network.stdlib_client import StdLibClient, HTTPError
from pyogp.lib.base.exc import ResourceNotFound, ResourceError, RegionSeedCapNotAvailable, RegionMessageError
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.utilities.helpers import Helpers
from pyogp.lib.base.event_queue import EventQueueClient
from pyogp.lib.base.objects import ObjectManager
from pyogp.lib.base.datatypes import UUID
from pyogp.lib.base.event_system import AppEventsHandler
from pyogp.lib.base.parcel import ParcelManager

# messaging
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.circuit import Host
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.message_handler import MessageHandler

# utilities
from pyogp.lib.base.utilities.helpers import Wait

# initialize logging
logger = getLogger('pyogp.lib.base.region')
log = logger.log

class Region(object):
    """ a region container

    The Region class is a container for region specific data.
    It is also a nice place for convenience code.

    Example, of initializing a region class:

    Initialize the login class
    
    >>> region = Region(256, 256, 'https://somesim.cap/uuid', 'EnableSimulator,TeleportFinish,CrossedRegion', '127.0.0.1', 13000, 650000000, {'agent_id':'00000000-0000-0000-0000-000000000000', 'session_id':'00000000-0000-0000-0000-000000000000', 'secure_session_id:'00000000-0000-0000-0000-000000000000'})

    Start the udp and event queue connections to the region
    
    >>> region.connect()

    Sample implementations: examples/sample_region_connect.py
    Tests: tests/region.txt, tests/test_region.py        

    """

    def __init__(self, global_x = 0, global_y = 0, seed_capability_url = None, udp_blacklist = None, sim_ip = None, sim_port = None, circuit_code = None, agent = None, settings = None, message_handler = None, handle = None, events_handler = None):
        """ initialize a region """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            self.settings = Settings()

        # allow the packet_handler to be passed in
        # otherwise, grab the defaults
        if message_handler != None:
            self.message_handler = message_handler
        #elif self.settings.HANDLE_PACKETS:
        else:
            self.message_handler = MessageHandler()
        
        # allow the eventhandler to be passed in
        # so that applications running multiple avatars
        # may use the same eventhandler

        # otherwise, let's just use our own
        if events_handler != None:
            self.events_handler = events_handler
        else:
            self.events_handler = AppEventsHandler()

        # initialize the init params
        self.global_x = int(global_x)
        self.global_y = int(global_y)
        self.grid_x = self.global_x/256
        self.grid_y = self.global_y/256
        self.seed_capability_url = seed_capability_url
        self.udp_blacklist = udp_blacklist
        self.sim_ip = sim_ip
        self.sim_port = sim_port
        self.circuit_code = circuit_code
        self.agent = agent   # an agent object
        self.handle = handle
        self.is_host_region = False

        # UDP connection information
        if (self.sim_ip != None) and (self.sim_port != None):
            self.messenger = UDPDispatcher(settings = self.settings, message_handler = self.message_handler, region = self)
            self.host = Host((self.sim_ip, self.sim_port))
        else:
            self.host = None

        # other attributes
        self.RegionHandle = None    # from AgentMovementComplete
        self.SimName = None
        self.seed_capability = None
        self.capabilities = {}
        self.event_queue = None
        self.connected = False
        self.helpers = Helpers()

        self._isUDPRunning = False
        self._isEventQueueRunning = False

        # data storage containers
        self.packet_queue = []

        self.objects = ObjectManager(agent = self.agent, region = self, settings = self.settings, message_handler = self.message_handler, events_handler = self.events_handler)
        
        self.parcel_manager = ParcelManager(agent = self.agent, region = self, settings = self.settings, message_handler = self.message_handler, events_handler = self.events_handler)
        

        # required packet handlers
        onPacketAck_received = self.message_handler.register('PacketAck')
        onPacketAck_received.subscribe(self.helpers.null_packet_handler, self)

        # data we need
        self.region_caps_list = ['ChatSessionRequest',
                            'CopyInventoryFromNotecard',
                            'DispatchRegionInfo',
                            'EstateChangeInfo',
                            'EventQueueGet',
                            'FetchInventory',
                            'WebFetchInventoryDescendents',
                            'FetchLib',
                            'FetchLibDescendents',
                            'GroupProposalBallot',
                            'HomeLocation',
                            'MapLayer',
                            'MapLayerGod',
                            'NewFileAgentInventory',
                            'ParcelPropertiesUpdate',
                            'ParcelVoiceInfoRequest',
                            'ProvisionVoiceAccountRequest',
                            'RemoteParcelRequest',
                            'RequestTextureDownload',
                            'SearchStatRequest',
                            'SearchStatTracking',
                            'SendPostcard',
                            'SendUserReport',
                            'SendUserReportWithScreenshot',
                            'ServerReleaseNotes',
                            'StartGroupProposal',
                            'UpdateAgentLanguage',
                            'UpdateGestureAgentInventory',
                            'UpdateNotecardAgentInventory',
                            'UpdateScriptAgent',
                            'UpdateGestureTaskInventory',
                            'UpdateNotecardTaskInventory',
                            'UpdateScriptTask',
                            'ViewerStartAuction',
                            'UntrustedSimulatorMessage',
                            'ViewerStats'
        ]
        if self.settings.LOG_VERBOSE:
            log(DEBUG, 'initializing region domain: %s' %self)

    def enable_callbacks(self):
        '''enables the callback handles for this Region'''

        if self.settings.ENABLE_OBJECT_TRACKING:
            self.objects.enable_callbacks()
        if self.settings.ENABLE_PARCEL_TRACKING:
            self.parcel_manager.enable_callbacks()
            
        if self.settings.HANDLE_PACKETS:
            pass

    def enable_child_simulator(self, IP, Port, Handle):

        log(INFO, "Would enable a simulator at %s:%s with a handle of %s" % (IP, Port, Handle))

    def send_message_next(self, packet, reliable = False):
        """ inserts this packet at the fron of the queue """

        #if str(type(packet)) != '<class \'pyogp.lib.base.message.message.Message\'>':
            #packet = packet()

        self.packet_queue.insert(0, (packet, reliable))

    def enqueue_message(self, packet, reliable = False):
        """ queues packets for the messaging system to send """

        #if str(type(packet)) != '<class \'pyogp.lib.base.message.message.Message\'>':
            #packet = packet()

        self.packet_queue.append((packet, reliable))

    def send_message(self, packet, reliable = False):
        """ send a packet to the host """

        #if str(type(packet)) != '<class \'pyogp.lib.base.message.message.Message\'>':
            #packet = packet()

        if self.host == None or self.messenger == None:
            raise RegionMessageError(self)
        else:
            if reliable == False:
                self.messenger.send_message(packet, self.host)
            else:
                self.messenger.send_reliable(packet, self.host, 0)

    def send_reliable(self, packet):
        """ send a reliable packet to the host """

        #if str(type(packet)) != '<class \'pyogp.lib.base.message.message.Message\'>':
            #packet = packet()

        if self.host == None or self.messenger == None:
            raise RegionMessageError(self)
        else:
            self.messenger.send_reliable(packet, self.host, 0)

    def _set_seed_capability(self, url = None):
        """ sets the seed_cap attribute as a RegionSeedCapability instance """

        if url != None:
            self.seed_capability_url = url
        self.seed_cap = RegionSeedCapability('seed_cap', self.seed_capability_url, settings = self.settings)

        if self.settings.LOG_VERBOSE:
            log(DEBUG, 'setting region domain seed cap: %s' % (self.seed_capability_url))

    def _get_region_public_seed(self, custom_headers={'Accept' : 'application/llsd+xml'}):
        """ call this capability, return the parsed result """

        if self.settings.ENABLE_CAPS_LOGGING:
            log(DEBUG, 'Getting region public_seed %s' %(self.region_uri))

        try:
            restclient = StdLibClient()
            response = restclient.GET(self.region_uri, custom_headers)
        except HTTPError, e:
            if e.code == 404:
                raise ResourceNotFound(self.region_uri)
            else:
                raise ResourceError(self.region_uri, e.code, e.msg, e.fp.read(), method="GET")

        data = llsd.parse(response.body)

        if self.settings.ENABLE_CAPS_LOGGING:
            log(DEBUG, 'Get of cap %s response is: %s' % (self.region_uri, data))        

        return data

    def _get_region_capabilities(self):
        """ queries the region seed cap for capabilities """

        if (self.seed_cap == None):
            raise RegionSeedCapNotAvailable("querying for agent capabilities")
        else:

            if self.settings.ENABLE_CAPS_LOGGING:
                log(INFO, 'Getting caps from region seed cap %s' % (self.seed_cap))

            # use self.region_caps.keys() to pass a list to be parsed into LLSD            
            self.capabilities = self.seed_cap.get(self.region_caps_list, self.settings)

    def connect(self):
        """ connect to the udp circuit code and event queue"""
        self.enable_callbacks()
        # if this is the agent's host region, spawn the event queue
        # spawn an eventlet api instance that runs the event queue connection
        if self.seed_capability_url != None:

            # set up the seed capability
            self._set_seed_capability()

            # grab the agent's capabilities from the sim
            self._get_region_capabilities()

            log(DEBUG, 'Spawning region event queue connection')
            self._startEventQueue()


        # send the first few packets necessary to establish presence
        self._init_agent_in_region()

        self.last_ping = 0

        # spawn an eventlet api instance that runs the UDP connection
        log(DEBUG, 'Spawning region UDP connection')
        if self.settings.LOG_COROUTINE_SPAWNS:
            log(INFO, "Spawning a coroutine for udp connection to the agent's host region %s" % (str(self.sim_ip) + ":" + str(self.sim_port)))
        api.spawn(self._processUDP)

        log(DEBUG, "Spawned region data connections")

    def connect_child(self):
        """ connect to the a child region udp circuit code """

        # send the UseCircuitCode packet
        self.sendUseCircuitCode(self.circuit_code, self.agent.session_id, self.agent.agent_id)

        self.last_ping = 0

        # spawn an eventlet api instance that runs the UDP connection
        log(DEBUG, 'Spawning region UDP connection for child region %s' % (str(self.sim_ip) + ":" + str(self.sim_port)))

        if self.settings.LOG_COROUTINE_SPAWNS:
            log(INFO, "Spawning a coroutine for udp connection to the agent's child region %s" % (str(self.sim_ip) + ":" + str(self.sim_port)))

        api.spawn(self._processUDP)

    def logout(self):
        """ send a logout packet """

        log(INFO, "Disconnecting from region %s" % (self.SimName))

        try:

            self.send_LogoutRequest(self.agent.agent_id, self.agent.session_id)

            # ToDo: We should parse a response packet prior to really disconnecting
            Wait(1)

            self._isUDPRunning = False
            self._stopEventQueue()

            return True
        except Exception, error:
            log(ERROR, "Error logging out from region.")
            return False

    def send_LogoutRequest(self, agent_id, session_id):
        """ send a LogoutRequest message to the host simulator """

        packet = Message('LogoutRequest',
                        Block('AgentData',
                                AgentID = agent_id,
                                SessionID = session_id))

        self.send_message(packet)

    def kill_coroutines(self):
        """ trigger to end processes spawned by the child regions """

        self._isUDPRunning = False
        self._stopEventQueue()

    def _init_agent_in_region(self):
        """ send a few packets to set things up """

        # send the UseCircuitCode packet
        self.sendUseCircuitCode(self.circuit_code, self.agent.session_id, self.agent.agent_id)

        # wait a sec, then send the rest
        time.sleep(1)

        # send the CompleteAgentMovement packet
        self.sendCompleteAgentMovement(self.agent.agent_id, self.agent.session_id, self.circuit_code)

        # send a UUIDNameRequest packet
        #self.sendUUIDNameRequest()

        # send an AgentUpdate packet to complete the loop
        self.sendAgentUpdate(self.agent.agent_id, self.agent.session_id)

    def sendUseCircuitCode(self, circuit_code, session_id, agent_id):
        """ initializing on a simulator requires announcing the circuit code an agent will use """

        packet = Message('UseCircuitCode',
                        Block('CircuitCode',
                                Code = circuit_code,
                                SessionID = session_id,
                                ID = agent_id))

        self.send_reliable(packet)

    def sendCompleteAgentMovement(self, agent_id, session_id, circuit_code):
        """ initializing on a simulator requires sending CompleteAgentMovement, also required on teleport """

        packet = Message('CompleteAgentMovement',
                        Block('AgentData',
                                AgentID = agent_id,
                                SessionID = session_id,
                                CircuitCode = circuit_code))

        self.send_reliable(packet)

    def sendUUIDNameRequest(self, agent_ids = []):
        """ sends a packet requesting the name corresponding to a UUID """

        packet = Message('UUIDNameRequest',
                        *[Block('UUIDNameBlock',
                                ID = agent_id) for agent_id in agent_ids])

        self.send_message(packet)

    def sendAgentUpdate(self,
                        AgentID,
                        SessionID,
                        BodyRotation = (0.0,0.0,0.0,1.0),
                        HeadRotation = (0.0,0.0,0.0,1.0),
                        State = 0x00,
                        CameraCenter = (0.0,0.0,0.0),
                        CameraAtAxis = (0.0,0.0,0.0),
                        CameraLeftAxis = (0.0,0.0,0.0),
                        CameraUpAxis = (0.0,0.0,0.0),
                        Far = 0,
                        ControlFlags = 0x00,
                        Flags = 0x00):
        """ sends an AgentUpdate packet to *this* simulator"""

        packet = Message('AgentUpdate',
                        Block('AgentData',
                                AgentID = AgentID,
                                SessionID = SessionID,
                                BodyRotation = BodyRotation,
                                HeadRotation = HeadRotation,
                                State = State,
                                CameraCenter = CameraCenter,
                                CameraAtAxis = CameraAtAxis,
                                CameraLeftAxis = CameraLeftAxis,
                                CameraUpAxis = CameraUpAxis,
                                Far = Far,
                                ControlFlags = ControlFlags,
                                Flags = Flags))

        self.send_message(packet)

    def sendRegionHandshakeReply(self, AgentID, SessionID, Flags = 00):
        """ sends a RegionHandshake packet """

        packet = Message('RegionHandshakeReply',
                        Block('AgentData',
                                AgentID = AgentID,
                                SessionID = SessionID),
                        Block('RegionInfo',
                                Flags = Flags))

        self.send_reliable(packet)

    def sendCompletePingCheck(self, PingID):
        """ sends a CompletePingCheck packet """

        packet = Message('CompletePingCheck',
                        Block('PingID',
                                PingID = PingID))

        self.send_message(packet)

        # we need to increment the last ping id
        self.last_ping += 1

    def _processUDP(self):
        """ check for packets and handle certain cases """

        self._isUDPRunning = True

        # the RegionHandshake packet requires a response
        onRegionHandshake_received = self.message_handler.register('RegionHandshake')
        onRegionHandshake_received.subscribe(self.onRegionHandshake)

        # the StartPingCheck packet requires a response
        onStartPingCheck_received = self.message_handler.register('StartPingCheck')
        onStartPingCheck_received.subscribe(self.onStartPingCheck)

        while self._isUDPRunning:

            # free up resources for other stuff to happen
            api.sleep(0)

            # check for new messages
            msg_buf, msg_size = self.messenger.udp_client.receive_packet(self.messenger.socket)
            self.messenger.receive_check(self.messenger.udp_client.get_sender(),
                                            msg_buf, msg_size)

            if self.messenger.has_unacked():

                self.messenger.process_acks()

                # if this region is the host region, send agent updates
                if self.is_host_region:
                # pull the camera back a bit, 20m
                # we are currently facing east, so pull back on the x axis
                    CameraCenter = (self.agent.Position.X - 20.0, self.agent.Position.Y, self.agent.Position.Z)

                    self.sendAgentUpdate(self.agent.agent_id, self.agent.session_id, CameraCenter = CameraCenter, CameraAtAxis = self.settings.DEFAULT_CAMERA_AT_AXIS, CameraLeftAxis = self.settings.DEFAULT_CAMERA_AT_AXIS, CameraUpAxis = self.settings.DEFAULT_CAMERA_UP_AXIS, Far = self.settings.DEFAULT_CAMERA_DRAW_DISTANCE)

            # send pending messages in the queue
            for (packet, reliable) in self.packet_queue:
                self.send_message(packet, reliable)
                self.packet_queue.remove((packet, reliable))

        log(DEBUG, "Stopped the UDP connection for %s" % (self.SimName))

    def _startEventQueue(self):
        """ polls the event queue capability and parses the results  """

        self.event_queue = EventQueueClient(self.capabilities['EventQueueGet'], settings = self.settings, message_handler = self.message_handler, region = self)

        api.spawn(self.event_queue.start)

        self._isEventQueueRunning = True

    def _stopEventQueue(self):
        """ shuts down the running event queue """

        if self._isEventQueueRunning == True and self.event_queue._running == True:
            self.event_queue.stop()

    def onRegionHandshake(self, packet):
        """ handles the response to receiving a RegionHandshake packet """

        # send the reply
        self.sendRegionHandshakeReply(self.agent.agent_id, self.agent.session_id)

        # propagate the incoming data
        self.SimName = packet.blocks['RegionInfo'][0].get_variable('SimName').data
        self.SimAccess = packet.blocks['RegionInfo'][0].get_variable('SimAccess').data
        self.SimOwner = packet.blocks['RegionInfo'][0].get_variable('SimOwner').data
        self.IsEstateManager = packet.blocks['RegionInfo'][0].get_variable('IsEstateManager').data
        self.WaterHeight = packet.blocks['RegionInfo'][0].get_variable('WaterHeight').data
        self.BillableFactor = packet.blocks['RegionInfo'][0].get_variable('BillableFactor').data
        self.TerrainBase0 = packet.blocks['RegionInfo'][0].get_variable('TerrainBase0').data
        self.TerrainBase1 = packet.blocks['RegionInfo'][0].get_variable('TerrainBase1').data
        self.TerrainBase2 = packet.blocks['RegionInfo'][0].get_variable('TerrainBase2').data
        self.TerrainStartHeight00 = packet.blocks['RegionInfo'][0].get_variable('TerrainStartHeight00').data
        self.TerrainStartHeight01 = packet.blocks['RegionInfo'][0].get_variable('TerrainStartHeight01').data
        self.TerrainStartHeight10 = packet.blocks['RegionInfo'][0].get_variable('TerrainStartHeight10').data
        self.TerrainStartHeight11 = packet.blocks['RegionInfo'][0].get_variable('TerrainStartHeight11').data
        self.TerrainHeightRange00 = packet.blocks['RegionInfo'][0].get_variable('TerrainHeightRange00').data
        self.TerrainHeightRange01 = packet.blocks['RegionInfo'][0].get_variable('TerrainHeightRange01').data
        self.TerrainHeightRange10 = packet.blocks['RegionInfo'][0].get_variable('TerrainHeightRange10').data
        self.TerrainHeightRange11 = packet.blocks['RegionInfo'][0].get_variable('TerrainHeightRange11').data
        self.CPUClassID = packet.blocks['RegionInfo3'][0].get_variable('CPUClassID').data
        self.CPURatio = packet.blocks['RegionInfo3'][0].get_variable('CPURatio').data
        self.ColoName = packet.blocks['RegionInfo3'][0].get_variable('ColoName').data
        self.ProductSKU = packet.blocks['RegionInfo3'][0].get_variable('ProductSKU').data
        self.ProductName = packet.blocks['RegionInfo3'][0].get_variable('ProductName').data
        self.RegionID = packet.blocks['RegionInfo2'][0].get_variable('RegionID').data

        # we are connected
        self.connected = True

        log(INFO, "Connected agent \'%s %s\' to region %s" % (self.agent.firstname, self.agent.lastname, self.SimName))

    def onStartPingCheck(self, packet):
        """ sends the CompletePingCheck packet """

        self.sendCompletePingCheck(self.last_ping)

    @staticmethod
    def xy_to_handle(x, y):
        """Convert an x, y region location into a 64-bit handle"""
        return (int(x)*256 << 32) + int(y)*256

    @staticmethod
    def handle_to_xy(handle):
        """Convert a handle into an x,y region location. Handle can be an int or binary string."""
        import struct
        if isinstance(handle, str):
            handle =  struct.unpack('Q', handle)[0]
            
        x = int((handle >> 32)/256)
        y = int((handle & 0xffffffff)/256)
        return x, y


class RegionSeedCapability(Capability):
    """ a seed capability which is able to retrieve other capabilities """

    def get(self, names=[], settings = None):
        """if this is a seed cap we can retrieve other caps here"""

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        #log(INFO, 'requesting from the region domain the following caps: %s' % (names))

        payload = names
        parsed_result = self.POST(payload)  #['caps']
        if self.settings.ENABLE_CAPS_LOGGING:
            log(INFO, 'Request for caps returned: %s' % (parsed_result.keys()))

        caps = {}
        for name in names:
            # TODO: some caps might be seed caps, how do we know? 
            if parsed_result.has_key(name):
                caps[name] = Capability(name, parsed_result[name], settings = self.settings)
            else:
                if self.settings.ENABLE_CAPS_LOGGING:
                    log(DEBUG, 'Requested capability \'%s\' is not available' %  (name))
            #log(INFO, 'got cap: %s' % (name))

        return caps

    def __repr__(self):
        return "<RegionSeedCapability for %s>" % (self.public_url)



