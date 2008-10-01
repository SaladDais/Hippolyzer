"""
@file template_dict.py
@date 2008-09-16
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

from types import MsgFrequency
from interfaces import ITemplateDictionary
import grokcore.component as grok
from grokcore.component import GlobalUtility

from data import msg_tmpl, msg_details
from template_parser import MessageTemplateParser
from data_packer import DataPacker
from types import MsgType, EndianType

from pyogp.lib.base import exc

class TemplateDictionary(GlobalUtility):
    """the dictionary with all known templates"""
    
    grok.implements(ITemplateDictionary)
    
    def __init__(self, template_list=None):

        if template_list == None:
            parser = MessageTemplateParser(msg_tmpl)
            template_list = parser.message_templates
            template_dict = TemplateDictionary(template_list)

        # maps name to template
        self.message_templates = {}
        
        # maps (freq,num) to template
        self.message_dict = {}

        self.build_dictionaries(template_list)
        self.build_message_ids()

    def build_dictionaries(self, template_list):
        for template in template_list:
            self.message_templates[template.name] = template

            #do a mapping of type to a string for easier reference
            frequency_str = ''
            if template.frequency == MsgFrequency.FIXED_FREQUENCY_MESSAGE:
                frequency_str = "Fixed"
            elif template.frequency == MsgFrequency.LOW_FREQUENCY_MESSAGE:
                frequency_str = "Low"
            elif template.frequency == MsgFrequency.MEDIUM_FREQUENCY_MESSAGE:
                frequency_str = "Medium"
            elif template.frequency == MsgFrequency.HIGH_FREQUENCY_MESSAGE:
                frequency_str = "High"
                
            self.message_dict[(frequency_str, \
                               template.msg_num)] = template


    def build_message_ids(self):
        packer = DataPacker()
        for template in self.message_templates.values():
            frequency = template.frequency
            if frequency == MsgFrequency.FIXED_FREQUENCY_MESSAGE:   
                #have to do this because Fixed messages are stored as a long in the template
                template.msg_num_hex = '\xff\xff\xff' + \
                                       packer.pack_data(template.msg_num, \
                                                        MsgType.MVT_U8)
            elif frequency == MsgFrequency.LOW_FREQUENCY_MESSAGE:
                template.msg_num_hex = '\xff\xff' + \
                                packer.pack_data(template.msg_num, \
                                                 MsgType.MVT_U16, \
                                                 EndianType.BIG)
            elif frequency == MsgFrequency.MEDIUM_FREQUENCY_MESSAGE:
                template.msg_num_hex = '\xff' + \
                                packer.pack_data(template.msg_num, \
                                                 MsgType.MVT_U8, \
                                                 EndianType.BIG)
            elif frequency == MsgFrequency.HIGH_FREQUENCY_MESSAGE:
                template.msg_num_hex = packer.pack_data(template.msg_num, \
                                                         MsgType.MVT_U8, \
                                                         EndianType.BIG)

    def get_template(self, template_name):
        if template_name in self.message_templates:
            return self.message_templates[template_name]

        return None
    
    def get_template_by_pair(self, frequency, num):
        if (frequency, num) in self.message_dict:
            return self.message_dict[(frequency, num)]

        return None

    def __getitem__(self, i):
        return self.get_template(i)
    

