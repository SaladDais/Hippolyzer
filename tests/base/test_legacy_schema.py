import unittest

from hippolyzer.lib.base.datatypes import *
from hippolyzer.lib.base.legacy_inv import InventoryModel
from hippolyzer.lib.base.wearables import Wearable, VISUAL_PARAMS

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
