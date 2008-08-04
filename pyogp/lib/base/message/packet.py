from pyogp.lib.base.message.data_unpacker import DataUnpacker
from pyogp.lib.base.message.message_types import PacketLayout, MsgType

class Packet(object):
    def __init__(self, sock, packet_buffer, buffer_length, params):
        self.name = ''
        self.socket             = sock
        self.buffer             = packet_buffer
        self.buffer_length      = buffer_length
        self.retries            = 0
        self.host               = None
        self.expiration_time    = 0
        
        if params != {}:
            self.host = params['host']
            self.retries = params['retries']

        self.packet_id = DataUnpacker().unpack_data(packet_buffer, \
                                                    MsgType.MVT_U32, \
                                                    PacketLayout.PACKET_ID_LENGTH)
