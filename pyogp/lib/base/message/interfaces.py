"""
@file interfaces.py
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

# preserving contents as comments
pass

'''
from zope.interface import Interface, Attribute

class ITemplateDictionary(Interface):
    """the template dictionary
    
    This component is a utility which knows about all the templates
    and can return the necessary template for each
    """
    
    def get_template(template_name):
        """return the template with this name or None if not found
        
        TODO: Discuss if KeyError is better
        """
    
    def get_template_by_pair(self, frequency, num):
        """return a template by frequency and number"""
        
    def __getitem__(name):
        """alias for get_template"""

class IHost(Interface):
    ip          = Attribute("""address of the host""")
    port        = Attribute("""port of the host""")

    def is_ok():
        """ determines if the host is valid """
    
class IUDPDispatcher(Interface):
    def receive_check(host, msg_buf, msg_size):
        """ gets a raw message and tries to handle it """
    
class IPacket(Interface):
    name                = Attribute("""name of the message""")
    message_data        = Attribute("""name of the message""")

class IUDPPacket(IPacket):
    send_flags          = Attribute("""name of the message""")
    reliable_params     = Attribute("""name of the message""")
    packet_id           = Attribute("""name of the message""")
    
    acks                = Attribute("""name of the message""")
    num_acks            = Attribute("""name of the message""")

    trusted             = Attribute("""name of the message""")
    reliable            = Attribute("""name of the message""")
    resent              = Attribute("""name of the message""")
    
    socket              = Attribute("""name of the message""")
    retries             = Attribute("""name of the message""")
    host                = Attribute("""name of the message""")
    expiration_time     = Attribute("""name of the message""")

class ILLSDPacket(IPacket):
    pass

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
'''
