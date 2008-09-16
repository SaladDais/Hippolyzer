"""
@file udpserializer.py
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
import grokcore.component as grok
from zope.component import getUtility
from interfaces import ITemplateDictionary

#pyogp libs
from interfaces import IUDPPacket
from template import MsgData, MsgBlockData, MsgVariableData
from types import MsgType, MsgBlockType, MsgFrequency, EndianType, sizeof
from data_packer import DataPacker

from pyogp.lib.base.interfaces import ISerialization

class UDPPacketSerializer(grok.Adapter):
    """ an adpater for serializing a IUDPPacket into the UDP message format
    
	This class builds messages at its high level, that is, keeping
        that data in data structure form. A serializer should be used on
        the message produced by this so that it can be sent over a network. """

    grok.implements(ISerialization)
    grok.context(IUDPPacket)

    def __init__(self, context):
	"""initialize the adapter"""
        self.context = context	# the UDPPacket

        template_dict = getUtility(ITemplateDictionary)
        self.current_template = template_dict.get_template(context.name)
        self.packer = DataPacker()

    def serialize(self):
        """ Builds the message by serializing the data. Creates a packet ready
            to be sent. """

        #doesn't build in the header flags, sequence number, or data offset
        msg_buffer = ''
        bytes = 0

        #put the flags in the begining of the data. NOTE: for 1 byte, endian doesn't matter
        msg_buffer += self.packer.pack_data(self.context.send_flags, MsgType.MVT_U8)

        #set packet ID
        msg_buffer += self.packer.pack_data(self.context.packet_id, \
                                                  MsgType.MVT_S32, \
                                                  endian_type=EndianType.BIG)

        #pack in the offset to the data. NOTE: for 1 byte, endian doesn't matter
        msg_buffer += self.packer.pack_data(0, MsgType.MVT_U8)
        
        if self.current_template == None:
            return None

        #don't need to pack the frequency and message number. The template
        #stores it because it doesn't change per template.
        pack_freq_num = self.current_template.msg_num_hex
        msg_buffer += pack_freq_num
        bytes += len(pack_freq_num)

        message_data = self.context.message_data

        for block in self.current_template.get_blocks():
            packed_block, block_size = self.build_block(block, message_data)
            msg_buffer += packed_block
            bytes += block_size

        self.message_buffer = msg_buffer
        
        return msg_buffer

    def build_block(self, template_block, message_data):
        block_buffer = ''
        bytes = 0

        #the MsgData blocks is a list of lists
        #each block in the list is a block_list because you can have more than
        #one block for any given name
        block_list = message_data.get_block(template_block.name)
        block_count = len(block_list)

        #multiple block type means there is a static number of these blocks
        #that make up this message, with the number stored in the template
        #don't need to add it to the buffer, because the message handlers that
        #receieve this know how many to read automatically
        if template_block.type == MsgBlockType.MBT_MULTIPLE:
            if template_block.number != block_count:
                raise Exception('Block ' + template_block.name + ' is type MBT_MULTIPLE \
                          but only has data stored for ' + str(block_count) + ' out of its ' + \
                          template_block.number + ' blocks')
                                  
        #variable means the block variables can repeat, so we have to
        #mark how many blocks there are of this type that repeat, stored in
        #the data
        if template_block.type == MsgBlockType.MBT_VARIABLE:
            block_buffer += struct.pack('>B', block_count)
            bytes += 1            

        for block in block_list:
            
            for v in template_block.get_variables(): #message_block.get_variables():
                #this mapping has to occur to make sure the data is written in correct order
                variable = block.get_variable(v.name)
                var_size  = v.size
                var_data  = variable.data
                
                if variable == None:
                    raise Exception('Variable ' + variable.name + ' in block ' + \
                        message_block.name + ' of message ' + message_data.name + \
                        " wasn't set prior to buildMessage call")

                #if its a VARIABLE type, we have to write in the size of the data
                if v.type == MsgType.MVT_VARIABLE:
                    #data_size = template_block.get_variable(variable.name).size
                    if var_size == 1:
                        block_buffer += self.packer.pack_data(len(var_data), MsgType.MVT_U8)
                        #block_buffer += struct.pack('>B', var_size)
                    elif var_size == 2:
                        block_buffer += self.packer.pack_data(len(var_data), MsgType.MVT_U16)
                        #block_buffer += struct.pack('>H', var_size)
                    elif var_size == 4:
                        block_buffer += self.packer.pack_data(len(var_data), MsgType.MVT_U32)
                        #block_buffer += struct.pack('>I', var_size)
                    else:
                        raise Exception('Attempting to build variable with unknown size \
                                          of ' + str(var_size))

                    bytes += var_size
                
                data = self.packer.pack_data(var_data, v.type)
                block_buffer += data
                bytes += len(data)

        return block_buffer, bytes
    
    """this is currently done in the parser
    def build_message_ids(self):
        packer = DataPacker()
        for template in self.template_list.message_templates.values():
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
                                                         EndianType.BIG)"""
