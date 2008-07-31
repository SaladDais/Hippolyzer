from zope.component import getGlobalSiteManager
gsm = getGlobalSiteManager()

class MessageSystem(object):
    def __init__():
        self.builder      = None
        self.reader       = None
        self.circuit_info = None
        self.socket       = None

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

    def send_message(self, host):
        """ Sends the message that is currently built to the desired host """
        #build it if it isn't built
        
        #make sure host is OK (ip and address aren't null)
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

    
