import unittest

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.vfs import STATIC_VFS


class StaticVFSTest(unittest.TestCase):
    def test_basic(self):
        # Load the block for the fly anim
        block = STATIC_VFS[UUID("aec4610c-757f-bc4e-c092-c6e9caf18daf")]
        anim_data = STATIC_VFS.read_block(block)
        self.assertEqual(len(anim_data), 1414)
