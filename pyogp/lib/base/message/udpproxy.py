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

# pyogp
from pyogp.lib.base.udpdispatcher import UDPDispatcher

# initialize logging
logger = getLogger('message.udpproxy')

class UDPProxy(UDPDispatcher):
    """ proxies a Second Life viewer's UDP connection to a region """

    def __init__(self, sim_ip, sim_port, udp_client = None, settings = None, message_handler = None, message_template = None, message_xml = None):
        """ initialize a UDP proxy, mapping 2 ports to a single outbound port """

        super(UDPProxy, self).__init__(udp_client, settings, message_handler, message_template, message_xml)
    
        self.target_host = Host((sim_ip, sim_port))

        # ToDo: change all this crap below!

        # the outgoing connection to the grid
        self.server_facing_udp_client = NetUDPClient()  # the sender, what we are proxying the target to 
        #self.server_facing_socket = self.server_facing_udp_client.start_udp_connection()
        self.server_facing_udp_dispatcher = UDPDispatcher(udp_client=self.server_facing_udp_client)

        # the local connection for the client
        self.viewer_facing_udp_client = NetUDPClient()  # the sender, what we are proxying the target to 
        #self.viewer_facing_socket = self.viewer_facing_udp_client.start_udp_connection()
        self.viewer_facing_udp_dispatcher = UDPDispatcher(udp_client=self.viewer_facing_udp_client)

        logger.debug("Building socket pair for %s udp proxy" % (self.target_host))

    def pin_udp_proxy_ports(self, viewer_facing_port, server_facing_port):

        try:

            # tell the sim_socket to be on a specific port
            logger.debug("Binding server_facing_socket to port %s" % (server_facing_port))
            self.server_facing_udp_dispatcher.socket.bind((socket.gethostname(), server_facing_port))

            # tell the local_socket to be on a specific port
            logger.debug("Binding viewer_facing_socket to port %s" % (viewer_facing_port))
            self.viewer_facing_udp_dispatcher.socket.bind((socket.gethostname(), viewer_facing_port))

            hostname = self.viewer_facing_udp_dispatcher.socket.getsockname()[0]

            self.local_host = Host((hostname, viewer_facing_port))
            
            return hostname

        except Exception, e:
            raise

    def start_proxy(self):

        logger.debug("Starting proxies in UDPProxy")

        self._is_running = True

        while self._is_running:

            try: 
                api.sleep(0)

                self._send_viewer_to_sim()
                self._receive_sim_to_viewer()
            except KeyboardInterrupt:
                logger.INFO("Stopping UDP proxy for %s" % (self.target_host))
                break
            except:
                traceback.print_exc()

    def _send_viewer_to_sim(self):

        logger.debug("Checking for msgs from viewer")

        msg_buf, msg_size = self.viewer_facing_udp_client.receive_packet(self.viewer_facing_udp_dispatcher.socket)
        recv_packet = self.viewer_facing_udp_dispatcher.receive_check(self.viewer_facing_udp_dispatcher.udp_client.get_sender(),
                                                        msg_buf, 
                                                        msg_size)
        
        #logger.debug("viewer_facing_udp_client.receive_packet got %s:%s" % (msg_buf, msg_size))

        if msg_size > 0:
            logger.debug("Sending from %s to %s! Data: len(%s) Host: %s" % (self.viewer_facing_udp_dispatcher.socket.getsockname(), self.server_facing_udp_dispatcher.socket.getsockname(), len(msg_buf), self.target_host))
            self.server_facing_udp_client.send_packet(self.server_facing_udp_dispatcher.socket, msg_buf, self.target_host)

    def _receive_sim_to_viewer(self):

        logger.debug("Checking for msgs from server")

        msg_buf, msg_size = self.server_facing_udp_client.receive_packet(self.server_facing_udp_dispatcher.socket)
        recv_packet = self.server_facing_udp_dispatcher.receive_check(self.server_facing_udp_dispatcher.udp_client.get_sender(),
                                                        msg_buf, 
                                                        msg_size)

        #logger.debug("server_facing_udp_client.receive_packet got %s:%s" % (msg_buf, msg_size))

        if msg_size > 0:
            logger.debug("Sending from %s to %s! Data: len(%s) Host: %s" % (self.server_facing_udp_dispatcher.socket.getsockname(), self.viewer_facing_udp_dispatcher.socket.getsockname(), len(msg_buf), self.target_host))
            self.viewer_facing_udp_client.send_packet(self.viewer_facing_udp_dispatcher.socket, msg_buf, self.local_host)