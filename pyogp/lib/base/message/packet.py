import grokcore.component as grok

from types import PackFlags
from interfaces import IUDPPacket, IMessageData

class UDPPacket(grok.Adapter):
    grok.implements(IUDPPacket)
    grok.context(IMessageData)
    
    def __init__(self, context):
        self.name = context.name
        self.send_flags         = PackFlags.LL_NONE
        self.packet_id          = 0 #aka, sequence number

        self.message_data       = context
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
