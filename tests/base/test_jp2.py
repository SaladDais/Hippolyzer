import os.path
import unittest

import glymur
from glymur.codestream import CMEsegment

from hippolyzer.lib.base.jp2_utils import BufferedJp2k

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


@unittest.skipIf(glymur.jp2k.opj2.OPENJP2 is None, "OpenJPEG library missing")
class TestJP2Utils(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(os.path.join(BASE_PATH, "test_resources", "plywood.j2c"), "rb") as f:
            cls.j2c_bytes = f.read()

    def test_load_j2c(self):
        j = BufferedJp2k(contents=self.j2c_bytes)
        j.parse()
        # Last segment in the header is the comment section
        com: CMEsegment = j.codestream.segment[-1]
        self.assertEqual("CME", com.marker_id)
        # In this case the comment is the encoder version
        self.assertEqual(b'Kakadu-3.0.3', com.ccme)

    def test_read_j2c_data(self):
        j = BufferedJp2k(self.j2c_bytes)
        pixels = j[::]
        self.assertEqual((512, 512, 3), pixels.shape)

    def test_save_j2c_data(self):
        j = BufferedJp2k(self.j2c_bytes)
        pixels = j[::]
        j[::] = pixels
        new_j2c_bytes = bytes(j)
        self.assertNotEqual(self.j2c_bytes, new_j2c_bytes)
        # Glymur will have replaced the CME section with its own
        self.assertIn(b"Created by OpenJPEG", new_j2c_bytes)
