import unittest

from hippolyzer.lib.base.datatypes import *
from hippolyzer.lib.base.legacy_inv import InventoryModel

SIMPLE_INV = """\tinv_object\t0
\t{
\t\tobj_id\tf4d91477-def1-487a-b4f3-6fa201c17376
\t\tparent_id\t00000000-0000-0000-0000-000000000000
\t\ttype\tcategory
\t\tname\tContents|
\t}
\tinv_item\t0
\t{
\t\titem_id\tdd163122-946b-44df-99f6-a6030e2b9597
\t\tparent_id\tf4d91477-def1-487a-b4f3-6fa201c17376
\tpermissions 0
\t{
\t\tbase_mask\t7fffffff
\t\towner_mask\t7fffffff
\t\tgroup_mask\t00000000
\t\teveryone_mask\t00000000
\t\tnext_owner_mask\t0008e000
\t\tcreator_id\ta2e76fcd-9360-4f6d-a924-000000000003
\t\towner_id\ta2e76fcd-9360-4f6d-a924-000000000003
\t\tlast_owner_id\ta2e76fcd-9360-4f6d-a924-000000000003
\t\tgroup_id\t00000000-0000-0000-0000-000000000000
\t}
\t\tasset_id\t00000000-0000-0000-0000-000000000000
\t\ttype\tlsltext
\t\tinv_type\tscript
\t\tflags\t00000000
\tsale_info\t0
\t{
\t\tsale_type\tnot
\t\tsale_price\t10
\t}
\t\tname\tNew Script|
\t\tdesc\t2020-04-20 04:20:39 lsl2 script|
\t\tcreation_date\t1587367239
\t}
"""


class TestLegacyInv(unittest.TestCase):
    def test_parse(self):
        model = InventoryModel.from_str(SIMPLE_INV)
        self.assertTrue(UUID('f4d91477-def1-487a-b4f3-6fa201c17376') in model.containers)
        self.assertIsNotNone(model.root)

    def test_serialize(self):
        model = InventoryModel.from_str(SIMPLE_INV)
        new_model = InventoryModel.from_str(model.to_str())
        self.assertEqual(model, new_model)

    def test_item_access(self):
        model = InventoryModel.from_str(SIMPLE_INV)
        item = model.items[UUID('dd163122-946b-44df-99f6-a6030e2b9597')]
        self.assertEqual(item.name, "New Script")
        self.assertEqual(item.sale_info.sale_type, "not")
        self.assertEqual(item.model, model)
