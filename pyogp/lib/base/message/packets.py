"""
@file packets.py
@date 2009-02-04
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

from pyogp.lib.base.message.message import Message, Block

class RegionPresenceRequestByRegionIDPacket(object):
    ''' a template for a RegionPresenceRequestByRegionID packet '''

    def __init__(self):
        self.name = 'RegionPresenceRequestByRegionID'

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RegionPresenceRequestByRegionID', Block('RegionData', RegionID = self.RegionData['RegionID']))

class GroupAccountSummaryRequestPacket(object):
    ''' a template for a GroupAccountSummaryRequest packet '''

    def __init__(self):
        self.name = 'GroupAccountSummaryRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.MoneyData = {}    # New MoneyData block
        self.MoneyData['RequestID'] = None    # MVT_LLUUID
        self.MoneyData['IntervalDays'] = None    # MVT_S32
        self.MoneyData['CurrentInterval'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupAccountSummaryRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('MoneyData', RequestID = self.MoneyData['RequestID'], IntervalDays = self.MoneyData['IntervalDays'], CurrentInterval = self.MoneyData['CurrentInterval']))

class CancelAuctionPacket(object):
    ''' a template for a CancelAuction packet '''

    def __init__(self):
        self.name = 'CancelAuction'

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['ParcelID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CancelAuction', Block('ParcelData', ParcelID = self.ParcelData['ParcelID']))

class StateSavePacket(object):
    ''' a template for a StateSave packet '''

    def __init__(self):
        self.name = 'StateSave'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['Filename'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('StateSave', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('DataBlock', Filename = self.DataBlock['Filename']))

class UpdateAttachmentPacket(object):
    ''' a template for a UpdateAttachment packet '''

    def __init__(self):
        self.name = 'UpdateAttachment'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.AttachmentBlock = {}    # New AttachmentBlock block
        self.AttachmentBlock['AttachmentPoint'] = None    # MVT_U8

        self.OperationData = {}    # New OperationData block
        self.OperationData['AddItem'] = None    # MVT_BOOL
        self.OperationData['UseExistingAsset'] = None    # MVT_BOOL

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID
        self.InventoryData['FolderID'] = None    # MVT_LLUUID
        self.InventoryData['CreatorID'] = None    # MVT_LLUUID
        self.InventoryData['OwnerID'] = None    # MVT_LLUUID
        self.InventoryData['GroupID'] = None    # MVT_LLUUID
        self.InventoryData['BaseMask'] = None    # MVT_U32
        self.InventoryData['OwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupMask'] = None    # MVT_U32
        self.InventoryData['EveryoneMask'] = None    # MVT_U32
        self.InventoryData['NextOwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupOwned'] = None    # MVT_BOOL
        self.InventoryData['AssetID'] = None    # MVT_LLUUID
        self.InventoryData['Type'] = None    # MVT_S8
        self.InventoryData['InvType'] = None    # MVT_S8
        self.InventoryData['Flags'] = None    # MVT_U32
        self.InventoryData['SaleType'] = None    # MVT_U8
        self.InventoryData['SalePrice'] = None    # MVT_S32
        self.InventoryData['Name'] = None    # MVT_VARIABLE
        self.InventoryData['Description'] = None    # MVT_VARIABLE
        self.InventoryData['CreationDate'] = None    # MVT_S32
        self.InventoryData['CRC'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UpdateAttachment', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('AttachmentBlock', AttachmentPoint = self.AttachmentBlock['AttachmentPoint']), Block('OperationData', AddItem = self.OperationData['AddItem'], UseExistingAsset = self.OperationData['UseExistingAsset']), Block('InventoryData', ItemID = self.InventoryData['ItemID'], FolderID = self.InventoryData['FolderID'], CreatorID = self.InventoryData['CreatorID'], OwnerID = self.InventoryData['OwnerID'], GroupID = self.InventoryData['GroupID'], BaseMask = self.InventoryData['BaseMask'], OwnerMask = self.InventoryData['OwnerMask'], GroupMask = self.InventoryData['GroupMask'], EveryoneMask = self.InventoryData['EveryoneMask'], NextOwnerMask = self.InventoryData['NextOwnerMask'], GroupOwned = self.InventoryData['GroupOwned'], AssetID = self.InventoryData['AssetID'], Type = self.InventoryData['Type'], InvType = self.InventoryData['InvType'], Flags = self.InventoryData['Flags'], SaleType = self.InventoryData['SaleType'], SalePrice = self.InventoryData['SalePrice'], Name = self.InventoryData['Name'], Description = self.InventoryData['Description'], CreationDate = self.InventoryData['CreationDate'], CRC = self.InventoryData['CRC']))

class ParcelJoinPacket(object):
    ''' a template for a ParcelJoin packet '''

    def __init__(self):
        self.name = 'ParcelJoin'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['West'] = None    # MVT_F32
        self.ParcelData['South'] = None    # MVT_F32
        self.ParcelData['East'] = None    # MVT_F32
        self.ParcelData['North'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelJoin', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', West = self.ParcelData['West'], South = self.ParcelData['South'], East = self.ParcelData['East'], North = self.ParcelData['North']))

class ObjectDeletePacket(object):
    ''' a template for a ObjectDelete packet '''

    def __init__(self):
        self.name = 'ObjectDelete'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['Force'] = None    # MVT_BOOL

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectDelete', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], Force = self.AgentData['Force']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class RegionHandleRequestPacket(object):
    ''' a template for a RegionHandleRequest packet '''

    def __init__(self):
        self.name = 'RegionHandleRequest'

        self.RequestBlock = {}    # New RequestBlock block
        self.RequestBlock['RegionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RegionHandleRequest', Block('RequestBlock', RegionID = self.RequestBlock['RegionID']))

class ScriptQuestionPacket(object):
    ''' a template for a ScriptQuestion packet '''

    def __init__(self):
        self.name = 'ScriptQuestion'

        self.Data = {}    # New Data block
        self.Data['TaskID'] = None    # MVT_LLUUID
        self.Data['ItemID'] = None    # MVT_LLUUID
        self.Data['ObjectName'] = None    # MVT_VARIABLE
        self.Data['ObjectOwner'] = None    # MVT_VARIABLE
        self.Data['Questions'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptQuestion', Block('Data', TaskID = self.Data['TaskID'], ItemID = self.Data['ItemID'], ObjectName = self.Data['ObjectName'], ObjectOwner = self.Data['ObjectOwner'], Questions = self.Data['Questions']))

class CreateTrustedCircuitPacket(object):
    ''' a template for a CreateTrustedCircuit packet '''

    def __init__(self):
        self.name = 'CreateTrustedCircuit'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['EndPointID'] = None    # MVT_LLUUID
        self.DataBlock['Digest'] = None    # MVT_FIXED

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CreateTrustedCircuit', Block('DataBlock', EndPointID = self.DataBlock['EndPointID'], Digest = self.DataBlock['Digest']))

class DataHomeLocationRequestPacket(object):
    ''' a template for a DataHomeLocationRequest packet '''

    def __init__(self):
        self.name = 'DataHomeLocationRequest'

        self.Info = {}    # New Info block
        self.Info['AgentID'] = None    # MVT_LLUUID
        self.Info['KickedFromEstateID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DataHomeLocationRequest', Block('Info', AgentID = self.Info['AgentID'], KickedFromEstateID = self.Info['KickedFromEstateID']))

class RemoveTaskInventoryPacket(object):
    ''' a template for a RemoveTaskInventory packet '''

    def __init__(self):
        self.name = 'RemoveTaskInventory'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['LocalID'] = None    # MVT_U32
        self.InventoryData['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RemoveTaskInventory', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('InventoryData', LocalID = self.InventoryData['LocalID'], ItemID = self.InventoryData['ItemID']))

class SystemKickUserPacket(object):
    ''' a template for a SystemKickUser packet '''

    def __init__(self):
        self.name = 'SystemKickUser'

        self.AgentInfo = {}    # New AgentInfo block
        self.AgentInfo['AgentID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SystemKickUser', Block('AgentInfo', AgentID = self.AgentInfo['AgentID']))

class ConfirmXferPacketPacket(object):
    ''' a template for a ConfirmXferPacket packet '''

    def __init__(self):
        self.name = 'ConfirmXferPacket'

        self.XferID = {}    # New XferID block
        self.XferID['ID'] = None    # MVT_U64
        self.XferID['Packet'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ConfirmXferPacket', Block('XferID', ID = self.XferID['ID'], Packet = self.XferID['Packet']))

class ClassifiedInfoUpdatePacket(object):
    ''' a template for a ClassifiedInfoUpdate packet '''

    def __init__(self):
        self.name = 'ClassifiedInfoUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['ClassifiedID'] = None    # MVT_LLUUID
        self.Data['Category'] = None    # MVT_U32
        self.Data['Name'] = None    # MVT_VARIABLE
        self.Data['Desc'] = None    # MVT_VARIABLE
        self.Data['ParcelID'] = None    # MVT_LLUUID
        self.Data['ParentEstate'] = None    # MVT_U32
        self.Data['SnapshotID'] = None    # MVT_LLUUID
        self.Data['PosGlobal'] = None    # MVT_LLVector3d
        self.Data['ClassifiedFlags'] = None    # MVT_U8
        self.Data['PriceForListing'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ClassifiedInfoUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', ClassifiedID = self.Data['ClassifiedID'], Category = self.Data['Category'], Name = self.Data['Name'], Desc = self.Data['Desc'], ParcelID = self.Data['ParcelID'], ParentEstate = self.Data['ParentEstate'], SnapshotID = self.Data['SnapshotID'], PosGlobal = self.Data['PosGlobal'], ClassifiedFlags = self.Data['ClassifiedFlags'], PriceForListing = self.Data['PriceForListing']))

class ReportAutosaveCrashPacket(object):
    ''' a template for a ReportAutosaveCrash packet '''

    def __init__(self):
        self.name = 'ReportAutosaveCrash'

        self.AutosaveData = {}    # New AutosaveData block
        self.AutosaveData['PID'] = None    # MVT_S32
        self.AutosaveData['Status'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ReportAutosaveCrash', Block('AutosaveData', PID = self.AutosaveData['PID'], Status = self.AutosaveData['Status']))

class SetSimPresenceInDatabasePacket(object):
    ''' a template for a SetSimPresenceInDatabase packet '''

    def __init__(self):
        self.name = 'SetSimPresenceInDatabase'

        self.SimData = {}    # New SimData block
        self.SimData['RegionID'] = None    # MVT_LLUUID
        self.SimData['HostName'] = None    # MVT_VARIABLE
        self.SimData['GridX'] = None    # MVT_U32
        self.SimData['GridY'] = None    # MVT_U32
        self.SimData['PID'] = None    # MVT_S32
        self.SimData['AgentCount'] = None    # MVT_S32
        self.SimData['TimeToLive'] = None    # MVT_S32
        self.SimData['Status'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SetSimPresenceInDatabase', Block('SimData', RegionID = self.SimData['RegionID'], HostName = self.SimData['HostName'], GridX = self.SimData['GridX'], GridY = self.SimData['GridY'], PID = self.SimData['PID'], AgentCount = self.SimData['AgentCount'], TimeToLive = self.SimData['TimeToLive'], Status = self.SimData['Status']))

class GroupVoteHistoryItemReplyPacket(object):
    ''' a template for a GroupVoteHistoryItemReply packet '''

    def __init__(self):
        self.name = 'GroupVoteHistoryItemReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.TransactionData = {}    # New TransactionData block
        self.TransactionData['TransactionID'] = None    # MVT_LLUUID
        self.TransactionData['TotalNumItems'] = None    # MVT_U32

        self.HistoryItemData = {}    # New HistoryItemData block
        self.HistoryItemData['VoteID'] = None    # MVT_LLUUID
        self.HistoryItemData['TerseDateID'] = None    # MVT_VARIABLE
        self.HistoryItemData['StartDateTime'] = None    # MVT_VARIABLE
        self.HistoryItemData['EndDateTime'] = None    # MVT_VARIABLE
        self.HistoryItemData['VoteInitiator'] = None    # MVT_LLUUID
        self.HistoryItemData['VoteType'] = None    # MVT_VARIABLE
        self.HistoryItemData['VoteResult'] = None    # MVT_VARIABLE
        self.HistoryItemData['Majority'] = None    # MVT_F32
        self.HistoryItemData['Quorum'] = None    # MVT_S32
        self.HistoryItemData['ProposalText'] = None    # MVT_VARIABLE

        self.VoteItem = {}    # New VoteItem block
        self.VoteItem['CandidateID'] = None    # MVT_LLUUID
        self.VoteItem['VoteCast'] = None    # MVT_VARIABLE
        self.VoteItem['NumVotes'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupVoteHistoryItemReply', Block('AgentData', AgentID = self.AgentData['AgentID'], GroupID = self.AgentData['GroupID']), Block('TransactionData', TransactionID = self.TransactionData['TransactionID'], TotalNumItems = self.TransactionData['TotalNumItems']), Block('HistoryItemData', VoteID = self.HistoryItemData['VoteID'], TerseDateID = self.HistoryItemData['TerseDateID'], StartDateTime = self.HistoryItemData['StartDateTime'], EndDateTime = self.HistoryItemData['EndDateTime'], VoteInitiator = self.HistoryItemData['VoteInitiator'], VoteType = self.HistoryItemData['VoteType'], VoteResult = self.HistoryItemData['VoteResult'], Majority = self.HistoryItemData['Majority'], Quorum = self.HistoryItemData['Quorum'], ProposalText = self.HistoryItemData['ProposalText']), Block('VoteItem', CandidateID = self.VoteItem['CandidateID'], VoteCast = self.VoteItem['VoteCast'], NumVotes = self.VoteItem['NumVotes']))

class ChildAgentUnknownPacket(object):
    ''' a template for a ChildAgentUnknown packet '''

    def __init__(self):
        self.name = 'ChildAgentUnknown'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ChildAgentUnknown', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class ObjectSpinStartPacket(object):
    ''' a template for a ObjectSpinStart packet '''

    def __init__(self):
        self.name = 'ObjectSpinStart'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectSpinStart', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectID = self.ObjectData['ObjectID']))

class CreateGroupReplyPacket(object):
    ''' a template for a CreateGroupReply packet '''

    def __init__(self):
        self.name = 'CreateGroupReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.ReplyData = {}    # New ReplyData block
        self.ReplyData['GroupID'] = None    # MVT_LLUUID
        self.ReplyData['Success'] = None    # MVT_BOOL
        self.ReplyData['Message'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CreateGroupReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('ReplyData', GroupID = self.ReplyData['GroupID'], Success = self.ReplyData['Success'], Message = self.ReplyData['Message']))

class ParcelDwellReplyPacket(object):
    ''' a template for a ParcelDwellReply packet '''

    def __init__(self):
        self.name = 'ParcelDwellReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['LocalID'] = None    # MVT_S32
        self.Data['ParcelID'] = None    # MVT_LLUUID
        self.Data['Dwell'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelDwellReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('Data', LocalID = self.Data['LocalID'], ParcelID = self.Data['ParcelID'], Dwell = self.Data['Dwell']))

class ObjectShapePacket(object):
    ''' a template for a ObjectShape packet '''

    def __init__(self):
        self.name = 'ObjectShape'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['PathCurve'] = None    # MVT_U8
        self.ObjectData['ProfileCurve'] = None    # MVT_U8
        self.ObjectData['PathBegin'] = None    # MVT_U16
        self.ObjectData['PathEnd'] = None    # MVT_U16
        self.ObjectData['PathScaleX'] = None    # MVT_U8
        self.ObjectData['PathScaleY'] = None    # MVT_U8
        self.ObjectData['PathShearX'] = None    # MVT_U8
        self.ObjectData['PathShearY'] = None    # MVT_U8
        self.ObjectData['PathTwist'] = None    # MVT_S8
        self.ObjectData['PathTwistBegin'] = None    # MVT_S8
        self.ObjectData['PathRadiusOffset'] = None    # MVT_S8
        self.ObjectData['PathTaperX'] = None    # MVT_S8
        self.ObjectData['PathTaperY'] = None    # MVT_S8
        self.ObjectData['PathRevolutions'] = None    # MVT_U8
        self.ObjectData['PathSkew'] = None    # MVT_S8
        self.ObjectData['ProfileBegin'] = None    # MVT_U16
        self.ObjectData['ProfileEnd'] = None    # MVT_U16
        self.ObjectData['ProfileHollow'] = None    # MVT_U16

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectShape', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], PathCurve = self.ObjectData['PathCurve'], ProfileCurve = self.ObjectData['ProfileCurve'], PathBegin = self.ObjectData['PathBegin'], PathEnd = self.ObjectData['PathEnd'], PathScaleX = self.ObjectData['PathScaleX'], PathScaleY = self.ObjectData['PathScaleY'], PathShearX = self.ObjectData['PathShearX'], PathShearY = self.ObjectData['PathShearY'], PathTwist = self.ObjectData['PathTwist'], PathTwistBegin = self.ObjectData['PathTwistBegin'], PathRadiusOffset = self.ObjectData['PathRadiusOffset'], PathTaperX = self.ObjectData['PathTaperX'], PathTaperY = self.ObjectData['PathTaperY'], PathRevolutions = self.ObjectData['PathRevolutions'], PathSkew = self.ObjectData['PathSkew'], ProfileBegin = self.ObjectData['ProfileBegin'], ProfileEnd = self.ObjectData['ProfileEnd'], ProfileHollow = self.ObjectData['ProfileHollow']))

class MuteListUpdatePacket(object):
    ''' a template for a MuteListUpdate packet '''

    def __init__(self):
        self.name = 'MuteListUpdate'

        self.MuteData = {}    # New MuteData block
        self.MuteData['AgentID'] = None    # MVT_LLUUID
        self.MuteData['Filename'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MuteListUpdate', Block('MuteData', AgentID = self.MuteData['AgentID'], Filename = self.MuteData['Filename']))

class ParcelPropertiesRequestByIDPacket(object):
    ''' a template for a ParcelPropertiesRequestByID packet '''

    def __init__(self):
        self.name = 'ParcelPropertiesRequestByID'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['SequenceID'] = None    # MVT_S32
        self.ParcelData['LocalID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelPropertiesRequestByID', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', SequenceID = self.ParcelData['SequenceID'], LocalID = self.ParcelData['LocalID']))

class UpdateUserInfoPacket(object):
    ''' a template for a UpdateUserInfo packet '''

    def __init__(self):
        self.name = 'UpdateUserInfo'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.UserData = {}    # New UserData block
        self.UserData['IMViaEMail'] = None    # MVT_BOOL
        self.UserData['DirectoryVisibility'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UpdateUserInfo', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('UserData', IMViaEMail = self.UserData['IMViaEMail'], DirectoryVisibility = self.UserData['DirectoryVisibility']))

class RedoPacket(object):
    ''' a template for a Redo packet '''

    def __init__(self):
        self.name = 'Redo'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('Redo', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('ObjectData', ObjectID = self.ObjectData['ObjectID']))

class FetchInventoryReplyPacket(object):
    ''' a template for a FetchInventoryReply packet '''

    def __init__(self):
        self.name = 'FetchInventoryReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID
        self.InventoryData['FolderID'] = None    # MVT_LLUUID
        self.InventoryData['CreatorID'] = None    # MVT_LLUUID
        self.InventoryData['OwnerID'] = None    # MVT_LLUUID
        self.InventoryData['GroupID'] = None    # MVT_LLUUID
        self.InventoryData['BaseMask'] = None    # MVT_U32
        self.InventoryData['OwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupMask'] = None    # MVT_U32
        self.InventoryData['EveryoneMask'] = None    # MVT_U32
        self.InventoryData['NextOwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupOwned'] = None    # MVT_BOOL
        self.InventoryData['AssetID'] = None    # MVT_LLUUID
        self.InventoryData['Type'] = None    # MVT_S8
        self.InventoryData['InvType'] = None    # MVT_S8
        self.InventoryData['Flags'] = None    # MVT_U32
        self.InventoryData['SaleType'] = None    # MVT_U8
        self.InventoryData['SalePrice'] = None    # MVT_S32
        self.InventoryData['Name'] = None    # MVT_VARIABLE
        self.InventoryData['Description'] = None    # MVT_VARIABLE
        self.InventoryData['CreationDate'] = None    # MVT_S32
        self.InventoryData['CRC'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('FetchInventoryReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('InventoryData', ItemID = self.InventoryData['ItemID'], FolderID = self.InventoryData['FolderID'], CreatorID = self.InventoryData['CreatorID'], OwnerID = self.InventoryData['OwnerID'], GroupID = self.InventoryData['GroupID'], BaseMask = self.InventoryData['BaseMask'], OwnerMask = self.InventoryData['OwnerMask'], GroupMask = self.InventoryData['GroupMask'], EveryoneMask = self.InventoryData['EveryoneMask'], NextOwnerMask = self.InventoryData['NextOwnerMask'], GroupOwned = self.InventoryData['GroupOwned'], AssetID = self.InventoryData['AssetID'], Type = self.InventoryData['Type'], InvType = self.InventoryData['InvType'], Flags = self.InventoryData['Flags'], SaleType = self.InventoryData['SaleType'], SalePrice = self.InventoryData['SalePrice'], Name = self.InventoryData['Name'], Description = self.InventoryData['Description'], CreationDate = self.InventoryData['CreationDate'], CRC = self.InventoryData['CRC']))

class AvatarInterestsUpdatePacket(object):
    ''' a template for a AvatarInterestsUpdate packet '''

    def __init__(self):
        self.name = 'AvatarInterestsUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.PropertiesData = {}    # New PropertiesData block
        self.PropertiesData['WantToMask'] = None    # MVT_U32
        self.PropertiesData['WantToText'] = None    # MVT_VARIABLE
        self.PropertiesData['SkillsMask'] = None    # MVT_U32
        self.PropertiesData['SkillsText'] = None    # MVT_VARIABLE
        self.PropertiesData['LanguagesText'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarInterestsUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('PropertiesData', WantToMask = self.PropertiesData['WantToMask'], WantToText = self.PropertiesData['WantToText'], SkillsMask = self.PropertiesData['SkillsMask'], SkillsText = self.PropertiesData['SkillsText'], LanguagesText = self.PropertiesData['LanguagesText']))

class ImagePacketPacket(object):
    ''' a template for a ImagePacket packet '''

    def __init__(self):
        self.name = 'ImagePacket'

        self.ImageID = {}    # New ImageID block
        self.ImageID['ID'] = None    # MVT_LLUUID
        self.ImageID['Packet'] = None    # MVT_U16

        self.ImageData = {}    # New ImageData block
        self.ImageData['Data'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ImagePacket', Block('ImageID', ID = self.ImageID['ID'], Packet = self.ImageID['Packet']), Block('ImageData', Data = self.ImageData['Data']))

class ParcelInfoRequestPacket(object):
    ''' a template for a ParcelInfoRequest packet '''

    def __init__(self):
        self.name = 'ParcelInfoRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['ParcelID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelInfoRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', ParcelID = self.Data['ParcelID']))

class GrantGodlikePowersPacket(object):
    ''' a template for a GrantGodlikePowers packet '''

    def __init__(self):
        self.name = 'GrantGodlikePowers'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GrantData = {}    # New GrantData block
        self.GrantData['GodLevel'] = None    # MVT_U8
        self.GrantData['Token'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GrantGodlikePowers', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GrantData', GodLevel = self.GrantData['GodLevel'], Token = self.GrantData['Token']))

class ViewerFrozenMessagePacket(object):
    ''' a template for a ViewerFrozenMessage packet '''

    def __init__(self):
        self.name = 'ViewerFrozenMessage'

        self.FrozenData = {}    # New FrozenData block
        self.FrozenData['Data'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ViewerFrozenMessage', Block('FrozenData', Data = self.FrozenData['Data']))

class RegionPresenceResponsePacket(object):
    ''' a template for a RegionPresenceResponse packet '''

    def __init__(self):
        self.name = 'RegionPresenceResponse'

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionID'] = None    # MVT_LLUUID
        self.RegionData['RegionHandle'] = None    # MVT_U64
        self.RegionData['InternalRegionIP'] = None    # MVT_IP_ADDR
        self.RegionData['ExternalRegionIP'] = None    # MVT_IP_ADDR
        self.RegionData['RegionPort'] = None    # MVT_IP_PORT
        self.RegionData['ValidUntil'] = None    # MVT_F64
        self.RegionData['Message'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RegionPresenceResponse', Block('RegionData', RegionID = self.RegionData['RegionID'], RegionHandle = self.RegionData['RegionHandle'], InternalRegionIP = self.RegionData['InternalRegionIP'], ExternalRegionIP = self.RegionData['ExternalRegionIP'], RegionPort = self.RegionData['RegionPort'], ValidUntil = self.RegionData['ValidUntil'], Message = self.RegionData['Message']))

class OpenCircuitPacket(object):
    ''' a template for a OpenCircuit packet '''

    def __init__(self):
        self.name = 'OpenCircuit'

        self.CircuitInfo = {}    # New CircuitInfo block
        self.CircuitInfo['IP'] = None    # MVT_IP_ADDR
        self.CircuitInfo['Port'] = None    # MVT_IP_PORT

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('OpenCircuit', Block('CircuitInfo', IP = self.CircuitInfo['IP'], Port = self.CircuitInfo['Port']))

class GroupRoleDataRequestPacket(object):
    ''' a template for a GroupRoleDataRequest packet '''

    def __init__(self):
        self.name = 'GroupRoleDataRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['RequestID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupRoleDataRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', GroupID = self.GroupData['GroupID'], RequestID = self.GroupData['RequestID']))

class AgentMovementCompletePacket(object):
    ''' a template for a AgentMovementComplete packet '''

    def __init__(self):
        self.name = 'AgentMovementComplete'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['Position'] = None    # MVT_LLVector3
        self.Data['LookAt'] = None    # MVT_LLVector3
        self.Data['RegionHandle'] = None    # MVT_U64
        self.Data['Timestamp'] = None    # MVT_U32

        self.SimData = {}    # New SimData block
        self.SimData['ChannelVersion'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentMovementComplete', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', Position = self.Data['Position'], LookAt = self.Data['LookAt'], RegionHandle = self.Data['RegionHandle'], Timestamp = self.Data['Timestamp']), Block('SimData', ChannelVersion = self.SimData['ChannelVersion']))

class InviteGroupRequestPacket(object):
    ''' a template for a InviteGroupRequest packet '''

    def __init__(self):
        self.name = 'InviteGroupRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID

        self.InviteData = {}    # New InviteData block
        self.InviteData['InviteeID'] = None    # MVT_LLUUID
        self.InviteData['RoleID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('InviteGroupRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', GroupID = self.GroupData['GroupID']), Block('InviteData', InviteeID = self.InviteData['InviteeID'], RoleID = self.InviteData['RoleID']))

class ViewerStartAuctionPacket(object):
    ''' a template for a ViewerStartAuction packet '''

    def __init__(self):
        self.name = 'ViewerStartAuction'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['LocalID'] = None    # MVT_S32
        self.ParcelData['SnapshotID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ViewerStartAuction', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', LocalID = self.ParcelData['LocalID'], SnapshotID = self.ParcelData['SnapshotID']))

class ObjectNamePacket(object):
    ''' a template for a ObjectName packet '''

    def __init__(self):
        self.name = 'ObjectName'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['LocalID'] = None    # MVT_U32
        self.ObjectData['Name'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectName', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', LocalID = self.ObjectData['LocalID'], Name = self.ObjectData['Name']))

class CrossedRegionPacket(object):
    ''' a template for a CrossedRegion packet '''

    def __init__(self):
        self.name = 'CrossedRegion'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.RegionData = {}    # New RegionData block
        self.RegionData['SimIP'] = None    # MVT_IP_ADDR
        self.RegionData['SimPort'] = None    # MVT_IP_PORT
        self.RegionData['RegionHandle'] = None    # MVT_U64
        self.RegionData['SeedCapability'] = None    # MVT_VARIABLE

        self.Info = {}    # New Info block
        self.Info['Position'] = None    # MVT_LLVector3
        self.Info['LookAt'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CrossedRegion', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('RegionData', SimIP = self.RegionData['SimIP'], SimPort = self.RegionData['SimPort'], RegionHandle = self.RegionData['RegionHandle'], SeedCapability = self.RegionData['SeedCapability']), Block('Info', Position = self.Info['Position'], LookAt = self.Info['LookAt']))

class SetCPURatioPacket(object):
    ''' a template for a SetCPURatio packet '''

    def __init__(self):
        self.name = 'SetCPURatio'

        self.Data = {}    # New Data block
        self.Data['Ratio'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SetCPURatio', Block('Data', Ratio = self.Data['Ratio']))

class ParcelBuyPassPacket(object):
    ''' a template for a ParcelBuyPass packet '''

    def __init__(self):
        self.name = 'ParcelBuyPass'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['LocalID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelBuyPass', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', LocalID = self.ParcelData['LocalID']))

class MapItemRequestPacket(object):
    ''' a template for a MapItemRequest packet '''

    def __init__(self):
        self.name = 'MapItemRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['Flags'] = None    # MVT_U32
        self.AgentData['EstateID'] = None    # MVT_U32
        self.AgentData['Godlike'] = None    # MVT_BOOL

        self.RequestData = {}    # New RequestData block
        self.RequestData['ItemType'] = None    # MVT_U32
        self.RequestData['RegionHandle'] = None    # MVT_U64

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MapItemRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], Flags = self.AgentData['Flags'], EstateID = self.AgentData['EstateID'], Godlike = self.AgentData['Godlike']), Block('RequestData', ItemType = self.RequestData['ItemType'], RegionHandle = self.RequestData['RegionHandle']))

class AgentQuitCopyPacket(object):
    ''' a template for a AgentQuitCopy packet '''

    def __init__(self):
        self.name = 'AgentQuitCopy'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.FuseBlock = {}    # New FuseBlock block
        self.FuseBlock['ViewerCircuitCode'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentQuitCopy', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('FuseBlock', ViewerCircuitCode = self.FuseBlock['ViewerCircuitCode']))

class RequestTaskInventoryPacket(object):
    ''' a template for a RequestTaskInventory packet '''

    def __init__(self):
        self.name = 'RequestTaskInventory'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['LocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RequestTaskInventory', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('InventoryData', LocalID = self.InventoryData['LocalID']))

class FreezeUserPacket(object):
    ''' a template for a FreezeUser packet '''

    def __init__(self):
        self.name = 'FreezeUser'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['TargetID'] = None    # MVT_LLUUID
        self.Data['Flags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('FreezeUser', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', TargetID = self.Data['TargetID'], Flags = self.Data['Flags']))

class StartPingCheckPacket(object):
    ''' a template for a StartPingCheck packet '''

    def __init__(self):
        self.name = 'StartPingCheck'

        self.PingID = {}    # New PingID block
        self.PingID['PingID'] = None    # MVT_U8
        self.PingID['OldestUnacked'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('StartPingCheck', Block('PingID', PingID = self.PingID['PingID'], OldestUnacked = self.PingID['OldestUnacked']))

class GroupDataUpdatePacket(object):
    ''' a template for a GroupDataUpdate packet '''

    def __init__(self):
        self.name = 'GroupDataUpdate'

        self.AgentGroupData = {}    # New AgentGroupData block
        self.AgentGroupData['AgentID'] = None    # MVT_LLUUID
        self.AgentGroupData['GroupID'] = None    # MVT_LLUUID
        self.AgentGroupData['AgentPowers'] = None    # MVT_U64
        self.AgentGroupData['GroupTitle'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupDataUpdate', Block('AgentGroupData', AgentID = self.AgentGroupData['AgentID'], GroupID = self.AgentGroupData['GroupID'], AgentPowers = self.AgentGroupData['AgentPowers'], GroupTitle = self.AgentGroupData['GroupTitle']))

class TeleportLocationRequestPacket(object):
    ''' a template for a TeleportLocationRequest packet '''

    def __init__(self):
        self.name = 'TeleportLocationRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Info = {}    # New Info block
        self.Info['RegionHandle'] = None    # MVT_U64
        self.Info['Position'] = None    # MVT_LLVector3
        self.Info['LookAt'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TeleportLocationRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Info', RegionHandle = self.Info['RegionHandle'], Position = self.Info['Position'], LookAt = self.Info['LookAt']))

class UpdateCreateInventoryItemPacket(object):
    ''' a template for a UpdateCreateInventoryItem packet '''

    def __init__(self):
        self.name = 'UpdateCreateInventoryItem'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SimApproved'] = None    # MVT_BOOL
        self.AgentData['TransactionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID
        self.InventoryData['FolderID'] = None    # MVT_LLUUID
        self.InventoryData['CallbackID'] = None    # MVT_U32
        self.InventoryData['CreatorID'] = None    # MVT_LLUUID
        self.InventoryData['OwnerID'] = None    # MVT_LLUUID
        self.InventoryData['GroupID'] = None    # MVT_LLUUID
        self.InventoryData['BaseMask'] = None    # MVT_U32
        self.InventoryData['OwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupMask'] = None    # MVT_U32
        self.InventoryData['EveryoneMask'] = None    # MVT_U32
        self.InventoryData['NextOwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupOwned'] = None    # MVT_BOOL
        self.InventoryData['AssetID'] = None    # MVT_LLUUID
        self.InventoryData['Type'] = None    # MVT_S8
        self.InventoryData['InvType'] = None    # MVT_S8
        self.InventoryData['Flags'] = None    # MVT_U32
        self.InventoryData['SaleType'] = None    # MVT_U8
        self.InventoryData['SalePrice'] = None    # MVT_S32
        self.InventoryData['Name'] = None    # MVT_VARIABLE
        self.InventoryData['Description'] = None    # MVT_VARIABLE
        self.InventoryData['CreationDate'] = None    # MVT_S32
        self.InventoryData['CRC'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UpdateCreateInventoryItem', Block('AgentData', AgentID = self.AgentData['AgentID'], SimApproved = self.AgentData['SimApproved'], TransactionID = self.AgentData['TransactionID']), Block('InventoryData', ItemID = self.InventoryData['ItemID'], FolderID = self.InventoryData['FolderID'], CallbackID = self.InventoryData['CallbackID'], CreatorID = self.InventoryData['CreatorID'], OwnerID = self.InventoryData['OwnerID'], GroupID = self.InventoryData['GroupID'], BaseMask = self.InventoryData['BaseMask'], OwnerMask = self.InventoryData['OwnerMask'], GroupMask = self.InventoryData['GroupMask'], EveryoneMask = self.InventoryData['EveryoneMask'], NextOwnerMask = self.InventoryData['NextOwnerMask'], GroupOwned = self.InventoryData['GroupOwned'], AssetID = self.InventoryData['AssetID'], Type = self.InventoryData['Type'], InvType = self.InventoryData['InvType'], Flags = self.InventoryData['Flags'], SaleType = self.InventoryData['SaleType'], SalePrice = self.InventoryData['SalePrice'], Name = self.InventoryData['Name'], Description = self.InventoryData['Description'], CreationDate = self.InventoryData['CreationDate'], CRC = self.InventoryData['CRC']))

class NearestLandingRegionUpdatedPacket(object):
    ''' a template for a NearestLandingRegionUpdated packet '''

    def __init__(self):
        self.name = 'NearestLandingRegionUpdated'

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionHandle'] = None    # MVT_U64

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('NearestLandingRegionUpdated', Block('RegionData', RegionHandle = self.RegionData['RegionHandle']))

class EconomyDataPacket(object):
    ''' a template for a EconomyData packet '''

    def __init__(self):
        self.name = 'EconomyData'

        self.Info = {}    # New Info block
        self.Info['ObjectCapacity'] = None    # MVT_S32
        self.Info['ObjectCount'] = None    # MVT_S32
        self.Info['PriceEnergyUnit'] = None    # MVT_S32
        self.Info['PriceObjectClaim'] = None    # MVT_S32
        self.Info['PricePublicObjectDecay'] = None    # MVT_S32
        self.Info['PricePublicObjectDelete'] = None    # MVT_S32
        self.Info['PriceParcelClaim'] = None    # MVT_S32
        self.Info['PriceParcelClaimFactor'] = None    # MVT_F32
        self.Info['PriceUpload'] = None    # MVT_S32
        self.Info['PriceRentLight'] = None    # MVT_S32
        self.Info['TeleportMinPrice'] = None    # MVT_S32
        self.Info['TeleportPriceExponent'] = None    # MVT_F32
        self.Info['EnergyEfficiency'] = None    # MVT_F32
        self.Info['PriceObjectRent'] = None    # MVT_F32
        self.Info['PriceObjectScaleFactor'] = None    # MVT_F32
        self.Info['PriceParcelRent'] = None    # MVT_S32
        self.Info['PriceGroupCreate'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EconomyData', Block('Info', ObjectCapacity = self.Info['ObjectCapacity'], ObjectCount = self.Info['ObjectCount'], PriceEnergyUnit = self.Info['PriceEnergyUnit'], PriceObjectClaim = self.Info['PriceObjectClaim'], PricePublicObjectDecay = self.Info['PricePublicObjectDecay'], PricePublicObjectDelete = self.Info['PricePublicObjectDelete'], PriceParcelClaim = self.Info['PriceParcelClaim'], PriceParcelClaimFactor = self.Info['PriceParcelClaimFactor'], PriceUpload = self.Info['PriceUpload'], PriceRentLight = self.Info['PriceRentLight'], TeleportMinPrice = self.Info['TeleportMinPrice'], TeleportPriceExponent = self.Info['TeleportPriceExponent'], EnergyEfficiency = self.Info['EnergyEfficiency'], PriceObjectRent = self.Info['PriceObjectRent'], PriceObjectScaleFactor = self.Info['PriceObjectScaleFactor'], PriceParcelRent = self.Info['PriceParcelRent'], PriceGroupCreate = self.Info['PriceGroupCreate']))

class LiveHelpGroupReplyPacket(object):
    ''' a template for a LiveHelpGroupReply packet '''

    def __init__(self):
        self.name = 'LiveHelpGroupReply'

        self.ReplyData = {}    # New ReplyData block
        self.ReplyData['RequestID'] = None    # MVT_LLUUID
        self.ReplyData['GroupID'] = None    # MVT_LLUUID
        self.ReplyData['Selection'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LiveHelpGroupReply', Block('ReplyData', RequestID = self.ReplyData['RequestID'], GroupID = self.ReplyData['GroupID'], Selection = self.ReplyData['Selection']))

class UseCircuitCodePacket(object):
    ''' a template for a UseCircuitCode packet '''

    def __init__(self):
        self.name = 'UseCircuitCode'

        self.CircuitCode = {}    # New CircuitCode block
        self.CircuitCode['Code'] = None    # MVT_U32
        self.CircuitCode['SessionID'] = None    # MVT_LLUUID
        self.CircuitCode['ID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UseCircuitCode', Block('CircuitCode', Code = self.CircuitCode['Code'], SessionID = self.CircuitCode['SessionID'], ID = self.CircuitCode['ID']))

class GroupAccountTransactionsReplyPacket(object):
    ''' a template for a GroupAccountTransactionsReply packet '''

    def __init__(self):
        self.name = 'GroupAccountTransactionsReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.MoneyData = {}    # New MoneyData block
        self.MoneyData['RequestID'] = None    # MVT_LLUUID
        self.MoneyData['IntervalDays'] = None    # MVT_S32
        self.MoneyData['CurrentInterval'] = None    # MVT_S32
        self.MoneyData['StartDate'] = None    # MVT_VARIABLE

        self.HistoryData = {}    # New HistoryData block
        self.HistoryData['Time'] = None    # MVT_VARIABLE
        self.HistoryData['User'] = None    # MVT_VARIABLE
        self.HistoryData['Type'] = None    # MVT_S32
        self.HistoryData['Item'] = None    # MVT_VARIABLE
        self.HistoryData['Amount'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupAccountTransactionsReply', Block('AgentData', AgentID = self.AgentData['AgentID'], GroupID = self.AgentData['GroupID']), Block('MoneyData', RequestID = self.MoneyData['RequestID'], IntervalDays = self.MoneyData['IntervalDays'], CurrentInterval = self.MoneyData['CurrentInterval'], StartDate = self.MoneyData['StartDate']), Block('HistoryData', Time = self.HistoryData['Time'], User = self.HistoryData['User'], Type = self.HistoryData['Type'], Item = self.HistoryData['Item'], Amount = self.HistoryData['Amount']))

class UUIDGroupNameRequestPacket(object):
    ''' a template for a UUIDGroupNameRequest packet '''

    def __init__(self):
        self.name = 'UUIDGroupNameRequest'

        self.UUIDNameBlock = {}    # New UUIDNameBlock block
        self.UUIDNameBlock['ID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UUIDGroupNameRequest', Block('UUIDNameBlock', ID = self.UUIDNameBlock['ID']))

class ObjectDelinkPacket(object):
    ''' a template for a ObjectDelink packet '''

    def __init__(self):
        self.name = 'ObjectDelink'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectDelink', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class SimStatusPacket(object):
    ''' a template for a SimStatus packet '''

    def __init__(self):
        self.name = 'SimStatus'

        self.SimStatus = {}    # New SimStatus block
        self.SimStatus['CanAcceptAgents'] = None    # MVT_BOOL
        self.SimStatus['CanAcceptTasks'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SimStatus', Block('SimStatus', CanAcceptAgents = self.SimStatus['CanAcceptAgents'], CanAcceptTasks = self.SimStatus['CanAcceptTasks']))

class GrantUserRightsPacket(object):
    ''' a template for a GrantUserRights packet '''

    def __init__(self):
        self.name = 'GrantUserRights'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Rights = {}    # New Rights block
        self.Rights['AgentRelated'] = None    # MVT_LLUUID
        self.Rights['RelatedRights'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GrantUserRights', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Rights', AgentRelated = self.Rights['AgentRelated'], RelatedRights = self.Rights['RelatedRights']))

class ParcelAccessListRequestPacket(object):
    ''' a template for a ParcelAccessListRequest packet '''

    def __init__(self):
        self.name = 'ParcelAccessListRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['SequenceID'] = None    # MVT_S32
        self.Data['Flags'] = None    # MVT_U32
        self.Data['LocalID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelAccessListRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', SequenceID = self.Data['SequenceID'], Flags = self.Data['Flags'], LocalID = self.Data['LocalID']))

class ParcelMediaCommandMessagePacket(object):
    ''' a template for a ParcelMediaCommandMessage packet '''

    def __init__(self):
        self.name = 'ParcelMediaCommandMessage'

        self.CommandBlock = {}    # New CommandBlock block
        self.CommandBlock['Flags'] = None    # MVT_U32
        self.CommandBlock['Command'] = None    # MVT_U32
        self.CommandBlock['Time'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelMediaCommandMessage', Block('CommandBlock', Flags = self.CommandBlock['Flags'], Command = self.CommandBlock['Command'], Time = self.CommandBlock['Time']))

class ObjectFlagUpdatePacket(object):
    ''' a template for a ObjectFlagUpdate packet '''

    def __init__(self):
        self.name = 'ObjectFlagUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['ObjectLocalID'] = None    # MVT_U32
        self.AgentData['UsePhysics'] = None    # MVT_BOOL
        self.AgentData['IsTemporary'] = None    # MVT_BOOL
        self.AgentData['IsPhantom'] = None    # MVT_BOOL
        self.AgentData['CastsShadows'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectFlagUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], ObjectLocalID = self.AgentData['ObjectLocalID'], UsePhysics = self.AgentData['UsePhysics'], IsTemporary = self.AgentData['IsTemporary'], IsPhantom = self.AgentData['IsPhantom'], CastsShadows = self.AgentData['CastsShadows']))

class DeclineFriendshipPacket(object):
    ''' a template for a DeclineFriendship packet '''

    def __init__(self):
        self.name = 'DeclineFriendship'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.TransactionBlock = {}    # New TransactionBlock block
        self.TransactionBlock['TransactionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DeclineFriendship', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('TransactionBlock', TransactionID = self.TransactionBlock['TransactionID']))

class AvatarNotesUpdatePacket(object):
    ''' a template for a AvatarNotesUpdate packet '''

    def __init__(self):
        self.name = 'AvatarNotesUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['TargetID'] = None    # MVT_LLUUID
        self.Data['Notes'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarNotesUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', TargetID = self.Data['TargetID'], Notes = self.Data['Notes']))

class DetachAttachmentIntoInvPacket(object):
    ''' a template for a DetachAttachmentIntoInv packet '''

    def __init__(self):
        self.name = 'DetachAttachmentIntoInv'

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['AgentID'] = None    # MVT_LLUUID
        self.ObjectData['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DetachAttachmentIntoInv', Block('ObjectData', AgentID = self.ObjectData['AgentID'], ItemID = self.ObjectData['ItemID']))

class ParcelObjectOwnersRequestPacket(object):
    ''' a template for a ParcelObjectOwnersRequest packet '''

    def __init__(self):
        self.name = 'ParcelObjectOwnersRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['LocalID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelObjectOwnersRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', LocalID = self.ParcelData['LocalID']))

class RemoveInventoryFolderPacket(object):
    ''' a template for a RemoveInventoryFolder packet '''

    def __init__(self):
        self.name = 'RemoveInventoryFolder'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.FolderData = {}    # New FolderData block
        self.FolderData['FolderID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RemoveInventoryFolder', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('FolderData', FolderID = self.FolderData['FolderID']))

class TransferAbortPacket(object):
    ''' a template for a TransferAbort packet '''

    def __init__(self):
        self.name = 'TransferAbort'

        self.TransferInfo = {}    # New TransferInfo block
        self.TransferInfo['TransferID'] = None    # MVT_LLUUID
        self.TransferInfo['ChannelType'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TransferAbort', Block('TransferInfo', TransferID = self.TransferInfo['TransferID'], ChannelType = self.TransferInfo['ChannelType']))

class DirPlacesQueryBackendPacket(object):
    ''' a template for a DirPlacesQueryBackend packet '''

    def __init__(self):
        self.name = 'DirPlacesQueryBackend'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['QueryText'] = None    # MVT_VARIABLE
        self.QueryData['QueryFlags'] = None    # MVT_U32
        self.QueryData['Category'] = None    # MVT_S8
        self.QueryData['SimName'] = None    # MVT_VARIABLE
        self.QueryData['EstateID'] = None    # MVT_U32
        self.QueryData['Godlike'] = None    # MVT_BOOL
        self.QueryData['QueryStart'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirPlacesQueryBackend', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID'], QueryText = self.QueryData['QueryText'], QueryFlags = self.QueryData['QueryFlags'], Category = self.QueryData['Category'], SimName = self.QueryData['SimName'], EstateID = self.QueryData['EstateID'], Godlike = self.QueryData['Godlike'], QueryStart = self.QueryData['QueryStart']))

class UserReportPacket(object):
    ''' a template for a UserReport packet '''

    def __init__(self):
        self.name = 'UserReport'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ReportData = {}    # New ReportData block
        self.ReportData['ReportType'] = None    # MVT_U8
        self.ReportData['Category'] = None    # MVT_U8
        self.ReportData['Position'] = None    # MVT_LLVector3
        self.ReportData['CheckFlags'] = None    # MVT_U8
        self.ReportData['ScreenshotID'] = None    # MVT_LLUUID
        self.ReportData['ObjectID'] = None    # MVT_LLUUID
        self.ReportData['AbuserID'] = None    # MVT_LLUUID
        self.ReportData['AbuseRegionName'] = None    # MVT_VARIABLE
        self.ReportData['AbuseRegionID'] = None    # MVT_LLUUID
        self.ReportData['Summary'] = None    # MVT_VARIABLE
        self.ReportData['Details'] = None    # MVT_VARIABLE
        self.ReportData['VersionString'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UserReport', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ReportData', ReportType = self.ReportData['ReportType'], Category = self.ReportData['Category'], Position = self.ReportData['Position'], CheckFlags = self.ReportData['CheckFlags'], ScreenshotID = self.ReportData['ScreenshotID'], ObjectID = self.ReportData['ObjectID'], AbuserID = self.ReportData['AbuserID'], AbuseRegionName = self.ReportData['AbuseRegionName'], AbuseRegionID = self.ReportData['AbuseRegionID'], Summary = self.ReportData['Summary'], Details = self.ReportData['Details'], VersionString = self.ReportData['VersionString']))

class SimulatorLoadPacket(object):
    ''' a template for a SimulatorLoad packet '''

    def __init__(self):
        self.name = 'SimulatorLoad'

        self.SimulatorLoad = {}    # New SimulatorLoad block
        self.SimulatorLoad['TimeDilation'] = None    # MVT_F32
        self.SimulatorLoad['AgentCount'] = None    # MVT_S32
        self.SimulatorLoad['CanAcceptAgents'] = None    # MVT_BOOL

        self.AgentList = {}    # New AgentList block
        self.AgentList['CircuitCode'] = None    # MVT_U32
        self.AgentList['X'] = None    # MVT_U8
        self.AgentList['Y'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SimulatorLoad', Block('SimulatorLoad', TimeDilation = self.SimulatorLoad['TimeDilation'], AgentCount = self.SimulatorLoad['AgentCount'], CanAcceptAgents = self.SimulatorLoad['CanAcceptAgents']), Block('AgentList', CircuitCode = self.AgentList['CircuitCode'], X = self.AgentList['X'], Y = self.AgentList['Y']))

class GroupMembersReplyPacket(object):
    ''' a template for a GroupMembersReply packet '''

    def __init__(self):
        self.name = 'GroupMembersReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['RequestID'] = None    # MVT_LLUUID
        self.GroupData['MemberCount'] = None    # MVT_S32

        self.MemberData = {}    # New MemberData block
        self.MemberData['AgentID'] = None    # MVT_LLUUID
        self.MemberData['Contribution'] = None    # MVT_S32
        self.MemberData['OnlineStatus'] = None    # MVT_VARIABLE
        self.MemberData['AgentPowers'] = None    # MVT_U64
        self.MemberData['Title'] = None    # MVT_VARIABLE
        self.MemberData['IsOwner'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupMembersReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('GroupData', GroupID = self.GroupData['GroupID'], RequestID = self.GroupData['RequestID'], MemberCount = self.GroupData['MemberCount']), Block('MemberData', AgentID = self.MemberData['AgentID'], Contribution = self.MemberData['Contribution'], OnlineStatus = self.MemberData['OnlineStatus'], AgentPowers = self.MemberData['AgentPowers'], Title = self.MemberData['Title'], IsOwner = self.MemberData['IsOwner']))

class ScriptResetPacket(object):
    ''' a template for a ScriptReset packet '''

    def __init__(self):
        self.name = 'ScriptReset'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Script = {}    # New Script block
        self.Script['ObjectID'] = None    # MVT_LLUUID
        self.Script['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptReset', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Script', ObjectID = self.Script['ObjectID'], ItemID = self.Script['ItemID']))

class VelocityInterpolateOnPacket(object):
    ''' a template for a VelocityInterpolateOn packet '''

    def __init__(self):
        self.name = 'VelocityInterpolateOn'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('VelocityInterpolateOn', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class NameValuePairPacket(object):
    ''' a template for a NameValuePair packet '''

    def __init__(self):
        self.name = 'NameValuePair'

        self.TaskData = {}    # New TaskData block
        self.TaskData['ID'] = None    # MVT_LLUUID

        self.NameValueData = {}    # New NameValueData block
        self.NameValueData['NVPair'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('NameValuePair', Block('TaskData', ID = self.TaskData['ID']), Block('NameValueData', NVPair = self.NameValueData['NVPair']))

class ParcelReclaimPacket(object):
    ''' a template for a ParcelReclaim packet '''

    def __init__(self):
        self.name = 'ParcelReclaim'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['LocalID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelReclaim', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', LocalID = self.Data['LocalID']))

class BuyObjectInventoryPacket(object):
    ''' a template for a BuyObjectInventory packet '''

    def __init__(self):
        self.name = 'BuyObjectInventory'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['ObjectID'] = None    # MVT_LLUUID
        self.Data['ItemID'] = None    # MVT_LLUUID
        self.Data['FolderID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('BuyObjectInventory', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', ObjectID = self.Data['ObjectID'], ItemID = self.Data['ItemID'], FolderID = self.Data['FolderID']))

class EventLocationRequestPacket(object):
    ''' a template for a EventLocationRequest packet '''

    def __init__(self):
        self.name = 'EventLocationRequest'

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID

        self.EventData = {}    # New EventData block
        self.EventData['EventID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EventLocationRequest', Block('QueryData', QueryID = self.QueryData['QueryID']), Block('EventData', EventID = self.EventData['EventID']))

class PickDeletePacket(object):
    ''' a template for a PickDelete packet '''

    def __init__(self):
        self.name = 'PickDelete'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['PickID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('PickDelete', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', PickID = self.Data['PickID']))

class MapLayerReplyPacket(object):
    ''' a template for a MapLayerReply packet '''

    def __init__(self):
        self.name = 'MapLayerReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['Flags'] = None    # MVT_U32

        self.LayerData = {}    # New LayerData block
        self.LayerData['Left'] = None    # MVT_U32
        self.LayerData['Right'] = None    # MVT_U32
        self.LayerData['Top'] = None    # MVT_U32
        self.LayerData['Bottom'] = None    # MVT_U32
        self.LayerData['ImageID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MapLayerReply', Block('AgentData', AgentID = self.AgentData['AgentID'], Flags = self.AgentData['Flags']), Block('LayerData', Left = self.LayerData['Left'], Right = self.LayerData['Right'], Top = self.LayerData['Top'], Bottom = self.LayerData['Bottom'], ImageID = self.LayerData['ImageID']))

class TeleportLandmarkRequestPacket(object):
    ''' a template for a TeleportLandmarkRequest packet '''

    def __init__(self):
        self.name = 'TeleportLandmarkRequest'

        self.Info = {}    # New Info block
        self.Info['AgentID'] = None    # MVT_LLUUID
        self.Info['SessionID'] = None    # MVT_LLUUID
        self.Info['LandmarkID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TeleportLandmarkRequest', Block('Info', AgentID = self.Info['AgentID'], SessionID = self.Info['SessionID'], LandmarkID = self.Info['LandmarkID']))

class PurgeInventoryDescendentsPacket(object):
    ''' a template for a PurgeInventoryDescendents packet '''

    def __init__(self):
        self.name = 'PurgeInventoryDescendents'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['FolderID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('PurgeInventoryDescendents', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('InventoryData', FolderID = self.InventoryData['FolderID']))

class KickUserAckPacket(object):
    ''' a template for a KickUserAck packet '''

    def __init__(self):
        self.name = 'KickUserAck'

        self.UserInfo = {}    # New UserInfo block
        self.UserInfo['SessionID'] = None    # MVT_LLUUID
        self.UserInfo['Flags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('KickUserAck', Block('UserInfo', SessionID = self.UserInfo['SessionID'], Flags = self.UserInfo['Flags']))

class AvatarSitResponsePacket(object):
    ''' a template for a AvatarSitResponse packet '''

    def __init__(self):
        self.name = 'AvatarSitResponse'

        self.SitObject = {}    # New SitObject block
        self.SitObject['ID'] = None    # MVT_LLUUID

        self.SitTransform = {}    # New SitTransform block
        self.SitTransform['AutoPilot'] = None    # MVT_BOOL
        self.SitTransform['SitPosition'] = None    # MVT_LLVector3
        self.SitTransform['SitRotation'] = None    # MVT_LLQuaternion
        self.SitTransform['CameraEyeOffset'] = None    # MVT_LLVector3
        self.SitTransform['CameraAtOffset'] = None    # MVT_LLVector3
        self.SitTransform['ForceMouselook'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarSitResponse', Block('SitObject', ID = self.SitObject['ID']), Block('SitTransform', AutoPilot = self.SitTransform['AutoPilot'], SitPosition = self.SitTransform['SitPosition'], SitRotation = self.SitTransform['SitRotation'], CameraEyeOffset = self.SitTransform['CameraEyeOffset'], CameraAtOffset = self.SitTransform['CameraAtOffset'], ForceMouselook = self.SitTransform['ForceMouselook']))

class ClassifiedInfoRequestPacket(object):
    ''' a template for a ClassifiedInfoRequest packet '''

    def __init__(self):
        self.name = 'ClassifiedInfoRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['ClassifiedID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ClassifiedInfoRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', ClassifiedID = self.Data['ClassifiedID']))

class UpdateMuteListEntryPacket(object):
    ''' a template for a UpdateMuteListEntry packet '''

    def __init__(self):
        self.name = 'UpdateMuteListEntry'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.MuteData = {}    # New MuteData block
        self.MuteData['MuteID'] = None    # MVT_LLUUID
        self.MuteData['MuteName'] = None    # MVT_VARIABLE
        self.MuteData['MuteType'] = None    # MVT_S32
        self.MuteData['MuteFlags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UpdateMuteListEntry', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('MuteData', MuteID = self.MuteData['MuteID'], MuteName = self.MuteData['MuteName'], MuteType = self.MuteData['MuteType'], MuteFlags = self.MuteData['MuteFlags']))

class RegionInfoPacket(object):
    ''' a template for a RegionInfo packet '''

    def __init__(self):
        self.name = 'RegionInfo'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.RegionInfo = {}    # New RegionInfo block
        self.RegionInfo['SimName'] = None    # MVT_VARIABLE
        self.RegionInfo['EstateID'] = None    # MVT_U32
        self.RegionInfo['ParentEstateID'] = None    # MVT_U32
        self.RegionInfo['RegionFlags'] = None    # MVT_U32
        self.RegionInfo['SimAccess'] = None    # MVT_U8
        self.RegionInfo['MaxAgents'] = None    # MVT_U8
        self.RegionInfo['BillableFactor'] = None    # MVT_F32
        self.RegionInfo['ObjectBonusFactor'] = None    # MVT_F32
        self.RegionInfo['WaterHeight'] = None    # MVT_F32
        self.RegionInfo['TerrainRaiseLimit'] = None    # MVT_F32
        self.RegionInfo['TerrainLowerLimit'] = None    # MVT_F32
        self.RegionInfo['PricePerMeter'] = None    # MVT_S32
        self.RegionInfo['RedirectGridX'] = None    # MVT_S32
        self.RegionInfo['RedirectGridY'] = None    # MVT_S32
        self.RegionInfo['UseEstateSun'] = None    # MVT_BOOL
        self.RegionInfo['SunHour'] = None    # MVT_F32

        self.RegionInfo2 = {}    # New RegionInfo2 block
        self.RegionInfo2['ProductSKU'] = None    # MVT_VARIABLE
        self.RegionInfo2['ProductName'] = None    # MVT_VARIABLE
        self.RegionInfo2['MaxAgents32'] = None    # MVT_U32
        self.RegionInfo2['HardMaxAgents'] = None    # MVT_U32
        self.RegionInfo2['HardMaxObjects'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RegionInfo', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('RegionInfo', SimName = self.RegionInfo['SimName'], EstateID = self.RegionInfo['EstateID'], ParentEstateID = self.RegionInfo['ParentEstateID'], RegionFlags = self.RegionInfo['RegionFlags'], SimAccess = self.RegionInfo['SimAccess'], MaxAgents = self.RegionInfo['MaxAgents'], BillableFactor = self.RegionInfo['BillableFactor'], ObjectBonusFactor = self.RegionInfo['ObjectBonusFactor'], WaterHeight = self.RegionInfo['WaterHeight'], TerrainRaiseLimit = self.RegionInfo['TerrainRaiseLimit'], TerrainLowerLimit = self.RegionInfo['TerrainLowerLimit'], PricePerMeter = self.RegionInfo['PricePerMeter'], RedirectGridX = self.RegionInfo['RedirectGridX'], RedirectGridY = self.RegionInfo['RedirectGridY'], UseEstateSun = self.RegionInfo['UseEstateSun'], SunHour = self.RegionInfo['SunHour']), Block('RegionInfo2', ProductSKU = self.RegionInfo2['ProductSKU'], ProductName = self.RegionInfo2['ProductName'], MaxAgents32 = self.RegionInfo2['MaxAgents32'], HardMaxAgents = self.RegionInfo2['HardMaxAgents'], HardMaxObjects = self.RegionInfo2['HardMaxObjects']))

class UserReportInternalPacket(object):
    ''' a template for a UserReportInternal packet '''

    def __init__(self):
        self.name = 'UserReportInternal'

        self.ReportData = {}    # New ReportData block
        self.ReportData['ReportType'] = None    # MVT_U8
        self.ReportData['Category'] = None    # MVT_U8
        self.ReportData['ReporterID'] = None    # MVT_LLUUID
        self.ReportData['ViewerPosition'] = None    # MVT_LLVector3
        self.ReportData['AgentPosition'] = None    # MVT_LLVector3
        self.ReportData['ScreenshotID'] = None    # MVT_LLUUID
        self.ReportData['ObjectID'] = None    # MVT_LLUUID
        self.ReportData['OwnerID'] = None    # MVT_LLUUID
        self.ReportData['LastOwnerID'] = None    # MVT_LLUUID
        self.ReportData['CreatorID'] = None    # MVT_LLUUID
        self.ReportData['RegionID'] = None    # MVT_LLUUID
        self.ReportData['AbuserID'] = None    # MVT_LLUUID
        self.ReportData['AbuseRegionName'] = None    # MVT_VARIABLE
        self.ReportData['AbuseRegionID'] = None    # MVT_LLUUID
        self.ReportData['Summary'] = None    # MVT_VARIABLE
        self.ReportData['Details'] = None    # MVT_VARIABLE
        self.ReportData['VersionString'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UserReportInternal', Block('ReportData', ReportType = self.ReportData['ReportType'], Category = self.ReportData['Category'], ReporterID = self.ReportData['ReporterID'], ViewerPosition = self.ReportData['ViewerPosition'], AgentPosition = self.ReportData['AgentPosition'], ScreenshotID = self.ReportData['ScreenshotID'], ObjectID = self.ReportData['ObjectID'], OwnerID = self.ReportData['OwnerID'], LastOwnerID = self.ReportData['LastOwnerID'], CreatorID = self.ReportData['CreatorID'], RegionID = self.ReportData['RegionID'], AbuserID = self.ReportData['AbuserID'], AbuseRegionName = self.ReportData['AbuseRegionName'], AbuseRegionID = self.ReportData['AbuseRegionID'], Summary = self.ReportData['Summary'], Details = self.ReportData['Details'], VersionString = self.ReportData['VersionString']))

class GroupActiveProposalItemReplyPacket(object):
    ''' a template for a GroupActiveProposalItemReply packet '''

    def __init__(self):
        self.name = 'GroupActiveProposalItemReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.TransactionData = {}    # New TransactionData block
        self.TransactionData['TransactionID'] = None    # MVT_LLUUID
        self.TransactionData['TotalNumItems'] = None    # MVT_U32

        self.ProposalData = {}    # New ProposalData block
        self.ProposalData['VoteID'] = None    # MVT_LLUUID
        self.ProposalData['VoteInitiator'] = None    # MVT_LLUUID
        self.ProposalData['TerseDateID'] = None    # MVT_VARIABLE
        self.ProposalData['StartDateTime'] = None    # MVT_VARIABLE
        self.ProposalData['EndDateTime'] = None    # MVT_VARIABLE
        self.ProposalData['AlreadyVoted'] = None    # MVT_BOOL
        self.ProposalData['VoteCast'] = None    # MVT_VARIABLE
        self.ProposalData['Majority'] = None    # MVT_F32
        self.ProposalData['Quorum'] = None    # MVT_S32
        self.ProposalData['ProposalText'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupActiveProposalItemReply', Block('AgentData', AgentID = self.AgentData['AgentID'], GroupID = self.AgentData['GroupID']), Block('TransactionData', TransactionID = self.TransactionData['TransactionID'], TotalNumItems = self.TransactionData['TotalNumItems']), Block('ProposalData', VoteID = self.ProposalData['VoteID'], VoteInitiator = self.ProposalData['VoteInitiator'], TerseDateID = self.ProposalData['TerseDateID'], StartDateTime = self.ProposalData['StartDateTime'], EndDateTime = self.ProposalData['EndDateTime'], AlreadyVoted = self.ProposalData['AlreadyVoted'], VoteCast = self.ProposalData['VoteCast'], Majority = self.ProposalData['Majority'], Quorum = self.ProposalData['Quorum'], ProposalText = self.ProposalData['ProposalText']))

class RetrieveInstantMessagesPacket(object):
    ''' a template for a RetrieveInstantMessages packet '''

    def __init__(self):
        self.name = 'RetrieveInstantMessages'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RetrieveInstantMessages', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class ScriptDataReplyPacket(object):
    ''' a template for a ScriptDataReply packet '''

    def __init__(self):
        self.name = 'ScriptDataReply'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['Hash'] = None    # MVT_U64
        self.DataBlock['Reply'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptDataReply', Block('DataBlock', Hash = self.DataBlock['Hash'], Reply = self.DataBlock['Reply']))

class ParcelAccessListUpdatePacket(object):
    ''' a template for a ParcelAccessListUpdate packet '''

    def __init__(self):
        self.name = 'ParcelAccessListUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['Flags'] = None    # MVT_U32
        self.Data['LocalID'] = None    # MVT_S32
        self.Data['TransactionID'] = None    # MVT_LLUUID
        self.Data['SequenceID'] = None    # MVT_S32
        self.Data['Sections'] = None    # MVT_S32

        self.List = {}    # New List block
        self.List['ID'] = None    # MVT_LLUUID
        self.List['Time'] = None    # MVT_S32
        self.List['Flags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelAccessListUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', Flags = self.Data['Flags'], LocalID = self.Data['LocalID'], TransactionID = self.Data['TransactionID'], SequenceID = self.Data['SequenceID'], Sections = self.Data['Sections']), Block('List', ID = self.List['ID'], Time = self.List['Time'], Flags = self.List['Flags']))

class ObjectImagePacket(object):
    ''' a template for a ObjectImage packet '''

    def __init__(self):
        self.name = 'ObjectImage'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['MediaURL'] = None    # MVT_VARIABLE
        self.ObjectData['TextureEntry'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectImage', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], MediaURL = self.ObjectData['MediaURL'], TextureEntry = self.ObjectData['TextureEntry']))

class ActivateGesturesPacket(object):
    ''' a template for a ActivateGestures packet '''

    def __init__(self):
        self.name = 'ActivateGestures'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['Flags'] = None    # MVT_U32

        self.Data = {}    # New Data block
        self.Data['ItemID'] = None    # MVT_LLUUID
        self.Data['AssetID'] = None    # MVT_LLUUID
        self.Data['GestureFlags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ActivateGestures', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], Flags = self.AgentData['Flags']), Block('Data', ItemID = self.Data['ItemID'], AssetID = self.Data['AssetID'], GestureFlags = self.Data['GestureFlags']))

class ScriptTeleportRequestPacket(object):
    ''' a template for a ScriptTeleportRequest packet '''

    def __init__(self):
        self.name = 'ScriptTeleportRequest'

        self.Data = {}    # New Data block
        self.Data['ObjectName'] = None    # MVT_VARIABLE
        self.Data['SimName'] = None    # MVT_VARIABLE
        self.Data['SimPosition'] = None    # MVT_LLVector3
        self.Data['LookAt'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptTeleportRequest', Block('Data', ObjectName = self.Data['ObjectName'], SimName = self.Data['SimName'], SimPosition = self.Data['SimPosition'], LookAt = self.Data['LookAt']))

class RpcScriptRequestInboundPacket(object):
    ''' a template for a RpcScriptRequestInbound packet '''

    def __init__(self):
        self.name = 'RpcScriptRequestInbound'

        self.TargetBlock = {}    # New TargetBlock block
        self.TargetBlock['GridX'] = None    # MVT_U32
        self.TargetBlock['GridY'] = None    # MVT_U32

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['TaskID'] = None    # MVT_LLUUID
        self.DataBlock['ItemID'] = None    # MVT_LLUUID
        self.DataBlock['ChannelID'] = None    # MVT_LLUUID
        self.DataBlock['IntValue'] = None    # MVT_U32
        self.DataBlock['StringValue'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RpcScriptRequestInbound', Block('TargetBlock', GridX = self.TargetBlock['GridX'], GridY = self.TargetBlock['GridY']), Block('DataBlock', TaskID = self.DataBlock['TaskID'], ItemID = self.DataBlock['ItemID'], ChannelID = self.DataBlock['ChannelID'], IntValue = self.DataBlock['IntValue'], StringValue = self.DataBlock['StringValue']))

class TeleportFailedPacket(object):
    ''' a template for a TeleportFailed packet '''

    def __init__(self):
        self.name = 'TeleportFailed'

        self.Info = {}    # New Info block
        self.Info['AgentID'] = None    # MVT_LLUUID
        self.Info['Reason'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TeleportFailed', Block('Info', AgentID = self.Info['AgentID'], Reason = self.Info['Reason']))

class RezObjectFromNotecardPacket(object):
    ''' a template for a RezObjectFromNotecard packet '''

    def __init__(self):
        self.name = 'RezObjectFromNotecard'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.RezData = {}    # New RezData block
        self.RezData['FromTaskID'] = None    # MVT_LLUUID
        self.RezData['BypassRaycast'] = None    # MVT_U8
        self.RezData['RayStart'] = None    # MVT_LLVector3
        self.RezData['RayEnd'] = None    # MVT_LLVector3
        self.RezData['RayTargetID'] = None    # MVT_LLUUID
        self.RezData['RayEndIsIntersection'] = None    # MVT_BOOL
        self.RezData['RezSelected'] = None    # MVT_BOOL
        self.RezData['RemoveItem'] = None    # MVT_BOOL
        self.RezData['ItemFlags'] = None    # MVT_U32
        self.RezData['GroupMask'] = None    # MVT_U32
        self.RezData['EveryoneMask'] = None    # MVT_U32
        self.RezData['NextOwnerMask'] = None    # MVT_U32

        self.NotecardData = {}    # New NotecardData block
        self.NotecardData['NotecardItemID'] = None    # MVT_LLUUID
        self.NotecardData['ObjectID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RezObjectFromNotecard', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('RezData', FromTaskID = self.RezData['FromTaskID'], BypassRaycast = self.RezData['BypassRaycast'], RayStart = self.RezData['RayStart'], RayEnd = self.RezData['RayEnd'], RayTargetID = self.RezData['RayTargetID'], RayEndIsIntersection = self.RezData['RayEndIsIntersection'], RezSelected = self.RezData['RezSelected'], RemoveItem = self.RezData['RemoveItem'], ItemFlags = self.RezData['ItemFlags'], GroupMask = self.RezData['GroupMask'], EveryoneMask = self.RezData['EveryoneMask'], NextOwnerMask = self.RezData['NextOwnerMask']), Block('NotecardData', NotecardItemID = self.NotecardData['NotecardItemID'], ObjectID = self.NotecardData['ObjectID']), Block('InventoryData', ItemID = self.InventoryData['ItemID']))

class AvatarGroupsReplyPacket(object):
    ''' a template for a AvatarGroupsReply packet '''

    def __init__(self):
        self.name = 'AvatarGroupsReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['AvatarID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupPowers'] = None    # MVT_U64
        self.GroupData['AcceptNotices'] = None    # MVT_BOOL
        self.GroupData['GroupTitle'] = None    # MVT_VARIABLE
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['GroupName'] = None    # MVT_VARIABLE
        self.GroupData['GroupInsigniaID'] = None    # MVT_LLUUID

        self.NewGroupData = {}    # New NewGroupData block
        self.NewGroupData['ListInProfile'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarGroupsReply', Block('AgentData', AgentID = self.AgentData['AgentID'], AvatarID = self.AgentData['AvatarID']), Block('GroupData', GroupPowers = self.GroupData['GroupPowers'], AcceptNotices = self.GroupData['AcceptNotices'], GroupTitle = self.GroupData['GroupTitle'], GroupID = self.GroupData['GroupID'], GroupName = self.GroupData['GroupName'], GroupInsigniaID = self.GroupData['GroupInsigniaID']), Block('NewGroupData', ListInProfile = self.NewGroupData['ListInProfile']))

class ObjectUpdatePacket(object):
    ''' a template for a ObjectUpdate packet '''

    def __init__(self):
        self.name = 'ObjectUpdate'

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionHandle'] = None    # MVT_U64
        self.RegionData['TimeDilation'] = None    # MVT_U16

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ID'] = None    # MVT_U32
        self.ObjectData['State'] = None    # MVT_U8
        self.ObjectData['FullID'] = None    # MVT_LLUUID
        self.ObjectData['CRC'] = None    # MVT_U32
        self.ObjectData['PCode'] = None    # MVT_U8
        self.ObjectData['Material'] = None    # MVT_U8
        self.ObjectData['ClickAction'] = None    # MVT_U8
        self.ObjectData['Scale'] = None    # MVT_LLVector3
        self.ObjectData['ObjectData'] = None    # MVT_VARIABLE
        self.ObjectData['ParentID'] = None    # MVT_U32
        self.ObjectData['UpdateFlags'] = None    # MVT_U32
        self.ObjectData['PathCurve'] = None    # MVT_U8
        self.ObjectData['ProfileCurve'] = None    # MVT_U8
        self.ObjectData['PathBegin'] = None    # MVT_U16
        self.ObjectData['PathEnd'] = None    # MVT_U16
        self.ObjectData['PathScaleX'] = None    # MVT_U8
        self.ObjectData['PathScaleY'] = None    # MVT_U8
        self.ObjectData['PathShearX'] = None    # MVT_U8
        self.ObjectData['PathShearY'] = None    # MVT_U8
        self.ObjectData['PathTwist'] = None    # MVT_S8
        self.ObjectData['PathTwistBegin'] = None    # MVT_S8
        self.ObjectData['PathRadiusOffset'] = None    # MVT_S8
        self.ObjectData['PathTaperX'] = None    # MVT_S8
        self.ObjectData['PathTaperY'] = None    # MVT_S8
        self.ObjectData['PathRevolutions'] = None    # MVT_U8
        self.ObjectData['PathSkew'] = None    # MVT_S8
        self.ObjectData['ProfileBegin'] = None    # MVT_U16
        self.ObjectData['ProfileEnd'] = None    # MVT_U16
        self.ObjectData['ProfileHollow'] = None    # MVT_U16
        self.ObjectData['TextureEntry'] = None    # MVT_VARIABLE
        self.ObjectData['TextureAnim'] = None    # MVT_VARIABLE
        self.ObjectData['NameValue'] = None    # MVT_VARIABLE
        self.ObjectData['Data'] = None    # MVT_VARIABLE
        self.ObjectData['Text'] = None    # MVT_VARIABLE
        self.ObjectData['TextColor'] = None    # MVT_FIXED
        self.ObjectData['MediaURL'] = None    # MVT_VARIABLE
        self.ObjectData['PSBlock'] = None    # MVT_VARIABLE
        self.ObjectData['ExtraParams'] = None    # MVT_VARIABLE
        self.ObjectData['Sound'] = None    # MVT_LLUUID
        self.ObjectData['OwnerID'] = None    # MVT_LLUUID
        self.ObjectData['Gain'] = None    # MVT_F32
        self.ObjectData['Flags'] = None    # MVT_U8
        self.ObjectData['Radius'] = None    # MVT_F32
        self.ObjectData['JointType'] = None    # MVT_U8
        self.ObjectData['JointPivot'] = None    # MVT_LLVector3
        self.ObjectData['JointAxisOrAnchor'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectUpdate', Block('RegionData', RegionHandle = self.RegionData['RegionHandle'], TimeDilation = self.RegionData['TimeDilation']), Block('ObjectData', ID = self.ObjectData['ID'], State = self.ObjectData['State'], FullID = self.ObjectData['FullID'], CRC = self.ObjectData['CRC'], PCode = self.ObjectData['PCode'], Material = self.ObjectData['Material'], ClickAction = self.ObjectData['ClickAction'], Scale = self.ObjectData['Scale'], ObjectData = self.ObjectData['ObjectData'], ParentID = self.ObjectData['ParentID'], UpdateFlags = self.ObjectData['UpdateFlags'], PathCurve = self.ObjectData['PathCurve'], ProfileCurve = self.ObjectData['ProfileCurve'], PathBegin = self.ObjectData['PathBegin'], PathEnd = self.ObjectData['PathEnd'], PathScaleX = self.ObjectData['PathScaleX'], PathScaleY = self.ObjectData['PathScaleY'], PathShearX = self.ObjectData['PathShearX'], PathShearY = self.ObjectData['PathShearY'], PathTwist = self.ObjectData['PathTwist'], PathTwistBegin = self.ObjectData['PathTwistBegin'], PathRadiusOffset = self.ObjectData['PathRadiusOffset'], PathTaperX = self.ObjectData['PathTaperX'], PathTaperY = self.ObjectData['PathTaperY'], PathRevolutions = self.ObjectData['PathRevolutions'], PathSkew = self.ObjectData['PathSkew'], ProfileBegin = self.ObjectData['ProfileBegin'], ProfileEnd = self.ObjectData['ProfileEnd'], ProfileHollow = self.ObjectData['ProfileHollow'], TextureEntry = self.ObjectData['TextureEntry'], TextureAnim = self.ObjectData['TextureAnim'], NameValue = self.ObjectData['NameValue'], Data = self.ObjectData['Data'], Text = self.ObjectData['Text'], TextColor = self.ObjectData['TextColor'], MediaURL = self.ObjectData['MediaURL'], PSBlock = self.ObjectData['PSBlock'], ExtraParams = self.ObjectData['ExtraParams'], Sound = self.ObjectData['Sound'], OwnerID = self.ObjectData['OwnerID'], Gain = self.ObjectData['Gain'], Flags = self.ObjectData['Flags'], Radius = self.ObjectData['Radius'], JointType = self.ObjectData['JointType'], JointPivot = self.ObjectData['JointPivot'], JointAxisOrAnchor = self.ObjectData['JointAxisOrAnchor']))

class DirPopularQueryBackendPacket(object):
    ''' a template for a DirPopularQueryBackend packet '''

    def __init__(self):
        self.name = 'DirPopularQueryBackend'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['QueryFlags'] = None    # MVT_U32
        self.QueryData['EstateID'] = None    # MVT_U32
        self.QueryData['Godlike'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirPopularQueryBackend', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID'], QueryFlags = self.QueryData['QueryFlags'], EstateID = self.QueryData['EstateID'], Godlike = self.QueryData['Godlike']))

class FindAgentPacket(object):
    ''' a template for a FindAgent packet '''

    def __init__(self):
        self.name = 'FindAgent'

        self.AgentBlock = {}    # New AgentBlock block
        self.AgentBlock['Hunter'] = None    # MVT_LLUUID
        self.AgentBlock['Prey'] = None    # MVT_LLUUID
        self.AgentBlock['SpaceIP'] = None    # MVT_IP_ADDR

        self.LocationBlock = {}    # New LocationBlock block
        self.LocationBlock['GlobalX'] = None    # MVT_F64
        self.LocationBlock['GlobalY'] = None    # MVT_F64

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('FindAgent', Block('AgentBlock', Hunter = self.AgentBlock['Hunter'], Prey = self.AgentBlock['Prey'], SpaceIP = self.AgentBlock['SpaceIP']), Block('LocationBlock', GlobalX = self.LocationBlock['GlobalX'], GlobalY = self.LocationBlock['GlobalY']))

class EnableSimulatorPacket(object):
    ''' a template for a EnableSimulator packet '''

    def __init__(self):
        self.name = 'EnableSimulator'

        self.SimulatorInfo = {}    # New SimulatorInfo block
        self.SimulatorInfo['Handle'] = None    # MVT_U64
        self.SimulatorInfo['IP'] = None    # MVT_IP_ADDR
        self.SimulatorInfo['Port'] = None    # MVT_IP_PORT

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EnableSimulator', Block('SimulatorInfo', Handle = self.SimulatorInfo['Handle'], IP = self.SimulatorInfo['IP'], Port = self.SimulatorInfo['Port']))

class PlacesReplyPacket(object):
    ''' a template for a PlacesReply packet '''

    def __init__(self):
        self.name = 'PlacesReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['QueryID'] = None    # MVT_LLUUID

        self.TransactionData = {}    # New TransactionData block
        self.TransactionData['TransactionID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['OwnerID'] = None    # MVT_LLUUID
        self.QueryData['Name'] = None    # MVT_VARIABLE
        self.QueryData['Desc'] = None    # MVT_VARIABLE
        self.QueryData['ActualArea'] = None    # MVT_S32
        self.QueryData['BillableArea'] = None    # MVT_S32
        self.QueryData['Flags'] = None    # MVT_U8
        self.QueryData['GlobalX'] = None    # MVT_F32
        self.QueryData['GlobalY'] = None    # MVT_F32
        self.QueryData['GlobalZ'] = None    # MVT_F32
        self.QueryData['SimName'] = None    # MVT_VARIABLE
        self.QueryData['SnapshotID'] = None    # MVT_LLUUID
        self.QueryData['Dwell'] = None    # MVT_F32
        self.QueryData['Price'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('PlacesReply', Block('AgentData', AgentID = self.AgentData['AgentID'], QueryID = self.AgentData['QueryID']), Block('TransactionData', TransactionID = self.TransactionData['TransactionID']), Block('QueryData', OwnerID = self.QueryData['OwnerID'], Name = self.QueryData['Name'], Desc = self.QueryData['Desc'], ActualArea = self.QueryData['ActualArea'], BillableArea = self.QueryData['BillableArea'], Flags = self.QueryData['Flags'], GlobalX = self.QueryData['GlobalX'], GlobalY = self.QueryData['GlobalY'], GlobalZ = self.QueryData['GlobalZ'], SimName = self.QueryData['SimName'], SnapshotID = self.QueryData['SnapshotID'], Dwell = self.QueryData['Dwell'], Price = self.QueryData['Price']))

class SetGroupContributionPacket(object):
    ''' a template for a SetGroupContribution packet '''

    def __init__(self):
        self.name = 'SetGroupContribution'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['GroupID'] = None    # MVT_LLUUID
        self.Data['Contribution'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SetGroupContribution', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', GroupID = self.Data['GroupID'], Contribution = self.Data['Contribution']))

class ScriptSensorReplyPacket(object):
    ''' a template for a ScriptSensorReply packet '''

    def __init__(self):
        self.name = 'ScriptSensorReply'

        self.Requester = {}    # New Requester block
        self.Requester['SourceID'] = None    # MVT_LLUUID

        self.SensedData = {}    # New SensedData block
        self.SensedData['ObjectID'] = None    # MVT_LLUUID
        self.SensedData['OwnerID'] = None    # MVT_LLUUID
        self.SensedData['GroupID'] = None    # MVT_LLUUID
        self.SensedData['Position'] = None    # MVT_LLVector3
        self.SensedData['Velocity'] = None    # MVT_LLVector3
        self.SensedData['Rotation'] = None    # MVT_LLQuaternion
        self.SensedData['Name'] = None    # MVT_VARIABLE
        self.SensedData['Type'] = None    # MVT_S32
        self.SensedData['Range'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptSensorReply', Block('Requester', SourceID = self.Requester['SourceID']), Block('SensedData', ObjectID = self.SensedData['ObjectID'], OwnerID = self.SensedData['OwnerID'], GroupID = self.SensedData['GroupID'], Position = self.SensedData['Position'], Velocity = self.SensedData['Velocity'], Rotation = self.SensedData['Rotation'], Name = self.SensedData['Name'], Type = self.SensedData['Type'], Range = self.SensedData['Range']))

class LeaveGroupRequestPacket(object):
    ''' a template for a LeaveGroupRequest packet '''

    def __init__(self):
        self.name = 'LeaveGroupRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LeaveGroupRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', GroupID = self.GroupData['GroupID']))

class ParcelSalesPacket(object):
    ''' a template for a ParcelSales packet '''

    def __init__(self):
        self.name = 'ParcelSales'

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['ParcelID'] = None    # MVT_LLUUID
        self.ParcelData['BuyerID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelSales', Block('ParcelData', ParcelID = self.ParcelData['ParcelID'], BuyerID = self.ParcelData['BuyerID']))

class ObjectPermissionsPacket(object):
    ''' a template for a ObjectPermissions packet '''

    def __init__(self):
        self.name = 'ObjectPermissions'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.HeaderData = {}    # New HeaderData block
        self.HeaderData['Override'] = None    # MVT_BOOL

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['Field'] = None    # MVT_U8
        self.ObjectData['Set'] = None    # MVT_U8
        self.ObjectData['Mask'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectPermissions', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('HeaderData', Override = self.HeaderData['Override']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], Field = self.ObjectData['Field'], Set = self.ObjectData['Set'], Mask = self.ObjectData['Mask']))

class ObjectPropertiesPacket(object):
    ''' a template for a ObjectProperties packet '''

    def __init__(self):
        self.name = 'ObjectProperties'

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        self.ObjectData['CreatorID'] = None    # MVT_LLUUID
        self.ObjectData['OwnerID'] = None    # MVT_LLUUID
        self.ObjectData['GroupID'] = None    # MVT_LLUUID
        self.ObjectData['CreationDate'] = None    # MVT_U64
        self.ObjectData['BaseMask'] = None    # MVT_U32
        self.ObjectData['OwnerMask'] = None    # MVT_U32
        self.ObjectData['GroupMask'] = None    # MVT_U32
        self.ObjectData['EveryoneMask'] = None    # MVT_U32
        self.ObjectData['NextOwnerMask'] = None    # MVT_U32
        self.ObjectData['OwnershipCost'] = None    # MVT_S32
        self.ObjectData['SaleType'] = None    # MVT_U8
        self.ObjectData['SalePrice'] = None    # MVT_S32
        self.ObjectData['AggregatePerms'] = None    # MVT_U8
        self.ObjectData['AggregatePermTextures'] = None    # MVT_U8
        self.ObjectData['AggregatePermTexturesOwner'] = None    # MVT_U8
        self.ObjectData['Category'] = None    # MVT_U32
        self.ObjectData['InventorySerial'] = None    # MVT_S16
        self.ObjectData['ItemID'] = None    # MVT_LLUUID
        self.ObjectData['FolderID'] = None    # MVT_LLUUID
        self.ObjectData['FromTaskID'] = None    # MVT_LLUUID
        self.ObjectData['LastOwnerID'] = None    # MVT_LLUUID
        self.ObjectData['Name'] = None    # MVT_VARIABLE
        self.ObjectData['Description'] = None    # MVT_VARIABLE
        self.ObjectData['TouchName'] = None    # MVT_VARIABLE
        self.ObjectData['SitName'] = None    # MVT_VARIABLE
        self.ObjectData['TextureID'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectProperties', Block('ObjectData', ObjectID = self.ObjectData['ObjectID'], CreatorID = self.ObjectData['CreatorID'], OwnerID = self.ObjectData['OwnerID'], GroupID = self.ObjectData['GroupID'], CreationDate = self.ObjectData['CreationDate'], BaseMask = self.ObjectData['BaseMask'], OwnerMask = self.ObjectData['OwnerMask'], GroupMask = self.ObjectData['GroupMask'], EveryoneMask = self.ObjectData['EveryoneMask'], NextOwnerMask = self.ObjectData['NextOwnerMask'], OwnershipCost = self.ObjectData['OwnershipCost'], SaleType = self.ObjectData['SaleType'], SalePrice = self.ObjectData['SalePrice'], AggregatePerms = self.ObjectData['AggregatePerms'], AggregatePermTextures = self.ObjectData['AggregatePermTextures'], AggregatePermTexturesOwner = self.ObjectData['AggregatePermTexturesOwner'], Category = self.ObjectData['Category'], InventorySerial = self.ObjectData['InventorySerial'], ItemID = self.ObjectData['ItemID'], FolderID = self.ObjectData['FolderID'], FromTaskID = self.ObjectData['FromTaskID'], LastOwnerID = self.ObjectData['LastOwnerID'], Name = self.ObjectData['Name'], Description = self.ObjectData['Description'], TouchName = self.ObjectData['TouchName'], SitName = self.ObjectData['SitName'], TextureID = self.ObjectData['TextureID']))

class SetStartLocationPacket(object):
    ''' a template for a SetStartLocation packet '''

    def __init__(self):
        self.name = 'SetStartLocation'

        self.StartLocationData = {}    # New StartLocationData block
        self.StartLocationData['AgentID'] = None    # MVT_LLUUID
        self.StartLocationData['RegionID'] = None    # MVT_LLUUID
        self.StartLocationData['LocationID'] = None    # MVT_U32
        self.StartLocationData['RegionHandle'] = None    # MVT_U64
        self.StartLocationData['LocationPos'] = None    # MVT_LLVector3
        self.StartLocationData['LocationLookAt'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SetStartLocation', Block('StartLocationData', AgentID = self.StartLocationData['AgentID'], RegionID = self.StartLocationData['RegionID'], LocationID = self.StartLocationData['LocationID'], RegionHandle = self.StartLocationData['RegionHandle'], LocationPos = self.StartLocationData['LocationPos'], LocationLookAt = self.StartLocationData['LocationLookAt']))

class EstateCovenantReplyPacket(object):
    ''' a template for a EstateCovenantReply packet '''

    def __init__(self):
        self.name = 'EstateCovenantReply'

        self.Data = {}    # New Data block
        self.Data['CovenantID'] = None    # MVT_LLUUID
        self.Data['CovenantTimestamp'] = None    # MVT_U32
        self.Data['EstateName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EstateCovenantReply', Block('Data', CovenantID = self.Data['CovenantID'], CovenantTimestamp = self.Data['CovenantTimestamp'], EstateName = self.Data['EstateName']))

class MapNameRequestPacket(object):
    ''' a template for a MapNameRequest packet '''

    def __init__(self):
        self.name = 'MapNameRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['Flags'] = None    # MVT_U32
        self.AgentData['EstateID'] = None    # MVT_U32
        self.AgentData['Godlike'] = None    # MVT_BOOL

        self.NameData = {}    # New NameData block
        self.NameData['Name'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MapNameRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], Flags = self.AgentData['Flags'], EstateID = self.AgentData['EstateID'], Godlike = self.AgentData['Godlike']), Block('NameData', Name = self.NameData['Name']))

class AgentHeightWidthPacket(object):
    ''' a template for a AgentHeightWidth packet '''

    def __init__(self):
        self.name = 'AgentHeightWidth'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['CircuitCode'] = None    # MVT_U32

        self.HeightWidthBlock = {}    # New HeightWidthBlock block
        self.HeightWidthBlock['GenCounter'] = None    # MVT_U32
        self.HeightWidthBlock['Height'] = None    # MVT_U16
        self.HeightWidthBlock['Width'] = None    # MVT_U16

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentHeightWidth', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], CircuitCode = self.AgentData['CircuitCode']), Block('HeightWidthBlock', GenCounter = self.HeightWidthBlock['GenCounter'], Height = self.HeightWidthBlock['Height'], Width = self.HeightWidthBlock['Width']))

class DeclineCallingCardPacket(object):
    ''' a template for a DeclineCallingCard packet '''

    def __init__(self):
        self.name = 'DeclineCallingCard'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.TransactionBlock = {}    # New TransactionBlock block
        self.TransactionBlock['TransactionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DeclineCallingCard', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('TransactionBlock', TransactionID = self.TransactionBlock['TransactionID']))

class EventNotificationRemoveRequestPacket(object):
    ''' a template for a EventNotificationRemoveRequest packet '''

    def __init__(self):
        self.name = 'EventNotificationRemoveRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.EventData = {}    # New EventData block
        self.EventData['EventID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EventNotificationRemoveRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('EventData', EventID = self.EventData['EventID']))

class NeighborListPacket(object):
    ''' a template for a NeighborList packet '''

    def __init__(self):
        self.name = 'NeighborList'

        self.NeighborBlock = {}    # New NeighborBlock block
        self.NeighborBlock['IP'] = None    # MVT_IP_ADDR
        self.NeighborBlock['Port'] = None    # MVT_IP_PORT
        self.NeighborBlock['PublicIP'] = None    # MVT_IP_ADDR
        self.NeighborBlock['PublicPort'] = None    # MVT_IP_PORT
        self.NeighborBlock['RegionID'] = None    # MVT_LLUUID
        self.NeighborBlock['Name'] = None    # MVT_VARIABLE
        self.NeighborBlock['SimAccess'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('NeighborList', Block('NeighborBlock', IP = self.NeighborBlock['IP'], Port = self.NeighborBlock['Port'], PublicIP = self.NeighborBlock['PublicIP'], PublicPort = self.NeighborBlock['PublicPort'], RegionID = self.NeighborBlock['RegionID'], Name = self.NeighborBlock['Name'], SimAccess = self.NeighborBlock['SimAccess']))

class AgentDataUpdateRequestPacket(object):
    ''' a template for a AgentDataUpdateRequest packet '''

    def __init__(self):
        self.name = 'AgentDataUpdateRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentDataUpdateRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class GroupNoticeAddPacket(object):
    ''' a template for a GroupNoticeAdd packet '''

    def __init__(self):
        self.name = 'GroupNoticeAdd'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.MessageBlock = {}    # New MessageBlock block
        self.MessageBlock['ToGroupID'] = None    # MVT_LLUUID
        self.MessageBlock['ID'] = None    # MVT_LLUUID
        self.MessageBlock['Dialog'] = None    # MVT_U8
        self.MessageBlock['FromAgentName'] = None    # MVT_VARIABLE
        self.MessageBlock['Message'] = None    # MVT_VARIABLE
        self.MessageBlock['BinaryBucket'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupNoticeAdd', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('MessageBlock', ToGroupID = self.MessageBlock['ToGroupID'], ID = self.MessageBlock['ID'], Dialog = self.MessageBlock['Dialog'], FromAgentName = self.MessageBlock['FromAgentName'], Message = self.MessageBlock['Message'], BinaryBucket = self.MessageBlock['BinaryBucket']))

class CopyInventoryFromNotecardPacket(object):
    ''' a template for a CopyInventoryFromNotecard packet '''

    def __init__(self):
        self.name = 'CopyInventoryFromNotecard'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.NotecardData = {}    # New NotecardData block
        self.NotecardData['NotecardItemID'] = None    # MVT_LLUUID
        self.NotecardData['ObjectID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID
        self.InventoryData['FolderID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CopyInventoryFromNotecard', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('NotecardData', NotecardItemID = self.NotecardData['NotecardItemID'], ObjectID = self.NotecardData['ObjectID']), Block('InventoryData', ItemID = self.InventoryData['ItemID'], FolderID = self.InventoryData['FolderID']))

class NearestLandingRegionRequestPacket(object):
    ''' a template for a NearestLandingRegionRequest packet '''

    def __init__(self):
        self.name = 'NearestLandingRegionRequest'

        self.RequestingRegionData = {}    # New RequestingRegionData block
        self.RequestingRegionData['RegionHandle'] = None    # MVT_U64

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('NearestLandingRegionRequest', Block('RequestingRegionData', RegionHandle = self.RequestingRegionData['RegionHandle']))

class ChildAgentUpdatePacket(object):
    ''' a template for a ChildAgentUpdate packet '''

    def __init__(self):
        self.name = 'ChildAgentUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['RegionHandle'] = None    # MVT_U64
        self.AgentData['ViewerCircuitCode'] = None    # MVT_U32
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['AgentPos'] = None    # MVT_LLVector3
        self.AgentData['AgentVel'] = None    # MVT_LLVector3
        self.AgentData['Center'] = None    # MVT_LLVector3
        self.AgentData['Size'] = None    # MVT_LLVector3
        self.AgentData['AtAxis'] = None    # MVT_LLVector3
        self.AgentData['LeftAxis'] = None    # MVT_LLVector3
        self.AgentData['UpAxis'] = None    # MVT_LLVector3
        self.AgentData['ChangedGrid'] = None    # MVT_BOOL
        self.AgentData['Far'] = None    # MVT_F32
        self.AgentData['Aspect'] = None    # MVT_F32
        self.AgentData['Throttles'] = None    # MVT_VARIABLE
        self.AgentData['HeadRotation'] = None    # MVT_LLQuaternion
        self.AgentData['BodyRotation'] = None    # MVT_LLQuaternion
        self.AgentData['ControlFlags'] = None    # MVT_U32
        self.AgentData['EnergyLevel'] = None    # MVT_F32
        self.AgentData['GodLevel'] = None    # MVT_U8
        self.AgentData['AlwaysRun'] = None    # MVT_BOOL
        self.AgentData['PreyAgent'] = None    # MVT_LLUUID
        self.AgentData['AgentAccess'] = None    # MVT_U8
        self.AgentData['AgentTextures'] = None    # MVT_VARIABLE
        self.AgentData['ActiveGroupID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['GroupPowers'] = None    # MVT_U64
        self.GroupData['AcceptNotices'] = None    # MVT_BOOL

        self.AnimationData = {}    # New AnimationData block
        self.AnimationData['Animation'] = None    # MVT_LLUUID
        self.AnimationData['ObjectID'] = None    # MVT_LLUUID

        self.GranterBlock = {}    # New GranterBlock block
        self.GranterBlock['GranterID'] = None    # MVT_LLUUID

        self.NVPairData = {}    # New NVPairData block
        self.NVPairData['NVPairs'] = None    # MVT_VARIABLE

        self.VisualParam = {}    # New VisualParam block
        self.VisualParam['ParamValue'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ChildAgentUpdate', Block('AgentData', RegionHandle = self.AgentData['RegionHandle'], ViewerCircuitCode = self.AgentData['ViewerCircuitCode'], AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], AgentPos = self.AgentData['AgentPos'], AgentVel = self.AgentData['AgentVel'], Center = self.AgentData['Center'], Size = self.AgentData['Size'], AtAxis = self.AgentData['AtAxis'], LeftAxis = self.AgentData['LeftAxis'], UpAxis = self.AgentData['UpAxis'], ChangedGrid = self.AgentData['ChangedGrid'], Far = self.AgentData['Far'], Aspect = self.AgentData['Aspect'], Throttles = self.AgentData['Throttles'], HeadRotation = self.AgentData['HeadRotation'], BodyRotation = self.AgentData['BodyRotation'], ControlFlags = self.AgentData['ControlFlags'], EnergyLevel = self.AgentData['EnergyLevel'], GodLevel = self.AgentData['GodLevel'], AlwaysRun = self.AgentData['AlwaysRun'], PreyAgent = self.AgentData['PreyAgent'], AgentAccess = self.AgentData['AgentAccess'], AgentTextures = self.AgentData['AgentTextures'], ActiveGroupID = self.AgentData['ActiveGroupID']), Block('GroupData', GroupID = self.GroupData['GroupID'], GroupPowers = self.GroupData['GroupPowers'], AcceptNotices = self.GroupData['AcceptNotices']), Block('AnimationData', Animation = self.AnimationData['Animation'], ObjectID = self.AnimationData['ObjectID']), Block('GranterBlock', GranterID = self.GranterBlock['GranterID']), Block('NVPairData', NVPairs = self.NVPairData['NVPairs']), Block('VisualParam', ParamValue = self.VisualParam['ParamValue']))

class DirClassifiedQueryPacket(object):
    ''' a template for a DirClassifiedQuery packet '''

    def __init__(self):
        self.name = 'DirClassifiedQuery'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['QueryText'] = None    # MVT_VARIABLE
        self.QueryData['QueryFlags'] = None    # MVT_U32
        self.QueryData['Category'] = None    # MVT_U32
        self.QueryData['QueryStart'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirClassifiedQuery', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('QueryData', QueryID = self.QueryData['QueryID'], QueryText = self.QueryData['QueryText'], QueryFlags = self.QueryData['QueryFlags'], Category = self.QueryData['Category'], QueryStart = self.QueryData['QueryStart']))

class GroupRoleUpdatePacket(object):
    ''' a template for a GroupRoleUpdate packet '''

    def __init__(self):
        self.name = 'GroupRoleUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.RoleData = {}    # New RoleData block
        self.RoleData['RoleID'] = None    # MVT_LLUUID
        self.RoleData['Name'] = None    # MVT_VARIABLE
        self.RoleData['Description'] = None    # MVT_VARIABLE
        self.RoleData['Title'] = None    # MVT_VARIABLE
        self.RoleData['Powers'] = None    # MVT_U64
        self.RoleData['UpdateType'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupRoleUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('RoleData', RoleID = self.RoleData['RoleID'], Name = self.RoleData['Name'], Description = self.RoleData['Description'], Title = self.RoleData['Title'], Powers = self.RoleData['Powers'], UpdateType = self.RoleData['UpdateType']))

class TestMessagePacket(object):
    ''' a template for a TestMessage packet '''

    def __init__(self):
        self.name = 'TestMessage'

        self.TestBlock1 = {}    # New TestBlock1 block
        self.TestBlock1['Test1'] = None    # MVT_U32

        self.NeighborBlock = {}    # New NeighborBlock block
        self.NeighborBlock['Test0'] = None    # MVT_U32
        self.NeighborBlock['Test1'] = None    # MVT_U32
        self.NeighborBlock['Test2'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TestMessage', Block('TestBlock1', Test1 = self.TestBlock1['Test1']), Block('NeighborBlock', Test0 = self.NeighborBlock['Test0'], Test1 = self.NeighborBlock['Test1'], Test2 = self.NeighborBlock['Test2']))

class GroupAccountDetailsReplyPacket(object):
    ''' a template for a GroupAccountDetailsReply packet '''

    def __init__(self):
        self.name = 'GroupAccountDetailsReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.MoneyData = {}    # New MoneyData block
        self.MoneyData['RequestID'] = None    # MVT_LLUUID
        self.MoneyData['IntervalDays'] = None    # MVT_S32
        self.MoneyData['CurrentInterval'] = None    # MVT_S32
        self.MoneyData['StartDate'] = None    # MVT_VARIABLE

        self.HistoryData = {}    # New HistoryData block
        self.HistoryData['Description'] = None    # MVT_VARIABLE
        self.HistoryData['Amount'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupAccountDetailsReply', Block('AgentData', AgentID = self.AgentData['AgentID'], GroupID = self.AgentData['GroupID']), Block('MoneyData', RequestID = self.MoneyData['RequestID'], IntervalDays = self.MoneyData['IntervalDays'], CurrentInterval = self.MoneyData['CurrentInterval'], StartDate = self.MoneyData['StartDate']), Block('HistoryData', Description = self.HistoryData['Description'], Amount = self.HistoryData['Amount']))

class UUIDNameRequestPacket(object):
    ''' a template for a UUIDNameRequest packet '''

    def __init__(self):
        self.name = 'UUIDNameRequest'

        self.UUIDNameBlock = {}    # New UUIDNameBlock block
        self.UUIDNameBlock['ID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UUIDNameRequest', Block('UUIDNameBlock', ID = self.UUIDNameBlock['ID']))

class ObjectDropPacket(object):
    ''' a template for a ObjectDrop packet '''

    def __init__(self):
        self.name = 'ObjectDrop'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectDrop', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class AttachedSoundGainChangePacket(object):
    ''' a template for a AttachedSoundGainChange packet '''

    def __init__(self):
        self.name = 'AttachedSoundGainChange'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['ObjectID'] = None    # MVT_LLUUID
        self.DataBlock['Gain'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AttachedSoundGainChange', Block('DataBlock', ObjectID = self.DataBlock['ObjectID'], Gain = self.DataBlock['Gain']))

class AssetUploadCompletePacket(object):
    ''' a template for a AssetUploadComplete packet '''

    def __init__(self):
        self.name = 'AssetUploadComplete'

        self.AssetBlock = {}    # New AssetBlock block
        self.AssetBlock['UUID'] = None    # MVT_LLUUID
        self.AssetBlock['Type'] = None    # MVT_S8
        self.AssetBlock['Success'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AssetUploadComplete', Block('AssetBlock', UUID = self.AssetBlock['UUID'], Type = self.AssetBlock['Type'], Success = self.AssetBlock['Success']))

class ParcelBuyPacket(object):
    ''' a template for a ParcelBuy packet '''

    def __init__(self):
        self.name = 'ParcelBuy'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['GroupID'] = None    # MVT_LLUUID
        self.Data['IsGroupOwned'] = None    # MVT_BOOL
        self.Data['RemoveContribution'] = None    # MVT_BOOL
        self.Data['LocalID'] = None    # MVT_S32
        self.Data['Final'] = None    # MVT_BOOL

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['Price'] = None    # MVT_S32
        self.ParcelData['Area'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelBuy', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', GroupID = self.Data['GroupID'], IsGroupOwned = self.Data['IsGroupOwned'], RemoveContribution = self.Data['RemoveContribution'], LocalID = self.Data['LocalID'], Final = self.Data['Final']), Block('ParcelData', Price = self.ParcelData['Price'], Area = self.ParcelData['Area']))

class RpcScriptReplyInboundPacket(object):
    ''' a template for a RpcScriptReplyInbound packet '''

    def __init__(self):
        self.name = 'RpcScriptReplyInbound'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['TaskID'] = None    # MVT_LLUUID
        self.DataBlock['ItemID'] = None    # MVT_LLUUID
        self.DataBlock['ChannelID'] = None    # MVT_LLUUID
        self.DataBlock['IntValue'] = None    # MVT_U32
        self.DataBlock['StringValue'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RpcScriptReplyInbound', Block('DataBlock', TaskID = self.DataBlock['TaskID'], ItemID = self.DataBlock['ItemID'], ChannelID = self.DataBlock['ChannelID'], IntValue = self.DataBlock['IntValue'], StringValue = self.DataBlock['StringValue']))

class ObjectScalePacket(object):
    ''' a template for a ObjectScale packet '''

    def __init__(self):
        self.name = 'ObjectScale'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['Scale'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectScale', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], Scale = self.ObjectData['Scale']))

class TransferInventoryAckPacket(object):
    ''' a template for a TransferInventoryAck packet '''

    def __init__(self):
        self.name = 'TransferInventoryAck'

        self.InfoBlock = {}    # New InfoBlock block
        self.InfoBlock['TransactionID'] = None    # MVT_LLUUID
        self.InfoBlock['InventoryID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TransferInventoryAck', Block('InfoBlock', TransactionID = self.InfoBlock['TransactionID'], InventoryID = self.InfoBlock['InventoryID']))

class ScriptDialogReplyPacket(object):
    ''' a template for a ScriptDialogReply packet '''

    def __init__(self):
        self.name = 'ScriptDialogReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['ObjectID'] = None    # MVT_LLUUID
        self.Data['ChatChannel'] = None    # MVT_S32
        self.Data['ButtonIndex'] = None    # MVT_S32
        self.Data['ButtonLabel'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptDialogReply', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', ObjectID = self.Data['ObjectID'], ChatChannel = self.Data['ChatChannel'], ButtonIndex = self.Data['ButtonIndex'], ButtonLabel = self.Data['ButtonLabel']))

class RezSingleAttachmentFromInvPacket(object):
    ''' a template for a RezSingleAttachmentFromInv packet '''

    def __init__(self):
        self.name = 'RezSingleAttachmentFromInv'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ItemID'] = None    # MVT_LLUUID
        self.ObjectData['OwnerID'] = None    # MVT_LLUUID
        self.ObjectData['AttachmentPt'] = None    # MVT_U8
        self.ObjectData['ItemFlags'] = None    # MVT_U32
        self.ObjectData['GroupMask'] = None    # MVT_U32
        self.ObjectData['EveryoneMask'] = None    # MVT_U32
        self.ObjectData['NextOwnerMask'] = None    # MVT_U32
        self.ObjectData['Name'] = None    # MVT_VARIABLE
        self.ObjectData['Description'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RezSingleAttachmentFromInv', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ItemID = self.ObjectData['ItemID'], OwnerID = self.ObjectData['OwnerID'], AttachmentPt = self.ObjectData['AttachmentPt'], ItemFlags = self.ObjectData['ItemFlags'], GroupMask = self.ObjectData['GroupMask'], EveryoneMask = self.ObjectData['EveryoneMask'], NextOwnerMask = self.ObjectData['NextOwnerMask'], Name = self.ObjectData['Name'], Description = self.ObjectData['Description']))

class StartLurePacket(object):
    ''' a template for a StartLure packet '''

    def __init__(self):
        self.name = 'StartLure'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Info = {}    # New Info block
        self.Info['LureType'] = None    # MVT_U8
        self.Info['Message'] = None    # MVT_VARIABLE

        self.TargetData = {}    # New TargetData block
        self.TargetData['TargetID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('StartLure', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Info', LureType = self.Info['LureType'], Message = self.Info['Message']), Block('TargetData', TargetID = self.TargetData['TargetID']))

class UpdateInventoryFolderPacket(object):
    ''' a template for a UpdateInventoryFolder packet '''

    def __init__(self):
        self.name = 'UpdateInventoryFolder'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.FolderData = {}    # New FolderData block
        self.FolderData['FolderID'] = None    # MVT_LLUUID
        self.FolderData['ParentID'] = None    # MVT_LLUUID
        self.FolderData['Type'] = None    # MVT_S8
        self.FolderData['Name'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UpdateInventoryFolder', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('FolderData', FolderID = self.FolderData['FolderID'], ParentID = self.FolderData['ParentID'], Type = self.FolderData['Type'], Name = self.FolderData['Name']))

class TransferRequestPacket(object):
    ''' a template for a TransferRequest packet '''

    def __init__(self):
        self.name = 'TransferRequest'

        self.TransferInfo = {}    # New TransferInfo block
        self.TransferInfo['TransferID'] = None    # MVT_LLUUID
        self.TransferInfo['ChannelType'] = None    # MVT_S32
        self.TransferInfo['SourceType'] = None    # MVT_S32
        self.TransferInfo['Priority'] = None    # MVT_F32
        self.TransferInfo['Params'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TransferRequest', Block('TransferInfo', TransferID = self.TransferInfo['TransferID'], ChannelType = self.TransferInfo['ChannelType'], SourceType = self.TransferInfo['SourceType'], Priority = self.TransferInfo['Priority'], Params = self.TransferInfo['Params']))

class KillObjectPacket(object):
    ''' a template for a KillObject packet '''

    def __init__(self):
        self.name = 'KillObject'

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('KillObject', Block('ObjectData', ID = self.ObjectData['ID']))

class DirFindQueryBackendPacket(object):
    ''' a template for a DirFindQueryBackend packet '''

    def __init__(self):
        self.name = 'DirFindQueryBackend'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['QueryText'] = None    # MVT_VARIABLE
        self.QueryData['QueryFlags'] = None    # MVT_U32
        self.QueryData['QueryStart'] = None    # MVT_S32
        self.QueryData['EstateID'] = None    # MVT_U32
        self.QueryData['Godlike'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirFindQueryBackend', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID'], QueryText = self.QueryData['QueryText'], QueryFlags = self.QueryData['QueryFlags'], QueryStart = self.QueryData['QueryStart'], EstateID = self.QueryData['EstateID'], Godlike = self.QueryData['Godlike']))

class ViewerStatsPacket(object):
    ''' a template for a ViewerStats packet '''

    def __init__(self):
        self.name = 'ViewerStats'

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ViewerStats')

class TelehubInfoPacket(object):
    ''' a template for a TelehubInfo packet '''

    def __init__(self):
        self.name = 'TelehubInfo'

        self.TelehubBlock = {}    # New TelehubBlock block
        self.TelehubBlock['ObjectID'] = None    # MVT_LLUUID
        self.TelehubBlock['ObjectName'] = None    # MVT_VARIABLE
        self.TelehubBlock['TelehubPos'] = None    # MVT_LLVector3
        self.TelehubBlock['TelehubRot'] = None    # MVT_LLQuaternion

        self.SpawnPointBlock = {}    # New SpawnPointBlock block
        self.SpawnPointBlock['SpawnPointPos'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TelehubInfo', Block('TelehubBlock', ObjectID = self.TelehubBlock['ObjectID'], ObjectName = self.TelehubBlock['ObjectName'], TelehubPos = self.TelehubBlock['TelehubPos'], TelehubRot = self.TelehubBlock['TelehubRot']), Block('SpawnPointBlock', SpawnPointPos = self.SpawnPointBlock['SpawnPointPos']))

class TallyVotesPacket(object):
    ''' a template for a TallyVotes packet '''

    def __init__(self):
        self.name = 'TallyVotes'

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TallyVotes')

class ScriptRunningReplyPacket(object):
    ''' a template for a ScriptRunningReply packet '''

    def __init__(self):
        self.name = 'ScriptRunningReply'

        self.Script = {}    # New Script block
        self.Script['ObjectID'] = None    # MVT_LLUUID
        self.Script['ItemID'] = None    # MVT_LLUUID
        self.Script['Running'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptRunningReply', Block('Script', ObjectID = self.Script['ObjectID'], ItemID = self.Script['ItemID'], Running = self.Script['Running']))

class ObjectExportSelectedPacket(object):
    ''' a template for a ObjectExportSelected packet '''

    def __init__(self):
        self.name = 'ObjectExportSelected'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['RequestID'] = None    # MVT_LLUUID
        self.AgentData['VolumeDetail'] = None    # MVT_S16

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectExportSelected', Block('AgentData', AgentID = self.AgentData['AgentID'], RequestID = self.AgentData['RequestID'], VolumeDetail = self.AgentData['VolumeDetail']), Block('ObjectData', ObjectID = self.ObjectData['ObjectID']))

class JoinGroupRequestPacket(object):
    ''' a template for a JoinGroupRequest packet '''

    def __init__(self):
        self.name = 'JoinGroupRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('JoinGroupRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', GroupID = self.GroupData['GroupID']))

class RemoveParcelPacket(object):
    ''' a template for a RemoveParcel packet '''

    def __init__(self):
        self.name = 'RemoveParcel'

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['ParcelID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RemoveParcel', Block('ParcelData', ParcelID = self.ParcelData['ParcelID']))

class ObjectGroupPacket(object):
    ''' a template for a ObjectGroup packet '''

    def __init__(self):
        self.name = 'ObjectGroup'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectGroup', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class CreateInventoryItemPacket(object):
    ''' a template for a CreateInventoryItem packet '''

    def __init__(self):
        self.name = 'CreateInventoryItem'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.InventoryBlock = {}    # New InventoryBlock block
        self.InventoryBlock['CallbackID'] = None    # MVT_U32
        self.InventoryBlock['FolderID'] = None    # MVT_LLUUID
        self.InventoryBlock['TransactionID'] = None    # MVT_LLUUID
        self.InventoryBlock['NextOwnerMask'] = None    # MVT_U32
        self.InventoryBlock['Type'] = None    # MVT_S8
        self.InventoryBlock['InvType'] = None    # MVT_S8
        self.InventoryBlock['WearableType'] = None    # MVT_U8
        self.InventoryBlock['Name'] = None    # MVT_VARIABLE
        self.InventoryBlock['Description'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CreateInventoryItem', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('InventoryBlock', CallbackID = self.InventoryBlock['CallbackID'], FolderID = self.InventoryBlock['FolderID'], TransactionID = self.InventoryBlock['TransactionID'], NextOwnerMask = self.InventoryBlock['NextOwnerMask'], Type = self.InventoryBlock['Type'], InvType = self.InventoryBlock['InvType'], WearableType = self.InventoryBlock['WearableType'], Name = self.InventoryBlock['Name'], Description = self.InventoryBlock['Description']))

class PickInfoReplyPacket(object):
    ''' a template for a PickInfoReply packet '''

    def __init__(self):
        self.name = 'PickInfoReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['PickID'] = None    # MVT_LLUUID
        self.Data['CreatorID'] = None    # MVT_LLUUID
        self.Data['TopPick'] = None    # MVT_BOOL
        self.Data['ParcelID'] = None    # MVT_LLUUID
        self.Data['Name'] = None    # MVT_VARIABLE
        self.Data['Desc'] = None    # MVT_VARIABLE
        self.Data['SnapshotID'] = None    # MVT_LLUUID
        self.Data['User'] = None    # MVT_VARIABLE
        self.Data['OriginalName'] = None    # MVT_VARIABLE
        self.Data['SimName'] = None    # MVT_VARIABLE
        self.Data['PosGlobal'] = None    # MVT_LLVector3d
        self.Data['SortOrder'] = None    # MVT_S32
        self.Data['Enabled'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('PickInfoReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('Data', PickID = self.Data['PickID'], CreatorID = self.Data['CreatorID'], TopPick = self.Data['TopPick'], ParcelID = self.Data['ParcelID'], Name = self.Data['Name'], Desc = self.Data['Desc'], SnapshotID = self.Data['SnapshotID'], User = self.Data['User'], OriginalName = self.Data['OriginalName'], SimName = self.Data['SimName'], PosGlobal = self.Data['PosGlobal'], SortOrder = self.Data['SortOrder'], Enabled = self.Data['Enabled']))

class SystemMessagePacket(object):
    ''' a template for a SystemMessage packet '''

    def __init__(self):
        self.name = 'SystemMessage'

        self.MethodData = {}    # New MethodData block
        self.MethodData['Method'] = None    # MVT_VARIABLE
        self.MethodData['Invoice'] = None    # MVT_LLUUID
        self.MethodData['Digest'] = None    # MVT_FIXED

        self.ParamList = {}    # New ParamList block
        self.ParamList['Parameter'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SystemMessage', Block('MethodData', Method = self.MethodData['Method'], Invoice = self.MethodData['Invoice'], Digest = self.MethodData['Digest']), Block('ParamList', Parameter = self.ParamList['Parameter']))

class AgentResumePacket(object):
    ''' a template for a AgentResume packet '''

    def __init__(self):
        self.name = 'AgentResume'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['SerialNum'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentResume', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], SerialNum = self.AgentData['SerialNum']))

class InventoryAssetResponsePacket(object):
    ''' a template for a InventoryAssetResponse packet '''

    def __init__(self):
        self.name = 'InventoryAssetResponse'

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['AssetID'] = None    # MVT_LLUUID
        self.QueryData['IsReadable'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('InventoryAssetResponse', Block('QueryData', QueryID = self.QueryData['QueryID'], AssetID = self.QueryData['AssetID'], IsReadable = self.QueryData['IsReadable']))

class PayPriceReplyPacket(object):
    ''' a template for a PayPriceReply packet '''

    def __init__(self):
        self.name = 'PayPriceReply'

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        self.ObjectData['DefaultPayPrice'] = None    # MVT_S32

        self.ButtonData = {}    # New ButtonData block
        self.ButtonData['PayButton'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('PayPriceReply', Block('ObjectData', ObjectID = self.ObjectData['ObjectID'], DefaultPayPrice = self.ObjectData['DefaultPayPrice']), Block('ButtonData', PayButton = self.ButtonData['PayButton']))

class ParcelPropertiesPacket(object):
    ''' a template for a ParcelProperties packet '''

    def __init__(self):
        self.name = 'ParcelProperties'

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['RequestResult'] = None    # MVT_S32
        self.ParcelData['SequenceID'] = None    # MVT_S32
        self.ParcelData['SnapSelection'] = None    # MVT_BOOL
        self.ParcelData['SelfCount'] = None    # MVT_S32
        self.ParcelData['OtherCount'] = None    # MVT_S32
        self.ParcelData['PublicCount'] = None    # MVT_S32
        self.ParcelData['LocalID'] = None    # MVT_S32
        self.ParcelData['OwnerID'] = None    # MVT_LLUUID
        self.ParcelData['IsGroupOwned'] = None    # MVT_BOOL
        self.ParcelData['AuctionID'] = None    # MVT_U32
        self.ParcelData['ClaimDate'] = None    # MVT_S32
        self.ParcelData['ClaimPrice'] = None    # MVT_S32
        self.ParcelData['RentPrice'] = None    # MVT_S32
        self.ParcelData['AABBMin'] = None    # MVT_LLVector3
        self.ParcelData['AABBMax'] = None    # MVT_LLVector3
        self.ParcelData['Bitmap'] = None    # MVT_VARIABLE
        self.ParcelData['Area'] = None    # MVT_S32
        self.ParcelData['Status'] = None    # MVT_U8
        self.ParcelData['SimWideMaxPrims'] = None    # MVT_S32
        self.ParcelData['SimWideTotalPrims'] = None    # MVT_S32
        self.ParcelData['MaxPrims'] = None    # MVT_S32
        self.ParcelData['TotalPrims'] = None    # MVT_S32
        self.ParcelData['OwnerPrims'] = None    # MVT_S32
        self.ParcelData['GroupPrims'] = None    # MVT_S32
        self.ParcelData['OtherPrims'] = None    # MVT_S32
        self.ParcelData['SelectedPrims'] = None    # MVT_S32
        self.ParcelData['ParcelPrimBonus'] = None    # MVT_F32
        self.ParcelData['OtherCleanTime'] = None    # MVT_S32
        self.ParcelData['ParcelFlags'] = None    # MVT_U32
        self.ParcelData['SalePrice'] = None    # MVT_S32
        self.ParcelData['Name'] = None    # MVT_VARIABLE
        self.ParcelData['Desc'] = None    # MVT_VARIABLE
        self.ParcelData['MusicURL'] = None    # MVT_VARIABLE
        self.ParcelData['MediaURL'] = None    # MVT_VARIABLE
        self.ParcelData['MediaID'] = None    # MVT_LLUUID
        self.ParcelData['MediaAutoScale'] = None    # MVT_U8
        self.ParcelData['GroupID'] = None    # MVT_LLUUID
        self.ParcelData['PassPrice'] = None    # MVT_S32
        self.ParcelData['PassHours'] = None    # MVT_F32
        self.ParcelData['Category'] = None    # MVT_U8
        self.ParcelData['AuthBuyerID'] = None    # MVT_LLUUID
        self.ParcelData['SnapshotID'] = None    # MVT_LLUUID
        self.ParcelData['UserLocation'] = None    # MVT_LLVector3
        self.ParcelData['UserLookAt'] = None    # MVT_LLVector3
        self.ParcelData['LandingType'] = None    # MVT_U8
        self.ParcelData['RegionPushOverride'] = None    # MVT_BOOL
        self.ParcelData['RegionDenyAnonymous'] = None    # MVT_BOOL
        self.ParcelData['RegionDenyIdentified'] = None    # MVT_BOOL
        self.ParcelData['RegionDenyTransacted'] = None    # MVT_BOOL

        self.AgeVerificationBlock = {}    # New AgeVerificationBlock block
        self.AgeVerificationBlock['RegionDenyAgeUnverified'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelProperties', Block('ParcelData', RequestResult = self.ParcelData['RequestResult'], SequenceID = self.ParcelData['SequenceID'], SnapSelection = self.ParcelData['SnapSelection'], SelfCount = self.ParcelData['SelfCount'], OtherCount = self.ParcelData['OtherCount'], PublicCount = self.ParcelData['PublicCount'], LocalID = self.ParcelData['LocalID'], OwnerID = self.ParcelData['OwnerID'], IsGroupOwned = self.ParcelData['IsGroupOwned'], AuctionID = self.ParcelData['AuctionID'], ClaimDate = self.ParcelData['ClaimDate'], ClaimPrice = self.ParcelData['ClaimPrice'], RentPrice = self.ParcelData['RentPrice'], AABBMin = self.ParcelData['AABBMin'], AABBMax = self.ParcelData['AABBMax'], Bitmap = self.ParcelData['Bitmap'], Area = self.ParcelData['Area'], Status = self.ParcelData['Status'], SimWideMaxPrims = self.ParcelData['SimWideMaxPrims'], SimWideTotalPrims = self.ParcelData['SimWideTotalPrims'], MaxPrims = self.ParcelData['MaxPrims'], TotalPrims = self.ParcelData['TotalPrims'], OwnerPrims = self.ParcelData['OwnerPrims'], GroupPrims = self.ParcelData['GroupPrims'], OtherPrims = self.ParcelData['OtherPrims'], SelectedPrims = self.ParcelData['SelectedPrims'], ParcelPrimBonus = self.ParcelData['ParcelPrimBonus'], OtherCleanTime = self.ParcelData['OtherCleanTime'], ParcelFlags = self.ParcelData['ParcelFlags'], SalePrice = self.ParcelData['SalePrice'], Name = self.ParcelData['Name'], Desc = self.ParcelData['Desc'], MusicURL = self.ParcelData['MusicURL'], MediaURL = self.ParcelData['MediaURL'], MediaID = self.ParcelData['MediaID'], MediaAutoScale = self.ParcelData['MediaAutoScale'], GroupID = self.ParcelData['GroupID'], PassPrice = self.ParcelData['PassPrice'], PassHours = self.ParcelData['PassHours'], Category = self.ParcelData['Category'], AuthBuyerID = self.ParcelData['AuthBuyerID'], SnapshotID = self.ParcelData['SnapshotID'], UserLocation = self.ParcelData['UserLocation'], UserLookAt = self.ParcelData['UserLookAt'], LandingType = self.ParcelData['LandingType'], RegionPushOverride = self.ParcelData['RegionPushOverride'], RegionDenyAnonymous = self.ParcelData['RegionDenyAnonymous'], RegionDenyIdentified = self.ParcelData['RegionDenyIdentified'], RegionDenyTransacted = self.ParcelData['RegionDenyTransacted']), Block('AgeVerificationBlock', RegionDenyAgeUnverified = self.AgeVerificationBlock['RegionDenyAgeUnverified']))

class DirClassifiedReplyPacket(object):
    ''' a template for a DirClassifiedReply packet '''

    def __init__(self):
        self.name = 'DirClassifiedReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID

        self.QueryReplies = {}    # New QueryReplies block
        self.QueryReplies['ClassifiedID'] = None    # MVT_LLUUID
        self.QueryReplies['Name'] = None    # MVT_VARIABLE
        self.QueryReplies['ClassifiedFlags'] = None    # MVT_U8
        self.QueryReplies['CreationDate'] = None    # MVT_U32
        self.QueryReplies['ExpirationDate'] = None    # MVT_U32
        self.QueryReplies['PriceForListing'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirClassifiedReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID']), Block('QueryReplies', ClassifiedID = self.QueryReplies['ClassifiedID'], Name = self.QueryReplies['Name'], ClassifiedFlags = self.QueryReplies['ClassifiedFlags'], CreationDate = self.QueryReplies['CreationDate'], ExpirationDate = self.QueryReplies['ExpirationDate'], PriceForListing = self.QueryReplies['PriceForListing']))

class GenericMessagePacket(object):
    ''' a template for a GenericMessage packet '''

    def __init__(self):
        self.name = 'GenericMessage'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['TransactionID'] = None    # MVT_LLUUID

        self.MethodData = {}    # New MethodData block
        self.MethodData['Method'] = None    # MVT_VARIABLE
        self.MethodData['Invoice'] = None    # MVT_LLUUID

        self.ParamList = {}    # New ParamList block
        self.ParamList['Parameter'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GenericMessage', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], TransactionID = self.AgentData['TransactionID']), Block('MethodData', Method = self.MethodData['Method'], Invoice = self.MethodData['Invoice']), Block('ParamList', Parameter = self.ParamList['Parameter']))

class SimStatsPacket(object):
    ''' a template for a SimStats packet '''

    def __init__(self):
        self.name = 'SimStats'

        self.Region = {}    # New Region block
        self.Region['RegionX'] = None    # MVT_U32
        self.Region['RegionY'] = None    # MVT_U32
        self.Region['RegionFlags'] = None    # MVT_U32
        self.Region['ObjectCapacity'] = None    # MVT_U32

        self.Stat = {}    # New Stat block
        self.Stat['StatID'] = None    # MVT_U32
        self.Stat['StatValue'] = None    # MVT_F32

        self.PidStat = {}    # New PidStat block
        self.PidStat['PID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SimStats', Block('Region', RegionX = self.Region['RegionX'], RegionY = self.Region['RegionY'], RegionFlags = self.Region['RegionFlags'], ObjectCapacity = self.Region['ObjectCapacity']), Block('Stat', StatID = self.Stat['StatID'], StatValue = self.Stat['StatValue']), Block('PidStat', PID = self.PidStat['PID']))

class FeatureDisabledPacket(object):
    ''' a template for a FeatureDisabled packet '''

    def __init__(self):
        self.name = 'FeatureDisabled'

        self.FailureInfo = {}    # New FailureInfo block
        self.FailureInfo['ErrorMessage'] = None    # MVT_VARIABLE
        self.FailureInfo['AgentID'] = None    # MVT_LLUUID
        self.FailureInfo['TransactionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('FeatureDisabled', Block('FailureInfo', ErrorMessage = self.FailureInfo['ErrorMessage'], AgentID = self.FailureInfo['AgentID'], TransactionID = self.FailureInfo['TransactionID']))

class PacketAckPacket(object):
    ''' a template for a PacketAck packet '''

    def __init__(self):
        self.name = 'PacketAck'

        self.Packets = {}    # New Packets block
        self.Packets['ID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('PacketAck', Block('Packets', ID = self.Packets['ID']))

class GroupRoleMembersReplyPacket(object):
    ''' a template for a GroupRoleMembersReply packet '''

    def __init__(self):
        self.name = 'GroupRoleMembersReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID
        self.AgentData['RequestID'] = None    # MVT_LLUUID
        self.AgentData['TotalPairs'] = None    # MVT_U32

        self.MemberData = {}    # New MemberData block
        self.MemberData['RoleID'] = None    # MVT_LLUUID
        self.MemberData['MemberID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupRoleMembersReply', Block('AgentData', AgentID = self.AgentData['AgentID'], GroupID = self.AgentData['GroupID'], RequestID = self.AgentData['RequestID'], TotalPairs = self.AgentData['TotalPairs']), Block('MemberData', RoleID = self.MemberData['RoleID'], MemberID = self.MemberData['MemberID']))

class LogoutReplyPacket(object):
    ''' a template for a LogoutReply packet '''

    def __init__(self):
        self.name = 'LogoutReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LogoutReply', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('InventoryData', ItemID = self.InventoryData['ItemID']))

class EmailMessageReplyPacket(object):
    ''' a template for a EmailMessageReply packet '''

    def __init__(self):
        self.name = 'EmailMessageReply'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['ObjectID'] = None    # MVT_LLUUID
        self.DataBlock['More'] = None    # MVT_U32
        self.DataBlock['Time'] = None    # MVT_U32
        self.DataBlock['FromAddress'] = None    # MVT_VARIABLE
        self.DataBlock['Subject'] = None    # MVT_VARIABLE
        self.DataBlock['Data'] = None    # MVT_VARIABLE
        self.DataBlock['MailFilter'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EmailMessageReply', Block('DataBlock', ObjectID = self.DataBlock['ObjectID'], More = self.DataBlock['More'], Time = self.DataBlock['Time'], FromAddress = self.DataBlock['FromAddress'], Subject = self.DataBlock['Subject'], Data = self.DataBlock['Data'], MailFilter = self.DataBlock['MailFilter']))

class CompleteAuctionPacket(object):
    ''' a template for a CompleteAuction packet '''

    def __init__(self):
        self.name = 'CompleteAuction'

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['ParcelID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CompleteAuction', Block('ParcelData', ParcelID = self.ParcelData['ParcelID']))

class ObjectSelectPacket(object):
    ''' a template for a ObjectSelect packet '''

    def __init__(self):
        self.name = 'ObjectSelect'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectSelect', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class MultipleObjectUpdatePacket(object):
    ''' a template for a MultipleObjectUpdate packet '''

    def __init__(self):
        self.name = 'MultipleObjectUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['Type'] = None    # MVT_U8
        self.ObjectData['Data'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MultipleObjectUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], Type = self.ObjectData['Type'], Data = self.ObjectData['Data']))

class MoneyBalanceReplyPacket(object):
    ''' a template for a MoneyBalanceReply packet '''

    def __init__(self):
        self.name = 'MoneyBalanceReply'

        self.MoneyData = {}    # New MoneyData block
        self.MoneyData['AgentID'] = None    # MVT_LLUUID
        self.MoneyData['TransactionID'] = None    # MVT_LLUUID
        self.MoneyData['TransactionSuccess'] = None    # MVT_BOOL
        self.MoneyData['MoneyBalance'] = None    # MVT_S32
        self.MoneyData['SquareMetersCredit'] = None    # MVT_S32
        self.MoneyData['SquareMetersCommitted'] = None    # MVT_S32
        self.MoneyData['Description'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MoneyBalanceReply', Block('MoneyData', AgentID = self.MoneyData['AgentID'], TransactionID = self.MoneyData['TransactionID'], TransactionSuccess = self.MoneyData['TransactionSuccess'], MoneyBalance = self.MoneyData['MoneyBalance'], SquareMetersCredit = self.MoneyData['SquareMetersCredit'], SquareMetersCommitted = self.MoneyData['SquareMetersCommitted'], Description = self.MoneyData['Description']))

class RevokePermissionsPacket(object):
    ''' a template for a RevokePermissions packet '''

    def __init__(self):
        self.name = 'RevokePermissions'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['ObjectID'] = None    # MVT_LLUUID
        self.Data['ObjectPermissions'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RevokePermissions', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', ObjectID = self.Data['ObjectID'], ObjectPermissions = self.Data['ObjectPermissions']))

class RpcChannelRequestPacket(object):
    ''' a template for a RpcChannelRequest packet '''

    def __init__(self):
        self.name = 'RpcChannelRequest'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['GridX'] = None    # MVT_U32
        self.DataBlock['GridY'] = None    # MVT_U32
        self.DataBlock['TaskID'] = None    # MVT_LLUUID
        self.DataBlock['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RpcChannelRequest', Block('DataBlock', GridX = self.DataBlock['GridX'], GridY = self.DataBlock['GridY'], TaskID = self.DataBlock['TaskID'], ItemID = self.DataBlock['ItemID']))

class TeleportCancelPacket(object):
    ''' a template for a TeleportCancel packet '''

    def __init__(self):
        self.name = 'TeleportCancel'

        self.Info = {}    # New Info block
        self.Info['AgentID'] = None    # MVT_LLUUID
        self.Info['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TeleportCancel', Block('Info', AgentID = self.Info['AgentID'], SessionID = self.Info['SessionID']))

class DeRezAckPacket(object):
    ''' a template for a DeRezAck packet '''

    def __init__(self):
        self.name = 'DeRezAck'

        self.TransactionData = {}    # New TransactionData block
        self.TransactionData['TransactionID'] = None    # MVT_LLUUID
        self.TransactionData['Success'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DeRezAck', Block('TransactionData', TransactionID = self.TransactionData['TransactionID'], Success = self.TransactionData['Success']))

class AvatarPropertiesReplyPacket(object):
    ''' a template for a AvatarPropertiesReply packet '''

    def __init__(self):
        self.name = 'AvatarPropertiesReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['AvatarID'] = None    # MVT_LLUUID

        self.PropertiesData = {}    # New PropertiesData block
        self.PropertiesData['ImageID'] = None    # MVT_LLUUID
        self.PropertiesData['FLImageID'] = None    # MVT_LLUUID
        self.PropertiesData['PartnerID'] = None    # MVT_LLUUID
        self.PropertiesData['AboutText'] = None    # MVT_VARIABLE
        self.PropertiesData['FLAboutText'] = None    # MVT_VARIABLE
        self.PropertiesData['BornOn'] = None    # MVT_VARIABLE
        self.PropertiesData['ProfileURL'] = None    # MVT_VARIABLE
        self.PropertiesData['CharterMember'] = None    # MVT_VARIABLE
        self.PropertiesData['Flags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarPropertiesReply', Block('AgentData', AgentID = self.AgentData['AgentID'], AvatarID = self.AgentData['AvatarID']), Block('PropertiesData', ImageID = self.PropertiesData['ImageID'], FLImageID = self.PropertiesData['FLImageID'], PartnerID = self.PropertiesData['PartnerID'], AboutText = self.PropertiesData['AboutText'], FLAboutText = self.PropertiesData['FLAboutText'], BornOn = self.PropertiesData['BornOn'], ProfileURL = self.PropertiesData['ProfileURL'], CharterMember = self.PropertiesData['CharterMember'], Flags = self.PropertiesData['Flags']))

class ObjectUpdateCachedPacket(object):
    ''' a template for a ObjectUpdateCached packet '''

    def __init__(self):
        self.name = 'ObjectUpdateCached'

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionHandle'] = None    # MVT_U64
        self.RegionData['TimeDilation'] = None    # MVT_U16

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ID'] = None    # MVT_U32
        self.ObjectData['CRC'] = None    # MVT_U32
        self.ObjectData['UpdateFlags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectUpdateCached', Block('RegionData', RegionHandle = self.RegionData['RegionHandle'], TimeDilation = self.RegionData['TimeDilation']), Block('ObjectData', ID = self.ObjectData['ID'], CRC = self.ObjectData['CRC'], UpdateFlags = self.ObjectData['UpdateFlags']))

class LogTextMessagePacket(object):
    ''' a template for a LogTextMessage packet '''

    def __init__(self):
        self.name = 'LogTextMessage'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['FromAgentId'] = None    # MVT_LLUUID
        self.DataBlock['ToAgentId'] = None    # MVT_LLUUID
        self.DataBlock['GlobalX'] = None    # MVT_F64
        self.DataBlock['GlobalY'] = None    # MVT_F64
        self.DataBlock['Time'] = None    # MVT_U32
        self.DataBlock['Message'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LogTextMessage', Block('DataBlock', FromAgentId = self.DataBlock['FromAgentId'], ToAgentId = self.DataBlock['ToAgentId'], GlobalX = self.DataBlock['GlobalX'], GlobalY = self.DataBlock['GlobalY'], Time = self.DataBlock['Time'], Message = self.DataBlock['Message']))

class DirLandReplyPacket(object):
    ''' a template for a DirLandReply packet '''

    def __init__(self):
        self.name = 'DirLandReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID

        self.QueryReplies = {}    # New QueryReplies block
        self.QueryReplies['ParcelID'] = None    # MVT_LLUUID
        self.QueryReplies['Name'] = None    # MVT_VARIABLE
        self.QueryReplies['Auction'] = None    # MVT_BOOL
        self.QueryReplies['ForSale'] = None    # MVT_BOOL
        self.QueryReplies['SalePrice'] = None    # MVT_S32
        self.QueryReplies['ActualArea'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirLandReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID']), Block('QueryReplies', ParcelID = self.QueryReplies['ParcelID'], Name = self.QueryReplies['Name'], Auction = self.QueryReplies['Auction'], ForSale = self.QueryReplies['ForSale'], SalePrice = self.QueryReplies['SalePrice'], ActualArea = self.QueryReplies['ActualArea']))

class RemoveInventoryItemPacket(object):
    ''' a template for a RemoveInventoryItem packet '''

    def __init__(self):
        self.name = 'RemoveInventoryItem'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RemoveInventoryItem', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('InventoryData', ItemID = self.InventoryData['ItemID']))

class RegionHandshakeReplyPacket(object):
    ''' a template for a RegionHandshakeReply packet '''

    def __init__(self):
        self.name = 'RegionHandshakeReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.RegionInfo = {}    # New RegionInfo block
        self.RegionInfo['Flags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RegionHandshakeReply', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('RegionInfo', Flags = self.RegionInfo['Flags']))

class AvatarPickerReplyPacket(object):
    ''' a template for a AvatarPickerReply packet '''

    def __init__(self):
        self.name = 'AvatarPickerReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['QueryID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['AvatarID'] = None    # MVT_LLUUID
        self.Data['FirstName'] = None    # MVT_VARIABLE
        self.Data['LastName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarPickerReply', Block('AgentData', AgentID = self.AgentData['AgentID'], QueryID = self.AgentData['QueryID']), Block('Data', AvatarID = self.Data['AvatarID'], FirstName = self.Data['FirstName'], LastName = self.Data['LastName']))

class AgentIsNowWearingPacket(object):
    ''' a template for a AgentIsNowWearing packet '''

    def __init__(self):
        self.name = 'AgentIsNowWearing'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.WearableData = {}    # New WearableData block
        self.WearableData['ItemID'] = None    # MVT_LLUUID
        self.WearableData['WearableType'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentIsNowWearing', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('WearableData', ItemID = self.WearableData['ItemID'], WearableType = self.WearableData['WearableType']))

class SimulatorSetMapPacket(object):
    ''' a template for a SimulatorSetMap packet '''

    def __init__(self):
        self.name = 'SimulatorSetMap'

        self.MapData = {}    # New MapData block
        self.MapData['RegionHandle'] = None    # MVT_U64
        self.MapData['Type'] = None    # MVT_S32
        self.MapData['MapImage'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SimulatorSetMap', Block('MapData', RegionHandle = self.MapData['RegionHandle'], Type = self.MapData['Type'], MapImage = self.MapData['MapImage']))

class EjectGroupMemberRequestPacket(object):
    ''' a template for a EjectGroupMemberRequest packet '''

    def __init__(self):
        self.name = 'EjectGroupMemberRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID

        self.EjectData = {}    # New EjectData block
        self.EjectData['EjecteeID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EjectGroupMemberRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', GroupID = self.GroupData['GroupID']), Block('EjectData', EjecteeID = self.EjectData['EjecteeID']))

class LogParcelChangesPacket(object):
    ''' a template for a LogParcelChanges packet '''

    def __init__(self):
        self.name = 'LogParcelChanges'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionHandle'] = None    # MVT_U64

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['ParcelID'] = None    # MVT_LLUUID
        self.ParcelData['OwnerID'] = None    # MVT_LLUUID
        self.ParcelData['IsOwnerGroup'] = None    # MVT_BOOL
        self.ParcelData['ActualArea'] = None    # MVT_S32
        self.ParcelData['Action'] = None    # MVT_S8
        self.ParcelData['TransactionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LogParcelChanges', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('RegionData', RegionHandle = self.RegionData['RegionHandle']), Block('ParcelData', ParcelID = self.ParcelData['ParcelID'], OwnerID = self.ParcelData['OwnerID'], IsOwnerGroup = self.ParcelData['IsOwnerGroup'], ActualArea = self.ParcelData['ActualArea'], Action = self.ParcelData['Action'], TransactionID = self.ParcelData['TransactionID']))

class ObjectDeGrabPacket(object):
    ''' a template for a ObjectDeGrab packet '''

    def __init__(self):
        self.name = 'ObjectDeGrab'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['LocalID'] = None    # MVT_U32

        self.SurfaceInfo = {}    # New SurfaceInfo block
        self.SurfaceInfo['UVCoord'] = None    # MVT_LLVector3
        self.SurfaceInfo['STCoord'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectDeGrab', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', LocalID = self.ObjectData['LocalID']), Block('SurfaceInfo', UVCoord = self.SurfaceInfo['UVCoord'], STCoord = self.SurfaceInfo['STCoord']))

class ParcelPropertiesRequestPacket(object):
    ''' a template for a ParcelPropertiesRequest packet '''

    def __init__(self):
        self.name = 'ParcelPropertiesRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['SequenceID'] = None    # MVT_S32
        self.ParcelData['West'] = None    # MVT_F32
        self.ParcelData['South'] = None    # MVT_F32
        self.ParcelData['East'] = None    # MVT_F32
        self.ParcelData['North'] = None    # MVT_F32
        self.ParcelData['SnapSelection'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelPropertiesRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', SequenceID = self.ParcelData['SequenceID'], West = self.ParcelData['West'], South = self.ParcelData['South'], East = self.ParcelData['East'], North = self.ParcelData['North'], SnapSelection = self.ParcelData['SnapSelection']))

class OfflineNotificationPacket(object):
    ''' a template for a OfflineNotification packet '''

    def __init__(self):
        self.name = 'OfflineNotification'

        self.AgentBlock = {}    # New AgentBlock block
        self.AgentBlock['AgentID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('OfflineNotification', Block('AgentBlock', AgentID = self.AgentBlock['AgentID']))

class ParcelSelectObjectsPacket(object):
    ''' a template for a ParcelSelectObjects packet '''

    def __init__(self):
        self.name = 'ParcelSelectObjects'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['LocalID'] = None    # MVT_S32
        self.ParcelData['ReturnType'] = None    # MVT_U32

        self.ReturnIDs = {}    # New ReturnIDs block
        self.ReturnIDs['ReturnID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelSelectObjects', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', LocalID = self.ParcelData['LocalID'], ReturnType = self.ParcelData['ReturnType']), Block('ReturnIDs', ReturnID = self.ReturnIDs['ReturnID']))

class LandStatReplyPacket(object):
    ''' a template for a LandStatReply packet '''

    def __init__(self):
        self.name = 'LandStatReply'

        self.RequestData = {}    # New RequestData block
        self.RequestData['ReportType'] = None    # MVT_U32
        self.RequestData['RequestFlags'] = None    # MVT_U32
        self.RequestData['TotalObjectCount'] = None    # MVT_U32

        self.ReportData = {}    # New ReportData block
        self.ReportData['TaskLocalID'] = None    # MVT_U32
        self.ReportData['TaskID'] = None    # MVT_LLUUID
        self.ReportData['LocationX'] = None    # MVT_F32
        self.ReportData['LocationY'] = None    # MVT_F32
        self.ReportData['LocationZ'] = None    # MVT_F32
        self.ReportData['Score'] = None    # MVT_F32
        self.ReportData['TaskName'] = None    # MVT_VARIABLE
        self.ReportData['OwnerName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LandStatReply', Block('RequestData', ReportType = self.RequestData['ReportType'], RequestFlags = self.RequestData['RequestFlags'], TotalObjectCount = self.RequestData['TotalObjectCount']), Block('ReportData', TaskLocalID = self.ReportData['TaskLocalID'], TaskID = self.ReportData['TaskID'], LocationX = self.ReportData['LocationX'], LocationY = self.ReportData['LocationY'], LocationZ = self.ReportData['LocationZ'], Score = self.ReportData['Score'], TaskName = self.ReportData['TaskName'], OwnerName = self.ReportData['OwnerName']))

class AgentThrottlePacket(object):
    ''' a template for a AgentThrottle packet '''

    def __init__(self):
        self.name = 'AgentThrottle'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['CircuitCode'] = None    # MVT_U32

        self.Throttle = {}    # New Throttle block
        self.Throttle['GenCounter'] = None    # MVT_U32
        self.Throttle['Throttles'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentThrottle', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], CircuitCode = self.AgentData['CircuitCode']), Block('Throttle', GenCounter = self.Throttle['GenCounter'], Throttles = self.Throttle['Throttles']))

class ViewerEffectPacket(object):
    ''' a template for a ViewerEffect packet '''

    def __init__(self):
        self.name = 'ViewerEffect'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Effect = {}    # New Effect block
        self.Effect['ID'] = None    # MVT_LLUUID
        self.Effect['AgentID'] = None    # MVT_LLUUID
        self.Effect['Type'] = None    # MVT_U8
        self.Effect['Duration'] = None    # MVT_F32
        self.Effect['Color'] = None    # MVT_FIXED
        self.Effect['TypeData'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ViewerEffect', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Effect', ID = self.Effect['ID'], AgentID = self.Effect['AgentID'], Type = self.Effect['Type'], Duration = self.Effect['Duration'], Color = self.Effect['Color'], TypeData = self.Effect['TypeData']))

class OfferCallingCardPacket(object):
    ''' a template for a OfferCallingCard packet '''

    def __init__(self):
        self.name = 'OfferCallingCard'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.AgentBlock = {}    # New AgentBlock block
        self.AgentBlock['DestID'] = None    # MVT_LLUUID
        self.AgentBlock['TransactionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('OfferCallingCard', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('AgentBlock', DestID = self.AgentBlock['DestID'], TransactionID = self.AgentBlock['TransactionID']))

class EventInfoReplyPacket(object):
    ''' a template for a EventInfoReply packet '''

    def __init__(self):
        self.name = 'EventInfoReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.EventData = {}    # New EventData block
        self.EventData['EventID'] = None    # MVT_U32
        self.EventData['Creator'] = None    # MVT_VARIABLE
        self.EventData['Name'] = None    # MVT_VARIABLE
        self.EventData['Category'] = None    # MVT_VARIABLE
        self.EventData['Desc'] = None    # MVT_VARIABLE
        self.EventData['Date'] = None    # MVT_VARIABLE
        self.EventData['DateUTC'] = None    # MVT_U32
        self.EventData['Duration'] = None    # MVT_U32
        self.EventData['Cover'] = None    # MVT_U32
        self.EventData['Amount'] = None    # MVT_U32
        self.EventData['SimName'] = None    # MVT_VARIABLE
        self.EventData['GlobalPos'] = None    # MVT_LLVector3d
        self.EventData['EventFlags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EventInfoReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('EventData', EventID = self.EventData['EventID'], Creator = self.EventData['Creator'], Name = self.EventData['Name'], Category = self.EventData['Category'], Desc = self.EventData['Desc'], Date = self.EventData['Date'], DateUTC = self.EventData['DateUTC'], Duration = self.EventData['Duration'], Cover = self.EventData['Cover'], Amount = self.EventData['Amount'], SimName = self.EventData['SimName'], GlobalPos = self.EventData['GlobalPos'], EventFlags = self.EventData['EventFlags']))

class AgentAnimationPacket(object):
    ''' a template for a AgentAnimation packet '''

    def __init__(self):
        self.name = 'AgentAnimation'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.AnimationList = {}    # New AnimationList block
        self.AnimationList['AnimID'] = None    # MVT_LLUUID
        self.AnimationList['StartAnim'] = None    # MVT_BOOL

        self.PhysicalAvatarEventList = {}    # New PhysicalAvatarEventList block
        self.PhysicalAvatarEventList['TypeData'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentAnimation', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('AnimationList', AnimID = self.AnimationList['AnimID'], StartAnim = self.AnimationList['StartAnim']), Block('PhysicalAvatarEventList', TypeData = self.PhysicalAvatarEventList['TypeData']))

class AgentCachedTexturePacket(object):
    ''' a template for a AgentCachedTexture packet '''

    def __init__(self):
        self.name = 'AgentCachedTexture'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['SerialNum'] = None    # MVT_S32

        self.WearableData = {}    # New WearableData block
        self.WearableData['ID'] = None    # MVT_LLUUID
        self.WearableData['TextureIndex'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentCachedTexture', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], SerialNum = self.AgentData['SerialNum']), Block('WearableData', ID = self.WearableData['ID'], TextureIndex = self.WearableData['TextureIndex']))

class GroupNoticesListReplyPacket(object):
    ''' a template for a GroupNoticesListReply packet '''

    def __init__(self):
        self.name = 'GroupNoticesListReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['NoticeID'] = None    # MVT_LLUUID
        self.Data['Timestamp'] = None    # MVT_U32
        self.Data['FromName'] = None    # MVT_VARIABLE
        self.Data['Subject'] = None    # MVT_VARIABLE
        self.Data['HasAttachment'] = None    # MVT_BOOL
        self.Data['AssetType'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupNoticesListReply', Block('AgentData', AgentID = self.AgentData['AgentID'], GroupID = self.AgentData['GroupID']), Block('Data', NoticeID = self.Data['NoticeID'], Timestamp = self.Data['Timestamp'], FromName = self.Data['FromName'], Subject = self.Data['Subject'], HasAttachment = self.Data['HasAttachment'], AssetType = self.Data['AssetType']))

class FetchInventoryPacket(object):
    ''' a template for a FetchInventory packet '''

    def __init__(self):
        self.name = 'FetchInventory'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['OwnerID'] = None    # MVT_LLUUID
        self.InventoryData['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('FetchInventory', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('InventoryData', OwnerID = self.InventoryData['OwnerID'], ItemID = self.InventoryData['ItemID']))

class AvatarAppearancePacket(object):
    ''' a template for a AvatarAppearance packet '''

    def __init__(self):
        self.name = 'AvatarAppearance'

        self.Sender = {}    # New Sender block
        self.Sender['ID'] = None    # MVT_LLUUID
        self.Sender['IsTrial'] = None    # MVT_BOOL

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['TextureEntry'] = None    # MVT_VARIABLE

        self.VisualParam = {}    # New VisualParam block
        self.VisualParam['ParamValue'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarAppearance', Block('Sender', ID = self.Sender['ID'], IsTrial = self.Sender['IsTrial']), Block('ObjectData', TextureEntry = self.ObjectData['TextureEntry']), Block('VisualParam', ParamValue = self.VisualParam['ParamValue']))

class ChildAgentPositionUpdatePacket(object):
    ''' a template for a ChildAgentPositionUpdate packet '''

    def __init__(self):
        self.name = 'ChildAgentPositionUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['RegionHandle'] = None    # MVT_U64
        self.AgentData['ViewerCircuitCode'] = None    # MVT_U32
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['AgentPos'] = None    # MVT_LLVector3
        self.AgentData['AgentVel'] = None    # MVT_LLVector3
        self.AgentData['Center'] = None    # MVT_LLVector3
        self.AgentData['Size'] = None    # MVT_LLVector3
        self.AgentData['AtAxis'] = None    # MVT_LLVector3
        self.AgentData['LeftAxis'] = None    # MVT_LLVector3
        self.AgentData['UpAxis'] = None    # MVT_LLVector3
        self.AgentData['ChangedGrid'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ChildAgentPositionUpdate', Block('AgentData', RegionHandle = self.AgentData['RegionHandle'], ViewerCircuitCode = self.AgentData['ViewerCircuitCode'], AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], AgentPos = self.AgentData['AgentPos'], AgentVel = self.AgentData['AgentVel'], Center = self.AgentData['Center'], Size = self.AgentData['Size'], AtAxis = self.AgentData['AtAxis'], LeftAxis = self.AgentData['LeftAxis'], UpAxis = self.AgentData['UpAxis'], ChangedGrid = self.AgentData['ChangedGrid']))

class DirEventsReplyPacket(object):
    ''' a template for a DirEventsReply packet '''

    def __init__(self):
        self.name = 'DirEventsReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID

        self.QueryReplies = {}    # New QueryReplies block
        self.QueryReplies['OwnerID'] = None    # MVT_LLUUID
        self.QueryReplies['Name'] = None    # MVT_VARIABLE
        self.QueryReplies['EventID'] = None    # MVT_U32
        self.QueryReplies['Date'] = None    # MVT_VARIABLE
        self.QueryReplies['UnixTime'] = None    # MVT_U32
        self.QueryReplies['EventFlags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirEventsReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID']), Block('QueryReplies', OwnerID = self.QueryReplies['OwnerID'], Name = self.QueryReplies['Name'], EventID = self.QueryReplies['EventID'], Date = self.QueryReplies['Date'], UnixTime = self.QueryReplies['UnixTime'], EventFlags = self.QueryReplies['EventFlags']))

class GroupTitlesReplyPacket(object):
    ''' a template for a GroupTitlesReply packet '''

    def __init__(self):
        self.name = 'GroupTitlesReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID
        self.AgentData['RequestID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['Title'] = None    # MVT_VARIABLE
        self.GroupData['RoleID'] = None    # MVT_LLUUID
        self.GroupData['Selected'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupTitlesReply', Block('AgentData', AgentID = self.AgentData['AgentID'], GroupID = self.AgentData['GroupID'], RequestID = self.AgentData['RequestID']), Block('GroupData', Title = self.GroupData['Title'], RoleID = self.GroupData['RoleID'], Selected = self.GroupData['Selected']))

class RegionPresenceRequestByHandlePacket(object):
    ''' a template for a RegionPresenceRequestByHandle packet '''

    def __init__(self):
        self.name = 'RegionPresenceRequestByHandle'

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionHandle'] = None    # MVT_U64

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RegionPresenceRequestByHandle', Block('RegionData', RegionHandle = self.RegionData['RegionHandle']))

class GroupAccountSummaryReplyPacket(object):
    ''' a template for a GroupAccountSummaryReply packet '''

    def __init__(self):
        self.name = 'GroupAccountSummaryReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.MoneyData = {}    # New MoneyData block
        self.MoneyData['RequestID'] = None    # MVT_LLUUID
        self.MoneyData['IntervalDays'] = None    # MVT_S32
        self.MoneyData['CurrentInterval'] = None    # MVT_S32
        self.MoneyData['StartDate'] = None    # MVT_VARIABLE
        self.MoneyData['Balance'] = None    # MVT_S32
        self.MoneyData['TotalCredits'] = None    # MVT_S32
        self.MoneyData['TotalDebits'] = None    # MVT_S32
        self.MoneyData['ObjectTaxCurrent'] = None    # MVT_S32
        self.MoneyData['LightTaxCurrent'] = None    # MVT_S32
        self.MoneyData['LandTaxCurrent'] = None    # MVT_S32
        self.MoneyData['GroupTaxCurrent'] = None    # MVT_S32
        self.MoneyData['ParcelDirFeeCurrent'] = None    # MVT_S32
        self.MoneyData['ObjectTaxEstimate'] = None    # MVT_S32
        self.MoneyData['LightTaxEstimate'] = None    # MVT_S32
        self.MoneyData['LandTaxEstimate'] = None    # MVT_S32
        self.MoneyData['GroupTaxEstimate'] = None    # MVT_S32
        self.MoneyData['ParcelDirFeeEstimate'] = None    # MVT_S32
        self.MoneyData['NonExemptMembers'] = None    # MVT_S32
        self.MoneyData['LastTaxDate'] = None    # MVT_VARIABLE
        self.MoneyData['TaxDate'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupAccountSummaryReply', Block('AgentData', AgentID = self.AgentData['AgentID'], GroupID = self.AgentData['GroupID']), Block('MoneyData', RequestID = self.MoneyData['RequestID'], IntervalDays = self.MoneyData['IntervalDays'], CurrentInterval = self.MoneyData['CurrentInterval'], StartDate = self.MoneyData['StartDate'], Balance = self.MoneyData['Balance'], TotalCredits = self.MoneyData['TotalCredits'], TotalDebits = self.MoneyData['TotalDebits'], ObjectTaxCurrent = self.MoneyData['ObjectTaxCurrent'], LightTaxCurrent = self.MoneyData['LightTaxCurrent'], LandTaxCurrent = self.MoneyData['LandTaxCurrent'], GroupTaxCurrent = self.MoneyData['GroupTaxCurrent'], ParcelDirFeeCurrent = self.MoneyData['ParcelDirFeeCurrent'], ObjectTaxEstimate = self.MoneyData['ObjectTaxEstimate'], LightTaxEstimate = self.MoneyData['LightTaxEstimate'], LandTaxEstimate = self.MoneyData['LandTaxEstimate'], GroupTaxEstimate = self.MoneyData['GroupTaxEstimate'], ParcelDirFeeEstimate = self.MoneyData['ParcelDirFeeEstimate'], NonExemptMembers = self.MoneyData['NonExemptMembers'], LastTaxDate = self.MoneyData['LastTaxDate'], TaxDate = self.MoneyData['TaxDate']))

class CheckParcelAuctionsPacket(object):
    ''' a template for a CheckParcelAuctions packet '''

    def __init__(self):
        self.name = 'CheckParcelAuctions'

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionHandle'] = None    # MVT_U64

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CheckParcelAuctions', Block('RegionData', RegionHandle = self.RegionData['RegionHandle']))

class ObjectAttachPacket(object):
    ''' a template for a ObjectAttach packet '''

    def __init__(self):
        self.name = 'ObjectAttach'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['AttachmentPoint'] = None    # MVT_U8

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['Rotation'] = None    # MVT_LLQuaternion

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectAttach', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], AttachmentPoint = self.AgentData['AttachmentPoint']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], Rotation = self.ObjectData['Rotation']))

class RemoveAttachmentPacket(object):
    ''' a template for a RemoveAttachment packet '''

    def __init__(self):
        self.name = 'RemoveAttachment'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.AttachmentBlock = {}    # New AttachmentBlock block
        self.AttachmentBlock['AttachmentPoint'] = None    # MVT_U8
        self.AttachmentBlock['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RemoveAttachment', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('AttachmentBlock', AttachmentPoint = self.AttachmentBlock['AttachmentPoint'], ItemID = self.AttachmentBlock['ItemID']))

class ParcelDividePacket(object):
    ''' a template for a ParcelDivide packet '''

    def __init__(self):
        self.name = 'ParcelDivide'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['West'] = None    # MVT_F32
        self.ParcelData['South'] = None    # MVT_F32
        self.ParcelData['East'] = None    # MVT_F32
        self.ParcelData['North'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelDivide', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', West = self.ParcelData['West'], South = self.ParcelData['South'], East = self.ParcelData['East'], North = self.ParcelData['North']))

class ObjectDuplicatePacket(object):
    ''' a template for a ObjectDuplicate packet '''

    def __init__(self):
        self.name = 'ObjectDuplicate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.SharedData = {}    # New SharedData block
        self.SharedData['Offset'] = None    # MVT_LLVector3
        self.SharedData['DuplicateFlags'] = None    # MVT_U32

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectDuplicate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('SharedData', Offset = self.SharedData['Offset'], DuplicateFlags = self.SharedData['DuplicateFlags']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class RegionIDAndHandleReplyPacket(object):
    ''' a template for a RegionIDAndHandleReply packet '''

    def __init__(self):
        self.name = 'RegionIDAndHandleReply'

        self.ReplyBlock = {}    # New ReplyBlock block
        self.ReplyBlock['RegionID'] = None    # MVT_LLUUID
        self.ReplyBlock['RegionHandle'] = None    # MVT_U64

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RegionIDAndHandleReply', Block('ReplyBlock', RegionID = self.ReplyBlock['RegionID'], RegionHandle = self.ReplyBlock['RegionHandle']))

class ScriptControlChangePacket(object):
    ''' a template for a ScriptControlChange packet '''

    def __init__(self):
        self.name = 'ScriptControlChange'

        self.Data = {}    # New Data block
        self.Data['TakeControls'] = None    # MVT_BOOL
        self.Data['Controls'] = None    # MVT_U32
        self.Data['PassToAgent'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptControlChange', Block('Data', TakeControls = self.Data['TakeControls'], Controls = self.Data['Controls'], PassToAgent = self.Data['PassToAgent']))

class DenyTrustedCircuitPacket(object):
    ''' a template for a DenyTrustedCircuit packet '''

    def __init__(self):
        self.name = 'DenyTrustedCircuit'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['EndPointID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DenyTrustedCircuit', Block('DataBlock', EndPointID = self.DataBlock['EndPointID']))

class DataHomeLocationReplyPacket(object):
    ''' a template for a DataHomeLocationReply packet '''

    def __init__(self):
        self.name = 'DataHomeLocationReply'

        self.Info = {}    # New Info block
        self.Info['AgentID'] = None    # MVT_LLUUID
        self.Info['RegionHandle'] = None    # MVT_U64
        self.Info['Position'] = None    # MVT_LLVector3
        self.Info['LookAt'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DataHomeLocationReply', Block('Info', AgentID = self.Info['AgentID'], RegionHandle = self.Info['RegionHandle'], Position = self.Info['Position'], LookAt = self.Info['LookAt']))

class SaveAssetIntoInventoryPacket(object):
    ''' a template for a SaveAssetIntoInventory packet '''

    def __init__(self):
        self.name = 'SaveAssetIntoInventory'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID
        self.InventoryData['NewAssetID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SaveAssetIntoInventory', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('InventoryData', ItemID = self.InventoryData['ItemID'], NewAssetID = self.InventoryData['NewAssetID']))

class EjectUserPacket(object):
    ''' a template for a EjectUser packet '''

    def __init__(self):
        self.name = 'EjectUser'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['TargetID'] = None    # MVT_LLUUID
        self.Data['Flags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EjectUser', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', TargetID = self.Data['TargetID'], Flags = self.Data['Flags']))

class SendXferPacketPacket(object):
    ''' a template for a SendXferPacket packet '''

    def __init__(self):
        self.name = 'SendXferPacket'

        self.XferID = {}    # New XferID block
        self.XferID['ID'] = None    # MVT_U64
        self.XferID['Packet'] = None    # MVT_U32

        self.DataPacket = {}    # New DataPacket block
        self.DataPacket['Data'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SendXferPacket', Block('XferID', ID = self.XferID['ID'], Packet = self.XferID['Packet']), Block('DataPacket', Data = self.DataPacket['Data']))

class ClassifiedDeletePacket(object):
    ''' a template for a ClassifiedDelete packet '''

    def __init__(self):
        self.name = 'ClassifiedDelete'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['ClassifiedID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ClassifiedDelete', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', ClassifiedID = self.Data['ClassifiedID']))

class SimWideDeletesPacket(object):
    ''' a template for a SimWideDeletes packet '''

    def __init__(self):
        self.name = 'SimWideDeletes'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['TargetID'] = None    # MVT_LLUUID
        self.DataBlock['Flags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SimWideDeletes', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('DataBlock', TargetID = self.DataBlock['TargetID'], Flags = self.DataBlock['Flags']))

class UnsubscribeLoadPacket(object):
    ''' a template for a UnsubscribeLoad packet '''

    def __init__(self):
        self.name = 'UnsubscribeLoad'

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UnsubscribeLoad')

class StartGroupProposalPacket(object):
    ''' a template for a StartGroupProposal packet '''

    def __init__(self):
        self.name = 'StartGroupProposal'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ProposalData = {}    # New ProposalData block
        self.ProposalData['GroupID'] = None    # MVT_LLUUID
        self.ProposalData['Quorum'] = None    # MVT_S32
        self.ProposalData['Majority'] = None    # MVT_F32
        self.ProposalData['Duration'] = None    # MVT_S32
        self.ProposalData['ProposalText'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('StartGroupProposal', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ProposalData', GroupID = self.ProposalData['GroupID'], Quorum = self.ProposalData['Quorum'], Majority = self.ProposalData['Majority'], Duration = self.ProposalData['Duration'], ProposalText = self.ProposalData['ProposalText']))

class KillChildAgentsPacket(object):
    ''' a template for a KillChildAgents packet '''

    def __init__(self):
        self.name = 'KillChildAgents'

        self.IDBlock = {}    # New IDBlock block
        self.IDBlock['AgentID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('KillChildAgents', Block('IDBlock', AgentID = self.IDBlock['AgentID']))

class ObjectSpinUpdatePacket(object):
    ''' a template for a ObjectSpinUpdate packet '''

    def __init__(self):
        self.name = 'ObjectSpinUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        self.ObjectData['Rotation'] = None    # MVT_LLQuaternion

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectSpinUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectID = self.ObjectData['ObjectID'], Rotation = self.ObjectData['Rotation']))

class UpdateGroupInfoPacket(object):
    ''' a template for a UpdateGroupInfo packet '''

    def __init__(self):
        self.name = 'UpdateGroupInfo'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['Charter'] = None    # MVT_VARIABLE
        self.GroupData['ShowInList'] = None    # MVT_BOOL
        self.GroupData['InsigniaID'] = None    # MVT_LLUUID
        self.GroupData['MembershipFee'] = None    # MVT_S32
        self.GroupData['OpenEnrollment'] = None    # MVT_BOOL
        self.GroupData['AllowPublish'] = None    # MVT_BOOL
        self.GroupData['MaturePublish'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UpdateGroupInfo', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', GroupID = self.GroupData['GroupID'], Charter = self.GroupData['Charter'], ShowInList = self.GroupData['ShowInList'], InsigniaID = self.GroupData['InsigniaID'], MembershipFee = self.GroupData['MembershipFee'], OpenEnrollment = self.GroupData['OpenEnrollment'], AllowPublish = self.GroupData['AllowPublish'], MaturePublish = self.GroupData['MaturePublish']))

class RequestParcelTransferPacket(object):
    ''' a template for a RequestParcelTransfer packet '''

    def __init__(self):
        self.name = 'RequestParcelTransfer'

        self.Data = {}    # New Data block
        self.Data['TransactionID'] = None    # MVT_LLUUID
        self.Data['TransactionTime'] = None    # MVT_U32
        self.Data['SourceID'] = None    # MVT_LLUUID
        self.Data['DestID'] = None    # MVT_LLUUID
        self.Data['OwnerID'] = None    # MVT_LLUUID
        self.Data['Flags'] = None    # MVT_U8
        self.Data['TransactionType'] = None    # MVT_S32
        self.Data['Amount'] = None    # MVT_S32
        self.Data['BillableArea'] = None    # MVT_S32
        self.Data['ActualArea'] = None    # MVT_S32
        self.Data['Final'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RequestParcelTransfer', Block('Data', TransactionID = self.Data['TransactionID'], TransactionTime = self.Data['TransactionTime'], SourceID = self.Data['SourceID'], DestID = self.Data['DestID'], OwnerID = self.Data['OwnerID'], Flags = self.Data['Flags'], TransactionType = self.Data['TransactionType'], Amount = self.Data['Amount'], BillableArea = self.Data['BillableArea'], ActualArea = self.Data['ActualArea'], Final = self.Data['Final']))

class ObjectIncludeInSearchPacket(object):
    ''' a template for a ObjectIncludeInSearch packet '''

    def __init__(self):
        self.name = 'ObjectIncludeInSearch'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['IncludeInSearch'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectIncludeInSearch', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], IncludeInSearch = self.ObjectData['IncludeInSearch']))

class ObjectExtraParamsPacket(object):
    ''' a template for a ObjectExtraParams packet '''

    def __init__(self):
        self.name = 'ObjectExtraParams'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['ParamType'] = None    # MVT_U16
        self.ObjectData['ParamInUse'] = None    # MVT_BOOL
        self.ObjectData['ParamSize'] = None    # MVT_U32
        self.ObjectData['ParamData'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectExtraParams', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], ParamType = self.ObjectData['ParamType'], ParamInUse = self.ObjectData['ParamInUse'], ParamSize = self.ObjectData['ParamSize'], ParamData = self.ObjectData['ParamData']))

class UseCachedMuteListPacket(object):
    ''' a template for a UseCachedMuteList packet '''

    def __init__(self):
        self.name = 'UseCachedMuteList'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UseCachedMuteList', Block('AgentData', AgentID = self.AgentData['AgentID']))

class ParcelPropertiesUpdatePacket(object):
    ''' a template for a ParcelPropertiesUpdate packet '''

    def __init__(self):
        self.name = 'ParcelPropertiesUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['LocalID'] = None    # MVT_S32
        self.ParcelData['Flags'] = None    # MVT_U32
        self.ParcelData['ParcelFlags'] = None    # MVT_U32
        self.ParcelData['SalePrice'] = None    # MVT_S32
        self.ParcelData['Name'] = None    # MVT_VARIABLE
        self.ParcelData['Desc'] = None    # MVT_VARIABLE
        self.ParcelData['MusicURL'] = None    # MVT_VARIABLE
        self.ParcelData['MediaURL'] = None    # MVT_VARIABLE
        self.ParcelData['MediaID'] = None    # MVT_LLUUID
        self.ParcelData['MediaAutoScale'] = None    # MVT_U8
        self.ParcelData['GroupID'] = None    # MVT_LLUUID
        self.ParcelData['PassPrice'] = None    # MVT_S32
        self.ParcelData['PassHours'] = None    # MVT_F32
        self.ParcelData['Category'] = None    # MVT_U8
        self.ParcelData['AuthBuyerID'] = None    # MVT_LLUUID
        self.ParcelData['SnapshotID'] = None    # MVT_LLUUID
        self.ParcelData['UserLocation'] = None    # MVT_LLVector3
        self.ParcelData['UserLookAt'] = None    # MVT_LLVector3
        self.ParcelData['LandingType'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelPropertiesUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', LocalID = self.ParcelData['LocalID'], Flags = self.ParcelData['Flags'], ParcelFlags = self.ParcelData['ParcelFlags'], SalePrice = self.ParcelData['SalePrice'], Name = self.ParcelData['Name'], Desc = self.ParcelData['Desc'], MusicURL = self.ParcelData['MusicURL'], MediaURL = self.ParcelData['MediaURL'], MediaID = self.ParcelData['MediaID'], MediaAutoScale = self.ParcelData['MediaAutoScale'], GroupID = self.ParcelData['GroupID'], PassPrice = self.ParcelData['PassPrice'], PassHours = self.ParcelData['PassHours'], Category = self.ParcelData['Category'], AuthBuyerID = self.ParcelData['AuthBuyerID'], SnapshotID = self.ParcelData['SnapshotID'], UserLocation = self.ParcelData['UserLocation'], UserLookAt = self.ParcelData['UserLookAt'], LandingType = self.ParcelData['LandingType']))

class ParcelRenamePacket(object):
    ''' a template for a ParcelRename packet '''

    def __init__(self):
        self.name = 'ParcelRename'

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['ParcelID'] = None    # MVT_LLUUID
        self.ParcelData['NewName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelRename', Block('ParcelData', ParcelID = self.ParcelData['ParcelID'], NewName = self.ParcelData['NewName']))

class UndoLandPacket(object):
    ''' a template for a UndoLand packet '''

    def __init__(self):
        self.name = 'UndoLand'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UndoLand', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class BulkUpdateInventoryPacket(object):
    ''' a template for a BulkUpdateInventory packet '''

    def __init__(self):
        self.name = 'BulkUpdateInventory'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['TransactionID'] = None    # MVT_LLUUID

        self.FolderData = {}    # New FolderData block
        self.FolderData['FolderID'] = None    # MVT_LLUUID
        self.FolderData['ParentID'] = None    # MVT_LLUUID
        self.FolderData['Type'] = None    # MVT_S8
        self.FolderData['Name'] = None    # MVT_VARIABLE

        self.ItemData = {}    # New ItemData block
        self.ItemData['ItemID'] = None    # MVT_LLUUID
        self.ItemData['CallbackID'] = None    # MVT_U32
        self.ItemData['FolderID'] = None    # MVT_LLUUID
        self.ItemData['CreatorID'] = None    # MVT_LLUUID
        self.ItemData['OwnerID'] = None    # MVT_LLUUID
        self.ItemData['GroupID'] = None    # MVT_LLUUID
        self.ItemData['BaseMask'] = None    # MVT_U32
        self.ItemData['OwnerMask'] = None    # MVT_U32
        self.ItemData['GroupMask'] = None    # MVT_U32
        self.ItemData['EveryoneMask'] = None    # MVT_U32
        self.ItemData['NextOwnerMask'] = None    # MVT_U32
        self.ItemData['GroupOwned'] = None    # MVT_BOOL
        self.ItemData['AssetID'] = None    # MVT_LLUUID
        self.ItemData['Type'] = None    # MVT_S8
        self.ItemData['InvType'] = None    # MVT_S8
        self.ItemData['Flags'] = None    # MVT_U32
        self.ItemData['SaleType'] = None    # MVT_U8
        self.ItemData['SalePrice'] = None    # MVT_S32
        self.ItemData['Name'] = None    # MVT_VARIABLE
        self.ItemData['Description'] = None    # MVT_VARIABLE
        self.ItemData['CreationDate'] = None    # MVT_S32
        self.ItemData['CRC'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('BulkUpdateInventory', Block('AgentData', AgentID = self.AgentData['AgentID'], TransactionID = self.AgentData['TransactionID']), Block('FolderData', FolderID = self.FolderData['FolderID'], ParentID = self.FolderData['ParentID'], Type = self.FolderData['Type'], Name = self.FolderData['Name']), Block('ItemData', ItemID = self.ItemData['ItemID'], CallbackID = self.ItemData['CallbackID'], FolderID = self.ItemData['FolderID'], CreatorID = self.ItemData['CreatorID'], OwnerID = self.ItemData['OwnerID'], GroupID = self.ItemData['GroupID'], BaseMask = self.ItemData['BaseMask'], OwnerMask = self.ItemData['OwnerMask'], GroupMask = self.ItemData['GroupMask'], EveryoneMask = self.ItemData['EveryoneMask'], NextOwnerMask = self.ItemData['NextOwnerMask'], GroupOwned = self.ItemData['GroupOwned'], AssetID = self.ItemData['AssetID'], Type = self.ItemData['Type'], InvType = self.ItemData['InvType'], Flags = self.ItemData['Flags'], SaleType = self.ItemData['SaleType'], SalePrice = self.ItemData['SalePrice'], Name = self.ItemData['Name'], Description = self.ItemData['Description'], CreationDate = self.ItemData['CreationDate'], CRC = self.ItemData['CRC']))

class ClearFollowCamPropertiesPacket(object):
    ''' a template for a ClearFollowCamProperties packet '''

    def __init__(self):
        self.name = 'ClearFollowCamProperties'

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ClearFollowCamProperties', Block('ObjectData', ObjectID = self.ObjectData['ObjectID']))

class ImageDataPacket(object):
    ''' a template for a ImageData packet '''

    def __init__(self):
        self.name = 'ImageData'

        self.ImageID = {}    # New ImageID block
        self.ImageID['ID'] = None    # MVT_LLUUID
        self.ImageID['Codec'] = None    # MVT_U8
        self.ImageID['Size'] = None    # MVT_U32
        self.ImageID['Packets'] = None    # MVT_U16

        self.ImageData = {}    # New ImageData block
        self.ImageData['Data'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ImageData', Block('ImageID', ID = self.ImageID['ID'], Codec = self.ImageID['Codec'], Size = self.ImageID['Size'], Packets = self.ImageID['Packets']), Block('ImageData', Data = self.ImageData['Data']))

class ParcelInfoReplyPacket(object):
    ''' a template for a ParcelInfoReply packet '''

    def __init__(self):
        self.name = 'ParcelInfoReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['ParcelID'] = None    # MVT_LLUUID
        self.Data['OwnerID'] = None    # MVT_LLUUID
        self.Data['Name'] = None    # MVT_VARIABLE
        self.Data['Desc'] = None    # MVT_VARIABLE
        self.Data['ActualArea'] = None    # MVT_S32
        self.Data['BillableArea'] = None    # MVT_S32
        self.Data['Flags'] = None    # MVT_U8
        self.Data['GlobalX'] = None    # MVT_F32
        self.Data['GlobalY'] = None    # MVT_F32
        self.Data['GlobalZ'] = None    # MVT_F32
        self.Data['SimName'] = None    # MVT_VARIABLE
        self.Data['SnapshotID'] = None    # MVT_LLUUID
        self.Data['Dwell'] = None    # MVT_F32
        self.Data['SalePrice'] = None    # MVT_S32
        self.Data['AuctionID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelInfoReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('Data', ParcelID = self.Data['ParcelID'], OwnerID = self.Data['OwnerID'], Name = self.Data['Name'], Desc = self.Data['Desc'], ActualArea = self.Data['ActualArea'], BillableArea = self.Data['BillableArea'], Flags = self.Data['Flags'], GlobalX = self.Data['GlobalX'], GlobalY = self.Data['GlobalY'], GlobalZ = self.Data['GlobalZ'], SimName = self.Data['SimName'], SnapshotID = self.Data['SnapshotID'], Dwell = self.Data['Dwell'], SalePrice = self.Data['SalePrice'], AuctionID = self.Data['AuctionID']))

class GodlikeMessagePacket(object):
    ''' a template for a GodlikeMessage packet '''

    def __init__(self):
        self.name = 'GodlikeMessage'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['TransactionID'] = None    # MVT_LLUUID

        self.MethodData = {}    # New MethodData block
        self.MethodData['Method'] = None    # MVT_VARIABLE
        self.MethodData['Invoice'] = None    # MVT_LLUUID

        self.ParamList = {}    # New ParamList block
        self.ParamList['Parameter'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GodlikeMessage', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], TransactionID = self.AgentData['TransactionID']), Block('MethodData', Method = self.MethodData['Method'], Invoice = self.MethodData['Invoice']), Block('ParamList', Parameter = self.ParamList['Parameter']))

class HealthMessagePacket(object):
    ''' a template for a HealthMessage packet '''

    def __init__(self):
        self.name = 'HealthMessage'

        self.HealthData = {}    # New HealthData block
        self.HealthData['Health'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('HealthMessage', Block('HealthData', Health = self.HealthData['Health']))

class UpdateSimulatorPacket(object):
    ''' a template for a UpdateSimulator packet '''

    def __init__(self):
        self.name = 'UpdateSimulator'

        self.SimulatorInfo = {}    # New SimulatorInfo block
        self.SimulatorInfo['RegionID'] = None    # MVT_LLUUID
        self.SimulatorInfo['SimName'] = None    # MVT_VARIABLE
        self.SimulatorInfo['EstateID'] = None    # MVT_U32
        self.SimulatorInfo['SimAccess'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UpdateSimulator', Block('SimulatorInfo', RegionID = self.SimulatorInfo['RegionID'], SimName = self.SimulatorInfo['SimName'], EstateID = self.SimulatorInfo['EstateID'], SimAccess = self.SimulatorInfo['SimAccess']))

class CloseCircuitPacket(object):
    ''' a template for a CloseCircuit packet '''

    def __init__(self):
        self.name = 'CloseCircuit'

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CloseCircuit')

class GroupRoleDataReplyPacket(object):
    ''' a template for a GroupRoleDataReply packet '''

    def __init__(self):
        self.name = 'GroupRoleDataReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['RequestID'] = None    # MVT_LLUUID
        self.GroupData['RoleCount'] = None    # MVT_S32

        self.RoleData = {}    # New RoleData block
        self.RoleData['RoleID'] = None    # MVT_LLUUID
        self.RoleData['Name'] = None    # MVT_VARIABLE
        self.RoleData['Title'] = None    # MVT_VARIABLE
        self.RoleData['Description'] = None    # MVT_VARIABLE
        self.RoleData['Powers'] = None    # MVT_U64
        self.RoleData['Members'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupRoleDataReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('GroupData', GroupID = self.GroupData['GroupID'], RequestID = self.GroupData['RequestID'], RoleCount = self.GroupData['RoleCount']), Block('RoleData', RoleID = self.RoleData['RoleID'], Name = self.RoleData['Name'], Title = self.RoleData['Title'], Description = self.RoleData['Description'], Powers = self.RoleData['Powers'], Members = self.RoleData['Members']))

class DataServerLogoutPacket(object):
    ''' a template for a DataServerLogout packet '''

    def __init__(self):
        self.name = 'DataServerLogout'

        self.UserData = {}    # New UserData block
        self.UserData['AgentID'] = None    # MVT_LLUUID
        self.UserData['ViewerIP'] = None    # MVT_IP_ADDR
        self.UserData['Disconnect'] = None    # MVT_BOOL
        self.UserData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DataServerLogout', Block('UserData', AgentID = self.UserData['AgentID'], ViewerIP = self.UserData['ViewerIP'], Disconnect = self.UserData['Disconnect'], SessionID = self.UserData['SessionID']))

class InviteGroupResponsePacket(object):
    ''' a template for a InviteGroupResponse packet '''

    def __init__(self):
        self.name = 'InviteGroupResponse'

        self.InviteData = {}    # New InviteData block
        self.InviteData['AgentID'] = None    # MVT_LLUUID
        self.InviteData['InviteeID'] = None    # MVT_LLUUID
        self.InviteData['GroupID'] = None    # MVT_LLUUID
        self.InviteData['RoleID'] = None    # MVT_LLUUID
        self.InviteData['MembershipFee'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('InviteGroupResponse', Block('InviteData', AgentID = self.InviteData['AgentID'], InviteeID = self.InviteData['InviteeID'], GroupID = self.InviteData['GroupID'], RoleID = self.InviteData['RoleID'], MembershipFee = self.InviteData['MembershipFee']))

class StartAuctionPacket(object):
    ''' a template for a StartAuction packet '''

    def __init__(self):
        self.name = 'StartAuction'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['ParcelID'] = None    # MVT_LLUUID
        self.ParcelData['SnapshotID'] = None    # MVT_LLUUID
        self.ParcelData['Name'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('StartAuction', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('ParcelData', ParcelID = self.ParcelData['ParcelID'], SnapshotID = self.ParcelData['SnapshotID'], Name = self.ParcelData['Name']))

class ObjectDescriptionPacket(object):
    ''' a template for a ObjectDescription packet '''

    def __init__(self):
        self.name = 'ObjectDescription'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['LocalID'] = None    # MVT_U32
        self.ObjectData['Description'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectDescription', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', LocalID = self.ObjectData['LocalID'], Description = self.ObjectData['Description']))

class ObjectPositionPacket(object):
    ''' a template for a ObjectPosition packet '''

    def __init__(self):
        self.name = 'ObjectPosition'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['Position'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectPosition', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], Position = self.ObjectData['Position']))

class MoneyTransferBackendPacket(object):
    ''' a template for a MoneyTransferBackend packet '''

    def __init__(self):
        self.name = 'MoneyTransferBackend'

        self.MoneyData = {}    # New MoneyData block
        self.MoneyData['TransactionID'] = None    # MVT_LLUUID
        self.MoneyData['TransactionTime'] = None    # MVT_U32
        self.MoneyData['SourceID'] = None    # MVT_LLUUID
        self.MoneyData['DestID'] = None    # MVT_LLUUID
        self.MoneyData['Flags'] = None    # MVT_U8
        self.MoneyData['Amount'] = None    # MVT_S32
        self.MoneyData['AggregatePermNextOwner'] = None    # MVT_U8
        self.MoneyData['AggregatePermInventory'] = None    # MVT_U8
        self.MoneyData['TransactionType'] = None    # MVT_S32
        self.MoneyData['RegionID'] = None    # MVT_LLUUID
        self.MoneyData['GridX'] = None    # MVT_U32
        self.MoneyData['GridY'] = None    # MVT_U32
        self.MoneyData['Description'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MoneyTransferBackend', Block('MoneyData', TransactionID = self.MoneyData['TransactionID'], TransactionTime = self.MoneyData['TransactionTime'], SourceID = self.MoneyData['SourceID'], DestID = self.MoneyData['DestID'], Flags = self.MoneyData['Flags'], Amount = self.MoneyData['Amount'], AggregatePermNextOwner = self.MoneyData['AggregatePermNextOwner'], AggregatePermInventory = self.MoneyData['AggregatePermInventory'], TransactionType = self.MoneyData['TransactionType'], RegionID = self.MoneyData['RegionID'], GridX = self.MoneyData['GridX'], GridY = self.MoneyData['GridY'], Description = self.MoneyData['Description']))

class ParcelDeedToGroupPacket(object):
    ''' a template for a ParcelDeedToGroup packet '''

    def __init__(self):
        self.name = 'ParcelDeedToGroup'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['GroupID'] = None    # MVT_LLUUID
        self.Data['LocalID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelDeedToGroup', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', GroupID = self.Data['GroupID'], LocalID = self.Data['LocalID']))

class MapItemReplyPacket(object):
    ''' a template for a MapItemReply packet '''

    def __init__(self):
        self.name = 'MapItemReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['Flags'] = None    # MVT_U32

        self.RequestData = {}    # New RequestData block
        self.RequestData['ItemType'] = None    # MVT_U32

        self.Data = {}    # New Data block
        self.Data['X'] = None    # MVT_U32
        self.Data['Y'] = None    # MVT_U32
        self.Data['ID'] = None    # MVT_LLUUID
        self.Data['Extra'] = None    # MVT_S32
        self.Data['Extra2'] = None    # MVT_S32
        self.Data['Name'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MapItemReply', Block('AgentData', AgentID = self.AgentData['AgentID'], Flags = self.AgentData['Flags']), Block('RequestData', ItemType = self.RequestData['ItemType']), Block('Data', X = self.Data['X'], Y = self.Data['Y'], ID = self.Data['ID'], Extra = self.Data['Extra'], Extra2 = self.Data['Extra2'], Name = self.Data['Name']))

class ImageNotInDatabasePacket(object):
    ''' a template for a ImageNotInDatabase packet '''

    def __init__(self):
        self.name = 'ImageNotInDatabase'

        self.ImageID = {}    # New ImageID block
        self.ImageID['ID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ImageNotInDatabase', Block('ImageID', ID = self.ImageID['ID']))

class ReplyTaskInventoryPacket(object):
    ''' a template for a ReplyTaskInventory packet '''

    def __init__(self):
        self.name = 'ReplyTaskInventory'

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['TaskID'] = None    # MVT_LLUUID
        self.InventoryData['Serial'] = None    # MVT_S16
        self.InventoryData['Filename'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ReplyTaskInventory', Block('InventoryData', TaskID = self.InventoryData['TaskID'], Serial = self.InventoryData['Serial'], Filename = self.InventoryData['Filename']))

class AvatarPropertiesRequestPacket(object):
    ''' a template for a AvatarPropertiesRequest packet '''

    def __init__(self):
        self.name = 'AvatarPropertiesRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['AvatarID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarPropertiesRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], AvatarID = self.AgentData['AvatarID']))

class AgentGroupDataUpdatePacket(object):
    ''' a template for a AgentGroupDataUpdate packet '''

    def __init__(self):
        self.name = 'AgentGroupDataUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['GroupPowers'] = None    # MVT_U64
        self.GroupData['AcceptNotices'] = None    # MVT_BOOL
        self.GroupData['GroupInsigniaID'] = None    # MVT_LLUUID
        self.GroupData['Contribution'] = None    # MVT_S32
        self.GroupData['GroupName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentGroupDataUpdate', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('GroupData', GroupID = self.GroupData['GroupID'], GroupPowers = self.GroupData['GroupPowers'], AcceptNotices = self.GroupData['AcceptNotices'], GroupInsigniaID = self.GroupData['GroupInsigniaID'], Contribution = self.GroupData['Contribution'], GroupName = self.GroupData['GroupName']))

class DirLandQueryPacket(object):
    ''' a template for a DirLandQuery packet '''

    def __init__(self):
        self.name = 'DirLandQuery'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['QueryFlags'] = None    # MVT_U32
        self.QueryData['SearchType'] = None    # MVT_U32
        self.QueryData['Price'] = None    # MVT_S32
        self.QueryData['Area'] = None    # MVT_S32
        self.QueryData['QueryStart'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirLandQuery', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('QueryData', QueryID = self.QueryData['QueryID'], QueryFlags = self.QueryData['QueryFlags'], SearchType = self.QueryData['SearchType'], Price = self.QueryData['Price'], Area = self.QueryData['Area'], QueryStart = self.QueryData['QueryStart']))

class MoveInventoryItemPacket(object):
    ''' a template for a MoveInventoryItem packet '''

    def __init__(self):
        self.name = 'MoveInventoryItem'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['Stamp'] = None    # MVT_BOOL

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID
        self.InventoryData['FolderID'] = None    # MVT_LLUUID
        self.InventoryData['NewName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MoveInventoryItem', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], Stamp = self.AgentData['Stamp']), Block('InventoryData', ItemID = self.InventoryData['ItemID'], FolderID = self.InventoryData['FolderID'], NewName = self.InventoryData['NewName']))

class TeleportLandingStatusChangedPacket(object):
    ''' a template for a TeleportLandingStatusChanged packet '''

    def __init__(self):
        self.name = 'TeleportLandingStatusChanged'

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionHandle'] = None    # MVT_U64

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TeleportLandingStatusChanged', Block('RegionData', RegionHandle = self.RegionData['RegionHandle']))

class AvatarPickerRequestPacket(object):
    ''' a template for a AvatarPickerRequest packet '''

    def __init__(self):
        self.name = 'AvatarPickerRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['QueryID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['Name'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarPickerRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], QueryID = self.AgentData['QueryID']), Block('Data', Name = self.Data['Name']))

class AgentWearablesRequestPacket(object):
    ''' a template for a AgentWearablesRequest packet '''

    def __init__(self):
        self.name = 'AgentWearablesRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentWearablesRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class AvatarTextureUpdatePacket(object):
    ''' a template for a AvatarTextureUpdate packet '''

    def __init__(self):
        self.name = 'AvatarTextureUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['TexturesChanged'] = None    # MVT_BOOL

        self.WearableData = {}    # New WearableData block
        self.WearableData['CacheID'] = None    # MVT_LLUUID
        self.WearableData['TextureIndex'] = None    # MVT_U8
        self.WearableData['HostName'] = None    # MVT_VARIABLE

        self.TextureData = {}    # New TextureData block
        self.TextureData['TextureID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarTextureUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], TexturesChanged = self.AgentData['TexturesChanged']), Block('WearableData', CacheID = self.WearableData['CacheID'], TextureIndex = self.WearableData['TextureIndex'], HostName = self.WearableData['HostName']), Block('TextureData', TextureID = self.TextureData['TextureID']))

class GroupActiveProposalsRequestPacket(object):
    ''' a template for a GroupActiveProposalsRequest packet '''

    def __init__(self):
        self.name = 'GroupActiveProposalsRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID

        self.TransactionData = {}    # New TransactionData block
        self.TransactionData['TransactionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupActiveProposalsRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', GroupID = self.GroupData['GroupID']), Block('TransactionData', TransactionID = self.TransactionData['TransactionID']))

class UUIDGroupNameReplyPacket(object):
    ''' a template for a UUIDGroupNameReply packet '''

    def __init__(self):
        self.name = 'UUIDGroupNameReply'

        self.UUIDNameBlock = {}    # New UUIDNameBlock block
        self.UUIDNameBlock['ID'] = None    # MVT_LLUUID
        self.UUIDNameBlock['GroupName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UUIDGroupNameReply', Block('UUIDNameBlock', ID = self.UUIDNameBlock['ID'], GroupName = self.UUIDNameBlock['GroupName']))

class ObjectGrabPacket(object):
    ''' a template for a ObjectGrab packet '''

    def __init__(self):
        self.name = 'ObjectGrab'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['LocalID'] = None    # MVT_U32
        self.ObjectData['GrabOffset'] = None    # MVT_LLVector3

        self.SurfaceInfo = {}    # New SurfaceInfo block
        self.SurfaceInfo['UVCoord'] = None    # MVT_LLVector3
        self.SurfaceInfo['STCoord'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectGrab', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', LocalID = self.ObjectData['LocalID'], GrabOffset = self.ObjectData['GrabOffset']), Block('SurfaceInfo', UVCoord = self.SurfaceInfo['UVCoord'], STCoord = self.SurfaceInfo['STCoord']))

class AttachedSoundPacket(object):
    ''' a template for a AttachedSound packet '''

    def __init__(self):
        self.name = 'AttachedSound'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['SoundID'] = None    # MVT_LLUUID
        self.DataBlock['ObjectID'] = None    # MVT_LLUUID
        self.DataBlock['OwnerID'] = None    # MVT_LLUUID
        self.DataBlock['Gain'] = None    # MVT_F32
        self.DataBlock['Flags'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AttachedSound', Block('DataBlock', SoundID = self.DataBlock['SoundID'], ObjectID = self.DataBlock['ObjectID'], OwnerID = self.DataBlock['OwnerID'], Gain = self.DataBlock['Gain'], Flags = self.DataBlock['Flags']))

class ChangeUserRightsPacket(object):
    ''' a template for a ChangeUserRights packet '''

    def __init__(self):
        self.name = 'ChangeUserRights'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.Rights = {}    # New Rights block
        self.Rights['AgentRelated'] = None    # MVT_LLUUID
        self.Rights['RelatedRights'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ChangeUserRights', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('Rights', AgentRelated = self.Rights['AgentRelated'], RelatedRights = self.Rights['RelatedRights']))

class ParcelSetOtherCleanTimePacket(object):
    ''' a template for a ParcelSetOtherCleanTime packet '''

    def __init__(self):
        self.name = 'ParcelSetOtherCleanTime'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['LocalID'] = None    # MVT_S32
        self.ParcelData['OtherCleanTime'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelSetOtherCleanTime', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', LocalID = self.ParcelData['LocalID'], OtherCleanTime = self.ParcelData['OtherCleanTime']))

class ParcelMediaUpdatePacket(object):
    ''' a template for a ParcelMediaUpdate packet '''

    def __init__(self):
        self.name = 'ParcelMediaUpdate'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['MediaURL'] = None    # MVT_VARIABLE
        self.DataBlock['MediaID'] = None    # MVT_LLUUID
        self.DataBlock['MediaAutoScale'] = None    # MVT_U8

        self.DataBlockExtended = {}    # New DataBlockExtended block
        self.DataBlockExtended['MediaType'] = None    # MVT_VARIABLE
        self.DataBlockExtended['MediaDesc'] = None    # MVT_VARIABLE
        self.DataBlockExtended['MediaWidth'] = None    # MVT_S32
        self.DataBlockExtended['MediaHeight'] = None    # MVT_S32
        self.DataBlockExtended['MediaLoop'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelMediaUpdate', Block('DataBlock', MediaURL = self.DataBlock['MediaURL'], MediaID = self.DataBlock['MediaID'], MediaAutoScale = self.DataBlock['MediaAutoScale']), Block('DataBlockExtended', MediaType = self.DataBlockExtended['MediaType'], MediaDesc = self.DataBlockExtended['MediaDesc'], MediaWidth = self.DataBlockExtended['MediaWidth'], MediaHeight = self.DataBlockExtended['MediaHeight'], MediaLoop = self.DataBlockExtended['MediaLoop']))

class ObjectClickActionPacket(object):
    ''' a template for a ObjectClickAction packet '''

    def __init__(self):
        self.name = 'ObjectClickAction'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['ClickAction'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectClickAction', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], ClickAction = self.ObjectData['ClickAction']))

class FormFriendshipPacket(object):
    ''' a template for a FormFriendship packet '''

    def __init__(self):
        self.name = 'FormFriendship'

        self.AgentBlock = {}    # New AgentBlock block
        self.AgentBlock['SourceID'] = None    # MVT_LLUUID
        self.AgentBlock['DestID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('FormFriendship', Block('AgentBlock', SourceID = self.AgentBlock['SourceID'], DestID = self.AgentBlock['DestID']))

class AvatarPicksReplyPacket(object):
    ''' a template for a AvatarPicksReply packet '''

    def __init__(self):
        self.name = 'AvatarPicksReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['TargetID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['PickID'] = None    # MVT_LLUUID
        self.Data['PickName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarPicksReply', Block('AgentData', AgentID = self.AgentData['AgentID'], TargetID = self.AgentData['TargetID']), Block('Data', PickID = self.Data['PickID'], PickName = self.Data['PickName']))

class AgentSitPacket(object):
    ''' a template for a AgentSit packet '''

    def __init__(self):
        self.name = 'AgentSit'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentSit', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class CreateNewOutfitAttachmentsPacket(object):
    ''' a template for a CreateNewOutfitAttachments packet '''

    def __init__(self):
        self.name = 'CreateNewOutfitAttachments'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.HeaderData = {}    # New HeaderData block
        self.HeaderData['NewFolderID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['OldItemID'] = None    # MVT_LLUUID
        self.ObjectData['OldFolderID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CreateNewOutfitAttachments', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('HeaderData', NewFolderID = self.HeaderData['NewFolderID']), Block('ObjectData', OldItemID = self.ObjectData['OldItemID'], OldFolderID = self.ObjectData['OldFolderID']))

class ParcelObjectOwnersReplyPacket(object):
    ''' a template for a ParcelObjectOwnersReply packet '''

    def __init__(self):
        self.name = 'ParcelObjectOwnersReply'

        self.Data = {}    # New Data block
        self.Data['OwnerID'] = None    # MVT_LLUUID
        self.Data['IsGroupOwned'] = None    # MVT_BOOL
        self.Data['Count'] = None    # MVT_S32
        self.Data['OnlineStatus'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelObjectOwnersReply', Block('Data', OwnerID = self.Data['OwnerID'], IsGroupOwned = self.Data['IsGroupOwned'], Count = self.Data['Count'], OnlineStatus = self.Data['OnlineStatus']))

class FetchInventoryDescendentsPacket(object):
    ''' a template for a FetchInventoryDescendents packet '''

    def __init__(self):
        self.name = 'FetchInventoryDescendents'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['FolderID'] = None    # MVT_LLUUID
        self.InventoryData['OwnerID'] = None    # MVT_LLUUID
        self.InventoryData['SortOrder'] = None    # MVT_S32
        self.InventoryData['FetchFolders'] = None    # MVT_BOOL
        self.InventoryData['FetchItems'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('FetchInventoryDescendents', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('InventoryData', FolderID = self.InventoryData['FolderID'], OwnerID = self.InventoryData['OwnerID'], SortOrder = self.InventoryData['SortOrder'], FetchFolders = self.InventoryData['FetchFolders'], FetchItems = self.InventoryData['FetchItems']))

class RequestXferPacket(object):
    ''' a template for a RequestXfer packet '''

    def __init__(self):
        self.name = 'RequestXfer'

        self.XferID = {}    # New XferID block
        self.XferID['ID'] = None    # MVT_U64
        self.XferID['Filename'] = None    # MVT_VARIABLE
        self.XferID['FilePath'] = None    # MVT_U8
        self.XferID['DeleteOnCompletion'] = None    # MVT_BOOL
        self.XferID['UseBigPackets'] = None    # MVT_BOOL
        self.XferID['VFileID'] = None    # MVT_LLUUID
        self.XferID['VFileType'] = None    # MVT_S16

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RequestXfer', Block('XferID', ID = self.XferID['ID'], Filename = self.XferID['Filename'], FilePath = self.XferID['FilePath'], DeleteOnCompletion = self.XferID['DeleteOnCompletion'], UseBigPackets = self.XferID['UseBigPackets'], VFileID = self.XferID['VFileID'], VFileType = self.XferID['VFileType']))

class SoundTriggerPacket(object):
    ''' a template for a SoundTrigger packet '''

    def __init__(self):
        self.name = 'SoundTrigger'

        self.SoundData = {}    # New SoundData block
        self.SoundData['SoundID'] = None    # MVT_LLUUID
        self.SoundData['OwnerID'] = None    # MVT_LLUUID
        self.SoundData['ObjectID'] = None    # MVT_LLUUID
        self.SoundData['ParentID'] = None    # MVT_LLUUID
        self.SoundData['Handle'] = None    # MVT_U64
        self.SoundData['Position'] = None    # MVT_LLVector3
        self.SoundData['Gain'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SoundTrigger', Block('SoundData', SoundID = self.SoundData['SoundID'], OwnerID = self.SoundData['OwnerID'], ObjectID = self.SoundData['ObjectID'], ParentID = self.SoundData['ParentID'], Handle = self.SoundData['Handle'], Position = self.SoundData['Position'], Gain = self.SoundData['Gain']))

class DirPlacesReplyPacket(object):
    ''' a template for a DirPlacesReply packet '''

    def __init__(self):
        self.name = 'DirPlacesReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID

        self.QueryReplies = {}    # New QueryReplies block
        self.QueryReplies['ParcelID'] = None    # MVT_LLUUID
        self.QueryReplies['Name'] = None    # MVT_VARIABLE
        self.QueryReplies['ForSale'] = None    # MVT_BOOL
        self.QueryReplies['Auction'] = None    # MVT_BOOL
        self.QueryReplies['Dwell'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirPlacesReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID']), Block('QueryReplies', ParcelID = self.QueryReplies['ParcelID'], Name = self.QueryReplies['Name'], ForSale = self.QueryReplies['ForSale'], Auction = self.QueryReplies['Auction'], Dwell = self.QueryReplies['Dwell']))

class AlertMessagePacket(object):
    ''' a template for a AlertMessage packet '''

    def __init__(self):
        self.name = 'AlertMessage'

        self.AlertData = {}    # New AlertData block
        self.AlertData['Message'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AlertMessage', Block('AlertData', Message = self.AlertData['Message']))

class SimulatorShutdownRequestPacket(object):
    ''' a template for a SimulatorShutdownRequest packet '''

    def __init__(self):
        self.name = 'SimulatorShutdownRequest'

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SimulatorShutdownRequest')

class GroupProfileReplyPacket(object):
    ''' a template for a GroupProfileReply packet '''

    def __init__(self):
        self.name = 'GroupProfileReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['Name'] = None    # MVT_VARIABLE
        self.GroupData['Charter'] = None    # MVT_VARIABLE
        self.GroupData['ShowInList'] = None    # MVT_BOOL
        self.GroupData['MemberTitle'] = None    # MVT_VARIABLE
        self.GroupData['PowersMask'] = None    # MVT_U64
        self.GroupData['InsigniaID'] = None    # MVT_LLUUID
        self.GroupData['FounderID'] = None    # MVT_LLUUID
        self.GroupData['MembershipFee'] = None    # MVT_S32
        self.GroupData['OpenEnrollment'] = None    # MVT_BOOL
        self.GroupData['Money'] = None    # MVT_S32
        self.GroupData['GroupMembershipCount'] = None    # MVT_S32
        self.GroupData['GroupRolesCount'] = None    # MVT_S32
        self.GroupData['AllowPublish'] = None    # MVT_BOOL
        self.GroupData['MaturePublish'] = None    # MVT_BOOL
        self.GroupData['OwnerRole'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupProfileReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('GroupData', GroupID = self.GroupData['GroupID'], Name = self.GroupData['Name'], Charter = self.GroupData['Charter'], ShowInList = self.GroupData['ShowInList'], MemberTitle = self.GroupData['MemberTitle'], PowersMask = self.GroupData['PowersMask'], InsigniaID = self.GroupData['InsigniaID'], FounderID = self.GroupData['FounderID'], MembershipFee = self.GroupData['MembershipFee'], OpenEnrollment = self.GroupData['OpenEnrollment'], Money = self.GroupData['Money'], GroupMembershipCount = self.GroupData['GroupMembershipCount'], GroupRolesCount = self.GroupData['GroupRolesCount'], AllowPublish = self.GroupData['AllowPublish'], MaturePublish = self.GroupData['MaturePublish'], OwnerRole = self.GroupData['OwnerRole']))

class ScriptSensorRequestPacket(object):
    ''' a template for a ScriptSensorRequest packet '''

    def __init__(self):
        self.name = 'ScriptSensorRequest'

        self.Requester = {}    # New Requester block
        self.Requester['SourceID'] = None    # MVT_LLUUID
        self.Requester['RequestID'] = None    # MVT_LLUUID
        self.Requester['SearchID'] = None    # MVT_LLUUID
        self.Requester['SearchPos'] = None    # MVT_LLVector3
        self.Requester['SearchDir'] = None    # MVT_LLQuaternion
        self.Requester['SearchName'] = None    # MVT_VARIABLE
        self.Requester['Type'] = None    # MVT_S32
        self.Requester['Range'] = None    # MVT_F32
        self.Requester['Arc'] = None    # MVT_F32
        self.Requester['RegionHandle'] = None    # MVT_U64
        self.Requester['SearchRegions'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptSensorRequest', Block('Requester', SourceID = self.Requester['SourceID'], RequestID = self.Requester['RequestID'], SearchID = self.Requester['SearchID'], SearchPos = self.Requester['SearchPos'], SearchDir = self.Requester['SearchDir'], SearchName = self.Requester['SearchName'], Type = self.Requester['Type'], Range = self.Requester['Range'], Arc = self.Requester['Arc'], RegionHandle = self.Requester['RegionHandle'], SearchRegions = self.Requester['SearchRegions']))

class VelocityInterpolateOffPacket(object):
    ''' a template for a VelocityInterpolateOff packet '''

    def __init__(self):
        self.name = 'VelocityInterpolateOff'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('VelocityInterpolateOff', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class RemoveNameValuePairPacket(object):
    ''' a template for a RemoveNameValuePair packet '''

    def __init__(self):
        self.name = 'RemoveNameValuePair'

        self.TaskData = {}    # New TaskData block
        self.TaskData['ID'] = None    # MVT_LLUUID

        self.NameValueData = {}    # New NameValueData block
        self.NameValueData['NVPair'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RemoveNameValuePair', Block('TaskData', ID = self.TaskData['ID']), Block('NameValueData', NVPair = self.NameValueData['NVPair']))

class ParcelClaimPacket(object):
    ''' a template for a ParcelClaim packet '''

    def __init__(self):
        self.name = 'ParcelClaim'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['GroupID'] = None    # MVT_LLUUID
        self.Data['IsGroupOwned'] = None    # MVT_BOOL
        self.Data['Final'] = None    # MVT_BOOL

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['West'] = None    # MVT_F32
        self.ParcelData['South'] = None    # MVT_F32
        self.ParcelData['East'] = None    # MVT_F32
        self.ParcelData['North'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelClaim', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', GroupID = self.Data['GroupID'], IsGroupOwned = self.Data['IsGroupOwned'], Final = self.Data['Final']), Block('ParcelData', West = self.ParcelData['West'], South = self.ParcelData['South'], East = self.ParcelData['East'], North = self.ParcelData['North']))

class SetAlwaysRunPacket(object):
    ''' a template for a SetAlwaysRun packet '''

    def __init__(self):
        self.name = 'SetAlwaysRun'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['AlwaysRun'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SetAlwaysRun', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], AlwaysRun = self.AgentData['AlwaysRun']))

class EventLocationReplyPacket(object):
    ''' a template for a EventLocationReply packet '''

    def __init__(self):
        self.name = 'EventLocationReply'

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID

        self.EventData = {}    # New EventData block
        self.EventData['Success'] = None    # MVT_BOOL
        self.EventData['RegionID'] = None    # MVT_LLUUID
        self.EventData['RegionPos'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EventLocationReply', Block('QueryData', QueryID = self.QueryData['QueryID']), Block('EventData', Success = self.EventData['Success'], RegionID = self.EventData['RegionID'], RegionPos = self.EventData['RegionPos']))

class PickGodDeletePacket(object):
    ''' a template for a PickGodDelete packet '''

    def __init__(self):
        self.name = 'PickGodDelete'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['PickID'] = None    # MVT_LLUUID
        self.Data['QueryID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('PickGodDelete', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', PickID = self.Data['PickID'], QueryID = self.Data['QueryID']))

class MapBlockRequestPacket(object):
    ''' a template for a MapBlockRequest packet '''

    def __init__(self):
        self.name = 'MapBlockRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['Flags'] = None    # MVT_U32
        self.AgentData['EstateID'] = None    # MVT_U32
        self.AgentData['Godlike'] = None    # MVT_BOOL

        self.PositionData = {}    # New PositionData block
        self.PositionData['MinX'] = None    # MVT_U16
        self.PositionData['MaxX'] = None    # MVT_U16
        self.PositionData['MinY'] = None    # MVT_U16
        self.PositionData['MaxY'] = None    # MVT_U16

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MapBlockRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], Flags = self.AgentData['Flags'], EstateID = self.AgentData['EstateID'], Godlike = self.AgentData['Godlike']), Block('PositionData', MinX = self.PositionData['MinX'], MaxX = self.PositionData['MaxX'], MinY = self.PositionData['MinY'], MaxY = self.PositionData['MaxY']))

class TeleportProgressPacket(object):
    ''' a template for a TeleportProgress packet '''

    def __init__(self):
        self.name = 'TeleportProgress'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.Info = {}    # New Info block
        self.Info['TeleportFlags'] = None    # MVT_U32
        self.Info['Message'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TeleportProgress', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('Info', TeleportFlags = self.Info['TeleportFlags'], Message = self.Info['Message']))

class UpdateTaskInventoryPacket(object):
    ''' a template for a UpdateTaskInventory packet '''

    def __init__(self):
        self.name = 'UpdateTaskInventory'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.UpdateData = {}    # New UpdateData block
        self.UpdateData['LocalID'] = None    # MVT_U32
        self.UpdateData['Key'] = None    # MVT_U8

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID
        self.InventoryData['FolderID'] = None    # MVT_LLUUID
        self.InventoryData['CreatorID'] = None    # MVT_LLUUID
        self.InventoryData['OwnerID'] = None    # MVT_LLUUID
        self.InventoryData['GroupID'] = None    # MVT_LLUUID
        self.InventoryData['BaseMask'] = None    # MVT_U32
        self.InventoryData['OwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupMask'] = None    # MVT_U32
        self.InventoryData['EveryoneMask'] = None    # MVT_U32
        self.InventoryData['NextOwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupOwned'] = None    # MVT_BOOL
        self.InventoryData['TransactionID'] = None    # MVT_LLUUID
        self.InventoryData['Type'] = None    # MVT_S8
        self.InventoryData['InvType'] = None    # MVT_S8
        self.InventoryData['Flags'] = None    # MVT_U32
        self.InventoryData['SaleType'] = None    # MVT_U8
        self.InventoryData['SalePrice'] = None    # MVT_S32
        self.InventoryData['Name'] = None    # MVT_VARIABLE
        self.InventoryData['Description'] = None    # MVT_VARIABLE
        self.InventoryData['CreationDate'] = None    # MVT_S32
        self.InventoryData['CRC'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UpdateTaskInventory', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('UpdateData', LocalID = self.UpdateData['LocalID'], Key = self.UpdateData['Key']), Block('InventoryData', ItemID = self.InventoryData['ItemID'], FolderID = self.InventoryData['FolderID'], CreatorID = self.InventoryData['CreatorID'], OwnerID = self.InventoryData['OwnerID'], GroupID = self.InventoryData['GroupID'], BaseMask = self.InventoryData['BaseMask'], OwnerMask = self.InventoryData['OwnerMask'], GroupMask = self.InventoryData['GroupMask'], EveryoneMask = self.InventoryData['EveryoneMask'], NextOwnerMask = self.InventoryData['NextOwnerMask'], GroupOwned = self.InventoryData['GroupOwned'], TransactionID = self.InventoryData['TransactionID'], Type = self.InventoryData['Type'], InvType = self.InventoryData['InvType'], Flags = self.InventoryData['Flags'], SaleType = self.InventoryData['SaleType'], SalePrice = self.InventoryData['SalePrice'], Name = self.InventoryData['Name'], Description = self.InventoryData['Description'], CreationDate = self.InventoryData['CreationDate'], CRC = self.InventoryData['CRC']))

class GodKickUserPacket(object):
    ''' a template for a GodKickUser packet '''

    def __init__(self):
        self.name = 'GodKickUser'

        self.UserInfo = {}    # New UserInfo block
        self.UserInfo['GodID'] = None    # MVT_LLUUID
        self.UserInfo['GodSessionID'] = None    # MVT_LLUUID
        self.UserInfo['AgentID'] = None    # MVT_LLUUID
        self.UserInfo['KickFlags'] = None    # MVT_U32
        self.UserInfo['Reason'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GodKickUser', Block('UserInfo', GodID = self.UserInfo['GodID'], GodSessionID = self.UserInfo['GodSessionID'], AgentID = self.UserInfo['AgentID'], KickFlags = self.UserInfo['KickFlags'], Reason = self.UserInfo['Reason']))

class AvatarAnimationPacket(object):
    ''' a template for a AvatarAnimation packet '''

    def __init__(self):
        self.name = 'AvatarAnimation'

        self.Sender = {}    # New Sender block
        self.Sender['ID'] = None    # MVT_LLUUID

        self.AnimationList = {}    # New AnimationList block
        self.AnimationList['AnimID'] = None    # MVT_LLUUID
        self.AnimationList['AnimSequenceID'] = None    # MVT_S32

        self.AnimationSourceList = {}    # New AnimationSourceList block
        self.AnimationSourceList['ObjectID'] = None    # MVT_LLUUID

        self.PhysicalAvatarEventList = {}    # New PhysicalAvatarEventList block
        self.PhysicalAvatarEventList['TypeData'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarAnimation', Block('Sender', ID = self.Sender['ID']), Block('AnimationList', AnimID = self.AnimationList['AnimID'], AnimSequenceID = self.AnimationList['AnimSequenceID']), Block('AnimationSourceList', ObjectID = self.AnimationSourceList['ObjectID']), Block('PhysicalAvatarEventList', TypeData = self.PhysicalAvatarEventList['TypeData']))

class ClassifiedInfoReplyPacket(object):
    ''' a template for a ClassifiedInfoReply packet '''

    def __init__(self):
        self.name = 'ClassifiedInfoReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['ClassifiedID'] = None    # MVT_LLUUID
        self.Data['CreatorID'] = None    # MVT_LLUUID
        self.Data['CreationDate'] = None    # MVT_U32
        self.Data['ExpirationDate'] = None    # MVT_U32
        self.Data['Category'] = None    # MVT_U32
        self.Data['Name'] = None    # MVT_VARIABLE
        self.Data['Desc'] = None    # MVT_VARIABLE
        self.Data['ParcelID'] = None    # MVT_LLUUID
        self.Data['ParentEstate'] = None    # MVT_U32
        self.Data['SnapshotID'] = None    # MVT_LLUUID
        self.Data['SimName'] = None    # MVT_VARIABLE
        self.Data['PosGlobal'] = None    # MVT_LLVector3d
        self.Data['ParcelName'] = None    # MVT_VARIABLE
        self.Data['ClassifiedFlags'] = None    # MVT_U8
        self.Data['PriceForListing'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ClassifiedInfoReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('Data', ClassifiedID = self.Data['ClassifiedID'], CreatorID = self.Data['CreatorID'], CreationDate = self.Data['CreationDate'], ExpirationDate = self.Data['ExpirationDate'], Category = self.Data['Category'], Name = self.Data['Name'], Desc = self.Data['Desc'], ParcelID = self.Data['ParcelID'], ParentEstate = self.Data['ParentEstate'], SnapshotID = self.Data['SnapshotID'], SimName = self.Data['SimName'], PosGlobal = self.Data['PosGlobal'], ParcelName = self.Data['ParcelName'], ClassifiedFlags = self.Data['ClassifiedFlags'], PriceForListing = self.Data['PriceForListing']))

class GodUpdateRegionInfoPacket(object):
    ''' a template for a GodUpdateRegionInfo packet '''

    def __init__(self):
        self.name = 'GodUpdateRegionInfo'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.RegionInfo = {}    # New RegionInfo block
        self.RegionInfo['SimName'] = None    # MVT_VARIABLE
        self.RegionInfo['EstateID'] = None    # MVT_U32
        self.RegionInfo['ParentEstateID'] = None    # MVT_U32
        self.RegionInfo['RegionFlags'] = None    # MVT_U32
        self.RegionInfo['BillableFactor'] = None    # MVT_F32
        self.RegionInfo['PricePerMeter'] = None    # MVT_S32
        self.RegionInfo['RedirectGridX'] = None    # MVT_S32
        self.RegionInfo['RedirectGridY'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GodUpdateRegionInfo', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('RegionInfo', SimName = self.RegionInfo['SimName'], EstateID = self.RegionInfo['EstateID'], ParentEstateID = self.RegionInfo['ParentEstateID'], RegionFlags = self.RegionInfo['RegionFlags'], BillableFactor = self.RegionInfo['BillableFactor'], PricePerMeter = self.RegionInfo['PricePerMeter'], RedirectGridX = self.RegionInfo['RedirectGridX'], RedirectGridY = self.RegionInfo['RedirectGridY']))

class SetSimStatusInDatabasePacket(object):
    ''' a template for a SetSimStatusInDatabase packet '''

    def __init__(self):
        self.name = 'SetSimStatusInDatabase'

        self.Data = {}    # New Data block
        self.Data['RegionID'] = None    # MVT_LLUUID
        self.Data['HostName'] = None    # MVT_VARIABLE
        self.Data['X'] = None    # MVT_S32
        self.Data['Y'] = None    # MVT_S32
        self.Data['PID'] = None    # MVT_S32
        self.Data['AgentCount'] = None    # MVT_S32
        self.Data['TimeToLive'] = None    # MVT_S32
        self.Data['Status'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SetSimStatusInDatabase', Block('Data', RegionID = self.Data['RegionID'], HostName = self.Data['HostName'], X = self.Data['X'], Y = self.Data['Y'], PID = self.Data['PID'], AgentCount = self.Data['AgentCount'], TimeToLive = self.Data['TimeToLive'], Status = self.Data['Status']))

class GroupVoteHistoryRequestPacket(object):
    ''' a template for a GroupVoteHistoryRequest packet '''

    def __init__(self):
        self.name = 'GroupVoteHistoryRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID

        self.TransactionData = {}    # New TransactionData block
        self.TransactionData['TransactionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupVoteHistoryRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', GroupID = self.GroupData['GroupID']), Block('TransactionData', TransactionID = self.TransactionData['TransactionID']))

class ChildAgentDyingPacket(object):
    ''' a template for a ChildAgentDying packet '''

    def __init__(self):
        self.name = 'ChildAgentDying'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ChildAgentDying', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class CreateGroupRequestPacket(object):
    ''' a template for a CreateGroupRequest packet '''

    def __init__(self):
        self.name = 'CreateGroupRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['Name'] = None    # MVT_VARIABLE
        self.GroupData['Charter'] = None    # MVT_VARIABLE
        self.GroupData['ShowInList'] = None    # MVT_BOOL
        self.GroupData['InsigniaID'] = None    # MVT_LLUUID
        self.GroupData['MembershipFee'] = None    # MVT_S32
        self.GroupData['OpenEnrollment'] = None    # MVT_BOOL
        self.GroupData['AllowPublish'] = None    # MVT_BOOL
        self.GroupData['MaturePublish'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CreateGroupRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', Name = self.GroupData['Name'], Charter = self.GroupData['Charter'], ShowInList = self.GroupData['ShowInList'], InsigniaID = self.GroupData['InsigniaID'], MembershipFee = self.GroupData['MembershipFee'], OpenEnrollment = self.GroupData['OpenEnrollment'], AllowPublish = self.GroupData['AllowPublish'], MaturePublish = self.GroupData['MaturePublish']))

class ParcelDwellRequestPacket(object):
    ''' a template for a ParcelDwellRequest packet '''

    def __init__(self):
        self.name = 'ParcelDwellRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['LocalID'] = None    # MVT_S32
        self.Data['ParcelID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelDwellRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', LocalID = self.Data['LocalID'], ParcelID = self.Data['ParcelID']))

class ObjectMaterialPacket(object):
    ''' a template for a ObjectMaterial packet '''

    def __init__(self):
        self.name = 'ObjectMaterial'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['Material'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectMaterial', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], Material = self.ObjectData['Material']))

class ObjectAddPacket(object):
    ''' a template for a ObjectAdd packet '''

    def __init__(self):
        self.name = 'ObjectAdd'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['PCode'] = None    # MVT_U8
        self.ObjectData['Material'] = None    # MVT_U8
        self.ObjectData['AddFlags'] = None    # MVT_U32
        self.ObjectData['PathCurve'] = None    # MVT_U8
        self.ObjectData['ProfileCurve'] = None    # MVT_U8
        self.ObjectData['PathBegin'] = None    # MVT_U16
        self.ObjectData['PathEnd'] = None    # MVT_U16
        self.ObjectData['PathScaleX'] = None    # MVT_U8
        self.ObjectData['PathScaleY'] = None    # MVT_U8
        self.ObjectData['PathShearX'] = None    # MVT_U8
        self.ObjectData['PathShearY'] = None    # MVT_U8
        self.ObjectData['PathTwist'] = None    # MVT_S8
        self.ObjectData['PathTwistBegin'] = None    # MVT_S8
        self.ObjectData['PathRadiusOffset'] = None    # MVT_S8
        self.ObjectData['PathTaperX'] = None    # MVT_S8
        self.ObjectData['PathTaperY'] = None    # MVT_S8
        self.ObjectData['PathRevolutions'] = None    # MVT_U8
        self.ObjectData['PathSkew'] = None    # MVT_S8
        self.ObjectData['ProfileBegin'] = None    # MVT_U16
        self.ObjectData['ProfileEnd'] = None    # MVT_U16
        self.ObjectData['ProfileHollow'] = None    # MVT_U16
        self.ObjectData['BypassRaycast'] = None    # MVT_U8
        self.ObjectData['RayStart'] = None    # MVT_LLVector3
        self.ObjectData['RayEnd'] = None    # MVT_LLVector3
        self.ObjectData['RayTargetID'] = None    # MVT_LLUUID
        self.ObjectData['RayEndIsIntersection'] = None    # MVT_U8
        self.ObjectData['Scale'] = None    # MVT_LLVector3
        self.ObjectData['Rotation'] = None    # MVT_LLQuaternion
        self.ObjectData['State'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectAdd', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('ObjectData', PCode = self.ObjectData['PCode'], Material = self.ObjectData['Material'], AddFlags = self.ObjectData['AddFlags'], PathCurve = self.ObjectData['PathCurve'], ProfileCurve = self.ObjectData['ProfileCurve'], PathBegin = self.ObjectData['PathBegin'], PathEnd = self.ObjectData['PathEnd'], PathScaleX = self.ObjectData['PathScaleX'], PathScaleY = self.ObjectData['PathScaleY'], PathShearX = self.ObjectData['PathShearX'], PathShearY = self.ObjectData['PathShearY'], PathTwist = self.ObjectData['PathTwist'], PathTwistBegin = self.ObjectData['PathTwistBegin'], PathRadiusOffset = self.ObjectData['PathRadiusOffset'], PathTaperX = self.ObjectData['PathTaperX'], PathTaperY = self.ObjectData['PathTaperY'], PathRevolutions = self.ObjectData['PathRevolutions'], PathSkew = self.ObjectData['PathSkew'], ProfileBegin = self.ObjectData['ProfileBegin'], ProfileEnd = self.ObjectData['ProfileEnd'], ProfileHollow = self.ObjectData['ProfileHollow'], BypassRaycast = self.ObjectData['BypassRaycast'], RayStart = self.ObjectData['RayStart'], RayEnd = self.ObjectData['RayEnd'], RayTargetID = self.ObjectData['RayTargetID'], RayEndIsIntersection = self.ObjectData['RayEndIsIntersection'], Scale = self.ObjectData['Scale'], Rotation = self.ObjectData['Rotation'], State = self.ObjectData['State']))

class DeactivateGesturesPacket(object):
    ''' a template for a DeactivateGestures packet '''

    def __init__(self):
        self.name = 'DeactivateGestures'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['Flags'] = None    # MVT_U32

        self.Data = {}    # New Data block
        self.Data['ItemID'] = None    # MVT_LLUUID
        self.Data['GestureFlags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DeactivateGestures', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], Flags = self.AgentData['Flags']), Block('Data', ItemID = self.Data['ItemID'], GestureFlags = self.Data['GestureFlags']))

class ParcelOverlayPacket(object):
    ''' a template for a ParcelOverlay packet '''

    def __init__(self):
        self.name = 'ParcelOverlay'

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['SequenceID'] = None    # MVT_S32
        self.ParcelData['Data'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelOverlay', Block('ParcelData', SequenceID = self.ParcelData['SequenceID'], Data = self.ParcelData['Data']))

class UserInfoReplyPacket(object):
    ''' a template for a UserInfoReply packet '''

    def __init__(self):
        self.name = 'UserInfoReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.UserData = {}    # New UserData block
        self.UserData['IMViaEMail'] = None    # MVT_BOOL
        self.UserData['DirectoryVisibility'] = None    # MVT_VARIABLE
        self.UserData['EMail'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UserInfoReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('UserData', IMViaEMail = self.UserData['IMViaEMail'], DirectoryVisibility = self.UserData['DirectoryVisibility'], EMail = self.UserData['EMail']))

class UndoPacket(object):
    ''' a template for a Undo packet '''

    def __init__(self):
        self.name = 'Undo'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('Undo', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('ObjectData', ObjectID = self.ObjectData['ObjectID']))

class TransferInventoryPacket(object):
    ''' a template for a TransferInventory packet '''

    def __init__(self):
        self.name = 'TransferInventory'

        self.InfoBlock = {}    # New InfoBlock block
        self.InfoBlock['SourceID'] = None    # MVT_LLUUID
        self.InfoBlock['DestID'] = None    # MVT_LLUUID
        self.InfoBlock['TransactionID'] = None    # MVT_LLUUID

        self.InventoryBlock = {}    # New InventoryBlock block
        self.InventoryBlock['InventoryID'] = None    # MVT_LLUUID
        self.InventoryBlock['Type'] = None    # MVT_S8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TransferInventory', Block('InfoBlock', SourceID = self.InfoBlock['SourceID'], DestID = self.InfoBlock['DestID'], TransactionID = self.InfoBlock['TransactionID']), Block('InventoryBlock', InventoryID = self.InventoryBlock['InventoryID'], Type = self.InventoryBlock['Type']))

class AvatarPropertiesUpdatePacket(object):
    ''' a template for a AvatarPropertiesUpdate packet '''

    def __init__(self):
        self.name = 'AvatarPropertiesUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.PropertiesData = {}    # New PropertiesData block
        self.PropertiesData['ImageID'] = None    # MVT_LLUUID
        self.PropertiesData['FLImageID'] = None    # MVT_LLUUID
        self.PropertiesData['AboutText'] = None    # MVT_VARIABLE
        self.PropertiesData['FLAboutText'] = None    # MVT_VARIABLE
        self.PropertiesData['AllowPublish'] = None    # MVT_BOOL
        self.PropertiesData['MaturePublish'] = None    # MVT_BOOL
        self.PropertiesData['ProfileURL'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarPropertiesUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('PropertiesData', ImageID = self.PropertiesData['ImageID'], FLImageID = self.PropertiesData['FLImageID'], AboutText = self.PropertiesData['AboutText'], FLAboutText = self.PropertiesData['FLAboutText'], AllowPublish = self.PropertiesData['AllowPublish'], MaturePublish = self.PropertiesData['MaturePublish'], ProfileURL = self.PropertiesData['ProfileURL']))

class LayerDataPacket(object):
    ''' a template for a LayerData packet '''

    def __init__(self):
        self.name = 'LayerData'

        self.LayerID = {}    # New LayerID block
        self.LayerID['Type'] = None    # MVT_U8

        self.LayerData = {}    # New LayerData block
        self.LayerData['Data'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LayerData', Block('LayerID', Type = self.LayerID['Type']), Block('LayerData', Data = self.LayerData['Data']))

class DirPopularReplyPacket(object):
    ''' a template for a DirPopularReply packet '''

    def __init__(self):
        self.name = 'DirPopularReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID

        self.QueryReplies = {}    # New QueryReplies block
        self.QueryReplies['ParcelID'] = None    # MVT_LLUUID
        self.QueryReplies['Name'] = None    # MVT_VARIABLE
        self.QueryReplies['Dwell'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirPopularReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID']), Block('QueryReplies', ParcelID = self.QueryReplies['ParcelID'], Name = self.QueryReplies['Name'], Dwell = self.QueryReplies['Dwell']))

class RequestGodlikePowersPacket(object):
    ''' a template for a RequestGodlikePowers packet '''

    def __init__(self):
        self.name = 'RequestGodlikePowers'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.RequestBlock = {}    # New RequestBlock block
        self.RequestBlock['Godlike'] = None    # MVT_BOOL
        self.RequestBlock['Token'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RequestGodlikePowers', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('RequestBlock', Godlike = self.RequestBlock['Godlike'], Token = self.RequestBlock['Token']))

class MeanCollisionAlertPacket(object):
    ''' a template for a MeanCollisionAlert packet '''

    def __init__(self):
        self.name = 'MeanCollisionAlert'

        self.MeanCollision = {}    # New MeanCollision block
        self.MeanCollision['Victim'] = None    # MVT_LLUUID
        self.MeanCollision['Perp'] = None    # MVT_LLUUID
        self.MeanCollision['Time'] = None    # MVT_U32
        self.MeanCollision['Mag'] = None    # MVT_F32
        self.MeanCollision['Type'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MeanCollisionAlert', Block('MeanCollision', Victim = self.MeanCollision['Victim'], Perp = self.MeanCollision['Perp'], Time = self.MeanCollision['Time'], Mag = self.MeanCollision['Mag'], Type = self.MeanCollision['Type']))

class DirFindQueryPacket(object):
    ''' a template for a DirFindQuery packet '''

    def __init__(self):
        self.name = 'DirFindQuery'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['QueryText'] = None    # MVT_VARIABLE
        self.QueryData['QueryFlags'] = None    # MVT_U32
        self.QueryData['QueryStart'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirFindQuery', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('QueryData', QueryID = self.QueryData['QueryID'], QueryText = self.QueryData['QueryText'], QueryFlags = self.QueryData['QueryFlags'], QueryStart = self.QueryData['QueryStart']))

class SetGroupAcceptNoticesPacket(object):
    ''' a template for a SetGroupAcceptNotices packet '''

    def __init__(self):
        self.name = 'SetGroupAcceptNotices'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['GroupID'] = None    # MVT_LLUUID
        self.Data['AcceptNotices'] = None    # MVT_BOOL

        self.NewData = {}    # New NewData block
        self.NewData['ListInProfile'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SetGroupAcceptNotices', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', GroupID = self.Data['GroupID'], AcceptNotices = self.Data['AcceptNotices']), Block('NewData', ListInProfile = self.NewData['ListInProfile']))

class CompleteAgentMovementPacket(object):
    ''' a template for a CompleteAgentMovement packet '''

    def __init__(self):
        self.name = 'CompleteAgentMovement'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['CircuitCode'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CompleteAgentMovement', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], CircuitCode = self.AgentData['CircuitCode']))

class LeaveGroupReplyPacket(object):
    ''' a template for a LeaveGroupReply packet '''

    def __init__(self):
        self.name = 'LeaveGroupReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['Success'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LeaveGroupReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('GroupData', GroupID = self.GroupData['GroupID'], Success = self.GroupData['Success']))

class ParcelGodMarkAsContentPacket(object):
    ''' a template for a ParcelGodMarkAsContent packet '''

    def __init__(self):
        self.name = 'ParcelGodMarkAsContent'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['LocalID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelGodMarkAsContent', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', LocalID = self.ParcelData['LocalID']))

class ObjectSaleInfoPacket(object):
    ''' a template for a ObjectSaleInfo packet '''

    def __init__(self):
        self.name = 'ObjectSaleInfo'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['LocalID'] = None    # MVT_U32
        self.ObjectData['SaleType'] = None    # MVT_U8
        self.ObjectData['SalePrice'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectSaleInfo', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', LocalID = self.ObjectData['LocalID'], SaleType = self.ObjectData['SaleType'], SalePrice = self.ObjectData['SalePrice']))

class CoarseLocationUpdatePacket(object):
    ''' a template for a CoarseLocationUpdate packet '''

    def __init__(self):
        self.name = 'CoarseLocationUpdate'

        self.Location = {}    # New Location block
        self.Location['X'] = None    # MVT_U8
        self.Location['Y'] = None    # MVT_U8
        self.Location['Z'] = None    # MVT_U8

        self.Index = {}    # New Index block
        self.Index['You'] = None    # MVT_S16
        self.Index['Prey'] = None    # MVT_S16

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CoarseLocationUpdate', Block('Location', X = self.Location['X'], Y = self.Location['Y'], Z = self.Location['Z']), Block('Index', You = self.Index['You'], Prey = self.Index['Prey']), Block('AgentData', AgentID = self.AgentData['AgentID']))

class NetTestPacket(object):
    ''' a template for a NetTest packet '''

    def __init__(self):
        self.name = 'NetTest'

        self.NetBlock = {}    # New NetBlock block
        self.NetBlock['Port'] = None    # MVT_IP_PORT

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('NetTest', Block('NetBlock', Port = self.NetBlock['Port']))

class ForceObjectSelectPacket(object):
    ''' a template for a ForceObjectSelect packet '''

    def __init__(self):
        self.name = 'ForceObjectSelect'

        self.Header = {}    # New Header block
        self.Header['ResetList'] = None    # MVT_BOOL

        self.Data = {}    # New Data block
        self.Data['LocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ForceObjectSelect', Block('Header', ResetList = self.Header['ResetList']), Block('Data', LocalID = self.Data['LocalID']))

class MapBlockReplyPacket(object):
    ''' a template for a MapBlockReply packet '''

    def __init__(self):
        self.name = 'MapBlockReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['Flags'] = None    # MVT_U32

        self.Data = {}    # New Data block
        self.Data['X'] = None    # MVT_U16
        self.Data['Y'] = None    # MVT_U16
        self.Data['Name'] = None    # MVT_VARIABLE
        self.Data['Access'] = None    # MVT_U8
        self.Data['RegionFlags'] = None    # MVT_U32
        self.Data['WaterHeight'] = None    # MVT_U8
        self.Data['Agents'] = None    # MVT_U8
        self.Data['MapImageID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MapBlockReply', Block('AgentData', AgentID = self.AgentData['AgentID'], Flags = self.AgentData['Flags']), Block('Data', X = self.Data['X'], Y = self.Data['Y'], Name = self.Data['Name'], Access = self.Data['Access'], RegionFlags = self.Data['RegionFlags'], WaterHeight = self.Data['WaterHeight'], Agents = self.Data['Agents'], MapImageID = self.Data['MapImageID']))

class AgentSetAppearancePacket(object):
    ''' a template for a AgentSetAppearance packet '''

    def __init__(self):
        self.name = 'AgentSetAppearance'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['SerialNum'] = None    # MVT_U32
        self.AgentData['Size'] = None    # MVT_LLVector3

        self.WearableData = {}    # New WearableData block
        self.WearableData['CacheID'] = None    # MVT_LLUUID
        self.WearableData['TextureIndex'] = None    # MVT_U8

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['TextureEntry'] = None    # MVT_VARIABLE

        self.VisualParam = {}    # New VisualParam block
        self.VisualParam['ParamValue'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentSetAppearance', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], SerialNum = self.AgentData['SerialNum'], Size = self.AgentData['Size']), Block('WearableData', CacheID = self.WearableData['CacheID'], TextureIndex = self.WearableData['TextureIndex']), Block('ObjectData', TextureEntry = self.ObjectData['TextureEntry']), Block('VisualParam', ParamValue = self.VisualParam['ParamValue']))

class MoveTaskInventoryPacket(object):
    ''' a template for a MoveTaskInventory packet '''

    def __init__(self):
        self.name = 'MoveTaskInventory'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['FolderID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['LocalID'] = None    # MVT_U32
        self.InventoryData['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MoveTaskInventory', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], FolderID = self.AgentData['FolderID']), Block('InventoryData', LocalID = self.InventoryData['LocalID'], ItemID = self.InventoryData['ItemID']))

class EventGodDeletePacket(object):
    ''' a template for a EventGodDelete packet '''

    def __init__(self):
        self.name = 'EventGodDelete'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.EventData = {}    # New EventData block
        self.EventData['EventID'] = None    # MVT_U32

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['QueryText'] = None    # MVT_VARIABLE
        self.QueryData['QueryFlags'] = None    # MVT_U32
        self.QueryData['QueryStart'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EventGodDelete', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('EventData', EventID = self.EventData['EventID']), Block('QueryData', QueryID = self.QueryData['QueryID'], QueryText = self.QueryData['QueryText'], QueryFlags = self.QueryData['QueryFlags'], QueryStart = self.QueryData['QueryStart']))

class CompletePingCheckPacket(object):
    ''' a template for a CompletePingCheck packet '''

    def __init__(self):
        self.name = 'CompletePingCheck'

        self.PingID = {}    # New PingID block
        self.PingID['PingID'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CompletePingCheck', Block('PingID', PingID = self.PingID['PingID']))

class AgentDataUpdatePacket(object):
    ''' a template for a AgentDataUpdate packet '''

    def __init__(self):
        self.name = 'AgentDataUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['FirstName'] = None    # MVT_VARIABLE
        self.AgentData['LastName'] = None    # MVT_VARIABLE
        self.AgentData['GroupTitle'] = None    # MVT_VARIABLE
        self.AgentData['ActiveGroupID'] = None    # MVT_LLUUID
        self.AgentData['GroupPowers'] = None    # MVT_U64
        self.AgentData['GroupName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentDataUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], FirstName = self.AgentData['FirstName'], LastName = self.AgentData['LastName'], GroupTitle = self.AgentData['GroupTitle'], ActiveGroupID = self.AgentData['ActiveGroupID'], GroupPowers = self.AgentData['GroupPowers'], GroupName = self.AgentData['GroupName']))

class TeleportRequestPacket(object):
    ''' a template for a TeleportRequest packet '''

    def __init__(self):
        self.name = 'TeleportRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Info = {}    # New Info block
        self.Info['RegionID'] = None    # MVT_LLUUID
        self.Info['Position'] = None    # MVT_LLVector3
        self.Info['LookAt'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TeleportRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Info', RegionID = self.Info['RegionID'], Position = self.Info['Position'], LookAt = self.Info['LookAt']))

class UpdateInventoryItemPacket(object):
    ''' a template for a UpdateInventoryItem packet '''

    def __init__(self):
        self.name = 'UpdateInventoryItem'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['TransactionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID
        self.InventoryData['FolderID'] = None    # MVT_LLUUID
        self.InventoryData['CallbackID'] = None    # MVT_U32
        self.InventoryData['CreatorID'] = None    # MVT_LLUUID
        self.InventoryData['OwnerID'] = None    # MVT_LLUUID
        self.InventoryData['GroupID'] = None    # MVT_LLUUID
        self.InventoryData['BaseMask'] = None    # MVT_U32
        self.InventoryData['OwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupMask'] = None    # MVT_U32
        self.InventoryData['EveryoneMask'] = None    # MVT_U32
        self.InventoryData['NextOwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupOwned'] = None    # MVT_BOOL
        self.InventoryData['TransactionID'] = None    # MVT_LLUUID
        self.InventoryData['Type'] = None    # MVT_S8
        self.InventoryData['InvType'] = None    # MVT_S8
        self.InventoryData['Flags'] = None    # MVT_U32
        self.InventoryData['SaleType'] = None    # MVT_U8
        self.InventoryData['SalePrice'] = None    # MVT_S32
        self.InventoryData['Name'] = None    # MVT_VARIABLE
        self.InventoryData['Description'] = None    # MVT_VARIABLE
        self.InventoryData['CreationDate'] = None    # MVT_S32
        self.InventoryData['CRC'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UpdateInventoryItem', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], TransactionID = self.AgentData['TransactionID']), Block('InventoryData', ItemID = self.InventoryData['ItemID'], FolderID = self.InventoryData['FolderID'], CallbackID = self.InventoryData['CallbackID'], CreatorID = self.InventoryData['CreatorID'], OwnerID = self.InventoryData['OwnerID'], GroupID = self.InventoryData['GroupID'], BaseMask = self.InventoryData['BaseMask'], OwnerMask = self.InventoryData['OwnerMask'], GroupMask = self.InventoryData['GroupMask'], EveryoneMask = self.InventoryData['EveryoneMask'], NextOwnerMask = self.InventoryData['NextOwnerMask'], GroupOwned = self.InventoryData['GroupOwned'], TransactionID = self.InventoryData['TransactionID'], Type = self.InventoryData['Type'], InvType = self.InventoryData['InvType'], Flags = self.InventoryData['Flags'], SaleType = self.InventoryData['SaleType'], SalePrice = self.InventoryData['SalePrice'], Name = self.InventoryData['Name'], Description = self.InventoryData['Description'], CreationDate = self.InventoryData['CreationDate'], CRC = self.InventoryData['CRC']))

class NearestLandingRegionReplyPacket(object):
    ''' a template for a NearestLandingRegionReply packet '''

    def __init__(self):
        self.name = 'NearestLandingRegionReply'

        self.LandingRegionData = {}    # New LandingRegionData block
        self.LandingRegionData['RegionHandle'] = None    # MVT_U64

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('NearestLandingRegionReply', Block('LandingRegionData', RegionHandle = self.LandingRegionData['RegionHandle']))

class EdgeDataPacketPacket(object):
    ''' a template for a EdgeDataPacket packet '''

    def __init__(self):
        self.name = 'EdgeDataPacket'

        self.EdgeData = {}    # New EdgeData block
        self.EdgeData['LayerType'] = None    # MVT_U8
        self.EdgeData['Direction'] = None    # MVT_U8
        self.EdgeData['LayerData'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EdgeDataPacket', Block('EdgeData', LayerType = self.EdgeData['LayerType'], Direction = self.EdgeData['Direction'], LayerData = self.EdgeData['LayerData']))

class EconomyDataRequestPacket(object):
    ''' a template for a EconomyDataRequest packet '''

    def __init__(self):
        self.name = 'EconomyDataRequest'

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EconomyDataRequest')

class LiveHelpGroupRequestPacket(object):
    ''' a template for a LiveHelpGroupRequest packet '''

    def __init__(self):
        self.name = 'LiveHelpGroupRequest'

        self.RequestData = {}    # New RequestData block
        self.RequestData['RequestID'] = None    # MVT_LLUUID
        self.RequestData['AgentID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LiveHelpGroupRequest', Block('RequestData', RequestID = self.RequestData['RequestID'], AgentID = self.RequestData['AgentID']))

class AddCircuitCodePacket(object):
    ''' a template for a AddCircuitCode packet '''

    def __init__(self):
        self.name = 'AddCircuitCode'

        self.CircuitCode = {}    # New CircuitCode block
        self.CircuitCode['Code'] = None    # MVT_U32
        self.CircuitCode['SessionID'] = None    # MVT_LLUUID
        self.CircuitCode['AgentID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AddCircuitCode', Block('CircuitCode', Code = self.CircuitCode['Code'], SessionID = self.CircuitCode['SessionID'], AgentID = self.CircuitCode['AgentID']))

class GroupAccountTransactionsRequestPacket(object):
    ''' a template for a GroupAccountTransactionsRequest packet '''

    def __init__(self):
        self.name = 'GroupAccountTransactionsRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.MoneyData = {}    # New MoneyData block
        self.MoneyData['RequestID'] = None    # MVT_LLUUID
        self.MoneyData['IntervalDays'] = None    # MVT_S32
        self.MoneyData['CurrentInterval'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupAccountTransactionsRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('MoneyData', RequestID = self.MoneyData['RequestID'], IntervalDays = self.MoneyData['IntervalDays'], CurrentInterval = self.MoneyData['CurrentInterval']))

class UUIDNameReplyPacket(object):
    ''' a template for a UUIDNameReply packet '''

    def __init__(self):
        self.name = 'UUIDNameReply'

        self.UUIDNameBlock = {}    # New UUIDNameBlock block
        self.UUIDNameBlock['ID'] = None    # MVT_LLUUID
        self.UUIDNameBlock['FirstName'] = None    # MVT_VARIABLE
        self.UUIDNameBlock['LastName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UUIDNameReply', Block('UUIDNameBlock', ID = self.UUIDNameBlock['ID'], FirstName = self.UUIDNameBlock['FirstName'], LastName = self.UUIDNameBlock['LastName']))

class ObjectLinkPacket(object):
    ''' a template for a ObjectLink packet '''

    def __init__(self):
        self.name = 'ObjectLink'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectLink', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class PreloadSoundPacket(object):
    ''' a template for a PreloadSound packet '''

    def __init__(self):
        self.name = 'PreloadSound'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['ObjectID'] = None    # MVT_LLUUID
        self.DataBlock['OwnerID'] = None    # MVT_LLUUID
        self.DataBlock['SoundID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('PreloadSound', Block('DataBlock', ObjectID = self.DataBlock['ObjectID'], OwnerID = self.DataBlock['OwnerID'], SoundID = self.DataBlock['SoundID']))

class EmailMessageRequestPacket(object):
    ''' a template for a EmailMessageRequest packet '''

    def __init__(self):
        self.name = 'EmailMessageRequest'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['ObjectID'] = None    # MVT_LLUUID
        self.DataBlock['FromAddress'] = None    # MVT_VARIABLE
        self.DataBlock['Subject'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EmailMessageRequest', Block('DataBlock', ObjectID = self.DataBlock['ObjectID'], FromAddress = self.DataBlock['FromAddress'], Subject = self.DataBlock['Subject']))

class ParcelGodForceOwnerPacket(object):
    ''' a template for a ParcelGodForceOwner packet '''

    def __init__(self):
        self.name = 'ParcelGodForceOwner'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['OwnerID'] = None    # MVT_LLUUID
        self.Data['LocalID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelGodForceOwner', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', OwnerID = self.Data['OwnerID'], LocalID = self.Data['LocalID']))

class ScriptMailRegistrationPacket(object):
    ''' a template for a ScriptMailRegistration packet '''

    def __init__(self):
        self.name = 'ScriptMailRegistration'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['TargetIP'] = None    # MVT_VARIABLE
        self.DataBlock['TargetPort'] = None    # MVT_IP_PORT
        self.DataBlock['TaskID'] = None    # MVT_LLUUID
        self.DataBlock['Flags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptMailRegistration', Block('DataBlock', TargetIP = self.DataBlock['TargetIP'], TargetPort = self.DataBlock['TargetPort'], TaskID = self.DataBlock['TaskID'], Flags = self.DataBlock['Flags']))

class ObjectRotationPacket(object):
    ''' a template for a ObjectRotation packet '''

    def __init__(self):
        self.name = 'ObjectRotation'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['Rotation'] = None    # MVT_LLQuaternion

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectRotation', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], Rotation = self.ObjectData['Rotation']))

class AcceptFriendshipPacket(object):
    ''' a template for a AcceptFriendship packet '''

    def __init__(self):
        self.name = 'AcceptFriendship'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.TransactionBlock = {}    # New TransactionBlock block
        self.TransactionBlock['TransactionID'] = None    # MVT_LLUUID

        self.FolderData = {}    # New FolderData block
        self.FolderData['FolderID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AcceptFriendship', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('TransactionBlock', TransactionID = self.TransactionBlock['TransactionID']), Block('FolderData', FolderID = self.FolderData['FolderID']))

class AvatarNotesReplyPacket(object):
    ''' a template for a AvatarNotesReply packet '''

    def __init__(self):
        self.name = 'AvatarNotesReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['TargetID'] = None    # MVT_LLUUID
        self.Data['Notes'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarNotesReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('Data', TargetID = self.Data['TargetID'], Notes = self.Data['Notes']))

class RezMultipleAttachmentsFromInvPacket(object):
    ''' a template for a RezMultipleAttachmentsFromInv packet '''

    def __init__(self):
        self.name = 'RezMultipleAttachmentsFromInv'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.HeaderData = {}    # New HeaderData block
        self.HeaderData['CompoundMsgID'] = None    # MVT_LLUUID
        self.HeaderData['TotalObjects'] = None    # MVT_U8
        self.HeaderData['FirstDetachAll'] = None    # MVT_BOOL

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ItemID'] = None    # MVT_LLUUID
        self.ObjectData['OwnerID'] = None    # MVT_LLUUID
        self.ObjectData['AttachmentPt'] = None    # MVT_U8
        self.ObjectData['ItemFlags'] = None    # MVT_U32
        self.ObjectData['GroupMask'] = None    # MVT_U32
        self.ObjectData['EveryoneMask'] = None    # MVT_U32
        self.ObjectData['NextOwnerMask'] = None    # MVT_U32
        self.ObjectData['Name'] = None    # MVT_VARIABLE
        self.ObjectData['Description'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RezMultipleAttachmentsFromInv', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('HeaderData', CompoundMsgID = self.HeaderData['CompoundMsgID'], TotalObjects = self.HeaderData['TotalObjects'], FirstDetachAll = self.HeaderData['FirstDetachAll']), Block('ObjectData', ItemID = self.ObjectData['ItemID'], OwnerID = self.ObjectData['OwnerID'], AttachmentPt = self.ObjectData['AttachmentPt'], ItemFlags = self.ObjectData['ItemFlags'], GroupMask = self.ObjectData['GroupMask'], EveryoneMask = self.ObjectData['EveryoneMask'], NextOwnerMask = self.ObjectData['NextOwnerMask'], Name = self.ObjectData['Name'], Description = self.ObjectData['Description']))

class TeleportLureRequestPacket(object):
    ''' a template for a TeleportLureRequest packet '''

    def __init__(self):
        self.name = 'TeleportLureRequest'

        self.Info = {}    # New Info block
        self.Info['AgentID'] = None    # MVT_LLUUID
        self.Info['SessionID'] = None    # MVT_LLUUID
        self.Info['LureID'] = None    # MVT_LLUUID
        self.Info['TeleportFlags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TeleportLureRequest', Block('Info', AgentID = self.Info['AgentID'], SessionID = self.Info['SessionID'], LureID = self.Info['LureID'], TeleportFlags = self.Info['TeleportFlags']))

class MoveInventoryFolderPacket(object):
    ''' a template for a MoveInventoryFolder packet '''

    def __init__(self):
        self.name = 'MoveInventoryFolder'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['Stamp'] = None    # MVT_BOOL

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['FolderID'] = None    # MVT_LLUUID
        self.InventoryData['ParentID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MoveInventoryFolder', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], Stamp = self.AgentData['Stamp']), Block('InventoryData', FolderID = self.InventoryData['FolderID'], ParentID = self.InventoryData['ParentID']))

class TransferInfoPacket(object):
    ''' a template for a TransferInfo packet '''

    def __init__(self):
        self.name = 'TransferInfo'

        self.TransferInfo = {}    # New TransferInfo block
        self.TransferInfo['TransferID'] = None    # MVT_LLUUID
        self.TransferInfo['ChannelType'] = None    # MVT_S32
        self.TransferInfo['TargetType'] = None    # MVT_S32
        self.TransferInfo['Status'] = None    # MVT_S32
        self.TransferInfo['Size'] = None    # MVT_S32
        self.TransferInfo['Params'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TransferInfo', Block('TransferInfo', TransferID = self.TransferInfo['TransferID'], ChannelType = self.TransferInfo['ChannelType'], TargetType = self.TransferInfo['TargetType'], Status = self.TransferInfo['Status'], Size = self.TransferInfo['Size'], Params = self.TransferInfo['Params']))

class DirPlacesQueryPacket(object):
    ''' a template for a DirPlacesQuery packet '''

    def __init__(self):
        self.name = 'DirPlacesQuery'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['QueryText'] = None    # MVT_VARIABLE
        self.QueryData['QueryFlags'] = None    # MVT_U32
        self.QueryData['Category'] = None    # MVT_S8
        self.QueryData['SimName'] = None    # MVT_VARIABLE
        self.QueryData['QueryStart'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirPlacesQuery', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('QueryData', QueryID = self.QueryData['QueryID'], QueryText = self.QueryData['QueryText'], QueryFlags = self.QueryData['QueryFlags'], Category = self.QueryData['Category'], SimName = self.QueryData['SimName'], QueryStart = self.QueryData['QueryStart']))

class ScriptAnswerYesPacket(object):
    ''' a template for a ScriptAnswerYes packet '''

    def __init__(self):
        self.name = 'ScriptAnswerYes'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['TaskID'] = None    # MVT_LLUUID
        self.Data['ItemID'] = None    # MVT_LLUUID
        self.Data['Questions'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptAnswerYes', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', TaskID = self.Data['TaskID'], ItemID = self.Data['ItemID'], Questions = self.Data['Questions']))

class SimulatorPresentAtLocationPacket(object):
    ''' a template for a SimulatorPresentAtLocation packet '''

    def __init__(self):
        self.name = 'SimulatorPresentAtLocation'

        self.SimulatorPublicHostBlock = {}    # New SimulatorPublicHostBlock block
        self.SimulatorPublicHostBlock['Port'] = None    # MVT_IP_PORT
        self.SimulatorPublicHostBlock['SimulatorIP'] = None    # MVT_IP_ADDR
        self.SimulatorPublicHostBlock['GridX'] = None    # MVT_U32
        self.SimulatorPublicHostBlock['GridY'] = None    # MVT_U32

        self.NeighborBlock = {}    # New NeighborBlock block
        self.NeighborBlock['IP'] = None    # MVT_IP_ADDR
        self.NeighborBlock['Port'] = None    # MVT_IP_PORT

        self.SimulatorBlock = {}    # New SimulatorBlock block
        self.SimulatorBlock['SimName'] = None    # MVT_VARIABLE
        self.SimulatorBlock['SimAccess'] = None    # MVT_U8
        self.SimulatorBlock['RegionFlags'] = None    # MVT_U32
        self.SimulatorBlock['RegionID'] = None    # MVT_LLUUID
        self.SimulatorBlock['EstateID'] = None    # MVT_U32
        self.SimulatorBlock['ParentEstateID'] = None    # MVT_U32

        self.TelehubBlock = {}    # New TelehubBlock block
        self.TelehubBlock['HasTelehub'] = None    # MVT_BOOL
        self.TelehubBlock['TelehubPos'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SimulatorPresentAtLocation', Block('SimulatorPublicHostBlock', Port = self.SimulatorPublicHostBlock['Port'], SimulatorIP = self.SimulatorPublicHostBlock['SimulatorIP'], GridX = self.SimulatorPublicHostBlock['GridX'], GridY = self.SimulatorPublicHostBlock['GridY']), Block('NeighborBlock', IP = self.NeighborBlock['IP'], Port = self.NeighborBlock['Port']), Block('SimulatorBlock', SimName = self.SimulatorBlock['SimName'], SimAccess = self.SimulatorBlock['SimAccess'], RegionFlags = self.SimulatorBlock['RegionFlags'], RegionID = self.SimulatorBlock['RegionID'], EstateID = self.SimulatorBlock['EstateID'], ParentEstateID = self.SimulatorBlock['ParentEstateID']), Block('TelehubBlock', HasTelehub = self.TelehubBlock['HasTelehub'], TelehubPos = self.TelehubBlock['TelehubPos']))

class GroupMembersRequestPacket(object):
    ''' a template for a GroupMembersRequest packet '''

    def __init__(self):
        self.name = 'GroupMembersRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['RequestID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupMembersRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', GroupID = self.GroupData['GroupID'], RequestID = self.GroupData['RequestID']))

class SetScriptRunningPacket(object):
    ''' a template for a SetScriptRunning packet '''

    def __init__(self):
        self.name = 'SetScriptRunning'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Script = {}    # New Script block
        self.Script['ObjectID'] = None    # MVT_LLUUID
        self.Script['ItemID'] = None    # MVT_LLUUID
        self.Script['Running'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SetScriptRunning', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Script', ObjectID = self.Script['ObjectID'], ItemID = self.Script['ItemID'], Running = self.Script['Running']))

class ModifyLandPacket(object):
    ''' a template for a ModifyLand packet '''

    def __init__(self):
        self.name = 'ModifyLand'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ModifyBlock = {}    # New ModifyBlock block
        self.ModifyBlock['Action'] = None    # MVT_U8
        self.ModifyBlock['BrushSize'] = None    # MVT_U8
        self.ModifyBlock['Seconds'] = None    # MVT_F32
        self.ModifyBlock['Height'] = None    # MVT_F32

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['LocalID'] = None    # MVT_S32
        self.ParcelData['West'] = None    # MVT_F32
        self.ParcelData['South'] = None    # MVT_F32
        self.ParcelData['East'] = None    # MVT_F32
        self.ParcelData['North'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ModifyLand', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ModifyBlock', Action = self.ModifyBlock['Action'], BrushSize = self.ModifyBlock['BrushSize'], Seconds = self.ModifyBlock['Seconds'], Height = self.ModifyBlock['Height']), Block('ParcelData', LocalID = self.ParcelData['LocalID'], West = self.ParcelData['West'], South = self.ParcelData['South'], East = self.ParcelData['East'], North = self.ParcelData['North']))

class SimCrashedPacket(object):
    ''' a template for a SimCrashed packet '''

    def __init__(self):
        self.name = 'SimCrashed'

        self.Data = {}    # New Data block
        self.Data['RegionX'] = None    # MVT_U32
        self.Data['RegionY'] = None    # MVT_U32

        self.Users = {}    # New Users block
        self.Users['AgentID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SimCrashed', Block('Data', RegionX = self.Data['RegionX'], RegionY = self.Data['RegionY']), Block('Users', AgentID = self.Users['AgentID']))

class MergeParcelPacket(object):
    ''' a template for a MergeParcel packet '''

    def __init__(self):
        self.name = 'MergeParcel'

        self.MasterParcelData = {}    # New MasterParcelData block
        self.MasterParcelData['MasterID'] = None    # MVT_LLUUID

        self.SlaveParcelData = {}    # New SlaveParcelData block
        self.SlaveParcelData['SlaveID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MergeParcel', Block('MasterParcelData', MasterID = self.MasterParcelData['MasterID']), Block('SlaveParcelData', SlaveID = self.SlaveParcelData['SlaveID']))

class ObjectBuyPacket(object):
    ''' a template for a ObjectBuy packet '''

    def __init__(self):
        self.name = 'ObjectBuy'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID
        self.AgentData['CategoryID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        self.ObjectData['SaleType'] = None    # MVT_U8
        self.ObjectData['SalePrice'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectBuy', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID'], CategoryID = self.AgentData['CategoryID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID'], SaleType = self.ObjectData['SaleType'], SalePrice = self.ObjectData['SalePrice']))

class CreateLandmarkForEventPacket(object):
    ''' a template for a CreateLandmarkForEvent packet '''

    def __init__(self):
        self.name = 'CreateLandmarkForEvent'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.EventData = {}    # New EventData block
        self.EventData['EventID'] = None    # MVT_U32

        self.InventoryBlock = {}    # New InventoryBlock block
        self.InventoryBlock['FolderID'] = None    # MVT_LLUUID
        self.InventoryBlock['Name'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CreateLandmarkForEvent', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('EventData', EventID = self.EventData['EventID']), Block('InventoryBlock', FolderID = self.InventoryBlock['FolderID'], Name = self.InventoryBlock['Name']))

class PickInfoUpdatePacket(object):
    ''' a template for a PickInfoUpdate packet '''

    def __init__(self):
        self.name = 'PickInfoUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['PickID'] = None    # MVT_LLUUID
        self.Data['CreatorID'] = None    # MVT_LLUUID
        self.Data['TopPick'] = None    # MVT_BOOL
        self.Data['ParcelID'] = None    # MVT_LLUUID
        self.Data['Name'] = None    # MVT_VARIABLE
        self.Data['Desc'] = None    # MVT_VARIABLE
        self.Data['SnapshotID'] = None    # MVT_LLUUID
        self.Data['PosGlobal'] = None    # MVT_LLVector3d

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('PickInfoUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', PickID = self.Data['PickID'], CreatorID = self.Data['CreatorID'], TopPick = self.Data['TopPick'], ParcelID = self.Data['ParcelID'], Name = self.Data['Name'], Desc = self.Data['Desc'], SnapshotID = self.Data['SnapshotID'], PosGlobal = self.Data['PosGlobal']))

class MapLayerRequestPacket(object):
    ''' a template for a MapLayerRequest packet '''

    def __init__(self):
        self.name = 'MapLayerRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['Flags'] = None    # MVT_U32
        self.AgentData['EstateID'] = None    # MVT_U32
        self.AgentData['Godlike'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MapLayerRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], Flags = self.AgentData['Flags'], EstateID = self.AgentData['EstateID'], Godlike = self.AgentData['Godlike']))

class TeleportLocalPacket(object):
    ''' a template for a TeleportLocal packet '''

    def __init__(self):
        self.name = 'TeleportLocal'

        self.Info = {}    # New Info block
        self.Info['AgentID'] = None    # MVT_LLUUID
        self.Info['LocationID'] = None    # MVT_U32
        self.Info['Position'] = None    # MVT_LLVector3
        self.Info['LookAt'] = None    # MVT_LLVector3
        self.Info['TeleportFlags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TeleportLocal', Block('Info', AgentID = self.Info['AgentID'], LocationID = self.Info['LocationID'], Position = self.Info['Position'], LookAt = self.Info['LookAt'], TeleportFlags = self.Info['TeleportFlags']))

class RemoveInventoryObjectsPacket(object):
    ''' a template for a RemoveInventoryObjects packet '''

    def __init__(self):
        self.name = 'RemoveInventoryObjects'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.FolderData = {}    # New FolderData block
        self.FolderData['FolderID'] = None    # MVT_LLUUID

        self.ItemData = {}    # New ItemData block
        self.ItemData['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RemoveInventoryObjects', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('FolderData', FolderID = self.FolderData['FolderID']), Block('ItemData', ItemID = self.ItemData['ItemID']))

class KickUserPacket(object):
    ''' a template for a KickUser packet '''

    def __init__(self):
        self.name = 'KickUser'

        self.TargetBlock = {}    # New TargetBlock block
        self.TargetBlock['TargetIP'] = None    # MVT_IP_ADDR
        self.TargetBlock['TargetPort'] = None    # MVT_IP_PORT

        self.UserInfo = {}    # New UserInfo block
        self.UserInfo['AgentID'] = None    # MVT_LLUUID
        self.UserInfo['SessionID'] = None    # MVT_LLUUID
        self.UserInfo['Reason'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('KickUser', Block('TargetBlock', TargetIP = self.TargetBlock['TargetIP'], TargetPort = self.TargetBlock['TargetPort']), Block('UserInfo', AgentID = self.UserInfo['AgentID'], SessionID = self.UserInfo['SessionID'], Reason = self.UserInfo['Reason']))

class CameraConstraintPacket(object):
    ''' a template for a CameraConstraint packet '''

    def __init__(self):
        self.name = 'CameraConstraint'

        self.CameraCollidePlane = {}    # New CameraCollidePlane block
        self.CameraCollidePlane['Plane'] = None    # MVT_LLVector4

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CameraConstraint', Block('CameraCollidePlane', Plane = self.CameraCollidePlane['Plane']))

class AvatarClassifiedReplyPacket(object):
    ''' a template for a AvatarClassifiedReply packet '''

    def __init__(self):
        self.name = 'AvatarClassifiedReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['TargetID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['ClassifiedID'] = None    # MVT_LLUUID
        self.Data['Name'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarClassifiedReply', Block('AgentData', AgentID = self.AgentData['AgentID'], TargetID = self.AgentData['TargetID']), Block('Data', ClassifiedID = self.Data['ClassifiedID'], Name = self.Data['Name']))

class MuteListRequestPacket(object):
    ''' a template for a MuteListRequest packet '''

    def __init__(self):
        self.name = 'MuteListRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.MuteData = {}    # New MuteData block
        self.MuteData['MuteCRC'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MuteListRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('MuteData', MuteCRC = self.MuteData['MuteCRC']))

class RequestRegionInfoPacket(object):
    ''' a template for a RequestRegionInfo packet '''

    def __init__(self):
        self.name = 'RequestRegionInfo'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RequestRegionInfo', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class LogFailedMoneyTransactionPacket(object):
    ''' a template for a LogFailedMoneyTransaction packet '''

    def __init__(self):
        self.name = 'LogFailedMoneyTransaction'

        self.TransactionData = {}    # New TransactionData block
        self.TransactionData['TransactionID'] = None    # MVT_LLUUID
        self.TransactionData['TransactionTime'] = None    # MVT_U32
        self.TransactionData['TransactionType'] = None    # MVT_S32
        self.TransactionData['SourceID'] = None    # MVT_LLUUID
        self.TransactionData['DestID'] = None    # MVT_LLUUID
        self.TransactionData['Flags'] = None    # MVT_U8
        self.TransactionData['Amount'] = None    # MVT_S32
        self.TransactionData['SimulatorIP'] = None    # MVT_IP_ADDR
        self.TransactionData['GridX'] = None    # MVT_U32
        self.TransactionData['GridY'] = None    # MVT_U32
        self.TransactionData['FailureType'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LogFailedMoneyTransaction', Block('TransactionData', TransactionID = self.TransactionData['TransactionID'], TransactionTime = self.TransactionData['TransactionTime'], TransactionType = self.TransactionData['TransactionType'], SourceID = self.TransactionData['SourceID'], DestID = self.TransactionData['DestID'], Flags = self.TransactionData['Flags'], Amount = self.TransactionData['Amount'], SimulatorIP = self.TransactionData['SimulatorIP'], GridX = self.TransactionData['GridX'], GridY = self.TransactionData['GridY'], FailureType = self.TransactionData['FailureType']))

class GroupTitlesRequestPacket(object):
    ''' a template for a GroupTitlesRequest packet '''

    def __init__(self):
        self.name = 'GroupTitlesRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID
        self.AgentData['RequestID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupTitlesRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID'], RequestID = self.AgentData['RequestID']))

class ImprovedInstantMessagePacket(object):
    ''' a template for a ImprovedInstantMessage packet '''

    def __init__(self):
        self.name = 'ImprovedInstantMessage'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.MessageBlock = {}    # New MessageBlock block
        self.MessageBlock['FromGroup'] = None    # MVT_BOOL
        self.MessageBlock['ToAgentID'] = None    # MVT_LLUUID
        self.MessageBlock['ParentEstateID'] = None    # MVT_U32
        self.MessageBlock['RegionID'] = None    # MVT_LLUUID
        self.MessageBlock['Position'] = None    # MVT_LLVector3
        self.MessageBlock['Offline'] = None    # MVT_U8
        self.MessageBlock['Dialog'] = None    # MVT_U8
        self.MessageBlock['ID'] = None    # MVT_LLUUID
        self.MessageBlock['Timestamp'] = None    # MVT_U32
        self.MessageBlock['FromAgentName'] = None    # MVT_VARIABLE
        self.MessageBlock['Message'] = None    # MVT_VARIABLE
        self.MessageBlock['BinaryBucket'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ImprovedInstantMessage', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('MessageBlock', FromGroup = self.MessageBlock['FromGroup'], ToAgentID = self.MessageBlock['ToAgentID'], ParentEstateID = self.MessageBlock['ParentEstateID'], RegionID = self.MessageBlock['RegionID'], Position = self.MessageBlock['Position'], Offline = self.MessageBlock['Offline'], Dialog = self.MessageBlock['Dialog'], ID = self.MessageBlock['ID'], Timestamp = self.MessageBlock['Timestamp'], FromAgentName = self.MessageBlock['FromAgentName'], Message = self.MessageBlock['Message'], BinaryBucket = self.MessageBlock['BinaryBucket']))

class ScriptDataRequestPacket(object):
    ''' a template for a ScriptDataRequest packet '''

    def __init__(self):
        self.name = 'ScriptDataRequest'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['Hash'] = None    # MVT_U64
        self.DataBlock['RequestType'] = None    # MVT_S8
        self.DataBlock['Request'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptDataRequest', Block('DataBlock', Hash = self.DataBlock['Hash'], RequestType = self.DataBlock['RequestType'], Request = self.DataBlock['Request']))

class ParcelAccessListReplyPacket(object):
    ''' a template for a ParcelAccessListReply packet '''

    def __init__(self):
        self.name = 'ParcelAccessListReply'

        self.Data = {}    # New Data block
        self.Data['AgentID'] = None    # MVT_LLUUID
        self.Data['SequenceID'] = None    # MVT_S32
        self.Data['Flags'] = None    # MVT_U32
        self.Data['LocalID'] = None    # MVT_S32

        self.List = {}    # New List block
        self.List['ID'] = None    # MVT_LLUUID
        self.List['Time'] = None    # MVT_S32
        self.List['Flags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelAccessListReply', Block('Data', AgentID = self.Data['AgentID'], SequenceID = self.Data['SequenceID'], Flags = self.Data['Flags'], LocalID = self.Data['LocalID']), Block('List', ID = self.List['ID'], Time = self.List['Time'], Flags = self.List['Flags']))

class ObjectDeselectPacket(object):
    ''' a template for a ObjectDeselect packet '''

    def __init__(self):
        self.name = 'ObjectDeselect'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectDeselect', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class RequestMultipleObjectsPacket(object):
    ''' a template for a RequestMultipleObjects packet '''

    def __init__(self):
        self.name = 'RequestMultipleObjects'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['CacheMissType'] = None    # MVT_U8
        self.ObjectData['ID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RequestMultipleObjects', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', CacheMissType = self.ObjectData['CacheMissType'], ID = self.ObjectData['ID']))

class RoutedMoneyBalanceReplyPacket(object):
    ''' a template for a RoutedMoneyBalanceReply packet '''

    def __init__(self):
        self.name = 'RoutedMoneyBalanceReply'

        self.TargetBlock = {}    # New TargetBlock block
        self.TargetBlock['TargetIP'] = None    # MVT_IP_ADDR
        self.TargetBlock['TargetPort'] = None    # MVT_IP_PORT

        self.MoneyData = {}    # New MoneyData block
        self.MoneyData['AgentID'] = None    # MVT_LLUUID
        self.MoneyData['TransactionID'] = None    # MVT_LLUUID
        self.MoneyData['TransactionSuccess'] = None    # MVT_BOOL
        self.MoneyData['MoneyBalance'] = None    # MVT_S32
        self.MoneyData['SquareMetersCredit'] = None    # MVT_S32
        self.MoneyData['SquareMetersCommitted'] = None    # MVT_S32
        self.MoneyData['Description'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RoutedMoneyBalanceReply', Block('TargetBlock', TargetIP = self.TargetBlock['TargetIP'], TargetPort = self.TargetBlock['TargetPort']), Block('MoneyData', AgentID = self.MoneyData['AgentID'], TransactionID = self.MoneyData['TransactionID'], TransactionSuccess = self.MoneyData['TransactionSuccess'], MoneyBalance = self.MoneyData['MoneyBalance'], SquareMetersCredit = self.MoneyData['SquareMetersCredit'], SquareMetersCommitted = self.MoneyData['SquareMetersCommitted'], Description = self.MoneyData['Description']))

class LoadURLPacket(object):
    ''' a template for a LoadURL packet '''

    def __init__(self):
        self.name = 'LoadURL'

        self.Data = {}    # New Data block
        self.Data['ObjectName'] = None    # MVT_VARIABLE
        self.Data['ObjectID'] = None    # MVT_LLUUID
        self.Data['OwnerID'] = None    # MVT_LLUUID
        self.Data['OwnerIsGroup'] = None    # MVT_BOOL
        self.Data['Message'] = None    # MVT_VARIABLE
        self.Data['URL'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LoadURL', Block('Data', ObjectName = self.Data['ObjectName'], ObjectID = self.Data['ObjectID'], OwnerID = self.Data['OwnerID'], OwnerIsGroup = self.Data['OwnerIsGroup'], Message = self.Data['Message'], URL = self.Data['URL']))

class RpcChannelReplyPacket(object):
    ''' a template for a RpcChannelReply packet '''

    def __init__(self):
        self.name = 'RpcChannelReply'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['TaskID'] = None    # MVT_LLUUID
        self.DataBlock['ItemID'] = None    # MVT_LLUUID
        self.DataBlock['ChannelID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RpcChannelReply', Block('DataBlock', TaskID = self.DataBlock['TaskID'], ItemID = self.DataBlock['ItemID'], ChannelID = self.DataBlock['ChannelID']))

class TeleportStartPacket(object):
    ''' a template for a TeleportStart packet '''

    def __init__(self):
        self.name = 'TeleportStart'

        self.Info = {}    # New Info block
        self.Info['TeleportFlags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TeleportStart', Block('Info', TeleportFlags = self.Info['TeleportFlags']))

class RezObjectPacket(object):
    ''' a template for a RezObject packet '''

    def __init__(self):
        self.name = 'RezObject'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.RezData = {}    # New RezData block
        self.RezData['FromTaskID'] = None    # MVT_LLUUID
        self.RezData['BypassRaycast'] = None    # MVT_U8
        self.RezData['RayStart'] = None    # MVT_LLVector3
        self.RezData['RayEnd'] = None    # MVT_LLVector3
        self.RezData['RayTargetID'] = None    # MVT_LLUUID
        self.RezData['RayEndIsIntersection'] = None    # MVT_BOOL
        self.RezData['RezSelected'] = None    # MVT_BOOL
        self.RezData['RemoveItem'] = None    # MVT_BOOL
        self.RezData['ItemFlags'] = None    # MVT_U32
        self.RezData['GroupMask'] = None    # MVT_U32
        self.RezData['EveryoneMask'] = None    # MVT_U32
        self.RezData['NextOwnerMask'] = None    # MVT_U32

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID
        self.InventoryData['FolderID'] = None    # MVT_LLUUID
        self.InventoryData['CreatorID'] = None    # MVT_LLUUID
        self.InventoryData['OwnerID'] = None    # MVT_LLUUID
        self.InventoryData['GroupID'] = None    # MVT_LLUUID
        self.InventoryData['BaseMask'] = None    # MVT_U32
        self.InventoryData['OwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupMask'] = None    # MVT_U32
        self.InventoryData['EveryoneMask'] = None    # MVT_U32
        self.InventoryData['NextOwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupOwned'] = None    # MVT_BOOL
        self.InventoryData['TransactionID'] = None    # MVT_LLUUID
        self.InventoryData['Type'] = None    # MVT_S8
        self.InventoryData['InvType'] = None    # MVT_S8
        self.InventoryData['Flags'] = None    # MVT_U32
        self.InventoryData['SaleType'] = None    # MVT_U8
        self.InventoryData['SalePrice'] = None    # MVT_S32
        self.InventoryData['Name'] = None    # MVT_VARIABLE
        self.InventoryData['Description'] = None    # MVT_VARIABLE
        self.InventoryData['CreationDate'] = None    # MVT_S32
        self.InventoryData['CRC'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RezObject', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('RezData', FromTaskID = self.RezData['FromTaskID'], BypassRaycast = self.RezData['BypassRaycast'], RayStart = self.RezData['RayStart'], RayEnd = self.RezData['RayEnd'], RayTargetID = self.RezData['RayTargetID'], RayEndIsIntersection = self.RezData['RayEndIsIntersection'], RezSelected = self.RezData['RezSelected'], RemoveItem = self.RezData['RemoveItem'], ItemFlags = self.RezData['ItemFlags'], GroupMask = self.RezData['GroupMask'], EveryoneMask = self.RezData['EveryoneMask'], NextOwnerMask = self.RezData['NextOwnerMask']), Block('InventoryData', ItemID = self.InventoryData['ItemID'], FolderID = self.InventoryData['FolderID'], CreatorID = self.InventoryData['CreatorID'], OwnerID = self.InventoryData['OwnerID'], GroupID = self.InventoryData['GroupID'], BaseMask = self.InventoryData['BaseMask'], OwnerMask = self.InventoryData['OwnerMask'], GroupMask = self.InventoryData['GroupMask'], EveryoneMask = self.InventoryData['EveryoneMask'], NextOwnerMask = self.InventoryData['NextOwnerMask'], GroupOwned = self.InventoryData['GroupOwned'], TransactionID = self.InventoryData['TransactionID'], Type = self.InventoryData['Type'], InvType = self.InventoryData['InvType'], Flags = self.InventoryData['Flags'], SaleType = self.InventoryData['SaleType'], SalePrice = self.InventoryData['SalePrice'], Name = self.InventoryData['Name'], Description = self.InventoryData['Description'], CreationDate = self.InventoryData['CreationDate'], CRC = self.InventoryData['CRC']))

class AvatarInterestsReplyPacket(object):
    ''' a template for a AvatarInterestsReply packet '''

    def __init__(self):
        self.name = 'AvatarInterestsReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['AvatarID'] = None    # MVT_LLUUID

        self.PropertiesData = {}    # New PropertiesData block
        self.PropertiesData['WantToMask'] = None    # MVT_U32
        self.PropertiesData['WantToText'] = None    # MVT_VARIABLE
        self.PropertiesData['SkillsMask'] = None    # MVT_U32
        self.PropertiesData['SkillsText'] = None    # MVT_VARIABLE
        self.PropertiesData['LanguagesText'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarInterestsReply', Block('AgentData', AgentID = self.AgentData['AgentID'], AvatarID = self.AgentData['AvatarID']), Block('PropertiesData', WantToMask = self.PropertiesData['WantToMask'], WantToText = self.PropertiesData['WantToText'], SkillsMask = self.PropertiesData['SkillsMask'], SkillsText = self.PropertiesData['SkillsText'], LanguagesText = self.PropertiesData['LanguagesText']))

class ObjectUpdateCompressedPacket(object):
    ''' a template for a ObjectUpdateCompressed packet '''

    def __init__(self):
        self.name = 'ObjectUpdateCompressed'

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionHandle'] = None    # MVT_U64
        self.RegionData['TimeDilation'] = None    # MVT_U16

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['UpdateFlags'] = None    # MVT_U32
        self.ObjectData['Data'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectUpdateCompressed', Block('RegionData', RegionHandle = self.RegionData['RegionHandle'], TimeDilation = self.RegionData['TimeDilation']), Block('ObjectData', UpdateFlags = self.ObjectData['UpdateFlags'], Data = self.ObjectData['Data']))

class DirPopularQueryPacket(object):
    ''' a template for a DirPopularQuery packet '''

    def __init__(self):
        self.name = 'DirPopularQuery'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['QueryFlags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirPopularQuery', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('QueryData', QueryID = self.QueryData['QueryID'], QueryFlags = self.QueryData['QueryFlags']))

class ChangeInventoryItemFlagsPacket(object):
    ''' a template for a ChangeInventoryItemFlags packet '''

    def __init__(self):
        self.name = 'ChangeInventoryItemFlags'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID
        self.InventoryData['Flags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ChangeInventoryItemFlags', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('InventoryData', ItemID = self.InventoryData['ItemID'], Flags = self.InventoryData['Flags']))

class SimulatorViewerTimeMessagePacket(object):
    ''' a template for a SimulatorViewerTimeMessage packet '''

    def __init__(self):
        self.name = 'SimulatorViewerTimeMessage'

        self.TimeInfo = {}    # New TimeInfo block
        self.TimeInfo['UsecSinceStart'] = None    # MVT_U64
        self.TimeInfo['SecPerDay'] = None    # MVT_U32
        self.TimeInfo['SecPerYear'] = None    # MVT_U32
        self.TimeInfo['SunDirection'] = None    # MVT_LLVector3
        self.TimeInfo['SunPhase'] = None    # MVT_F32
        self.TimeInfo['SunAngVelocity'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SimulatorViewerTimeMessage', Block('TimeInfo', UsecSinceStart = self.TimeInfo['UsecSinceStart'], SecPerDay = self.TimeInfo['SecPerDay'], SecPerYear = self.TimeInfo['SecPerYear'], SunDirection = self.TimeInfo['SunDirection'], SunPhase = self.TimeInfo['SunPhase'], SunAngVelocity = self.TimeInfo['SunAngVelocity']))

class PlacesQueryPacket(object):
    ''' a template for a PlacesQuery packet '''

    def __init__(self):
        self.name = 'PlacesQuery'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['QueryID'] = None    # MVT_LLUUID

        self.TransactionData = {}    # New TransactionData block
        self.TransactionData['TransactionID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryText'] = None    # MVT_VARIABLE
        self.QueryData['QueryFlags'] = None    # MVT_U32
        self.QueryData['Category'] = None    # MVT_S8
        self.QueryData['SimName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('PlacesQuery', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], QueryID = self.AgentData['QueryID']), Block('TransactionData', TransactionID = self.TransactionData['TransactionID']), Block('QueryData', QueryText = self.QueryData['QueryText'], QueryFlags = self.QueryData['QueryFlags'], Category = self.QueryData['Category'], SimName = self.QueryData['SimName']))

class ActivateGroupPacket(object):
    ''' a template for a ActivateGroup packet '''

    def __init__(self):
        self.name = 'ActivateGroup'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ActivateGroup', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']))

class SubscribeLoadPacket(object):
    ''' a template for a SubscribeLoad packet '''

    def __init__(self):
        self.name = 'SubscribeLoad'

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SubscribeLoad')

class EjectGroupMemberReplyPacket(object):
    ''' a template for a EjectGroupMemberReply packet '''

    def __init__(self):
        self.name = 'EjectGroupMemberReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID

        self.EjectData = {}    # New EjectData block
        self.EjectData['Success'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EjectGroupMemberReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('GroupData', GroupID = self.GroupData['GroupID']), Block('EjectData', Success = self.EjectData['Success']))

class CheckParcelSalesPacket(object):
    ''' a template for a CheckParcelSales packet '''

    def __init__(self):
        self.name = 'CheckParcelSales'

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionHandle'] = None    # MVT_U64

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CheckParcelSales', Block('RegionData', RegionHandle = self.RegionData['RegionHandle']))

class DerezContainerPacket(object):
    ''' a template for a DerezContainer packet '''

    def __init__(self):
        self.name = 'DerezContainer'

        self.Data = {}    # New Data block
        self.Data['ObjectID'] = None    # MVT_LLUUID
        self.Data['Delete'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DerezContainer', Block('Data', ObjectID = self.Data['ObjectID'], Delete = self.Data['Delete']))

class ConfirmEnableSimulatorPacket(object):
    ''' a template for a ConfirmEnableSimulator packet '''

    def __init__(self):
        self.name = 'ConfirmEnableSimulator'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ConfirmEnableSimulator', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class SetStartLocationRequestPacket(object):
    ''' a template for a SetStartLocationRequest packet '''

    def __init__(self):
        self.name = 'SetStartLocationRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.StartLocationData = {}    # New StartLocationData block
        self.StartLocationData['SimName'] = None    # MVT_VARIABLE
        self.StartLocationData['LocationID'] = None    # MVT_U32
        self.StartLocationData['LocationPos'] = None    # MVT_LLVector3
        self.StartLocationData['LocationLookAt'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SetStartLocationRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('StartLocationData', SimName = self.StartLocationData['SimName'], LocationID = self.StartLocationData['LocationID'], LocationPos = self.StartLocationData['LocationPos'], LocationLookAt = self.StartLocationData['LocationLookAt']))

class EstateCovenantRequestPacket(object):
    ''' a template for a EstateCovenantRequest packet '''

    def __init__(self):
        self.name = 'EstateCovenantRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EstateCovenantRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class ErrorPacket(object):
    ''' a template for a Error packet '''

    def __init__(self):
        self.name = 'Error'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['Code'] = None    # MVT_S32
        self.Data['Token'] = None    # MVT_VARIABLE
        self.Data['ID'] = None    # MVT_LLUUID
        self.Data['System'] = None    # MVT_VARIABLE
        self.Data['Message'] = None    # MVT_VARIABLE
        self.Data['Data'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('Error', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('Data', Code = self.Data['Code'], Token = self.Data['Token'], ID = self.Data['ID'], System = self.Data['System'], Message = self.Data['Message'], Data = self.Data['Data']))

class AgentFOVPacket(object):
    ''' a template for a AgentFOV packet '''

    def __init__(self):
        self.name = 'AgentFOV'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['CircuitCode'] = None    # MVT_U32

        self.FOVBlock = {}    # New FOVBlock block
        self.FOVBlock['GenCounter'] = None    # MVT_U32
        self.FOVBlock['VerticalAngle'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentFOV', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], CircuitCode = self.AgentData['CircuitCode']), Block('FOVBlock', GenCounter = self.FOVBlock['GenCounter'], VerticalAngle = self.FOVBlock['VerticalAngle']))

class AcceptCallingCardPacket(object):
    ''' a template for a AcceptCallingCard packet '''

    def __init__(self):
        self.name = 'AcceptCallingCard'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.TransactionBlock = {}    # New TransactionBlock block
        self.TransactionBlock['TransactionID'] = None    # MVT_LLUUID

        self.FolderData = {}    # New FolderData block
        self.FolderData['FolderID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AcceptCallingCard', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('TransactionBlock', TransactionID = self.TransactionBlock['TransactionID']), Block('FolderData', FolderID = self.FolderData['FolderID']))

class EventNotificationAddRequestPacket(object):
    ''' a template for a EventNotificationAddRequest packet '''

    def __init__(self):
        self.name = 'EventNotificationAddRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.EventData = {}    # New EventData block
        self.EventData['EventID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EventNotificationAddRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('EventData', EventID = self.EventData['EventID']))

class AgentUpdatePacket(object):
    ''' a template for a AgentUpdate packet '''

    def __init__(self):
        self.name = 'AgentUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['BodyRotation'] = None    # MVT_LLQuaternion
        self.AgentData['HeadRotation'] = None    # MVT_LLQuaternion
        self.AgentData['State'] = None    # MVT_U8
        self.AgentData['CameraCenter'] = None    # MVT_LLVector3
        self.AgentData['CameraAtAxis'] = None    # MVT_LLVector3
        self.AgentData['CameraLeftAxis'] = None    # MVT_LLVector3
        self.AgentData['CameraUpAxis'] = None    # MVT_LLVector3
        self.AgentData['Far'] = None    # MVT_F32
        self.AgentData['ControlFlags'] = None    # MVT_U32
        self.AgentData['Flags'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], BodyRotation = self.AgentData['BodyRotation'], HeadRotation = self.AgentData['HeadRotation'], State = self.AgentData['State'], CameraCenter = self.AgentData['CameraCenter'], CameraAtAxis = self.AgentData['CameraAtAxis'], CameraLeftAxis = self.AgentData['CameraLeftAxis'], CameraUpAxis = self.AgentData['CameraUpAxis'], Far = self.AgentData['Far'], ControlFlags = self.AgentData['ControlFlags'], Flags = self.AgentData['Flags']))

class AgentCachedTextureResponsePacket(object):
    ''' a template for a AgentCachedTextureResponse packet '''

    def __init__(self):
        self.name = 'AgentCachedTextureResponse'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['SerialNum'] = None    # MVT_S32

        self.WearableData = {}    # New WearableData block
        self.WearableData['TextureID'] = None    # MVT_LLUUID
        self.WearableData['TextureIndex'] = None    # MVT_U8
        self.WearableData['HostName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentCachedTextureResponse', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], SerialNum = self.AgentData['SerialNum']), Block('WearableData', TextureID = self.WearableData['TextureID'], TextureIndex = self.WearableData['TextureIndex'], HostName = self.WearableData['HostName']))

class GroupNoticeRequestPacket(object):
    ''' a template for a GroupNoticeRequest packet '''

    def __init__(self):
        self.name = 'GroupNoticeRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['GroupNoticeID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupNoticeRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', GroupNoticeID = self.Data['GroupNoticeID']))

class RemoveMuteListEntryPacket(object):
    ''' a template for a RemoveMuteListEntry packet '''

    def __init__(self):
        self.name = 'RemoveMuteListEntry'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.MuteData = {}    # New MuteData block
        self.MuteData['MuteID'] = None    # MVT_LLUUID
        self.MuteData['MuteName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RemoveMuteListEntry', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('MuteData', MuteID = self.MuteData['MuteID'], MuteName = self.MuteData['MuteName']))

class SetFollowCamPropertiesPacket(object):
    ''' a template for a SetFollowCamProperties packet '''

    def __init__(self):
        self.name = 'SetFollowCamProperties'

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID

        self.CameraProperty = {}    # New CameraProperty block
        self.CameraProperty['Type'] = None    # MVT_S32
        self.CameraProperty['Value'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SetFollowCamProperties', Block('ObjectData', ObjectID = self.ObjectData['ObjectID']), Block('CameraProperty', Type = self.CameraProperty['Type'], Value = self.CameraProperty['Value']))

class ChildAgentAlivePacket(object):
    ''' a template for a ChildAgentAlive packet '''

    def __init__(self):
        self.name = 'ChildAgentAlive'

        self.AgentData = {}    # New AgentData block
        self.AgentData['RegionHandle'] = None    # MVT_U64
        self.AgentData['ViewerCircuitCode'] = None    # MVT_U32
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ChildAgentAlive', Block('AgentData', RegionHandle = self.AgentData['RegionHandle'], ViewerCircuitCode = self.AgentData['ViewerCircuitCode'], AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class DirGroupsReplyPacket(object):
    ''' a template for a DirGroupsReply packet '''

    def __init__(self):
        self.name = 'DirGroupsReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID

        self.QueryReplies = {}    # New QueryReplies block
        self.QueryReplies['GroupID'] = None    # MVT_LLUUID
        self.QueryReplies['GroupName'] = None    # MVT_VARIABLE
        self.QueryReplies['Members'] = None    # MVT_S32
        self.QueryReplies['SearchOrder'] = None    # MVT_F32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirGroupsReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID']), Block('QueryReplies', GroupID = self.QueryReplies['GroupID'], GroupName = self.QueryReplies['GroupName'], Members = self.QueryReplies['Members'], SearchOrder = self.QueryReplies['SearchOrder']))

class GroupTitleUpdatePacket(object):
    ''' a template for a GroupTitleUpdate packet '''

    def __init__(self):
        self.name = 'GroupTitleUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID
        self.AgentData['TitleRoleID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupTitleUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID'], TitleRoleID = self.AgentData['TitleRoleID']))

class GroupAccountDetailsRequestPacket(object):
    ''' a template for a GroupAccountDetailsRequest packet '''

    def __init__(self):
        self.name = 'GroupAccountDetailsRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.MoneyData = {}    # New MoneyData block
        self.MoneyData['RequestID'] = None    # MVT_LLUUID
        self.MoneyData['IntervalDays'] = None    # MVT_S32
        self.MoneyData['CurrentInterval'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupAccountDetailsRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('MoneyData', RequestID = self.MoneyData['RequestID'], IntervalDays = self.MoneyData['IntervalDays'], CurrentInterval = self.MoneyData['CurrentInterval']))

class ParcelAuctionsPacket(object):
    ''' a template for a ParcelAuctions packet '''

    def __init__(self):
        self.name = 'ParcelAuctions'

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['ParcelID'] = None    # MVT_LLUUID
        self.ParcelData['WinnerID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelAuctions', Block('ParcelData', ParcelID = self.ParcelData['ParcelID'], WinnerID = self.ParcelData['WinnerID']))

class ObjectDetachPacket(object):
    ''' a template for a ObjectDetach packet '''

    def __init__(self):
        self.name = 'ObjectDetach'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectDetach', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class AssetUploadRequestPacket(object):
    ''' a template for a AssetUploadRequest packet '''

    def __init__(self):
        self.name = 'AssetUploadRequest'

        self.AssetBlock = {}    # New AssetBlock block
        self.AssetBlock['TransactionID'] = None    # MVT_LLUUID
        self.AssetBlock['Type'] = None    # MVT_S8
        self.AssetBlock['Tempfile'] = None    # MVT_BOOL
        self.AssetBlock['StoreLocal'] = None    # MVT_BOOL
        self.AssetBlock['AssetData'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AssetUploadRequest', Block('AssetBlock', TransactionID = self.AssetBlock['TransactionID'], Type = self.AssetBlock['Type'], Tempfile = self.AssetBlock['Tempfile'], StoreLocal = self.AssetBlock['StoreLocal'], AssetData = self.AssetBlock['AssetData']))

class ParcelReleasePacket(object):
    ''' a template for a ParcelRelease packet '''

    def __init__(self):
        self.name = 'ParcelRelease'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['LocalID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelRelease', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', LocalID = self.Data['LocalID']))

class RpcScriptRequestInboundForwardPacket(object):
    ''' a template for a RpcScriptRequestInboundForward packet '''

    def __init__(self):
        self.name = 'RpcScriptRequestInboundForward'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['RPCServerIP'] = None    # MVT_IP_ADDR
        self.DataBlock['RPCServerPort'] = None    # MVT_IP_PORT
        self.DataBlock['TaskID'] = None    # MVT_LLUUID
        self.DataBlock['ItemID'] = None    # MVT_LLUUID
        self.DataBlock['ChannelID'] = None    # MVT_LLUUID
        self.DataBlock['IntValue'] = None    # MVT_U32
        self.DataBlock['StringValue'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RpcScriptRequestInboundForward', Block('DataBlock', RPCServerIP = self.DataBlock['RPCServerIP'], RPCServerPort = self.DataBlock['RPCServerPort'], TaskID = self.DataBlock['TaskID'], ItemID = self.DataBlock['ItemID'], ChannelID = self.DataBlock['ChannelID'], IntValue = self.DataBlock['IntValue'], StringValue = self.DataBlock['StringValue']))

class ObjectDuplicateOnRayPacket(object):
    ''' a template for a ObjectDuplicateOnRay packet '''

    def __init__(self):
        self.name = 'ObjectDuplicateOnRay'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID
        self.AgentData['RayStart'] = None    # MVT_LLVector3
        self.AgentData['RayEnd'] = None    # MVT_LLVector3
        self.AgentData['BypassRaycast'] = None    # MVT_BOOL
        self.AgentData['RayEndIsIntersection'] = None    # MVT_BOOL
        self.AgentData['CopyCenters'] = None    # MVT_BOOL
        self.AgentData['CopyRotates'] = None    # MVT_BOOL
        self.AgentData['RayTargetID'] = None    # MVT_LLUUID
        self.AgentData['DuplicateFlags'] = None    # MVT_U32

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectDuplicateOnRay', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID'], RayStart = self.AgentData['RayStart'], RayEnd = self.AgentData['RayEnd'], BypassRaycast = self.AgentData['BypassRaycast'], RayEndIsIntersection = self.AgentData['RayEndIsIntersection'], CopyCenters = self.AgentData['CopyCenters'], CopyRotates = self.AgentData['CopyRotates'], RayTargetID = self.AgentData['RayTargetID'], DuplicateFlags = self.AgentData['DuplicateFlags']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class MoneyTransferRequestPacket(object):
    ''' a template for a MoneyTransferRequest packet '''

    def __init__(self):
        self.name = 'MoneyTransferRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.MoneyData = {}    # New MoneyData block
        self.MoneyData['SourceID'] = None    # MVT_LLUUID
        self.MoneyData['DestID'] = None    # MVT_LLUUID
        self.MoneyData['Flags'] = None    # MVT_U8
        self.MoneyData['Amount'] = None    # MVT_S32
        self.MoneyData['AggregatePermNextOwner'] = None    # MVT_U8
        self.MoneyData['AggregatePermInventory'] = None    # MVT_U8
        self.MoneyData['TransactionType'] = None    # MVT_S32
        self.MoneyData['Description'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MoneyTransferRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('MoneyData', SourceID = self.MoneyData['SourceID'], DestID = self.MoneyData['DestID'], Flags = self.MoneyData['Flags'], Amount = self.MoneyData['Amount'], AggregatePermNextOwner = self.MoneyData['AggregatePermNextOwner'], AggregatePermInventory = self.MoneyData['AggregatePermInventory'], TransactionType = self.MoneyData['TransactionType'], Description = self.MoneyData['Description']))

class ScriptDialogPacket(object):
    ''' a template for a ScriptDialog packet '''

    def __init__(self):
        self.name = 'ScriptDialog'

        self.Data = {}    # New Data block
        self.Data['ObjectID'] = None    # MVT_LLUUID
        self.Data['FirstName'] = None    # MVT_VARIABLE
        self.Data['LastName'] = None    # MVT_VARIABLE
        self.Data['ObjectName'] = None    # MVT_VARIABLE
        self.Data['Message'] = None    # MVT_VARIABLE
        self.Data['ChatChannel'] = None    # MVT_S32
        self.Data['ImageID'] = None    # MVT_LLUUID

        self.Buttons = {}    # New Buttons block
        self.Buttons['ButtonLabel'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ScriptDialog', Block('Data', ObjectID = self.Data['ObjectID'], FirstName = self.Data['FirstName'], LastName = self.Data['LastName'], ObjectName = self.Data['ObjectName'], Message = self.Data['Message'], ChatChannel = self.Data['ChatChannel'], ImageID = self.Data['ImageID']), Block('Buttons', ButtonLabel = self.Buttons['ButtonLabel']))

class RequestTrustedCircuitPacket(object):
    ''' a template for a RequestTrustedCircuit packet '''

    def __init__(self):
        self.name = 'RequestTrustedCircuit'

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RequestTrustedCircuit')

class TeleportFinishPacket(object):
    ''' a template for a TeleportFinish packet '''

    def __init__(self):
        self.name = 'TeleportFinish'

        self.Info = {}    # New Info block
        self.Info['AgentID'] = None    # MVT_LLUUID
        self.Info['LocationID'] = None    # MVT_U32
        self.Info['SimIP'] = None    # MVT_IP_ADDR
        self.Info['SimPort'] = None    # MVT_IP_PORT
        self.Info['RegionHandle'] = None    # MVT_U64
        self.Info['SeedCapability'] = None    # MVT_VARIABLE
        self.Info['SimAccess'] = None    # MVT_U8
        self.Info['TeleportFlags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TeleportFinish', Block('Info', AgentID = self.Info['AgentID'], LocationID = self.Info['LocationID'], SimIP = self.Info['SimIP'], SimPort = self.Info['SimPort'], RegionHandle = self.Info['RegionHandle'], SeedCapability = self.Info['SeedCapability'], SimAccess = self.Info['SimAccess'], TeleportFlags = self.Info['TeleportFlags']))

class CreateInventoryFolderPacket(object):
    ''' a template for a CreateInventoryFolder packet '''

    def __init__(self):
        self.name = 'CreateInventoryFolder'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.FolderData = {}    # New FolderData block
        self.FolderData['FolderID'] = None    # MVT_LLUUID
        self.FolderData['ParentID'] = None    # MVT_LLUUID
        self.FolderData['Type'] = None    # MVT_S8
        self.FolderData['Name'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CreateInventoryFolder', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('FolderData', FolderID = self.FolderData['FolderID'], ParentID = self.FolderData['ParentID'], Type = self.FolderData['Type'], Name = self.FolderData['Name']))

class DisableSimulatorPacket(object):
    ''' a template for a DisableSimulator packet '''

    def __init__(self):
        self.name = 'DisableSimulator'

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DisableSimulator')

class TransferPacketPacket(object):
    ''' a template for a TransferPacket packet '''

    def __init__(self):
        self.name = 'TransferPacket'

        self.TransferData = {}    # New TransferData block
        self.TransferData['TransferID'] = None    # MVT_LLUUID
        self.TransferData['ChannelType'] = None    # MVT_S32
        self.TransferData['Packet'] = None    # MVT_S32
        self.TransferData['Status'] = None    # MVT_S32
        self.TransferData['Data'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TransferPacket', Block('TransferData', TransferID = self.TransferData['TransferID'], ChannelType = self.TransferData['ChannelType'], Packet = self.TransferData['Packet'], Status = self.TransferData['Status'], Data = self.TransferData['Data']))

class ClassifiedGodDeletePacket(object):
    ''' a template for a ClassifiedGodDelete packet '''

    def __init__(self):
        self.name = 'ClassifiedGodDelete'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['ClassifiedID'] = None    # MVT_LLUUID
        self.Data['QueryID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ClassifiedGodDelete', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', ClassifiedID = self.Data['ClassifiedID'], QueryID = self.Data['QueryID']))

class TrackAgentPacket(object):
    ''' a template for a TrackAgent packet '''

    def __init__(self):
        self.name = 'TrackAgent'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.TargetData = {}    # New TargetData block
        self.TargetData['PreyID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TrackAgent', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('TargetData', PreyID = self.TargetData['PreyID']))

class SimulatorReadyPacket(object):
    ''' a template for a SimulatorReady packet '''

    def __init__(self):
        self.name = 'SimulatorReady'

        self.SimulatorBlock = {}    # New SimulatorBlock block
        self.SimulatorBlock['SimName'] = None    # MVT_VARIABLE
        self.SimulatorBlock['SimAccess'] = None    # MVT_U8
        self.SimulatorBlock['RegionFlags'] = None    # MVT_U32
        self.SimulatorBlock['RegionID'] = None    # MVT_LLUUID
        self.SimulatorBlock['EstateID'] = None    # MVT_U32
        self.SimulatorBlock['ParentEstateID'] = None    # MVT_U32

        self.TelehubBlock = {}    # New TelehubBlock block
        self.TelehubBlock['HasTelehub'] = None    # MVT_BOOL
        self.TelehubBlock['TelehubPos'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SimulatorReady', Block('SimulatorBlock', SimName = self.SimulatorBlock['SimName'], SimAccess = self.SimulatorBlock['SimAccess'], RegionFlags = self.SimulatorBlock['RegionFlags'], RegionID = self.SimulatorBlock['RegionID'], EstateID = self.SimulatorBlock['EstateID'], ParentEstateID = self.SimulatorBlock['ParentEstateID']), Block('TelehubBlock', HasTelehub = self.TelehubBlock['HasTelehub'], TelehubPos = self.TelehubBlock['TelehubPos']))

class GroupProposalBallotPacket(object):
    ''' a template for a GroupProposalBallot packet '''

    def __init__(self):
        self.name = 'GroupProposalBallot'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ProposalData = {}    # New ProposalData block
        self.ProposalData['ProposalID'] = None    # MVT_LLUUID
        self.ProposalData['GroupID'] = None    # MVT_LLUUID
        self.ProposalData['VoteCast'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupProposalBallot', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ProposalData', ProposalID = self.ProposalData['ProposalID'], GroupID = self.ProposalData['GroupID'], VoteCast = self.ProposalData['VoteCast']))

class GetScriptRunningPacket(object):
    ''' a template for a GetScriptRunning packet '''

    def __init__(self):
        self.name = 'GetScriptRunning'

        self.Script = {}    # New Script block
        self.Script['ObjectID'] = None    # MVT_LLUUID
        self.Script['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GetScriptRunning', Block('Script', ObjectID = self.Script['ObjectID'], ItemID = self.Script['ItemID']))

class ObjectSpinStopPacket(object):
    ''' a template for a ObjectSpinStop packet '''

    def __init__(self):
        self.name = 'ObjectSpinStop'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectSpinStop', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectID = self.ObjectData['ObjectID']))

class GroupRoleChangesPacket(object):
    ''' a template for a GroupRoleChanges packet '''

    def __init__(self):
        self.name = 'GroupRoleChanges'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.RoleChange = {}    # New RoleChange block
        self.RoleChange['RoleID'] = None    # MVT_LLUUID
        self.RoleChange['MemberID'] = None    # MVT_LLUUID
        self.RoleChange['Change'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupRoleChanges', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('RoleChange', RoleID = self.RoleChange['RoleID'], MemberID = self.RoleChange['MemberID'], Change = self.RoleChange['Change']))

class UpdateParcelPacket(object):
    ''' a template for a UpdateParcel packet '''

    def __init__(self):
        self.name = 'UpdateParcel'

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['ParcelID'] = None    # MVT_LLUUID
        self.ParcelData['RegionHandle'] = None    # MVT_U64
        self.ParcelData['OwnerID'] = None    # MVT_LLUUID
        self.ParcelData['GroupOwned'] = None    # MVT_BOOL
        self.ParcelData['Status'] = None    # MVT_U8
        self.ParcelData['Name'] = None    # MVT_VARIABLE
        self.ParcelData['Description'] = None    # MVT_VARIABLE
        self.ParcelData['MusicURL'] = None    # MVT_VARIABLE
        self.ParcelData['RegionX'] = None    # MVT_F32
        self.ParcelData['RegionY'] = None    # MVT_F32
        self.ParcelData['ActualArea'] = None    # MVT_S32
        self.ParcelData['BillableArea'] = None    # MVT_S32
        self.ParcelData['ShowDir'] = None    # MVT_BOOL
        self.ParcelData['IsForSale'] = None    # MVT_BOOL
        self.ParcelData['Category'] = None    # MVT_U8
        self.ParcelData['SnapshotID'] = None    # MVT_LLUUID
        self.ParcelData['UserLocation'] = None    # MVT_LLVector3
        self.ParcelData['SalePrice'] = None    # MVT_S32
        self.ParcelData['AuthorizedBuyerID'] = None    # MVT_LLUUID
        self.ParcelData['AllowPublish'] = None    # MVT_BOOL
        self.ParcelData['MaturePublish'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UpdateParcel', Block('ParcelData', ParcelID = self.ParcelData['ParcelID'], RegionHandle = self.ParcelData['RegionHandle'], OwnerID = self.ParcelData['OwnerID'], GroupOwned = self.ParcelData['GroupOwned'], Status = self.ParcelData['Status'], Name = self.ParcelData['Name'], Description = self.ParcelData['Description'], MusicURL = self.ParcelData['MusicURL'], RegionX = self.ParcelData['RegionX'], RegionY = self.ParcelData['RegionY'], ActualArea = self.ParcelData['ActualArea'], BillableArea = self.ParcelData['BillableArea'], ShowDir = self.ParcelData['ShowDir'], IsForSale = self.ParcelData['IsForSale'], Category = self.ParcelData['Category'], SnapshotID = self.ParcelData['SnapshotID'], UserLocation = self.ParcelData['UserLocation'], SalePrice = self.ParcelData['SalePrice'], AuthorizedBuyerID = self.ParcelData['AuthorizedBuyerID'], AllowPublish = self.ParcelData['AllowPublish'], MaturePublish = self.ParcelData['MaturePublish']))

class RezRestoreToWorldPacket(object):
    ''' a template for a RezRestoreToWorld packet '''

    def __init__(self):
        self.name = 'RezRestoreToWorld'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['ItemID'] = None    # MVT_LLUUID
        self.InventoryData['FolderID'] = None    # MVT_LLUUID
        self.InventoryData['CreatorID'] = None    # MVT_LLUUID
        self.InventoryData['OwnerID'] = None    # MVT_LLUUID
        self.InventoryData['GroupID'] = None    # MVT_LLUUID
        self.InventoryData['BaseMask'] = None    # MVT_U32
        self.InventoryData['OwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupMask'] = None    # MVT_U32
        self.InventoryData['EveryoneMask'] = None    # MVT_U32
        self.InventoryData['NextOwnerMask'] = None    # MVT_U32
        self.InventoryData['GroupOwned'] = None    # MVT_BOOL
        self.InventoryData['TransactionID'] = None    # MVT_LLUUID
        self.InventoryData['Type'] = None    # MVT_S8
        self.InventoryData['InvType'] = None    # MVT_S8
        self.InventoryData['Flags'] = None    # MVT_U32
        self.InventoryData['SaleType'] = None    # MVT_U8
        self.InventoryData['SalePrice'] = None    # MVT_S32
        self.InventoryData['Name'] = None    # MVT_VARIABLE
        self.InventoryData['Description'] = None    # MVT_VARIABLE
        self.InventoryData['CreationDate'] = None    # MVT_S32
        self.InventoryData['CRC'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RezRestoreToWorld', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('InventoryData', ItemID = self.InventoryData['ItemID'], FolderID = self.InventoryData['FolderID'], CreatorID = self.InventoryData['CreatorID'], OwnerID = self.InventoryData['OwnerID'], GroupID = self.InventoryData['GroupID'], BaseMask = self.InventoryData['BaseMask'], OwnerMask = self.InventoryData['OwnerMask'], GroupMask = self.InventoryData['GroupMask'], EveryoneMask = self.InventoryData['EveryoneMask'], NextOwnerMask = self.InventoryData['NextOwnerMask'], GroupOwned = self.InventoryData['GroupOwned'], TransactionID = self.InventoryData['TransactionID'], Type = self.InventoryData['Type'], InvType = self.InventoryData['InvType'], Flags = self.InventoryData['Flags'], SaleType = self.InventoryData['SaleType'], SalePrice = self.InventoryData['SalePrice'], Name = self.InventoryData['Name'], Description = self.InventoryData['Description'], CreationDate = self.InventoryData['CreationDate'], CRC = self.InventoryData['CRC']))

class ObjectOwnerPacket(object):
    ''' a template for a ObjectOwner packet '''

    def __init__(self):
        self.name = 'ObjectOwner'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.HeaderData = {}    # New HeaderData block
        self.HeaderData['Override'] = None    # MVT_BOOL
        self.HeaderData['OwnerID'] = None    # MVT_LLUUID
        self.HeaderData['GroupID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectOwner', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('HeaderData', Override = self.HeaderData['Override'], OwnerID = self.HeaderData['OwnerID'], GroupID = self.HeaderData['GroupID']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class RezScriptPacket(object):
    ''' a template for a RezScript packet '''

    def __init__(self):
        self.name = 'RezScript'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

        self.UpdateBlock = {}    # New UpdateBlock block
        self.UpdateBlock['ObjectLocalID'] = None    # MVT_U32
        self.UpdateBlock['Enabled'] = None    # MVT_BOOL

        self.InventoryBlock = {}    # New InventoryBlock block
        self.InventoryBlock['ItemID'] = None    # MVT_LLUUID
        self.InventoryBlock['FolderID'] = None    # MVT_LLUUID
        self.InventoryBlock['CreatorID'] = None    # MVT_LLUUID
        self.InventoryBlock['OwnerID'] = None    # MVT_LLUUID
        self.InventoryBlock['GroupID'] = None    # MVT_LLUUID
        self.InventoryBlock['BaseMask'] = None    # MVT_U32
        self.InventoryBlock['OwnerMask'] = None    # MVT_U32
        self.InventoryBlock['GroupMask'] = None    # MVT_U32
        self.InventoryBlock['EveryoneMask'] = None    # MVT_U32
        self.InventoryBlock['NextOwnerMask'] = None    # MVT_U32
        self.InventoryBlock['GroupOwned'] = None    # MVT_BOOL
        self.InventoryBlock['TransactionID'] = None    # MVT_LLUUID
        self.InventoryBlock['Type'] = None    # MVT_S8
        self.InventoryBlock['InvType'] = None    # MVT_S8
        self.InventoryBlock['Flags'] = None    # MVT_U32
        self.InventoryBlock['SaleType'] = None    # MVT_U8
        self.InventoryBlock['SalePrice'] = None    # MVT_S32
        self.InventoryBlock['Name'] = None    # MVT_VARIABLE
        self.InventoryBlock['Description'] = None    # MVT_VARIABLE
        self.InventoryBlock['CreationDate'] = None    # MVT_S32
        self.InventoryBlock['CRC'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RezScript', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], GroupID = self.AgentData['GroupID']), Block('UpdateBlock', ObjectLocalID = self.UpdateBlock['ObjectLocalID'], Enabled = self.UpdateBlock['Enabled']), Block('InventoryBlock', ItemID = self.InventoryBlock['ItemID'], FolderID = self.InventoryBlock['FolderID'], CreatorID = self.InventoryBlock['CreatorID'], OwnerID = self.InventoryBlock['OwnerID'], GroupID = self.InventoryBlock['GroupID'], BaseMask = self.InventoryBlock['BaseMask'], OwnerMask = self.InventoryBlock['OwnerMask'], GroupMask = self.InventoryBlock['GroupMask'], EveryoneMask = self.InventoryBlock['EveryoneMask'], NextOwnerMask = self.InventoryBlock['NextOwnerMask'], GroupOwned = self.InventoryBlock['GroupOwned'], TransactionID = self.InventoryBlock['TransactionID'], Type = self.InventoryBlock['Type'], InvType = self.InventoryBlock['InvType'], Flags = self.InventoryBlock['Flags'], SaleType = self.InventoryBlock['SaleType'], SalePrice = self.InventoryBlock['SalePrice'], Name = self.InventoryBlock['Name'], Description = self.InventoryBlock['Description'], CreationDate = self.InventoryBlock['CreationDate'], CRC = self.InventoryBlock['CRC']))

class ParcelReturnObjectsPacket(object):
    ''' a template for a ParcelReturnObjects packet '''

    def __init__(self):
        self.name = 'ParcelReturnObjects'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['LocalID'] = None    # MVT_S32
        self.ParcelData['ReturnType'] = None    # MVT_U32

        self.TaskIDs = {}    # New TaskIDs block
        self.TaskIDs['TaskID'] = None    # MVT_LLUUID

        self.OwnerIDs = {}    # New OwnerIDs block
        self.OwnerIDs['OwnerID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelReturnObjects', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', LocalID = self.ParcelData['LocalID'], ReturnType = self.ParcelData['ReturnType']), Block('TaskIDs', TaskID = self.TaskIDs['TaskID']), Block('OwnerIDs', OwnerID = self.OwnerIDs['OwnerID']))

class InitiateDownloadPacket(object):
    ''' a template for a InitiateDownload packet '''

    def __init__(self):
        self.name = 'InitiateDownload'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.FileData = {}    # New FileData block
        self.FileData['SimFilename'] = None    # MVT_VARIABLE
        self.FileData['ViewerFilename'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('InitiateDownload', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('FileData', SimFilename = self.FileData['SimFilename'], ViewerFilename = self.FileData['ViewerFilename']))

class AgentPausePacket(object):
    ''' a template for a AgentPause packet '''

    def __init__(self):
        self.name = 'AgentPause'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['SerialNum'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentPause', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], SerialNum = self.AgentData['SerialNum']))

class RequestInventoryAssetPacket(object):
    ''' a template for a RequestInventoryAsset packet '''

    def __init__(self):
        self.name = 'RequestInventoryAsset'

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['AgentID'] = None    # MVT_LLUUID
        self.QueryData['OwnerID'] = None    # MVT_LLUUID
        self.QueryData['ItemID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RequestInventoryAsset', Block('QueryData', QueryID = self.QueryData['QueryID'], AgentID = self.QueryData['AgentID'], OwnerID = self.QueryData['OwnerID'], ItemID = self.QueryData['ItemID']))

class RequestPayPricePacket(object):
    ''' a template for a RequestPayPrice packet '''

    def __init__(self):
        self.name = 'RequestPayPrice'

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RequestPayPrice', Block('ObjectData', ObjectID = self.ObjectData['ObjectID']))

class RequestImagePacket(object):
    ''' a template for a RequestImage packet '''

    def __init__(self):
        self.name = 'RequestImage'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.RequestImage = {}    # New RequestImage block
        self.RequestImage['Image'] = None    # MVT_LLUUID
        self.RequestImage['DiscardLevel'] = None    # MVT_S8
        self.RequestImage['DownloadPriority'] = None    # MVT_F32
        self.RequestImage['Packet'] = None    # MVT_U32
        self.RequestImage['Type'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RequestImage', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('RequestImage', Image = self.RequestImage['Image'], DiscardLevel = self.RequestImage['DiscardLevel'], DownloadPriority = self.RequestImage['DownloadPriority'], Packet = self.RequestImage['Packet'], Type = self.RequestImage['Type']))

class DirClassifiedQueryBackendPacket(object):
    ''' a template for a DirClassifiedQueryBackend packet '''

    def __init__(self):
        self.name = 'DirClassifiedQueryBackend'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['QueryText'] = None    # MVT_VARIABLE
        self.QueryData['QueryFlags'] = None    # MVT_U32
        self.QueryData['Category'] = None    # MVT_U32
        self.QueryData['EstateID'] = None    # MVT_U32
        self.QueryData['Godlike'] = None    # MVT_BOOL
        self.QueryData['QueryStart'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirClassifiedQueryBackend', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID'], QueryText = self.QueryData['QueryText'], QueryFlags = self.QueryData['QueryFlags'], Category = self.QueryData['Category'], EstateID = self.QueryData['EstateID'], Godlike = self.QueryData['Godlike'], QueryStart = self.QueryData['QueryStart']))

class EstateOwnerMessagePacket(object):
    ''' a template for a EstateOwnerMessage packet '''

    def __init__(self):
        self.name = 'EstateOwnerMessage'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['TransactionID'] = None    # MVT_LLUUID

        self.MethodData = {}    # New MethodData block
        self.MethodData['Method'] = None    # MVT_VARIABLE
        self.MethodData['Invoice'] = None    # MVT_LLUUID

        self.ParamList = {}    # New ParamList block
        self.ParamList['Parameter'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EstateOwnerMessage', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], TransactionID = self.AgentData['TransactionID']), Block('MethodData', Method = self.MethodData['Method'], Invoice = self.MethodData['Invoice']), Block('ParamList', Parameter = self.ParamList['Parameter']))

class ChatFromSimulatorPacket(object):
    ''' a template for a ChatFromSimulator packet '''

    def __init__(self):
        self.name = 'ChatFromSimulator'

        self.ChatData = {}    # New ChatData block
        self.ChatData['FromName'] = None    # MVT_VARIABLE
        self.ChatData['SourceID'] = None    # MVT_LLUUID
        self.ChatData['OwnerID'] = None    # MVT_LLUUID
        self.ChatData['SourceType'] = None    # MVT_U8
        self.ChatData['ChatType'] = None    # MVT_U8
        self.ChatData['Audible'] = None    # MVT_U8
        self.ChatData['Position'] = None    # MVT_LLVector3
        self.ChatData['Message'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ChatFromSimulator', Block('ChatData', FromName = self.ChatData['FromName'], SourceID = self.ChatData['SourceID'], OwnerID = self.ChatData['OwnerID'], SourceType = self.ChatData['SourceType'], ChatType = self.ChatData['ChatType'], Audible = self.ChatData['Audible'], Position = self.ChatData['Position'], Message = self.ChatData['Message']))

class LogDwellTimePacket(object):
    ''' a template for a LogDwellTime packet '''

    def __init__(self):
        self.name = 'LogDwellTime'

        self.DwellInfo = {}    # New DwellInfo block
        self.DwellInfo['AgentID'] = None    # MVT_LLUUID
        self.DwellInfo['SessionID'] = None    # MVT_LLUUID
        self.DwellInfo['Duration'] = None    # MVT_F32
        self.DwellInfo['SimName'] = None    # MVT_VARIABLE
        self.DwellInfo['RegionX'] = None    # MVT_U32
        self.DwellInfo['RegionY'] = None    # MVT_U32
        self.DwellInfo['AvgAgentsInView'] = None    # MVT_U8
        self.DwellInfo['AvgViewerFPS'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LogDwellTime', Block('DwellInfo', AgentID = self.DwellInfo['AgentID'], SessionID = self.DwellInfo['SessionID'], Duration = self.DwellInfo['Duration'], SimName = self.DwellInfo['SimName'], RegionX = self.DwellInfo['RegionX'], RegionY = self.DwellInfo['RegionY'], AvgAgentsInView = self.DwellInfo['AvgAgentsInView'], AvgViewerFPS = self.DwellInfo['AvgViewerFPS']))

class GroupRoleMembersRequestPacket(object):
    ''' a template for a GroupRoleMembersRequest packet '''

    def __init__(self):
        self.name = 'GroupRoleMembersRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['RequestID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupRoleMembersRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', GroupID = self.GroupData['GroupID'], RequestID = self.GroupData['RequestID']))

class LogoutRequestPacket(object):
    ''' a template for a LogoutRequest packet '''

    def __init__(self):
        self.name = 'LogoutRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LogoutRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class GroupProfileRequestPacket(object):
    ''' a template for a GroupProfileRequest packet '''

    def __init__(self):
        self.name = 'GroupProfileRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupProfileRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('GroupData', GroupID = self.GroupData['GroupID']))

class ConfirmAuctionStartPacket(object):
    ''' a template for a ConfirmAuctionStart packet '''

    def __init__(self):
        self.name = 'ConfirmAuctionStart'

        self.AuctionData = {}    # New AuctionData block
        self.AuctionData['ParcelID'] = None    # MVT_LLUUID
        self.AuctionData['AuctionID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ConfirmAuctionStart', Block('AuctionData', ParcelID = self.AuctionData['ParcelID'], AuctionID = self.AuctionData['AuctionID']))

class ObjectCategoryPacket(object):
    ''' a template for a ObjectCategory packet '''

    def __init__(self):
        self.name = 'ObjectCategory'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['LocalID'] = None    # MVT_U32
        self.ObjectData['Category'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectCategory', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', LocalID = self.ObjectData['LocalID'], Category = self.ObjectData['Category']))

class RequestObjectPropertiesFamilyPacket(object):
    ''' a template for a RequestObjectPropertiesFamily packet '''

    def __init__(self):
        self.name = 'RequestObjectPropertiesFamily'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['RequestFlags'] = None    # MVT_U32
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RequestObjectPropertiesFamily', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', RequestFlags = self.ObjectData['RequestFlags'], ObjectID = self.ObjectData['ObjectID']))

class MoneyBalanceRequestPacket(object):
    ''' a template for a MoneyBalanceRequest packet '''

    def __init__(self):
        self.name = 'MoneyBalanceRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.MoneyData = {}    # New MoneyData block
        self.MoneyData['TransactionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('MoneyBalanceRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('MoneyData', TransactionID = self.MoneyData['TransactionID']))

class ForceScriptControlReleasePacket(object):
    ''' a template for a ForceScriptControlRelease packet '''

    def __init__(self):
        self.name = 'ForceScriptControlRelease'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ForceScriptControlRelease', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class SendPostcardPacket(object):
    ''' a template for a SendPostcard packet '''

    def __init__(self):
        self.name = 'SendPostcard'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['AssetID'] = None    # MVT_LLUUID
        self.AgentData['PosGlobal'] = None    # MVT_LLVector3d
        self.AgentData['To'] = None    # MVT_VARIABLE
        self.AgentData['From'] = None    # MVT_VARIABLE
        self.AgentData['Name'] = None    # MVT_VARIABLE
        self.AgentData['Subject'] = None    # MVT_VARIABLE
        self.AgentData['Msg'] = None    # MVT_VARIABLE
        self.AgentData['AllowPublish'] = None    # MVT_BOOL
        self.AgentData['MaturePublish'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SendPostcard', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], AssetID = self.AgentData['AssetID'], PosGlobal = self.AgentData['PosGlobal'], To = self.AgentData['To'], From = self.AgentData['From'], Name = self.AgentData['Name'], Subject = self.AgentData['Subject'], Msg = self.AgentData['Msg'], AllowPublish = self.AgentData['AllowPublish'], MaturePublish = self.AgentData['MaturePublish']))

class RebakeAvatarTexturesPacket(object):
    ''' a template for a RebakeAvatarTextures packet '''

    def __init__(self):
        self.name = 'RebakeAvatarTextures'

        self.TextureData = {}    # New TextureData block
        self.TextureData['TextureID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RebakeAvatarTextures', Block('TextureData', TextureID = self.TextureData['TextureID']))

class DeRezObjectPacket(object):
    ''' a template for a DeRezObject packet '''

    def __init__(self):
        self.name = 'DeRezObject'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.AgentBlock = {}    # New AgentBlock block
        self.AgentBlock['GroupID'] = None    # MVT_LLUUID
        self.AgentBlock['Destination'] = None    # MVT_U8
        self.AgentBlock['DestinationID'] = None    # MVT_LLUUID
        self.AgentBlock['TransactionID'] = None    # MVT_LLUUID
        self.AgentBlock['PacketCount'] = None    # MVT_U8
        self.AgentBlock['PacketNumber'] = None    # MVT_U8

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectLocalID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DeRezObject', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('AgentBlock', GroupID = self.AgentBlock['GroupID'], Destination = self.AgentBlock['Destination'], DestinationID = self.AgentBlock['DestinationID'], TransactionID = self.AgentBlock['TransactionID'], PacketCount = self.AgentBlock['PacketCount'], PacketNumber = self.AgentBlock['PacketNumber']), Block('ObjectData', ObjectLocalID = self.ObjectData['ObjectLocalID']))

class AvatarPropertiesRequestBackendPacket(object):
    ''' a template for a AvatarPropertiesRequestBackend packet '''

    def __init__(self):
        self.name = 'AvatarPropertiesRequestBackend'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['AvatarID'] = None    # MVT_LLUUID
        self.AgentData['GodLevel'] = None    # MVT_U8
        self.AgentData['WebProfilesDisabled'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarPropertiesRequestBackend', Block('AgentData', AgentID = self.AgentData['AgentID'], AvatarID = self.AgentData['AvatarID'], GodLevel = self.AgentData['GodLevel'], WebProfilesDisabled = self.AgentData['WebProfilesDisabled']))

class ImprovedTerseObjectUpdatePacket(object):
    ''' a template for a ImprovedTerseObjectUpdate packet '''

    def __init__(self):
        self.name = 'ImprovedTerseObjectUpdate'

        self.RegionData = {}    # New RegionData block
        self.RegionData['RegionHandle'] = None    # MVT_U64
        self.RegionData['TimeDilation'] = None    # MVT_U16

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['Data'] = None    # MVT_VARIABLE
        self.ObjectData['TextureEntry'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ImprovedTerseObjectUpdate', Block('RegionData', RegionHandle = self.RegionData['RegionHandle'], TimeDilation = self.RegionData['TimeDilation']), Block('ObjectData', Data = self.ObjectData['Data'], TextureEntry = self.ObjectData['TextureEntry']))

class AgentDropGroupPacket(object):
    ''' a template for a AgentDropGroup packet '''

    def __init__(self):
        self.name = 'AgentDropGroup'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['GroupID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentDropGroup', Block('AgentData', AgentID = self.AgentData['AgentID'], GroupID = self.AgentData['GroupID']))

class DirLandQueryBackendPacket(object):
    ''' a template for a DirLandQueryBackend packet '''

    def __init__(self):
        self.name = 'DirLandQueryBackend'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID
        self.QueryData['QueryFlags'] = None    # MVT_U32
        self.QueryData['SearchType'] = None    # MVT_U32
        self.QueryData['Price'] = None    # MVT_S32
        self.QueryData['Area'] = None    # MVT_S32
        self.QueryData['QueryStart'] = None    # MVT_S32
        self.QueryData['EstateID'] = None    # MVT_U32
        self.QueryData['Godlike'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirLandQueryBackend', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID'], QueryFlags = self.QueryData['QueryFlags'], SearchType = self.QueryData['SearchType'], Price = self.QueryData['Price'], Area = self.QueryData['Area'], QueryStart = self.QueryData['QueryStart'], EstateID = self.QueryData['EstateID'], Godlike = self.QueryData['Godlike']))

class CopyInventoryItemPacket(object):
    ''' a template for a CopyInventoryItem packet '''

    def __init__(self):
        self.name = 'CopyInventoryItem'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.InventoryData = {}    # New InventoryData block
        self.InventoryData['CallbackID'] = None    # MVT_U32
        self.InventoryData['OldAgentID'] = None    # MVT_LLUUID
        self.InventoryData['OldItemID'] = None    # MVT_LLUUID
        self.InventoryData['NewFolderID'] = None    # MVT_LLUUID
        self.InventoryData['NewName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('CopyInventoryItem', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('InventoryData', CallbackID = self.InventoryData['CallbackID'], OldAgentID = self.InventoryData['OldAgentID'], OldItemID = self.InventoryData['OldItemID'], NewFolderID = self.InventoryData['NewFolderID'], NewName = self.InventoryData['NewName']))

class RegionHandshakePacket(object):
    ''' a template for a RegionHandshake packet '''

    def __init__(self):
        self.name = 'RegionHandshake'

        self.RegionInfo = {}    # New RegionInfo block
        self.RegionInfo['RegionFlags'] = None    # MVT_U32
        self.RegionInfo['SimAccess'] = None    # MVT_U8
        self.RegionInfo['SimName'] = None    # MVT_VARIABLE
        self.RegionInfo['SimOwner'] = None    # MVT_LLUUID
        self.RegionInfo['IsEstateManager'] = None    # MVT_BOOL
        self.RegionInfo['WaterHeight'] = None    # MVT_F32
        self.RegionInfo['BillableFactor'] = None    # MVT_F32
        self.RegionInfo['CacheID'] = None    # MVT_LLUUID
        self.RegionInfo['TerrainBase0'] = None    # MVT_LLUUID
        self.RegionInfo['TerrainBase1'] = None    # MVT_LLUUID
        self.RegionInfo['TerrainBase2'] = None    # MVT_LLUUID
        self.RegionInfo['TerrainBase3'] = None    # MVT_LLUUID
        self.RegionInfo['TerrainDetail0'] = None    # MVT_LLUUID
        self.RegionInfo['TerrainDetail1'] = None    # MVT_LLUUID
        self.RegionInfo['TerrainDetail2'] = None    # MVT_LLUUID
        self.RegionInfo['TerrainDetail3'] = None    # MVT_LLUUID
        self.RegionInfo['TerrainStartHeight00'] = None    # MVT_F32
        self.RegionInfo['TerrainStartHeight01'] = None    # MVT_F32
        self.RegionInfo['TerrainStartHeight10'] = None    # MVT_F32
        self.RegionInfo['TerrainStartHeight11'] = None    # MVT_F32
        self.RegionInfo['TerrainHeightRange00'] = None    # MVT_F32
        self.RegionInfo['TerrainHeightRange01'] = None    # MVT_F32
        self.RegionInfo['TerrainHeightRange10'] = None    # MVT_F32
        self.RegionInfo['TerrainHeightRange11'] = None    # MVT_F32

        self.RegionInfo2 = {}    # New RegionInfo2 block
        self.RegionInfo2['RegionID'] = None    # MVT_LLUUID

        self.RegionInfo3 = {}    # New RegionInfo3 block
        self.RegionInfo3['CPUClassID'] = None    # MVT_S32
        self.RegionInfo3['CPURatio'] = None    # MVT_S32
        self.RegionInfo3['ColoName'] = None    # MVT_VARIABLE
        self.RegionInfo3['ProductSKU'] = None    # MVT_VARIABLE
        self.RegionInfo3['ProductName'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('RegionHandshake', Block('RegionInfo', RegionFlags = self.RegionInfo['RegionFlags'], SimAccess = self.RegionInfo['SimAccess'], SimName = self.RegionInfo['SimName'], SimOwner = self.RegionInfo['SimOwner'], IsEstateManager = self.RegionInfo['IsEstateManager'], WaterHeight = self.RegionInfo['WaterHeight'], BillableFactor = self.RegionInfo['BillableFactor'], CacheID = self.RegionInfo['CacheID'], TerrainBase0 = self.RegionInfo['TerrainBase0'], TerrainBase1 = self.RegionInfo['TerrainBase1'], TerrainBase2 = self.RegionInfo['TerrainBase2'], TerrainBase3 = self.RegionInfo['TerrainBase3'], TerrainDetail0 = self.RegionInfo['TerrainDetail0'], TerrainDetail1 = self.RegionInfo['TerrainDetail1'], TerrainDetail2 = self.RegionInfo['TerrainDetail2'], TerrainDetail3 = self.RegionInfo['TerrainDetail3'], TerrainStartHeight00 = self.RegionInfo['TerrainStartHeight00'], TerrainStartHeight01 = self.RegionInfo['TerrainStartHeight01'], TerrainStartHeight10 = self.RegionInfo['TerrainStartHeight10'], TerrainStartHeight11 = self.RegionInfo['TerrainStartHeight11'], TerrainHeightRange00 = self.RegionInfo['TerrainHeightRange00'], TerrainHeightRange01 = self.RegionInfo['TerrainHeightRange01'], TerrainHeightRange10 = self.RegionInfo['TerrainHeightRange10'], TerrainHeightRange11 = self.RegionInfo['TerrainHeightRange11']), Block('RegionInfo2', RegionID = self.RegionInfo2['RegionID']), Block('RegionInfo3', CPUClassID = self.RegionInfo3['CPUClassID'], CPURatio = self.RegionInfo3['CPURatio'], ColoName = self.RegionInfo3['ColoName'], ProductSKU = self.RegionInfo3['ProductSKU'], ProductName = self.RegionInfo3['ProductName']))

class AvatarPickerRequestBackendPacket(object):
    ''' a template for a AvatarPickerRequestBackend packet '''

    def __init__(self):
        self.name = 'AvatarPickerRequestBackend'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['QueryID'] = None    # MVT_LLUUID
        self.AgentData['GodLevel'] = None    # MVT_U8

        self.Data = {}    # New Data block
        self.Data['Name'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AvatarPickerRequestBackend', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], QueryID = self.AgentData['QueryID'], GodLevel = self.AgentData['GodLevel']), Block('Data', Name = self.Data['Name']))

class AgentWearablesUpdatePacket(object):
    ''' a template for a AgentWearablesUpdate packet '''

    def __init__(self):
        self.name = 'AgentWearablesUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID
        self.AgentData['SerialNum'] = None    # MVT_U32

        self.WearableData = {}    # New WearableData block
        self.WearableData['ItemID'] = None    # MVT_LLUUID
        self.WearableData['AssetID'] = None    # MVT_LLUUID
        self.WearableData['WearableType'] = None    # MVT_U8

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentWearablesUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID'], SerialNum = self.AgentData['SerialNum']), Block('WearableData', ItemID = self.WearableData['ItemID'], AssetID = self.WearableData['AssetID'], WearableType = self.WearableData['WearableType']))

class SimulatorMapUpdatePacket(object):
    ''' a template for a SimulatorMapUpdate packet '''

    def __init__(self):
        self.name = 'SimulatorMapUpdate'

        self.MapData = {}    # New MapData block
        self.MapData['Flags'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('SimulatorMapUpdate', Block('MapData', Flags = self.MapData['Flags']))

class JoinGroupReplyPacket(object):
    ''' a template for a JoinGroupReply packet '''

    def __init__(self):
        self.name = 'JoinGroupReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.GroupData = {}    # New GroupData block
        self.GroupData['GroupID'] = None    # MVT_LLUUID
        self.GroupData['Success'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('JoinGroupReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('GroupData', GroupID = self.GroupData['GroupID'], Success = self.GroupData['Success']))

class ChatPassPacket(object):
    ''' a template for a ChatPass packet '''

    def __init__(self):
        self.name = 'ChatPass'

        self.ChatData = {}    # New ChatData block
        self.ChatData['Channel'] = None    # MVT_S32
        self.ChatData['Position'] = None    # MVT_LLVector3
        self.ChatData['ID'] = None    # MVT_LLUUID
        self.ChatData['OwnerID'] = None    # MVT_LLUUID
        self.ChatData['Name'] = None    # MVT_VARIABLE
        self.ChatData['SourceType'] = None    # MVT_U8
        self.ChatData['Type'] = None    # MVT_U8
        self.ChatData['Radius'] = None    # MVT_F32
        self.ChatData['SimAccess'] = None    # MVT_U8
        self.ChatData['Message'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ChatPass', Block('ChatData', Channel = self.ChatData['Channel'], Position = self.ChatData['Position'], ID = self.ChatData['ID'], OwnerID = self.ChatData['OwnerID'], Name = self.ChatData['Name'], SourceType = self.ChatData['SourceType'], Type = self.ChatData['Type'], Radius = self.ChatData['Radius'], SimAccess = self.ChatData['SimAccess'], Message = self.ChatData['Message']))

class ObjectGrabUpdatePacket(object):
    ''' a template for a ObjectGrabUpdate packet '''

    def __init__(self):
        self.name = 'ObjectGrabUpdate'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        self.ObjectData['GrabOffsetInitial'] = None    # MVT_LLVector3
        self.ObjectData['GrabPosition'] = None    # MVT_LLVector3
        self.ObjectData['TimeSinceLast'] = None    # MVT_U32

        self.SurfaceInfo = {}    # New SurfaceInfo block
        self.SurfaceInfo['UVCoord'] = None    # MVT_LLVector3
        self.SurfaceInfo['STCoord'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectGrabUpdate', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ObjectData', ObjectID = self.ObjectData['ObjectID'], GrabOffsetInitial = self.ObjectData['GrabOffsetInitial'], GrabPosition = self.ObjectData['GrabPosition'], TimeSinceLast = self.ObjectData['TimeSinceLast']), Block('SurfaceInfo', UVCoord = self.SurfaceInfo['UVCoord'], STCoord = self.SurfaceInfo['STCoord']))

class ObjectPropertiesFamilyPacket(object):
    ''' a template for a ObjectPropertiesFamily packet '''

    def __init__(self):
        self.name = 'ObjectPropertiesFamily'

        self.ObjectData = {}    # New ObjectData block
        self.ObjectData['RequestFlags'] = None    # MVT_U32
        self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        self.ObjectData['OwnerID'] = None    # MVT_LLUUID
        self.ObjectData['GroupID'] = None    # MVT_LLUUID
        self.ObjectData['BaseMask'] = None    # MVT_U32
        self.ObjectData['OwnerMask'] = None    # MVT_U32
        self.ObjectData['GroupMask'] = None    # MVT_U32
        self.ObjectData['EveryoneMask'] = None    # MVT_U32
        self.ObjectData['NextOwnerMask'] = None    # MVT_U32
        self.ObjectData['OwnershipCost'] = None    # MVT_S32
        self.ObjectData['SaleType'] = None    # MVT_U8
        self.ObjectData['SalePrice'] = None    # MVT_S32
        self.ObjectData['Category'] = None    # MVT_U32
        self.ObjectData['LastOwnerID'] = None    # MVT_LLUUID
        self.ObjectData['Name'] = None    # MVT_VARIABLE
        self.ObjectData['Description'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ObjectPropertiesFamily', Block('ObjectData', RequestFlags = self.ObjectData['RequestFlags'], ObjectID = self.ObjectData['ObjectID'], OwnerID = self.ObjectData['OwnerID'], GroupID = self.ObjectData['GroupID'], BaseMask = self.ObjectData['BaseMask'], OwnerMask = self.ObjectData['OwnerMask'], GroupMask = self.ObjectData['GroupMask'], EveryoneMask = self.ObjectData['EveryoneMask'], NextOwnerMask = self.ObjectData['NextOwnerMask'], OwnershipCost = self.ObjectData['OwnershipCost'], SaleType = self.ObjectData['SaleType'], SalePrice = self.ObjectData['SalePrice'], Category = self.ObjectData['Category'], LastOwnerID = self.ObjectData['LastOwnerID'], Name = self.ObjectData['Name'], Description = self.ObjectData['Description']))

class OnlineNotificationPacket(object):
    ''' a template for a OnlineNotification packet '''

    def __init__(self):
        self.name = 'OnlineNotification'

        self.AgentBlock = {}    # New AgentBlock block
        self.AgentBlock['AgentID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('OnlineNotification', Block('AgentBlock', AgentID = self.AgentBlock['AgentID']))

class ParcelDisableObjectsPacket(object):
    ''' a template for a ParcelDisableObjects packet '''

    def __init__(self):
        self.name = 'ParcelDisableObjects'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ParcelData = {}    # New ParcelData block
        self.ParcelData['LocalID'] = None    # MVT_S32
        self.ParcelData['ReturnType'] = None    # MVT_U32

        self.TaskIDs = {}    # New TaskIDs block
        self.TaskIDs['TaskID'] = None    # MVT_LLUUID

        self.OwnerIDs = {}    # New OwnerIDs block
        self.OwnerIDs['OwnerID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ParcelDisableObjects', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ParcelData', LocalID = self.ParcelData['LocalID'], ReturnType = self.ParcelData['ReturnType']), Block('TaskIDs', TaskID = self.TaskIDs['TaskID']), Block('OwnerIDs', OwnerID = self.OwnerIDs['OwnerID']))

class LandStatRequestPacket(object):
    ''' a template for a LandStatRequest packet '''

    def __init__(self):
        self.name = 'LandStatRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.RequestData = {}    # New RequestData block
        self.RequestData['ReportType'] = None    # MVT_U32
        self.RequestData['RequestFlags'] = None    # MVT_U32
        self.RequestData['Filter'] = None    # MVT_VARIABLE
        self.RequestData['ParcelLocalID'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('LandStatRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('RequestData', ReportType = self.RequestData['ReportType'], RequestFlags = self.RequestData['RequestFlags'], Filter = self.RequestData['Filter'], ParcelLocalID = self.RequestData['ParcelLocalID']))

class ChatFromViewerPacket(object):
    ''' a template for a ChatFromViewer packet '''

    def __init__(self):
        self.name = 'ChatFromViewer'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ChatData = {}    # New ChatData block
        self.ChatData['Message'] = None    # MVT_VARIABLE
        self.ChatData['Type'] = None    # MVT_U8
        self.ChatData['Channel'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('ChatFromViewer', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ChatData', Message = self.ChatData['Message'], Type = self.ChatData['Type'], Channel = self.ChatData['Channel']))

class InternalScriptMailPacket(object):
    ''' a template for a InternalScriptMail packet '''

    def __init__(self):
        self.name = 'InternalScriptMail'

        self.DataBlock = {}    # New DataBlock block
        self.DataBlock['From'] = None    # MVT_VARIABLE
        self.DataBlock['To'] = None    # MVT_LLUUID
        self.DataBlock['Subject'] = None    # MVT_VARIABLE
        self.DataBlock['Body'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('InternalScriptMail', Block('DataBlock', From = self.DataBlock['From'], To = self.DataBlock['To'], Subject = self.DataBlock['Subject'], Body = self.DataBlock['Body']))

class TerminateFriendshipPacket(object):
    ''' a template for a TerminateFriendship packet '''

    def __init__(self):
        self.name = 'TerminateFriendship'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.ExBlock = {}    # New ExBlock block
        self.ExBlock['OtherID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('TerminateFriendship', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('ExBlock', OtherID = self.ExBlock['OtherID']))

class EventInfoRequestPacket(object):
    ''' a template for a EventInfoRequest packet '''

    def __init__(self):
        self.name = 'EventInfoRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.EventData = {}    # New EventData block
        self.EventData['EventID'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('EventInfoRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('EventData', EventID = self.EventData['EventID']))

class AgentRequestSitPacket(object):
    ''' a template for a AgentRequestSit packet '''

    def __init__(self):
        self.name = 'AgentRequestSit'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.TargetObject = {}    # New TargetObject block
        self.TargetObject['TargetID'] = None    # MVT_LLUUID
        self.TargetObject['Offset'] = None    # MVT_LLVector3

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentRequestSit', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('TargetObject', TargetID = self.TargetObject['TargetID'], Offset = self.TargetObject['Offset']))

class UserInfoRequestPacket(object):
    ''' a template for a UserInfoRequest packet '''

    def __init__(self):
        self.name = 'UserInfoRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('UserInfoRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']))

class GroupNoticesListRequestPacket(object):
    ''' a template for a GroupNoticesListRequest packet '''

    def __init__(self):
        self.name = 'GroupNoticesListRequest'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['SessionID'] = None    # MVT_LLUUID

        self.Data = {}    # New Data block
        self.Data['GroupID'] = None    # MVT_LLUUID

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('GroupNoticesListRequest', Block('AgentData', AgentID = self.AgentData['AgentID'], SessionID = self.AgentData['SessionID']), Block('Data', GroupID = self.Data['GroupID']))

class InventoryDescendentsPacket(object):
    ''' a template for a InventoryDescendents packet '''

    def __init__(self):
        self.name = 'InventoryDescendents'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID
        self.AgentData['FolderID'] = None    # MVT_LLUUID
        self.AgentData['OwnerID'] = None    # MVT_LLUUID
        self.AgentData['Version'] = None    # MVT_S32
        self.AgentData['Descendents'] = None    # MVT_S32

        self.FolderData = {}    # New FolderData block
        self.FolderData['FolderID'] = None    # MVT_LLUUID
        self.FolderData['ParentID'] = None    # MVT_LLUUID
        self.FolderData['Type'] = None    # MVT_S8
        self.FolderData['Name'] = None    # MVT_VARIABLE

        self.ItemData = {}    # New ItemData block
        self.ItemData['ItemID'] = None    # MVT_LLUUID
        self.ItemData['FolderID'] = None    # MVT_LLUUID
        self.ItemData['CreatorID'] = None    # MVT_LLUUID
        self.ItemData['OwnerID'] = None    # MVT_LLUUID
        self.ItemData['GroupID'] = None    # MVT_LLUUID
        self.ItemData['BaseMask'] = None    # MVT_U32
        self.ItemData['OwnerMask'] = None    # MVT_U32
        self.ItemData['GroupMask'] = None    # MVT_U32
        self.ItemData['EveryoneMask'] = None    # MVT_U32
        self.ItemData['NextOwnerMask'] = None    # MVT_U32
        self.ItemData['GroupOwned'] = None    # MVT_BOOL
        self.ItemData['AssetID'] = None    # MVT_LLUUID
        self.ItemData['Type'] = None    # MVT_S8
        self.ItemData['InvType'] = None    # MVT_S8
        self.ItemData['Flags'] = None    # MVT_U32
        self.ItemData['SaleType'] = None    # MVT_U8
        self.ItemData['SalePrice'] = None    # MVT_S32
        self.ItemData['Name'] = None    # MVT_VARIABLE
        self.ItemData['Description'] = None    # MVT_VARIABLE
        self.ItemData['CreationDate'] = None    # MVT_S32
        self.ItemData['CRC'] = None    # MVT_U32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('InventoryDescendents', Block('AgentData', AgentID = self.AgentData['AgentID'], FolderID = self.AgentData['FolderID'], OwnerID = self.AgentData['OwnerID'], Version = self.AgentData['Version'], Descendents = self.AgentData['Descendents']), Block('FolderData', FolderID = self.FolderData['FolderID'], ParentID = self.FolderData['ParentID'], Type = self.FolderData['Type'], Name = self.FolderData['Name']), Block('ItemData', ItemID = self.ItemData['ItemID'], FolderID = self.ItemData['FolderID'], CreatorID = self.ItemData['CreatorID'], OwnerID = self.ItemData['OwnerID'], GroupID = self.ItemData['GroupID'], BaseMask = self.ItemData['BaseMask'], OwnerMask = self.ItemData['OwnerMask'], GroupMask = self.ItemData['GroupMask'], EveryoneMask = self.ItemData['EveryoneMask'], NextOwnerMask = self.ItemData['NextOwnerMask'], GroupOwned = self.ItemData['GroupOwned'], AssetID = self.ItemData['AssetID'], Type = self.ItemData['Type'], InvType = self.ItemData['InvType'], Flags = self.ItemData['Flags'], SaleType = self.ItemData['SaleType'], SalePrice = self.ItemData['SalePrice'], Name = self.ItemData['Name'], Description = self.ItemData['Description'], CreationDate = self.ItemData['CreationDate'], CRC = self.ItemData['CRC']))

class AbortXferPacket(object):
    ''' a template for a AbortXfer packet '''

    def __init__(self):
        self.name = 'AbortXfer'

        self.XferID = {}    # New XferID block
        self.XferID['ID'] = None    # MVT_U64
        self.XferID['Result'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AbortXfer', Block('XferID', ID = self.XferID['ID'], Result = self.XferID['Result']))

class AtomicPassObjectPacket(object):
    ''' a template for a AtomicPassObject packet '''

    def __init__(self):
        self.name = 'AtomicPassObject'

        self.TaskData = {}    # New TaskData block
        self.TaskData['TaskID'] = None    # MVT_LLUUID
        self.TaskData['AttachmentNeedsSave'] = None    # MVT_BOOL

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AtomicPassObject', Block('TaskData', TaskID = self.TaskData['TaskID'], AttachmentNeedsSave = self.TaskData['AttachmentNeedsSave']))

class DirPeopleReplyPacket(object):
    ''' a template for a DirPeopleReply packet '''

    def __init__(self):
        self.name = 'DirPeopleReply'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.QueryData = {}    # New QueryData block
        self.QueryData['QueryID'] = None    # MVT_LLUUID

        self.QueryReplies = {}    # New QueryReplies block
        self.QueryReplies['FirstName'] = None    # MVT_VARIABLE
        self.QueryReplies['LastName'] = None    # MVT_VARIABLE
        self.QueryReplies['Group'] = None    # MVT_VARIABLE
        self.QueryReplies['Online'] = None    # MVT_BOOL
        self.QueryReplies['Reputation'] = None    # MVT_S32

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('DirPeopleReply', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('QueryData', QueryID = self.QueryData['QueryID']), Block('QueryReplies', FirstName = self.QueryReplies['FirstName'], LastName = self.QueryReplies['LastName'], Group = self.QueryReplies['Group'], Online = self.QueryReplies['Online'], Reputation = self.QueryReplies['Reputation']))

class AgentAlertMessagePacket(object):
    ''' a template for a AgentAlertMessage packet '''

    def __init__(self):
        self.name = 'AgentAlertMessage'

        self.AgentData = {}    # New AgentData block
        self.AgentData['AgentID'] = None    # MVT_LLUUID

        self.AlertData = {}    # New AlertData block
        self.AlertData['Modal'] = None    # MVT_BOOL
        self.AlertData['Message'] = None    # MVT_VARIABLE

    def __call__(self):
        ''' transforms the attributes into a Message '''

        return Message('AgentAlertMessage', Block('AgentData', AgentID = self.AgentData['AgentID']), Block('AlertData', Modal = self.AlertData['Modal'], Message = self.AlertData['Message']))

