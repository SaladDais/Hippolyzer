
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
import re

# related
import uuid
import struct

# pyogp
from pyogp.lib.base.datatypes import UUID
from pyogp.lib.base.exc import ResourceError, ResourceNotFound, DataParsingError
from pyogp.lib.base.datamanager import DataManager

# pyogp.message
from pyogp.lib.base.message.message import Message, Block

# pyogp utilities
from pyogp.lib.base.utilities.enums import ImprovedIMDialogue

# initialize logging
logger = getLogger('pyogp.lib.base.inventory')
log = logger.log

# ToDo: handle library inventory properly. right now, it's treated as regular inv. store it in self.library_folders

class InventoryManager(DataManager):
    """ is an inventory container 

    Initialize the event queue client class
    >>> inventory = InventoryManager()

    Sample implementations: agent.py
    Tests: tests/test_inventory.py
    """

    def __init__(self, agent = None, settings = None):
        """ set up the inventory manager """
        super(InventoryManager, self).__init__(agent, settings)
        # For now, store the inventory contents in a list
        #     of folders with it's contents list containing it's inventory items
        # Ditto the library

        self.folders = []
        self.library_folders = []

        # the root inventory and library root folder are special cases
        self.inventory_root = None
        self.library_root = None

        if self.settings.LOG_VERBOSE:
            log(INFO, "Initializing inventory storage")

    def enable_callbacks(self):
        """ enable monitors for certain inventory related packet events """

        onInventoryDescendents_received = self.agent.region.message_handler.register('InventoryDescendents')
        onInventoryDescendents_received.subscribe(self.onInventoryDescendents)

        onFetchInventoryReply_received = self.agent.region.message_handler.register('FetchInventoryReply')
        onFetchInventoryReply_received.subscribe(self.onFetchInventoryReply)

        onBulkUpdateInventory_received = self.agent.region.message_handler.register('BulkUpdateInventory')
        onBulkUpdateInventory_received.subscribe(self.onBulkUpdateInventory)

    def onInventoryDescendents(self, packet):

        raise NotImplemented("onInventoryDescendents")

    def onFetchInventoryReply(self, packet):

        raise NotImplemented("onFetchInventoryReply")

    def onBulkUpdateInventory(self, packet):
        """ handle the inventory data being delivered in the BullkUpdateInventory packet """

        for FolderData_block in packet.blocks['FolderData']:

            _FolderID = FolderData_block.get_variable('FolderID').data
            _ParentID = FolderData_block.get_variable('ParentID').data
            _Type = FolderData_block.get_variable('Type').data
            _Name = FolderData_block.get_variable('Name').data

            folder = InventoryFolder( _Name, _FolderID, _ParentID, None, _Type)

            self._store_inventory_folder(folder)

        for ItemData_block in packet.blocks['ItemData']:

            # what is CallbackID??? not doing anything with it.

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

            inventory_item = InventoryItem(_ItemID,
                                            _FolderID,
                                            _CreatorID,
                                            _OwnerID,
                                            _GroupID,
                                            _BaseMask,
                                            _OwnerMask,
                                            _GroupMask,
                                            _EveryoneMask,
                                            _NextOwnerMask,
                                            _GroupOwned,
                                            _AssetID,
                                            _Type,
                                            _InvType,
                                            _Flags,
                                            _SaleType,
                                            _SalePrice,
                                            _Name,
                                            _Description,
                                            _CreationDate,
                                            _CRC)

            self._store_inventory_item(inventory_item)

    def _parse_folders_from_login_response(self):
        """ the login response may contain inventory information, append data to our folders list """

        if self.settings.LOG_VERBOSE:
            log(DEBUG, 'Parsing the login response for inventory folders')

        if self.agent.login_response.has_key('inventory-skeleton'):
            [self._store_inventory_folder(folder, 'inventory') for folder in self.agent.login_response['inventory-skeleton']]

        if self.agent.login_response.has_key('inventory-skel-lib'):
            [self._store_inventory_folder(folder, 'library') for folder in self.agent.login_response['inventory-skel-lib']]

    def _store_inventory_item(self, inventory_item, destination = 'inventory'):
        """ inventory items comes from packets, or from caps """

        if destination == 'inventory':

            container = self.folders

        elif destination == 'library':

            container = self.library_folders

        else:

            log(WARNING, 'Not storing folder data, as it\'s not bound for a valid destination.')
            return

        # replace an existing list member, else, append
        # for now, we are assuming the parent folder exists.
        # if it doesn't we'll know via traceback

        index = [container.index(folder) for folder in container if str(folder.FolderID) == str(inventory_item.FolderID)]

        # did not find a folder for this item
        # this is probably a case we are not handling correctly
        if len(index) == 0:
            if self.settings.LOG_VERBOSE:
                log(DEBUG, 'Did not find parent folder %s for Inventory Item %s: %s' % (inventory_item.ItemID, inventory_item.FolderID, inventory_item.Name))
            return

        try:

            inventory_index = [container[index].index(item) for item in container[index].inventory]

            container[index[0]].inventory[inventory_index[0]] = inventory_item

            if self.settings.LOG_VERBOSE:
                log(DEBUG, 'Replacing a stored inventory item: %s' % (inventory_item.ItemID))

        except:

            container[index[0]].inventory.append(inventory_item)

            if self.settings.LOG_VERBOSE:
                log(DEBUG, 'Storing a new inventory item: %s ' % (inventory_item.ItemID))

    def search_inventory(self, folder_list = [], item_id = None, name = None,
                         match_list = []):
        """ search through all inventory folders for an id(uuid) or Name, and
        return a list of matching InventoryItems or InventoryFolders

        recursive search, based on folder_id. if no folder id is specified
        look through everything in self.folders

        This does not request inventory from the grid. It could, were we to go about enabling this...
        """ 
        
        def match():
            _match = lambda arg : False
            if item_id != None:
                def _match(arg):
                    if isinstance(arg, InventoryItem):
                        return str(arg.ItemID) == str(item_id)
                    else:
                        return str(arg.FolderID) == str(item_id)
            elif name != None:
                pattern = re.compile(name)
                def _match(arg):
                    if pattern.match(arg.Name):
                        return True
                    else:
                        return False
            return _match

        is_match = match()

        # search our inventory storage if we aren't told what to look in
        if folder_list == []:
            search_folders = self.folders
        else:
            search_folders = folder_list

        for item in search_folders:
            if is_match(item):
                match_list.append(item)
            if isinstance(item, InventoryFolder):
                matches = self.search_inventory_folder(item.FolderID,
                                                       _id=item_id,
                                                       name=name)
                match_list.extend(matches)
        return match_list
        
    def search_inventory_folder(self, folder_id, _id = None, name = None):
        """ search an inventory folder for _id or name

        return a list of matches
        """ 
        
        match_list = []
        
        search_folder = [folder for folder in self.folders if str(folder.FolderID) == str(folder_id)][0]
        
        for item in search_folder.inventory:

            if _id != None:

                if isinstance(item, InventoryItem):
                    if str(item.ItemID) == str(_id):
                        match_list.append(item)
                elif isinstance(item, InventoryFolder):
                    if str(item.FolderID) == str(_id):
                        match_list.append(item)

            elif name != None:

                pattern = re.compile(name)

                if pattern.match(item.Name):
                    match_list.append(item)

        return match_list

    def _store_inventory_folder(self, folder_data, destination = 'inventory'):
        """ inventory folder data comes from either packets or login, or from caps. destination is either 'inventory' or 'library' """

        if destination == 'inventory':

            container = self.folders

        elif destination == 'library':

            container = self.library_folders

        else:

            log(WARNING, 'Not storing folder data, as it\'s not bound for a valid destination.')
            return

        # if it's a dict, we are parsing login response data or a caps response
        # transform to an InventoryFolder() instance and store it if we havne't already stored it, otherwise, update the params
        if type(folder_data) == dict:

            if folder_data.has_key('category_id'):

                # this is from caps

                folder = InventoryFolder(folder_data['name'], folder_data['category_id'], folder_data['parent_id'], folder_data['version'], folder_data['type_default'], folder_data['agent_id'])

            else:
 
                # this is from login inv skeleton
    
                folder = InventoryFolder(folder_data['name'], folder_data['folder_id'], folder_data['parent_id'], folder_data['version'], folder_data['type_default'])

        elif isinstance(folder_data, InventoryFolder):

            folder = folder_data

        # see if we have already stored this folder
        index = [container.index(target_folder) for target_folder in container if str(folder.FolderID) == str(target_folder.FolderID)]

        # skip storing folders we already know about
        if len(index) == 1:

            # we may be receiving an update to the folder attributes, if so, save off the contents, swap in the new representation, then append the contents

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Replacing a stored inventory folder: %s for agent \'%s\'' % (folder.FolderID, self.agent.agent_id))

            contents = container[index[0]].inventory

            container[index[0]] = folder

            container[index[0]].inventory = contents

        else:

            if self.settings.LOG_VERBOSE: log(DEBUG, "Storing inventory folder %s" % (folder.Name))

            if folder_data['parent_id'] == '00000000-0000-0000-0000-000000000000' and folder_data['name'] == 'My Inventory':

                self.inventory_root = folder

            elif folder_data['parent_id'] == '00000000-0000-0000-0000-000000000000' and folder_data['name'] == 'Library':

                self.library_root = folder

            container.append(folder)

    def display_folder_contents(self, folder_id = None):
        """ returns a list of the local representation of a folder's contents """

        if folder_id != None:

            return [member for member in self.folders if str(member.ParentID) == str(folder_id)]

        # the name case is not handled at this time
        '''
        elif name != None:

            folder_ids = [member.folder_id for member in self.contents if member.name == name]

            return [member for member in self.contents if member.name == name]
        '''

    def request_known_folder_contents(self, folder_id = None):
        """ send requests to the server for contents of all known folders """

        [self.inventory._request_folder_contents(folder.FolderID) for folder in self.inventory.folders if str(folder.ParentID) == str(self.inventory.inventory_root.FolderID)]

    def _request_folder_contents(self, folder_id = None, source = 'inventory'):
        """ send a request to the server for folder contents, wraps sendFetchInventoryDescendentsPacket """

        if source == 'inventory':

            self.sendFetchInventoryDescendentsRequest(folder_id = folder_id)

        elif source == 'library':

            self.sendFetchLibDescendentsRequest(folder_id = folder_id)

    def request_inventory_by_id(self, id_list = None):
        """ ask for inventory data by id via a list """

        if id_list != None:

            self.send_FetchInventory(self.agent.agent_id, self.agent.session_id, self.agent.agent_id, id_list)

    def send_FetchInventory(self, agent_id, session_id, owner_id, inventory_ids):
        """
        send a FetchInventory message to the host simulator 
        each of the ids in inventory_ids will be sent in it's own InventoryData block
        """

        packet = Message('FetchInventory',
                        Block('AgentData',
                                AgentID = agent_id,
                                SessionID = session_id),
                        *[Block('InventoryData',
                                OwnerID = owner_id,
                                ItemID = item_id) for item_id in inventory_ids])

        # enqueue the message
        self.region.enqueue_message(packet)

    def give_inventory(self, ItemID = None, agent_id = None):
        """ offers another agent the specified inventory item 
        
        searches the local inventory for the specified ItemID
        given a match, sends an ImprovedInventoryMessage packet to the specified AgentID
        """

        if not (ItemID or agent_id):
            log(WARNING, "ItemID and agent_id are required in InventoryManager().give_inventory()")
            return

        item_id = self.search_inventory(item_id = ItemID)

        if item_id == []:
            log(WARNING, "ItemID %s not found in inventory of %s" % (ItemID, self.agent.Name()))
            return
        elif len(item_id) > 1:
            log(WARNING, "Multiple matches in inventory for ItemID %s, using the first one in InventoryManager().give_inventory()" % (ItemID))

        inv_item = item_id[0]

        inv_item.give(self.agent, agent_id)

    def handle_inventory_offer(self, packet):
        """ parses and handles an incoming inventory offer """

        FromAgentID = packet.blocks['AgentData'][0].get_variable('AgentID').data
        FromAgentName = packet.blocks['MessageBlock'][0].get_variable('FromAgentName').data
        InventoryName = packet.blocks['MessageBlock'][0].get_variable('Message').data
        ID = packet.blocks['MessageBlock'][0].get_variable('ID').data
        _Message = packet.blocks['MessageBlock'][0].get_variable('Message').data
        ToAgentID = packet.blocks['MessageBlock'][0].get_variable('ToAgentID').data

        BinaryBucket = packet.blocks['MessageBlock'][0].get_variable('BinaryBucket').data

        # parse the binary bucket
        AssetType = struct.unpack(">b", BinaryBucket[0:1])[0]
        ItemID =  UUID(BinaryBucket[1:17])

        if str(FromAgentID) == str(self.agent.agent_id):

            log(INFO, "%s offered inventory to %s" % (self.agent.Name(), ToAgentID))

        else:

            log(INFO, "%s received an inventory offer from %s for %s." % (self.agent.Name(), FromAgentName, InventoryName))

            if self.settings.LOG_VERBOSE:
                log(DEBUG, "Inventory offer data. \n\tFromAgentID: %s \n\tFromAgentName: %s \n\tInventoryName: %s \n\tID: %s \n\tAssetType: %s \n\tItemID: %s \n\tMessage: %s" % (FromAgentID, FromAgentName, InventoryName, ID, AssetType, ItemID, Message))

        if self.agent.settings.ACCEPT_INVENTORY_OFFERS:

            accept = True

        else:

            accept = False

        self.confirm_inventory_offer(FromAgentID, FromAgentName, InventoryName, ID, AssetType, ItemID, accept)

    def confirm_inventory_offer(self, FromAgentID, FromAgentName, InventoryName, ID, AssetType, ItemID, accept):
        """ sends an ImprovedInstantMessage packet accepting or declining an inventory offer """

        if accept:
            accept_key = ImprovedIMDialogue.InventoryAccepted
            log(INFO, "Sending an inventory accepted message to %s for item %s(%s)" % (FromAgentName, InventoryName, ID))
        else:
            accept_key = ImprovedIMDialogue.InventoryDeclined
            log(INFO, "Sending an inventory declined message to %s for item %s(%s)" % (FromAgentName, InventoryName, ID))

        self.agent.send_ImprovedInstantMessage(self.agent.agent_id, self.agent.session_id, 0, FromAgentID, 0, UUID(), self.agent.Position, 0, accept_key, ID, 0, self.agent.Name(), '', '')

    def create_new_item(self, folder, name, desc, asset_type, inv_type,
                        wearable_type, next_owner_permission, callback=None):
        """
        Creates a new item in folder.
        """
        transaction_id = UUID()
        transaction_id.random()
        
        updateCreateInventoryHandler = self.agent.region.message_handler.register('UpdateCreateInventoryItem')

        def onUpdateCreateInventoryItem(packet):
            if str(transaction_id) != \
                   str(packet.blocks['AgentData'][0]\
                       .get_variable('TransactionID').data):
                inv_data = packet.blocks['InventoryData'][0]
                item = InventoryItem(inv_data.get_variable('ItemID').data,
                                     inv_data.get_variable('FolderID').data,
                                     inv_data.get_variable('CreatorID').data,
                                     inv_data.get_variable('OwnerID').data,
                                     inv_data.get_variable('GroupID').data,
                                     inv_data.get_variable('BaseMask').data,
                                     inv_data.get_variable('OwnerMask').data,
                                     inv_data.get_variable('GroupMask').data,
                                     inv_data.get_variable('EveryoneMask').data,
                                     inv_data.get_variable('NextOwnerMask').data,
                                     inv_data.get_variable('GroupOwned').data,
                                     inv_data.get_variable('AssetID').data,
                                     inv_data.get_variable('Type').data,
                                     inv_data.get_variable('InvType').data,
                                     inv_data.get_variable('Flags').data,
                                     inv_data.get_variable('SaleType').data,
                                     inv_data.get_variable('SalePrice').data,
                                     inv_data.get_variable('Name').data,
                                     inv_data.get_variable('Description').data,
                                     inv_data.get_variable('CreationDate').data,
                                     inv_data.get_variable('CRC').data)
                                                                 
                self._store_inventory_item(item)
                updateCreateInventoryHandler.unsubscribe(onUpdateCreateInventoryItem)
                if callback != None:
                    callback(item)
                
        updateCreateInventoryHandler.subscribe(onUpdateCreateInventoryItem) 
        
        self.send_CreateInventoryItem(self.agent.agent_id,
                                      self.agent.session_id,
                                      0,
                                      folder.FolderID,
                                      transaction_id,
                                      next_owner_permission,
                                      asset_type,
                                      inv_type,
                                      wearable_type,
                                      name,
                                      desc)
                
    def send_CreateInventoryItem(self, agent_id, session_id, callback_id,
                                 folder_id, transaction_id, next_owner_mask,
                                 type_, inv_type, wearable_type, name, desc):
        """ sends a CreateInventoryItem message """
        args = [Block('AgentData',
                      AgentID = agent_id,
                      SessionID = session_id)]
        args += [Block('InventoryBlock',
                       CallbackID = callback_id,
                       FolderID = folder_id,
                       TransactionID = transaction_id,
                       NextOwnerMask = next_owner_mask,
                       Type = type_,
                       InvType = inv_type,
                       WearableType = wearable_type,
                       Name = name,
                       Description = desc)]
        self.agent.region.enqueue_message(Message("CreateInventoryItem", *args))
        
    def sendFetchInventoryDescendentsRequest(self, folder_id = None):
        """ send a request to the grid for folder contents """

        raise NotImplemented("sendFetchInventoryDescendentsRequest")

    def sendFetchInventoryRequest(self, folder_id = None):
        """ send a request to the grid for inventory items in folder """

        raise NotImplemented("sendFetchInventoryRequest")

    def sendFetchLibRequest(self, item_id = None):
        """ send a request to the grid for library items """

        raise NotImplemented("sendFetchLibRequest")

    def sendFetchLibDescendentsRequest(self, item_id = None):
        """ send a request to the grid for library folder contents """

        raise NotImplemented("sendFetchDescendentsRequest")

class AIS(InventoryManager):
    """ AIS specific inventory manager """

    def __init__(self, agent, capabilities, settings = None):

        super(AIS, self).__init__(agent, settings)

        self.capabilities = capabilities

    def sendFetchInventoryRequest(self, item_ids = []):
        """ send a request to the grid for inventory item attributes """

        if len(item_ids) == 0:
            log(WARNING, "sendFetchInventoryRequest requires > 0 item_ids, 0 passed in")
            return
        elif type(item_ids) != list:
            log(WARNING, "sendFetchInventoryRequest requires a list of item_ids, %s passed in" % (type(item_ids)))
            return            

        cap = self.capabilities['FetchInventory']

        post_body = {'items': [{'item_id': str(item_id)} for item_id in item_ids]}

        custom_headers = {'Accept' : 'application/llsd+xml'}

        try:
            result = cap.POST(post_body, custom_headers)
        except ResourceError, error:
            log(ERROR, error)
            return
        except ResourceNotFound, error:
            log(ERROR, "404 calling: %s" % (error))
            return

        for item in response['folders']:

            self._store_caps_items(item, folder_id)

    def sendFetchLibRequest(self, folder_id, item_ids = []):
        """ send a request to the grid for library item attributes """

        if len(item_ids) == 0:
            log(WARNING, "sendFetchLibRequest requires > 0 item_ids, 0 passed in")
            return
        elif type(item_ids) != list:
            log(WARNING, "sendFetchLibRequest a list of item_ids, %s passed in" % (type(item_ids)))
            return            

        cap = self.capabilities['FetchLib']

        post_body = {'items': [{'item_id': str(item_id)} for item_id in item_ids]}

        custom_headers = {'Accept' : 'application/llsd+xml'}

        try:
            result = cap.POST(post_body, custom_headers)
        except ResourceError, error:
            log(ERROR, error)
            return
        except ResourceNotFound, error:
            log(ERROR, "404 calling: %s" % (error))
            return

        for item in response['folders']:

            self._store_caps_items(item, folder_id, 'library')

    def sendFetchInventoryDescendentsRequest(self, folder_id):
        """ send a request to the server for inventory folder contents """

        cap = self.capabilities['WebFetchInventoryDescendents']

        post_body = {'folders': [{'folder_id': str(folder_id), 'owner_id': str(self.agent.agent_id)}]}

        custom_headers = {'Accept' : 'application/llsd+xml'}

        try:
            response = cap.POST(post_body, custom_headers)
        except ResourceError, error:
            log(ERROR, error)
            return
        except ResourceNotFound, error:
            log(ERROR, "404 calling: %s" % (error))
            return

        '''
        Response shape
        
        {'folders':[ {'category': CATEGORY_SHAPE,
                'categories': [CATEGORY_SHAPE,],
                'items': [ITEM_SHAPE,] }]}
        '''
        
        for member in response['folders']:

            if member.has_key('category'):
                self._store_inventory_folder(member['category'])

            if member.has_key('categories'):
                [self._store_inventory_folder(folder_info) for folder_info in member['categories']]

            # pass a tuple of (item_info, category_id)
            if member.has_key('items'):
                self._store_caps_items(member['items'], member['category']['category_id'])

    def _store_caps_items(self, items, folder_id, destination = 'inventory'):
        """ transform an AIS caps response's inventory items and folder_id to InventoryItems and store it """

        for item in items:
            inventory_item = InventoryItem(item['item_id'], folder_id, item['permissions']['creator_id'], item['permissions']['owner_id'], item['permissions']['group_id'], item['permissions']['base_mask'], item['permissions']['owner_mask'], item['permissions']['group_mask'], item['permissions']['everyone_mask'], item['permissions']['next_owner_mask'], None, item['asset_id'], item['type'], item['inv_type'], item['flags'], item['sale_info']['sale_type'], item['sale_info']['sale_price'], item['name'], item['desc'], item['created_at'], None, item['permissions']['last_owner_id'])

            self._store_inventory_item(inventory_item, destination)

    def sendFetchLibDescendentsRequest(self, folder_id):
        """ send a request to the server for folder contents """

        cap = self.capabilities['FetchLibDescendents']

        post_body = {'folders': [{'folder_id': str(folder_id), 'owner_id': self.settings.ALEXANDRIA_LINDEN}]}

        custom_headers = {'Accept' : 'application/llsd+xml'}

        try:
            response = cap.POST(post_body, custom_headers)
        except ResourceError, error:
            log(ERROR, error)
            return
        except ResourceNotFound, error:
            log(ERROR, "404 calling: %s" % (error))
            return

        '''
        Response shape

        {'folders':[ {'category': CATEGORY_SHAPE,
                 'categories': [CATEGORY_SHAPE,],
                 'items': [ITEM_SHAPE,] }]}
        '''

        for member in response['folders']:

            if member.has_key('category'):
                self._store_inventory_folder(member['category'], 'library')

            if member.has_key('categories'):
                [self._store_inventory_folder(folder_info, 'library') for folder_info in member['categories']]

            if member.has_key('items'):
                self._store_caps_items(member['items'], member['category']['category_id'], 'library')


class UDP_Inventory(InventoryManager):
    
    def __init__(self, agent, settings = None):

        super(UDP_Inventory, self).__init__(agent, settings)

    def sendFetchInventoryRequest(self, folder_id = None):
        """ send a request to the grid for folder attributes """

        raise NotImplemented("sendFetchInventoryRequest")

    def sendFetchLibRequest(self, item_id = None):
        """ send a request to the grid for library items """

        raise NotImplemented("sendFetchInventoryRequest")

    def sendFetchInventoryDescendentsRequest(self, folder_id = None):
        """ send a request to the grid for folder contents """

        packet = Message('FetchInventoryDescendents',
                        Block('AgentData',
                                AgentID = self.agent.agent_id,          # MVT_LLUUID
                                SessionID = self.agent.session_id),     # MVT_LLUUID
                        Block('InventoryData',
                                FolderID = UUID(str(folder_id)),        # MVT_LLUUID
                                OwnerID = self.agent.agent_id,          # MVT_LLUUID
                                SortOrder = 0,                          # MVT_S32, 0 = name, 1 = time
                                FetchFolders = True,                    # MVT_BOOL
                                FetchItems = True))                     # MVT_BOOL

        self.agent.region.enqueue_message(packet)

    def sendFetchLibDescendentsRequest(self, folder_id = None):
        """ send a request to the grid for library items """

        raise NotImplemented("sendFetchLibDescendentsRequest")

    def onFetchInventoryReply(self, packet):

        _agent_id = packet.blocks['AgentData'][0].get_variable('AgentID')

        for InventoryData_block in packet.blocks['InventoryData']:

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

            self._store_inventory_item(inventory_item)

    def onInventoryDescendents(self, packet):
        
        if packet.blocks['AgentData'][0].get_variable('Descendents') > 0:

            _agent_id = packet.blocks['AgentData'][0].get_variable('AgentID')
            _folder_id = packet.blocks['AgentData'][0].get_variable('FolderID')
            _owner_id = packet.blocks['AgentData'][0].get_variable('OwnerID')
            _version = packet.blocks['AgentData'][0].get_variable('Version')
            _descendents = packet.blocks['AgentData'][0].get_variable('Descendents')
            # _descendents is not dealt with in any way here


            if str(packet.blocks['ItemData'][0].get_variable('ItemID').data) != str(UUID()):

                for ItemData_block in packet.blocks['ItemData']:

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

                    self._store_inventory_item(inventory_item)

            if str(packet.blocks['FolderData'][0].get_variable('FolderID').data) != str(UUID()):

                for FolderData_block in packet.blocks['FolderData']:

                    _FolderID = FolderData_block.get_variable('FolderID').data
                    _ParentID = FolderData_block.get_variable('ParentID').data
                    _Type = FolderData_block.get_variable('Type').data
                    _Name = FolderData_block.get_variable('Name').data

                    folder = InventoryFolder( _Name, _FolderID, _ParentID, None, _Type, _agent_id)

                    self._store_inventory_folder(folder)

class InventoryFolder(object):
    """ represents an Inventory folder 

    Initialize the event queue client class
    >>> inventoryfolder = InventoryFolder()

    Sample implementations: inventory.py
    Tests: tests/test_inventory.py
    """

    def __init__(self, Name = None, FolderID = None, ParentID = None, Version = None, Type = None, AgentID = UUID(), Descendents = 0):
        """ initialize the inventory folder """

        self.type = 'InventoryFolder'

        self.Name = Name
        self.FolderID = UUID(str(FolderID))
        self.ParentID = UUID(str(ParentID))
        self.Version = Version
        self.Type = Type
        self.Descendents = Descendents
        self.AgentID = UUID(str(AgentID))

        self.inventory = []

    def purge_descendents(self, agent):
        """ removes inventory from this folder, by unlinking the inventory from this parent folder """

        self.send_PurgeInventoryDescendents(agent.agent_id, agent.session_id, self.FolderID)

    def send_PurgeInventoryDescendents(self, agent, agent_id, session_id, folder_id):
        """ send a PurgeInventoryDescendents message to the host simulator """

        packet = Message('PurgeInventoryDescendents',
                        Block('AgentData',
                                AgentID = agent_id,
                                SessionID = session_id),
                        Block('InventoryData',
                                FolderID = folder_id))

        agent.region.enqueue_message(packet)

    def move(self, agent, parent_id, restamp = False):
        """ reparents this inventory folder """

        self.send_MoveInventoryFolder(agent, agent.agent_id, agent.session_id, restamp, self.FolderID, UUID(str(parent_id)))

    def send_MoveInventoryFolder(self, agent, agent_id, session_id, restamp, folder_id, parent_id):
        """ sends a MoveInventoryFolder message to the host simulator """

        # ToDo: the InventoryData block may the variable, if moved to a more
        # generic location (not nested under Inventory folder),
        # make it such that multiple blocks can be sent
        # use *[Block('InventoryData',FolderID = folder_id) for folder_id in folder_ids]

        packet = Message('MoveInventoryFolder',
                        Block('AgentData',
                            AgentID = agent_id,
                            SessionID = session_id,
                            Stamp = restamp),
                        Block('InventoryData',
                            FolderID = folder_id,
                            ParentID = parent_id))

        agent.region.enqueue_message(packet)

    def remove(self, agent):
        """ removes this inventory folder """

        self.send_RemoveInventoryFolder(agent, agent.agent_id, agent.session_id, False, self.FolderID)

    def send_RemoveInventoryFolder(self, agent, agent_id, session_id, restamp, folder_id):
        """ sends a RemoveInventoryFolder message to the host simulator """

        # ToDo: the InventoryData block may the variable, if moved to a more
        # generic location (not nested under Inventory folder),
        # make it such that multiple blocks can be sent
        # use *[Block('InventoryData',FolderID = folder_id) for folder_id in folder_ids]

        packet = Message('RemoveInventoryFolder',
                        Block('AgentData',
                                AgentID = agent_id,
                                SessionID = session_id,
                                Stamp = restamp),
                        Block('InventoryData',
                                FolderID = folder_id))

        agent.region.enqueue_message(packet)

class InventoryItem(object):
    """ represents an Inventory item 

    Initialize the InventoryItem class
    >>> inventoryitem = InventoryItem()

    Sample implementations: inventory.py
    Tests: tests/test_inventory.py
    """

    def __init__(self,
                 ItemID = None,
                 FolderID = None,
                 CreatorID = None,
                 OwnerID = None,
                 GroupID = None,
                 BaseMask = None,
                 OwnerMask = None,
                 GroupMask = None,
                 EveryoneMask = None,
                 NextOwnerMask = 0,
                 GroupOwned = None,
                 AssetID = None,
                 Type = None,
                 InvType = None,
                 Flags = None,
                 SaleType = None,
                 SalePrice = None,
                 Name = None,
                 Description = None,
                 CreationDate = None,
                 CRC = None,
                 LastOwnerID = UUID()):
        """ initialize the inventory item """

        self.type = 'InventoryItem'

        self.ItemID = UUID(str(ItemID))            # LLUUID
        self.FolderID = UUID(str(FolderID))        # LLUUID
        self.CreatorID = UUID(str(CreatorID))      # LLUUID
        self.OwnerID = UUID(str(OwnerID))          # LLUUID
        self.GroupID = UUID(str(GroupID))          # LLUUID
        self.BaseMask = BaseMask                        # U32
        self.OwnerMask = OwnerMask                      # U32
        self.GroupMask = GroupMask                      # U32
        self.EveryoneMask = EveryoneMask                # U32
        self.NextOwnerMask = NextOwnerMask
        self.GroupOwned = GroupOwned                    # Bool
        self.AssetID = UUID(str(AssetID))          # LLUUID
        self.Type = Type                                # S8
        self.InvType = InvType                          # S8
        self.Flags = Flags                              # U32
        self.SaleType = SaleType                        # U8
        self.SalePrice = SalePrice                      # S32
        self.Name = Name                                # Variable 1
        self.Description = Description                  # Variable 1
        self.CreationDate = CreationDate                # S32
        self.CRC = CRC                                  # U32
        self.LastOwnerID = UUID(str(LastOwnerID))

    def rez_object(self, agent, relative_position = (1, 0, 0)):

        # self.agent.Position holds where we are. we need to add this Vector3 to the incoming tuple (vector to a vector)
        location_to_rez_x = agent.Position.X + relative_position[0]
        location_to_rez_y = agent.Position.Y  + relative_position[1]
        location_to_rez_z = agent.Position.Z + relative_position[2]

        location_to_rez = (location_to_rez_x, location_to_rez_y, location_to_rez_z)

        sendRezObject(agent, self, location_to_rez, location_to_rez)

    def update(self, agent, name = None, value = None):
        """ allow arbitraty update to any data in the inventory item 
        
        accepts a dictionary of key:value pairs which will update the stored inventory items
        and then send an UpdateInventoryItem packet
        """

        if self.__dict__.has_key(name):
            self.setattr(self, name, value)
            sendUpdateInventoryItem(agent, [self])
        else:
            raise DataParsingError('Inventory item attribute update failes, no field named \'%s\'' % (name))

    def give(self, agent, to_agent_id):
        """ sends the target agent an inventory offer of this """

        # prep variables and send the message
        _AgentID = agent.agent_id
        _SessionID = agent.session_id
        _FromGroup = False
        _ToAgentID = to_agent_id
        _ParentEstateID = 0
        _RegionID = agent.region.RegionID
        _Position = agent.Position
        _Offline = 0
        _Dialog = ImprovedIMDialogue.InventoryOffered
        _ID = uuid.uuid4()
        _Timestamp = 0
        _FromAgentName = agent.Name()
        _Message = self.Name
        _BinaryBucket = struct.pack(">b", self.Type) + self.ItemID.get_bytes() # binary of asset type and id

        log(INFO, "Sending inventory offer of %s from %s to %s" % (self.Name, agent.agent_id, to_agent_id))

        agent.send_ImprovedInstantMessage(_AgentID, _SessionID, _FromGroup, _ToAgentID, _ParentEstateID, _RegionID, _Position, _Offline, _Dialog, _ID, _Timestamp, _FromAgentName, _Message, _BinaryBucket)

# ~~~~~~~~~~~~~~~
# Packet Wrappers
# ~~~~~~~~~~~~~~~

def sendUpdateInventoryItem(agent, inventory_items = [], ):
    """ sends an UpdateInventoryItem packet to a region 

    this function expects an InventoryItem instance already with updated data
    """

    packet = Message('UpdateInventoryItem',
                    Block('AgentData',
                            AgentID = agent.agent_id,
                            SessionID = agent.session_id,
                            TransactionID = UUID()),
                    *[Block('InventoryData',
                            ItemID = item.ItemID,
                            FolderID = item.FolderID,
                            CallbackID = UUID(),
                            CreatorID = item.CreatorID,
                            OwnerID = item.OwnerID,
                            GroupID = item.GroupID,
                            BaseMask = item.BaseMask,
                            OwnerMask = item.OwnerMask,
                            GroupMask = item.GroupMask,
                            EveryoneMask = item.EveryoneMask,
                            NextOwnerMask = item.NextOwnerMask,
                            GroupOwned = item.GroupOwned,
                            TransactionID = UUID(),
                            Type = item.Type,
                            InvType = item.InvType,
                            Flags = item.Flags,
                            SaleType = item.SaleType,
                            SalePrice = item.SalePrice,
                            Name = item.Name,
                            Description = item.Description,
                            CreationDate = item.CreationDate,
                            CRC = item.CRC) for item in inventory_items])

    agent.region.enqueue_message(packet)

def sendRezObject(agent, inventory_item, RayStart, RayEnd, FromTaskID = UUID(), BypassRaycast = 1,  RayTargetID = UUID(), RayEndIsIntersection = False, RezSelected = False, RemoveItem = False, ItemFlags = 0, GroupMask = 0, EveryoneMask = 0, NextOwnerMask = 0):
    """ sends a RezObject packet to a region """

    packet = Message('RezObject',
                    Block('AgentData',
                          AgentID = agent.agent_id,
                          SessionID = agent.session_id,
                          GroupID = agent.ActiveGroupID),
                    Block('RezData',
                          FromTaskID = UUID(str(FromTaskID)),
                          BypassRaycast = BypassRaycast,
                          RayStart = RayStart,
                          RayEnd = RayEnd,
                          RayTargetID = UUID(str(RayTargetID)),
                          RayEndIsIntersection = RayEndIsIntersection,
                          RezSelected = RezSelected,
                          RemoveItem = RemoveItem,
                          ItemFlags = ItemFlags,
                          GroupMask = GroupMask,
                          EveryoneMask = EveryoneMask,
                          NextOwnerMask = NextOwnerMask),
                    Block('InventoryData',
                          ItemID = inventory_item.ItemID,
                          FolderID = inventory_item.FolderID,
                          CreatorID = inventory_item.CreatorID,
                          OwnerID = inventory_item.OwnerID,
                          GroupID = inventory_item.GroupID,
                          BaseMask = inventory_item.BaseMask,
                          OwnerMask = inventory_item.OwnerMask,
                          GroupMask = inventory_item.GroupMask,
                          EveryoneMask = inventory_item.EveryoneMask,
                          GroupOwned = inventory_item.GroupOwned,
                          TransactionID = UUID(),
                          Type = inventory_item.Type,
                          InvType = inventory_item.InvType,
                          Flags = inventory_item.Flags,
                          SaleType = inventory_item.SaleType,
                          SalePrice = inventory_item.SalePrice,
                          Name = inventory_item.Name,
                          Description = inventory_item.Description,
                          CreationDate = inventory_item.CreationDate,
                          CRC = inventory_item.CRC,
                          NextOwnerMask = inventory_item.NextOwnerMask))

    agent.region.enqueue_message(packet)


    


