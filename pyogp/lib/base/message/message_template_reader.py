#standard libs
import struct

#pyogp libs
import pyogp.lib.base.message.message_template 
from pyogp.lib.base.message.message_template import MsgData, MsgBlockData, \
     MsgVariableData
#import pyogp.lib.base.message_types
from pyogp.lib.base.message.message_types import MsgType, MsgBlockType, MsgFrequency, sizeof
from pyogp.lib.base.message.data_packer import DataPacker

class MessageTemplateReader(object):
    
    def __init__(self, template_dict):
        self.template_dict = template_dict
        self.current_template = None
        self.current_msg = None
        self.current_block = None

        self.cur_msg_name = ''
        self.cur_block_name = ''

    def validate_message(self, message_buffer, buffer_size):
        """ Determines if the message follows a given template. """
        header = message_buffer[message_template.PACKET_ID_LENGTH:]
        self.current_template = self.decode_header(header)
        if self.current_template == None:
            return False

        return True

    def read_message(self, message_buffer):
        """ Goes through the message and decodes all the data in it. """
        pass

    def decode_template(self, message_buffer, buffer_size):
        """ Determines the template that the message in the buffer
            appears to be using. """
        pass

    def decode_header(self, header):
        frequency = decode_frequency(header)
        num = decode_num(header)
        
        return self.template_dict.get_template_by_pair(frequency, num)

    def decode_frequency(self, header):
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

    def decode_num(self, header):
        frequency = decode_frequency(header)

        if frequency == 'Low':
            return struct.unpack('>B', header[2:4])[0] #int("0x"+ByteToHex(header[2:4]).replace(' ', ''),16)
            
        elif frequency == 'Medium':
            return struct.unpack('>B', header[1:2])[0] #int("0x"+ByteToHex(header[1:2]).replace(' ', ''),16)
            
        elif frequency == 'High':
            return struct.unpack('>B', header[0])[0] #int("0x"+ByteToHex(header[0]), 16)  

        elif frequency == 'Fixed':
            return struct.unpack('>B', header[0:4])[0] #int("0x"+ByteToHex(header[0:4]).replace(' ', ''), 16)

        else:
            return None
