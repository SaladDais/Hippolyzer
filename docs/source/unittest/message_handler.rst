message_handler
===============


.. module:: pyogp.lib.base.tests.message_handler

This is a doctest, the content here is verbatim from the source file at pyogp.lib.base.tests.message_handler.txt.


MessageHandler
~~~~~~~~~~~~~~

The basic message handling event/callbackcase
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, initialize the packet handler
    >>> from pyogp.lib.base.message.message_handler import MessageHandler
    >>> message_handler = MessageHandler()

How about a mock callback handler
    >>> def callback(packet): print packet

    >>> onStartPingCheck_received = message_handler.register("StartPingCheck")
    >>> onStartPingCheck_received.subscribe(callback)

Stage a packet
    >>> from pyogp.lib.base.message.message import Message
    >>> packet = Message('StartPingCheck')

Fire the event, it returns a Message instance
    >>> type(message_handler.handle(packet))
    >>> Message

