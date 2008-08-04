from zope.interface import Interface, Attribute

class IMessageData(Interface):
    """base interface for data that can be serialized to be sent over
       a network, or deserialized from networked received data. """
    name       = Attribute("""name of the message""")
    size       = Attribute("""size of the message""")
    block_map  = Attribute("""map of the blocks for the message""")

    def add_block(block):
        """ adds a given block to the message """
    def get_block(block_name):
        """ gets one of the message's blocks """
        
    def add_data(block_name, var_name, data, data_size):
        """ adds data to one of the message's blocks """        
    
class IMessageBuilder(Interface):
    """base interface for a message builder"""
    current_msg    = Attribute("""the message built/being built""")

    def is_built():
        """ returns true if the message has been built """

    def build_message(offset_size):
        """ returns the message and its size in serialized form. """

    def new_message(message_name):
        """ creates a new message that will be used to build into. """

    def next_block(block_name):
        """ sets the next block of the current message that we will be
            adding data to. """
        #NOTE: might be helpful to have a way to have this method mixed
        #with the add_data method. It IS Python btw.

    def add_data(var_name, data, data_type):
        """ adds data to the current block of message being built """

class IMessageReader(Interface):
    """base interface for a message builder"""
    current_msg    = Attribute("""message read/being read""")
    
    def validate_message(message_buffer, buffer_size):
        """ makes sure the message is a valid message that can be read """

    def read_message(message_buffer):
        """ reads the message and parses its data """

    def get_data(block_name, var_name, data_type, block_number = 0):
        """ gets data from a block in the message """

    def clear_message():
        """ clears the message being read """

"""
Due to the fact that LLSD can be sent multiple different ways, we have can
have different types of senders for an LLSD message. We can send to
eventqueue, http, or to capabilities. There should then be something that
maps destination (host) to a sender type. Sending an llsd message is then
delgated to the sender, rather than sent directly by the messaging system.
"""
class HTTPSender(Interface):
    pass
