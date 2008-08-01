#third party
from zope.interface import implements

#local
from pyogp.lib.base.message.interfaces import IMessageBuilder
from pyogp.lib.base.message.message_template import MsgData, MsgBlockData, \
     MsgVariableData

class LLSDMessageBuilder(object):
    implements(IMessageBuilder)

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
        for block in self.current_msg.block_map:
            #message can have multiple of the same block names, so
            #message actually holds a block list
            block_list = self.current_msg.block_map[block]
            
            for block_data in block_list:
                #set up the block list
                if block_data.name not in msg:
                    msg[block_data.name] = []
                #each block in the block list is a map
                block = {}
                msg[block_data.name].append(block)                

                #go through the variables for the data
                for variable in block_data.variable_map.values():
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
        var = MsgVariableData(var_name, data_type)
        self.current_block.add_variable(var)
        #size doesn't matter for llsd, formatter will take care of it
        self.current_block.add_data(var_name, data, -1)
