#standard libs
import struct

#pyogp libs
from pyogp.lib.base.message.message_template import MsgData, MsgBlockData, \
     MsgVariableData
#import pyogp.lib.base.message_types
from pyogp.lib.base.message.message_types import MsgType, MsgBlockType, \
     MsgFrequency, PacketLayout, sizeof
from pyogp.lib.base.message.data_unpacker import DataUnpacker

class MessageTemplateReader(object):
    
    def __init__(self, template_dict):
        self.template_dict = template_dict
        self.unpacker = DataUnpacker()
        self.current_template = None
        self.receive_size = -1
        self.current_msg = None
        self.current_block = None

    def validate_message(self, message_buffer, buffer_size):
        """ Determines if the message follows a given template. """
        self.receive_size = buffer_size
        if self.__decode_template(message_buffer, buffer_size) == True:
            self.current_template.received_count += 1
            return True

        return False

    def read_message(self, message_buffer):
        """ Goes through the message and decodes all the data in it. """
        return self.__decode_data(message_buffer)            

    def get_data(self, block_name, var_name, data_type, block_number = 0):
        if self.receive_size == -1:
            raise Exception("Message hasn't been validated and read")
    
        if self.current_msg == None:
            raise Exception("Message hasn't been read yet")

        block_list = self.current_msg.get_block(block_name)
        if len(block_list) <= block_number:
            raise Exception("Block not in message")
            
        block_data = block_list[block_number]
        var_data = block_data.get_variable(var_name)

        if var_data.type != data_type:
            #error: variable types don't match
            return None
        
        return var_data.data

    def clear_message(self):
        self.current_template = None
        self.receive_size = -1
        self.current_msg = None
        self.current_block = None        
        
    def __decode_template(self, message_buffer, buffer_size):
        """ Determines the template that the message in the buffer
            appears to be using. """
        if PacketLayout.PACKET_ID_LENGTH >= buffer_size:
            raise Exception("Reading " + str(PacketLayout.PACKET_ID_LENGTH) + \
                            " bytes from a buffer that is only " + \
                            str(buffer_size) + " bytes long")
        
        header = message_buffer[PacketLayout.PACKET_ID_LENGTH:]
        self.current_template = self.__decode_header(header)
        if self.current_template != None:
            return True

        return False

    def __decode_data(self, data):
        if self.current_template == None:
            raise Exception('Attempting to decode data without validating it')
        if self.current_msg != None:
            #print 'WARNING: Attempting to decode data without clearing the last message'
            self.current_msg = None

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
        
        self.current_msg = MsgData(self.current_template.name)
        
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
                return False

            for i in range(repeat_count):
                block_data = MsgBlockData(block.name)
                block_data.block_number = i
                self.current_block = block_data
                
                self.current_msg.add_block(self.current_block)
                
                for variable in block.variables:
                    var_data = MsgVariableData(variable.name, variable.type)
                    self.current_block.add_variable(var_data)
                    
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
                            return False
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
                            raise Exception('Attempting to read variable with unknown size \
                                              of ' + str(data_size))
                        
                        decode_pos += data_size
                    #HACK: this is a slow procedure, should passed in
                    if (decode_pos + var_size) > len(data):
                        print "ERROR 2: trying to read " +  str(decode_pos + var_size) + \
                              " from a buffer of len " + str(len(data))
                        return False
                    unpacked_data = self.unpacker.unpack_data(data, \
                                                              variable.type, \
                                                              decode_pos, \
                                                              var_size=var_size)
                    self.current_block.add_data(variable.name, unpacked_data, var_size)
                    decode_pos += var_size

        if len(self.current_msg.block_map) <= 0 and len(self.current_template.blocks) > 0:
            raise Exception("Read message is empty")
        return True
 
    def __decode_header(self, header):
        frequency = self.__decode_frequency(header)
        num = self.__decode_num(header)
        
        return self.template_dict.get_template_by_pair(frequency, num)

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
        

        
