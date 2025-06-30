import unittest

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.client.inventory_manager import InventoryManager
from tests.client import MockClientRegion

CREATE_FOLDER_PAYLOAD = {
    '_base_uri': 'slcap://InventoryAPIv3',
    '_created_categories': [
        UUID(int=2),
    ],
    '_created_items': [],
    '_embedded': {
        'categories': {
            f'{UUID(int=2)}': {
                '_embedded': {'categories': {}, 'items': {}, 'links': {}},
                '_links': {
                    'parent': {'href': f'/category/{UUID(int=1)}'},
                    'self': {'href': f'/category/{UUID(int=2)}'}
                },
                'agent_id': f'{UUID(int=9)}',
                'category_id': f'{UUID(int=2)}',
                'name': 'New Folder',
                'parent_id': f'{UUID(int=1)}',
                'type_default': -1,
                'version': 1
            }
        },
        'items': {}, 'links': {}
    },
    '_links': {
        'categories': {'href': f'/category/{UUID(int=1)}/categories'},
        'category': {'href': f'/category/{UUID(int=1)}', 'name': 'self'},
        'children': {'href': f'/category/{UUID(int=1)}/children'},
        'items': {'href': f'/category/{UUID(int=1)}/items'},
        'links': {'href': f'/category/{UUID(int=1)}/links'},
        'parent': {'href': '/category/00000000-0000-0000-0000-000000000000'},
        'self': {'href': f'/category/{UUID(int=1)}/children'}
    },
    '_updated_category_versions': {str(UUID(int=1)): 27},
    'agent_id': UUID(int=9),
    'category_id': UUID(int=1),
    'name': 'My Inventory',
    'parent_id': UUID.ZERO,
    'type_default': 8,
    'version': 27,
}


class TestParcelOverlay(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.region = MockClientRegion()
        self.session = self.region.session()
        self.inv_manager = InventoryManager(self.session)
        self.model = self.inv_manager.model
        self.handler = self.region.message_handler

    def test_create_folder_response(self):
        self.inv_manager.process_aisv3_response(CREATE_FOLDER_PAYLOAD)
        self.assertIsNotNone(self.model.get_category(UUID(int=1)))
        self.assertIsNotNone(self.model.get_category(UUID(int=2)))
