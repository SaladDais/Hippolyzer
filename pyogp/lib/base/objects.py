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
import re
from binascii import b2a_base64

# related

# pyogp

# pyogp message
from pyogp.lib.base. message.packethandler import PacketHandler
from pyogp.lib.base.message.packets import *

# pyogp utilities
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

        # the avatar store consists of a list
        # of Avatar() instances
        # ToDo: should this go here, or be separate?
        self.avatar_store = []

        # other useful things
        self.helpers = Helpers()

        # set up callbacks
        if self.settings.HANDLE_PACKETS:
            if packet_handler != None:
                self.packet_handler = packet_handler
            else:
                self.packet_handler = PacketHandler()

            onObjectUpdate_received = self.packet_handler._register('ObjectUpdate')
            onObjectUpdate_received.subscribe(onObjectUpdate, self)

            onObjectUpdateCached_received = self.packet_handler._register('ObjectUpdateCached')
            onObjectUpdateCached_received.subscribe(onObjectUpdateCached, self)

            onObjectUpdateCompressed_received= self.packet_handler._register('ObjectUpdateCompressed')
            onObjectUpdateCompressed_received.subscribe(onObjectUpdateCompressed, self)

            onKillObject_received= self.packet_handler._register('KillObject')
            onKillObject_received.subscribe(onKillObject, self)


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

    def get_object_from_store(self, ID = None, FullID = None, Name = None):
        """ searches the store and returns object if stored, None otherwise """

        if ID != None:
            _object = [_object for _object in self.object_store if _object.ID == ID]
            return _object
        elif FullID != None:
            [_object for _object in self.object_store if _object.FullID == FullID]
            return _object
        else:
            return None

    def find_objects_by_name(self, Name):
        """ searches the store for known objects by name 
        
        returns a list of all such known objects
        """

        pattern = re.compile(Name)

        matches = [_object for _object in self.object_store if pattern.match(_object.NameValue)]

        return matches

    def remove_object_from_store(self, ID = None):
        """ removes an item from teh object store """

        self.object_store.remove(ID)

        if self.LOG_VERBOSE: log(DEBUG, "Deleted a killed object from the store")

    def request_object_update(self, ID = None, ID_list = None):
        """ requests object updates from the simulator

        accepts a tuple of (ID, CacheMissType), or a list of such tuples
        """

        packet = RequestMultipleObjectsPacket()
        packet.AgentData['AgentID'] = uuid.UUID(self.agent.agent_id)
        packet.AgentData['SessionID'] = uuid.UUID(self.agent.session_id)

        if ID != None:

            ObjectData = {}
            ObjectData['CacheMissType'] = ID[1]
            ObjectData['ID'] = ID[0]

            packet.ObjectDataBlocks.append(ObjectData)

        else:

            for ID in ID_list:

                ObjectData = {}
                ObjectData['CacheMissType'] = ID[1]
                ObjectData['ID'] = ID[0]

                packet.ObjectDataBlocks.append(ObjectData)

        # enqueue the message, send as reliable
        self.region.enqueue_message(packet(), True)

    def create_default_box(self, GroupID = uuid.UUID('00000000-0000-0000-0000-000000000000'), relative_position = (1, 0, 0)):
        """ creates the default box, defaulting as 1m to the east, with an option GroupID to set the prim to"""

        # self.agent.Position holds where we are. we need to add this tuple to the incoming tuple (vector to a vector)
        location_to_rez_x = self.agent.Position[0] + relative_position[0]
        location_to_rez_y = self.agent.Position[1] + relative_position[1]
        location_to_rez_z = self.agent.Position[2] + relative_position[2]

        location_to_rez = (location_to_rez_x, location_to_rez_y, location_to_rez_z)

        # not sure what RayTargetID is, send as uuid of zeros
        RayTargetID = uuid.UUID('00000000-0000-0000-0000-000000000000')

        self.object_add(GroupID = GroupID, PCode = 9, Material = 3, AddFlags = 2, PathCurve = 16, ProfileCurve = 1, PathBegin = 0, PathEnd = 0, PathScaleX = 100, PathScaleY = 100, PathShearX = 0, PathShearY = 0, PathTwist = 0, PathTwistBegin = 0, PathRadiusOffset = 0, PathTaperX = 0, PathTaperY = 0, PathRevolutions = 0, PathSkew = 0, ProfileBegin = 0, ProfileEnd = 0, ProfileHollow = 0, BypassRaycast = 1, RayStart = location_to_rez, RayEnd = location_to_rez, RayTargetID = RayTargetID, RayEndIsIntersection = 0, Scale = (0.5, 0.5, 0.5), Rotation = (0, 0, 0, 1), State = 0)

    def object_add(self, PCode, Material, AddFlags, PathCurve, ProfileCurve, PathBegin, PathEnd, PathScaleX, PathScaleY, PathShearX, PathShearY, PathTwist, PathTwistBegin, PathRadiusOffset, PathTaperX, PathTaperY, PathRevolutions, PathSkew, ProfileBegin, ProfileEnd, ProfileHollow, BypassRaycast, RayStart, RayEnd, RayTargetID, RayEndIsIntersection, Scale, Rotation, State, GroupID = uuid.UUID('00000000-0000-0000-0000-000000000000')):
        '''
        ObjectAdd - create new object in the world
        Simulator will assign ID and send message back to signal
        object actually created.

        AddFlags (see also ObjectUpdate)
        0x01 - use physics
        0x02 - create selected

        GroupID defaults to (No group active)
        '''

        packet = ObjectAddPacket()

        # build the AgentData block
        packet.AgentData['AgentID'] = uuid.UUID(str(self.agent.agent_id))
        packet.AgentData['SessionID'] = uuid.UUID(str(self.agent.session_id))
        packet.AgentData['GroupID'] = uuid.UUID(str(GroupID))

        # build the ObjactData block (it's a Single)
        packet.ObjectData['PCode'] = PCode
        packet.ObjectData['Material'] = Material
        packet.ObjectData['AddFlags'] = AddFlags
        packet.ObjectData['PathCurve'] = PathCurve
        packet.ObjectData['ProfileCurve'] = ProfileCurve
        packet.ObjectData['PathBegin'] = PathBegin
        packet.ObjectData['PathEnd'] = PathEnd
        packet.ObjectData['PathScaleX'] = PathScaleX
        packet.ObjectData['PathScaleY'] = PathScaleY
        packet.ObjectData['PathShearX'] = PathShearX
        packet.ObjectData['PathShearY'] = PathShearY
        packet.ObjectData['PathTwist'] = PathTwist
        packet.ObjectData['PathTwistBegin'] = PathTwistBegin
        packet.ObjectData['PathRadiusOffset'] = PathRadiusOffset
        packet.ObjectData['PathTaperX'] = PathTaperX
        packet.ObjectData['PathTaperY'] = PathTaperY
        packet.ObjectData['PathRevolutions'] = PathRevolutions
        packet.ObjectData['PathSkew'] = PathSkew
        packet.ObjectData['ProfileBegin'] = ProfileBegin
        packet.ObjectData['ProfileEnd'] = ProfileEnd
        packet.ObjectData['ProfileHollow'] = ProfileHollow
        packet.ObjectData['BypassRaycast'] = BypassRaycast
        packet.ObjectData['RayStart'] = RayStart
        packet.ObjectData['RayEnd'] = RayEnd
        packet.ObjectData['RayTargetID'] = uuid.UUID(str(RayTargetID))
        packet.ObjectData['RayEndIsIntersection'] = RayEndIsIntersection
        packet.ObjectData['Scale'] = Scale
        packet.ObjectData['Rotation'] = Rotation
        packet.ObjectData['State'] = State

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

    def update_object_permissions(self, agent, Field, Set, Mask, Override = False):
        """ update permissions for a list of objects

        This will update a specific bit to a specific value.
        """

        packet = ObjectPermissionsPacket()

        # build the AgentData block
        packet.AgentData['AgentID'] = uuid.UUID(str(agent.agent_id))
        packet.AgentData['SessionID'] = uuid.UUID(str(agent.session_id))

        packet.HeaderData['Override'] = Override # BOOL, God-bit.

        ObjectData = {}
        ObjectData['ObjectLocalID'] = self.ID
        ObjectData['Field'] = Field         # U32
        ObjectData['Set'] = Set             # U8
        ObjectData['Mask'] = Mask           # S32

        packet.ObjectDataBlocks.append(ObjectData)

        agent.region.enqueue_message(packet())

    def set_object_name(self, agent, Name):
        """ update the name of an object 

        """

        packet = ObjectPermissionsPacket()

        # build the AgentData block
        packet.AgentData['AgentID'] = uuid.UUID(str(agent.agent_id))
        packet.AgentData['SessionID'] = uuid.UUID(str(agent.session_id))

        ObjectData = {}
        ObjectData['LocalID'] = self.ID
        ObjectData['Name'] = Name

        packet.ObjectDataBlocks.append(ObjectData)

        agent.region.enqueue_message(packet())

    def set_object_description(self, agent, Description):
        """ update the description of an objects 

        """

        packet = ObjectPermissionsPacket()

        # build the AgentData block
        packet.AgentData['AgentID'] = uuid.UUID(str(agent.agent_id))
        packet.AgentData['SessionID'] = uuid.UUID(str(agent.session_id))

        ObjectData = {}
        ObjectData['LocalID'] = self.ID
        ObjectData['Description'] = Description

        packet.ObjectDataBlocks.append(ObjectData)

        agent.region.enqueue_message(packet())

    def select(self, agent):
        """ select an object
        
        """

        packet = ObjectSelectPacket()

        # build the AgentData block
        packet.AgentData['AgentID'] = uuid.UUID(str(agent.agent_id))
        packet.AgentData['SessionID'] = uuid.UUID(str(agent.session_id))

        ObjectData = {}
        ObjectData['ObjectLocalID'] = self.ID

        packet.ObjectDataBlocks.append(ObjectData)

        agent.region.enqueue_message(packet())

    def deselect(self, agent):
        """ deselect an object

        """

        packet = ObjectDeselectPacket()

        # build the AgentData block
        packet.AgentData['AgentID'] = uuid.UUID(str(agent.agent_id))
        packet.AgentData['SessionID'] = uuid.UUID(str(agent.session_id))

        ObjectData = {}
        ObjectData['ObjectLocalID'] = self.ID

        packet.ObjectDataBlocks.append(ObjectData)

        agent.region.enqueue_message(packet())

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

        # deal with the data stored in _ObjectData
        # see http://wiki.secondlife.com/wiki/ObjectUpdate#ObjectData_Format for details

        Foot_Collision_Plane = None 
        Position = None
        Velocity = None
        Acceleration = None
        Rotation = None
        AngularVelocity = None

        if len(_ObjectData) == 76:

            # Foot collision plane. LLVector4.
            # Angular velocity is ignored and set to 0. Falls through to 60 bytes parser. 
            print len(_ObjectData)
            data = [ord(x) for x in b2a_base64(_ObjectData)]

        elif len(_ObjectData) == 60:

            # 32 bit precision update.

            # Position. LLVector3.
            # Velocity. LLVector3.
            # Acceleration. LLVector3.
            # Rotation. LLVector3.
            # Angular velocity. LLVector3.
            print len(_ObjectData)
            string = b2a_base64(_ObjectData)
            data = [ord(x) for x in b2a_base64(_ObjectData)]
            print data

        elif len(_ObjectData) == 48:

            # Foot collision plane. LLVector4 
            # Falls through to 32 bytes parser.
            print len(_ObjectData)
            string = b2a_base64(_ObjectData)
            data = [ord(x) for x in b2a_base64(_ObjectData)]
            print data

        elif len(_ObjectData) == 32:

            # 16 bit precision update.

            # Position. U16Vec3.
            # Velocity. U16Vec3.
            # Acceleration. U16Vec3.
            # Rotation. U16Rot(4xU16).
            # Angular velocity. LLVector3.
            print len(_ObjectData)
            string = b2a_base64(_ObjectData)
            data = [ord(x) for x in b2a_base64(_ObjectData)]
            print data

        elif len(_ObjectData) == 16:

            # 8 bit precision update.

            # Position. U8Vec3.
            # Velocity. U8Vec3.
            # Acceleration. U8Vec3.
            # Rotation. U8Rot(4xU8).
            # Angular velocity. U8Vec3
            print len(_ObjectData)
            string = b2a_base64(_ObjectData)
            data = [ord(x) for x in b2a_base64(_ObjectData)]
            print data

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
            CacheMissType = 0

        _request_list.append((_ID, CacheMissType))

    # ask the simulator for updates
    objects.request_object_update(ID_list = _request_list)

def onObjectUpdateCompressed(packet, objects):

    pass

def onKillObject(packet, objects):

    _KillID = packet.message_data.blocks['ObjectData'][0].get_variable('ID').data

    try:
        objects.remove_object_from_store(_KillID)
    except:
        pass

    '''
    {
    	ObjectUpdateCompressed High 13 Trusted Unencoded
    	{
    		RegionData			Single
    		{	RegionHandle	U64		}
    		{   TimeDilation	U16		}
    	}
    	{
    		ObjectData			Variable
    		{   UpdateFlags			U32	}
    		{	Data			Variable   2	}
    	}
    }
    '''

'''
Object Related Messages


// ObjectAdd - create new object in the world
// Simulator will assign ID and send message back to signal
// object actually created.
//
// AddFlags (see also ObjectUpdate)
// 0x01 - use physics
// 0x02 - create selected
//
// If only one ImageID is sent for an object type that has more than
// one face, the same image is repeated on each subsequent face.
// 
// Data field is opaque type-specific data for this object
{
	ObjectAdd Medium 1 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID			LLUUID	}
	}
	{
		ObjectData			Single
		{	PCode			U8	}
		{	Material		U8	}
		{	AddFlags		U32	}	// see object_flags.h

		{	PathCurve		U8	}
		{	ProfileCurve	U8	}
		{	PathBegin		U16	}	// 0 to 1, quanta = 0.01
		{	PathEnd			U16	}	// 0 to 1, quanta = 0.01
		{	PathScaleX		U8	}	// 0 to 1, quanta = 0.01
		{	PathScaleY		U8	}	// 0 to 1, quanta = 0.01
		{	PathShearX		U8	}	// -.5 to .5, quanta = 0.01
		{	PathShearY		U8	}	// -.5 to .5, quanta = 0.01
		{	PathTwist		S8	}	// -1 to 1, quanta = 0.01
		{	PathTwistBegin		S8	}	// -1 to 1, quanta = 0.01
		{ 	PathRadiusOffset 	S8	} 	// -1 to 1, quanta = 0.01
		{ 	PathTaperX		S8	}	// -1 to 1, quanta = 0.01
		{	PathTaperY		S8	}	// -1 to 1, quanta = 0.01
		{	PathRevolutions		U8	}	// 0 to 3, quanta = 0.015
		{	PathSkew		S8	}	// -1 to 1, quanta = 0.01
		{	ProfileBegin	U16	}	// 0 to 1, quanta = 0.01
		{	ProfileEnd		U16	}	// 0 to 1, quanta = 0.01
		{	ProfileHollow	U16	}	// 0 to 1, quanta = 0.01

		{	BypassRaycast	U8	}
		{	RayStart		LLVector3	}
		{	RayEnd			LLVector3	}
		{	RayTargetID		LLUUID	}
		{	RayEndIsIntersection	U8	}

		{	Scale			LLVector3	}
		{	Rotation		LLQuaternion	}

		{	State			U8	}
	}
}


// ObjectDelete
// viewer -> simulator
{
	ObjectDelete Low 89 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	Force		BOOL	}	// BOOL, god trying to force delete
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}
}


// ObjectDuplicate
// viewer -> simulator
// Makes a copy of a set of objects, offset by a given amount
{
	ObjectDuplicate Low 90 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		SharedData			Single
		{	Offset			LLVector3	}
		{	DuplicateFlags	U32			}	// see object_flags.h
	}
	{
		ObjectData			Variable
		{	ObjectLocalID		U32		}
	}
}


// ObjectDuplicateOnRay
// viewer -> simulator
// Makes a copy of an object, using the add object raycast
// code to abut it to other objects.
{
	ObjectDuplicateOnRay Low 91 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID					LLUUID	}
		{	SessionID				LLUUID	}
		{	GroupID					LLUUID	}
		{	RayStart				LLVector3	}	// region local
		{	RayEnd					LLVector3	}	// region local
		{	BypassRaycast			BOOL	}
		{	RayEndIsIntersection	BOOL	}
		{	CopyCenters				BOOL	}
		{	CopyRotates				BOOL	}
		{	RayTargetID				LLUUID	}
		{	DuplicateFlags			U32		}	// see object_flags.h
	}
	{
		ObjectData			Variable
		{	ObjectLocalID			U32		}
	}
}


// MultipleObjectUpdate
// viewer -> simulator
// updates position, rotation and scale in one message
// positions sent as region-local floats
{
	MultipleObjectUpdate Medium 2 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData		Variable 
		{	ObjectLocalID	U32		}
		{   Type			U8		}
		{	Data			Variable	1	}	// custom type
	}
}

// RequestMultipleObjects
// viewer -> simulator
// reliable
//
// When the viewer gets a local_id/crc for an object that
// it either doesn't have, or doesn't have the current version
// of, it sends this upstream get get an update.
//
// CacheMissType 0 => full object (viewer doesn't have it)
// CacheMissType 1 => CRC mismatch only
{
	RequestMultipleObjects Medium 3 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData	Variable 
		{	CacheMissType	U8	}
		{	ID				U32	}
	}
}


// DEPRECATED: ObjectPosition
// == Old Behavior ==
// Set the position on objects
//
// == Reason for deprecation ==
// Unused code path was removed in the move to Havok4
// Object position, scale and rotation messages were already unified
// to MultipleObjectUpdate and this message was unused cruft.
//
// == New Location ==
// MultipleObjectUpdate can be used instead.
{
	ObjectPosition Medium 4 NotTrusted Zerocoded Deprecated
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32			}
		{	Position		LLVector3	}	// region
	}
}


// DEPRECATED: ObjectScale
// == Old Behavior ==
// Set the scale on objects
//
// == Reason for deprecation ==
// Unused code path was removed in the move to Havok4
// Object position, scale and rotation messages were already unified
// to MultipleObjectUpdate and this message was unused cruft.
//
// == New Location ==
// MultipleObjectUpdate can be used instead.
{
	ObjectScale Low 92 NotTrusted Zerocoded Deprecated
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32			}
		{	Scale			LLVector3	}
	}
}


// ObjectRotation
// viewer -> simulator
{
	ObjectRotation Low 93 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32				}
		{	Rotation		LLQuaternion	}
	}
}


// ObjectFlagUpdate
// viewer -> simulator
{
	ObjectFlagUpdate Low 94 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	ObjectLocalID	U32		}
		{	UsePhysics		BOOL	}
		{	IsTemporary		BOOL	}
		{	IsPhantom		BOOL	}
		{	CastsShadows	BOOL	}
	}
}


// ObjectClickAction
// viewer -> simulator
{
	ObjectClickAction Low 95 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32		}
		{	ClickAction		U8		}
	}
}


// ObjectImage
// viewer -> simulator
{
	ObjectImage Low 96 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData			Variable
		{	ObjectLocalID		U32				}
		{	MediaURL			Variable	1	}
		{	TextureEntry		Variable	2	}
	}
}


{
	ObjectMaterial Low 97 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
		{	Material	U8	}
	}
}


{
	ObjectShape Low 98 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData			Variable
		{	ObjectLocalID	U32	}
		{	PathCurve		U8	}
		{	ProfileCurve	U8	}
		{	PathBegin		U16	}	// 0 to 1, quanta = 0.01
		{	PathEnd			U16	}	// 0 to 1, quanta = 0.01
		{	PathScaleX		U8	}	// 0 to 1, quanta = 0.01
		{	PathScaleY		U8	}	// 0 to 1, quanta = 0.01
		{	PathShearX		U8	}	// -.5 to .5, quanta = 0.01
		{	PathShearY		U8	}	// -.5 to .5, quanta = 0.01
		{	PathTwist		S8	}	// -1 to 1, quanta = 0.01
		{	PathTwistBegin		S8	}	// -1 to 1, quanta = 0.01
		{ 	PathRadiusOffset 	S8	} 	// -1 to 1, quanta = 0.01
		{ 	PathTaperX		S8	}	// -1 to 1, quanta = 0.01
		{	PathTaperY		S8	}	// -1 to 1, quanta = 0.01
		{	PathRevolutions		U8	}	// 0 to 3, quanta = 0.015
		{	PathSkew		S8	}	// -1 to 1, quanta = 0.01
		{	ProfileBegin	U16	}	// 0 to 1, quanta = 0.01
		{	ProfileEnd		U16	}	// 0 to 1, quanta = 0.01
		{	ProfileHollow	U16	}	// 0 to 1, quanta = 0.01
	}
}

{
	ObjectExtraParams Low 99 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData			Variable
		{	ObjectLocalID	U32				}
		{	ParamType		U16				}
		{	ParamInUse		BOOL			}
		{	ParamSize		U32				}
		{	ParamData		Variable	1	}
	}
}


// ObjectOwner
// To make public, set OwnerID to LLUUID::null.
// TODO: Eliminate god-bit. Maybe not. God-bit is ok, because it's
// known on the server.
{
	ObjectOwner Low 100 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		HeaderData		Single
		{	Override	BOOL	}	// BOOL, God-bit.
		{	OwnerID		LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		ObjectData	Variable
		{	ObjectLocalID	U32	}
	}
}

// ObjectGroup
// To make the object part of no group, set GroupID = LLUUID::null.
// This call only works if objectid.ownerid == agentid.
{
	ObjectGroup	Low	101 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		ObjectData	Variable
		{	ObjectLocalID	U32	}
	}
}

// Attempt to buy an object. This will only pack root objects.
{
	ObjectBuy Low 102 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
		{	CategoryID	LLUUID	}	// folder where it goes (if derezed)
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
		{	SaleType		U8	}   // U8 -> EForSale
		{	SalePrice		S32	}
	}
}

// viewer -> simulator

// buy object inventory. If the transaction succeeds, it will add
// inventory to the agent, and potentially remove the original.
{
	BuyObjectInventory	Low	103 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		Data	Single
		{	ObjectID	LLUUID	}
		{	ItemID		LLUUID	}
		{	FolderID	LLUUID	}
	}
}

// sim -> viewer
// Used to propperly handle buying asset containers
{
	DerezContainer		Low	104 	Trusted Zerocoded
	{
		Data			Single
		{	ObjectID	LLUUID	}
		{	Delete		BOOL	}  // BOOL
	}
}

// ObjectPermissions
// Field - see llpermissionsflags.h
// If Set is true, tries to turn on bits in mask.
// If set is false, tries to turn off bits in mask.
// BUG: This just forces the permissions field.
{
	ObjectPermissions Low 105 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		HeaderData		Single
		{	Override	BOOL	}	// BOOL, God-bit.
	}
	{
		ObjectData	Variable
		{	ObjectLocalID	U32	}
		{	Field		U8	}
		{	Set			U8	}
		{	Mask		U32	}
	}
}

// set object sale information
{
	ObjectSaleInfo Low 106 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData			Variable
		{	LocalID			U32	}
		{	SaleType		U8	}   // U8 -> EForSale
		{	SalePrice		S32	}
	}
}


// set object names
{
	ObjectName Low 107 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	LocalID		U32	}
		{	Name		Variable	1	}
	}
}

// set object descriptions
{
	ObjectDescription Low 108 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	LocalID		U32	}
		{	Description	Variable	1	}
	}
}

// set object category
{
	ObjectCategory Low 109 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	LocalID		U32	}
		{	Category	U32	}
	}
}

// ObjectSelect
// Variable object data because rectangular selection can
// generate a large list very quickly.
{
	ObjectSelect Low 110 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}

}


// ObjectDeselect
{
	ObjectDeselect Low 111 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}

}

// ObjectAttach
{
	ObjectAttach Low 112 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	AttachmentPoint	U8	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32				}
		{	Rotation		LLQuaternion	}
	}
}

// ObjectDetach -- derezzes an attachment, marking its item in your inventory as not "(worn)"
{
	ObjectDetach Low 113 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}
}


// ObjectDrop -- drops an attachment from your avatar onto the ground
{
	ObjectDrop Low 114 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}
}


// ObjectLink
{
	ObjectLink Low 115 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}
}

// ObjectDelink
{
	ObjectDelink Low 116 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}
}


// ObjectGrab
{
	ObjectGrab Low 117 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData			Single
		{	LocalID				U32  }
		{	GrabOffset			LLVector3 }
	}
	{
		SurfaceInfo     Variable
		{   UVCoord     LLVector3 }
		{   STCoord     LLVector3 }
       	{   FaceIndex   S32 }
       	{   Position    LLVector3 }
       	{   Normal      LLVector3 }
       	{   Binormal    LLVector3 }
	}
}


// ObjectGrabUpdate
// TODO: Quantize this data, reduce message size.
// TimeSinceLast could go to 1 byte, since capped
// at 100 on sim.
{
	ObjectGrabUpdate Low 118 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData	Single
		{	ObjectID			LLUUID	}
		{	GrabOffsetInitial	LLVector3	}	// LLVector3
		{	GrabPosition		LLVector3	}	// LLVector3, region local
		{	TimeSinceLast		U32	}
	}
	{
		SurfaceInfo     Variable
		{   UVCoord     LLVector3 }
		{   STCoord     LLVector3 }
       	{   FaceIndex   S32 }
       	{   Position    LLVector3 }
       	{   Normal      LLVector3 }
       	{   Binormal    LLVector3 }
	}

}


// ObjectDeGrab				
{
	ObjectDeGrab Low 119 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData			Single
		{	LocalID				U32  }
	}
	{
		SurfaceInfo     Variable
		{   UVCoord     LLVector3 }
		{   STCoord     LLVector3 }
       	{   FaceIndex   S32 }
       	{   Position    LLVector3 }
       	{   Normal      LLVector3 }
       	{   Binormal    LLVector3 }
	}
}


// ObjectSpinStart
{
	ObjectSpinStart Low 120 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData			Single
		{	ObjectID		LLUUID	}
	}
}


// ObjectSpinUpdate
{
	ObjectSpinUpdate Low 121 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData			Single
		{	ObjectID		LLUUID	}
		{	Rotation		LLQuaternion }
	}
}


// ObjectSpinStop
{
	ObjectSpinStop Low 122 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData			Single
		{	ObjectID		LLUUID	}
	}
}

// Export selected objects
// viewer->sim
{
	ObjectExportSelected Low 123 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	RequestID		LLUUID  }
		{	VolumeDetail	S16		}
	}
	{
		ObjectData			Variable
		{	ObjectID		LLUUID	}
	}
}

'''
