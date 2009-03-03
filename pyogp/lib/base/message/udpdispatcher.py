"""
@file udpdispatcher.py
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

# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
#from types import *

# pyogp
from data import msg_tmpl, msg_details
from circuit import CircuitManager
from types import PacketLayout, PackFlags, MsgType, EndianType, sizeof
from data_unpacker import DataUnpacker
from data_packer import DataPacker
from udpserializer import UDPPacketSerializer
from udpdeserializer import UDPPacketDeserializer
from packet import UDPPacket
from message import Message, Block
from pyogp.lib.base.network.net import NetUDPClient
from pyogp.lib.base import exc
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.utilities.helpers import Helpers

# initialize logging
logger = getLogger('...base.message.udpdispatcher')
log = logger.log

#maybe make a global utility
class UDPDispatcher(object):
    #implements(IUDPDispatcher)

    def __init__(self, udp_client = None, settings = None, packet_handler = None):
        #holds the details of the message, or how the messages should be sent,
        #built, and read

        self.circuit_manager = CircuitManager()

        #the ID of the packet we most recently received
        self.receive_packet_id = -1

        self.socket = None

        if udp_client == None:
            self.udp_client = NetUDPClient()
        else:
            self.udp_client = udp_client

        self.socket = self.udp_client.start_udp_connection()
        self.unpacker = DataUnpacker()
        self.packer = DataPacker()

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            self.settings = Settings()

        self.helpers = Helpers()

        # allow the packet_handler to be passed in
        # otherwise, grab the defaults
        if packet_handler != None:
            self.packet_handler = packet_handler
        elif self.settings.HANDLE_PACKETS:
            from pyogp.lib.base.message.packet_handler import PacketHandler
            self.packet_handler = PacketHandler()

    def find_circuit(self, host):
        circuit = self.circuit_manager.get_circuit(host)
        if circuit == None:
            #there is a case where we want to return None,
            #when the last packet was protected
            circuit = self.circuit_manager.add_circuit(host, self.receive_packet_id)

        return circuit

    def receive_check(self, host, msg_buf, msg_size):
        #determine if we have any messages that can be received through UDP
        #also, check and decode the message we have received
        recv_packet = None
        #msg_buf, msg_size = self.udp_client.receive_packet(self.socket)

        #we have a message
        if msg_size > 0:
            udp_deserializer = UDPPacketDeserializer(msg_buf)
            recv_packet = udp_deserializer.deserialize()

            #couldn't deserialize
            if recv_packet == None:
                return None

            #determine sender
            #host = self.udp_client.get_sender()
            circuit = self.find_circuit(host)
            if circuit == None:
                raise exc.CircuitNotFound(host, 'preparing to check for packets')

            #Case - trusted packets can only come in over trusted circuits
            if circuit.is_trusted and \
                recv_packet.trusted == False:
                return None

            circuit.handle_packet(recv_packet)

            if self.settings.ENABLE_UDP_LOGGING:
                if self.settings.ENABLE_BYTES_TO_HEX_LOGGING:
                    hex_string = '<=>' + self.helpers.bytes_to_hex(msg_buf)
                else:
                    hex_string = ''
                log(DEBUG, 'Received packet: %s%s' % (recv_packet.name, hex_string))

            if self.settings.HANDLE_PACKETS:
                self.packet_handler._handle(recv_packet)

        return recv_packet

    def send_reliable(self, message, host, retries):
        """ Wants to be acked """
        #sets up the message so send_message will add the RELIABLE flag to
        #the message
        return self.__send_message(message, host, reliable=True, retries=retries)

    def send_retry(self, message, host):
        """ This is a retry because we didn't get acked """
        #sets up the message so send_message will add the RETRY flag to it
        return self.__send_message(host, message, retrying=True)                

    def send_message(self, message, host):
        return self.__send_message(message, host)

    def __send_message(self, message, host, reliable=False, retries=0, retrying=False):
        """ Sends the message that is currently built to the desired host """
        #make sure host is OK (ip and address aren't null)
        if host.is_ok() == False:
            return

        packet = UDPPacket(message)

        #use circuit manager to get the circuit to send on
        circuit = self.find_circuit(host)

        if reliable == True:
            circuit.prepare_packet(packet, PackFlags.LL_RELIABLE_FLAG, retries)
            if circuit.unack_packet_count <= 0:
                self.circuit_manager.unacked_circuits[host] = circuit
        elif retrying == True:
            circuit.prepare_packet(packet, PackFlags.LL_RESENT_FLAG)
        else:
            circuit.prepare_packet(packet)

        # serialize the data
        serializer = UDPPacketSerializer(packet)

        #serializer = ISerialization(packet)
        send_buffer = serializer.serialize()

        if self.settings.ENABLE_UDP_LOGGING:
            if packet.name in self.settings.UDP_SPAMMERS and self.settings.DISABLE_SPAMMERS:
                pass
            else:
                if self.settings.ENABLE_BYTES_TO_HEX_LOGGING:
                    hex_string = '<=>' + self.helpers.bytes_to_hex(send_buffer)
                else:
                    hex_string = ''
                log(DEBUG, 'Sent packet: %s%s' % (message.name, hex_string))

        #TODO: remove this when testing a network
        self.udp_client.send_packet(self.socket, send_buffer, host)

        return send_buffer

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
                #self.reset_send_buffer()
                self.send_buffer = ''
                self.send_buffer += unacked_packet.buffer
                self.send_retry(unacked_packet.host, unacked_packet.buffer)

                if unacked_packet.retries <= 0:
                    circuit.final_retry_packets[unacked_packet.packet_id] = unacked_packet
                    del circuit.unacked_packets[unacked_packet.packet_id]

            #final retries aren't resent, they are just forgotten about. boo
            #for unacked_packet in circuit.final_retry_packets.values():
            #    if now_time > unacked_packet.expiration_time:
            #        del circuit.final_retry_packets[unacked_packet.packet_id] 

    def __send_acks(self):
        """ Acks all packets received that we haven't acked yet. """
        for circuit in self.circuit_manager.circuit_map.values():
            acks_this_packet = 0
            msg = None

            for packet_id in circuit.acks:
                if acks_this_packet == 0:
                    msg = Message('PacketAck')

                block = Block("Packets", ID=packet_id)
                msg.add_block(block)
                acks_this_packet += 1
                if acks_this_packet > 250:
                    self.send_message(msg, circuit.host)
                    acks_this_packet = 0

            if acks_this_packet > 0:
                self.send_message(msg, circuit.host)    

            circuit.acks = []

    def has_unacked(self):
        for circuit in self.circuit_manager.circuit_map.values():
            if len(circuit.acks) > 0:
                return True

        return False
