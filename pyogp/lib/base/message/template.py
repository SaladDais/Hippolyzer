#!/usr/bin/python
"""
@file template.py
@author Linden Lab
@date 2008-06-13
@brief Iniitializes path directories

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
$/LicenseInfo$
"""

#standard libraries
import struct
import re
import pprint

from zope.interface import implements
import grokcore.component as grok

from interfaces import IMessageData

class MsgData(object):
    """ Used as a Message that is being created that will be
        serialized and sent. """

    implements(IMessageData)

    def __init__(self, name):
        self.name = name
        self.size = 0
        self.blocks = {}

    def add_block(self, block):
        if block.name not in self.blocks:
            self.blocks[block.name] = []
            
        self.blocks[block.name].append(block)

    def get_block(self, block_name):
        return self.blocks[block_name]

    def add_data(self, block_name, var_name, data, data_size):
        get_block(block_name).add_data(var_name, data, data_size)

class MsgBlockData(object):
    """ Used as a Message block that is being created that will be
        serialized and sent. """

    def __init__(self, name):
        self.name = name
        self.size = 0
        self.vars = {}
        self.block_number = 0
             
    def get_variable(self, var_name):
        return self.vars[var_name]

    def get_variables(self):
        return self.vars.values()

    def add_variable(self, var):
        self.vars[var.name] = var

class MsgVariableData(object):
    """ Used as a Message Block variable that is being created that will be
        serialized and sent """
    def __init__(self, name, data):
        self.name = name
        #data_size holds info whether or not the variable is of type
        #MVT_VARIABLE
        self.size = -1
        self.data = data

class MessageTemplateVariable(object):
    """TODO: Add docstring"""

    def __init__(self, name, tp, size):
        self.name = name
        self.type = tp
        self.size = size

class MessageTemplateBlock(object):
    """TODO: Add docstring"""


    def __init__(self, name):
        self.variables = []
        self.variable_map = {}
        self.name = name
        self.block_type = None
        self.number = 0

    def add_variable(self, var):
        self.variable_map[var.name] = var
        self.variables.append(var)

    def get_variables(self):
        return self.variables #self.variable_map.values()

    def get_variable(self, name):
        return self.variable_map[name]

class MessageTemplate(object):

    def __init__(self, name):
        self.blocks = []
        self.block_map = {}

        #this is the function or object that will handle this type of message
        self.received_count = 0
        
        self.name = name
        self.frequency = None
        self.msg_num = 0
        self.msg_num_hex = None
        self.msg_trust = None
        self.msg_deprecation = None
        self.msg_encoding = None

    def add_block(self, block):
        self.block_map[block.name] = block
        self.blocks.append(block)

    def get_blocks(self):
        return self.blocks #self.block_map.values()
        
    def get_block(self, name):
        return self.block_map[name]
