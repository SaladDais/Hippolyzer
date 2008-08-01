from zope.component import getGlobalSiteManager
gsm = getGlobalSiteManager()

from pyogp.lib.base.data import msg_tmpl, msg_details
from pyogp.lib.base.message.message_llsd_builder import LLSDMessageBuilder
from pyogp.lib.base.message.message_template_parser import MessageTemplateParser
from pyogp.lib.base.message.message_template_builder import MessageTemplateBuilder
from pyogp.lib.base.message.message_template_reader import MessageTemplateReader
from pyogp.lib.base.message.message_template_dict import TemplateDictionary
from pyogp.lib.base.message.message_dict import MessageDictionary
from pyogp.lib.base.message.circuitdata import CircuitManager
from pyogp.lib.base.message.message_types import PackFlags, sizeof
from pyogp.lib.base.message.data_unpacker import DataUnpacker
from pyogp.lib.base.message.net import *

class MessageSystem(object):
    def __init__(self, port):
        #holds the details of the message, or how the messages should be sent,
        #built, and read
        self.message_details    = None
        self.builder            = None
        self.reader             = None
        self.circuit_manager    = CircuitManager()
        self.port               = port
        self.socket             = None
        #the ID of the packet we most recently received
        self.receive_packet_id  = -1
        
        self.llsd_builder       = LLSDMessageBuilder()
        #self.llsd_reader        = LLSDMessageReader()

        self.message_dict, template_dict    = self.load_template(msg_tmpl, msg_details)
        self.template_builder               = MessageTemplateBuilder(template_dict)
        self.template_reader                = MessageTemplateReader(template_dict)

        self.socket = start_udp_connection(self.port)

        self.unpacker = DataUnpacker()

    def load_template(self, template_file, details_file):
        #use the parser to load the message_template.msg message templates
        parser                  = MessageTemplateParser(msg_tmpl)
        template_list           = parser.message_templates
        
        return MessageDictionary(details_file), TemplateDictionary(template_list)

    def find_circuit(self, host):
        circuit = self.circuit_manager.get_circuit(host)
        if circuit == None:
            #there is a case where we want to return None,
            #when the last packet was protected
            circuit = self.circuit_manager.add_circuit(host, self.receive_packet_id)

        return circuit

    def receive_check(self):
        #determine if we have any messages that can be received through UDP
        #also, check and decode the message we have received

        #just sets it to the last reader we used
        self.reader = self.template_reader
        valid_packet = False
        acks = 0
        recv_reliable = False
        
        while True:
            recv_reliable = False
            msg_buf, msg_size = receive_packet(self.socket)
            
            #we have a message
            if msg_size > 0:
                #determine packet flags
                flag = ord(msg_buf[0])
                self.receive_packet_id = \
                    self.unpacker.unpack_data(msg_buf[1:1+sizeof(MsgType.U32)], MsgType.U32)
                
                #determine sender
                host = get_sender()
                circuit = self.find_circuit(host)

                #ACK_FLAG - means the incoming packet is acking some old packets of ours
                if flag & PackFlags.LL_ACK_FLAG:
                    #apparently, the number of acks is stored at the end
                    #msg_size -= 1
                    #acks += msg_buf[msg_size]
                    #2 == packet ID size, 6 = min packet size
                    #msg_size -= acks * 2 + 6
                    
                    #looop
                        #read the packet ID of the packets that the incoming packet is acking
                        #tell the circuit that the packet with ID has been acked
                    #end loop
                    #if the circuit has no unacked packets, remove it from unacked circuits
                    pass
                
                #RELIABLE - means the message wants to be acked by us
                if flag & PackFlags.LL_RELIABLE_FLAG:
                    recv_reliable = True
                
                #RESENT   - packet that wasn't previously acked was resent
                if flag & PackFlags.LL_RESENT_FLAG:
                    #check if its a duplicate and the sender messed up somewhere
                      #case - ack we sent wasn't received by the sender
                    pass

                valid_packet = self.template_reader.validate_message(msg_buf, msg_size)
                
                #make sure packet validated correctly
                if valid_packet ==  True:
                    #Case - UseCircuitCode - only packet allowed to be valid on an unprotected circuit
                    if circuit == None:
                        valid_packet = False
                        continue
                    #Case - trusted packets can only come in over trusted circuits
                    elif circuit.is_trusted() and \
                        self.template_reader.is_trusted() == False:
                        valid_packet = False
                        continue
                    #Case - make sure its not a banned packet
                    #...
                        
                    valid_packet = self.template_reader.read_message(msg_buf)
    
                #make sure packet was read correctly (still valid)
                if valid_packet ==  True:
                    if recv_reliable == True:
                        circuit.collect_ack(self.receive_packet_id)
                        
            #we are attempting to get a single packet, so break once we get it
            #or we have no more messages to read
            if valid_packet == True and msg_size > 0:
                break

        #now determine if the packet we got was valid (and therefore is stored
        #in the reader)
        if valid_packet == False:
            self.template_reader.clear_message()

        return valid_packet
                                                     
                        
    def send_reliable(self, host):
        """ Wants to be acked """
        #sets up the message so send_message will add the RELIABLE flag to
        #the message
        pass
    
    def send_retry(self, host):
        """ This is a retry because we didn't get acked """
        #sets up the message so send_message will add the RETRY flag to it
        pass
        
    def send_acks(self, host):
        """ Acks all packets received that we haven't acked yet. """
        #go through the circuit manager, find the circuits that need acks
        #and send the acks by building ack messages
        #acks are just the packet_id that we are acking
        pass

    def send_message_circuit(self, circuit):
        """ allows someone to send a message only knowing the circuit """
        #send_message(map_circuit_to_host(circuit))
        pass

    def send_message_llsd(self, host, name, message):
        """ sends an llsd message without going through builder """
        pass

    def send_message(self, host):
        """ Sends the message that is currently built to the desired host """
        #build it if it isn't built
        
        #make sure host is OK (ip and address aren't null)


        #IF UDP/template message
        #use circuit manager to get the circuit to send on

        #if the packet is reliable, add it to the circuit manager's list of
        #unacked circuits
        #also, tell the circuit it is waiting for an ack for this packet

        #also, sends as many acks as we can onto the end of the packet
        #acks are just the packet_id that we are acking
        pass
                        
    def process_acks(self):
        #send the ones we didn't get acked
        resend_all_unacked()
        #send the acks we didn't reply to
        send_acks()
        pass

    def resend_all_unacked(self):
        """ Resends all packets sent that haven't yet been acked. """
        #go through all circuits in the map
            #go through all packets for circuit that are unacked
                #resend the packet  
        pass

    
