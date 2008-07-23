#!/usr/bin/python
"""
@file packet.py
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
       
#local libraries
from makepacketdict import makepacketdict, makereversepacketdict

mypacketdictionary = makepacketdict()
myreversedictionary = makereversepacketdict()

""" can construct and deconstruct packet headers. Has nothing to
        do with the packet payload, yet. """

#this probably needs to implement an interface so it can be serialized
class MsgData():
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

#this probably needs to implement an interface so it can be serialized
class MsgBlockData():
    """ Used as a Message block that is being created that will be
        serialized and sent. """
    def __init__(self, name):
        self.name = name
        self.size = 0
        self.variables = {}
        self.block_number = 0
             
    def get_variable(self, var_name):
        return self.variables[var_name]

    def add_variable(self, var):
        self.variables[var.name] = var

    def add_data(self, var_name, data, data_size):
        self.get_variable(var_name).add_data(data, data_size)

class MsgVariableData():
    """ Used as a Message Block variable that is being created that will be
        serialized and sent """
    def __init__(self, name, tp):
        self.name = name
        #data_size holds info whether or not the variable is of type
        #MVT_VARIABLE
        self.data_size = 0
        self.size = -1
        self.type = tp
        self.data = None

    #how DO we add data? What format will it be in?
    def add_data(self, data, data_size):
        self.data = data
        self.size = data_size

class MessageTemplateVariable():
    def __init__(self, name, tp, size):
        self.name = name
        self.type = tp
        self.size = size

class MessageTemplateBlock():
    def __init__(self, name):
        self.variable_map = {}
        self.name = name
        self.block_type = None
        self.number = 0

    def add_variable(self, var):
        self.variable_map[var.name] = var

    def get_variables(self):
        return self.variable_map.values()

    def get_variable(self, name):
        return self.variable_map[name]

class MessageTemplate():
    def __init__(self, name):
        self.block_map = {}
        #this is the function or object that will handle this type of message
        self.handler = None
        self.name = name
        self.frequency = None
        self.msg_num = 0
        self.msg_num_hex = None
        self.msg_trust = None
        self.msg_deprecation = None

    #this probably needs more arguments to pass to the func or object
    def set_handler(self, handler):
        self.handler = handler

    def add_block(self, block):
        self.block_map[block.name] = block

    def get_blocks(self):
        return self.block_map.values()
        
    def get_block(self, name):
        return self.block_map[name]
        
#these remain unformatted (by standard) because they are going to be moved    
def decodeHeaderPair(frequency, num):
    return mypacketdictionary[(frequency, num)]

def decodeFrequency(header):
    #if it is not a high
    if header[0] == '\xFF':
        #if it is not a medium frequency message
        if header[1] == '\xFF':
            #if it is a Fixed frequency message
            if header[2] == '\xFF':
                return 'Fixed'
            #then it is low
            else:
                return 'Low'
        #then it is medium
        else:
            return 'Medium'
    #then it is high
    else:
        return 'High'

    return None

def decodeNum(header):
    frequency = decodeFrequency(header)

    if frequency == 'Low':
        return struct.unpack('B', header[2:4])[0] #int("0x"+ByteToHex(header[2:4]).replace(' ', ''),16)
        
    elif frequency == 'Medium':
        return struct.unpack('B', header[1:2])[0] #int("0x"+ByteToHex(header[1:2]).replace(' ', ''),16)
        
    elif frequency == 'High':
        return struct.unpack('B', header[0])[0] #int("0x"+ByteToHex(header[0]), 16)  

    elif frequency == 'Fixed':
        return struct.unpack('B', header[0:4])[0] #int("0x"+ByteToHex(header[0:4]).replace(' ', ''), 16)

    else:
        return None

def decodeHeader(header):
    frequency = decodeFrequency(header)
    num = decodeNum(header)
    
    return decodeHeaderPair(frequency, num)

def encodePacketID(frequency, num):
    if frequency == 'Low':
        frequencyData = LOW_FREQUENCY_MESSAGE
        packedNum = struct.pack('>H', num)
        
    elif frequency == 'Medium':
        frequencyData = MEDIUM_FREQUENCY_MESSAGE
        packedNum = struct.pack('>B', num)

    elif frequency == 'High':
        frequencyData = HIGH_FREQUENCY_MESSAGE
        packedNum = struct.pack('>B', num)

    elif frequency == 'Fixed':
        frequencyData = FIXED_FREQUENCY_MESSAGE
        packedNum = struct.pack('>B', num)

    return frequencyData + packedNum

def encodeHeaderName(ack, sequenceNumber, packetName):
    header_tuple = myreversedictionary[packetName]
    frequency = header_tuple[0]
    num = header_tuple[1]
    return encodeHeader(ack, sequenceNumber, frequency, num)
    
def encodeHeader(ack, sequenceNumber, frequency, num):
    packetID = encodePacketID(frequency, num)
    return ack + struct.pack('>LB', sequenceNumber, 0) + packetID
