
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
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import uuid

#related
from eventlet import api

# pyogp
from pyogp.lib.base.datamanager import DataManager
from pyogp.lib.base.utilities.enums import TransferChannelType, TransferSourceType, \
     TransferTargetType, TransferStatus

# pyogp messaging
from pyogp.lib.base.message.message_handler import MessageHandler
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.utilities.helpers import Helpers
from pyogp.lib.base.exc import NotImplemented, ResourceError, ResourceNotFound
from pyogp.lib.base.objects import Object
from pyogp.lib.base.datatypes import Vector3, UUID
from pyogp.lib.base.caps import Capability


# initialize logging
logger = getLogger('pyogp.lib.base.assets')
log = logger.log

class AssetManager(DataManager):
    """
    The AssetManager class handles the assets of an Agent() instance

    Sample implementations: 
    Tests: test_assets.py 
    """

    def __init__(self, agent, settings = None):
        super(AssetManager, self).__init__(agent, settings)
        #indexed by assetID
        self.assets = {} 
                
    def enable_callbacks(self):
        pass


    def request_asset(self, assetID, assetType, isPriority, callback=None, itemID=None):
        """
        Sends a TransferRequest to the sim for asset assetID with type assetType,
        will call back with the assetID and True with asset received or False
        if request failed.  On successful request the asset is store in
        self.assets 
        """
        transferID = UUID()  #associate the assetID with the transferID
        transferID.random()
        transferInfoHandler = self.agent.region.message_handler.register('TransferInfo')
        transferPacketHandler = self.agent.region.message_handler.register('TransferPacket')

        def onTransferPacket(packet):
            """
            TransferPacket of a successful TransferRequest
            TODO wait for all all packets to arrive and assemble the data
            """
            # fill in data for Asset in the requests queue and pop it off and story in assets dict
            if str(transferID) == str(packet.blocks['TransferData'][0].get_variable('TransferID').data):
                
                self.assets[str(assetID)] = AssetWearable(assetID, assetType,
                                                         packet.blocks['TransferData'][0].get_variable('Data').data)
                if callback != None:
                    callback(assetID, True)
                transferPacketHandler.unsubscribe(onTransferPacket)
        
        def onTransferInfo(packet):
            """
            Status of TransferRequest
            Account for size and multiple packets
            TODO set packet count
            """
            
            if str(transferID) == str(packet.blocks['TransferInfo'][0].get_variable('TransferID')):
                status = packet.blocks['TransferInfo'][0].get_variable("Status").data
                if status != TransferStatus.OK:
                    log(WARNING, "Request for asset %s failed with status %s" \
                        % (assetID, status))
                    if callback != None:
                        callback(assetID, False)
                    transferPacketHandler.unsubscribe(onTransferPacket)
                transferInfoHandler.unsubscribe(onTransferInfo)
            
        transferInfoHandler.subscribe(onTransferInfo)
        transferPacketHandler.subscribe(onTransferPacket)

        if isPriority:
            priority = 1.0
        else:
            priortity = 0.0

        params = ''
        if itemID != None:
            params += self.agent.agent_id.get_bytes() + \
                      self.agent.session_id.get_bytes() + \
                      self.agent.agent_id.get_bytes() + \
                      UUID().get_bytes() + \
                      itemID.get_bytes()
                      
        params += assetID.get_bytes() + \
                  Helpers().int_to_bytes(assetType) 
        
        self.send_TransferRequest(transferID,
                                  TransferChannelType.Asset,
                                  TransferSourceType.Asset,
                                  priority,
                                  params)


    """
    def upload_asset(self, transaction_id, type_, tempfile, store_local,
                     asset_data=None):
        
        assetUploadCompleteHandler = self.agent.region.message_handler.register('AssetUploadComplete')
        def onAssetUploadComplete(packet):
            log(INFO, "AssetUploadComplete: %s" % packet)
            
        assetUploadCompleteHandler.subscribe(onAssetUploadComplete)
        
        self.send_AssetUploadRequest(transaction_id, type_, tempfile,
                                     store_local)
    """
    def upload_script_via_caps(self, item_id, script):

        def upload_script_via_caps_responder(response):
        
            if response['state'] == 'upload':
                cap = Capability('UpdateScriptAgentResponse', response['uploader'])
                response = cap.POST_FILE(script)
                upload_script_via_caps_responder(response)
            elif response['state'] == 'complete':
                log(DEBUG, "Upload of script Successful")
            else:
                log(WARNING, "Upload failed")
        
        cap = self.agent.region.capabilities['UpdateScriptAgent']
        post_body = {'item_id' : str(item_id), 'target': 'lsl2'}
        custom_headers = {'Accept' : 'application/llsd+xml'}

        try:
            response = cap.POST(post_body, custom_headers)
        except ResourceError, error:
            log(ERROR, error)
            return
        except ResourceNotFound, error:
            log(ERROR, "404 calling: %s" % (error))
            return
        upload_script_via_caps_responder(response)
        
    
        
        
    def upload_via_udp(self):
        pass
    
    def get_asset(self, assetID):
        return self.assets[str(assetID)]

    def send_AssetUploadRequest(self, TransactionID, Type, Tempfile, \
                                StoreLocal, AssetData=None):
        """
        Sends an AssetUploadRequest packet to request that an asset be
        uploaded to the to the sim
        """
        packet = Message('AssetUploadRequest',
                         Block('AssetBlock',
                               TransactionID = TransactionID,
                               Type = Type,
                               Tempfile = Tempfile,
                               StoreLocal = StoreLocal,
                               AssetData = AssetData))
        self.agent.region.enqueue_message(packet)

    
    def send_TransferRequest(self, TransferID, ChannelType, SourceType,
                             Priority, Params):
        """
        sends a TransferRequest packet to request an asset to download, the
        assetID and assetType of the request are stored in the Params variable
        see assets.request_asset for example.
        """
        packet = Message('TransferRequest',
                         Block('TransferInfo',
                               TransferID = TransferID,
                               ChannelType = ChannelType,
                               SourceType = SourceType,
                               Priority = Priority,
                               Params = Params))

        
        self.agent.region.enqueue_message(packet)
        
class Asset(object):
    def __init__(self, assetID, assetType, data):
        self.assetID = assetID
        self.assetType = assetType
        self.data = data

class AssetWearable(Asset):
    
    def __init__(self, assetID, assetType, data):
        super(AssetWearable, self).__init__(assetID, assetType, data)
        self.Version = -1
        self.Name = ''
        self.Description = ''
        self.Type = -1
        self.Permissions = ''
        self.SaleInfo = ''
        self.params = {}
        self.textures = {}
        self.parse_data()

    def parse_data(self):
        tokens = self.data.split()
        i = iter(tokens)
        while True:
            try:
                token = i.next()
                if token.lower() == 'version':
                    self.Version = int(i.next())
                if token.lower() == 'type':
                    self.Type = int(i.next())
                if token.lower() == 'parameters':
                    count = int(i.next())
                    while count > 0:
                        paramID = int(i.next())
                        paramVal = i.next()
                        #TODO Verify this is correct behavior this fix may be a hack
                        if paramVal == '.':
                            self.params[paramID] = 0.0
                        else:
                            self.params[paramID] = float(paramVal)
                        count -= 1
                if token.lower() == 'textures':
                    count = int(i.next())
                    while count > 0:
                        textureID = int(i.next())
                        self.textures[textureID] = UUID(i.next())
                        count -= 1
            except StopIteration:
                break


