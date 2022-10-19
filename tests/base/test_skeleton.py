import unittest

import numpy as np

from hippolyzer.lib.base.mesh_skeleton import load_avatar_skeleton


class TestSkeleton(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skeleton = load_avatar_skeleton()

    def test_get_joint(self):
        node = self.skeleton["mNeck"]
        self.assertEqual("mNeck", node.name)
        self.assertEqual(self.skeleton, node.skeleton())

    def test_get_joint_index(self):
        self.assertEqual(7, self.skeleton["mNeck"].index)
        self.assertEqual(113, self.skeleton["mKneeLeft"].index)

    def test_get_joint_parent(self):
        self.assertEqual("mChest", self.skeleton["mNeck"].parent().name)

    def test_get_joint_matrix(self):
        expected_mat = np.array([
            [1., 0., 0., -0.01],
            [0., 1., 0., 0.],
            [0., 0., 1., 0.251],
            [0., 0., 0., 1.]
        ])
        np.testing.assert_equal(expected_mat, self.skeleton["mNeck"].matrix)
