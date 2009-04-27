packet_handler
==============


.. module:: pyogp.lib.base.tests.packet_handler

This is a doctest, the content here is verbatim from the source file at pyogp.lib.base.tests.packet_handler.txt.

PacketHandler
~~~~~~~~~~~~~

The basic packet handling event/callbackcase
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, initialize the packet handler
    >>> from pyogp.lib.base.message.packethandler import PacketHandler
    >>> packet_handler = PacketHandler()

How about a mock callback handler
    >>> def callback(packet): print packet

    >>> onStartPingCheck_received = packet_handler._register("StartPingCheck")
    >>> onStartPingCheck_received.subscribe(callback)

Stage a packet
    >>> from pyogp.lib.base.message.packets import StartPingCheckPacket
    >>> packet = StartPingCheckPacket()

Fire the event, it returns a packet
Unpossible to include this in the test, the memory ref keeps changing
But, you get the idea...
    event_data = packet_handler._handle(packet)
    <pyogp.lib.base.message.packets.StartPingCheckPacket object at 0x14da450>

