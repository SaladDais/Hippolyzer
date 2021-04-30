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


class TestEvents(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_base_settings(self):
        settings = Settings()
        self.assertEqual(settings.quiet_logging, False)
        self.assertEqual(settings.HANDLE_PACKETS, True)
        self.assertEqual(settings.LOG_VERBOSE, True)
        self.assertEqual(settings.ENABLE_BYTES_TO_HEX_LOGGING, False)
        self.assertEqual(settings.ENABLE_CAPS_LOGGING, True)
        self.assertEqual(settings.ENABLE_CAPS_LLSD_LOGGING, False)
        self.assertEqual(settings.ENABLE_EQ_LOGGING, True)
        self.assertEqual(settings.ENABLE_UDP_LOGGING, True)
        self.assertEqual(settings.ENABLE_OBJECT_LOGGING, True)
        self.assertEqual(settings.LOG_SKIPPED_PACKETS, True)
        self.assertEqual(settings.ENABLE_HOST_LOGGING, True)
        self.assertEqual(settings.LOG_COROUTINE_SPAWNS, True)
        self.assertEqual(settings.DISABLE_SPAMMERS, True)
        self.assertEqual(settings.UDP_SPAMMERS, ['PacketAck', 'AgentUpdate'])

    def test_quiet_settings(self):
        settings = Settings(True)
        self.assertEqual(settings.quiet_logging, True)
        self.assertEqual(settings.HANDLE_PACKETS, True)
        self.assertEqual(settings.LOG_VERBOSE, False)
        self.assertEqual(settings.ENABLE_BYTES_TO_HEX_LOGGING, False)
        self.assertEqual(settings.ENABLE_CAPS_LOGGING, False)
        self.assertEqual(settings.ENABLE_CAPS_LLSD_LOGGING, False)
        self.assertEqual(settings.ENABLE_EQ_LOGGING, False)
        self.assertEqual(settings.ENABLE_UDP_LOGGING, False)
        self.assertEqual(settings.ENABLE_OBJECT_LOGGING, False)
        self.assertEqual(settings.LOG_SKIPPED_PACKETS, False)
        self.assertEqual(settings.ENABLE_HOST_LOGGING, False)
        self.assertEqual(settings.LOG_COROUTINE_SPAWNS, False)
