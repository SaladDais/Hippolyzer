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

        # store the inventory contents in a list
        # Ditto the library

        self.contents = []
        self.count = len(self.contents)

        # the root inventory and library root folder are special cases
        self.root_folder = None
        self.library_root = None

        # set up callbacks
        if self.settings.HANDLE_PACKETS:
             self.packet_handler = self.agent.packet_handler

             onInventoryDescendents_received = self.packet_handler._register('InventoryDescendents')
             onInventoryDescendents_received.subscribe(onInventoryDescendents, self)     

        if self.settings.LOG_VERBOSE: log(INFO, "Initializing the inventory")

    def _parse_inventory_from_login_response(self):
        """ the login response may contain inventory information, append data to our contents list """

        if self.settings.LOG_VERBOSE: log(DEBUG, 'Parsing the login response for inventory folders')

        if self.agent.login_response.has_key('inventory-skeleton'):
            [self._add_inventory_folder(folder) for folder in self.agent.login_response['inventory-skeleton']]

        if self.agent.login_response.has_key('inventory-skel-lib'):
            [self._add_inventory_folder(folder) for folder in self.agent.login_response['inventory-skel-lib']]

    def _add_inventory_folder(self, folder_data):
        """ inventory folder data comes from either packets or login """

        if self.settings.LOG_VERBOSE: log(DEBUG, "Adding inventory folder %s" % (folder_data['name']))

        # if it's a dict, we are parsing login response data
        if type(folder_data) == dict:

            folder = InventoryFolder(folder_data['name'], folder_data['folder_id'], folder_data['parent_id'], folder_data['version'], folder_data['type_default'])

            self.contents.append(folder)

            if folder_data['parent_id'] == '00000000-0000-0000-0000-000000000000' and folder_data['name'] == 'My Inventory':
                self.root_folder = folder
            elif folder_data['parent_id'] == '00000000-0000-0000-0000-000000000000' and folder_data['name'] == 'Library':
                self.library_root = folder

    def get_folder_contents(self, folder_id = None, name = None):
        """ returns a list of the local representation of a folder's contents """

        if folder_id != None:

            return [member for member in self.contents if member.parent_id == folder_id]

        # the name case is not handled at this time
        '''
        elif name != None:

            folder_ids = [member.folder_id for member in self.contents if member.name == name]

            return [member for member in self.contents if member.name == name]
        '''

    def _request_folder_contents(self, folder_id = None, name = None):
        """ send a request to the server for folder contents, wraps sendFetchInventoryDescendentsPacket """

        self.sendFetchInventoryDescendentsPacket(folder_id = str(folder_id))

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

        self.agent.region.send_message(packet())

        return True

class InventoryFolder(object):
    """ represents an Inventory folder 

    Initialize the event queue client class
    >>> inventoryfolder = InventoryFolder()

    Sample implementations: inventory.py
    Tests: tests/test_inventory.py
    """

    def __init__(self, name = None, folder_id = None, parent_id = None, version = None, type_default = None):
        """ initialize the inventory folder """

        self.name = name
        self.folder_id = uuid.UUID(folder_id)
        self.parent_id = uuid.UUID(parent_id)
        self.version = version
        self.type_default = type_default

class InventoryItem(object):
    """ represents an Inventory item 

    Initialize the event queue client class
    >>> inventoryitem = InventoryItem()

    Sample implementations: inventory.py
    Tests: tests/test_inventory.py
    """

    def __init__(self):
        """ set up the event queue attributes """

        pass

#~~~~~~~~~~
# Callbacks
#~~~~~~~~~~

def onInventoryDescendents(packet, inventory):

    print packet