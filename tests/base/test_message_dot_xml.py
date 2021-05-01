
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

from hippolyzer.lib.base.message.message_dot_xml import MessageDotXML


class TestMessageDotXML(unittest.TestCase):

    def setUp(self):
        self.message_xml = MessageDotXML()

    def test_constructor(self):
        self.assertTrue(self.message_xml.serverDefaults)
        self.assertTrue(self.message_xml.messages)
        self.assertTrue(self.message_xml.capBans)
        self.assertTrue(self.message_xml.maxQueuedEvents)
        self.assertTrue(self.message_xml.messageBans)

    def test_validate_udp_msg_false(self):
        self.assertEqual(self.message_xml.validate_udp_msg('ParcelProperties'), False)

    def test_validate_udp_msg_true(self):
        self.assertEqual(self.message_xml.validate_udp_msg('CloseCircuit'), True)
