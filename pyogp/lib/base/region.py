"""
@file regiondomain.py
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

# std lib
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import re
from urllib import quote
from urlparse import urlparse, urljoin
import time
import uuid
import os

# related
from indra.base import llsd
from eventlet import api, coros

# pyogp
from pyogp.lib.base.caps import Capability, SeedCapability
from pyogp.lib.base.network.stdlib_client import StdLibClient, HTTPError
import pyogp.lib.base.exc
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.utilities.helpers import Helpers
from pyogp.lib.base.event_queue import EventQueueClient, EventQueueHandler
from pyogp.lib.base.objects import Objects

# messaging
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.circuit import Host
from pyogp.lib.base.message.packets import *
from pyogp.lib.base.message.packethandler import PacketHandler

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

    # ToDo: finish this

    Sample implementations: examples/sample_region_connect.py
    Tests: tests/region.txt, tests/test_region.py        

    """

    def __init__(self, global_x = 0, global_y = 0, seed_capability_url = None, udp_blacklist = None, sim_ip = None, sim_port = None, circuit_code = None, agent = None, settings = None, packet_handler = None, event_queue_handler = None):
        """ initialize a region """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        # allow the packet_handler to be passed in
        # otherwise, grab the defaults
        if packet_handler != None:
            self.packet_handler = packet_handler
        elif self.settings.HANDLE_PACKETS:
            self.packet_handler = PacketHandler()

        # allow the event_queue_handler to be passed in
        # otherwise, grab the defaults
        if event_queue_handler != None:
            self.event_queue_handler = event_queue_handler
        elif self.settings.HANDLE_EVENT_QUEUE_DATA:
            self.event_queue_handler = EventQueueHandler(settings = self.settings)

        # initialize the init params
        self.global_x = global_x
        self.global_y = global_y
        self.grid_x = self.global_x/256
        self.grid_y = self.global_y/256
        self.seed_capability_url = seed_capability_url
        self.udp_blacklist = udp_blacklist
        self.sim_ip = sim_ip
        self.sim_port = sim_port
        self.circuit_code = circuit_code
        self.agent = agent   # an agent object

        # UDP connection information
        if (self.sim_ip != None) and (self.sim_port != None):
            self.messenger = UDPDispatcher(settings = self.settings, packet_handler = self.packet_handler)
            self.host = Host((self.sim_ip,self.sim_port))
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

        if self.settings.ENABLE_OBJECT_TRACKING == True:
            self.objects = Objects(agent = self.agent, region = self, settings = self.settings, packet_handler = self.packet_handler)
        else:
            self.objects = None

        # required packet handlers
        onPacketAck_received = self.packet_handler._register('PacketAck')
        onPacketAck_received.subscribe(self.helpers.null_packet_handler, self)

        if self.settings.MULTIPLE_SIM_CONNECTIONS:

            onEnableSimulator_received = self.packet_handler._register('EnableSimulator')
            onEnableSimulator_received.subscribe(onEnableSimulator, self)

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

        #set up some callbacks
        if self.settings.HANDLE_PACKETS:
            pass

        if self.settings.LOG_VERBOSE: log(DEBUG, 'initializing region domain: %s' %self)

    def enable_child_simulator(self, IP, Port, Handle):

        log(INFO, "Would enable a simulator at %s:%s with a handle of %s" % (IP, Port, Handle))

    def send_message_next(self, packet, reliable = False):
        """ inserts this packet at the fron of the queue """

        # if the packet data type != UDPPacket, serialize it
        if str(type(packet)) != '<class \'pyogp.lib.base.message.packet.UDPPacket\'>':
            packet = packet()

        self.packet_queue.insert(0, (packet, reliable))

    def enqueue_message(self, packet, reliable = False):
        """ queues packets for the messaging system to send """

        # if the packet data type != UDPPacket, serialize it
        if str(type(packet)) != '<class \'pyogp.lib.base.message.message.Message\'>':
            packet = packet()

        self.packet_queue.append((packet, reliable))

    def send_message(self, packet, reliable = False):
        """ send a packet to the host """

        # if the packet data type != UDPPacket, serialize it
        if str(type(packet)) != '<class \'pyogp.lib.base.message.message.Message\'>':
            packet = packet()

        if self.host == None or self.messenger == None:
            raise RegionMessageError(self)
        else:
            if reliable == False:
                self.messenger.send_message(packet, self.host)
            else:
                self.messenger.send_reliable(packet, self.host, 0)

    def send_reliable(self, packet):
        """ send a reliable packet to the host """

        # if the packet data type != UDPPacket, serialize it
        if str(type(packet)) != '<class \'pyogp.lib.base.message.message.Message\'>':
            packet = packet()

        if self.host == None or self.messenger == None:
            raise RegionMessageError(self)
        else:
            self.messenger.send_reliable(packet, self.host, 0)

    def _set_seed_capability(self, url = None):

        if url != None:
            self.seed_capability_url = url
        self.seed_cap = RegionSeedCapability('seed_cap', self.seed_capability_url, settings = self.settings)

        if self.settings.ENABLE_CAPS_LOGGING: log(DEBUG, 'setting region domain seed cap: %s' % (self.seed_capability_url))

    def _get_region_public_seed(self, custom_headers={'Accept' : 'application/llsd+xml'}):
        """ call this capability, return the parsed result """

        if self.settings.ENABLE_CAPS_LOGGING: log(DEBUG, 'Getting region public_seed %s' %(self.region_uri))

        try:
            restclient = StdLibClient()
            response = restclient.GET(self.region_uri, custom_headers)
        except HTTPError, e:
            if e.code==404:
                raise exc.ResourceNotFound(self.region_uri)
            else:
                raise exc.ResourceError(self.region_uri, e.code, e.msg, e.fp.read(), method="GET")

        data = llsd.parse(response.body)

        if self.settings.ENABLE_CAPS_LOGGING: log(DEBUG, 'Get of cap %s response is: %s' % (self.region_uri, data))        

        return data

    def _get_region_capabilities(self):
        """ queries the region seed cap for capabilities """

        if (self.seed_cap == None):
            raise exc.RegionSeedCapNotAvailable("querying for agent capabilities")
            return
        else:

            if self.settings.ENABLE_CAPS_LOGGING: log(INFO, 'Getting caps from region seed cap %s' % (self.seed_cap))

            # use self.region_caps.keys() to pass a list to be parsed into LLSD            
            self.capabilities = self.seed_cap.get(self.region_caps_list, self.settings)

    def connect(self):
        """ connect to the udp circuit code and event queue"""

        # set up the seed capability
        self._set_seed_capability()

        # grab the agent's capabilities from the sim
        self._get_region_capabilities()

        # send the first few packets necessary to establish presence
        self._init_agent_in_region()

        self.last_ping = 0

        # spawn an eventlet api instance that runs the UDP connection
        log(DEBUG, 'Spawning region UDP connection')
        api.spawn(self._processUDP)

        # spawn an eventlet api instance that runs the event queue connection
        log(DEBUG, 'Spawning region event queue connection')
        self._startEventQueue()

        log(DEBUG, "Spawned region data connections")

    def logout(self):
        """ send a logout packet """

        log(INFO, "Disconnecting from region %s" % (self.SimName))

        try:
            # this should move to a handled method
            packet = LogoutRequestPacket()
            packet.AgentData['AgentID'] = uuid.UUID(self.agent.session_id)
            packet.AgentData['SessionID'] = uuid.UUID(self.agent.session_id)

            self.send_message(packet())

            self._isUDPRunning = False
            self._stopEventQueue()

            return True
        except:
            return False

    def _init_agent_in_region(self):
        """ send a few packets to set things up """

        # send the UseCircuitCode packet
        self.sendUseCircuitCode()

        # wait a sec, then send the rest
        time.sleep(1)

        # send the CompleteAgentMovement packet
        self.sendCompleteAgentMovement()

        # send a UUIDNameRequest packet
        #self.sendUUIDNameRequest()

        # send an AgentUpdate packet to complete the loop
        self.sendAgentUpdate()

    def sendUseCircuitCode(self):
        """ initializing on a simulator requires announcing the circuit code an agent will use """

        packet = UseCircuitCodePacket()

        packet.CircuitCode['Code'] = self.circuit_code
        packet.CircuitCode['SessionID'] = uuid.UUID(self.agent.session_id)
        packet.CircuitCode['ID'] = uuid.UUID(self.agent.agent_id)

        self.send_reliable(packet())

    def sendCompleteAgentMovement(self):
        """ initializing on a simulator requires sending CompleteAgentMovement, also required on teleport """

        packet = CompleteAgentMovementPacket()

        packet.AgentData['AgentID'] = uuid.UUID(self.agent.agent_id)
        packet.AgentData['SessionID'] = uuid.UUID(self.agent.session_id)
        packet.AgentData['CircuitCode'] = self.circuit_code

        self.send_reliable(packet())

    def sendUUIDNameRequest(self, agent_ids = []):
        """ sends a packet requesting the name corresponding to a UUID """

        packet = UUIDNameRequestPacket()

        if agent_ids == []:
            UUIDNameBlock = {}
            UUIDNameBlock['ID'] = uuid.UUID(self.agent.agent_id)
            packet.UUIDNameBlockBlocks.append(UUIDNameBlock)
        else:
            for agent_id in agent_ids:
                UUIDNameBlock = {}
                UUIDNameBlock['ID'] = uuid.UUID(uuid)
                packet.UUIDNameBlockBlocks.append(UUIDNameBlock)

        self.send_message(packet())

    def sendAgentUpdate(self, BodyRotation = (0.0,0.0,0.0,1.0), HeadRotation = (0.0,0.0,0.0,1.0), State = 0x00, CameraCenter = (0.0,0.0,0.0), CameraAtAxis = (0.0,0.0,0.0), CameraLeftAxis = (0.0,0.0,0.0), CameraUpAxis = (0.0,0.0,0.0), Far = 0, ControlFlags = 0x00, Flags = 0x00):
        """ sends an AgentUpdate packet """

        packet = AgentUpdatePacket()

        packet.AgentData['AgentID'] = uuid.UUID(str(self.agent.agent_id))
        packet.AgentData['SessionID'] = uuid.UUID(str(self.agent.session_id))

        # configurable data points
        packet.AgentData['BodyRotation'] = BodyRotation
        packet.AgentData['HeadRotation'] = HeadRotation
        packet.AgentData['State'] = State
        packet.AgentData['CameraCenter'] = CameraCenter
        packet.AgentData['CameraAtAxis'] = CameraAtAxis
        packet.AgentData['CameraLeftAxis'] = CameraLeftAxis
        packet.AgentData['CameraUpAxis'] = CameraUpAxis
        packet.AgentData['Far'] = Far
        packet.AgentData['ControlFlags'] = ControlFlags
        packet.AgentData['Flags'] = Flags

        self.send_message(packet())

    def sendRegionHandshakeReply(self):
        """ sends a RegionHandshake packet """

        packet = RegionHandshakeReplyPacket()
        packet.AgentData['SessionID'] = uuid.UUID(self.agent.session_id)    # MVT_LLUUID
        packet.AgentData['AgentID'] = uuid.UUID(self.agent.agent_id) 
        packet.RegionInfo['Flags'] = 0

        self.send_reliable(packet())

    def sendCompletePingCheck(self):
        """ sends a CompletePingCheck packet """

        packet = CompletePingCheckPacket()
        packet.PingID['PingID'] = self.last_ping

        self.send_message(packet())

        # we need to increment the last ping id
        self.last_ping += 1

    def _processUDP(self):
        """ check for packets and handle certain cases """

        self._isUDPRunning = True

        # the RegionHandshake packet requires a response
        onRegionHandshake_received = self.packet_handler._register('RegionHandshake')
        onRegionHandshake_received.subscribe(onRegionHandshake, self)

        # the StartPingCheck packet requires a response
        onStartPingCheck_received = self.packet_handler._register('StartPingCheck')
        onStartPingCheck_received.subscribe(onStartPingCheck, self)

        while self._isUDPRunning:

            # free up resources for other stuff to happen
            api.sleep(0)

            # check for new messages
            msg_buf, msg_size = self.messenger.udp_client.receive_packet(self.messenger.socket)
            self.messenger.receive_check(self.messenger.udp_client.get_sender(),
                                            msg_buf, msg_size)

            if self.messenger.has_unacked():

                self.messenger.process_acks()

                # pull the camera back a bit, 20m
                # we are currently facing east, so pull back on the x axis
                CameraCenter = (self.agent.Position.X - 20.0, self.agent.Position.Y, self.agent.Position.Z)
                self.sendAgentUpdate(CameraCenter = CameraCenter, CameraAtAxis = self.settings.DEFAULT_CAMERA_AT_AXIS, CameraLeftAxis = self.settings.DEFAULT_CAMERA_AT_AXIS, CameraUpAxis = self.settings.DEFAULT_CAMERA_UP_AXIS, Far = self.settings.DEFAULT_CAMERA_DRAW_DISTANCE)

            # send pending messages in the queue
            for (packet, reliable) in self.packet_queue:
                self.send_message(packet, reliable)
                self.packet_queue.remove((packet, reliable))

        log(DEBUG, "Stopped the UDP connection for %s" % (self.SimName))

    def _startEventQueue(self):
        """ polls the event queue capability and parses the results  """

        self.event_queue = EventQueueClient(self.capabilities['EventQueueGet'], settings = self.settings, packet_handler = self.packet_handler, region = self, event_queue_handler = self.event_queue_handler)
        api.spawn(self.event_queue.start)
        self._isEventQueueRunning = True

    def _stopEventQueue(self):
        """ shuts down the running event queue """

        if self._isEventQueueRunning == True and self.event_queue._running == True:
            self.event_queue.stop = True

def onRegionHandshake(packet, region):
    """ handles the response to receiving a RegionHandshake packet """

    # send the reply
    region.sendRegionHandshakeReply()

    # propagate the incoming data
    region.SimName = packet.message_data.blocks['RegionInfo'][0].get_variable('SimName')
    region.SimAccess = packet.message_data.blocks['RegionInfo'][0].get_variable('SimAccess')
    region.SimOwner = packet.message_data.blocks['RegionInfo'][0].get_variable('SimOwner')
    region.IsEstateManager = packet.message_data.blocks['RegionInfo'][0].get_variable('IsEstateManager')
    region.WaterHeight = packet.message_data.blocks['RegionInfo'][0].get_variable('WaterHeight')
    region.BillableFactor = packet.message_data.blocks['RegionInfo'][0].get_variable('BillableFactor')
    region.TerrainBase0 = packet.message_data.blocks['RegionInfo'][0].get_variable('TerrainBase0')
    region.TerrainBase1 = packet.message_data.blocks['RegionInfo'][0].get_variable('TerrainBase1')
    region.TerrainBase2 = packet.message_data.blocks['RegionInfo'][0].get_variable('TerrainBase2')
    region.TerrainStartHeight00 = packet.message_data.blocks['RegionInfo'][0].get_variable('TerrainStartHeight00')
    region.TerrainStartHeight01 = packet.message_data.blocks['RegionInfo'][0].get_variable('TerrainStartHeight01')
    region.TerrainStartHeight10 = packet.message_data.blocks['RegionInfo'][0].get_variable('TerrainStartHeight10')
    region.TerrainStartHeight11 = packet.message_data.blocks['RegionInfo'][0].get_variable('TerrainStartHeight11')
    region.TerrainHeightRange00 = packet.message_data.blocks['RegionInfo'][0].get_variable('TerrainHeightRange00')
    region.TerrainHeightRange01 = packet.message_data.blocks['RegionInfo'][0].get_variable('TerrainHeightRange01')
    region.TerrainHeightRange10 = packet.message_data.blocks['RegionInfo'][0].get_variable('TerrainHeightRange10')
    region.TerrainHeightRange11 = packet.message_data.blocks['RegionInfo'][0].get_variable('TerrainHeightRange11')
    region.CPUClassID = packet.message_data.blocks['RegionInfo3'][0].get_variable('CPUClassID')
    region.CPURatio = packet.message_data.blocks['RegionInfo3'][0].get_variable('CPURatio')
    region.ColoName = packet.message_data.blocks['RegionInfo3'][0].get_variable('ColoName')
    region.ProductSKU = packet.message_data.blocks['RegionInfo3'][0].get_variable('ProductSKU')
    region.ProductName = packet.message_data.blocks['RegionInfo3'][0].get_variable('ProductName')
    region.RegionID = packet.message_data.blocks['RegionInfo2'][0].get_variable('RegionID')

    # we are connected
    region.connected = True

    log(INFO, "Rezzed agent \'%s %s\' in region %s" % (region.agent.firstname, region.agent.lastname, region.SimName))

def onStartPingCheck(packet, region):
    """ sends the CompletePingCheck packet """

    region.sendCompletePingCheck()

def onEnableSimulator(packet, region):
    """ handler for the EnableSimulator packet sent over the event queue """

    IP = [ord(x) for x in packet.message_data.blocks['SimulatorInfo'][0].get_variable('IP').data]
    IP = '.'.join([str(x) for x in IP])

    Port = packet.message_data.blocks['SimulatorInfo'][0].get_variable('Port').data

    # not sure what this is, but pass it up
    Handle = [ord(x) for x in packet.message_data.blocks['SimulatorInfo'][0].get_variable('Handle').data]

    region.enable_child_simulator(IP, Port, Handle)

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
        if self.settings.ENABLE_CAPS_LOGGING: log(INFO, 'Request for caps returned: %s' % (parsed_result.keys()))

        caps = {}
        for name in names:
            # TODO: some caps might be seed caps, how do we know? 
            if parsed_result.has_key(name):
                caps[name]=Capability(name, parsed_result[name], settings = self.settings)
            else:
                if self.settings.ENABLE_CAPS_LOGGING: log(DEBUG, 'Requested capability \'%s\' is not available' %  (name))
            #log(INFO, 'got cap: %s' % (name))

        return caps

    def __repr__(self):
        return "<RegionSeedCapability for %s>" % (self.public_url)
