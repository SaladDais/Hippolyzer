
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

# Note: This is currently not in use. Message() is used instead, though, this may be a better 
# implementation in that it references the template

from pyogp.lib.base import exc

class MessageFactory(object):
    #not here, this goes somewhere else
    def new_message(self, message_name):
        """ Creates a new packet where data can be added to it. Note, the variables
            are added when they are used, or data added to them, so to make sure
            no bad data is sent over the network. """
        self.has_been_built = False
        self.current_template = self.template_list[message_name]
        #error check
        if self.current_template == None:
            return
        self.current_msg = MsgData(message_name)
        self.cur_msg_name = message_name

        for block in self.current_template.get_blocks():
            block_data = MsgBlockData(block.name)
            self.current_msg.add_block(block_data)

    def next_block(self, block_name):
        self.has_been_built = False
        if block_name not in self.current_template.block_map:
            #error: 
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
        #more than one block of the same name (when type is MULTIPLE or VARIABLE), so we
        #might have to create a whole new block
        else:
            #make sure it isn't SINGLE and trying to create a new block
            if template_block.type == MsgBlockType.MBT_SINGLE:
                raise exc.MessageBuildingError("block count", "exceding intended block count of 1")


            elif template_block.type == MsgBlockType.MBT_MULTIPLE and \
                 template_block.number == block_data.block_number:
                raise exc.MessageBuildingError("block count", "exceeding intended block count")

            block_data.block_number += 1
            self.current_block = MsgBlockData(block_name)
            self.current_msg.add_block(self.current_block)
            self.cur_block_name = block_name

            for variable in template_block.get_variables():
                var_data = MsgVariableData(variable.name, variable.type)
                self.current_block.add_variable(var_data)

    def add_data(self, var_name, data, data_type):
        """ the data type is passed in to make sure that the programmer is aware of
            what type (and therefore size) of the data that is being passed in. """
        self.has_been_built = False
        if self.current_template == None:
            raise exc.MessageBuildingError("data", "invalid context")

        if self.current_block == None:
            raise exc.MessageBuildingError("data", "adding to what should be a null block")

        template_variable = self.current_template.get_block(self.cur_block_name).get_variable(var_name)
        if template_variable == None:
            raise exc.MessageBuildingError("data", "variable is not appropriate for block")

        #this should be the size of the actual data
        size = sizeof(data_type)

        if data_type == MsgType.MVT_VARIABLE:
            #if its a MVT_VARIABLE type of data, then size will be -1 for the type
            #so the actual size we will have to get from the data itself
            #HACK - this may cause a bug if the data type doesn't have len
            size = len(data)
            #template holds the max size the data can be
            data_size = template_variable.size
            #error check - size can't be larger than the bytes will hold

            self.current_block.add_data(var_name, data, size)

        else:
            #size check can't be done on VARIABLE sized variables
            if self.__check_size(var_name, data, size) == False:
                raise exc.MessageBuildingError("data", "invalid variable size")

            self.current_block.add_data(var_name, data, size)

    def __check_size(self, var_name, data, data_size):
        block = self.template_list[self.cur_msg_name].get_block(self.cur_block_name)
        size = block.get_variable(var_name).size
        if size != data_size:
            return False

        return True



