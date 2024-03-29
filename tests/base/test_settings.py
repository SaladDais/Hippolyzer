"""
Copyright 2009, Linden Research, Inc.
  See NOTICE.md for previous contributors
Copyright 2021, Salad Dais
All Rights Reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
import unittest

from hippolyzer.lib.base.settings import Settings


class TestSettings(unittest.TestCase):
    def test_base_settings(self):
        settings = Settings()
        self.assertEqual(settings.ENABLE_DEFERRED_PACKET_PARSING, True)
        settings.ENABLE_DEFERRED_PACKET_PARSING = False
        self.assertEqual(settings.ENABLE_DEFERRED_PACKET_PARSING, False)
