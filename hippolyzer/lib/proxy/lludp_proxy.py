import logging
import weakref
from typing import Optional, Tuple

from hippolyzer.lib.base.message.message_dot_xml import MessageDotXML
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.message.udpserializer import UDPMessageSerializer
from hippolyzer.lib.base.settings import Settings
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.packets import ProxiedUDPPacket
from hippolyzer.lib.proxy.message import ProxiedMessage
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


class BaseLLUDPProxyProtocol(UDPProxyProtocol):
    def __init__(self, source_addr: Tuple[str, int]):
        super().__init__(source_addr)
        self.settings = Settings()
        self.settings.ENABLE_DEFERRED_PACKET_PARSING = True
        self.settings.HANDLE_PACKETS = False
        self.serializer = UDPMessageSerializer()
        self.deserializer = UDPMessageDeserializer(
            settings=self.settings,
            message_cls=ProxiedMessage,
        )
        self.message_xml = MessageDotXML()

    def _ensure_message_allowed(self, msg: ProxiedMessage):
        if not self.message_xml.validate_udp_msg(msg.name):
            LOG.warning(
                f"Received {msg.name!r} over UDP, when it should come over the event queue. Discarding."
            )
            raise PermissionError(f"UDPBanned message {msg.name}")


class InterceptingLLUDPProxyProtocol(BaseLLUDPProxyProtocol):
    def __init__(self, source_addr: Tuple[str, int], session_manager: SessionManager):
        super().__init__(source_addr)
        self.session_manager: SessionManager = session_manager
        self.session: Optional[Session] = None

    def _handle_proxied_packet(self, packet: ProxiedUDPPacket):
        message: Optional[ProxiedMessage] = None
        region: Optional[ProxiedRegion] = None
        # Try to do an initial region lookup so we have it for handle_proxied_packet()
        if self.session:
            region = self.session.region_by_circuit_addr(packet.far_addr)
        deserialize_exc = None
        try:
            message = self.deserializer.deserialize(packet.data)
            message.direction = packet.direction
        except Exception as e:
            # Hang onto this since handle_proxied_packet doesn't need a parseable
            # message. If that hook doesn't handle the packet then re-raise.
            deserialize_exc = e

        if AddonManager.handle_proxied_packet(self.session_manager, packet,
                                              self.session, region, message):
            # Swallow any error raised by above message deserialization, it was handled.
            return

        if deserialize_exc is not None:
            # handle_proxied_packet() didn't deal with the error, so it's fatal.
            raise deserialize_exc

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

        if message.name == "AgentMovementComplete":
            self.session.main_region = region
            if region.handle is None:
                region.handle = message["Data"]["RegionHandle"]
            LOG.info(f"Setting main region to {region!r}, had circuit addr {packet.far_addr!r}")
            AddonManager.handle_region_changed(self.session, region)

        try:
            region.message_handler.handle(message)
        except:
            LOG.exception("Failed in region message handler")

        message_logger = self.session_manager.message_logger

        handled = AddonManager.handle_lludp_message(
            self.session, region, message
        )

        if message_logger:
            message_logger.log_lludp_message(self.session, region, message)

        if handled:
            return

        if message.name in ("CloseCircuit", "DisableSimulator"):
            region.mark_dead()
        elif message.name == "RegionHandshake":
            region.name = str(message["RegionInfo"][0]["SimName"])

        # This message is owned by an async handler, drop it so it doesn't get
        # sent with the normal flow.
        if message.queued and not message.dropped:
            region.circuit.drop_message(message)

        if not message.dropped:
            region.circuit.send_message(message)

    def close(self):
        super().close()
        if self.session:
            AddonManager.handle_session_closed(self.session)
            self.session_manager.close_session(self.session)
        self.session = None
