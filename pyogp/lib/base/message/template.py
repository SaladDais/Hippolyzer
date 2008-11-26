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
import binascii

from types import MsgType, MsgBlockType

class MsgData(object):
    """ Used as a Message that is being created that will be
        serialized and sent. """

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
        self.var_list = []       #LDE 25oct2008 added a var_list to keep track of the order the vars are listed in the template file
        self.block_number = 0
             
    def get_variable(self, var_name):
        return self.vars[var_name]

    def get_variables(self):
        return self.vars.values()

    def add_variable(self, var):
        self.vars[var.name] = var
        self.var_list.append(var.name)   #LDE 25oct2008 wanted to keep in entry order for nice display later on

class MsgVariableData(object):
    """ Used as a Message Block variable that is being created that will be
        serialized and sent """
    def __init__(self, name, data, var_type=None):   #LDE 23oct2008 added var_type for display issues
        self.name = name
        #data_size holds info whether or not the variable is of type
        #MVT_VARIABLE
        self.size = -1
        self.data = data
        self.var_type = var_type    #LDE 25oct2008 adding var_type to allow for easier formatting of data in display
    def get_var_type_as_string(self):
        return MsgType.MVT_as_string(self.var_type) #LDE 23oct2008 adding var_type_as_string to allow for easier display
    
    def get_data_as_string(self):
        if self.var_type == MsgType.MVT_VARIABLE:
            return binascii.hexlify(self.data) #LDE 23oct2008. Returns hex-string version of var-length data for display
        else: return str(self.data)
    
class MessageTemplateVariable(object):
    """TODO: Add docstring"""

    def __init__(self, name, tp, size):
        self.name = name
        self.type = tp
        self.size = size
        
    def get_name(self):
        return self.name
    
    def get_type(self):
        return self.type
    def get_type_as_string(self):             
        return MsgType.MVT_as_string(self.type)      #LDE 23oct2008 Display convenience

class MessageTemplateBlock(object):
    """TODO: Add docstring"""


    def __init__(self, name):
        self.variables = []
        self.variable_map = {}
        self.name = name
        self.block_type = 0
        self.number = 0

    def add_variable(self, var):
        self.variable_map[var.name] = var
        self.variables.append(var)

    def get_variables(self):
        return self.variables #self.variable_map.values()

    def get_variable(self, name):
        return self.variable_map[name]
    
    def get_name(self):
        return self.name
    
    def get_block_type(self):
        return self.block_type
    
    def get_block_type_as_string(self):
        return MsgBlockType.MBT_as_string(self.block_type)  #LDE 23oct2008 Display convenience
    
    def get_block_number(self):
        return self.number

class MessageTemplate(object):
    frequency_strings = {-1:'fixed', 1:'high', 2:'medium', 4:'low'}      #strings for printout
    depecration_strings = ["Deprecated","UDPDeprecated","NotDeprecated"] #using _as_string methods
    encoding_strings = ["Unencoded","Zerocoded"]  #etc
    trusted_strings = ["Trusted","NotTrusted"]    #etc LDE 24oct2008
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
    
    def get_name(self):
        return self.name
    
    def get_frequency(self):
        return self.frequency
    
    def get_frequency_as_string(self):
        return MessageTemplate.frequency_strings[self.frequency]   #LDE 23oct2008 Display convenience
    
    def get_message_number(self):
        return self.msg_num
    
    def get_message_hex_num(self):
        return ''.join( [ "%02X" % ord( x ) for x in self.msg_num_hex ] ).strip()

    
    def get_message_trust(self):
        return self.msg_trust
    
    def get_message_trust_as_string(self):                 #LDE 23oct2008 Display convenience
        return MessageTemplate.trusted_strings[self.msg_trust]
    
    def get_message_encoding(self):
        return self.msg_encoding
    
    def get_message_encoding_as_string(self):   #added _as_string method for easier display
        return MessageTemplate.encoding_strings[self.msg_encoding]
    
    def get_deprecation(self):
        return self.msg_deprecation
        
    def get_deprecation_as_string(self):       #added _as_string method for easier display
        return MessageTemplate.depecration_strings[self.msg_deprecation]
        
