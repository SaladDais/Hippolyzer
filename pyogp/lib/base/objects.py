"""
@file object.py
@date 2009-03-03
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
import uuid

# related

# pyogp
from pyogp.lib.base.message.packet_handler import PacketHandler
from pyogp.lib.base.message.packets import *
from pyogp.lib.base.utilities.helpers import Helpers

# initialize logging
logger = getLogger('pyogp.lib.base.inventory')
log = logger.log

class Objects(object):
    """ is an Object Manager 

    Initialize the event queue client class
    >>> objects = Objects()

    Sample implementations: region.py
    Tests: tests/test_objects.py
    """

    def __init__(self, agent = None, region = None, settings = None, packet_handler = None):
        """ set up the inventory manager """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        self.agent = agent
        self.region = region

        # the object store consists of a list
        # of Object() instances
        self.object_store = []

        # other useful things
        self.helpers = Helpers()

        # set up callbacks
        if self.settings.HANDLE_PACKETS:
            if packet_handler != None:
                self.packet_handler = packet_handler
            else:
                self.packet_handler = PacketHandler()

            '''
            onObjectUpdateCached_log = self.packet_handler._register('ObjectUpdateCached')
            onObjectUpdateCached_log.subscribe(self.helpers.log_packet, self)     
            '''

            onObjectUpdate_received = self.packet_handler._register('ObjectUpdate')
            onObjectUpdate_received.subscribe(onObjectUpdate, self)

            onObjectUpdateCached_log = self.packet_handler._register('ObjectUpdateCached')
            onObjectUpdateCached_log.subscribe(onObjectUpdateCached, self)

        if self.settings.LOG_VERBOSE: log(INFO, "Initializing object storage")

    def store_object(self, _object):
        """ append to or replace an object in self.objects """

        # replace an existing list member, else, append

        try:

            index = [self.object_store.index(_object_) for _object_ in self.object_store if _object_.ID == _object.ID]

            self.object_store[index[0]] = _object

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Replacing a stored object: %s in region \'%s\'' % (_object.ID, self.region.SimName))

        except:

            self.object_store.append(_object)

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Stored a new object: %s in region \'%s\'' % (_object.ID, self.region.SimName))

    def get_object_from_store(self, ID = None, FullID = None):
        """ searches the store and returns object if stored, None otherwise """

        if ID != None:
            _object = [_object for _object in self.object_store if _object.ID == ID]
            return _object
        elif FullID != None:
            [_object for _object in self.object_store if _object.FullID == FullID]
            return _object
        else:
            return None

    def request_object_update(self, ID = None, ID_list = None):
        """ requests object updates from the simulator
        
        accepts a tuple of (ID, CacheMissType), or a list of such tuples
        """

        packet = RequestMultipleObjectsPacket()
        packet.AgentData['AgentID'] = uuid.UUID(self.agent.agent_id)
        packet.AgentData['SessionID'] = uuid.UUID(self.agent.session_id)

        if ID != None:

            ObjectData = {}
            ObjectData['CacheMissType'] = ID[0]
            ObjectData['ID'] = ID[1]
             
            packet.ObjectDataBlocks.append(ObjectData)

        else:

             for ID in ID_list:

                 ObjectData = {}
                 ObjectData['CacheMissType'] = ID[0]
                 ObjectData['ID'] = ID[1]

                 packet.ObjectDataBlocks.append(ObjectData)

        # enqueue the message, send as reliable
        self.region.enqueue_message(packet(), True)

class Object(object):
    """ represents an Object 

    Initialize the Object class instance
    >>> object = Object()

    Sample implementations: objects.py
    Tests: tests/test_objects.py
    """

    def __init__(self, ID = None, State = None, FullID = None, CRC = None, PCode = None, Material = None, ClickAction = None, Scale = None, ObjectData = None, ParentID = None, UpdateFlags = None, PathCurve = None, ProfileCurve = None, PathBegin = None, PathEnd = None, PathScaleX = None, PathScaleY = None, PathShearX = None, PathShearY = None, PathTwist = None, PathTwistBegin = None, PathRadiusOffset = None, PathTaperX = None, PathTaperY = None, PathRevolutions = None, PathSkew = None, ProfileBegin = None, ProfileEnd = None, ProfileHollow = None, TextureEntry = None, TextureAnim = None, NameValue = None, Data = None, Text = None, TextColor = None, MediaURL = None, PSBlock = None, ExtraParams = None, Sound = None, OwnerID = None, Gain = None, Flags = None, Radius = None, JointType = None, JointPivot = None, JointAxisOrAnchor = None):
        """ set up the event queue attributes """

        self.ID = ID                                 # U32
        self.State = State                           # U8
        self.FullID = uuid.UUID(str(FullID))         # LLUUID
        self.CRC = CRC                               # U32 // TEMPORARY HACK FOR JAMES
        self.PCode = PCode                           # U8
        self.Material = Material                     # U8
        self.ClickAction = ClickAction               # U8
        self.Scale = Scale                           # LLVector3
        self.ObjectData = ObjectData                 # Variable 1
        self.ParentID = ParentID                     # U32
        self.UpdateFlags = UpdateFlags               # U32 // U32, see object_flags.h
        self.PathCurve = PathCurve                   # U8
        self.ProfileCurve = ProfileCurve             # U8
        self.PathBegin = PathBegin                   # U16 // 0 to 1, quanta = 0.01
        self.PathEnd = PathEnd                       # U16 // 0 to 1, quanta = 0.01
        self.PathScaleX = PathScaleX                 # U8 // 0 to 1, quanta = 0.01
        self.PathScaleY = PathScaleY                 # U8 // 0 to 1, quanta = 0.01
        self.PathShearX = PathShearX                 # U8 // -.5 to .5, quanta = 0.01
        self.PathShearY = PathShearY                 # U8 // -.5 to .5, quanta = 0.01
        self.PathTwist = PathTwist                   # S8 // -1 to 1, quanta = 0.01
        self.PathTwistBegin = PathTwistBegin         # S8 // -1 to 1, quanta = 0.01
        self.PathRadiusOffset = PathRadiusOffset     # S8 // -1 to 1, quanta = 0.01
        self.PathTaperX = PathTaperX                 # S8 // -1 to 1, quanta = 0.01
        self.PathTaperY = PathTaperY                 # S8 // -1 to 1, quanta = 0.01
        self.PathRevolutions = PathRevolutions       # U8 // 0 to 3, quanta = 0.015
        self.PathSkew = PathSkew                     # S8 // -1 to 1, quanta = 0.01
        self.ProfileBegin = ProfileBegin             # U16 // 0 to 1, quanta = 0.01
        self.ProfileEnd = ProfileEnd                 # U16 // 0 to 1, quanta = 0.01
        self.ProfileHollow = ProfileHollow           # U16 // 0 to 1, quanta = 0.01
        self.TextureEntry = TextureEntry             # Variable 2
        self.TextureAnim = TextureAnim               # Variable 1
        self.NameValue = NameValue                   # Variable 2
        self.Data = Data                             # Variable 2
        self.Text = Text                             # Variable 1 // llSetText() hovering text
        self.TextColor = TextColor                   # Fixed 4 // actually, a LLColor4U
        self.MediaURL = MediaURL                     # Variable 1 // URL for web page, movie, etc.
        self.PSBlock = PSBlock                       # Variable 1
        self.ExtraParams = ExtraParams               # Variable 1
        self.Sound = uuid.UUID(str(Sound))           # LLUUID
        self.OwnerID = uuid.UUID(str(OwnerID))       # LLUUID // HACK object's owner id, only set if non-null sound, for muting
        self.Gain = Gain                             # F32
        self.Flags = Flags                           # U8
        self.Radius = Radius                         # F32 // cutoff radius
        self.JointType = JointType                   # U8
        self.JointPivot = JointPivot                 # LLVector3
        self.JointAxisOrAnchor = JointAxisOrAnchor   # LLVector3

def onObjectUpdate(packet, objects):
    """ populates an Object instance and adds it to the Objects() store """

    # ToDo: handle these 2 variables properly
    _RegionHandle = packet.message_data.blocks['RegionData'][0].get_variable('RegionHandle').data
    _TimeDilation = packet.message_data.blocks['RegionData'][0].get_variable('TimeDilation').data

    for ObjectData_block in packet.message_data.blocks['ObjectData']:

        _ID = ObjectData_block.get_variable('ID').data
        _State = ObjectData_block.get_variable('State').data
        _FullID = ObjectData_block.get_variable('FullID').data
        _CRC = ObjectData_block.get_variable('CRC').data
        _PCode = ObjectData_block.get_variable('PCode').data
        _Material = ObjectData_block.get_variable('Material').data
        _ClickAction = ObjectData_block.get_variable('ClickAction').data
        _Scale = ObjectData_block.get_variable('Scale').data
        _ObjectData = ObjectData_block.get_variable('ObjectData').data
        _ParentID = ObjectData_block.get_variable('ParentID').data
        _UpdateFlags = ObjectData_block.get_variable('UpdateFlags').data
        _PathCurve = ObjectData_block.get_variable('PathCurve').data
        _ProfileCurve = ObjectData_block.get_variable('ProfileCurve').data
        _PathBegin = ObjectData_block.get_variable('PathBegin').data
        _PathEnd = ObjectData_block.get_variable('PathEnd').data
        _PathScaleX = ObjectData_block.get_variable('PathScaleX').data
        _PathScaleY = ObjectData_block.get_variable('PathScaleY').data
        _PathShearX = ObjectData_block.get_variable('PathShearX').data
        _PathShearY = ObjectData_block.get_variable('PathShearY').data
        _PathTwist = ObjectData_block.get_variable('PathTwist').data
        _PathTwistBegin = ObjectData_block.get_variable('PathTwistBegin').data
        _PathRadiusOffset = ObjectData_block.get_variable('PathRadiusOffset').data
        _PathTaperX = ObjectData_block.get_variable('PathTaperX').data
        _PathTaperY = ObjectData_block.get_variable('PathTaperY').data
        _PathRevolutions = ObjectData_block.get_variable('PathRevolutions').data
        _PathSkew = ObjectData_block.get_variable('PathSkew').data
        _ProfileBegin = ObjectData_block.get_variable('ProfileBegin').data
        _ProfileEnd = ObjectData_block.get_variable('ProfileEnd').data
        _ProfileHollow = ObjectData_block.get_variable('ProfileHollow').data
        _TextureEntry = ObjectData_block.get_variable('TextureEntry').data
        _TextureAnim = ObjectData_block.get_variable('TextureAnim').data
        _NameValue = ObjectData_block.get_variable('NameValue').data
        _Data = ObjectData_block.get_variable('Data').data
        _Text = ObjectData_block.get_variable('Text').data
        _TextColor = ObjectData_block.get_variable('TextColor').data
        _MediaURL = ObjectData_block.get_variable('MediaURL').data
        _PSBlock = ObjectData_block.get_variable('PSBlock').data
        _ExtraParams = ObjectData_block.get_variable('ExtraParams').data
        _Sound = ObjectData_block.get_variable('Sound').data
        _OwnerID = ObjectData_block.get_variable('OwnerID').data
        _Gain = ObjectData_block.get_variable('Gain').data
        _Flags = ObjectData_block.get_variable('Flags').data
        _Radius = ObjectData_block.get_variable('Radius').data
        _JointType = ObjectData_block.get_variable('JointType').data
        _JointPivot = ObjectData_block.get_variable('JointPivot').data
        _JointAxisOrAnchor = ObjectData_block.get_variable('JointAxisOrAnchor').data

        _object = Object(_ID, _State, _FullID, _CRC, _PCode, _Material, _ClickAction, _Scale, _ObjectData, _ParentID, _UpdateFlags, _PathCurve, _ProfileCurve, _PathBegin, _PathEnd, _PathScaleX, _PathScaleY, _PathShearX, _PathShearY, _PathTwist, _PathTwistBegin, _PathRadiusOffset, _PathTaperX, _PathTaperY, _PathRevolutions, _PathSkew, _ProfileBegin, _ProfileEnd, _ProfileHollow, _TextureEntry, _TextureAnim, _NameValue, _Data, _Text, _TextColor, _MediaURL, _PSBlock, _ExtraParams, _Sound, _OwnerID, _Gain, _Flags, _Radius, _JointType, _JointPivot, _JointAxisOrAnchor)

        # add the object to the store
        objects.store_object(_object)

def onObjectUpdateCached(packet, objects):
    """ borrowing from libomv, we'll request object data for all data coming in via ObjectUpdateCached"""

    # ToDo: handle these 2 variables properly
    _RegionHandle = packet.message_data.blocks['RegionData'][0].get_variable('RegionHandle').data
    _TimeDilation = packet.message_data.blocks['RegionData'][0].get_variable('TimeDilation').data

    _request_list = []

    for ObjectData_block in packet.message_data.blocks['ObjectData']:

        _ID = ObjectData_block.get_variable('ID').data
        _CRC = ObjectData_block.get_variable('CRC').data
        _UpdateFlags = ObjectData_block.get_variable('UpdateFlags').data        

        # Objects.request_object_update() expects a tuple of (_ID, CacheMissType)

        # see if we have the object stored already
        _object = objects.get_object_from_store(ID = _ID)

        if _object == None or _object == []:
            CacheMissType = 1
        else:
            print _object[0]
            CacheMissType = 0

        _request_list.append((_ID, CacheMissType))

    # ask the simulator for updates
    objects.request_object_update(ID_list = _request_list)
