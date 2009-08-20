
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

from template import MsgData, MsgBlockData, MsgVariableData
from msgtypes import PackFlags

# NOTE: right now there is no checking with the template

# reference message_template.msg for the proper schema for messages

class MessageBase(MsgData):
    """ base representation of a message's name, blocks, and variables.
    
    MessageBase expects a name, and *args consisting of Block() instances 
    (which takes a name and **kwargs)
    """

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
    """ base representation of a block
    
    Block expects a name, and kwargs for variables (var_name = value)
    """

    def __init__(self, name, **kwargs):

        super(Block, self).__init__(name)
        self.__parse_vars(kwargs)

    def __parse_vars(self, var_list):

        for variable_name in var_list:
            variable_data = var_list[variable_name]
            variable = Variable(variable_name, variable_data)
            self.add_variable(variable)

class Variable(MsgVariableData):
    """ base representation of a Variable (purely a convenience alias of MsgVariableData)

    Variable expects a name, and data
    """

    def __init__(self, name, data, var_type = None):

        super(Variable, self).__init__(name, data, var_type)

class Message(MessageBase):
    """ an active message """

    def __init__(self, name, *args):

        #self.name = context.name
        #self.name = name

        super(MessageBase, self).__init__(name)
        self.parse_blocks(args)

        self.original_args = args

        self.send_flags         = PackFlags.LL_NONE
        self.packet_id          = 0 # aka, sequence number
        self.event_queue_id     = 0 # aka, event queue id

        #self.message_data       = context
        #self.blocks = {}
        self.acks               = [] #may change
        self.num_acks           = 0

        self.trusted            = False
        self.reliable           = False
        self.resent             = False

        self.socket             = 0
        self.retries            = 1 #by default
        self.host               = None
        self.expiration_time    = 0

    def add_ack(self, packet_id):

        self.acks.append(packet_id)
        self.num_acks += 1

    def get_var(self, block, variable):

        return self.blocks[block].vars[variable]

    def data(self):
        """ a string representation of a packet """

        string = ''
        delim = '    '

        for k in self.__dict__:

            if k == 'name':
                string += '\nName: %s\n' % (self.name)
            if k == 'blocks':

                for ablock in self.blocks:
                    string += "%sBlock Name:%s%s\n" % (delim, delim, ablock)
                    for somevars in self.blocks[ablock]:

                        for avar in somevars.var_list:
                            zvar = somevars.get_variable(avar)
                            string += "%s%s%s:%s%s\n" % (delim, delim, zvar.name, delim, zvar)

        return string

    def __repr__(self):
        """ a string representation of a packet """

        return self.data()




