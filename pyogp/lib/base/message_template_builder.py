from pyogp.lib.base.message_template import MsgData, MsgBlockData, MsgVariableData

class MessageTemplateBuilder():
    """ This class builds messages at its high level, that is, keeping
        that data in data structure form. A serializer should be used on
        the message produced by this so that it can be sent over a network. """
    def __init__(self, template_dict):
        self.template_list = template_dict
        #when a message is being built, uses this template
        #to add blocks and variables
        self.current_template = None
        self.current_msg = None
        self.current_block = None

        self.cur_msg_name = ''
        self.cur_block_name = ''

    def get_current_message(self):
        return self.current_msg

    def get_current_block(self):
        return self.current_block
        
    def new_message(self, message_name):
        """ Creates a new packet where data can be added to it. Note, the variables
            are added when they are used, or data added to them, so to make sure
            no bad data is sent over the network. """
        self.current_template = self.template_list[message_name]
        #error check

        self.current_msg = MsgData(message_name)
        self.cur_msg_name = message_name

        for block in self.current_template.get_blocks():
            block_data = MsgBlockData(block.get_name())
            self.current_msg.add_block(block_data)

    def next_block(self, block_name):
        self.current_block = self.current_template.get_block(block_name)
        #error check

        self.cur_msg_name = block_name
        
        for variable in self.current_block.get_variables():
            var_data = MsgVariableData(variable.get_name(), variable.get_type())
            self.current_block.add_variable(var_data)

    def add_data(self, var_name, data, data_size):
        self.current_block.add_data(var_name, data, data_size)
            
"""class IMessageSerializer():
    implements ISerializer
    adapts MessageData

    #goes through MessageData and builds a byte string that can be sent over
    #UDP or tcp
    serialize (pack_message, build_message)

    #goes through each block of the message data
    pack_block

    #goes through each block of the message variables, creating a byte-code
    #string to return 
    pack_variable"""


