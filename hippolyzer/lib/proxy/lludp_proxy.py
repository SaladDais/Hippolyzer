import asyncio
import logging
import weakref
from typing import Optional, Tuple

from hippolyzer.lib.base.message.message_dot_xml import MessageDotXML
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.base.network.transport import UDPPacket
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager
from hippolyzer.lib.proxy.socks_proxy import SOCKS5Server, UDPProxyProtocol


LOG = logging.getLogger(__name__)


class SLSOCKS5Server(SOCKS5Server):
    def __init__(self, session_manager=None):
        super().__init__()
        self.session_manager = weakref.proxy(session_manager)

    def _udp_protocol_creator(self, source_addr):
        return lambda: InterceptingLLUDPProxyProtocol(source_addr, self.session_manager)


class InterceptingLLUDPProxyProtocol(UDPProxyProtocol):
    def __init__(self, source_addr: Tuple[str, int], session_manager: SessionManager):
        super().__init__(source_addr)
        self.session_manager: SessionManager = session_manager
        self.serializer = UDPMessageSerializer()
        self.deserializer = UDPMessageDeserializer(
            settings=self.session_manager.settings,
        )
        self.message_xml = MessageDotXML()
        self.session: Optional[Session] = None
        loop = asyncio.get_event_loop_policy().get_event_loop()
        self.resend_task = loop.create_task(self.attempt_resends())

    async def attempt_resends(self):
        while True:
            await asyncio.sleep(0.1)
            if self.session is None:
                continue
            for region in self.session.regions:
                if not region.circuit or not region.circuit.is_alive:
                    continue
                region.circuit.resend_unacked()

    def _ensure_message_allowed(self, msg: Message):
        if not self.message_xml.validate_udp_msg(msg.name):
            LOG.warning(
                f"Received {msg.name!r} over UDP, when it should come over the event queue. Discarding."
            )
            raise PermissionError(f"UDPBanned message {msg.name}")

    def handle_proxied_packet(self, packet: UDPPacket):
        region: Optional[ProxiedRegion] = None
        # Try to do an initial region lookup so we have it for handle_proxied_packet()
        if self.session:
            region = self.session.region_by_circuit_addr(packet.far_addr)

        # the proxied packet handler is allowed to mutate `packet.data` before
        # the message gets parsed.
        if AddonManager.handle_proxied_packet(self.session_manager, packet,
                                              self.session, region):
            return

        message = self.deserializer.deserialize(packet.data)
        message.direction = packet.direction
        message.sender = packet.src_addr
        message.meta.update(packet.meta)

        assert message is not None
        # Check for UDP bans on inbound messages
        if packet.incoming:
            self._ensure_message_allowed(message)

        if not self.session:
            # This proxy instance isn't tied to a session yet
            # First message should be "UseCircuitCode" and should let us
            # claim a pending session
            if message.name == "UseCircuitCode" and packet.outgoing:
                session_id = message["CircuitCode"][0]["SessionID"]
                self.session = self.session_manager.claim_session(session_id)
                if not self.session:
                    LOG.error(f"Wasn't able to claim session {session_id!r}! Generally this means that the "
                              f"login HTTP request was not intercepted for some reason. Have you configured "
                              f"the viewer to send all HTTP traffic through this proxy?")
                    return
            else:
                LOG.warning(
                    "Received unexpected message %s on %r before circuit open" % (
                        message.name, packet.far_addr
                    )
                )
                return

        if message.name == "UseCircuitCode" and packet.outgoing:
            # This will create a circuit, replace a circuit, or do nothing if
            # circuit is already alive.
            if not self.session.open_circuit(packet.src_addr, packet.dst_addr, self.transport):
                LOG.warning("Couldn't open circuit to %r, did we have a region???" % (
                    packet.dst_addr,
                ))
                return

        region = self.session.region_by_circuit_addr(packet.far_addr)
        if not region:
            LOG.error("No circuit for %r, dropping packet!" % (packet.far_addr,))
            return

        # Process any ACKs for messages we injected first
        region.circuit.collect_acks(message)

        if message.name == "AgentMovementComplete":
            self.session.main_region = region
            if region.handle is None:
                region.handle = message["Data"]["RegionHandle"]
            LOG.info(f"Setting main region to {region!r}, had circuit addr {packet.far_addr!r}")
            AddonManager.handle_region_changed(self.session, region)
        if message.name == "RegionHandshake":
            region.cache_id = message["RegionInfo"]["CacheID"]
            self.session.objects.track_region_objects(region.handle)
            if self.session_manager.settings.USE_VIEWER_OBJECT_CACHE:
                try:
                    region.objects.load_cache()
                except:
                    LOG.exception("Failed to load region cache, skipping")

        try:
            self.session.message_handler.handle(message)
        except:
            LOG.exception("Failed in session message handler")
        try:
            region.message_handler.handle(message)
        except:
            LOG.exception("Failed in region message handler")

        message_logger = self.session_manager.message_logger

        handled = AddonManager.handle_lludp_message(
            self.session, region, message
        )

        # This message is owned by an async handler, drop it so it doesn't get
        # sent with the normal flow.
        if message.queued:
            region.circuit.drop_message(message)

        # Shouldn't mutate the message past this point, so log it now.
        if message_logger:
            message_logger.log_lludp_message(self.session, region, message)

        if handled:
            return

        if message.name in ("CloseCircuit", "DisableSimulator"):
            region.mark_dead()
        elif message.name == "RegionHandshake":
            region.name = str(message["RegionInfo"][0]["SimName"])

        # Send the message if it wasn't explicitly dropped or sent before
        if not message.finalized:
            region.circuit.send(message)

    def close(self):
        super().close()
        if self.session:
            AddonManager.handle_session_closed(self.session)
            self.session_manager.close_session(self.session)
        self.session = None
        self.resend_task.cancel()
