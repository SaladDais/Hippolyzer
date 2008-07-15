import re
import packet
import pprint

def parse_packets():
    dic = {}
    count = 0
    lines = open("../../linden/scripts/messages/message_template.msg", ).xreadlines()
    #results = re.match("^\t([^\t{}]+.+)",line) #gets packet headers
    #results  = re.match("^\t\t([^{}]+.+)",line) #gets packet blocks
    #results  = re.match("^\t\t([{}]+.+)",line)  #gets block data

    current_packet = None
    current_block = None
    current_var = None

    #we have to go through all the packets and parse them
    while(True):
        try:
            line = lines.next()
        except StopIteration:
            break
        
        #get packet header, starting a new packet
        packet_header = re.match("^\t([^\t{}]+.+)",line) #gets packet headers
        if packet_header != None:
            parts = packet_header.group(1)
            parts = parts.split()
            
            current_packet = packet.Packet(parts)
            dic[current_packet.name] = current_packet

        block_header = re.match("^\t\t([^{}]+.+)",line) #gets packet block header
        if block_header != None:
            parts = block_header.group(1)
            parts = parts.split()
            
            current_block = packet.PacketBlock(parts)
            current_packet.addBlock(current_block)
            
        block_data  = re.match("^\t\t([{}]+.+)",line)  #gets block data
        if block_data != None:
            parts = block_data.group(1)
            parts = parts.split()
            parts.remove('{')
            parts.remove('}')
            current_var = packet.PacketBlockVariable(parts[0], parts[1])
            current_block.addVar(current_var)

    return dic

def print_packet_list(packet_list):
    for packet in packet_list:
        print '======================================'
        print packet
        
        for block in packet_list[packet].blocks:
            print '\t' + block.name
            
            for var in block.vars:
                print '\t\t' + var.name + '   ' + var.lltype

def get_all_types(packet_list):
    type_set = set([])
    for packet in packet_list:
        for block in packet_list[packet].blocks:
            for var in block.vars:
                type_set.add(var.lltype)                

    type_list = list(type_set)
    type_list.sort()
    return type_list

def main():
    p_list = parse_packets()
    #print_packet_list(p_list)

    p_typelist = get_all_types(p_list)
    pprint.pprint(p_typelist)
    
if __name__ == "__main__":
    main()
