"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""
# standard python libs
from logging import getLogger
import socket
import traceback

# related
from eventlet import api

# pyogp
from pyogp.lib.base.message.circuit import Host
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.network.net import NetUDPClient

# initialize logging
logger = getLogger('message.udpproxy')

class UDPProxy(UDPDispatcher):
    """ proxies a Second Life viewer's UDP connection to a region """

    def __init__(self, sim_ip, sim_port, viewer_facing_port, target_facing_port, udp_client = None, settings = None, message_handler = None, message_template = None, message_xml = None):
        """ initialize a UDP proxy, extending the UDPDispatcher """

        super(UDPProxy, self).__init__(udp_client, settings, message_handler, message_template, message_xml)

        self.settings.PROXY_LOGGING = True
        self.settings.ENABLE_DEFERRED_PACKET_PARSING = False # ToDo: remove this
    
        self.target_host = Host((sim_ip, sim_port))
        self.local_host = None
        self.viewer_address = None

        self.target_udp_client = self.udp_client # region facing
        self.target_socket = self.socket # already spun up as part of the parent UDPDispatcher class instance
        self.target_socket.bind((socket.gethostname(), target_facing_port)) # bind it to a port
        self.target_socket.setblocking(0) # set the socket to nonblocking

        self.proxy_udp_client = NetUDPClient()  # the viewer's socket
        self.proxy_socket = self.proxy_udp_client.start_udp_connection() # grab a socket!
        self.proxy_socket.bind((socket.gethostname(), viewer_facing_port)) # bind it to a port
        self.proxy_socket.setblocking(0) # set the socket to nonblocking
      
        # the viewer needs a local hostname to connect to, as well as a port
        self.hostname = self.proxy_socket.getsockname()[0]

        self.local_host = Host((self.hostname, viewer_facing_port)) # populate this convenience reference

        #logger.debug("Bound proxy for region %s to %s" % (self.target_host, self.target_socket.getsockname()))
        #logger.debug("Bound proxy for viewer (%s) to %s" % (self.local_host, self.proxy_socket.getsockname()))
        logger.info("Initialized the UDPProxy for %s" % (self.target_host))

    def start_proxy(self):

        logger.debug("Starting proxies in UDPProxy")
        
        api.sleep(2)

        self._is_running = True

        api.spawn(self._send_viewer_to_sim)
        api.spawn(self._receive_sim_to_viewer)

        while self._is_running:

            api.sleep(0)


    def _send_viewer_to_sim(self):

        # todo: find a way to not try and send data we just received
        self.proxy_socket_is_locked = False

        while self._is_running:

            msg_buf, msg_size = self.proxy_udp_client.receive_packet(self.proxy_socket)
        
            if not self.viewer_address:
                self.viewer_address = self.proxy_udp_client.get_sender()

            if msg_size > 0:
                try:
                    recv_packet = self.receive_check(self.proxy_udp_client.get_sender(),
                                                                    msg_buf, 
                                                                    msg_size)

                    logger.info("Sending message:%s ID:%s" % (recv_packet.name, recv_packet.packet_id))
                    logger.debug(recv_packet) # ToDo: make this optionally llsd logging once that's in
                except Exception, error:
                    logger.error("Problem handling viewer to sim proxy: %s." % (error))
                    traceback.print_exc()
        
                self.target_udp_client.send_packet(self.target_socket, 
                                                    msg_buf, 
                                                    self.target_host)

                
            api.sleep(0)

    def _receive_sim_to_viewer(self):

        while self._is_running:

            msg_buf, msg_size = self.target_udp_client.receive_packet(self.target_socket)

            if msg_size > 0:
                try:
                    recv_packet = self.receive_check(self.target_udp_client.get_sender(),
                                                                msg_buf, 
                                                                msg_size)

                    logger.info("Receiving message:%s ID:%s" % (recv_packet.name, recv_packet.packet_id))
                    logger.debug(recv_packet) # ToDo: make this optionally llsd logging once that's in
                except Exception, error:
                    logger.warning("Problem trying to handle sim to viewer proxy : %s" % (error))
                    traceback.print_exc()
            
                self.proxy_udp_client.send_packet(self.proxy_socket,
                                                    msg_buf,
                                                    self.viewer_address)

                
            api.sleep(0)