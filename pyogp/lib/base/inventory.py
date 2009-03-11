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

        # the root inventory and library root folder are special cases
        self.inventory_root = None
        self.library_root = None

        # set up callbacks
        if self.settings.HANDLE_PACKETS:
            if self.agent != None:
                self.packet_handler = self.agent.packet_handler
            else:
                from pyogp.lib.base.message.packethandler import PacketHandler
                self.packet_handler = PacketHandler()

            onInventoryDescendents_received = self.packet_handler._register('InventoryDescendents')
            onInventoryDescendents_received.subscribe(onInventoryDescendents, self)     

            onFetchInventoryReply_received = self.packet_handler._register('FetchInventoryReply')
            onFetchInventoryReply_received.subscribe(onFetchInventoryReply, self)

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

        try:

            inventory_index = [self.folders[index].index(item) for item in self.folders[index].inventory]

            self.folders[index[0]].inventory[inventory_index[0]] = inventory_item

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Replacing a stored inventory item: %s for agent \'%s\'' % (inventory_item.ItemID, self.agent.agent_id))

        except:

            self.folders[index[0]].inventory.append(inventory_item)

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Storing a new inventory item: %s in agent \'%s\'' % (inventory_item.ItemID, self.agent.agent_id))

    def search_inventory_by_id(self, item_id):
        """ search through all inventory folders for a uuid, return the match, or None if no match """ 

        pass


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

    def __init__(self, ItemID = None, FolderID = None, CreatorID = None, OwnerID = None, GroupID = None, BaseMask = None, OwnerMask = None, GroupMask = None, EveryoneMask = None, NextOwnerMask = None, GroupOwned = None, AssetID = None, Type = None, InvType = None, Flags = None, SaleType = None, SalePrice = None, Name = None, Description = None, CreationDate = None, CRC = None):
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
        self.NextOwnerMask = NextOwnerMask              # U32
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

#~~~~~~~~~~
# Callbacks
#~~~~~~~~~~

def onInventoryDescendents(packet, inventory):

    if packet.message_data.blocks['AgentData'][0].get_variable('Descendents') > 0:

        _agent_id = packet.message_data.blocks['AgentData'][0].get_variable('AgentID')
        _agent_id = packet.message_data.blocks['AgentData'][0].get_variable('AgentID')
        _folder_id = packet.message_data.blocks['AgentData'][0].get_variable('FolderID')
        _owner_id = packet.message_data.blocks['AgentData'][0].get_variable('OwnerID')
        _version = packet.message_data.blocks['AgentData'][0].get_variable('Version')
        _descendents = packet.message_data.blocks['AgentData'][0].get_variable('Descendents')

        if packet.message_data.blocks['ItemData'][0].get_variable('FolderID').data != uuid.UUID('00000000-0000-0000-0000-000000000000'):

            for ItemData_block in packet.message_data.blocks['ItemData']:

                _ItemID = ItemData_block.get_variable('ItemID').data
                _FolderID = ItemData_block.get_variable('FolderID').data
                _CreatorID = ItemData_block.get_variable('CreatorID').data
                _OwnerID = ItemData_block.get_variable('OwnerID').data
                _GroupID = ItemData_block.get_variable('GroupID').data
                _BaseMask = ItemData_block.get_variable('BaseMask').data
                _OwnerMask = ItemData_block.get_variable('OwnerMask').data
                _GroupMask = ItemData_block.get_variable('GroupMask').data
                _EveryoneMask = ItemData_block.get_variable('EveryoneMask').data
                _NextOwnerMask = ItemData_block.get_variable('NextOwnerMask').data
                _GroupOwned = ItemData_block.get_variable('GroupOwned').data
                _AssetID = ItemData_block.get_variable('AssetID').data
                _Type = ItemData_block.get_variable('Type').data
                _InvType = ItemData_block.get_variable('InvType').data
                _Flags = ItemData_block.get_variable('Flags').data
                _SaleType = ItemData_block.get_variable('SaleType').data
                _SalePrice = ItemData_block.get_variable('SalePrice').data
                _Name = ItemData_block.get_variable('Name').data
                _Description = ItemData_block.get_variable('Description').data
                _CreationDate = ItemData_block.get_variable('CreationDate').data
                _CRC = ItemData_block.get_variable('CRC').data

                inventory_item = InventoryItem(_ItemID, _FolderID, _CreatorID, _OwnerID, _GroupID, _BaseMask, _OwnerMask, _GroupMask, _EveryoneMask, _NextOwnerMask, _GroupOwned, _AssetID, _Type, _InvType, _Flags, _SaleType, _SalePrice, _Name, _Description, _CreationDate, _CRC)

                inventory._add_inventory_item(inventory_item)

        if packet.message_data.blocks['FolderData'][0].get_variable('FolderID').data != uuid.UUID('00000000-0000-0000-0000-000000000000'):

            for FolderData_block in packet.message_data.blocks['FolderData']:

                _FolderID = FolderData_block.get_variable('FolderID').data
                _ParentID = FolderData_block.get_variable('ParentID').data
                _Type = FolderData_block.get_variable('Type').data
                _Name = FolderData_block.get_variable('Name').data

                folder = InventoryFolder( _Name, _FolderID, _ParentID, None, _Type)
                
                inventory._add_inventory_folder(folder)

def onFetchInventoryReply(packet, inventory):

    _agent_id = packet.message_data.blocks['AgentData'][0].get_variable('AgentID')

    for InventoryData_block in packet.message_data.blocks['InventoryData']:

        _ItemID = InventoryData_block.get_variable('ItemID').data
        _FolderID = InventoryData_block.get_variable('FolderID').data
        _CreatorID = InventoryData_block.get_variable('CreatorID').data
        _OwnerID = InventoryData_block.get_variable('OwnerID').data
        _GroupID = InventoryData_block.get_variable('GroupID').data
        _BaseMask = InventoryData_block.get_variable('BaseMask').data
        _OwnerMask = InventoryData_block.get_variable('OwnerMask').data
        _GroupMask = InventoryData_block.get_variable('GroupMask').data
        _EveryoneMask = InventoryData_block.get_variable('EveryoneMask').data
        _NextOwnerMask = InventoryData_block.get_variable('NextOwnerMask').data
        _GroupOwned = InventoryData_block.get_variable('GroupOwned').data
        _AssetID = InventoryData_block.get_variable('AssetID').data
        _Type = InventoryData_block.get_variable('Type').data
        _InvType = InventoryData_block.get_variable('InvType').data
        _Flags = InventoryData_block.get_variable('Flags').data
        _SaleType = InventoryData_block.get_variable('SaleType').data
        _SalePrice = InventoryData_block.get_variable('SalePrice').data
        _Name = InventoryData_block.get_variable('Name').data
        _Description = InventoryData_block.get_variable('Description').data
        _CreationDate = InventoryData_block.get_variable('CreationDate').data
        _CRC = InventoryData_block.get_variable('CRC').data

        inventory_item = InventoryItem(_ItemID, _FolderID, _CreatorID, _OwnerID, _GroupID, _BaseMask, _OwnerMask, _GroupMask, _EveryoneMask, _NextOwnerMask, _GroupOwned, _AssetID, _Type, _InvType, _Flags, _SaleType, _SalePrice, _Name, _Description, _CreationDate, _CRC)

        inventory._add_inventory_item(inventory_item)

