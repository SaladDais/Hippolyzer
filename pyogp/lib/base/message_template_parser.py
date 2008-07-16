import re
import message_template
import pprint
from pyogp.lib.base.data import msg_tmpl

def template_message_parser():
    dic = {}
    count = 0
    msg_tmpl.seek(0)
    lines = msg_tmpl
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
            dic[current_packet.name] = current_packet

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
            #current_var = packet.PacketBlockVariable(parts[0], parts[1])
            #current_block.addVar(current_var)
            current_block.addVar(parts[0], parts[1])

    return dic

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
        for block in packet_list[packet].blocks:
            for varname in block.vars:
                type_set.add(block.vars[varname])

    type_list = list(type_set)
    type_list.sort()
    return type_list

def main():
    p_list = template_message_parser()
    #print_packet_list(p_list)

    p_typelist = get_all_types(p_list)
    pprint.pprint(p_typelist)
    return
    
if __name__ == "__main__":
    main()
