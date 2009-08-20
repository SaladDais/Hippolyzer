
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
from logging import getLogger, ERROR, WARNING, INFO, DEBUG
import uuid
import re
import struct
import math

# related


# pyogp
from pyogp.lib.base import *
from pyogp.lib.base.datamanager import DataManager
from pyogp.lib.base.permissions import PermissionsTarget, PermissionsMask
from pyogp.lib.base.datatypes import UUID, Vector3, Quaternion
from pyogp.lib.base.event_system import AppEvent

# pyogp message
from pyogp.lib.base.message.message_handler import MessageHandler
from pyogp.lib.base.message.message import Message, Block


# pyogp utilities
from pyogp.lib.base.utilities.helpers import Helpers
from pyogp.lib.base.utilities.enums import PCodeEnum, CompressedUpdateFlags, \
     Permissions, AssetType

# initialize logging
logger = getLogger('pyogp.lib.base.objects')
log = logger.log

class ObjectManager(DataManager):
    """ is an Object Manager

    Initialize the event queue client class
    >>> objects = ObjectManager()

    Sample implementations: region.py
    Tests: tests/test_objects.py
    """

    def __init__(self, agent = None, region = None, settings = None, message_handler = None, events_handler = None):
        """ set up the object manager """
        super(ObjectManager, self).__init__(agent, settings)
        self.region = region

        # the object store consists of a list
        # of Object() instances
        self.object_store = []

        # the avatar store consists of a list
        # of Avatar() instances
        self.avatar_store = []

        # other useful things
        self.helpers = Helpers()
       
        self.message_handler = message_handler
        
        if self.settings.LOG_VERBOSE: log(INFO, "Initializing object storage")

    def enable_callbacks(self):
        """enables the callback handlers for this ObjectManager"""
        if self.settings.HANDLE_PACKETS:
            # supply a MessageHandler if not given one
            if self.message_handler == None:
                self.message_handler = MessageHandler()

            onObjectUpdate_received = self.message_handler.register('ObjectUpdate')
            onObjectUpdate_received.subscribe(self.onObjectUpdate)

            onObjectUpdateCached_received = self.message_handler.register('ObjectUpdateCached')
            onObjectUpdateCached_received.subscribe(self.onObjectUpdateCached)

            onObjectUpdateCompressed_received = self.message_handler.register('ObjectUpdateCompressed')
            onObjectUpdateCompressed_received.subscribe(self.onObjectUpdateCompressed)

            onObjectProperties_received = self.message_handler.register('ObjectProperties')
            onObjectProperties_received.subscribe(self.onObjectProperties)

            onKillObject_received = self.message_handler.register('KillObject')
            onKillObject_received.subscribe(self.onKillObject)

            # uncomment these to view packets sent back to simulator
            # onObjectName_sent = self.message_handler.register('ObjectName')
            # onObjectName_sent.subscribe(self.helpers.log_packet, self)

            # onDeRezObject_sent = self.message_handler.register('DeRezObject')
            # onDeRezObject_sent.subscribe(self.helpers.log_packet, self)


    def process_multiple_object_updates(self, objects):
        """ process a list of object updates """

        [self.process_object_update(_object) for _object in objects]

    def process_object_update(self, _object):
        """ append to or replace an object in self.objects """

        # this is an avatar
        if _object.PCode == PCodeEnum.Avatar:

            self.store_avatar(_object)

        # this is a Primitive
        elif _object.PCode == PCodeEnum.Primitive:

            self.store_object(_object)

        else:

            if self.settings.LOG_VERBOSE:
                log(DEBUG, "Not processing object update of type %s" % (PCodeEnum(_object.PCode)))

    def store_object(self, _object):
        """ store a representation of an object that has been transformed from data off the wire """

        # replace an existing list member, else, append

        index = [self.object_store.index(_object_) for _object_ in self.object_store if _object_.LocalID == _object.LocalID]

        if index != []:

            self.object_store[index[0]] = _object

            #if self.settings.LOG_VERBOSE: log(DEBUG, 'Updating a stored object: %s in region \'%s\'' % (_object.FullID, self.region.SimName))

        else:

            self.object_store.append(_object)

            #if self.settings.LOG_VERBOSE: log(DEBUG, 'Stored a new object: %s in region \'%s\'' % (_object.LocalID, self.region.SimName))

    def store_avatar(self, _objectdata):
        """ store a representation of an avatar (Object() instance) that has been transformed from data off the wire  """

        #ToDo: should there be a separate Avatar() class?

        # if the object data pertains to us, update our data!
        if str(_objectdata.FullID) == str(self.agent.agent_id):

            if _objectdata.Position:
                self.agent.Position = _objectdata.Position
            if _objectdata.FootCollisionPlane: 
                self.agent.FootCollisionPlane = _objectdata.FootCollisionPlane
            if _objectdata.Velocity:
                self.agent.Velocity = _objectdata.Velocity
            if _objectdata.Acceleration:
                self.agent.Acceleration = _objectdata.Acceleration
            if _objectdata.Rotation:
                self.agent.Rotation = _objectdata.Rotation
            if _objectdata.AngularVelocity:
                self.agent.AngularVelocity = _objectdata.AngularVelocity

            if self.settings.ENABLE_APPEARANCE_MANAGEMENT:
                self.agent.appearance.TextureEntry = _objectdata.TextureEntry
                                
            self.agent.sendDynamicsUpdate()
            
        index = [self.avatar_store.index(_avatar_) for _avatar_ in self.avatar_store if _avatar_.LocalID == _objectdata.LocalID]

        if index != []:

            self.avatar_store[index[0]] = _objectdata

            #if self.settings.LOG_VERBOSE: log(DEBUG, 'Replacing a stored avatar: %s in region \'%s\'' % (_objectdata.LocalID, self.region.SimName))

        else:

            self.avatar_store.append(_objectdata)

            #if self.settings.LOG_VERBOSE: log(DEBUG, 'Stored a new avatar: %s in region \'%s\'' % (_objectdata.LocalID, self.region.SimName))

    def get_object_from_store(self, LocalID = None, FullID = None):
        """ searches the store and returns object if stored, None otherwise """

        _object = []

        if LocalID != None:
            _object = [_object for _object in self.object_store if _object.LocalID == LocalID]
        elif FullID != None:
            _object = [_object for _object in self.object_store if str(_object.FullID) == str(FullID)]

        if _object == []:
            return None
        else:
            return _object[0]

    def get_avatar_from_store(self, LocalID = None, FullID = None):
        """ searches the store and returns object if stored, None otherwise """

        if LocalID != None:
            _avatar = [_avatar for _avatar in self.avatar_store if _avatar.LocalID == LocalID]
        elif FullID != None:
            _avatar = [_avatar for _avatar in self.avatar_store if _avatar.FullID == FullID]

        if _avatar == []:
            return None
        else:
            return _avatar[0]

    def my_objects(self):
        """ returns a list of known objects where the calling client is the owner """

        matches = [_object for _object in self.object_store if str(_object.OwnerID) == str(self.agent.agent_id)]

        return matches

    def find_objects_by_name(self, Name):
        """ searches the store for known objects by name 

        returns a list of all such known objects
        """

        pattern = re.compile(Name)

        matches = [_object for _object in self.object_store if pattern.match(_object.Name)]

        return matches

    def find_objects_within_radius(self, radius):
        """ returns objects nearby. returns a list of objects """

        if type(radius) != float:
            radius = float(radius)

        objects_nearby = []

        for item in self.object_store:

            if item.Position == None:
                continue

            if math.sqrt(math.pow((item.Position.X - self.agent.Position.X), 2) +  math.pow((item.Position.Y - self.agent.Position.Y), 2) + math.pow((item.Position.Z - self.agent.Position.Z), 2)) <= radius:
                objects_nearby.append(item)

        return objects_nearby

    def remove_object_from_store(self, ID = None):
        """ handles removing a stored object representation """

        victim = self.get_object_from_store(LocalID = ID)

        if victim == None:
            victim = self.get_avatar_from_store(LocalID = ID)

        # if we do not know about this object, pass
        if victim == None or victim == []:
            return

        # this is an avatar
        if victim.PCode == PCodeEnum.Avatar:

            self.kill_stored_avatar(ID)

        # this is a Primitive
        elif victim.PCode == PCodeEnum.Primitive:

            self.kill_stored_object(ID)

        else:

            if self.settings.LOG_VERBOSE and self.settings.ENABLE_OBJECT_LOGGING:
                log(DEBUG, "Not processing kill of unstored object type %s" % (PCodeEnum(victim.PCode)))

    def kill_stored_avatar(self, ID):
        """ removes a stored avatar (Object() instance) from our list """

        index = [self.avatar_store.index(_avatar_) for _avatar_ in self.avatar_store if _avatar_.LocalID == ID]

        if index != []:
            del self.avatar_store[index[0]]
            if self.settings.LOG_VERBOSE and self.settings.ENABLE_OBJECT_LOGGING:
                log(DEBUG, "Kill on object data for avatar tracked as local id %s" % (ID))

    def kill_stored_object(self, ID):

        index = [self.object_store.index(_object_) for _object_ in self.object_store if _object_.LocalID == ID]

        if index != []:
            del self.object_store[index[0]]
            if self.settings.LOG_VERBOSE and self.settings.ENABLE_OBJECT_LOGGING:
                log(DEBUG, "Kill on object data for object tracked as local id %s" % (ID))

    def update_multiple_objects_properties(self, object_list):
        """ update the attributes of objects """

        #if self.settings.LOG_VERBOSE and self.settings.ENABLE_OBJECT_LOGGING: log(DEBUG, "Processing multiple object properties updates: %s" % (len(object_list)))

        for object_properties in object_list:

            self.update_object_properties(object_properties)

    def update_object_properties(self, object_properties):
        """ update the attributes of an object
        
        If the object is known, we update the properties. 
        If not, we create a new object
        """

        #if self.settings.LOG_VERBOSE and self.settings.ENABLE_OBJECT_LOGGING: log(DEBUG, "Processing object properties update for FullID: %s" % (object_properties['FullID']))

        if object_properties.has_key('PCode'):
            # this is an avatar
            if object_properties['PCode'] == PCodeEnum.Avatar:

                #if self.settings.LOG_VERBOSE and self.settings.ENABLE_OBJECT_LOGGING: log(DEBUG, "Creating a new avatar and storing their attributes. LocalID = %s" % (object_properties['LocalID']))

                _object = Object()
                _object._update_properties(object_properties)

                self.store_avatar(_object)

            else:

                self.update_prim_properties(object_properties)

        else:

            self.update_prim_properties(object_properties)

    def update_prim_properties(self, prim_properties):
        """ handles an object update and updates or adds to internal representation """

        _object = self.get_object_from_store(FullID = prim_properties['FullID'])

        if _object == None:
            #if self.settings.LOG_VERBOSE and self.settings.ENABLE_OBJECT_LOGGING: log(DEBUG, "Creating a new object and storing it's attributes. LocalID = %s" % (object_properties['LocalID']))
            _object = Object()
            _object._update_properties(prim_properties)
            self.store_object(_object)
        else:
            #if self.settings.LOG_VERBOSE and self.settings.ENABLE_OBJECT_LOGGING: log(DEBUG, "Updating an object's attributes. LocalID = %s" % (object_properties['LocalID']))
            _object._update_properties(prim_properties)
        if _object.UpdateFlags & 2 != 0 and self.agent != None:
            
            self.agent.events_handler.handle(AppEvent("ObjectSelected",
                                                      payload = {'object':_object}))
          

    def request_object_update(self, AgentID, SessionID, ID_CacheMissType_list = None):
        """ requests object updates from the simulator

        accepts a list of (ID, CacheMissType)
        """

        packet = Message('RequestMultipleObjects',
                        Block('AgentData',
                                AgentID = AgentID,
                                SessionID = SessionID),
                        *[Block('ObjectData',
                                CacheMissType = ID_CacheMissType[1],
                                ID = ID_CacheMissType[0]) for ID_CacheMissType in ID_CacheMissType_list])

        # enqueue the message, send as reliable
        self.region.enqueue_message(packet, True)

    def create_default_box(self, GroupID = UUID(), relative_position = (1, 0, 0)):
        """ creates the default box, defaulting as 1m to the east, with an option GroupID to set the prim to"""

        # self.agent.Position holds where we are. we need to add this tuple to the incoming tuple (vector to a vector)
        location_to_rez_x = self.agent.Position.X + relative_position[0]
        location_to_rez_y = self.agent.Position.Y + relative_position[1]
        location_to_rez_z = self.agent.Position.Z + relative_position[2]

        location_to_rez = (location_to_rez_x, location_to_rez_y, location_to_rez_z)

        # not sure what RayTargetID is, send as uuid of zeros
        RayTargetID = UUID()

        self.object_add(self.agent.agent_id, self.agent.session_id,
                        GroupID = GroupID, PCode = PCodeEnum.Primitive,
                        Material = 3, AddFlags = 2, PathCurve = 16,
                        ProfileCurve = 1, PathBegin = 0, PathEnd = 0,
                        PathScaleX = 100, PathScaleY = 100, PathShearX = 0,
                        PathShearY = 0, PathTwist = 0, PathTwistBegin = 0,
                        PathRadiusOffset = 0, PathTaperX = 0, PathTaperY = 0,
                        PathRevolutions = 0, PathSkew = 0, ProfileBegin = 0,
                        ProfileEnd = 0, ProfileHollow = 0, BypassRaycast = 1,
                        RayStart = location_to_rez, RayEnd = location_to_rez,
                        RayTargetID = RayTargetID, RayEndIsIntersection = 0,
                        Scale = (0.5, 0.5, 0.5), Rotation = (0, 0, 0, 1),
                        State = 0)

    def object_add(self, AgentID, SessionID, PCode, Material, AddFlags,
                   PathCurve, ProfileCurve, PathBegin, PathEnd, PathScaleX,
                   PathScaleY, PathShearX, PathShearY, PathTwist,
                   PathTwistBegin, PathRadiusOffset, PathTaperX,
                   PathTaperY, PathRevolutions, PathSkew, ProfileBegin,
                   ProfileEnd, ProfileHollow, BypassRaycast, RayStart,
                   RayEnd, RayTargetID, RayEndIsIntersection, Scale,
                   Rotation, State, GroupID = UUID()):
        '''
        ObjectAdd - create new object in the world
        Simulator will assign ID and send message back to signal
        object actually created.

        AddFlags (see also ObjectUpdate)
        0x01 - use physics
        0x02 - create selected

        GroupID defaults to (No group active)
        '''

        packet = Message('ObjectAdd',
                        Block('AgentData',
                            AgentID = AgentID,
                            SessionID = SessionID,
                            GroupID = GroupID),
                        Block('ObjectData',
                            PCode = PCode,
                            Material = Material,
                            AddFlags = AddFlags,
                            PathCurve = PathCurve,
                            ProfileCurve = ProfileCurve,
                            PathBegin = PathBegin,
                            PathEnd = PathEnd,
                            PathScaleX = PathScaleX,
                            PathScaleY = PathScaleY,
                            PathShearX = PathShearX,
                            PathShearY = PathShearY,
                            PathTwist = PathTwist,
                            PathTwistBegin = PathTwistBegin,
                            PathRadiusOffset = PathRadiusOffset,
                            PathTaperX = PathTaperX,
                            PathTaperY = PathTaperY,
                            PathRevolutions = PathRevolutions,
                            PathSkew = PathSkew,
                            ProfileBegin = ProfileBegin,
                            ProfileEnd = ProfileEnd,
                            ProfileHollow = ProfileHollow,
                            BypassRaycast = BypassRaycast,
                            RayStart = RayStart,
                            RayEnd = RayEnd,
                            RayTargetID = RayTargetID,
                            RayEndIsIntersection = RayEndIsIntersection,
                            Scale = Scale,
                            Rotation = Rotation,
                            State = State))

        self.region.enqueue_message(packet, True)

    def onObjectUpdate(self, packet):
        """ populates an Object instance and adds it to the ObjectManager() store """

        REGION_SIZE = 256.0
        MIN_HEIGHT = -REGION_SIZE
        MAX_HEIGHT = 4096.0

        object_list = []

        # ToDo: handle these 2 variables properly
        _RegionHandle = packet.blocks['RegionData'][0].get_variable('RegionHandle').data
        _TimeDilation = packet.blocks['RegionData'][0].get_variable('TimeDilation').data

        for ObjectData_block in packet.blocks['ObjectData']:

            object_properties = {}

            object_properties['LocalID'] = ObjectData_block.get_variable('ID').data
            object_properties['State'] = ObjectData_block.get_variable('State').data
            object_properties['FullID'] = ObjectData_block.get_variable('FullID').data
            object_properties['CRC'] = ObjectData_block.get_variable('CRC').data
            object_properties['PCode'] = ObjectData_block.get_variable('PCode').data
            object_properties['Material'] = ObjectData_block.get_variable('Material').data
            object_properties['ClickAction'] = ObjectData_block.get_variable('ClickAction').data
            object_properties['Scale'] = ObjectData_block.get_variable('Scale').data
            object_properties['ObjectData'] = ObjectData_block.get_variable('ObjectData').data
            object_properties['ParentID'] = ObjectData_block.get_variable('ParentID').data
            object_properties['UpdateFlags'] = ObjectData_block.get_variable('UpdateFlags').data
            object_properties['PathCurve'] = ObjectData_block.get_variable('PathCurve').data
            object_properties['ProfileCurve'] = ObjectData_block.get_variable('ProfileCurve').data
            object_properties['PathBegin'] = ObjectData_block.get_variable('PathBegin').data
            object_properties['PathEnd'] = ObjectData_block.get_variable('PathEnd').data
            object_properties['PathScaleX'] = ObjectData_block.get_variable('PathScaleX').data
            object_properties['PathScaleY'] = ObjectData_block.get_variable('PathScaleY').data
            object_properties['PathShearX'] = ObjectData_block.get_variable('PathShearX').data
            object_properties['PathShearY'] = ObjectData_block.get_variable('PathShearY').data
            object_properties['PathTwist'] = ObjectData_block.get_variable('PathTwist').data
            object_properties['PathTwistBegin'] = ObjectData_block.get_variable('PathTwistBegin').data
            object_properties['PathRadiusOffset'] = ObjectData_block.get_variable('PathRadiusOffset').data
            object_properties['PathTaperX'] = ObjectData_block.get_variable('PathTaperX').data
            object_properties['PathTaperY'] = ObjectData_block.get_variable('PathTaperY').data
            object_properties['PathRevolutions'] = ObjectData_block.get_variable('PathRevolutions').data
            object_properties['PathSkew'] = ObjectData_block.get_variable('PathSkew').data
            object_properties['ProfileBegin'] = ObjectData_block.get_variable('ProfileBegin').data
            object_properties['ProfileEnd'] = ObjectData_block.get_variable('ProfileEnd').data
            object_properties['ProfileHollow'] = ObjectData_block.get_variable('ProfileHollow').data
            object_properties['TextureEntry'] = ObjectData_block.get_variable('TextureEntry').data
            object_properties['TextureAnim'] = ObjectData_block.get_variable('TextureAnim').data
            object_properties['NameValue'] = ObjectData_block.get_variable('NameValue').data
            object_properties['Data'] = ObjectData_block.get_variable('Data').data
            object_properties['Text'] = ObjectData_block.get_variable('Text').data
            object_properties['TextColor'] = ObjectData_block.get_variable('TextColor').data
            object_properties['MediaURL'] = ObjectData_block.get_variable('MediaURL').data
            object_properties['PSBlock'] = ObjectData_block.get_variable('PSBlock').data
            object_properties['ExtraParams'] = ObjectData_block.get_variable('ExtraParams').data
            object_properties['Sound'] = ObjectData_block.get_variable('Sound').data
            object_properties['OwnerID'] = ObjectData_block.get_variable('OwnerID').data
            object_properties['Gain'] = ObjectData_block.get_variable('Gain').data
            object_properties['Flags'] = ObjectData_block.get_variable('Flags').data
            object_properties['Radius'] = ObjectData_block.get_variable('Radius').data
            object_properties['JointType'] = ObjectData_block.get_variable('JointType').data
            object_properties['JointPivot'] = ObjectData_block.get_variable('JointPivot').data
            object_properties['JointAxisOrAnchor'] = ObjectData_block.get_variable('JointAxisOrAnchor').data

            # deal with the data stored in _ObjectData
            # see http://wiki.secondlife.com/wiki/ObjectUpdate#ObjectData_Format for details

            object_properties['FootCollisionPlane'] = None 
            object_properties['Position'] = None
            object_properties['Velocity'] = None
            object_properties['Acceleration'] = None
            object_properties['Rotation'] = None
            object_properties['AngularVelocity'] = None

            objdata = object_properties['ObjectData'] 
            if len(objdata) == 76 or len(objdata) == 60:

                pos = 0

                if len(objdata) == 76:
                    # Foot collision plane. LLVector4.
                    # Angular velocity is ignored and set to 0. Falls through to 60 bytes parser. 
                    object_properties['FootCollisionPlane'] = Quaternion(objdata, pos)
                    pos += 16

                # 32 bit precision update.
                
                object_properties['Position'] = Vector3(objdata, pos+0)
                object_properties['Velocity'] = Vector3(objdata, pos+12)
                object_properties['Acceleration'] = Vector3(objdata, pos+24)
                object_properties['Rotation'] = Quaternion(objdata, pos+36, 3) # unpack from vector3
                object_properties['AngularVelocity'] = Vector3(objdata, pos+48)

                # *TODO: This is... weird
                #if len(objdata) == 76:
                #    object_properties['AngularVelocity'] = Vector3()


            elif len(objdata) == 48 or len(objdata) == 32:

                pos = 0
                if len(objdata) == 48:
                    # Foot collision plane. LLVector4 
                    object_properties['FootCollisionPlane'] = Quaternion(objdata, pos)
                    pos += 16

                # 32 bit precision update.

                # Position. U16Vec3.
                # Velocity. U16Vec3.
                # Acceleration. U16Vec3.
                # Rotation. U16Rot(4xU16).
                # Angular velocity. LLVector3.

                object_properties['Position'] = Vector3(
                    X=Helpers.packed_u16_to_float(objdata, pos+ 0, -0.5*REGION_SIZE, 1.5*REGION_SIZE),
                    Y=Helpers.packed_u16_to_float(objdata, pos+ 2, -0.5*REGION_SIZE, 1.5*REGION_SIZE),
                    Z=Helpers.packed_u16_to_float(objdata, pos+ 4, MIN_HEIGHT, MAX_HEIGHT))
                object_properties['Velocity'] = Vector3(
                    X=Helpers.packed_u16_to_float(objdata, pos+ 6, -REGION_SIZE, REGION_SIZE),
                    Y=Helpers.packed_u16_to_float(objdata, pos+ 8, -REGION_SIZE, REGION_SIZE),
                    Z=Helpers.packed_u16_to_float(objdata, pos+10, -REGION_SIZE, REGION_SIZE))
                object_properties['Acceleration'] = Vector3(
                    X=Helpers.packed_u16_to_float(objdata, pos+12, -REGION_SIZE, REGION_SIZE),
                    Y=Helpers.packed_u16_to_float(objdata, pos+14, -REGION_SIZE, REGION_SIZE),
                    Z=Helpers.packed_u16_to_float(objdata, pos+16, -REGION_SIZE, REGION_SIZE))
                object_properties['Rotation'] = Quaternion(
                    X=Helpers.packed_u16_to_float(objdata, pos+18, -1.0, 1.0),
                    Y=Helpers.packed_u16_to_float(objdata, pos+20, -1.0, 1.0),
                    Z=Helpers.packed_u16_to_float(objdata, pos+22, -1.0, 1.0),
                    W=Helpers.packed_u16_to_float(objdata, pos+24, -1.0, 1.0))
                object_properties['AngularVelocity'] = Vector3(
                    X=Helpers.packed_u16_to_float(objdata, pos+26, -REGION_SIZE, REGION_SIZE),
                    Y=Helpers.packed_u16_to_float(objdata, pos+28, -REGION_SIZE, REGION_SIZE),
                    Z=Helpers.packed_u16_to_float(objdata, pos+30, -REGION_SIZE, REGION_SIZE))

            elif len(objdata) == 16:

                # 8 bit precision update.

                # Position. U8Vec3.
                # Velocity. U8Vec3.
                # Acceleration. U8Vec3.
                # Rotation. U8Rot(4xU8).
                # Angular velocity. U8Vec3

                object_properties['Position'] = Vector3(
                    X=Helpers.packed_u8_to_float(objdata,  0, -0.5*REGION_SIZE, 1.5*REGION_SIZE),
                    Y=Helpers.packed_u8_to_float(objdata,  1, -0.5*REGION_SIZE, 1.5*REGION_SIZE),
                    Z=Helpers.packed_u8_to_float(objdata,  2, MIN_HEIGHT, MAX_HEIGHT))
                object_properties['Velocity'] = Vector3(
                    X=Helpers.packed_u8_to_float(objdata,  3, -REGION_SIZE, REGION_SIZE),
                    Y=Helpers.packed_u8_to_float(objdata,  4, -REGION_SIZE, REGION_SIZE),
                    Z=Helpers.packed_u8_to_float(objdata,  5, -REGION_SIZE, REGION_SIZE))
                object_properties['Acceleration'] = Vector3(
                    X=Helpers.packed_u8_to_float(objdata,  6, -REGION_SIZE, REGION_SIZE),
                    Y=Helpers.packed_u8_to_float(objdata,  7, -REGION_SIZE, REGION_SIZE),
                    Z=Helpers.packed_u8_to_float(objdata,  8, -REGION_SIZE, REGION_SIZE))
                object_properties['Rotation'] = Quaternion(
                    X=Helpers.packed_u8_to_float(objdata,  9, -1.0, 1.0),
                    Y=Helpers.packed_u8_to_float(objdata, 10, -1.0, 1.0),
                    Z=Helpers.packed_u8_to_float(objdata, 11, -1.0, 1.0),
                    W=Helpers.packed_u8_to_float(objdata, 12, -1.0, 1.0)) 
                object_properties['AngularVelocity'] = Vector3(
                    X=Helpers.packed_u8_to_float(objdata, 13, -REGION_SIZE, REGION_SIZE),
                    Y=Helpers.packed_u8_to_float(objdata, 14, -REGION_SIZE, REGION_SIZE),
                    Z=Helpers.packed_u8_to_float(objdata, 15, -REGION_SIZE, REGION_SIZE))
            
            object_list.append(object_properties)

        self.update_multiple_objects_properties(object_list)

    def onObjectUpdateCached(self, packet):
        """ borrowing from libomv, we'll request object data for all data coming in via ObjectUpdateCached"""

        # ToDo: handle these 2 variables properly
        _RegionHandle = packet.blocks['RegionData'][0].get_variable('RegionHandle').data
        _TimeDilation = packet.blocks['RegionData'][0].get_variable('TimeDilation').data

        _request_list = []

        for ObjectData_block in packet.blocks['ObjectData']:

            LocalID = ObjectData_block.get_variable('ID').data
            _CRC = ObjectData_block.get_variable('CRC').data
            _UpdateFlags = ObjectData_block.get_variable('UpdateFlags').data

            # Objects.request_object_update() expects a tuple of (_ID, CacheMissType)

            # see if we have the object stored already
            _object = self.get_object_from_store(LocalID = LocalID)

            if _object == None or _object == []:
                CacheMissType = 1
            else:
                CacheMissType = 0

            _request_list.append((LocalID, CacheMissType))

        # ask the simulator for updates
        self.request_object_update(self.agent.agent_id, self.agent.session_id, ID_CacheMissType_list = _request_list)

    def onObjectUpdateCompressed(self, packet):
        """ handles an ObjectUpdateCompressed message from a simulator """

        object_list = []

        # ToDo: handle these 2 variables properly
        _RegionHandle = packet.blocks['RegionData'][0].get_variable('RegionHandle').data
        _TimeDilation = packet.blocks['RegionData'][0].get_variable('TimeDilation').data

        for ObjectData_block in packet.blocks['ObjectData']:

            object_properties = {}

            object_properties['UpdateFlags'] = ObjectData_block.get_variable('UpdateFlags').data
            object_properties['Data'] = ObjectData_block.get_variable('Data').data
            _Data = object_properties['Data']

            pos = 0         # position in the binary string
            object_properties['FullID'] = UUID(bytes = _Data, offset = 0)        # LLUUID
            pos += 16
            object_properties['LocalID'] = struct.unpack("<I", _Data[pos:pos+4])[0]
            pos += 4
            object_properties['PCode'] = struct.unpack(">B", _Data[pos:pos+1])[0]
            pos += 1

            if object_properties['PCode'] != 9:         # if it is not a prim, stop.
                log(WARNING, 'Fix Me!! Skipping parsing of ObjectUpdateCompressed packet when it is not a prim.')
                # we ought to parse it and make sense of the data...
                continue

            object_properties['State'] = struct.unpack(">B", _Data[pos:pos+1])[0]
            pos += 1
            object_properties['CRC'] = struct.unpack("<I", _Data[pos:pos+4])[0]
            pos += 4
            object_properties['Material'] = struct.unpack(">B", _Data[pos:pos+1])[0]
            pos += 1
            object_properties['ClickAction'] = struct.unpack(">B", _Data[pos:pos+1])[0]
            pos += 1
            object_properties['Scale'] = Vector3(_Data, pos)
            pos += 12
            object_properties['Position'] = Vector3(_Data, pos)
            pos += 12
            object_properties['Rotation'] = Vector3(_Data, pos)
            pos += 12
            object_properties['Flags'] = struct.unpack(">B", _Data[pos:pos+1])[0]
            pos += 1
            object_properties['OwnerID'] = UUID(bytes = _Data, offset = pos)
            pos += 16

            # Placeholder vars, to be populated via flags if present
            object_properties['AngularVelocity'] = Vector3()
            object_properties['ParentID'] = UUID()
            object_properties['Text'] = ''
            object_properties['TextColor'] = None
            object_properties['MediaURL'] = ''
            object_properties['Sound'] = UUID()
            object_properties['Gain'] = 0
            object_properties['Flags'] = 0
            object_properties['Radius'] = 0
            object_properties['NameValue'] = ''
            object_properties['ExtraParams'] = None

            if object_properties['Flags'] != 0:

                log(WARNING, "FixMe! Quiting parsing an ObjectUpdateCompressed packet with flags due to incomplete implemention. Storing a partial representation of an object with uuid of %s" % (object_properties['FullID']))

                # the commented code is not working right, we need to figure out why!
                # ExtraParams in particular seemed troublesome

                '''
                print 'Flags: ', Flags

                if (Flags & CompressedUpdateFlags.contains_AngularVelocity) != 0:
                    _AngularVelocity = Vector3(_Data, pos)
                    pos += 12
                    print 'AngularVelocity: ', _AngularVelocity
                else:
                    _AngularVelocity = None

                if (Flags & CompressedUpdateFlags.contains_Parent) != 0:
                    _ParentID = UUID(_Data, pos)
                    pos += 16
                    print 'ParentID: ', _ParentID
                else:
                    _ParentID = None

                if (Flags & CompressedUpdateFlags.Tree) != 0:
                    # skip it, only iterate the position
                    pos += 1
                    print 'Tree'

                if (Flags & CompressedUpdateFlags.ScratchPad) != 0:
                    # skip it, only iterate the position
                    size = struct.unpack(">B", _Data[pos:pos+1])[0]
                    pos += 1
                    pos += size
                    print 'Scratchpad size'

                if (Flags & CompressedUpdateFlags.contains_Text) != 0:
                    # skip it, only iterate the position
                    _Text = ''
                    while struct.unpack(">B", _Data[pos:pos+1])[0] != 0:
                        pos += 1
                    pos += 1
                    _TextColor = struct.unpack("<I", _Data[pos:pos+4])[0]
                    pos += 4
                    print '_TextColor: ', _TextColor

                if (Flags & CompressedUpdateFlags.MediaURL) != 0:
                    # skip it, only iterate the position
                    _MediaURL = ''
                    while struct.unpack(">B", _Data[pos:pos+1])[0] != 0:
                        pos += 1
                    pos += 1
                    print '_MediaURL: ', _MediaURL

                if (Flags & CompressedUpdateFlags.contains_Particles) != 0:
                    # skip it, only iterate the position
                    ParticleData = _Data[pos:pos+86]
                    pos += 86
                    print 'Particles'

                # parse ExtraParams
                # ToDo: finish this up, for now we are just incrementing the position and not dealing with the data

                _Flexible = None
                _Light = None
                _Sculpt = None

                num_extra_params =  struct.unpack(">b", _Data[pos:pos+1])[0]
                print 'Number of extra params: ', num_extra_params
                pos += 1

                for i in range(num_extra_params):

                    # ExtraParam type
                    extraparam_type = struct.unpack("<H", _Data[pos:pos+2])[0]
                    pos += 2

                    datalength = struct.unpack("<I", _Data[pos:pos+4])[0]
                    print 'ExtraParams type: %s length: %s' % (extraparam_type, datalength)
                    pos += 4

                    pos += int(datalength)

                # ToDo: Deal with extra parameters
                #log(WARNING, "Incomplete implementation in onObjectUpdateCompressed when flags are present. Skipping parsing this object...")
                #continue

                if (Flags & CompressedUpdateFlags.contains_Sound) != 0:
                    # skip it, only iterate the position
                    #_Sound = UUID(bytes = _Data[pos:pos+16])
                    pos += 16
                    print 'Sound'

                    #_Gain = struct.unpack(">f", _Data[pos:pos+4])[0]
                    pos += 4

                    #_Flags = stuct.unpack(">B", _Data[pos:pos+1])[0]
                    pos += 1

                    #_Radius = struct.unpack(">f", _Data[pos:pos+4])[0]
                    pos += 4

                if (Flags & CompressedUpdateFlags.contains_NameValues) != 0:
                    # skip it, only iterate the position
                    _NameValue = ''

                    while _Data[pos:pos+1] != 0:
                        #_NameValue += struct.unpack(">c", _Data[pos:pos+1])[0]
                        pos += 1
                    pos += 1
                '''

                object_properties['PathCurve'] = None
                object_properties['PathBegin'] = None
                object_properties['PathEnd'] = None
                object_properties['PathScaleX'] = None
                object_properties['PathScaleY'] = None
                object_properties['PathShearX'] = None
                object_properties['PathShearY'] = None
                object_properties['PathTwist'] = None
                object_properties['PathTwistBegin'] = None
                object_properties['PathRadiusOffset'] = None
                object_properties['PathTaperX'] = None
                object_properties['PathTaperY'] = None
                object_properties['PathRevolutions'] = None
                object_properties['PathSkew'] = None
                object_properties['ProfileCurve'] = None
                object_properties['ProfileBegin'] = None
                object_properties['ProfileEnd'] = None
                object_properties['ProfileHollow'] = None
                object_properties['TextureEntry'] = None
                object_properties['TextureAnim'] = None
                object_properties['TextureAnim'] = None

            else:

                object_properties['PathCurve'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['PathBegin'] = struct.unpack("<H", _Data[pos:pos+2])[0]
                pos += 2
                object_properties['PathEnd'] = struct.unpack("<H", _Data[pos:pos+2])[0]
                pos += 2
                object_properties['PathScaleX'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['PathScaleY'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['PathShearX'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['PathShearY'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['PathTwist'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['PathTwistBegin'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['PathRadiusOffset'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['PathTaperX'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['PathTaperY'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['PathRevolutions'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['PathSkew'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['ProfileCurve'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['ProfileBegin'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['ProfileEnd'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1
                object_properties['ProfileHollow'] = struct.unpack(">B", _Data[pos:pos+1])[0]
                pos += 1 

                # Texture handling
                size = struct.unpack("<H", _Data[pos:pos+2])[0]
                pos += 2
                object_properties['TextureEntry'] = _Data[pos:pos+size]
                pos += size

                if (object_properties['Flags'] & CompressedUpdateFlags.TextureAnim) != 0:
                    object_properties['TextureAnim'] = struct.unpack("<H", _Data[pos:pos+2])[0]
                    pos += 2
                else:
                    object_properties['TextureAnim'] = None

            object_list.append(object_properties)

        self.update_multiple_objects_properties(object_list)

    def onKillObject(self, packet):

        _KillID = packet.blocks['ObjectData'][0].get_variable('ID').data

        self.remove_object_from_store(_KillID)

    def onObjectProperties(self, packet):

        object_list = []

        for ObjectData_block in packet.blocks['ObjectData']:

            object_properties = {}

            object_properties['FullID'] = ObjectData_block.get_variable('ObjectID').data
            object_properties['CreatorID'] = ObjectData_block.get_variable('CreatorID').data
            object_properties['OwnerID'] = ObjectData_block.get_variable('OwnerID').data
            object_properties['GroupID'] = ObjectData_block.get_variable('GroupID').data
            object_properties['CreationDate'] = ObjectData_block.get_variable('CreationDate').data
            object_properties['BaseMask'] = ObjectData_block.get_variable('BaseMask').data
            object_properties['OwnerMask'] = ObjectData_block.get_variable('OwnerMask').data
            object_properties['GroupMask'] = ObjectData_block.get_variable('GroupMask').data
            object_properties['EveryoneMask'] = ObjectData_block.get_variable('EveryoneMask').data
            object_properties['NextOwnerMask'] = ObjectData_block.get_variable('NextOwnerMask').data
            object_properties['OwnershipCost'] = ObjectData_block.get_variable('OwnershipCost').data
            #object_properties['TaxRate'] = ObjectData_block.get_variable('TaxRate').data
            object_properties['SaleType'] = ObjectData_block.get_variable('SaleType').data
            object_properties['SalePrice'] = ObjectData_block.get_variable('SalePrice').data
            object_properties['AggregatePerms'] = ObjectData_block.get_variable('AggregatePerms').data
            object_properties['AggregatePermTextures'] = ObjectData_block.get_variable('AggregatePermTextures').data
            object_properties['AggregatePermTexturesOwner'] = ObjectData_block.get_variable('AggregatePermTexturesOwner').data
            object_properties['Category'] = ObjectData_block.get_variable('Category').data
            object_properties['InventorySerial'] = ObjectData_block.get_variable('InventorySerial').data
            object_properties['ItemID'] = ObjectData_block.get_variable('ItemID').data
            object_properties['FolderID'] = ObjectData_block.get_variable('FolderID').data
            object_properties['FromTaskID'] = ObjectData_block.get_variable('FromTaskID').data
            object_properties['LastOwnerID'] = ObjectData_block.get_variable('LastOwnerID').data
            object_properties['Name'] = ObjectData_block.get_variable('Name').data
            object_properties['Description'] = ObjectData_block.get_variable('Description').data
            object_properties['TouchName'] = ObjectData_block.get_variable('TouchName').data
            object_properties['SitName'] = ObjectData_block.get_variable('SitName').data
            object_properties['TextureID'] = ObjectData_block.get_variable('TextureID').data

            object_list.append(object_properties)

        self.update_multiple_objects_properties(object_list)

    def send_RezScript(self, agent, prim, item_id=UUID(),
                       Enabled=True,
                       GroupID=UUID(),
                       BaseMask=Permissions.All,
                       OwnerMask=Permissions.All,
                       GroupMask=Permissions.None_,
                       EveryoneMask=Permissions.None_,
                       NextOwnerMask=Permissions.Transfer&Permissions.Move,
                       GroupOwned=False,
                       Type=AssetType.LSLText,
                       InvType=AssetType.LSLText,
                       Flags=0,
                       SaleType=0,
                       SalePrice=0,
                       Name="New Script",
                       Description="Created by PyOGP",
                       CreationDate=0,
                       CRC=0):
        """ sends a RezScript message to the sim, not providing a item_id will
        rez the default script otherwise the script with ItemID item_id will be rezzed
        to prim"""
        packet = Message('RezScript',
                         Block('AgentData',
                               AgentID = agent.agent_id,
                               SessionID = agent.session_id,
                               GroupID = agent.ActiveGroupID),
                         Block('UpdateBlock',
                               ObjectLocalID = prim.LocalID,
                               Enabled = Enabled),
                         Block('InventoryBlock',
                               ItemID = item_id,
                               FolderID = prim.FullID,
                               CreatorID = agent.agent_id,
                               OwnerID = agent.agent_id,
                               GroupID = GroupID,
                               BaseMask = BaseMask,
                               OwnerMask = OwnerMask,
                               GroupMask = GroupMask,
                               EveryoneMask = EveryoneMask,
                               NextOwnerMask = NextOwnerMask,
                               GroupOwned = GroupOwned,
                               TransactionID = UUID(),
                               Type = Type,
                               InvType = InvType,
                               Flags = Flags,
                               SaleType = SaleType,
                               SalePrice = SalePrice,
                               Name = Name,
                               Description = Description,
                               CreationDate = CreationDate,
                               CRC = CRC))
        agent.region.enqueue_message(packet)
    


class Object(object):
    """ represents an Object

    Initialize the Object class instance
    >>> object = Object()

    Sample implementations: objects.py
    Tests: tests/test_objects.py
    """

    def __init__(self, LocalID = None, State = None, FullID = None, CRC = None, PCode = None, Material = None, ClickAction = None, Scale = None, ObjectData = None, ParentID = None, UpdateFlags = None, PathCurve = None, ProfileCurve = None, PathBegin = None, PathEnd = None, PathScaleX = None, PathScaleY = None, PathShearX = None, PathShearY = None, PathTwist = None, PathTwistBegin = None, PathRadiusOffset = None, PathTaperX = None, PathTaperY = None, PathRevolutions = None, PathSkew = None, ProfileBegin = None, ProfileEnd = None, ProfileHollow = None, TextureEntry = None, TextureAnim = None, NameValue = None, Data = None, Text = None, TextColor = None, MediaURL = None, PSBlock = None, ExtraParams = None, Sound = None, OwnerID = None, Gain = None, Flags = None, Radius = None, JointType = None, JointPivot = None, JointAxisOrAnchor = None, FootCollisionPlane = None, Position = None, Velocity = None, Acceleration = None, Rotation = None, AngularVelocity = None):
        """ set up the object attributes """

        self.LocalID = LocalID                                 # U32
        self.State = State                           # U8
        self.FullID = FullID        # LLUUID
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
        self.Sound = Sound                           # LLUUID
        self.OwnerID = OwnerID                       # LLUUID // HACK object's owner id, only set if non-null sound, for muting
        self.Gain = Gain                             # F32
        self.Flags = Flags                           # U8
        self.Radius = Radius                         # F32 // cutoff radius
        self.JointType = JointType                   # U8
        self.JointPivot = JointPivot                 # LLVector3
        self.JointAxisOrAnchor = JointAxisOrAnchor   # LLVector3

        # from ObjectUpdateCompressed
        self.FootCollisionPlane = FootCollisionPlane
        self.Position = Position
        self.Velocity = Velocity
        self.Acceleration = Acceleration
        self.Rotation = Rotation
        self.AngularVelocity = AngularVelocity

        # from ObjectProperties
        self.CreatorID = None
        self.GroupID = None
        self.CreationDate = None
        self.BaseMask = None
        self.OwnerMask = None
        self.GroupMask = None
        self.EveryoneMask = None
        self.NextOwnerMask = None
        self.OwnershipCost = None
        # TaxRate
        self.SaleType = None
        self.SalePrice = None
        self.AggregatePerms = None
        self.AggregatePermTextures = None
        self.AggregatePermTexturesOwner = None
        self.Category = None
        self.InventorySerial = None
        self.ItemID = None
        self.FolderID = None
        self.FromTaskID = None
        self.LastOwnerID = None
        self.Name = None
        self.Description = None
        self.TouchName = None
        self.SitName = None
        self.TextureID = None

    def update_object_permissions(self, agent, Field, Set, Mask, Override = False):
        """ update permissions for a list of objects

        This will update a specific bit to a specific value.
        """

        self.send_ObjectPermissions(agent, agent.agent_id, agent.session_id, Field, Set, Mask, Override)

    def send_ObjectPermissions(self, agent, AgentID, SessionID, Field, Set, Mask, Override):
        """ send an ObjectPermissions message to the host simulator"""

        # Todo: ObjectData is variable
        # in the future when making this message not be Object() specific
        # make it such that one can pass in a dictionary containing
        # a list of attributes to build the *[Block()]

        packet = Message('ObjectPermissions',
                        Block('AgentData',
                                AgentID = AgentID,
                                SessionID = SessionID),
                        Block('HeaderData',
                                Override = Override),
                        Block('ObjectData',
                                ObjectLocalID = self.LocalID,
                                Field = Field,
                                Set = Set,
                                Mask = Mask))

        agent.region.enqueue_message(packet)

    def set_object_full_permissions(self, agent):
        """ 
        Set Next Owner Permissions Copy, Modify, Transfer 
        This is also called 'full permissions'.
        """

        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 1, PermissionsMask.Copy)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 1, PermissionsMask.Modify)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 1, PermissionsMask.Transfer)

    def set_object_copy_mod_permissions(self, agent):
        """ 
        Set Next Owner Permissions to Copy/Mod
        This is a common permission set for attachements.
        """

        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 1, PermissionsMask.Copy)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 1, PermissionsMask.Modify)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 0, PermissionsMask.Transfer)

    def set_object_mod_transfer_permissions(self, agent):
        """
        Set Next Owner Permissions to Mod/Transfer
        This is a common permission set for clothing.
        """

        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 0, PermissionsMask.Copy)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 1, PermissionsMask.Modify)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 1, PermissionsMask.Transfer)

    def set_object_transfer_only_permissions(self, agent):
        """
        Set Next Owner Permissions to Transfer Only
        This is the most restrictive set of permissions allowed.
        """

        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 0, PermissionsMask.Copy)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 0, PermissionsMask.Modify)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 1, PermissionsMask.Transfer)

    def set_object_copy_transfer_permissions(self, agent):
        """
        Set Next Owner Permissions to Copy/Transfer
        """

        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 1, PermissionsMask.Copy)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 0, PermissionsMask.Modify)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 1, PermissionsMask.Transfer)

    def set_object_copy_only_permissions(self, agent):
        """
        Set Next Owner Permissions to Copy Only
        """

        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 1, PermissionsMask.Copy)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 0, PermissionsMask.Modify)
        self.update_object_permissions(agent, PermissionsTarget.NextOwner, 0, PermissionsMask.Transfer)

    def set_object_name(self, agent, Name):
        """ update the name of an object 

        """

        self.send_ObjectName(agent, agent.agent_id, agent.session_id, {1:[self.LocalID, Name]})

    def send_ObjectName(self, agent, AgentID, SessionID, LocalID_Name_map):
        """ send on ObjectName message to the host simulator 

        expects LocalID_Name_map = {1:[LocalID, Name]}
        """

        packet = Message('ObjectName',
                        Block('AgentData',
                                AgentID = AgentID,
                                SessionID = SessionID),
                        *[Block('ObjectData',
                                LocalID = LocalID_Name_map[item][0],
                                Name = LocalID_Name_map[item][1]) for item in LocalID_Name_map])

        agent.region.enqueue_message(packet)

    def set_object_description(self, agent, Description):
        """ update the description of an objects 

        """

        self.send_ObjectDescription(agent, agent.agent_id, agent.session_id, {1:[self.LocalID, Description]})

    def send_ObjectDescription(self, agent, AgentID, SessionID, LocalID_Description_map):
        """ send on ObjectDescription message to the host simulator 

        expects LocalID_Description_map = {1:[LocalID, Description]}
        """

        packet = Message('ObjectDescription',
                        Block('AgentData',
                                AgentID = AgentID,
                                SessionID = SessionID),
                        *[Block('ObjectData',
                                LocalID = LocalID_Description_map[item][0],
                                Description = LocalID_Description_map[item][1]) for item in LocalID_Description_map])

        agent.region.enqueue_message(packet)

    def derez(self, agent, destination, destinationID, transactionID, GroupID, PacketCount = 1, PacketNumber = 0):
        """ derez an object, specifying the destination """

        self.send_DerezObject(agent, agent.agent_id, agent.session_id, GroupID, destination, destinationID, transactionID, PacketCount, PacketNumber, self.LocalID)

    def send_DerezObject(self, agent, AgentID, SessionID, GroupID, Destination, DestinationID, TransactionID, PacketCount, PacketNumber, ObjectLocalID):
        """ send a DerezObject message to the host simulator """

        packet = Message('DerezObject',
                        Block('AgentData',
                                AgentID = AgentID,
                                SessionID = SessionID),
                        Block('AgentBlock',
                                GroupID = GroupID,
                                Destination = Destination,
                                DestinationID = DestinationID,
                                TransactionID = TransactionID,
                                PacketCount = PacketCount,
                                PacketNumber = PacketNumber),
                        Block('ObjectData',
                                ObjectLocalID = ObjectLocalID))

        agent.region.enqueue_message(packet)

    def take(self, agent):
        """ take object into inventory """

        parent_folder = self.FolderID

        # Check if we have inventory turned on
        if not(parent_folder and agent.settings.ENABLE_INVENTORY_MANAGEMENT):
            log(WARNING,"Inventory not available, please enable settings.ENABLE_INVENTORY_MANAGEMENT")
            return 

        if not(parent_folder):
            # locate Object folder
            objects_folder = [ folder for folder in agent.inventory.folders if folder.Name == 'Objects' ]
            if objects_folder:
                parent_folder = objects_folder[0].FolderID
            else:
                log(ERROR,"Unable to locate top-level Objects folder to take item into inventory.")
                return

        self.derez(agent, 4, parent_folder, uuid.uuid4(), agent.ActiveGroupID)

    def select(self, agent):
        """ select an object

        """

        self.send_ObjectSelect(agent, agent.agent_id, agent.session_id, [self.LocalID])

    def send_ObjectSelect(self, agent, AgentID, SessionID, ObjectLocalIDs):
        """ send an ObjectSelect message to the agent's host simulator
        
        expects a list of ObjectLocalIDs """

        packet = Message('ObjectSelect',
                        Block('AgentData',
                                AgentID = AgentID,
                                SessionID = SessionID),
                        *[Block('ObjectData',
                                ObjectLocalID = ObjectLocalID) for ObjectLocalID in ObjectLocalIDs])

        agent.region.enqueue_message(packet)

    def deselect(self, agent):
        """ deselect an object

        """

        self.send_ObjectDeselect(agent, agent.agent_id, agent.session_id, [self.LocalID])

    def send_ObjectDeselect(self, agent, AgentID, SessionID, ObjectLocalIDs):
        """ send an ObjectDeselect message to the agent's host simulator

        expects a list of ObjectLocalIDs """

        packet = Message('ObjectDeselect',
                        Block('AgentData',
                                AgentID = AgentID,
                                SessionID = SessionID),
                        *[Block('ObjectData',
                                ObjectLocalID = ObjectLocalID) for ObjectLocalID in ObjectLocalIDs])

        agent.region.enqueue_message(packet)

        
    def _update_properties(self, properties):
        """ takes a dictionary of attribute:value and makes it so """

        for attribute in properties.keys():

            setattr(self, attribute, properties[attribute])

        


