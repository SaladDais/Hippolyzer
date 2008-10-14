"""
@file udpdeserializer.py
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

#standard libs
import struct
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

import grokcore.component as grok
from zope.component import getUtility

#pyogp libs
from interfaces import ITemplateDictionary
from pyogp.lib.base.interfaces import IDeserialization
from template import MsgData, MsgBlockData, MsgVariableData
from types import MsgType, MsgBlockType, MsgFrequency, PacketLayout, EndianType, PackFlags, sizeof
from data_unpacker import DataUnpacker
from interfaces import IUDPPacket

from pyogp.lib.base import exc

logger = getLogger('...base.message.udpdeserializer')
log = logger.log

class UDPPacketDeserializer(grok.Adapter):
    grok.implements(IDeserialization)
    grok.context(str)
        
    def __init__(self, context):
        self.context = context
        self.unpacker = DataUnpacker()
        self.current_template = None
        packet = None
        self.current_block = None

    def deserialize(self):
        if self.__validate_message(self.context) == True:
            return self.__decode_data(self.context)

        return None

    def __validate_message(self, message_buffer):
        """ Determines if the message follows a given template. """
        if self.__decode_template(message_buffer) == True:
            return True

        return False

    def __decode_template(self, message_buffer):
        """ Determines the template that the message in the buffer
            appears to be using. """
        if PacketLayout.PACKET_ID_LENGTH >= len(message_buffer):
            raise exc.MessageDeserializationError("packet length", "template mismatch")
        
        header = message_buffer[PacketLayout.PACKET_ID_LENGTH:]
        self.current_template = self.__decode_header(header)
        if self.current_template != None:
            return True

        log(INFO, "Received unknown packet: '%s', packet is not in our message_template" % (header))

        return False

    def __decode_header(self, header):
        frequency = self.__decode_frequency(header)
        num = self.__decode_num(header)

        #NEED TO GET THE GLOBAL TEMPLATE DICT
        template_dict = getUtility(ITemplateDictionary)
        return template_dict.get_template_by_pair(frequency, num)

    def __decode_frequency(self, header):
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

    def __decode_num(self, header):
        frequency = self.__decode_frequency(header)

        if frequency == 'Low':
            return struct.unpack('>H', header[2:4])[0] #int("0x"+ByteToHex(header[2:4]).replace(' ', ''),16)
            
        elif frequency == 'Medium':
            return struct.unpack('>B', header[1:2])[0] #int("0x"+ByteToHex(header[1:2]).replace(' ', ''),16)
            
        elif frequency == 'High':
            return struct.unpack('>B', header[0])[0] #int("0x"+ByteToHex(header[0]), 16)  

        elif frequency == 'Fixed':
            return struct.unpack('>B', header[3:4])[0] #int("0x"+ByteToHex(header[0:4]).replace(' ', ''), 16)

        else:
            return None

    def __decode_data(self, data):
        if self.current_template == None:
            raise exc.MessageTemplateNotFound("deserializing data")

        msg_data = MsgData(self.current_template.name)

        packet = IUDPPacket(msg_data)
        msg_size = len(data)

        packet.name = self.current_template.name
        
        #determine packet flags
        packet.send_flags = ord(data[0])
        packet.packet_id = \
            self.unpacker.unpack_data(data, MsgType.MVT_U32, 1, endian_type=EndianType.BIG)

        #Zero code flag
        if packet.send_flags & PackFlags.LL_ZERO_CODE_FLAG:
            data = self.zero_code_expand(data, msg_size)

        #ACK_FLAG - means the incoming packet is acking some old packets of ours
        if packet.send_flags & PackFlags.LL_ACK_FLAG:
            msg_size -= 1
            acks = self.unpacker.unpack_data(data, MsgType.MVT_U8, msg_size)
            ack_start = acks * sizeof(MsgType.MVT_S32)
            ack_data = data[msg_size-ack_start:]
            ack_pos = 0
            while acks > 0:
                ack_packet_id = self.unpacker.unpack_data(ack_data, MsgType.MVT_S32, \
                                                          start_index=ack_pos)
                ack_pos += sizeof(MsgType.MVT_S32)
                packet.add_ack(ack_packet_id)
                acks -= 1
        
        #RELIABLE - means the message wants to be acked by us
        if packet.send_flags & PackFlags.LL_RELIABLE_FLAG:
            packet.reliable = True
        
        #RESENT   - packet that wasn't previously acked was resent
        if packet.send_flags & PackFlags.LL_RESENT_FLAG:
            #check if its a duplicate and the sender messed up somewhere
              #case - ack we sent wasn't received by the sender
            pass

        #at the offset position, the messages stores the offset to where the
        #payload begins (may be extra header information)
        #print "Decoding offset"
        offset = self.unpacker.unpack_data(data, MsgType.MVT_U8, PacketLayout.PHL_OFFSET)

        freq_bytes = self.current_template.frequency
        #HACK: fixed case
        if freq_bytes == -1:
            freq_bytes = 4

        decode_pos = PacketLayout.PACKET_ID_LENGTH + \
                     freq_bytes + \
                     offset
        
        for block in self.current_template.blocks:
            repeat_count = 0

            if block.type == MsgBlockType.MBT_SINGLE:
                repeat_count = 1
            elif block.type == MsgBlockType.MBT_MULTIPLE:
                repeat_count = block.number
                
            elif block.type == MsgBlockType.MBT_VARIABLE:
                #if the block type is VARIABLE, then the current position
                #will be the repeat count written in
                #print "Reading VARIABLE block repeat count" 
                repeat_count = self.unpacker.unpack_data(data, \
                                                         MsgType.MVT_U8, \
                                                         decode_pos)
                
                decode_pos += 1
            else:
                print "ERROR: Unknown block type: " + str(block.type)
                return None

            for i in range(repeat_count):
                block_data = MsgBlockData(block.name)
                block_data.block_number = i
                self.current_block = block_data
                
                msg_data.add_block(self.current_block)
                
                for variable in block.variables:
                    
                    var_size = variable.size
                    if variable.type == MsgType.MVT_VARIABLE:
                        #this isn't the size of the data, but the max bytes
                        #the data can be
                        #need to copy because we have to advance our decode_pos
                        #afterwards
                        data_size = var_size
                        #HACK: this is a slow procedure, should passed in
                        if (decode_pos + data_size) > len(data):
                            print "ERROR: trying to read " +  str(decode_pos + var_size) + \
                                  " from a buffer of len " + str(len(data))
                            return None
                        if data_size == 1:
                            #print "Reading VARIABLE variable size 1 byte"
                            var_size = self.unpacker.unpack_data(data, \
                                                                 MsgType.MVT_U8, \
                                                                 decode_pos)
                        elif data_size == 2:
                            #print "Reading VARIABLE variable size 2 bytes" 
                            var_size = self.unpacker.unpack_data(data, \
                                                                 MsgType.MVT_U16, \
                                                                 decode_pos)
                        elif data_size == 4:
                            #print "Reading VARIABLE variable size 4 bytes"
                            var_size = self.unpacker.unpack_data(data, \
                                                                 MsgType.MVT_U32, \
                                                                 decode_pos)

                        else:
                            raise exc.MessageDeserializationError("variable", "unknown data size")
                        
                        decode_pos += data_size
                        
                    #HACK: this is a slow procedure, should passed in
                    if (decode_pos + var_size) > len(data):
                        print "ERROR 2: trying to read " +  str(decode_pos + var_size) + \
                              " from a buffer of len " + str(len(data))
                        return None
                    unpacked_data = self.unpacker.unpack_data(data, \
                                                              variable.type, \
                                                              decode_pos, \
                                                              var_size=var_size)

                    var_data = MsgVariableData(variable.name, unpacked_data)
                    self.current_block.add_variable(var_data)
                    decode_pos += var_size


        if len(msg_data.blocks) <= 0 and len(self.current_template.blocks) > 0:
            raise exc.MessageDeserializationError("message", "message is empty")
        
        packet.message_data = msg_data
        return packet

    def zero_code_expand(self, msg_buf, msg_size):
        if ord(msg_buf[0]) & PackFlags.LL_ZERO_CODE_FLAG == 0:
            return msg_buf

        header = msg_buf[0:PacketLayout.PACKET_ID_LENGTH]
        inputbuf = msg_buf[PacketLayout.PACKET_ID_LENGTH:]
        newstring = ""
        in_zero = False
        for c in inputbuf:
            if c != '\0':
                if in_zero == True:
                    zero_count = ord(c)
                    zero_count = zero_count -1
                    while zero_count>0:
                        newstring = newstring + '\x00'
                        zero_count = zero_count -1
                    in_zero = False
                else:
                    newstring = newstring + c
            else:
                newstring = newstring + c
                in_zero = True
        return header + newstring
