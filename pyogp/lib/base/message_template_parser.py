#standard libraries
import re
import pprint

#local libraries
import message_template
from pyogp.lib.base.data import msg_tmpl

class MessageTemplateParser():
    def __init__(self, template_file):
        if template_file == None:
            raise Exception('Template file cannot be None')

        self.template_file = template_file
        self.message_templates = []
        self.version = ''
        self.count = 0        
        self.__parse_template_file()

    def get_version(self):
        return self.version
        
    def get_template_list(self):
        return self.message_templates

    def get_count(self):
        return self.count

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

        current_packet = None
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
                
                current_packet = message_template.MessageTemplate(parts)
                self.__add_template(current_packet)

            block_header = re.match("^\t\t([^{}]+.+)",line) #gets packet block header
            if block_header != None:
                parts = block_header.group(1)
                parts = parts.split()
                
                current_block = message_template.MessageTemplateBlock(parts)
                current_packet.add_block(current_block)
                
            block_data  = re.match("^\t\t([{}]+.+)",line)  #gets block data
            if block_data != None:
                parts = block_data.group(1)
                parts = parts.split()
                parts.remove('{')
                parts.remove('}')
                current_var = message_template.MessageTemplateVariable(parts[0], parts[1])
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
    templates = parser.get_template_list()
    
    print_packet_list(templates)

    p_typelist = get_all_types(templates)
    pprint.pprint(p_typelist)
    return
    
if __name__ == "__main__":
    main()
