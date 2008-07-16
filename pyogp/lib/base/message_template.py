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

from makepacketdict import makepacketdict, makereversepacketdict
import struct
import pprint

mypacketdictionary = makepacketdict()
myreversedictionary = makereversepacketdict()

""" can construct and deconstruct packet headers. Has nothing to
        do with the packet payload, yet. """

LL_ZERO_CODE_FLAG = '\x80'
LL_RELIABLE_FLAG  = '\x40'
LL_RESENT_FLAG    = '\x20'
LL_ACK_FLAG       = '\x10'
LL_NONE           = '\x00'

FIXED_FREQUENCY_MESSAGE  = '\xFF\xFF\xFF'
LOW_FREQUENCY_MESSAGE    = '\xFF\xFF'
MEDIUM_FREQUENCY_MESSAGE = '\xFF'
HIGH_FREQUENCY_MESSAGE   = ''

"""class PacketBlockVariable():
    def __init__(self, name, tp):
        self.name = name
        self.lltype = tp"""

class MessageTemplateBlock():
    def __init__(self, header):
        self.header = header
        self.name = header[0]
        self.vars = {}
        #self.vars = []

    #def addVar(self, var):
        #self.vars.append(var)

    def addVar(self, name, typename):
        self.vars[name] = typename

    def getVar(self, index):
        return self.vars[index]

    """def getVarByName(self, name):
        for var in self.vars:
            if var.name == name:
                return var"""

    def getVarByName(self, name):
        return self.vars[name]

        return None

class MessageTemplate():
    def __init__(self, header):
        self.header = header
        self.name = header[0]
        self.blocks = []

    def addBlock(self, block):
        self.blocks.append(block)
        
    def getBlockByName(self, name):
        for block in self.blocks:
            if block.name == name:
                return block

        return None
    
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
