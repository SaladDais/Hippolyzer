from pyogp.lib.base.message.data_unpacker import DataUnpacker
from pyogp.lib.base.message.message_types import PacketLayout, MsgType

class Packet(object):
    def __init__(self, sock, packet_buffer, buffer_length, **kwds):
        self.name = ''
        self.socket             = sock
        self.buffer             = packet_buffer
        self.buffer_length      = buffer_length
        self.retries            = 0
        self.host               = None
        self.expiration_time    = 0
        
        if kwds != {}:
            self.host = kwds['host']
            self.retries = kwds['retries']
            self.name = kwds['name']

        id_buf = packet_buffer[PacketLayout.PACKET_ID_LENGTH:PacketLayout.PACKET_ID_LENGTH+4]
        self.packet_id = DataUnpacker().unpack_data(id_buf, MsgType.MVT_U32)
