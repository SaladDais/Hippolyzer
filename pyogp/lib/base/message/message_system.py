from zope.component import getUtility
from pyogp.lib.base.network.interfaces import IUDPClient

from pyogp.lib.base.data import msg_tmpl, msg_details
from pyogp.lib.base.message.message_llsd_builder import LLSDMessageBuilder
from pyogp.lib.base.message.message_template_parser import MessageTemplateParser
from pyogp.lib.base.message.message_template_builder import MessageTemplateBuilder
from pyogp.lib.base.message.message_template_reader import MessageTemplateReader
from pyogp.lib.base.message.message_template_dict import TemplateDictionary
from pyogp.lib.base.message.message_dict import MessageDictionary
from pyogp.lib.base.message.circuitdata import CircuitManager
from pyogp.lib.base.message.message_types import PacketLayout, PackFlags,\
                 MsgType, EndianType, sizeof
from pyogp.lib.base.message.data_unpacker import DataUnpacker
from pyogp.lib.base.message.data_packer import DataPacker

class MessageSystem(object):
    def __init__(self, port):
        #holds the details of the message, or how the messages should be sent,
        #built, and read
        self.send_buffer        = ''
        self.send_flags         = PackFlags.LL_NONE
        self.reliable_msg       = False
        self.reliable_params    = {}

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

        self.udp_client         = getUtility(IUDPClient)
        self.socket = self.udp_client.start_udp_connection(self.port)
        self.unpacker = DataUnpacker()
        self.packer = DataPacker()

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
            msg_buf, msg_size = self.udp_client.receive_packet(self.socket)

            #we have a message
            if msg_size > 0:
                #determine packet flags
                flag = ord(msg_buf[0])
                self.receive_packet_id = \
                    self.unpacker.unpack_data(msg_buf,MsgType.MVT_U32, 1, endian_type=EndianType.BIG)
                
                #determine sender
                host = self.udp_client.get_sender()
                circuit = self.find_circuit(host)

                if flag & PackFlags.LL_ZERO_CODE_FLAG:
                    msg_buf = self.zero_code_expand(msg_buf, msg_size)
    

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
                    elif circuit.is_trusted and \
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
            #if valid_packet == True and msg_size > 0:
            #    break
            #if valid_packet == False or msg_size <= 0:
            break
                
        #now determine if the packet we got was valid (and therefore is stored
        #in the reader)
        if valid_packet == False:
            self.template_reader.clear_message()

        return valid_packet
                                                                             
    def send_reliable(self, host, retries, message_buf=None):
        """ Wants to be acked """
        #sets up the message so send_message will add the RELIABLE flag to
        #the message
        self.reliable_msg = True
        self.send_flags |= PackFlags.LL_RELIABLE_FLAG
        self.reliable_params = {}
        self.reliable_params['retries'] = retries
        self.reliable_params['host'] = host
        self.send_message(host)
    
    def send_retry(self, host, message_buf=None):
        """ This is a retry because we didn't get acked """
        #sets up the message so send_message will add the RETRY flag to it
        unacked_packet.buffer[PacketLayout.PHL_FLAGS] |= PackFlags.LL_RESENT_FLAG
        send_message(host, message_buf)                

    def send_message_llsd(self, host, name, message):
        """ sends an llsd message without going through builder """
        pass

    def send_message(self, host, message_buf=None):
        """ Sends the message that is currently built to the desired host """
        message_size = -1
        
        #make sure host is OK (ip and address aren't null)
        if host.is_ok() == False:
            return

        #build it if it isn't built
        if message_buf == None:
            if self.builder.is_built() == False:
                message_buf, message_size = self.builder.build_message()
            else:
                message_buf = self.builder.message_buffer

        #use circuit manager to get the circuit to send on
        circuit = self.find_circuit(host)

        self.send_buffer = ''

        #put the flags in the begining of the data. NOTE: for 1 byte, endian doesn't matter
        self.send_buffer += self.packer.pack_data(self.send_flags, MsgType.MVT_U8)

        #set packet ID
        self.send_buffer += self.packer.pack_data(circuit.next_packet_id(), \
                                                  MsgType.MVT_S32, \
                                                  endian_type=EndianType.BIG)

        #pack in the offset to the data. NOTE: for 1 byte, endian doesn't matter
        self.send_buffer += self.packer.pack_data(0, MsgType.MVT_U8)

        #also, sends as many acks as we can onto the end of the packet
        #acks are just the packet_id that we are acking
        ack_count = len(circuit.acks)
        if ack_count > 0 and self.builder.cur_msg_name != "PacketAck":
            self.send_flags |= PackFlags.LL_ACK_FLAG
            for packet_id in circuit.acks:
                pack_id = self.packer.pack_data(packet_id, MsgType.MVT_S32)
                message_buf += pack_id

            append_ack_count = self.packer.pack_data(ack_count, MsgType.MVT_U8)
            message_buf += append_ack_count

        #now that the pre-message data is added, add the real data to the end
        self.send_buffer += message_buf

        if self.reliable_msg == True:
            if circuit.unack_packet_count <= 0:
                self.circuit_manager.unacked_circuits[host] = circuit

            circuit.add_reliable_packet(self.socket, self.send_buffer, \
                                        len(self.send_buffer), \
                                        self.reliable_params)

        #TODO: remove this when testing a network
        self.udp_client.send_packet(self.socket, self.send_buffer, host)
        self.reliable_msg = False
        self.reliable_params = {}
                        
    def process_acks(self):
        """ resends all of our messages that were unacked, and acks all
            the messages that others are waiting to be acked. """
        
        #send the ones we didn't get acked
        self.__resend_all_unacked()
        #send the acks we didn't reply to
        self.__send_acks()
        
    def __resend_all_unacked(self):
        """ Resends all packets sent that haven't yet been acked. """
        #now_time = get_time_now()
        
        #go through all circuits in the map
        for circuit in self.circuit_manager.unacked_circuits.values():
            for unacked_packet in circuit.unacked_packets.values():
                unacked_packet.retries -= 1
                #is this correct? should it be serialized or something?
                self.reset_send_buffer()
                self.send_buffer += unacked_packet.buffer
                send_retry(unacked_packet.host, unacked_packet.retries)

                if unacked_packet.retries <= 0:
                    circuit.final_retry_packets[packet.packet_id] = unacked_packet
                    del circuit.unacked_packets[unacked_packet.packet_id]

            #final retries aren't resent, they are just forgotten about. boo
            #for unacked_packet in circuit.final_retry_packets.values():
            #    if now_time > unacked_packet.expiration_time:
            #        del circuit.final_retry_packets[unacked_packet.packet_id] 

    def __send_acks(self):
        """ Acks all packets received that we haven't acked yet. """
        for circuit in self.circuit_manager.circuit_map.values():
            acks_this_packet = 0
            for packet_id in circuit.acks:
                if acks_this_packet == 0:
                    self.new_message("PacketAck")

                self.next_block("Packets")
                self.add_data("ID", packet_id, MsgType.MVT_U32)
                acks_this_packet += 1
                if acks_this_packet > 250:
                    self.send_message(circuit.host)
                    acks_this_packet = 0

            if acks_this_packet > 0:
                self.send_message(circuit.host)
                
            circuit.acks = []

    #the following methods are for a higher-level api
    #new_message is important because it selects the correct builder
            
    def new_message(self, message_name):
        if self.message_dict[message_name] == None:
            return

        flavor = self.message_dict.get_message_flavor(message_name)
        if flavor == 'template':
            self.builder = self.template_builder
        elif flavor == 'llsd':
            self.builder = self.llsd_builder

        self.reliable_msg = False
        self.builder.new_message(message_name)

    def next_block(self, block_name):
        self.builder.next_block(block_name)

    def add_data(self, var_name, data, data_type):
        self.builder.add_data(var_name, data, data_type)

    def get_received_message(self):
        return self.reader.current_msg

    def get_data(self, block_name, var_name, data_type, block_number=0):
        return self.reader.get_data(block_name, var_name, data_type, block_number=0)

    def zero_code_expand(self, msg_buf, msg_size):
        if ord(msg_buf[0]) & PackFlags.LL_ZERO_CODE_FLAG == 0:
            return msg_buf

        header = msg_buf[0:PacketLayout.PACKET_ID_LENGTH]
        inputbuf = msg_buf[PacketLayout.PACKET_ID_LENGTH:]
        newstring = ""
        in_zero = False
        for c in inputbuf:
            if c != '\0':
                if in_zero == True:
                    zero_count = ord(c)
                    zero_count = zero_count -1
                    while zero_count>0:
                        newstring = newstring + '\x00'
                        zero_count = zero_count -1
                    in_zero = False
                else:
                    newstring = newstring + c
            else:
                newstring = newstring + c
                in_zero = True
        return header + newstring
