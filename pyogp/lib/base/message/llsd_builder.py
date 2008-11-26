"""
@file llsd_builder.py
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

from template import MsgData, MsgBlockData, MsgVariableData

class LLSDMessageBuilder(object):
    #implements(IMessageBuilder)

    def __init__(self):
        self.current_template = None
        self.current_msg = None
        self.current_block = None

        self.cur_msg_name = ''
        self.cur_block_name = ''
        self.has_been_built = False

    def is_built(self):
        return self.has_been_built
                 
    def build_message(self):
        """ this does not serialize it for this type of builder. The message
            will be put in standard Python form and will need to be formatted
            based on who the target is (xml? something else?) """
        msg = {}
        for block in self.current_msg.blocks:
            #message can have multiple of the same block names, so
            #message actually holds a block list
            block_list = self.current_msg.blocks[block]
            
            for block_data in block_list:
                #set up the block list
                if block_data.name not in msg:
                    msg[block_data.name] = []
                #each block in the block list is a map
                block = {}
                msg[block_data.name].append(block)                

                #go through the variables for the data
                for variable in block_data.vars.values():
                    #the variable holds the key-value pairs of data
                    #for the block
                    block[variable.name] = variable.data
                    
        self.has_been_built = True
        return msg, len(msg)

    def new_message(self, message_name):
        self.has_been_built = False
        self.current_msg = MsgData(message_name)
        self.cur_msg_name = message_name

    def next_block(self, block_name):
        self.has_been_built = False
        block = MsgBlockData(block_name)
        self.current_msg.add_block(block)
        self.current_block = block
        self.cur_block_name = block_name

    def add_data(self, var_name, data, data_type):
        self.has_been_built = False
        var = MsgVariableData(var_name, data)
        self.current_block.add_variable(var)
