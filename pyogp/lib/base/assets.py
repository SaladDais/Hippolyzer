# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import uuid

#related
from eventlet import api

# pyogp
from pyogp.lib.base.datamanager import DataManager
# pyogp messaging
from pyogp.lib.base.message.message_handler import MessageHandler
from pyogp.lib.base.message.packets import *
from pyogp.lib.base.utilities.helpers import Helpers
from pyogp.lib.base.exc import NotImplemented
from pyogp.lib.base.objects import Object
from pyogp.lib.base.datatypes import *


# initialize logging
logger = getLogger('pyogp.lib.base.assets')
log = logger.log

class AssetManager(DataManager):
    """
    The AssetManager class handles the assets of an Agent() instance

    Sample implementations: 
    Tests: 
    """

    def __init__(self, agent, settings = None):
        super(AssetManager, self).__init__(agent, settings)
        self.requests = [] # queue of requests?
        self.assets = {} # indexed by assetID?

    def enable_callbacks(self):
        self.agent.region.message_handler.register('TransferInfo').subscribe(self.onTransferInfo)
        self.agent.region.message_handler.register('TransferPacket').subscribe(self.onTransferPacket)

    def request_asset(self, assetID, assetType, isPriority):
        self.requests.append(Asset(assetID, assetType, isPriority))
        packet = TransferRequestPacket()
        #TransferInfo 
        transferID = UUID()  #associate the assetID with the transferID
        transferID.random()
        packet.TransferInfo['TransferID'] = transferID
        packet.TransferInfo['ChannelType'] = 2 
        packet.TransferInfo['SourceType'] = 2
        if isPriority:
            packet.TransferInfo['Priority'] = 1.0
        else:
            packet.TransferInfo['Priority'] = 0.0
        packet.TransferInfo['Params'] = assetID.get_bytes() \
                                        + Helpers().int_to_bytes(5) #FIXME  <-assetID & type endianness of type may not be correct
        self.agent.region.enqueue_message(packet())
        return transferID

    def onTransferInfo(self, packet):
        log(INFO, "TransferInfo received %s" % packet)
        #raise NotImplemented("onTranferInfo")

    def onTransferPacket(self, packet):
        # fill in data for Asset in the requests queue and pop it off and story in assets dict
        log(INFO, "TransferPacket received %s" % packet)
        #raise NotImplemented("onTransferPacket")

    def get_asset(self, xxxID):
        raise NotImplemented("get_asset")

    def pending_downloads(self):
        if len(self.requests) > 0:
            return True
        return False
    
class Asset(object):
    def __init__(self, assetID, assetType, isPriority):
        self.assetID = assetID
        self.assetType = assetID
        self.isPriority = isPriority
        self.data = None
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

