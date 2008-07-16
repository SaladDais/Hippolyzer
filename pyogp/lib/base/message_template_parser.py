import re
import message_template
import pprint
from pyogp.lib.base.data import msg_tmpl

class Message_Template_Parser():
    def __init__(self):
        self.message_templates = {}

    def getTemplateList(self):
        return self.message_templates.values()

    def getTemplate(self, name):
        return self.message_templates[name]

    def addTemplate(self, new_template):
        self.message_templates[new_template.getName()] = new_template

    def parse_template_file(self, template_file):
        count = 0
        template_file.seek(0)
        lines = template_file
        #results = re.match("^\t([^\t{}]+.+)",line) #gets packet headers
        #results  = re.match("^\t\t([^{}]+.+)",line) #gets packet blocks
        #results  = re.match("^\t\t([{}]+.+)",line)  #gets block data

        current_packet = None
        current_block = None

        print lines

        #we have to go through all the packets and parse them
        while(True):
            try:
                line = lines.next()
                #print line
                #raw_input()
            except StopIteration:
                break
            
            #get packet header, starting a new packet
            packet_header = re.match("^\t([^\t{}]+.+)",line) #gets packet headers
            if packet_header != None:
                parts = packet_header.group(1)
                parts = parts.split()
                
                current_packet = message_template.MessageTemplate(parts)
                self.addTemplate(current_packet)

            block_header = re.match("^\t\t([^{}]+.+)",line) #gets packet block header
            if block_header != None:
                parts = block_header.group(1)
                parts = parts.split()
                
                current_block = message_template.MessageTemplateBlock(parts)
                current_packet.addBlock(current_block)
                
            block_data  = re.match("^\t\t([{}]+.+)",line)  #gets block data
            if block_data != None:
                parts = block_data.group(1)
                parts = parts.split()
                parts.remove('{')
                parts.remove('}')
                current_var = message_template.MessageTemplateVariable(parts[0], parts[1])
                current_block.addVar(current_var)

def print_packet_list(packet_list):
    for packet in packet_list:
        print '======================================'
        print packet
        
        for block in packet_list[packet].blocks:
            print '\t' + block.name
            
            for varname in block.vars:
                print '\t\t' + varname + '\t' + block.vars[varname]

def get_all_types(packet_list):
    type_set = set([])
    for packet in packet_list:
        for block in packet.getBlocks():
            for variable in block.getVariables():
                type_set.add(variable.getType())

    type_list = list(type_set)
    type_list.sort()
    return type_list

def main():
    parser = Message_Template_Parser()
    parser.parse_template_file(msg_tmpl)
    templates = parser.getTemplateList()
    
    #print_packet_list(templates)

    p_typelist = get_all_types(templates)
    pprint.pprint(p_typelist)
    return
    
if __name__ == "__main__":
    main()
