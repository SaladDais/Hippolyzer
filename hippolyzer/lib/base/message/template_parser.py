
"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""

#standard libraries
import struct
import string
import re
import pprint

#local libraries
import template
from data import msg_tmpl
from msgtypes import MsgFrequency, MsgTrust, MsgEncoding
from msgtypes import MsgDeprecation, MsgBlockType, MsgType, sizeof

MESSAGE = 1
BLOCK = 2
DATA = 3


class MessageTemplateParser(object):
    """a parser which parses the message template and creates MessageTemplate objects
       which are stored in self.message_templates
    """
    def __init__(self, template_file):
        if template_file == None:
            raise exc.MessageTemplateNotFound("initializing template parser")

        self.template_file = template_file
        self.message_templates = []
        self.version = ''
        self.count = 0
        self.state = 0
        self._parse_template_file()


    def _add_template(self, new_template):
        self.count += 1
        self.message_templates.append(new_template)

    def _parse_template_file(self):

        #regular expressions
        self.template_file.seek(0)
        lines = self.template_file
        start_re = '.*\{.*'
        end_re = '.*\}.*'
        block_data_re = '.*?(\w+)\s+(\w+)(\s+(\d+))?.*'
        block_header_re = '.*?(\w+)\s+(\w+)(\s+(\d+))?.*'
        message_header_re = '.*?(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)(\s+(\w+))?.*'
        version_re = "version.(.+)"
        comment_re = "^\s*//.*$"

        current_template = None
        current_block = None


        while True:
            try:
                line = lines.next()
            except StopIteration:
                break
            if re.match(comment_re, line):
                continue

            start = re.match(start_re, line)
            end = re.match(end_re, line)

            if self.version == '':
                version_test = re.match(version_re, line) #gets packet headers
                if version_test != None:
                    parts = version_test.group(1)
                    parts = parts.split()
                    self.version = float(parts[0])


            if start:
                self.state += 1

            if self.state == MESSAGE:
                message_header = re.match(message_header_re, line)
                if message_header != None:
                    current_template = self._start_new_template(message_header)
                    self._add_template(current_template)

            if self.state == BLOCK:
                block_header = re.match(block_header_re, line)
                if block_header != None:
                    current_block = self._start_new_block(block_header)
                    current_template.add_block(current_block)

            if self.state == DATA:
                block_data = re.match(block_data_re, line)
                if block_data != None:
                    current_block.add_variable(self._start_new_var(block_data))

            if end:
                self.state -= 1


    def _start_new_template(self, match):

        new_template = template.MessageTemplate(match.group(1))

        frequency = None
        if match.group(2) == 'Low':
            frequency = MsgFrequency.LOW_FREQUENCY_MESSAGE
        elif match.group(2) == 'Medium':
            frequency = MsgFrequency.MEDIUM_FREQUENCY_MESSAGE
        elif match.group(2) == 'High':
            frequency = MsgFrequency.HIGH_FREQUENCY_MESSAGE
        elif match.group(2) == 'Fixed':
            frequency = MsgFrequency.FIXED_FREQUENCY_MESSAGE

        new_template.frequency = frequency

        msg_num = string.atoi(match.group(3),0)
        if frequency == MsgFrequency.FIXED_FREQUENCY_MESSAGE:   
            #have to do this because Fixed messages are stored as a long in the template
            binTemp = struct.pack('>L', string.atol(match.group(3),0))
            msg_num_hex = binTemp
            msg_num = struct.unpack('>h', '\x00' + binTemp[3])[0]
        elif frequency == MsgFrequency.LOW_FREQUENCY_MESSAGE:
            msg_num_hex = struct.pack('>BBB', 0xff, 0xff, msg_num)
        elif frequency == MsgFrequency.MEDIUM_FREQUENCY_MESSAGE:
            msg_num_hex = struct.pack('>BB', 0xff, msg_num)
        elif frequency == MsgFrequency.HIGH_FREQUENCY_MESSAGE:
            msg_num_hex = struct.pack('>B', msg_num)

        new_template.msg_num = msg_num
        new_template.msg_num_hex = msg_num_hex

        msg_trust = None
        if match.group(4) == 'Trusted':
            msg_trust = MsgTrust.LL_TRUSTED
        elif match.group(4) == 'NotTrusted':
            msg_trust = MsgTrust.LL_NOTRUST

        new_template.msg_trust = msg_trust                 

        msg_encoding = None
        if match.group(5) == 'Unencoded':
            msg_encoding = MsgEncoding.LL_UNENCODED
        elif match.group(5) == 'Zerocoded':
            msg_encoding = MsgEncoding.LL_ZEROCODED

        new_template.msg_encoding = msg_encoding

        msg_dep = None
        if match.group(7) != None:
            if match.group(7) == 'Deprecated':
                msg_dep = MsgDeprecation.LL_DEPRECATED
            elif match.group(7) == 'UDPDeprecated':
                msg_dep = MsgDeprecation.LL_UDPDEPRECATED
            elif match.group(7) == 'UDPBlackListed':
                msg_dep = MsgDeprecation.LL_UDPBLACKLISTED
            elif match.group(7) == 'NotDeprecated':
                msg_dep = MsgDeprecation.LL_NOTDEPRECATED
        else:
            msg_dep = MsgDeprecation.LL_NOTDEPRECATED
        if msg_dep == None:
            print match.groups()
        new_template.msg_deprecation = msg_dep

        return new_template

    def _start_new_block(self, match):

        new_block = template.MessageTemplateBlock(match.group(1))

        block_type = None
        block_num = 0

        if match.group(2) == 'Single':
            block_type = MsgBlockType.MBT_SINGLE
        elif match.group(2) == 'Multiple':
            block_type = MsgBlockType.MBT_MULTIPLE
            block_num = int(match.group(4))
        elif match.group(2) == 'Variable':
            block_type = MsgBlockType.MBT_VARIABLE

        #LDE 230ct2008 block_type vs block.type issues...
        new_block.block_type = block_type
        new_block.number = block_num

        return new_block

    def _start_new_var(self, match):

        type_string = match.group(2)
        var_type = None
        var_size = -1
        if type_string == 'U8':
            var_type = MsgType.MVT_U8
        elif type_string == 'U16':
            var_type = MsgType.MVT_U16                    
        elif type_string == 'U32':
            var_type = MsgType.MVT_U32                    
        elif type_string == 'U64':
            var_type = MsgType.MVT_U64                    
        elif type_string == 'S8':
            var_type = MsgType.MVT_S8                    
        elif type_string == 'S16':
            var_type = MsgType.MVT_S16                    
        elif type_string == 'S32':
            var_type = MsgType.MVT_S32                   
        elif type_string == 'S64':
            var_type = MsgType.MVT_S64                    
        elif type_string == 'F32':
            var_type = MsgType.MVT_F32                    
        elif type_string == 'F64':
            var_type = MsgType.MVT_F64                    
        elif type_string == 'LLVector3':
            var_type = MsgType.MVT_LLVector3                    
        elif type_string == 'LLVector3d':
            var_type = MsgType.MVT_LLVector3d                    
        elif type_string == 'LLVector4':
            var_type = MsgType.MVT_LLVector4                    
        elif type_string == 'LLQuaternion':
            var_type = MsgType.MVT_LLQuaternion                    
        elif type_string == 'LLUUID':
            var_type = MsgType.MVT_LLUUID                    
        elif type_string == 'BOOL':
            var_type = MsgType.MVT_BOOL                    
        elif type_string == 'IPADDR':
            var_type = MsgType.MVT_IP_ADDR                    
        elif type_string == 'IPPORT':
            var_type = MsgType.MVT_IP_PORT                    
        elif type_string == 'Fixed' or  type_string == 'Variable':
            if type_string == 'Fixed':
                var_type = MsgType.MVT_FIXED
            elif type_string == 'Variable':
                var_type = MsgType.MVT_VARIABLE

            var_size = int(match.group(4))
            if var_size <= 0:
                raise exc.MessageTemplateParsingError("variable size %s does not match %s" % (var_size, type_string))
        #if the size hasn't been read yet, then read it from message_types
        if var_size == -1:
            var_size = sizeof(var_type)

        #LDE 23oct2008 add var+type to creation of MTV object for subsequent formmating goodness


        return template.MessageTemplateVariable(match.group(1), \
                                                var_type, var_size)



def print_packet_names(packet_list):
    frequency_counter = {"low":0, 'medium':0, "high":0, 'fixed':0}
    counter = 0
    for packet in packet_list:
        print '================================================================================='
        counter += 1
        frequency_counter[packet.get_frequency_as_string()]+=1
        #if packet.get_frequency_as_string() == "low":
        print counter, packet.get_name() + ' ' + packet.get_frequency_as_string()
        print '================================================================================='
    print
    for counters in frequency_counter:
        print counters, frequency_counter[counters]
    print

def print_packet_list(packet_list):
    for packet in packet_list:
        print '================================================================================='
        print packet.get_name() + ' ' + packet.get_frequency_as_string() + ' ' + \
                str(packet.get_message_number()) + ' ' + packet.get_message_hex_num() + \
                ' ' + packet.get_message_trust_as_string() + ' ' + \
                packet.get_message_encoding_as_string() + ' ' + packet.get_deprecation_as_string()

        for block in packet.get_blocks():

            print '\t' + str(block.get_name()) + ' ' + block.get_block_type_as_string() + ' ' + \
                  str(block.get_block_number())
            for variable in block.get_variables():
                sz = len(variable.get_name())
                print '\t\t' + variable.get_name().ljust(20) +"\t" + variable.get_type_as_string()

def get_all_types(packet_list):
    type_set = set([])
    for packet in packet_list:
        for block in packet.get_blocks():
            for variable in block.get_variables():
                type_set.add(variable.get_type_as_string())  #LDE 23oct2008 display using _as_string call

    type_list = list(type_set)
    type_list.sort()
    return type_list

def main():
    """tidied up this test which didn't seem to be working for me at first til I made a few changes"""
    parser = MessageTemplateParser(msg_tmpl)
    #parser._parse_template_file()  #LDE 23oct2008 part of tidying up thing above
    templates = parser.message_templates
    print_packet_names(templates)
    print_packet_list(templates)

    p_typelist = get_all_types(templates)
    pprint.pprint(p_typelist)
    return

if __name__ == "__main__":
    main()



