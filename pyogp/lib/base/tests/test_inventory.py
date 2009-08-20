
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
import unittest

#related
import uuid

# pyogp
from pyogp.lib.base.inventory import InventoryManager, InventoryFolder, \
     InventoryItem
from pyogp.lib.base.datatypes import UUID
from pyogp.lib.base.agent import Agent
from pyogp.lib.base.region import Region
from pyogp.lib.base.utilities.enums import AssetType, InventoryType, \
     WearablesIndex, Permissions
from pyogp.lib.base.message.message import Message, Block

# pyogp tests
import pyogp.lib.base.tests.config 

class TestInventory(unittest.TestCase):

    def setUp(self):

        self.inventory = InventoryManager()

        self.folder_data = [{'parent_id': '00000000-0000-0000-0000-000000000000', 'version': 154, 'name': 'My Inventory', 'type_default': 8, 'folder_id': '0201a00f-afde-477d-967b-e731d186b9d6'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 9, 'name': 'Trash', 'type_default': 14, 'folder_id': '1640c442-85a9-c917-361a-f86bf72dab1a'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 1, 'name': 'Animations', 'type_default': 20, 'folder_id': '2e406320-ab10-6e2e-8f6f-de2572ffd426'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 6, 'name': 'Daft Tux', 'type_default': -1, 'folder_id': '3d62430b-9a61-7921-f376-46fb81b61594'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 2, 'name': 'Bot attachments1', 'type_default': -1, 'folder_id': '54e00f7f-1110-26d4-de54-6bd0809a429b'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 4, 'name': 'Daft Tux', 'type_default': -1, 'folder_id': '57e90615-2b0f-f029-3c09-3bbfa89f09f1'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 394, 'name': 'Totoro', 'type_default': -1, 'folder_id': '6115057c-8db5-be07-2701-397b819e84a5'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 3, 'name': 'Calling Cards', 'type_default': 2, 'folder_id': '629d9d71-ffc3-dbe4-3b96-0dc75c7be1bc'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 5, 'name': 'PinkieBot', 'type_default': -1, 'folder_id': '8a0cef67-18d8-fb6d-06ef-f1520595cf34'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 96, 'name': 'Objects', 'type_default': 6, 'folder_id': '8ed27f52-b020-509b-585d-ad2f3bfbce05'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 4, 'name': 'Notecards', 'type_default': 7, 'folder_id': '909ee313-b342-88b5-dca4-45d9df75b4b8'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 7, 'name': 'PinkieBot', 'type_default': -1, 'folder_id': '948c687f-ae1e-bf86-3faa-6cd1b2f132ff'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 1, 'name': 'Textures', 'type_default': 0, 'folder_id': '9aacf954-8a44-f4ca-5913-34d035eeae41'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 1, 'name': 'Sounds', 'type_default': 1, 'folder_id': 'bf2a5d50-2766-5031-1ffb-20acd137b58f'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 1, 'name': 'Lost And Found', 'type_default': 16, 'folder_id': 'd6d82d34-47ff-afec-f71f-b1ea20df9ccb'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 675, 'name': 'Totoro Box for Bots', 'type_default': -1, 'folder_id': 'e2bc553b-d0c4-c588-f664-04d8474f8376'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 1, 'name': 'Landmarks', 'type_default': 3, 'folder_id': 'e7c67062-6b47-feb6-85d7-86013cdb068c'},
                            {'parent_id': '0201a00f-afde-477d-967b-e731d186b9d6', 'version': 1, 'name': 'Scripts', 'type_default': 10, 'folder_id': 'f7e94373-f376-fd46-59a5-57d2562bf514'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 4, 'name': 'PinkieBot', 'type_default': -1, 'folder_id': '155551ef-c49a-98b8-d554-ab9f7a1b1ae8'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 2, 'name': 'Bot attachments1', 'type_default': -1, 'folder_id': '15edc217-14dc-b454-7c82-535e2fa423b2'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 63, 'name': 'Trash', 'type_default': 14, 'folder_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 1, 'name': 'Photo Album', 'type_default': 15, 'folder_id': '580fb866-1c5f-4f58-8927-0d9e295799f4'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 2, 'name': 'Calling Cards', 'type_default': 2, 'folder_id': '6f4c244f-8f14-42f9-a900-4b73f9a2a48e'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 7, 'name': 'Scripts', 'type_default': 10, 'folder_id': '7adc4a9a-0370-4833-a25c-872be4ae6e22'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 1, 'name': 'Landmarks', 'type_default': 3, 'folder_id': '7b3f2f88-666e-4b68-80b1-4dab3359ba3b'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 5, 'name': 'Textures', 'type_default': 0, 'folder_id': '82af0bfc-42e5-4134-980d-a7587e563499'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 8, 'name': 'Notecards', 'type_default': 7, 'folder_id': '8fe0babc-c915-4481-9299-2ec868541496'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 9, 'name': 'Body Parts', 'type_default': 13, 'folder_id': 'aba5a5d2-9e13-401c-943d-95f79904c487'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 3, 'name': 'Gestures', 'type_default': 21, 'folder_id': 'bd1d2af5-df49-4b98-9fc6-301b49042a89'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 49, 'name': 'Objects', 'type_default': 6, 'folder_id': 'c55798a9-463a-4065-9604-4572924387a8'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 7, 'name': 'Clothing', 'type_default': 5, 'folder_id': 'c833cc69-ee0d-4d50-b014-be8101cbb7c1'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 21, 'name': 'Object', 'type_default': -1, 'folder_id': 'cc22dc06-71fa-0059-f2af-64723c987068'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 37, 'name': 'Lost And Found', 'type_default': 16, 'folder_id': 'd01c9207-347f-48cc-a307-06f7a967e974'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 1, 'name': 'Animations', 'type_default': 20, 'folder_id': 'dcb179f7-a58a-4b97-8bfa-bc395988945a'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 45, 'name': 'Totoro', 'type_default': -1, 'folder_id': 'effd593a-10b8-8fb1-52a3-86b930b5b6cb'},
                            {'parent_id': '52aaafe8-7c5e-8fe0-b47e-097198648c9b', 'version': 1, 'name': 'Sounds', 'type_default': 1, 'folder_id': 'fca217d3-62b9-498f-b084-a137582850da'},
                            {'parent_id': 'bd1d2af5-df49-4b98-9fc6-301b49042a89', 'version': 19, 'name': 'Female Gestures', 'type_default': -1, 'folder_id': '01a2f40b-a034-5911-d6a3-7804547c105a'},
                            {'parent_id': 'bd1d2af5-df49-4b98-9fc6-301b49042a89', 'version': 28, 'name': 'Common Gestures', 'type_default': -1, 'folder_id': '38bc2d0e-f626-6fd6-3ea7-cb8f9b753af3'}]

        for folder in self.folder_data:
            self.inventory._store_inventory_folder(folder)

        uuid_ = UUID('12345678-1234-1234-1234-123456789abc')
        inventory_item = InventoryItem(uuid_,
                                       '0201a00f-afde-477d-967b-e731d186b9d6',
                                       uuid_,
                                       uuid_,
                                       UUID(),
                                       0,
                                       0,
                                       0,
                                       0,
                                       0,
                                       False,
                                       uuid_,
                                       10,
                                       10,
                                       0,
                                       0,
                                       0,
                                       "a_item",
                                       "a_item_desc",
                                       0,
                                       0)
        self.inventory._store_inventory_item(inventory_item)
 
    def tearDown(self):
        self.inventory = None
        self.folder_data = None
        
    def test_display_folder_contents_by_id(self):

        self.assertEquals(len(self.inventory.display_folder_contents(folder_id = uuid.UUID('52aaafe8-7c5e-8fe0-b47e-097198648c9b'))), 18)

    def test_display_folder_contents_by_nonexistant_id(self):

        self.assertEquals(len(self.inventory.display_folder_contents(folder_id = uuid.UUID('00000001-0000-0000-0000-000000000000'))), 0)

    def test_search_inventory_for_folders(self):

        matches = self.inventory.search_inventory(self.inventory.folders,
                                                  item_id='0201a00f-afde-477d-967b-e731d186b9d6')
        self.assertEqual(len(matches), 1)
        folder = matches.pop()
        self.assertEqual(folder.Name, 'My Inventory')

        matches = self.inventory.search_inventory(self.inventory.folders,
                                                  name='Trash')
        self.assertTrue(len(matches), 1)
        folder = matches.pop()
        self.assertEqual(str(folder.FolderID), '52aaafe8-7c5e-8fe0-b47e-097198648c9b') 

    def test_search_inventory_for_items(self):

        matches = self.inventory.search_inventory(self.inventory.folders,
                                                  item_id='12345678-1234-1234-1234-123456789abc')
        self.assertTrue(len(matches), 1)
        item = matches.pop()
        self.assertEqual(item.Name, 'a_item')

        matches = self.inventory.search_inventory(self.inventory.folders,
                                                  name='a_item')
        self.assertTrue(len(matches), 1)
        item = matches.pop()
        self.assertEqual(str(item.ItemID), '12345678-1234-1234-1234-123456789abc') 
    
    def test_create_new_item(self):

        self.inventory.agent = Agent()
        agent_id = UUID()
        agent_id.random()
        self.inventory.agent.agent_id = agent_id
        
        self.inventory.agent.region = DummyRegion()

        matches = self.inventory.search_inventory(self.inventory.folders,
                                                  name='My Inventory')
        self.assertEqual(len(matches), 1)
        folder = matches.pop()
        self.inventory.create_new_item(folder, "Name", "Desc",  AssetType.LSLText,
                                       InventoryType.LSL, WearablesIndex.WT_SHAPE,
                                       0)
        packet = self.inventory.agent.region.dummy_packet_holder.pop()
        self.assertEqual(packet.name, "CreateInventoryItem")

        self.assertEqual(packet.get_block('InventoryBlock')[0].get_variable('FolderID').data, folder.FolderID)
        self.assertEqual(packet.get_block('InventoryBlock')[0].get_variable('Name').data, 'Name')
        self.assertEqual(packet.get_block('InventoryBlock')[0].get_variable('Description').data, 'Desc')

        fake_uuid = UUID()
        fake_uuid.random()
        packet = Message('UpdateCreateInventoryItem',
                         Block('AgentData',
                               AgentID = UUID(),
                               SimApproved = True,
                               TransactionID = UUID()),
                         Block('InventoryData',
                               ItemID=fake_uuid,
                               FolderID=folder.FolderID,
                               CallbackID=0,
                               CreatorID=agent_id,
                               OwnerID=agent_id,
                               GroupID=UUID(),
                               BaseMask=Permissions.All,
                               OwnerMask=Permissions.All,
                               GroupMask=Permissions.None_,
                               EveryoneMask=Permissions.None_,
                               NextOwnerMask=Permissions.None_,
                               GroupOwned=False,
                               AssetID=UUID(),
                               Type=AssetType.LSLText,
                               InvType=InventoryType.LSL,
                               Flags=0,
                               SaleType=0,
                               SalePrice=0,
                               Name="Name",
                               Description="Desc",
                               CreationDate=0,
                               CRC=0))
        self.inventory.agent.region.message_handler.handle(packet)
        matches = self.inventory.search_inventory(self.inventory.folders,
                                              name="Name")
        self.assertEqual(len(matches), 1)
        item = matches.pop()
        self.assertEqual(item.Name, "Name")  
    '''  
     def test_display_folder_contents_by_name(self):

         for folder in self.folder_data:

             self.inventory._store_inventory_folder(folder)

         self.assertEquals(len(self.inventory._display_folder_contents(name = 'Trash')), 18)
     '''


class DummyRegion(Region):
    dummy_packet_holder = []
    def enqueue_message(self, packet, reliable = False):
        self.dummy_packet_holder.append(packet)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInventory))
    return suite


