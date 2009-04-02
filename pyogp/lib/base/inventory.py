"""
@file inventory.py
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
import re

# related
import uuid

# pyogp
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.message.packets import *

# initialize logging
logger = getLogger('pyogp.lib.base.inventory')
log = logger.log

class Inventory(object):
    """ is an inventory container 

    Initialize the event queue client class
    >>> inventory = Inventory()

    Sample implementations: agent.py
    Tests: tests/test_inventory.py
    """

    def __init__(self, agent = None, settings = None):
        """ set up the inventory manager """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        self.agent = agent

        # For now, store the inventory contents in a list
        #     of folders with it's contents list containing it's inventory items
        # Ditto the library

        self.folders = []
        self.library_folders = []

        # the root inventory and library root folder are special cases
        self.inventory_root = None
        self.library_root = None

        if self.settings.LOG_VERBOSE: log(INFO, "Initializing inventory storage")

    def _parse_folders_from_login_response(self):
        """ the login response may contain inventory information, append data to our folders list """

        if self.settings.LOG_VERBOSE: log(DEBUG, 'Parsing the login response for inventory folders')

        if self.agent.login_response.has_key('inventory-skeleton'):
            [self._add_inventory_folder(folder) for folder in self.agent.login_response['inventory-skeleton']]

        if self.agent.login_response.has_key('inventory-skel-lib'):
            [self._add_inventory_folder(folder) for folder in self.agent.login_response['inventory-skel-lib']]

    def _add_inventory_item(self, inventory_item):
        """ inventory items comes from packets """

        # replace an existing list member, else, append
        # for now, we are assuming the parent folder exists.
        # if it doesn't we'll know via traceback

        index = [self.folders.index(folder) for folder in self.folders if folder.FolderID == inventory_item.FolderID]

        # did not find a folder for this item
        # this is probably a case we are not handling correctly
        if len(index) == 0:
            if self.settings.LOG_VERBOSE: log(DEBUG, 'Did not find parent folder %s for Inventory Item %s: %s' % (inventory_item.ItemID, inventory_item.FolderID, inventory_item.Name))
            return

        try:

            inventory_index = [self.folders[index].index(item) for item in self.folders[index].inventory]

            self.folders[index[0]].inventory[inventory_index[0]] = inventory_item

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Replacing a stored inventory item: %s for agent \'%s\'' % (inventory_item.ItemID, self.agent.agent_id))

        except:

            self.folders[index[0]].inventory.append(inventory_item)

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Storing a new inventory item: %s in agent \'%s\'' % (inventory_item.ItemID, self.agent.agent_id))

    def search_inventory(self, folder_list = [], item_id = None, name = None, match_list = []):
        """ search through all inventory folders for an id(uuid) or Name, and
        return a list of matching InventoryItems or InventoryFolders

        recursive search, based on folder_id. if no folder id is specified
        look through everything in self.folders

        This does not request inventory from the grid. It could, were we to go about enabling this...
        """ 

        # search our inventory storage if we aren't told what to look in
        if folder_list == []: 
            search_folders = self.folders
        else:
            search_folders = folder_list

        if item_id != None:

            item_id = uuid.UIUD(str(item_id))

            for item in search_folders:

                if str(type(item)) == '<class \'pyogp.lib.base.inventory.InventoryItem\'>':
                    if uuid.UIUD(str(item.ItemID)) == item_id:
                        match_list.append(item)

                elif str(type(item)) == '<class \'pyogp.lib.base.inventory.InventoryFolder\'>':
                    matches = self.search_inventory_folder(item.FolderID, _id = item_id)
                    match_list.extend(matches)

            return match_list

        elif name != None:

            for item in search_folders:

                pattern = re.compile(name)

                if str(type(item)) == '<class \'pyogp.lib.base.inventory.InventoryItem\'>':
                    if pattern.match(item.Name):
                        match_list.append(item)

                elif str(type(item)) == '<class \'pyogp.lib.base.inventory.InventoryFolder\'>':
                    matches = self.search_inventory_folder(item.FolderID, name = name.strip())
                    match_list.extend(matches)

            return match_list

        else:

            # return an empty list
            return []

    def search_inventory_folder(self, folder_id, _id = None, name = None):
        """ search an inventory folder for _id or name

        return a list of matches
        """ 

        match_list = []

        search_folder = [folder for folder in self.folders if folder.FolderID == folder_id][0]

        for item in search_folder.inventory:

            if _id != None:

                if str(type(item)) == '<class \'pyogp.lib.base.inventory.InventoryItem\'>':
                    if item.ItemID == _id:
                        match_list.append(item)

                elif str(type(item)) == '<class \'pyogp.lib.base.inventory.InventoryFolder\'>':
                    if item.FolderID== _id:
                        match_list.append(item)

            elif name != None:

                pattern = re.compile(name)

                if pattern.match(item.Name):
                    match_list.append(item)

        return match_list

    def _add_inventory_folder(self, folder_data):
        """ inventory folder data comes from either packets or login """

        # if it's a dict, we are parsing login response data
        if type(folder_data) == dict:

            if self.settings.LOG_VERBOSE: log(DEBUG, "Adding inventory folder %s" % (folder_data['name']))

            folder = InventoryFolder(folder_data['name'], folder_data['folder_id'], folder_data['parent_id'], folder_data['version'], folder_data['type_default'])

            self.folders.append(folder)

            if folder_data['parent_id'] == '00000000-0000-0000-0000-000000000000' and folder_data['name'] == 'My Inventory':
                self.inventory_root = folder

            elif folder_data['parent_id'] == '00000000-0000-0000-0000-000000000000' and folder_data['name'] == 'Library':
                self.library_root = folder

        # otherwise, we are adding an InventoryFolder() instance
        else:

            if self.settings.LOG_VERBOSE: log(DEBUG, "Adding inventory folder %s" % (folder_data.Name))

            self.folders.append(folder_data)

    def display_folder_contents(self, folder_id = None, name = None):
        """ returns a list of the local representation of a folder's contents """

        if folder_id != None:

            return [member for member in self.folders if member.ParentID == folder_id]

        # the name case is not handled at this time
        '''
        elif name != None:

            folder_ids = [member.folder_id for member in self.contents if member.name == name]

            return [member for member in self.contents if member.name == name]
        '''

    def request_known_folder_contents(self, folder_id = None):
        """ send requests to the server for contents of all known folders """

        [self.inventory._request_folder_contents(folder.FolderID) for folder in self.inventory.folders if folder.ParentID == self.inventory.inventory_root.FolderID]

    def _request_folder_contents(self, folder_id = None, name = None):
        """ send a request to the server for folder contents, wraps sendFetchInventoryDescendentsPacket """

        self.sendFetchInventoryDescendentsPacket(folder_id = folder_id)

    def request_inventory_by_id(self, id_list = None):
        """ ask for inventory data by id via a list """

        if id_list != None:

            packet = FetchInventoryPacket()

            # AgentData block
            packet.AgentData['AgentID'] = uuid.UUID(str(self.agent.agent_id))    # MVT_LLUUID
            packet.AgentData['SessionID'] = uuid.UUID(str(self.agent.session_id))    # MVT_LLUUID

            for inventory_id in id_list:

                InventoryData = {}
                InventoryData['OwnerID'] = uuid.UUID(str(self.agent.agent_id))    # MVT_LLUUID
                InventoryData['ItemID'] = uuid.UUID(str(inventory_id))    # MVT_LLUUID

                packet.InventoryDataBlocks.append(InventoryData)

            # enqueue the message
            self.region.enqueue_message(packet())                

    def sendFetchInventoryDescendentsPacket(self, folder_id = None, name = None):
        """ send a request to the server for folder contents """

        # the name case is not handled at this time
        packet = FetchInventoryDescendentsPacket()

        # AgentData block
        packet.AgentData['AgentID'] = uuid.UUID(str(self.agent.agent_id))    # MVT_LLUUID
        packet.AgentData['SessionID'] = uuid.UUID(str(self.agent.session_id))    # MVT_LLUUID

        # InventoryData block
        packet.InventoryData['FolderID'] = uuid.UUID(str(folder_id))    # MVT_LLUUID
        packet.InventoryData['OwnerID'] = uuid.UUID(str(self.agent.agent_id))    # MVT_LLUUID
        packet.InventoryData['SortOrder'] = 0    # MVT_S32, 0 = name, 1 = time
        packet.InventoryData['FetchFolders'] = True    # MVT_BOOL
        packet.InventoryData['FetchItems'] = True    # MVT_BOOL

        self.agent.region.enqueue_message(packet())

class InventoryFolder(object):
    """ represents an Inventory folder 

    Initialize the event queue client class
    >>> inventoryfolder = InventoryFolder()

    Sample implementations: inventory.py
    Tests: tests/test_inventory.py
    """

    def __init__(self, Name = None, FolderID = None, ParentID = None, Version = None, Type = None):
        """ initialize the inventory folder """

        self.type = 'InventoryFolder'

        self.Name = Name
        self.FolderID = uuid.UUID(str(FolderID))
        self.ParentID = uuid.UUID(str(ParentID))
        self.Version = Version
        self.Type = Type

        self.inventory = []

class InventoryItem(object):
    """ represents an Inventory item 

    Initialize the InventoryItem class
    >>> inventoryitem = InventoryItem()

    Sample implementations: inventory.py
    Tests: tests/test_inventory.py
    """

    def __init__(self, ItemID = None, FolderID = None, CreatorID = None, OwnerID = None, GroupID = None, BaseMask = None, OwnerMask = None, GroupMask = None, EveryoneMask = None, NextOwnerMask = 0, GroupOwned = None, AssetID = None, Type = None, InvType = None, Flags = None, SaleType = None, SalePrice = None, Name = None, Description = None, CreationDate = None, CRC = None):
        """ initialize the inventory item """

        self.type = 'InventoryItem'

        self.ItemID = uuid.UUID(str(ItemID))            # LLUUID
        self.FolderID = uuid.UUID(str(FolderID))        # LLUUID
        self.CreatorID = uuid.UUID(str(CreatorID))      # LLUUID
        self.OwnerID = uuid.UUID(str(OwnerID))          # LLUUID
        self.GroupID = uuid.UUID(str(GroupID))          # LLUUID
        self.BaseMask = BaseMask                        # U32
        self.OwnerMask = OwnerMask                      # U32
        self.GroupMask = GroupMask                      # U32
        self.EveryoneMask = EveryoneMask                # U32
        self.NextOwnerMask = NextOwnerMask 
        self.GroupOwned = GroupOwned                    # Bool
        self.AssetID = uuid.UUID(str(AssetID))          # LLUUID
        self.Type = Type                                # S8
        self.InvType = InvType                          # S8
        self.Flags = Flags                              # U32
        self.SaleType = SaleType                        # U8
        self.SalePrice = SalePrice                      # S32
        self.Name = Name                                # Variable 1
        self.Description = Description                  # Variable 1
        self.CreationDate = CreationDate                # S32
        self.CRC = CRC                                  # U32

    def rez_object(self, agent, relative_position = (1, 0, 0)):

        # self.agent.Position holds where we are. we need to add this Vector3 to the incoming tuple (vector to a vector)
        location_to_rez_x = agent.Position.X + relative_position[0]
        location_to_rez_y = agent.Position.Y  + relative_position[1]
        location_to_rez_z = agent.Position.Z + relative_position[2]

        location_to_rez = (location_to_rez_x, location_to_rez_y, location_to_rez_z)

        sendRezObject(agent, self, location_to_rez, location_to_rez)

    def update(agent, name = None, value = None):
        """ allow arbitraty update to any data in the inventory item """

        if self.__dict__.has_key(name):
            self.setattr(self, name, value)
            sendUpdateInventoryItem(agent, [self])
        else:
            raise DataParsingError('Inventory item attribute update failes, no field named \'%s\'' % (name))

# ~~~~~~~~~~~~~~~
# Packet Wrappers
# ~~~~~~~~~~~~~~~

def sendUpdateInventoryItem(agent, inventory_items = [], ):
    """ sends an UpdateInventoryItem packet to a region 

    this function expects an already transformed InventoryItem instance
    """

    packet - UpdateInventoryItemPacket()

    packet.AgentData["AgentID"] = uuid.UUID(str(agent.agent_id))
    packet.AgentData["SessionID"] = uuid.UUID(str(agent.session_id))
    packet.AgentData["TransactionID"] = uuid.UUID('00000000-0000-0000-0000-000000000000')

    for item in inventory_items:

        packet.InventoryData['ItemID'] = uuid.UUID(str(item.ItemID))
        packet.InventoryData['FolderID'] = uuid.UUID(str(item.FolderID))
        packet.InventoryData['CallbackID'] = uuid.UUID('00000000-0000-0000-0000-000000000000')
        packet.InventoryData['CreatorID'] = uuid.UUID(str(item.CreatorID))
        packet.InventoryData['OwnerID'] = uuid.UUID(str(item.OwnerID))
        packet.InventoryData['GroupID'] = uuid.UUID(str(item.GroupID))
        packet.InventoryData['BaseMask'] = item.BaseMask
        packet.InventoryData['OwnerMask'] = item.OwnerMask
        packet.InventoryData['GroupMask'] = item.GroupMask
        packet.InventoryData['EveryoneMask'] = item.EveryoneMask
        packet.InventoryData['NextOwnerMask'] = item.NextOwnerMask
        packet.InventoryData['GroupOwned'] = item.GroupOwned
        packet.InventoryData['TransactionID'] = uuid.UUID('00000000-0000-0000-0000-000000000000')
        packet.InventoryData['Type'] = item.Type 
        packet.InventoryData['InvType'] = item.InvType
        packet.InventoryData['Flags'] = item.Flags
        packet.InventoryData['SaleType'] = item.SaleType
        packet.InventoryData['SalePrice'] = item.SalePrice
        packet.InventoryData['Name'] = item.Name
        packet.InventoryData['Description'] = item.Description
        packet.InventoryData['CreationDate'] = item.CreationDate
        packet.InventoryData['CRC'] = item.CRC

    agent.region.enqueue_message(packet())

def sendRezObject(agent, inventory_item, RayStart, RayEnd, FromTaskID = uuid.UUID('00000000-0000-0000-0000-000000000000'), BypassRaycast = 1,  RayTargetID = uuid.UUID('00000000-0000-0000-0000-000000000000'), RayEndIsIntersection = False, RezSelected = False, RemoveItem = False, ItemFlags = 0, GroupMask = 0, EveryoneMask = 0, NextOwnerMask = 0):
    """ sends a RezObject packet to a region """

    packet = RezObjectPacket()

    packet.AgentData['AgentID'] = uuid.UUID(str(agent.agent_id))
    packet.AgentData['SessionID'] = uuid.UUID(str(agent.session_id))
    packet.AgentData['GroupID'] = uuid.UUID(str(agent.ActiveGroupID))

    packet.RezData['FromTaskID'] = uuid.UUID(str(FromTaskID))
    packet.RezData['BypassRaycast'] = BypassRaycast     # ???
    packet.RezData['RayStart'] = RayStart
    packet.RezData['RayEnd'] = RayEnd
    packet.RezData['RayTargetID'] = uuid.UUID(str(RayTargetID))
    packet.RezData['RayEndIsIntersection'] = RayEndIsIntersection
    packet.RezData['RezSelected'] = RezSelected
    packet.RezData['RemoveItem'] = RemoveItem
    packet.RezData['ItemFlags'] = ItemFlags
    packet.RezData['GroupMask'] = GroupMask
    packet.RezData['EveryoneMask'] = EveryoneMask
    packet.RezData['NextOwnerMask'] = inventory_item.NextOwnerMask

    packet.InventoryData['ItemID'] = uuid.UUID(str(inventory_item.ItemID))
    packet.InventoryData['FolderID'] = uuid.UUID(str(inventory_item.FolderID))
    packet.InventoryData['CreatorID'] = uuid.UUID(str(inventory_item.CreatorID))
    packet.InventoryData['OwnerID'] = uuid.UUID(str(inventory_item.OwnerID))
    packet.InventoryData['GroupID'] = uuid.UUID(str(inventory_item.GroupID))
    packet.InventoryData['BaseMask'] = inventory_item.BaseMask
    packet.InventoryData['OwnerMask'] = inventory_item.OwnerMask
    packet.InventoryData['GroupMask'] = inventory_item.GroupMask
    packet.InventoryData['EveryoneMask'] = inventory_item.EveryoneMask
    packet.InventoryData['GroupOwned'] = inventory_item.GroupOwned
    packet.InventoryData['TransactionID'] = uuid.UUID('00000000-0000-0000-0000-000000000000')
    packet.InventoryData['Type'] = inventory_item.Type 
    packet.InventoryData['InvType'] = inventory_item.InvType
    packet.InventoryData['Flags'] = inventory_item.Flags
    packet.InventoryData['SaleType'] = inventory_item.SaleType
    packet.InventoryData['SalePrice'] = inventory_item.SalePrice
    packet.InventoryData['Name'] = inventory_item.Name
    packet.InventoryData['Description'] = inventory_item.Description
    packet.InventoryData['CreationDate'] = inventory_item.CreationDate
    packet.InventoryData['CRC'] = inventory_item.CRC
    packet.InventoryData['NextOwnerMask'] = inventory_item.NextOwnerMask

    agent.region.enqueue_message(packet())

