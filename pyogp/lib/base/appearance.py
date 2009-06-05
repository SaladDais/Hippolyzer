# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import uuid

#related
from eventlet import api

# pyogp

# pyogp messaging
from pyogp.lib.base.message.message_handler import MessageHandler
from pyogp.lib.base.message.packets import *
from pyogp.lib.base.utilities.helpers import Helpers

# initialize logging
logger = getLogger('pyogp.lib.base.appearance')
log = logger.log

# ToDo: make this all go!
class Appearance(object):
    """The Appearance class handles appearance of an Agent() instance

    Sample implementations: 
    Tests: 
    """

    def __init__(self, settings = None, agent = None):
        """ initialize the appearance manager """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        self.agent = agent

        self.helpers = Helpers()
        # ~~~~~~~~~
        # Callbacks
        # ~~~~~~~~~

        onAgentWearablesUpdate_received = self.agent.message_handler.register('AgentWearablesUpdate')
        onAgentWearablesUpdate_received.subscribe(self.helpers.log_packet, self)

        '''
        onAgentDataUpdate_received = self.agent.message_handler.register('AgentDataUpdate')
        onAgentDataUpdate_received.subscribe(self.helpers.log_packet, self)
        '''

    def request_agent_wearables(self):
        """ ask the simulator what the avatar is wearing """

        packet = AgentWearablesRequestPacket()

        packet.AgentData['AgentID'] = self.agent.agent_id
        packet.AgentData['SessionID'] = self.agent.session_id

        self.agent.region.enqueue_message(packet())

# ~~~~~~~~~
# Callbacks
# ~~~~~~~~~


        '''
        {
        	AgentWearablesUpdate Low 382 Trusted Zerocoded
        	{
        		AgentData	Single
        		{	AgentID		LLUUID	}
        		{	SessionID	LLUUID	}
        		{	SerialNum	U32	}	// U32, Increases every time the wearables change for a given agent.  Used to avoid processing out of order packets.
        	}
        	{
        		WearableData	Variable
        		{	ItemID		LLUUID	}
        		{	AssetID		LLUUID	}
        		{	WearableType U8	}	// U8, LLWearable::EWearType
        	}
        }
        '''

"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

