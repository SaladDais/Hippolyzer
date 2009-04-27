from template import MsgData, MsgBlockData, MsgVariableData

#NOTE: right now there is no checking with the template
class Message(MsgData):

    def __init__(self, name, *args):
        super(Message, self).__init__(name)
        self.parse_blocks(args)

    def parse_blocks(self, block_list):
        for block in block_list:
            #can have a list of blocks if it is multiple or variable
            if type(block) == list:
                for bl in block:
                    self.add_block(bl)                                
            else:
                self.add_block(block)                                

class Block(MsgBlockData):

    def __init__(self, name, **kwds):
        super(Block, self).__init__(name)
        self.__parse_vars(kwds)

    def __parse_vars(self, var_list):
        for variable_name in var_list:
            variable_data = var_list[variable_name]
            variable = MsgVariableData(variable_name, variable_data)
            self.add_variable(variable)

"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

