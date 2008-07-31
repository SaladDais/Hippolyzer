from zope.component import getGlobalSiteManager
gsm = getGlobalSiteManager()

from pyogp.lib.base.data import msg_tmpl
from pyogp.lib.base.message.message_llsd_builder import LLSDMessageBuilder
from pyogp.lib.base.message.message_template_parser import MessageTemplateParser
from pyogp.lib.base.message.message_template_builder import MessageTemplateBuilder
from pyogp.lib.base.message.message_template_reader import MessageTemplateReader
from pyogp.lib.base.message.message_template_dict import TemplateDictionary

class MessageSystem(object):
    def __init__():
        self.builder      = None
        self.reader       = None
        self.circuit_info = None
        self.socket       = None

        self.llsd_builder       = LLSDMessageBuilder()
        #self.llsd_reader        = LLSDMessageReader()

        template_dict           = self.load_template(msg_tmpl)
        self.template_builder   = MessageTemplateBuilder(template_dict)
        self.template_reader    = MessageTemplateReader(template_dict)

    def load_template(self, template_file):
        #use the parser to load the message_template.msg message templates
        parser                  = MessageTemplateParser(msg_tmpl)
        template_list           = parser.message_templates
        return TemplateDictionary(self.template_list)

    def receive_check(self):
        #determine if we have any messages that can be received through UDP
        #also, check and decode the message we have received
        pass
                        
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

    
