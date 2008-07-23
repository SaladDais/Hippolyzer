#standard libs
import struct

#pyogp libs
from pyogp.lib.base.message_template import MsgData, MsgBlockData, \
     MsgVariableData
#import pyogp.lib.base.message_types
from pyogp.lib.base.message_types import MsgType, MsgBlockType, MsgFrequency, sizeof
from pyogp.lib.base.data_packer import DataPacker

class MessageTemplateBuilder(object):
    """ This class builds messages at its high level, that is, keeping
        that data in data structure form. A serializer should be used on
        the message produced by this so that it can be sent over a network. """
    def __init__(self, template_dict):
        self.template_list = template_dict
        #when a message is being built, uses this template
        #to add blocks and variables
        self.current_template = None
        self.current_msg = None
        self.current_block = None

        self.cur_msg_name = ''
        self.cur_block_name = ''

        self.packer = DataPacker()
                    
    def get_current_message(self):
        return self.current_msg

    def get_current_block(self):
        return self.current_block

    def build_message(self):
        """ Builds the message by serializing the data. Creates a packet ready
            to be sent. """
        #this probably needs a serializer to do the work
        #serializer should serialize the MsgData and traverse its blocks,
        #and the blocks variables
        #serializer should adapt the interface of MsgData (whatever it is),
        #and implement ISerializer

        #doesn't build in the header flags, sequence number, or data offset
        msg_buffer = ''
        bytes = 0
        
        if self.current_template == None:
            #error
            return None

        #don't need to pack the frequency and message number. The template
        #stores it because it doesn't change per template.
        pack_freq_num = self.current_template.msg_num_hex
        msg_buffer += pack_freq_num
        bytes += len(pack_freq_num)

        #add some offset?

        for block in self.current_template.get_blocks():
            packed_block, block_size = self.build_block(block, self.current_msg)
            msg_buffer += packed_block
            bytes += block_size
        
        return msg_buffer, bytes

    def build_block(self, template_block, message_data):
        block_buffer = ''
        bytes = 0

        block_list = message_data.get_block(template_block.name)
        block_count = len(block_list)

        message_block = block_list[0]
        
        #multiple block type means there is a static number of these blocks
        #that make up this message, with the number stored in the template
        #don't need to add it to the buffer, because the message handlers that
        #receieve this know how many to read automatically
        if template_block.type == MsgBlockType.MBT_MULTIPLE:
            if template_block.block_number != message_block.block_number:
                raise Exception('Block ' + template_block.name + ' is type MBT_MULTIPLE \
                          but only has data stored for ' + str(block_count) + ' out of its ' + \
                          template_block.block_number + ' blocks')
                                  
        #variable means the block variables can repeat, so we have to
        #mark how many blocks there are of this type that repeat, stored in
        #the data
        if template_block.type == MsgBlockType.MBT_VARIABLE:
            block_buffer += struct.pack('>B', message_block.block_number)
            bytes += 1            

        for block in block_list:
            for variable in message_block.get_variables():
                var_size  = variable.size
                
                if var_size == -1:
                    raise Exception('Variable ' + variable.name + ' in block ' + \
                        message_block.name + ' of message ' + message_data.name + \
                        ' wasn"t set prior to buildMessage call')

                data_size = variable.data_size
                #variable's data_size represents whether or not it is of the type
                #MVT_VARIABLE. If it is positive, it is
                if data_size > 0:
                    if data_size == 1:
                        block_buffer += struct.pack('>B', var_size)
                    elif data_size == 2:
                        block_buffer += struct.pack('>H', var_size)
                    elif data_size == 4:
                        block_buffer += struct.pack('>I', var_size)
                    else:
                        raise Exception('Attempting to build variable with unknown size \
                                          of ' + str(var_size))

                    bytes += data_size

                #make sure there IS data to pack
                if variable.data != None and var_size > 0:
                    data = self.packer.pack_data(variable.data, variable.type)
                    block_buffer += data
                    bytes += len(data)

        return block_buffer, bytes
    
    def new_message(self, message_name):
        """ Creates a new packet where data can be added to it. Note, the variables
            are added when they are used, or data added to them, so to make sure
            no bad data is sent over the network. """
        #error check
        self.current_template = self.template_list[message_name]
        self.current_msg = MsgData(message_name)
        self.cur_msg_name = message_name

        for block in self.current_template.get_blocks():
            block_data = MsgBlockData(block.name)
            self.current_msg.add_block(block_data)

    def next_block(self, block_name):
        #if it doesn't exist, create a new block (may be a VARIABLE or MULTIPLE type
        #block
        if block_name not in self.current_template.block_map:
            #error: 
            print 'ERROR: template doesn"t have the block'
            return

        template_block = self.current_template.get_block(block_name)
        block_data = self.current_msg.get_block(block_name)[0]

        #if the block's number is 0, then we haven't set up this block yet
        if block_data.block_number == 0:
            block_data.block_number = 1
            self.current_block = block_data
            self.cur_block_name = block_name
            
            for variable in template_block.get_variables():
                var_data = MsgVariableData(variable.name, variable.type)
                self.current_block.add_variable(var_data)

            return

        #although we may have a block already, there are some cases where we can have
        #more than one block of the same name (when type is MULTIPLE or VARIABLE)
        else:
            #make sure it isn't SINGLE
            if self.template_block.type == MsgBlockType.MBT_SINGLE:
                #error: can't have more than 1 block when its supposed to be 1
                print 'ERROR: can"t have more than 1 block when its supposed to be 1'
                return

            elif self.template_block.type == MsgBlockType.MBT_MULTIPLE and \
                 self.template_block.block_number == block_data.block_number:
                #error: we are about to exceed block total
                print 'ERROR: we are about to exceed block total'
                return
            
            block_data.block_number += 1
            self.current_block = MsgBlockData(block.name)
            self.current_msg.add_block(self.current_block)
            self.cur_block_name = block_name

            for variable in self.current_block.variables:
                var_data = MsgVariableData(variable.name, variable.type)
                self.current_block.add_variable(var_data)

    def add_data(self, var_name, data, data_type):
        """ the data type is passed in to make sure that the programmer is aware of
            what type (and therefore size) of the data that is being passed in. """
        self.__check_size(var_name, data, data_type)
        self.current_block.add_data(var_name, data, data_type)

    def __check_size(self, var_name, data, data_type):
        block = self.template_list[self.cur_msg_name].get_block(self.cur_block_name)
        data_size = sizeof(data_type)
        size = block.get_variable(var_name).size
        if size != data_size:
            #warning
            #for now, exception
            raise Exception('Variable size isn"t the same as the template size')
