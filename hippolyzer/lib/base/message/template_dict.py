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
import struct
import typing

from .msgtypes import MsgFrequency
from .data import msg_tmpl
from .template import MessageTemplate
from .template_parser import MessageTemplateParser


DEFAULT_PARSER = MessageTemplateParser(msg_tmpl)


class TemplateDictionary:
    """the dictionary with all known templates"""

    def __init__(self, template_list=None, message_template=None):
        if template_list is None:
            if message_template is None:
                parser = DEFAULT_PARSER
            else:
                parser = MessageTemplateParser(message_template)
            template_list = parser.message_templates

        self.template_list: typing.List[MessageTemplate] = []
        # maps name to template
        self.message_templates = {}

        # maps (freq,num) to template
        self.message_dict = {}

        self.load_templates(template_list)

    def load_templates(self, template_list):
        self.template_list.clear()
        self.template_list.extend(template_list)
        self.message_templates.clear()
        self.message_dict.clear()

        self.build_dictionaries(template_list)
        self.build_message_ids()

    def get_template_list(self):
        return [t.name for t in self.template_list]

    def build_dictionaries(self, template_list):
        for template in template_list:
            self.message_templates[template.name] = template

            # do a mapping of type to a string for easier reference
            frequency_str = ''
            if template.frequency == MsgFrequency.FIXED_FREQUENCY_MESSAGE:
                frequency_str = "Fixed"
            elif template.frequency == MsgFrequency.LOW_FREQUENCY_MESSAGE:
                frequency_str = "Low"
            elif template.frequency == MsgFrequency.MEDIUM_FREQUENCY_MESSAGE:
                frequency_str = "Medium"
            elif template.frequency == MsgFrequency.HIGH_FREQUENCY_MESSAGE:
                frequency_str = "High"

            self.message_dict[(frequency_str,
                               template.msg_num)] = template

    def build_message_ids(self):
        for template in list(self.message_templates.values()):
            frequency = template.frequency
            num_bytes = None
            if frequency == MsgFrequency.FIXED_FREQUENCY_MESSAGE:
                # have to do this because Fixed messages are stored as a long in the template
                num_bytes = b'\xff\xff\xff' + struct.pack("B", template.msg_num)
            elif frequency == MsgFrequency.LOW_FREQUENCY_MESSAGE:
                num_bytes = b'\xff\xff' + struct.pack("!H", template.msg_num)
            elif frequency == MsgFrequency.MEDIUM_FREQUENCY_MESSAGE:
                num_bytes = b'\xff' + struct.pack("B", template.msg_num)
            elif frequency == MsgFrequency.HIGH_FREQUENCY_MESSAGE:
                num_bytes = struct.pack("B", template.msg_num)
            template.msg_freq_num_bytes = num_bytes

    def get_template_by_name(self, template_name) -> typing.Optional[MessageTemplate]:
        return self.message_templates.get(template_name)

    def get_template_by_pair(self, frequency, num) -> typing.Optional[MessageTemplate]:
        return self.message_dict.get((frequency, num))

    def __getitem__(self, name):
        return self.get_template_by_name(name)

    def __contains__(self, item):
        return item in self.message_templates

    def __iter__(self):
        return iter(self.template_list)


DEFAULT_TEMPLATE_DICT = TemplateDictionary()
