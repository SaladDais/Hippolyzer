#standard libraries
import struct
import string
import re
import pprint

#local libraries
import message_template
from pyogp.lib.base.data import msg_tmpl
from pyogp.lib.base.message.message_types import MsgFrequency, MsgTrust, \
     MsgEncoding, MsgDeprecation, MsgBlockType, MsgType

class MessageTemplateParser(object):
    def __init__(self, template_file):
        if template_file == None:
            raise Exception('Template file cannot be None')

        self.template_file = template_file
        self.message_templates = []
        self.version = ''
        self.count = 0        
        self.__parse_template_file()

    def __add_template(self, new_template):
        self.count += 1
        #self.message_templates[new_template.get_name()] = new_template
        self.message_templates.append(new_template)

    def __parse_template_file(self):
        count = 0
        
        self.template_file.seek(0)
        lines = self.template_file
        #results = re.match("^\t([^\t{}]+.+)",line) #gets packet headers
        #results  = re.match("^\t\t([^{}]+.+)",line) #gets packet blocks
        #results  = re.match("^\t\t([{}]+.+)",line)  #gets block data

        current_template = None
        current_block = None

        #we have to go through all the packets and parse them
        while(True):
            try:
                line = lines.next()
                #print line
                #raw_input()
            except StopIteration:
                break

            if self.version == '':
                version_test = re.match("version.(.+)",line) #gets packet headers
                if version_test != None:
                    parts = version_test.group(1)
                    parts = parts.split()
                    self.version = float(parts[0])
            
            #get packet header, starting a new packet
            packet_header = re.match("^\t([^\t{}]+.+)",line) #gets packet headers
            if packet_header != None:
                parts = packet_header.group(1)
                parts = parts.split()
                
                current_template = message_template.MessageTemplate(parts[0])
                frequency = None
                if parts[1] == 'Low':
                    frequency = MsgFrequency.LOW_FREQUENCY_MESSAGE
                elif parts[1] == 'Medium':
                    frequency = MsgFrequency.MEDIUM_FREQUENCY_MESSAGE
                elif parts[1] == 'High':
                    frequency = MsgFrequency.HIGH_FREQUENCY_MESSAGE
                elif parts[1] == 'Fixed':
                    frequency = MsgFrequency.FIXED_FREQUENCY_MESSAGE

                current_template.frequency = frequency
                
                msg_num = string.atoi(parts[2],0)
                if frequency == MsgFrequency.FIXED_FREQUENCY_MESSAGE:   
                    #have to do this because Fixed messages are stored as a long in the template
                    binTemp = struct.pack('>L', string.atol(parts[2],0))
                    msg_num_hex = binTemp
                    msg_num = struct.unpack('>h','\x00' + binTemp[3])[0]
                elif frequency == MsgFrequency.LOW_FREQUENCY_MESSAGE:
                    msg_num_hex = struct.pack('>BBh',0xff,0xff, msg_num)
                elif frequency == MsgFrequency.MEDIUM_FREQUENCY_MESSAGE:
                    msg_num_hex = struct.pack('>BB',0xff, msg_num)
                elif frequency == MsgFrequency.HIGH_FREQUENCY_MESSAGE:
                    msg_num_hex = struct.pack('>B', msg_num)

                current_template.msg_num = msg_num
                current_template.msg_num_hex = msg_num_hex
            
                msg_trust = None
                if parts[3] == 'Trusted':
                    msg_trust = MsgTrust.LL_TRUSTED
                elif parts[3] == 'NotTrusted':
                    msg_trust = MsgTrust.LL_NOTRUST

                current_template.msg_trust = msg_trust                 

                msg_encoding = None
                if parts[4] == 'Unencoded':
                    msg_encoding = MsgEncoding.LL_UNENCODED
                elif parts[4] == 'Zerocoded':
                    msg_encoding = MsgEncoding.LL_ZEROCODED

                current_template.msg_encoding = msg_encoding

                msg_dep = None
                if len(parts) > 5:
                    if parts[5] == 'Deprecated':
                        msg_dep = MsgDeprecation.LL_DEPRECATED
                    elif parts[5] == 'UDPDeprecated':
                        msg_dep = MsgDeprecation.LL_UDPDEPRECATED
                    elif parts[5] == 'NotDeprecated':
                        msg_dep = MsgDeprecation.LL_NOTDEPRECATED
                else:
                    msg_dep = MsgDeprecation.LL_NOTDEPRECATED

                current_template.msg_deprecation = msg_dep

                self.__add_template(current_template)

            block_header = re.match("^\t\t([^{}]+.+)",line) #gets packet block header
            if block_header != None:
                parts = block_header.group(1)
                parts = parts.split()

                current_block = message_template.MessageTemplateBlock(parts[0])

                block_type = None
                block_num = 0
                if parts[1] == 'Single':
                    block_type = MsgBlockType.MBT_SINGLE
                elif parts[1] == 'Multiple':
                    block_type = MsgBlockType.MBT_MULTIPLE
                    block_num = int(parts[2])
                elif parts[1] == 'Variable':
                    block_type = MsgBlockType.MBT_VARIABLE

                current_block.type = block_type
                current_block.block_number = block_num
                    
                current_template.add_block(current_block)
                
            block_data  = re.match("^\t\t([{}]+.+)",line)  #gets block data
            if block_data != None:
                parts = block_data.group(1)
                parts = parts.split()
                parts.remove('{')
                parts.remove('}')
    
                type_string = parts[1]
                var_type = None
                var_size = -1
                if type_string == 'U8':
                    var_type = MsgType.MVT_U8
                    var_size = 1
                elif type_string == 'U16':
                    var_type = MsgType.MVT_U16                    
                    var_size = 2
                elif type_string == 'U32':
                    var_type = MsgType.MVT_U32                    
                    var_size = 4
                elif type_string == 'U64':
                    var_type = MsgType.MVT_U64                    
                    var_size = 8
                elif type_string == 'S8':
                    var_type = MsgType.MVT_S8                    
                    var_size = 1
                elif type_string == 'S16':
                    var_type = MsgType.MVT_S16                    
                    var_size = 2
                elif type_string == 'S32':
                    var_type = MsgType.MVT_S32                   
                    var_size = 4
                elif type_string == 'S64':
                    var_type = MsgType.MVT_S64                    
                    var_size = 8
                elif type_string == 'F32':
                    var_type = MsgType.MVT_F32                    
                    var_size = 4
                elif type_string == 'F64':
                    var_type = MsgType.MVT_F64                    
                    var_size = 8
                elif type_string == 'LLVector3':
                    var_type = MsgType.MVT_LLVector3                    
                    var_size = 12
                elif type_string == 'LLVector3d':
                    var_type = MsgType.MVT_LLVector3d                    
                    var_size = 24
                elif type_string == 'LLVector4':
                    var_type = MsgType.MVT_LLVector4                    
                    var_size = 16
                elif type_string == 'LLQuaternion':
                    var_type = MsgType.MVT_LLQuaternion                    
                    var_size = 12
                elif type_string == 'LLUUID':
                    var_type = MsgType.MVT_LLUUID                    
                    var_size = 16
                elif type_string == 'BOOL':
                    var_type = MsgType.MVT_BOOL                    
                    var_size = 1
                elif type_string == 'IPADDR':
                    var_type = MsgType.MVT_IP_ADDR                    
                    var_size = 4
                elif type_string == 'IPPORT':
                    var_type = MsgType.MVT_IP_PORT                    
                    var_size = 2
                elif type_string == 'Fixed' or  type_string == 'Variable':
                    if type_string == 'Fixed':
                        var_type = MsgType.MVT_FIXED
                    elif type_string == 'Variable':
                        var_type = MsgType.MVT_VARIABLE

                    var_size = int(parts[2])
                    if var_size <= 0:
                        raise Exception('Bad variable size')
                    
                current_var = message_template.MessageTemplateVariable(parts[0], var_type, var_size)
                current_block.add_variable(current_var)

        self.template_file.seek(0)

def print_packet_list(packet_list):
    for packet in packet_list:
        print '======================================'
        print packet.get_name() + ' ' + packet.get_frequency() + ' ' + \
                str(packet.get_message_number()) + ' ' + str(packet.get_message_hex_num()) + \
                ' ' + packet.get_message_trust() + ' ' + \
                packet.get_message_encoding() + ' ' + packet.get_deprecation()
        
        for block in packet.get_blocks():
            print '\t' + block.get_name() + ' ' + block.get_block_type() + ' ' + \
                  str(block.get_block_number())
            for variable in block.get_variables():
                sz = len(variable.get_name())
                print '\t\t' + variable.get_name() + variable.get_type().rjust(30 - sz)

def get_all_types(packet_list):
    type_set = set([])
    for packet in packet_list:
        for block in packet.get_blocks():
            for variable in block.get_variables():
                type_set.add(variable.get_type())

    type_list = list(type_set)
    type_list.sort()
    return type_list

def main():
    parser = MessageTemplateParser()
    parser.parse_template_file(msg_tmpl)
    templates = parser.message_templates
    
    print_packet_list(templates)

    p_typelist = get_all_types(templates)
    pprint.pprint(p_typelist)
    return
    
if __name__ == "__main__":
    main()
