import copy
import datetime as dt
import unittest

from hippolyzer.lib.base.datatypes import *
from hippolyzer.lib.base.inventory import InventoryModel, SaleType, InventoryItem
from hippolyzer.lib.base.wearables import Wearable, VISUAL_PARAMS

SIMPLE_INV = """\tinv_object\t0
\t{
\t\tobj_id\tf4d91477-def1-487a-b4f3-6fa201c17376
\t\tparent_id\t00000000-0000-0000-0000-000000000000
\t\ttype\tcategory
\t\tname\tContents|
\t\tmetadata\t<llsd><undef /></llsd>
|
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
\t\tmetadata\t<llsd><map><key>experience</key><uuid>a2e76fcd-9360-4f6d-a924-000000000003</uuid></map></llsd>
|
\t\tcreation_date\t1587367239
\t}
"""

SIMPLE_INV_PARSED = [
    {
        'name': 'Contents',
        'obj_id': UUID('f4d91477-def1-487a-b4f3-6fa201c17376'),
        'parent_id': UUID('00000000-0000-0000-0000-000000000000'),
        'type': 'category'
    },
    {
        'asset_id': UUID('00000000-0000-0000-0000-000000000000'),
        'created_at': 1587367239,
        'desc': '2020-04-20 04:20:39 lsl2 script',
        'flags': b'\x00\x00\x00\x00',
        'inv_type': 'script',
        'item_id': UUID('dd163122-946b-44df-99f6-a6030e2b9597'),
        'name': 'New Script',
        'metadata': {"experience": UUID("a2e76fcd-9360-4f6d-a924-000000000003")},
        'parent_id': UUID('f4d91477-def1-487a-b4f3-6fa201c17376'),
        'permissions': {
            'base_mask': 2147483647,
            'creator_id': UUID('a2e76fcd-9360-4f6d-a924-000000000003'),
            'everyone_mask': 0,
            'group_id': UUID('00000000-0000-0000-0000-000000000000'),
            'group_mask': 0,
            'last_owner_id': UUID('a2e76fcd-9360-4f6d-a924-000000000003'),
            'next_owner_mask': 581632,
            'owner_id': UUID('a2e76fcd-9360-4f6d-a924-000000000003'),
            'owner_mask': 2147483647,
        },
        'sale_info': {
            'sale_price': 10,
            'sale_type': 'not'
        },
        'type': 'lsltext'
    }
]

INV_CATEGORY = """\tinv_category\t0
\t{
\t\tcat_id\tf4d91477-def1-487a-b4f3-6fa201c17376
\t\tparent_id\t00000000-0000-0000-0000-000000000000
\t\ttype\tlsltext
\t\tpref_type\tlsltext
\t\tname\tScripts|
\t\towner_id\ta2e76fcd-9360-4f6d-a924-000000000003
\t}
"""


class TestLegacyInv(unittest.TestCase):
    def setUp(self) -> None:
        self.model = InventoryModel.from_str(SIMPLE_INV)

    def test_parse(self):
        self.assertTrue(UUID('f4d91477-def1-487a-b4f3-6fa201c17376') in self.model.nodes)
        self.assertIsNotNone(self.model.root)

    def test_parse_category(self):
        model = InventoryModel.from_str(INV_CATEGORY)
        self.assertEqual(UUID('f4d91477-def1-487a-b4f3-6fa201c17376'), model.root.node_id)

    def test_serialize(self):
        new_model = InventoryModel.from_str(self.model.to_str())
        self.assertEqual(self.model, new_model)

    def test_serialize_category(self):
        model = InventoryModel.from_str(INV_CATEGORY)
        new_model = InventoryModel.from_str(model.to_str())
        self.assertEqual(model, new_model)

    def test_category_legacy_serialization(self):
        self.assertEqual(INV_CATEGORY, InventoryModel.from_str(INV_CATEGORY).to_str())

    def test_item_access(self):
        item = self.model.nodes[UUID('dd163122-946b-44df-99f6-a6030e2b9597')]
        self.assertEqual(item.name, "New Script")
        self.assertEqual(item.sale_info.sale_type, SaleType.NOT)
        self.assertDictEqual(item.metadata, {"experience": UUID("a2e76fcd-9360-4f6d-a924-000000000003")})
        self.assertEqual(item.model, self.model)

    def test_access_children(self):
        root = self.model.root
        item = tuple(self.model.ordered_nodes)[1]
        self.assertEqual((item,), root.children)

    def test_access_parent(self):
        root = self.model.root
        item = tuple(self.model.ordered_nodes)[1]
        self.assertEqual(root, item.parent)
        self.assertEqual(None, root.parent)

    def test_unlink(self):
        self.assertEqual(1, len(self.model.root.children))
        item = tuple(self.model.ordered_nodes)[1]
        self.assertEqual([item], item.unlink())
        self.assertEqual(0, len(self.model.root.children))
        self.assertEqual(None, item.model)

    def test_relink(self):
        item = tuple(self.model.ordered_nodes)[1]
        for unlinked in item.unlink():
            self.model.add(unlinked)
        self.assertEqual(self.model, item.model)
        self.assertEqual(1, len(self.model.root.children))

    def test_eq_excludes_model(self):
        item = tuple(self.model.ordered_nodes)[1]
        item_copy = copy.copy(item)
        item_copy.model = None
        self.assertEqual(item, item_copy)

    def test_llsd_serialization(self):
        self.assertEqual(self.model.to_llsd(), SIMPLE_INV_PARSED)

    def test_llsd_date_parsing(self):
        model = InventoryModel.from_llsd(SIMPLE_INV_PARSED)
        item: InventoryItem = model.nodes.get(UUID("dd163122-946b-44df-99f6-a6030e2b9597"))  # type: ignore
        self.assertEqual(item.creation_date, dt.datetime(2020, 4, 20, 7, 20, 39, tzinfo=dt.timezone.utc))

    def test_llsd_serialization_ais(self):
        model = InventoryModel.from_str(INV_CATEGORY)
        self.assertEqual(
            [
                {
                    'agent_id': UUID('a2e76fcd-9360-4f6d-a924-000000000003'),
                    'category_id': UUID('f4d91477-def1-487a-b4f3-6fa201c17376'),
                    'name': 'Scripts',
                    'parent_id': UUID('00000000-0000-0000-0000-000000000000'),
                    'type_default': 10,
                    'version': -1
                }
            ],
            model.to_llsd("ais")
        )

    def test_llsd_legacy_equality(self):
        new_model = InventoryModel.from_llsd(self.model.to_llsd())
        self.assertEqual(self.model, new_model)
        new_model.root.name = "foo"
        self.assertNotEqual(self.model, new_model)

    def test_legacy_serialization(self):
        self.assertEqual(SIMPLE_INV, self.model.to_str())

    def test_difference_added(self):
        new_model = InventoryModel.from_llsd(self.model.to_llsd())
        diff = self.model.get_differences(new_model)
        self.assertEqual([], diff.changed)
        self.assertEqual([], diff.removed)

        new_model.root.name = "foo"
        diff = self.model.get_differences(new_model)
        self.assertEqual([new_model.root], diff.changed)
        self.assertEqual([], diff.removed)

        item = new_model.root.children[0]
        item.unlink()
        diff = self.model.get_differences(new_model)
        self.assertEqual([new_model.root], diff.changed)
        self.assertEqual([item], diff.removed)

        new_item = copy.copy(item)
        new_item.node_id = UUID.random()
        new_model.add(new_item)
        diff = self.model.get_differences(new_model)
        self.assertEqual([new_model.root, new_item], diff.changed)
        self.assertEqual([item], diff.removed)


GIRL_NEXT_DOOR_SHAPE = """LLWearable version 22
Girl Next Door - C2 - med - Adam n Eve

\tpermissions 0
\t{
\t\tbase_mask\t0008e000
\t\towner_mask\t0008e000
\t\tgroup_mask\t00000000
\t\teveryone_mask\t00000000
\t\tnext_owner_mask\t0008e000
\t\tcreator_id\tdf110c10-72e6-40d6-8916-14b4b0366b18
\t\towner_id\t285a8af7-7a1d-4608-8fb5-200b816e7ee1
\t\tlast_owner_id\t285a8af7-7a1d-4608-8fb5-200b816e7ee1
\t\tgroup_id\t00000000-0000-0000-0000-000000000000
\t}
\tsale_info\t0
\t{
\t\tsale_type\tnot
\t\tsale_price\t10
\t}
type 0
parameters 82
1 -.21
2 -.4
4 -.08
5 .04
6 -.04
7 .02
8 -.42
10 -.15
11 .16
12 -.5
13 0
14 1
15 -.16
17 .17
18 -.42
19 -.78
20 -.16
21 .01
22 0
23 -.44
24 .32
25 .35
27 -.55
33 -.11
34 .22
35 -.1
36 -1.06
37 -.86
38 -.42
80 0
105 .59
155 -.24
157 0
185 -.68
193 .55
196 -.98
505 .39
506 -.68
507 -.77
515 -1
517 -.11
518 .6
629 .5
637 .24
646 -.26
647 -.05
649 .36
650 .25
652 .4
653 .29
656 0
659 .76
662 .5
663 0
664 0
665 .08
675 -.14
676 -.58
678 .5
682 .5
683 -.17
684 .28
685 0
690 .42
692 .26
693 -.12
753 .51
756 -.2
758 .21
759 .5
760 .85
764 .32
765 .18
769 .37
773 .53
795 .22
796 0
799 .5
841 -.12
842 0
879 0
880 -.37
textures 0
"""


class TestWearable(unittest.TestCase):
    def test_parse(self):
        wearable = Wearable.from_str(GIRL_NEXT_DOOR_SHAPE)
        self.assertEqual(wearable.name, "Girl Next Door - C2 - med - Adam n Eve")
        self.assertEqual(wearable.parameters[841], -.12)

    def test_serialize(self):
        wearable = Wearable.from_str(GIRL_NEXT_DOOR_SHAPE)
        new_wearable = Wearable.from_str(wearable.to_str())
        self.assertEqual(wearable, new_wearable)

    def test_visual_params(self):
        param = VISUAL_PARAMS.by_name("Eyelid_Inner_Corner_Up")
        self.assertEqual(param.value_max, 1.2)
