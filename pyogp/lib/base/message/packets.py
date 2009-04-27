from pyogp.lib.base.message.message import Message, Block

class RegionPresenceRequestByRegionIDPacket(object):
    ''' a template for a RegionPresenceRequestByRegionID packet '''

    def __init__(self, RegionDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RegionPresenceRequestByRegionID'

        if RegionDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.RegionDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.RegionData = {}
            self.RegionData['RegionID'] = None    # MVT_LLUUID
        else:
            self.RegionDataBlocks = RegionDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.RegionDataBlocks:
            args.append(Block('RegionData', RegionID=block['RegionID']))

        return Message('RegionPresenceRequestByRegionID', args)

class GroupAccountSummaryRequestPacket(object):
    ''' a template for a GroupAccountSummaryRequest packet '''

    def __init__(self, AgentDataBlock = {}, MoneyDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupAccountSummaryRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MoneyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MoneyData = {}    # New MoneyData block
            self.MoneyData['RequestID'] = None    # MVT_LLUUID
            self.MoneyData['IntervalDays'] = None    # MVT_S32
            self.MoneyData['CurrentInterval'] = None    # MVT_S32
        else:
            self.MoneyData = MoneyDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('MoneyData', RequestID=self.MoneyData['RequestID'], IntervalDays=self.MoneyData['IntervalDays'], CurrentInterval=self.MoneyData['CurrentInterval']))

        return Message('GroupAccountSummaryRequest', args)

class CancelAuctionPacket(object):
    ''' a template for a CancelAuction packet '''

    def __init__(self, ParcelDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CancelAuction'

        if ParcelDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParcelDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParcelData = {}
            self.ParcelData['ParcelID'] = None    # MVT_LLUUID
        else:
            self.ParcelDataBlocks = ParcelDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.ParcelDataBlocks:
            args.append(Block('ParcelData', ParcelID=block['ParcelID']))

        return Message('CancelAuction', args)

class StateSavePacket(object):
    ''' a template for a StateSave packet '''

    def __init__(self, AgentDataBlock = {}, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'StateSave'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['Filename'] = None    # MVT_VARIABLE
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('DataBlock', Filename=self.DataBlock['Filename']))

        return Message('StateSave', args)

class UpdateAttachmentPacket(object):
    ''' a template for a UpdateAttachment packet '''

    def __init__(self, AgentDataBlock = {}, AttachmentBlockBlock = {}, OperationDataBlock = {}, InventoryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UpdateAttachment'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if AttachmentBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AttachmentBlock = {}    # New AttachmentBlock block
            self.AttachmentBlock['AttachmentPoint'] = None    # MVT_U8
        else:
            self.AttachmentBlock = AttachmentBlockBlock

        if OperationDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.OperationData = {}    # New OperationData block
            self.OperationData['AddItem'] = None    # MVT_BOOL
            self.OperationData['UseExistingAsset'] = None    # MVT_BOOL
        else:
            self.OperationData = OperationDataBlock

        if InventoryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.InventoryData = InventoryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('AttachmentBlock', AttachmentPoint=self.AttachmentBlock['AttachmentPoint']))
        args.append(Block('OperationData', AddItem=self.OperationData['AddItem'], UseExistingAsset=self.OperationData['UseExistingAsset']))
        args.append(Block('InventoryData', ItemID=self.InventoryData['ItemID'], FolderID=self.InventoryData['FolderID'], CreatorID=self.InventoryData['CreatorID'], OwnerID=self.InventoryData['OwnerID'], GroupID=self.InventoryData['GroupID'], BaseMask=self.InventoryData['BaseMask'], OwnerMask=self.InventoryData['OwnerMask'], GroupMask=self.InventoryData['GroupMask'], EveryoneMask=self.InventoryData['EveryoneMask'], NextOwnerMask=self.InventoryData['NextOwnerMask'], GroupOwned=self.InventoryData['GroupOwned'], AssetID=self.InventoryData['AssetID'], Type=self.InventoryData['Type'], InvType=self.InventoryData['InvType'], Flags=self.InventoryData['Flags'], SaleType=self.InventoryData['SaleType'], SalePrice=self.InventoryData['SalePrice'], Name=self.InventoryData['Name'], Description=self.InventoryData['Description'], CreationDate=self.InventoryData['CreationDate'], CRC=self.InventoryData['CRC']))

        return Message('UpdateAttachment', args)

class ParcelJoinPacket(object):
    ''' a template for a ParcelJoin packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelJoin'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['West'] = None    # MVT_F32
            self.ParcelData['South'] = None    # MVT_F32
            self.ParcelData['East'] = None    # MVT_F32
            self.ParcelData['North'] = None    # MVT_F32
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', West=self.ParcelData['West'], South=self.ParcelData['South'], East=self.ParcelData['East'], North=self.ParcelData['North']))

        return Message('ParcelJoin', args)

class ObjectDeletePacket(object):
    ''' a template for a ObjectDelete packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectDelete'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['Force'] = None    # MVT_BOOL
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], Force=self.AgentData['Force']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('ObjectDelete', args)

class RegionHandleRequestPacket(object):
    ''' a template for a RegionHandleRequest packet '''

    def __init__(self, RequestBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RegionHandleRequest'

        if RequestBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RequestBlock = {}    # New RequestBlock block
            self.RequestBlock['RegionID'] = None    # MVT_LLUUID
        else:
            self.RequestBlock = RequestBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('RequestBlock', RegionID=self.RequestBlock['RegionID']))

        return Message('RegionHandleRequest', args)

class ScriptQuestionPacket(object):
    ''' a template for a ScriptQuestion packet '''

    def __init__(self, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptQuestion'

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['TaskID'] = None    # MVT_LLUUID
            self.Data['ItemID'] = None    # MVT_LLUUID
            self.Data['ObjectName'] = None    # MVT_VARIABLE
            self.Data['ObjectOwner'] = None    # MVT_VARIABLE
            self.Data['Questions'] = None    # MVT_S32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Data', TaskID=self.Data['TaskID'], ItemID=self.Data['ItemID'], ObjectName=self.Data['ObjectName'], ObjectOwner=self.Data['ObjectOwner'], Questions=self.Data['Questions']))

        return Message('ScriptQuestion', args)

class CreateTrustedCircuitPacket(object):
    ''' a template for a CreateTrustedCircuit packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CreateTrustedCircuit'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['EndPointID'] = None    # MVT_LLUUID
            self.DataBlock['Digest'] = None    # MVT_FIXED
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', EndPointID=self.DataBlock['EndPointID'], Digest=self.DataBlock['Digest']))

        return Message('CreateTrustedCircuit', args)

class DataHomeLocationRequestPacket(object):
    ''' a template for a DataHomeLocationRequest packet '''

    def __init__(self, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DataHomeLocationRequest'

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['AgentID'] = None    # MVT_LLUUID
            self.Info['KickedFromEstateID'] = None    # MVT_U32
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Info', AgentID=self.Info['AgentID'], KickedFromEstateID=self.Info['KickedFromEstateID']))

        return Message('DataHomeLocationRequest', args)

class RemoveTaskInventoryPacket(object):
    ''' a template for a RemoveTaskInventory packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RemoveTaskInventory'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.InventoryData = {}    # New InventoryData block
            self.InventoryData['LocalID'] = None    # MVT_U32
            self.InventoryData['ItemID'] = None    # MVT_LLUUID
        else:
            self.InventoryData = InventoryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('InventoryData', LocalID=self.InventoryData['LocalID'], ItemID=self.InventoryData['ItemID']))

        return Message('RemoveTaskInventory', args)

class SystemKickUserPacket(object):
    ''' a template for a SystemKickUser packet '''

    def __init__(self, AgentInfoBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SystemKickUser'

        if AgentInfoBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.AgentInfoBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.AgentInfo = {}
            self.AgentInfo['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentInfoBlocks = AgentInfoBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.AgentInfoBlocks:
            args.append(Block('AgentInfo', AgentID=block['AgentID']))

        return Message('SystemKickUser', args)

class ConfirmXferPacketPacket(object):
    ''' a template for a ConfirmXferPacket packet '''

    def __init__(self, XferIDBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ConfirmXferPacket'

        if XferIDBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.XferID = {}    # New XferID block
            self.XferID['ID'] = None    # MVT_U64
            self.XferID['Packet'] = None    # MVT_U32
        else:
            self.XferID = XferIDBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('XferID', ID=self.XferID['ID'], Packet=self.XferID['Packet']))

        return Message('ConfirmXferPacket', args)

class ClassifiedInfoUpdatePacket(object):
    ''' a template for a ClassifiedInfoUpdate packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ClassifiedInfoUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', ClassifiedID=self.Data['ClassifiedID'], Category=self.Data['Category'], Name=self.Data['Name'], Desc=self.Data['Desc'], ParcelID=self.Data['ParcelID'], ParentEstate=self.Data['ParentEstate'], SnapshotID=self.Data['SnapshotID'], PosGlobal=self.Data['PosGlobal'], ClassifiedFlags=self.Data['ClassifiedFlags'], PriceForListing=self.Data['PriceForListing']))

        return Message('ClassifiedInfoUpdate', args)

class ReportAutosaveCrashPacket(object):
    ''' a template for a ReportAutosaveCrash packet '''

    def __init__(self, AutosaveDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ReportAutosaveCrash'

        if AutosaveDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AutosaveData = {}    # New AutosaveData block
            self.AutosaveData['PID'] = None    # MVT_S32
            self.AutosaveData['Status'] = None    # MVT_S32
        else:
            self.AutosaveData = AutosaveDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AutosaveData', PID=self.AutosaveData['PID'], Status=self.AutosaveData['Status']))

        return Message('ReportAutosaveCrash', args)

class SetSimPresenceInDatabasePacket(object):
    ''' a template for a SetSimPresenceInDatabase packet '''

    def __init__(self, SimDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SetSimPresenceInDatabase'

        if SimDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SimData = {}    # New SimData block
            self.SimData['RegionID'] = None    # MVT_LLUUID
            self.SimData['HostName'] = None    # MVT_VARIABLE
            self.SimData['GridX'] = None    # MVT_U32
            self.SimData['GridY'] = None    # MVT_U32
            self.SimData['PID'] = None    # MVT_S32
            self.SimData['AgentCount'] = None    # MVT_S32
            self.SimData['TimeToLive'] = None    # MVT_S32
            self.SimData['Status'] = None    # MVT_VARIABLE
        else:
            self.SimData = SimDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('SimData', RegionID=self.SimData['RegionID'], HostName=self.SimData['HostName'], GridX=self.SimData['GridX'], GridY=self.SimData['GridY'], PID=self.SimData['PID'], AgentCount=self.SimData['AgentCount'], TimeToLive=self.SimData['TimeToLive'], Status=self.SimData['Status']))

        return Message('SetSimPresenceInDatabase', args)

class GroupVoteHistoryItemReplyPacket(object):
    ''' a template for a GroupVoteHistoryItemReply packet '''

    def __init__(self, AgentDataBlock = {}, TransactionDataBlock = {}, HistoryItemDataBlock = {}, VoteItemBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupVoteHistoryItemReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if TransactionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransactionData = {}    # New TransactionData block
            self.TransactionData['TransactionID'] = None    # MVT_LLUUID
            self.TransactionData['TotalNumItems'] = None    # MVT_U32
        else:
            self.TransactionData = TransactionDataBlock

        if HistoryItemDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.HistoryItemData = HistoryItemDataBlock

        if VoteItemBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.VoteItemBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.VoteItem = {}
            self.VoteItem['CandidateID'] = None    # MVT_LLUUID
            self.VoteItem['VoteCast'] = None    # MVT_VARIABLE
            self.VoteItem['NumVotes'] = None    # MVT_S32
        else:
            self.VoteItemBlocks = VoteItemBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('TransactionData', TransactionID=self.TransactionData['TransactionID'], TotalNumItems=self.TransactionData['TotalNumItems']))
        args.append(Block('HistoryItemData', VoteID=self.HistoryItemData['VoteID'], TerseDateID=self.HistoryItemData['TerseDateID'], StartDateTime=self.HistoryItemData['StartDateTime'], EndDateTime=self.HistoryItemData['EndDateTime'], VoteInitiator=self.HistoryItemData['VoteInitiator'], VoteType=self.HistoryItemData['VoteType'], VoteResult=self.HistoryItemData['VoteResult'], Majority=self.HistoryItemData['Majority'], Quorum=self.HistoryItemData['Quorum'], ProposalText=self.HistoryItemData['ProposalText']))
        for block in self.VoteItemBlocks:
            args.append(Block('VoteItem', CandidateID=block['CandidateID'], VoteCast=block['VoteCast'], NumVotes=block['NumVotes']))

        return Message('GroupVoteHistoryItemReply', args)

class ChildAgentUnknownPacket(object):
    ''' a template for a ChildAgentUnknown packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ChildAgentUnknown'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('ChildAgentUnknown', args)

class ObjectSpinStartPacket(object):
    ''' a template for a ObjectSpinStart packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectSpinStart'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.ObjectData = ObjectDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ObjectData', ObjectID=self.ObjectData['ObjectID']))

        return Message('ObjectSpinStart', args)

class CreateGroupReplyPacket(object):
    ''' a template for a CreateGroupReply packet '''

    def __init__(self, AgentDataBlock = {}, ReplyDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CreateGroupReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ReplyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ReplyData = {}    # New ReplyData block
            self.ReplyData['GroupID'] = None    # MVT_LLUUID
            self.ReplyData['Success'] = None    # MVT_BOOL
            self.ReplyData['Message'] = None    # MVT_VARIABLE
        else:
            self.ReplyData = ReplyDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('ReplyData', GroupID=self.ReplyData['GroupID'], Success=self.ReplyData['Success'], Message=self.ReplyData['Message']))

        return Message('CreateGroupReply', args)

class ParcelDwellReplyPacket(object):
    ''' a template for a ParcelDwellReply packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelDwellReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['LocalID'] = None    # MVT_S32
            self.Data['ParcelID'] = None    # MVT_LLUUID
            self.Data['Dwell'] = None    # MVT_F32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('Data', LocalID=self.Data['LocalID'], ParcelID=self.Data['ParcelID'], Dwell=self.Data['Dwell']))

        return Message('ParcelDwellReply', args)

class ObjectShapePacket(object):
    ''' a template for a ObjectShape packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectShape'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
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
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], PathCurve=block['PathCurve'], ProfileCurve=block['ProfileCurve'], PathBegin=block['PathBegin'], PathEnd=block['PathEnd'], PathScaleX=block['PathScaleX'], PathScaleY=block['PathScaleY'], PathShearX=block['PathShearX'], PathShearY=block['PathShearY'], PathTwist=block['PathTwist'], PathTwistBegin=block['PathTwistBegin'], PathRadiusOffset=block['PathRadiusOffset'], PathTaperX=block['PathTaperX'], PathTaperY=block['PathTaperY'], PathRevolutions=block['PathRevolutions'], PathSkew=block['PathSkew'], ProfileBegin=block['ProfileBegin'], ProfileEnd=block['ProfileEnd'], ProfileHollow=block['ProfileHollow']))

        return Message('ObjectShape', args)

class MuteListUpdatePacket(object):
    ''' a template for a MuteListUpdate packet '''

    def __init__(self, MuteDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MuteListUpdate'

        if MuteDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MuteData = {}    # New MuteData block
            self.MuteData['AgentID'] = None    # MVT_LLUUID
            self.MuteData['Filename'] = None    # MVT_VARIABLE
        else:
            self.MuteData = MuteDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('MuteData', AgentID=self.MuteData['AgentID'], Filename=self.MuteData['Filename']))

        return Message('MuteListUpdate', args)

class ParcelPropertiesRequestByIDPacket(object):
    ''' a template for a ParcelPropertiesRequestByID packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelPropertiesRequestByID'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['SequenceID'] = None    # MVT_S32
            self.ParcelData['LocalID'] = None    # MVT_S32
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', SequenceID=self.ParcelData['SequenceID'], LocalID=self.ParcelData['LocalID']))

        return Message('ParcelPropertiesRequestByID', args)

class UpdateUserInfoPacket(object):
    ''' a template for a UpdateUserInfo packet '''

    def __init__(self, AgentDataBlock = {}, UserDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UpdateUserInfo'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if UserDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.UserData = {}    # New UserData block
            self.UserData['IMViaEMail'] = None    # MVT_BOOL
            self.UserData['DirectoryVisibility'] = None    # MVT_VARIABLE
        else:
            self.UserData = UserDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('UserData', IMViaEMail=self.UserData['IMViaEMail'], DirectoryVisibility=self.UserData['DirectoryVisibility']))

        return Message('UpdateUserInfo', args)

class RedoPacket(object):
    ''' a template for a Redo packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'Redo'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectID=block['ObjectID']))

        return Message('Redo', args)

class FetchInventoryReplyPacket(object):
    ''' a template for a FetchInventoryReply packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'FetchInventoryReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
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
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', ItemID=block['ItemID'], FolderID=block['FolderID'], CreatorID=block['CreatorID'], OwnerID=block['OwnerID'], GroupID=block['GroupID'], BaseMask=block['BaseMask'], OwnerMask=block['OwnerMask'], GroupMask=block['GroupMask'], EveryoneMask=block['EveryoneMask'], NextOwnerMask=block['NextOwnerMask'], GroupOwned=block['GroupOwned'], AssetID=block['AssetID'], Type=block['Type'], InvType=block['InvType'], Flags=block['Flags'], SaleType=block['SaleType'], SalePrice=block['SalePrice'], Name=block['Name'], Description=block['Description'], CreationDate=block['CreationDate'], CRC=block['CRC']))

        return Message('FetchInventoryReply', args)

class AvatarInterestsUpdatePacket(object):
    ''' a template for a AvatarInterestsUpdate packet '''

    def __init__(self, AgentDataBlock = {}, PropertiesDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarInterestsUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if PropertiesDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.PropertiesData = {}    # New PropertiesData block
            self.PropertiesData['WantToMask'] = None    # MVT_U32
            self.PropertiesData['WantToText'] = None    # MVT_VARIABLE
            self.PropertiesData['SkillsMask'] = None    # MVT_U32
            self.PropertiesData['SkillsText'] = None    # MVT_VARIABLE
            self.PropertiesData['LanguagesText'] = None    # MVT_VARIABLE
        else:
            self.PropertiesData = PropertiesDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('PropertiesData', WantToMask=self.PropertiesData['WantToMask'], WantToText=self.PropertiesData['WantToText'], SkillsMask=self.PropertiesData['SkillsMask'], SkillsText=self.PropertiesData['SkillsText'], LanguagesText=self.PropertiesData['LanguagesText']))

        return Message('AvatarInterestsUpdate', args)

class ImagePacketPacket(object):
    ''' a template for a ImagePacket packet '''

    def __init__(self, ImageIDBlock = {}, ImageDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ImagePacket'

        if ImageIDBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ImageID = {}    # New ImageID block
            self.ImageID['ID'] = None    # MVT_LLUUID
            self.ImageID['Packet'] = None    # MVT_U16
        else:
            self.ImageID = ImageIDBlock

        if ImageDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ImageData = {}    # New ImageData block
            self.ImageData['Data'] = None    # MVT_VARIABLE
        else:
            self.ImageData = ImageDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ImageID', ID=self.ImageID['ID'], Packet=self.ImageID['Packet']))
        args.append(Block('ImageData', Data=self.ImageData['Data']))

        return Message('ImagePacket', args)

class ParcelInfoRequestPacket(object):
    ''' a template for a ParcelInfoRequest packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelInfoRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['ParcelID'] = None    # MVT_LLUUID
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', ParcelID=self.Data['ParcelID']))

        return Message('ParcelInfoRequest', args)

class GrantGodlikePowersPacket(object):
    ''' a template for a GrantGodlikePowers packet '''

    def __init__(self, AgentDataBlock = {}, GrantDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GrantGodlikePowers'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GrantDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GrantData = {}    # New GrantData block
            self.GrantData['GodLevel'] = None    # MVT_U8
            self.GrantData['Token'] = None    # MVT_LLUUID
        else:
            self.GrantData = GrantDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GrantData', GodLevel=self.GrantData['GodLevel'], Token=self.GrantData['Token']))

        return Message('GrantGodlikePowers', args)

class ViewerFrozenMessagePacket(object):
    ''' a template for a ViewerFrozenMessage packet '''

    def __init__(self, FrozenDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ViewerFrozenMessage'

        if FrozenDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.FrozenData = {}    # New FrozenData block
            self.FrozenData['Data'] = None    # MVT_BOOL
        else:
            self.FrozenData = FrozenDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('FrozenData', Data=self.FrozenData['Data']))

        return Message('ViewerFrozenMessage', args)

class RegionPresenceResponsePacket(object):
    ''' a template for a RegionPresenceResponse packet '''

    def __init__(self, RegionDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RegionPresenceResponse'

        if RegionDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.RegionDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.RegionData = {}
            self.RegionData['RegionID'] = None    # MVT_LLUUID
            self.RegionData['RegionHandle'] = None    # MVT_U64
            self.RegionData['InternalRegionIP'] = None    # MVT_IP_ADDR
            self.RegionData['ExternalRegionIP'] = None    # MVT_IP_ADDR
            self.RegionData['RegionPort'] = None    # MVT_IP_PORT
            self.RegionData['ValidUntil'] = None    # MVT_F64
            self.RegionData['Message'] = None    # MVT_VARIABLE
        else:
            self.RegionDataBlocks = RegionDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.RegionDataBlocks:
            args.append(Block('RegionData', RegionID=block['RegionID'], RegionHandle=block['RegionHandle'], InternalRegionIP=block['InternalRegionIP'], ExternalRegionIP=block['ExternalRegionIP'], RegionPort=block['RegionPort'], ValidUntil=block['ValidUntil'], Message=block['Message']))

        return Message('RegionPresenceResponse', args)

class OpenCircuitPacket(object):
    ''' a template for a OpenCircuit packet '''

    def __init__(self, CircuitInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'OpenCircuit'

        if CircuitInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.CircuitInfo = {}    # New CircuitInfo block
            self.CircuitInfo['IP'] = None    # MVT_IP_ADDR
            self.CircuitInfo['Port'] = None    # MVT_IP_PORT
        else:
            self.CircuitInfo = CircuitInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('CircuitInfo', IP=self.CircuitInfo['IP'], Port=self.CircuitInfo['Port']))

        return Message('OpenCircuit', args)

class GroupRoleDataRequestPacket(object):
    ''' a template for a GroupRoleDataRequest packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupRoleDataRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
            self.GroupData['RequestID'] = None    # MVT_LLUUID
        else:
            self.GroupData = GroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID'], RequestID=self.GroupData['RequestID']))

        return Message('GroupRoleDataRequest', args)

class AgentMovementCompletePacket(object):
    ''' a template for a AgentMovementComplete packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}, SimDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentMovementComplete'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['Position'] = None    # MVT_LLVector3
            self.Data['LookAt'] = None    # MVT_LLVector3
            self.Data['RegionHandle'] = None    # MVT_U64
            self.Data['Timestamp'] = None    # MVT_U32
        else:
            self.Data = DataBlock

        if SimDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SimData = {}    # New SimData block
            self.SimData['ChannelVersion'] = None    # MVT_VARIABLE
        else:
            self.SimData = SimDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', Position=self.Data['Position'], LookAt=self.Data['LookAt'], RegionHandle=self.Data['RegionHandle'], Timestamp=self.Data['Timestamp']))
        args.append(Block('SimData', ChannelVersion=self.SimData['ChannelVersion']))

        return Message('AgentMovementComplete', args)

class InviteGroupRequestPacket(object):
    ''' a template for a InviteGroupRequest packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}, InviteDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'InviteGroupRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
        else:
            self.GroupData = GroupDataBlock

        if InviteDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InviteDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InviteData = {}
            self.InviteData['InviteeID'] = None    # MVT_LLUUID
            self.InviteData['RoleID'] = None    # MVT_LLUUID
        else:
            self.InviteDataBlocks = InviteDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID']))
        for block in self.InviteDataBlocks:
            args.append(Block('InviteData', InviteeID=block['InviteeID'], RoleID=block['RoleID']))

        return Message('InviteGroupRequest', args)

class ViewerStartAuctionPacket(object):
    ''' a template for a ViewerStartAuction packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ViewerStartAuction'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['LocalID'] = None    # MVT_S32
            self.ParcelData['SnapshotID'] = None    # MVT_LLUUID
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', LocalID=self.ParcelData['LocalID'], SnapshotID=self.ParcelData['SnapshotID']))

        return Message('ViewerStartAuction', args)

class ObjectNamePacket(object):
    ''' a template for a ObjectName packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectName'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['LocalID'] = None    # MVT_U32
            self.ObjectData['Name'] = None    # MVT_VARIABLE
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', LocalID=block['LocalID'], Name=block['Name']))

        return Message('ObjectName', args)

class CrossedRegionPacket(object):
    ''' a template for a CrossedRegion packet '''

    def __init__(self, AgentDataBlock = {}, RegionDataBlock = {}, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CrossedRegion'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RegionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionData = {}    # New RegionData block
            self.RegionData['SimIP'] = None    # MVT_IP_ADDR
            self.RegionData['SimPort'] = None    # MVT_IP_PORT
            self.RegionData['RegionHandle'] = None    # MVT_U64
            self.RegionData['SeedCapability'] = None    # MVT_VARIABLE
        else:
            self.RegionData = RegionDataBlock

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['Position'] = None    # MVT_LLVector3
            self.Info['LookAt'] = None    # MVT_LLVector3
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('RegionData', SimIP=self.RegionData['SimIP'], SimPort=self.RegionData['SimPort'], RegionHandle=self.RegionData['RegionHandle'], SeedCapability=self.RegionData['SeedCapability']))
        args.append(Block('Info', Position=self.Info['Position'], LookAt=self.Info['LookAt']))

        return Message('CrossedRegion', args)

class SetCPURatioPacket(object):
    ''' a template for a SetCPURatio packet '''

    def __init__(self, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SetCPURatio'

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['Ratio'] = None    # MVT_U8
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Data', Ratio=self.Data['Ratio']))

        return Message('SetCPURatio', args)

class ParcelBuyPassPacket(object):
    ''' a template for a ParcelBuyPass packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelBuyPass'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['LocalID'] = None    # MVT_S32
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', LocalID=self.ParcelData['LocalID']))

        return Message('ParcelBuyPass', args)

class MapItemRequestPacket(object):
    ''' a template for a MapItemRequest packet '''

    def __init__(self, AgentDataBlock = {}, RequestDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MapItemRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['Flags'] = None    # MVT_U32
            self.AgentData['EstateID'] = None    # MVT_U32
            self.AgentData['Godlike'] = None    # MVT_BOOL
        else:
            self.AgentData = AgentDataBlock

        if RequestDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RequestData = {}    # New RequestData block
            self.RequestData['ItemType'] = None    # MVT_U32
            self.RequestData['RegionHandle'] = None    # MVT_U64
        else:
            self.RequestData = RequestDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], Flags=self.AgentData['Flags'], EstateID=self.AgentData['EstateID'], Godlike=self.AgentData['Godlike']))
        args.append(Block('RequestData', ItemType=self.RequestData['ItemType'], RegionHandle=self.RequestData['RegionHandle']))

        return Message('MapItemRequest', args)

class AgentQuitCopyPacket(object):
    ''' a template for a AgentQuitCopy packet '''

    def __init__(self, AgentDataBlock = {}, FuseBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentQuitCopy'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if FuseBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.FuseBlock = {}    # New FuseBlock block
            self.FuseBlock['ViewerCircuitCode'] = None    # MVT_U32
        else:
            self.FuseBlock = FuseBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('FuseBlock', ViewerCircuitCode=self.FuseBlock['ViewerCircuitCode']))

        return Message('AgentQuitCopy', args)

class RequestTaskInventoryPacket(object):
    ''' a template for a RequestTaskInventory packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RequestTaskInventory'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.InventoryData = {}    # New InventoryData block
            self.InventoryData['LocalID'] = None    # MVT_U32
        else:
            self.InventoryData = InventoryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('InventoryData', LocalID=self.InventoryData['LocalID']))

        return Message('RequestTaskInventory', args)

class FreezeUserPacket(object):
    ''' a template for a FreezeUser packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'FreezeUser'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['TargetID'] = None    # MVT_LLUUID
            self.Data['Flags'] = None    # MVT_U32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', TargetID=self.Data['TargetID'], Flags=self.Data['Flags']))

        return Message('FreezeUser', args)

class StartPingCheckPacket(object):
    ''' a template for a StartPingCheck packet '''

    def __init__(self, PingIDBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'StartPingCheck'

        if PingIDBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.PingID = {}    # New PingID block
            self.PingID['PingID'] = None    # MVT_U8
            self.PingID['OldestUnacked'] = None    # MVT_U32
        else:
            self.PingID = PingIDBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('PingID', PingID=self.PingID['PingID'], OldestUnacked=self.PingID['OldestUnacked']))

        return Message('StartPingCheck', args)

class GroupDataUpdatePacket(object):
    ''' a template for a GroupDataUpdate packet '''

    def __init__(self, AgentGroupDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupDataUpdate'

        if AgentGroupDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.AgentGroupDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.AgentGroupData = {}
            self.AgentGroupData['AgentID'] = None    # MVT_LLUUID
            self.AgentGroupData['GroupID'] = None    # MVT_LLUUID
            self.AgentGroupData['AgentPowers'] = None    # MVT_U64
            self.AgentGroupData['GroupTitle'] = None    # MVT_VARIABLE
        else:
            self.AgentGroupDataBlocks = AgentGroupDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.AgentGroupDataBlocks:
            args.append(Block('AgentGroupData', AgentID=block['AgentID'], GroupID=block['GroupID'], AgentPowers=block['AgentPowers'], GroupTitle=block['GroupTitle']))

        return Message('GroupDataUpdate', args)

class TeleportLocationRequestPacket(object):
    ''' a template for a TeleportLocationRequest packet '''

    def __init__(self, AgentDataBlock = {}, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TeleportLocationRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['RegionHandle'] = None    # MVT_U64
            self.Info['Position'] = None    # MVT_LLVector3
            self.Info['LookAt'] = None    # MVT_LLVector3
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Info', RegionHandle=self.Info['RegionHandle'], Position=self.Info['Position'], LookAt=self.Info['LookAt']))

        return Message('TeleportLocationRequest', args)

class UpdateCreateInventoryItemPacket(object):
    ''' a template for a UpdateCreateInventoryItem packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UpdateCreateInventoryItem'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SimApproved'] = None    # MVT_BOOL
            self.AgentData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
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
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SimApproved=self.AgentData['SimApproved'], TransactionID=self.AgentData['TransactionID']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', ItemID=block['ItemID'], FolderID=block['FolderID'], CallbackID=block['CallbackID'], CreatorID=block['CreatorID'], OwnerID=block['OwnerID'], GroupID=block['GroupID'], BaseMask=block['BaseMask'], OwnerMask=block['OwnerMask'], GroupMask=block['GroupMask'], EveryoneMask=block['EveryoneMask'], NextOwnerMask=block['NextOwnerMask'], GroupOwned=block['GroupOwned'], AssetID=block['AssetID'], Type=block['Type'], InvType=block['InvType'], Flags=block['Flags'], SaleType=block['SaleType'], SalePrice=block['SalePrice'], Name=block['Name'], Description=block['Description'], CreationDate=block['CreationDate'], CRC=block['CRC']))

        return Message('UpdateCreateInventoryItem', args)

class NearestLandingRegionUpdatedPacket(object):
    ''' a template for a NearestLandingRegionUpdated packet '''

    def __init__(self, RegionDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'NearestLandingRegionUpdated'

        if RegionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionData = {}    # New RegionData block
            self.RegionData['RegionHandle'] = None    # MVT_U64
        else:
            self.RegionData = RegionDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('RegionData', RegionHandle=self.RegionData['RegionHandle']))

        return Message('NearestLandingRegionUpdated', args)

class EconomyDataPacket(object):
    ''' a template for a EconomyData packet '''

    def __init__(self, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EconomyData'

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Info', ObjectCapacity=self.Info['ObjectCapacity'], ObjectCount=self.Info['ObjectCount'], PriceEnergyUnit=self.Info['PriceEnergyUnit'], PriceObjectClaim=self.Info['PriceObjectClaim'], PricePublicObjectDecay=self.Info['PricePublicObjectDecay'], PricePublicObjectDelete=self.Info['PricePublicObjectDelete'], PriceParcelClaim=self.Info['PriceParcelClaim'], PriceParcelClaimFactor=self.Info['PriceParcelClaimFactor'], PriceUpload=self.Info['PriceUpload'], PriceRentLight=self.Info['PriceRentLight'], TeleportMinPrice=self.Info['TeleportMinPrice'], TeleportPriceExponent=self.Info['TeleportPriceExponent'], EnergyEfficiency=self.Info['EnergyEfficiency'], PriceObjectRent=self.Info['PriceObjectRent'], PriceObjectScaleFactor=self.Info['PriceObjectScaleFactor'], PriceParcelRent=self.Info['PriceParcelRent'], PriceGroupCreate=self.Info['PriceGroupCreate']))

        return Message('EconomyData', args)

class LiveHelpGroupReplyPacket(object):
    ''' a template for a LiveHelpGroupReply packet '''

    def __init__(self, ReplyDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LiveHelpGroupReply'

        if ReplyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ReplyData = {}    # New ReplyData block
            self.ReplyData['RequestID'] = None    # MVT_LLUUID
            self.ReplyData['GroupID'] = None    # MVT_LLUUID
            self.ReplyData['Selection'] = None    # MVT_VARIABLE
        else:
            self.ReplyData = ReplyDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ReplyData', RequestID=self.ReplyData['RequestID'], GroupID=self.ReplyData['GroupID'], Selection=self.ReplyData['Selection']))

        return Message('LiveHelpGroupReply', args)

class UseCircuitCodePacket(object):
    ''' a template for a UseCircuitCode packet '''

    def __init__(self, CircuitCodeBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UseCircuitCode'

        if CircuitCodeBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.CircuitCode = {}    # New CircuitCode block
            self.CircuitCode['Code'] = None    # MVT_U32
            self.CircuitCode['SessionID'] = None    # MVT_LLUUID
            self.CircuitCode['ID'] = None    # MVT_LLUUID
        else:
            self.CircuitCode = CircuitCodeBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('CircuitCode', Code=self.CircuitCode['Code'], SessionID=self.CircuitCode['SessionID'], ID=self.CircuitCode['ID']))

        return Message('UseCircuitCode', args)

class GroupAccountTransactionsReplyPacket(object):
    ''' a template for a GroupAccountTransactionsReply packet '''

    def __init__(self, AgentDataBlock = {}, MoneyDataBlock = {}, HistoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupAccountTransactionsReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MoneyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MoneyData = {}    # New MoneyData block
            self.MoneyData['RequestID'] = None    # MVT_LLUUID
            self.MoneyData['IntervalDays'] = None    # MVT_S32
            self.MoneyData['CurrentInterval'] = None    # MVT_S32
            self.MoneyData['StartDate'] = None    # MVT_VARIABLE
        else:
            self.MoneyData = MoneyDataBlock

        if HistoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.HistoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.HistoryData = {}
            self.HistoryData['Time'] = None    # MVT_VARIABLE
            self.HistoryData['User'] = None    # MVT_VARIABLE
            self.HistoryData['Type'] = None    # MVT_S32
            self.HistoryData['Item'] = None    # MVT_VARIABLE
            self.HistoryData['Amount'] = None    # MVT_S32
        else:
            self.HistoryDataBlocks = HistoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('MoneyData', RequestID=self.MoneyData['RequestID'], IntervalDays=self.MoneyData['IntervalDays'], CurrentInterval=self.MoneyData['CurrentInterval'], StartDate=self.MoneyData['StartDate']))
        for block in self.HistoryDataBlocks:
            args.append(Block('HistoryData', Time=block['Time'], User=block['User'], Type=block['Type'], Item=block['Item'], Amount=block['Amount']))

        return Message('GroupAccountTransactionsReply', args)

class UUIDGroupNameRequestPacket(object):
    ''' a template for a UUIDGroupNameRequest packet '''

    def __init__(self, UUIDNameBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UUIDGroupNameRequest'

        if UUIDNameBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.UUIDNameBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.UUIDNameBlock = {}
            self.UUIDNameBlock['ID'] = None    # MVT_LLUUID
        else:
            self.UUIDNameBlockBlocks = UUIDNameBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.UUIDNameBlockBlocks:
            args.append(Block('UUIDNameBlock', ID=block['ID']))

        return Message('UUIDGroupNameRequest', args)

class ObjectDelinkPacket(object):
    ''' a template for a ObjectDelink packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectDelink'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('ObjectDelink', args)

class SimStatusPacket(object):
    ''' a template for a SimStatus packet '''

    def __init__(self, SimStatusBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SimStatus'

        if SimStatusBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SimStatus = {}    # New SimStatus block
            self.SimStatus['CanAcceptAgents'] = None    # MVT_BOOL
            self.SimStatus['CanAcceptTasks'] = None    # MVT_BOOL
        else:
            self.SimStatus = SimStatusBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('SimStatus', CanAcceptAgents=self.SimStatus['CanAcceptAgents'], CanAcceptTasks=self.SimStatus['CanAcceptTasks']))

        return Message('SimStatus', args)

class GrantUserRightsPacket(object):
    ''' a template for a GrantUserRights packet '''

    def __init__(self, AgentDataBlock = {}, RightsBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GrantUserRights'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RightsBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.RightsBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Rights = {}
            self.Rights['AgentRelated'] = None    # MVT_LLUUID
            self.Rights['RelatedRights'] = None    # MVT_S32
        else:
            self.RightsBlocks = RightsBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.RightsBlocks:
            args.append(Block('Rights', AgentRelated=block['AgentRelated'], RelatedRights=block['RelatedRights']))

        return Message('GrantUserRights', args)

class ParcelAccessListRequestPacket(object):
    ''' a template for a ParcelAccessListRequest packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelAccessListRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['SequenceID'] = None    # MVT_S32
            self.Data['Flags'] = None    # MVT_U32
            self.Data['LocalID'] = None    # MVT_S32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', SequenceID=self.Data['SequenceID'], Flags=self.Data['Flags'], LocalID=self.Data['LocalID']))

        return Message('ParcelAccessListRequest', args)

class ParcelMediaCommandMessagePacket(object):
    ''' a template for a ParcelMediaCommandMessage packet '''

    def __init__(self, CommandBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelMediaCommandMessage'

        if CommandBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.CommandBlock = {}    # New CommandBlock block
            self.CommandBlock['Flags'] = None    # MVT_U32
            self.CommandBlock['Command'] = None    # MVT_U32
            self.CommandBlock['Time'] = None    # MVT_F32
        else:
            self.CommandBlock = CommandBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('CommandBlock', Flags=self.CommandBlock['Flags'], Command=self.CommandBlock['Command'], Time=self.CommandBlock['Time']))

        return Message('ParcelMediaCommandMessage', args)

class ObjectFlagUpdatePacket(object):
    ''' a template for a ObjectFlagUpdate packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectFlagUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['ObjectLocalID'] = None    # MVT_U32
            self.AgentData['UsePhysics'] = None    # MVT_BOOL
            self.AgentData['IsTemporary'] = None    # MVT_BOOL
            self.AgentData['IsPhantom'] = None    # MVT_BOOL
            self.AgentData['CastsShadows'] = None    # MVT_BOOL
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], ObjectLocalID=self.AgentData['ObjectLocalID'], UsePhysics=self.AgentData['UsePhysics'], IsTemporary=self.AgentData['IsTemporary'], IsPhantom=self.AgentData['IsPhantom'], CastsShadows=self.AgentData['CastsShadows']))

        return Message('ObjectFlagUpdate', args)

class DeclineFriendshipPacket(object):
    ''' a template for a DeclineFriendship packet '''

    def __init__(self, AgentDataBlock = {}, TransactionBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DeclineFriendship'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if TransactionBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransactionBlock = {}    # New TransactionBlock block
            self.TransactionBlock['TransactionID'] = None    # MVT_LLUUID
        else:
            self.TransactionBlock = TransactionBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('TransactionBlock', TransactionID=self.TransactionBlock['TransactionID']))

        return Message('DeclineFriendship', args)

class AvatarNotesUpdatePacket(object):
    ''' a template for a AvatarNotesUpdate packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarNotesUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['TargetID'] = None    # MVT_LLUUID
            self.Data['Notes'] = None    # MVT_VARIABLE
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', TargetID=self.Data['TargetID'], Notes=self.Data['Notes']))

        return Message('AvatarNotesUpdate', args)

class DetachAttachmentIntoInvPacket(object):
    ''' a template for a DetachAttachmentIntoInv packet '''

    def __init__(self, ObjectDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DetachAttachmentIntoInv'

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['AgentID'] = None    # MVT_LLUUID
            self.ObjectData['ItemID'] = None    # MVT_LLUUID
        else:
            self.ObjectData = ObjectDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ObjectData', AgentID=self.ObjectData['AgentID'], ItemID=self.ObjectData['ItemID']))

        return Message('DetachAttachmentIntoInv', args)

class ParcelObjectOwnersRequestPacket(object):
    ''' a template for a ParcelObjectOwnersRequest packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelObjectOwnersRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['LocalID'] = None    # MVT_S32
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', LocalID=self.ParcelData['LocalID']))

        return Message('ParcelObjectOwnersRequest', args)

class RemoveInventoryFolderPacket(object):
    ''' a template for a RemoveInventoryFolder packet '''

    def __init__(self, AgentDataBlock = {}, FolderDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RemoveInventoryFolder'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if FolderDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.FolderDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.FolderData = {}
            self.FolderData['FolderID'] = None    # MVT_LLUUID
        else:
            self.FolderDataBlocks = FolderDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.FolderDataBlocks:
            args.append(Block('FolderData', FolderID=block['FolderID']))

        return Message('RemoveInventoryFolder', args)

class TransferAbortPacket(object):
    ''' a template for a TransferAbort packet '''

    def __init__(self, TransferInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TransferAbort'

        if TransferInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransferInfo = {}    # New TransferInfo block
            self.TransferInfo['TransferID'] = None    # MVT_LLUUID
            self.TransferInfo['ChannelType'] = None    # MVT_S32
        else:
            self.TransferInfo = TransferInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TransferInfo', TransferID=self.TransferInfo['TransferID'], ChannelType=self.TransferInfo['ChannelType']))

        return Message('TransferAbort', args)

class DirPlacesQueryBackendPacket(object):
    ''' a template for a DirPlacesQueryBackend packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirPlacesQueryBackend'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['QueryText'] = None    # MVT_VARIABLE
            self.QueryData['QueryFlags'] = None    # MVT_U32
            self.QueryData['Category'] = None    # MVT_S8
            self.QueryData['SimName'] = None    # MVT_VARIABLE
            self.QueryData['EstateID'] = None    # MVT_U32
            self.QueryData['Godlike'] = None    # MVT_BOOL
            self.QueryData['QueryStart'] = None    # MVT_S32
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], QueryText=self.QueryData['QueryText'], QueryFlags=self.QueryData['QueryFlags'], Category=self.QueryData['Category'], SimName=self.QueryData['SimName'], EstateID=self.QueryData['EstateID'], Godlike=self.QueryData['Godlike'], QueryStart=self.QueryData['QueryStart']))

        return Message('DirPlacesQueryBackend', args)

class UserReportPacket(object):
    ''' a template for a UserReport packet '''

    def __init__(self, AgentDataBlock = {}, ReportDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UserReport'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ReportDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.ReportData = ReportDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ReportData', ReportType=self.ReportData['ReportType'], Category=self.ReportData['Category'], Position=self.ReportData['Position'], CheckFlags=self.ReportData['CheckFlags'], ScreenshotID=self.ReportData['ScreenshotID'], ObjectID=self.ReportData['ObjectID'], AbuserID=self.ReportData['AbuserID'], AbuseRegionName=self.ReportData['AbuseRegionName'], AbuseRegionID=self.ReportData['AbuseRegionID'], Summary=self.ReportData['Summary'], Details=self.ReportData['Details'], VersionString=self.ReportData['VersionString']))

        return Message('UserReport', args)

class SimulatorLoadPacket(object):
    ''' a template for a SimulatorLoad packet '''

    def __init__(self, SimulatorLoadBlock = {}, AgentListBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SimulatorLoad'

        if SimulatorLoadBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SimulatorLoad = {}    # New SimulatorLoad block
            self.SimulatorLoad['TimeDilation'] = None    # MVT_F32
            self.SimulatorLoad['AgentCount'] = None    # MVT_S32
            self.SimulatorLoad['CanAcceptAgents'] = None    # MVT_BOOL
        else:
            self.SimulatorLoad = SimulatorLoadBlock

        if AgentListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.AgentListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.AgentList = {}
            self.AgentList['CircuitCode'] = None    # MVT_U32
            self.AgentList['X'] = None    # MVT_U8
            self.AgentList['Y'] = None    # MVT_U8
        else:
            self.AgentListBlocks = AgentListBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('SimulatorLoad', TimeDilation=self.SimulatorLoad['TimeDilation'], AgentCount=self.SimulatorLoad['AgentCount'], CanAcceptAgents=self.SimulatorLoad['CanAcceptAgents']))
        for block in self.AgentListBlocks:
            args.append(Block('AgentList', CircuitCode=block['CircuitCode'], X=block['X'], Y=block['Y']))

        return Message('SimulatorLoad', args)

class GroupMembersReplyPacket(object):
    ''' a template for a GroupMembersReply packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}, MemberDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupMembersReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
            self.GroupData['RequestID'] = None    # MVT_LLUUID
            self.GroupData['MemberCount'] = None    # MVT_S32
        else:
            self.GroupData = GroupDataBlock

        if MemberDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.MemberDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.MemberData = {}
            self.MemberData['AgentID'] = None    # MVT_LLUUID
            self.MemberData['Contribution'] = None    # MVT_S32
            self.MemberData['OnlineStatus'] = None    # MVT_VARIABLE
            self.MemberData['AgentPowers'] = None    # MVT_U64
            self.MemberData['Title'] = None    # MVT_VARIABLE
            self.MemberData['IsOwner'] = None    # MVT_BOOL
        else:
            self.MemberDataBlocks = MemberDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID'], RequestID=self.GroupData['RequestID'], MemberCount=self.GroupData['MemberCount']))
        for block in self.MemberDataBlocks:
            args.append(Block('MemberData', AgentID=block['AgentID'], Contribution=block['Contribution'], OnlineStatus=block['OnlineStatus'], AgentPowers=block['AgentPowers'], Title=block['Title'], IsOwner=block['IsOwner']))

        return Message('GroupMembersReply', args)

class ScriptResetPacket(object):
    ''' a template for a ScriptReset packet '''

    def __init__(self, AgentDataBlock = {}, ScriptBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptReset'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ScriptBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Script = {}    # New Script block
            self.Script['ObjectID'] = None    # MVT_LLUUID
            self.Script['ItemID'] = None    # MVT_LLUUID
        else:
            self.Script = ScriptBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Script', ObjectID=self.Script['ObjectID'], ItemID=self.Script['ItemID']))

        return Message('ScriptReset', args)

class VelocityInterpolateOnPacket(object):
    ''' a template for a VelocityInterpolateOn packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'VelocityInterpolateOn'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('VelocityInterpolateOn', args)

class NameValuePairPacket(object):
    ''' a template for a NameValuePair packet '''

    def __init__(self, TaskDataBlock = {}, NameValueDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'NameValuePair'

        if TaskDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TaskData = {}    # New TaskData block
            self.TaskData['ID'] = None    # MVT_LLUUID
        else:
            self.TaskData = TaskDataBlock

        if NameValueDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.NameValueDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.NameValueData = {}
            self.NameValueData['NVPair'] = None    # MVT_VARIABLE
        else:
            self.NameValueDataBlocks = NameValueDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TaskData', ID=self.TaskData['ID']))
        for block in self.NameValueDataBlocks:
            args.append(Block('NameValueData', NVPair=block['NVPair']))

        return Message('NameValuePair', args)

class ParcelReclaimPacket(object):
    ''' a template for a ParcelReclaim packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelReclaim'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['LocalID'] = None    # MVT_S32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', LocalID=self.Data['LocalID']))

        return Message('ParcelReclaim', args)

class BuyObjectInventoryPacket(object):
    ''' a template for a BuyObjectInventory packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'BuyObjectInventory'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['ObjectID'] = None    # MVT_LLUUID
            self.Data['ItemID'] = None    # MVT_LLUUID
            self.Data['FolderID'] = None    # MVT_LLUUID
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', ObjectID=self.Data['ObjectID'], ItemID=self.Data['ItemID'], FolderID=self.Data['FolderID']))

        return Message('BuyObjectInventory', args)

class EventLocationRequestPacket(object):
    ''' a template for a EventLocationRequest packet '''

    def __init__(self, QueryDataBlock = {}, EventDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EventLocationRequest'

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
        else:
            self.QueryData = QueryDataBlock

        if EventDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.EventData = {}    # New EventData block
            self.EventData['EventID'] = None    # MVT_U32
        else:
            self.EventData = EventDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID']))
        args.append(Block('EventData', EventID=self.EventData['EventID']))

        return Message('EventLocationRequest', args)

class PickDeletePacket(object):
    ''' a template for a PickDelete packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'PickDelete'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['PickID'] = None    # MVT_LLUUID
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', PickID=self.Data['PickID']))

        return Message('PickDelete', args)

class MapLayerReplyPacket(object):
    ''' a template for a MapLayerReply packet '''

    def __init__(self, AgentDataBlock = {}, LayerDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MapLayerReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['Flags'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

        if LayerDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.LayerDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.LayerData = {}
            self.LayerData['Left'] = None    # MVT_U32
            self.LayerData['Right'] = None    # MVT_U32
            self.LayerData['Top'] = None    # MVT_U32
            self.LayerData['Bottom'] = None    # MVT_U32
            self.LayerData['ImageID'] = None    # MVT_LLUUID
        else:
            self.LayerDataBlocks = LayerDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], Flags=self.AgentData['Flags']))
        for block in self.LayerDataBlocks:
            args.append(Block('LayerData', Left=block['Left'], Right=block['Right'], Top=block['Top'], Bottom=block['Bottom'], ImageID=block['ImageID']))

        return Message('MapLayerReply', args)

class TeleportLandmarkRequestPacket(object):
    ''' a template for a TeleportLandmarkRequest packet '''

    def __init__(self, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TeleportLandmarkRequest'

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['AgentID'] = None    # MVT_LLUUID
            self.Info['SessionID'] = None    # MVT_LLUUID
            self.Info['LandmarkID'] = None    # MVT_LLUUID
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Info', AgentID=self.Info['AgentID'], SessionID=self.Info['SessionID'], LandmarkID=self.Info['LandmarkID']))

        return Message('TeleportLandmarkRequest', args)

class PurgeInventoryDescendentsPacket(object):
    ''' a template for a PurgeInventoryDescendents packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'PurgeInventoryDescendents'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.InventoryData = {}    # New InventoryData block
            self.InventoryData['FolderID'] = None    # MVT_LLUUID
        else:
            self.InventoryData = InventoryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('InventoryData', FolderID=self.InventoryData['FolderID']))

        return Message('PurgeInventoryDescendents', args)

class KickUserAckPacket(object):
    ''' a template for a KickUserAck packet '''

    def __init__(self, UserInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'KickUserAck'

        if UserInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.UserInfo = {}    # New UserInfo block
            self.UserInfo['SessionID'] = None    # MVT_LLUUID
            self.UserInfo['Flags'] = None    # MVT_U32
        else:
            self.UserInfo = UserInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('UserInfo', SessionID=self.UserInfo['SessionID'], Flags=self.UserInfo['Flags']))

        return Message('KickUserAck', args)

class AvatarSitResponsePacket(object):
    ''' a template for a AvatarSitResponse packet '''

    def __init__(self, SitObjectBlock = {}, SitTransformBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarSitResponse'

        if SitObjectBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SitObject = {}    # New SitObject block
            self.SitObject['ID'] = None    # MVT_LLUUID
        else:
            self.SitObject = SitObjectBlock

        if SitTransformBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SitTransform = {}    # New SitTransform block
            self.SitTransform['AutoPilot'] = None    # MVT_BOOL
            self.SitTransform['SitPosition'] = None    # MVT_LLVector3
            self.SitTransform['SitRotation'] = None    # MVT_LLQuaternion
            self.SitTransform['CameraEyeOffset'] = None    # MVT_LLVector3
            self.SitTransform['CameraAtOffset'] = None    # MVT_LLVector3
            self.SitTransform['ForceMouselook'] = None    # MVT_BOOL
        else:
            self.SitTransform = SitTransformBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('SitObject', ID=self.SitObject['ID']))
        args.append(Block('SitTransform', AutoPilot=self.SitTransform['AutoPilot'], SitPosition=self.SitTransform['SitPosition'], SitRotation=self.SitTransform['SitRotation'], CameraEyeOffset=self.SitTransform['CameraEyeOffset'], CameraAtOffset=self.SitTransform['CameraAtOffset'], ForceMouselook=self.SitTransform['ForceMouselook']))

        return Message('AvatarSitResponse', args)

class ClassifiedInfoRequestPacket(object):
    ''' a template for a ClassifiedInfoRequest packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ClassifiedInfoRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['ClassifiedID'] = None    # MVT_LLUUID
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', ClassifiedID=self.Data['ClassifiedID']))

        return Message('ClassifiedInfoRequest', args)

class UpdateMuteListEntryPacket(object):
    ''' a template for a UpdateMuteListEntry packet '''

    def __init__(self, AgentDataBlock = {}, MuteDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UpdateMuteListEntry'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MuteDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MuteData = {}    # New MuteData block
            self.MuteData['MuteID'] = None    # MVT_LLUUID
            self.MuteData['MuteName'] = None    # MVT_VARIABLE
            self.MuteData['MuteType'] = None    # MVT_S32
            self.MuteData['MuteFlags'] = None    # MVT_U32
        else:
            self.MuteData = MuteDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('MuteData', MuteID=self.MuteData['MuteID'], MuteName=self.MuteData['MuteName'], MuteType=self.MuteData['MuteType'], MuteFlags=self.MuteData['MuteFlags']))

        return Message('UpdateMuteListEntry', args)

class RegionInfoPacket(object):
    ''' a template for a RegionInfo packet '''

    def __init__(self, AgentDataBlock = {}, RegionInfoBlock = {}, RegionInfo2Block = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RegionInfo'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RegionInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.RegionInfo = RegionInfoBlock

        if RegionInfo2Block == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionInfo2 = {}    # New RegionInfo2 block
            self.RegionInfo2['ProductSKU'] = None    # MVT_VARIABLE
            self.RegionInfo2['ProductName'] = None    # MVT_VARIABLE
            self.RegionInfo2['MaxAgents32'] = None    # MVT_U32
            self.RegionInfo2['HardMaxAgents'] = None    # MVT_U32
            self.RegionInfo2['HardMaxObjects'] = None    # MVT_U32
        else:
            self.RegionInfo2 = RegionInfo2Block

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('RegionInfo', SimName=self.RegionInfo['SimName'], EstateID=self.RegionInfo['EstateID'], ParentEstateID=self.RegionInfo['ParentEstateID'], RegionFlags=self.RegionInfo['RegionFlags'], SimAccess=self.RegionInfo['SimAccess'], MaxAgents=self.RegionInfo['MaxAgents'], BillableFactor=self.RegionInfo['BillableFactor'], ObjectBonusFactor=self.RegionInfo['ObjectBonusFactor'], WaterHeight=self.RegionInfo['WaterHeight'], TerrainRaiseLimit=self.RegionInfo['TerrainRaiseLimit'], TerrainLowerLimit=self.RegionInfo['TerrainLowerLimit'], PricePerMeter=self.RegionInfo['PricePerMeter'], RedirectGridX=self.RegionInfo['RedirectGridX'], RedirectGridY=self.RegionInfo['RedirectGridY'], UseEstateSun=self.RegionInfo['UseEstateSun'], SunHour=self.RegionInfo['SunHour']))
        args.append(Block('RegionInfo2', ProductSKU=self.RegionInfo2['ProductSKU'], ProductName=self.RegionInfo2['ProductName'], MaxAgents32=self.RegionInfo2['MaxAgents32'], HardMaxAgents=self.RegionInfo2['HardMaxAgents'], HardMaxObjects=self.RegionInfo2['HardMaxObjects']))

        return Message('RegionInfo', args)

class UserReportInternalPacket(object):
    ''' a template for a UserReportInternal packet '''

    def __init__(self, ReportDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UserReportInternal'

        if ReportDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.ReportData = ReportDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ReportData', ReportType=self.ReportData['ReportType'], Category=self.ReportData['Category'], ReporterID=self.ReportData['ReporterID'], ViewerPosition=self.ReportData['ViewerPosition'], AgentPosition=self.ReportData['AgentPosition'], ScreenshotID=self.ReportData['ScreenshotID'], ObjectID=self.ReportData['ObjectID'], OwnerID=self.ReportData['OwnerID'], LastOwnerID=self.ReportData['LastOwnerID'], CreatorID=self.ReportData['CreatorID'], RegionID=self.ReportData['RegionID'], AbuserID=self.ReportData['AbuserID'], AbuseRegionName=self.ReportData['AbuseRegionName'], AbuseRegionID=self.ReportData['AbuseRegionID'], Summary=self.ReportData['Summary'], Details=self.ReportData['Details'], VersionString=self.ReportData['VersionString']))

        return Message('UserReportInternal', args)

class GroupActiveProposalItemReplyPacket(object):
    ''' a template for a GroupActiveProposalItemReply packet '''

    def __init__(self, AgentDataBlock = {}, TransactionDataBlock = {}, ProposalDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupActiveProposalItemReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if TransactionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransactionData = {}    # New TransactionData block
            self.TransactionData['TransactionID'] = None    # MVT_LLUUID
            self.TransactionData['TotalNumItems'] = None    # MVT_U32
        else:
            self.TransactionData = TransactionDataBlock

        if ProposalDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ProposalDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ProposalData = {}
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
        else:
            self.ProposalDataBlocks = ProposalDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('TransactionData', TransactionID=self.TransactionData['TransactionID'], TotalNumItems=self.TransactionData['TotalNumItems']))
        for block in self.ProposalDataBlocks:
            args.append(Block('ProposalData', VoteID=block['VoteID'], VoteInitiator=block['VoteInitiator'], TerseDateID=block['TerseDateID'], StartDateTime=block['StartDateTime'], EndDateTime=block['EndDateTime'], AlreadyVoted=block['AlreadyVoted'], VoteCast=block['VoteCast'], Majority=block['Majority'], Quorum=block['Quorum'], ProposalText=block['ProposalText']))

        return Message('GroupActiveProposalItemReply', args)

class RetrieveInstantMessagesPacket(object):
    ''' a template for a RetrieveInstantMessages packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RetrieveInstantMessages'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('RetrieveInstantMessages', args)

class ScriptDataReplyPacket(object):
    ''' a template for a ScriptDataReply packet '''

    def __init__(self, DataBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptDataReply'

        if DataBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.DataBlock = {}
            self.DataBlock['Hash'] = None    # MVT_U64
            self.DataBlock['Reply'] = None    # MVT_VARIABLE
        else:
            self.DataBlockBlocks = DataBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.DataBlockBlocks:
            args.append(Block('DataBlock', Hash=block['Hash'], Reply=block['Reply']))

        return Message('ScriptDataReply', args)

class ParcelAccessListUpdatePacket(object):
    ''' a template for a ParcelAccessListUpdate packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}, ListBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelAccessListUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['Flags'] = None    # MVT_U32
            self.Data['LocalID'] = None    # MVT_S32
            self.Data['TransactionID'] = None    # MVT_LLUUID
            self.Data['SequenceID'] = None    # MVT_S32
            self.Data['Sections'] = None    # MVT_S32
        else:
            self.Data = DataBlock

        if ListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.List = {}
            self.List['ID'] = None    # MVT_LLUUID
            self.List['Time'] = None    # MVT_S32
            self.List['Flags'] = None    # MVT_U32
        else:
            self.ListBlocks = ListBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', Flags=self.Data['Flags'], LocalID=self.Data['LocalID'], TransactionID=self.Data['TransactionID'], SequenceID=self.Data['SequenceID'], Sections=self.Data['Sections']))
        for block in self.ListBlocks:
            args.append(Block('List', ID=block['ID'], Time=block['Time'], Flags=block['Flags']))

        return Message('ParcelAccessListUpdate', args)

class ObjectImagePacket(object):
    ''' a template for a ObjectImage packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectImage'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['MediaURL'] = None    # MVT_VARIABLE
            self.ObjectData['TextureEntry'] = None    # MVT_VARIABLE
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], MediaURL=block['MediaURL'], TextureEntry=block['TextureEntry']))

        return Message('ObjectImage', args)

class ActivateGesturesPacket(object):
    ''' a template for a ActivateGestures packet '''

    def __init__(self, AgentDataBlock = {}, DataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ActivateGestures'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['Flags'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

        if DataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Data = {}
            self.Data['ItemID'] = None    # MVT_LLUUID
            self.Data['AssetID'] = None    # MVT_LLUUID
            self.Data['GestureFlags'] = None    # MVT_U32
        else:
            self.DataBlocks = DataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], Flags=self.AgentData['Flags']))
        for block in self.DataBlocks:
            args.append(Block('Data', ItemID=block['ItemID'], AssetID=block['AssetID'], GestureFlags=block['GestureFlags']))

        return Message('ActivateGestures', args)

class ScriptTeleportRequestPacket(object):
    ''' a template for a ScriptTeleportRequest packet '''

    def __init__(self, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptTeleportRequest'

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['ObjectName'] = None    # MVT_VARIABLE
            self.Data['SimName'] = None    # MVT_VARIABLE
            self.Data['SimPosition'] = None    # MVT_LLVector3
            self.Data['LookAt'] = None    # MVT_LLVector3
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Data', ObjectName=self.Data['ObjectName'], SimName=self.Data['SimName'], SimPosition=self.Data['SimPosition'], LookAt=self.Data['LookAt']))

        return Message('ScriptTeleportRequest', args)

class RpcScriptRequestInboundPacket(object):
    ''' a template for a RpcScriptRequestInbound packet '''

    def __init__(self, TargetBlockBlock = {}, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RpcScriptRequestInbound'

        if TargetBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TargetBlock = {}    # New TargetBlock block
            self.TargetBlock['GridX'] = None    # MVT_U32
            self.TargetBlock['GridY'] = None    # MVT_U32
        else:
            self.TargetBlock = TargetBlockBlock

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['TaskID'] = None    # MVT_LLUUID
            self.DataBlock['ItemID'] = None    # MVT_LLUUID
            self.DataBlock['ChannelID'] = None    # MVT_LLUUID
            self.DataBlock['IntValue'] = None    # MVT_U32
            self.DataBlock['StringValue'] = None    # MVT_VARIABLE
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TargetBlock', GridX=self.TargetBlock['GridX'], GridY=self.TargetBlock['GridY']))
        args.append(Block('DataBlock', TaskID=self.DataBlock['TaskID'], ItemID=self.DataBlock['ItemID'], ChannelID=self.DataBlock['ChannelID'], IntValue=self.DataBlock['IntValue'], StringValue=self.DataBlock['StringValue']))

        return Message('RpcScriptRequestInbound', args)

class TeleportFailedPacket(object):
    ''' a template for a TeleportFailed packet '''

    def __init__(self, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TeleportFailed'

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['AgentID'] = None    # MVT_LLUUID
            self.Info['Reason'] = None    # MVT_VARIABLE
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Info', AgentID=self.Info['AgentID'], Reason=self.Info['Reason']))

        return Message('TeleportFailed', args)

class RezObjectFromNotecardPacket(object):
    ''' a template for a RezObjectFromNotecard packet '''

    def __init__(self, AgentDataBlock = {}, RezDataBlock = {}, NotecardDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RezObjectFromNotecard'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RezDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.RezData = RezDataBlock

        if NotecardDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.NotecardData = {}    # New NotecardData block
            self.NotecardData['NotecardItemID'] = None    # MVT_LLUUID
            self.NotecardData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.NotecardData = NotecardDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
            self.InventoryData['ItemID'] = None    # MVT_LLUUID
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('RezData', FromTaskID=self.RezData['FromTaskID'], BypassRaycast=self.RezData['BypassRaycast'], RayStart=self.RezData['RayStart'], RayEnd=self.RezData['RayEnd'], RayTargetID=self.RezData['RayTargetID'], RayEndIsIntersection=self.RezData['RayEndIsIntersection'], RezSelected=self.RezData['RezSelected'], RemoveItem=self.RezData['RemoveItem'], ItemFlags=self.RezData['ItemFlags'], GroupMask=self.RezData['GroupMask'], EveryoneMask=self.RezData['EveryoneMask'], NextOwnerMask=self.RezData['NextOwnerMask']))
        args.append(Block('NotecardData', NotecardItemID=self.NotecardData['NotecardItemID'], ObjectID=self.NotecardData['ObjectID']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', ItemID=block['ItemID']))

        return Message('RezObjectFromNotecard', args)

class AvatarGroupsReplyPacket(object):
    ''' a template for a AvatarGroupsReply packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlocks = [], NewGroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarGroupsReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['AvatarID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.GroupDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.GroupData = {}
            self.GroupData['GroupPowers'] = None    # MVT_U64
            self.GroupData['AcceptNotices'] = None    # MVT_BOOL
            self.GroupData['GroupTitle'] = None    # MVT_VARIABLE
            self.GroupData['GroupID'] = None    # MVT_LLUUID
            self.GroupData['GroupName'] = None    # MVT_VARIABLE
            self.GroupData['GroupInsigniaID'] = None    # MVT_LLUUID
        else:
            self.GroupDataBlocks = GroupDataBlocks

        if NewGroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.NewGroupData = {}    # New NewGroupData block
            self.NewGroupData['ListInProfile'] = None    # MVT_BOOL
        else:
            self.NewGroupData = NewGroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], AvatarID=self.AgentData['AvatarID']))
        for block in self.GroupDataBlocks:
            args.append(Block('GroupData', GroupPowers=block['GroupPowers'], AcceptNotices=block['AcceptNotices'], GroupTitle=block['GroupTitle'], GroupID=block['GroupID'], GroupName=block['GroupName'], GroupInsigniaID=block['GroupInsigniaID']))
        args.append(Block('NewGroupData', ListInProfile=self.NewGroupData['ListInProfile']))

        return Message('AvatarGroupsReply', args)

class ObjectUpdatePacket(object):
    ''' a template for a ObjectUpdate packet '''

    def __init__(self, RegionDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectUpdate'

        if RegionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionData = {}    # New RegionData block
            self.RegionData['RegionHandle'] = None    # MVT_U64
            self.RegionData['TimeDilation'] = None    # MVT_U16
        else:
            self.RegionData = RegionDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
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
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('RegionData', RegionHandle=self.RegionData['RegionHandle'], TimeDilation=self.RegionData['TimeDilation']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ID=block['ID'], State=block['State'], FullID=block['FullID'], CRC=block['CRC'], PCode=block['PCode'], Material=block['Material'], ClickAction=block['ClickAction'], Scale=block['Scale'], ObjectData=block['ObjectData'], ParentID=block['ParentID'], UpdateFlags=block['UpdateFlags'], PathCurve=block['PathCurve'], ProfileCurve=block['ProfileCurve'], PathBegin=block['PathBegin'], PathEnd=block['PathEnd'], PathScaleX=block['PathScaleX'], PathScaleY=block['PathScaleY'], PathShearX=block['PathShearX'], PathShearY=block['PathShearY'], PathTwist=block['PathTwist'], PathTwistBegin=block['PathTwistBegin'], PathRadiusOffset=block['PathRadiusOffset'], PathTaperX=block['PathTaperX'], PathTaperY=block['PathTaperY'], PathRevolutions=block['PathRevolutions'], PathSkew=block['PathSkew'], ProfileBegin=block['ProfileBegin'], ProfileEnd=block['ProfileEnd'], ProfileHollow=block['ProfileHollow'], TextureEntry=block['TextureEntry'], TextureAnim=block['TextureAnim'], NameValue=block['NameValue'], Data=block['Data'], Text=block['Text'], TextColor=block['TextColor'], MediaURL=block['MediaURL'], PSBlock=block['PSBlock'], ExtraParams=block['ExtraParams'], Sound=block['Sound'], OwnerID=block['OwnerID'], Gain=block['Gain'], Flags=block['Flags'], Radius=block['Radius'], JointType=block['JointType'], JointPivot=block['JointPivot'], JointAxisOrAnchor=block['JointAxisOrAnchor']))

        return Message('ObjectUpdate', args)

class DirPopularQueryBackendPacket(object):
    ''' a template for a DirPopularQueryBackend packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirPopularQueryBackend'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['QueryFlags'] = None    # MVT_U32
            self.QueryData['EstateID'] = None    # MVT_U32
            self.QueryData['Godlike'] = None    # MVT_BOOL
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], QueryFlags=self.QueryData['QueryFlags'], EstateID=self.QueryData['EstateID'], Godlike=self.QueryData['Godlike']))

        return Message('DirPopularQueryBackend', args)

class FindAgentPacket(object):
    ''' a template for a FindAgent packet '''

    def __init__(self, AgentBlockBlock = {}, LocationBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'FindAgent'

        if AgentBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentBlock = {}    # New AgentBlock block
            self.AgentBlock['Hunter'] = None    # MVT_LLUUID
            self.AgentBlock['Prey'] = None    # MVT_LLUUID
            self.AgentBlock['SpaceIP'] = None    # MVT_IP_ADDR
        else:
            self.AgentBlock = AgentBlockBlock

        if LocationBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.LocationBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.LocationBlock = {}
            self.LocationBlock['GlobalX'] = None    # MVT_F64
            self.LocationBlock['GlobalY'] = None    # MVT_F64
        else:
            self.LocationBlockBlocks = LocationBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentBlock', Hunter=self.AgentBlock['Hunter'], Prey=self.AgentBlock['Prey'], SpaceIP=self.AgentBlock['SpaceIP']))
        for block in self.LocationBlockBlocks:
            args.append(Block('LocationBlock', GlobalX=block['GlobalX'], GlobalY=block['GlobalY']))

        return Message('FindAgent', args)

class EnableSimulatorPacket(object):
    ''' a template for a EnableSimulator packet '''

    def __init__(self, SimulatorInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EnableSimulator'

        if SimulatorInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SimulatorInfo = {}    # New SimulatorInfo block
            self.SimulatorInfo['Handle'] = None    # MVT_U64
            self.SimulatorInfo['IP'] = None    # MVT_IP_ADDR
            self.SimulatorInfo['Port'] = None    # MVT_IP_PORT
        else:
            self.SimulatorInfo = SimulatorInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('SimulatorInfo', Handle=self.SimulatorInfo['Handle'], IP=self.SimulatorInfo['IP'], Port=self.SimulatorInfo['Port']))

        return Message('EnableSimulator', args)

class PlacesReplyPacket(object):
    ''' a template for a PlacesReply packet '''

    def __init__(self, AgentDataBlock = {}, TransactionDataBlock = {}, QueryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'PlacesReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['QueryID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if TransactionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransactionData = {}    # New TransactionData block
            self.TransactionData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.TransactionData = TransactionDataBlock

        if QueryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.QueryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.QueryData = {}
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
        else:
            self.QueryDataBlocks = QueryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], QueryID=self.AgentData['QueryID']))
        args.append(Block('TransactionData', TransactionID=self.TransactionData['TransactionID']))
        for block in self.QueryDataBlocks:
            args.append(Block('QueryData', OwnerID=block['OwnerID'], Name=block['Name'], Desc=block['Desc'], ActualArea=block['ActualArea'], BillableArea=block['BillableArea'], Flags=block['Flags'], GlobalX=block['GlobalX'], GlobalY=block['GlobalY'], GlobalZ=block['GlobalZ'], SimName=block['SimName'], SnapshotID=block['SnapshotID'], Dwell=block['Dwell'], Price=block['Price']))

        return Message('PlacesReply', args)

class SetGroupContributionPacket(object):
    ''' a template for a SetGroupContribution packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SetGroupContribution'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['GroupID'] = None    # MVT_LLUUID
            self.Data['Contribution'] = None    # MVT_S32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', GroupID=self.Data['GroupID'], Contribution=self.Data['Contribution']))

        return Message('SetGroupContribution', args)

class ScriptSensorReplyPacket(object):
    ''' a template for a ScriptSensorReply packet '''

    def __init__(self, RequesterBlock = {}, SensedDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptSensorReply'

        if RequesterBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Requester = {}    # New Requester block
            self.Requester['SourceID'] = None    # MVT_LLUUID
        else:
            self.Requester = RequesterBlock

        if SensedDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.SensedDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.SensedData = {}
            self.SensedData['ObjectID'] = None    # MVT_LLUUID
            self.SensedData['OwnerID'] = None    # MVT_LLUUID
            self.SensedData['GroupID'] = None    # MVT_LLUUID
            self.SensedData['Position'] = None    # MVT_LLVector3
            self.SensedData['Velocity'] = None    # MVT_LLVector3
            self.SensedData['Rotation'] = None    # MVT_LLQuaternion
            self.SensedData['Name'] = None    # MVT_VARIABLE
            self.SensedData['Type'] = None    # MVT_S32
            self.SensedData['Range'] = None    # MVT_F32
        else:
            self.SensedDataBlocks = SensedDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Requester', SourceID=self.Requester['SourceID']))
        for block in self.SensedDataBlocks:
            args.append(Block('SensedData', ObjectID=block['ObjectID'], OwnerID=block['OwnerID'], GroupID=block['GroupID'], Position=block['Position'], Velocity=block['Velocity'], Rotation=block['Rotation'], Name=block['Name'], Type=block['Type'], Range=block['Range']))

        return Message('ScriptSensorReply', args)

class LeaveGroupRequestPacket(object):
    ''' a template for a LeaveGroupRequest packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LeaveGroupRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
        else:
            self.GroupData = GroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID']))

        return Message('LeaveGroupRequest', args)

class ParcelSalesPacket(object):
    ''' a template for a ParcelSales packet '''

    def __init__(self, ParcelDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelSales'

        if ParcelDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParcelDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParcelData = {}
            self.ParcelData['ParcelID'] = None    # MVT_LLUUID
            self.ParcelData['BuyerID'] = None    # MVT_LLUUID
        else:
            self.ParcelDataBlocks = ParcelDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.ParcelDataBlocks:
            args.append(Block('ParcelData', ParcelID=block['ParcelID'], BuyerID=block['BuyerID']))

        return Message('ParcelSales', args)

class ObjectPermissionsPacket(object):
    ''' a template for a ObjectPermissions packet '''

    def __init__(self, AgentDataBlock = {}, HeaderDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectPermissions'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if HeaderDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.HeaderData = {}    # New HeaderData block
            self.HeaderData['Override'] = None    # MVT_BOOL
        else:
            self.HeaderData = HeaderDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['Field'] = None    # MVT_U8
            self.ObjectData['Set'] = None    # MVT_U8
            self.ObjectData['Mask'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('HeaderData', Override=self.HeaderData['Override']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], Field=block['Field'], Set=block['Set'], Mask=block['Mask']))

        return Message('ObjectPermissions', args)

class ObjectPropertiesPacket(object):
    ''' a template for a ObjectProperties packet '''

    def __init__(self, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectProperties'

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
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
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectID=block['ObjectID'], CreatorID=block['CreatorID'], OwnerID=block['OwnerID'], GroupID=block['GroupID'], CreationDate=block['CreationDate'], BaseMask=block['BaseMask'], OwnerMask=block['OwnerMask'], GroupMask=block['GroupMask'], EveryoneMask=block['EveryoneMask'], NextOwnerMask=block['NextOwnerMask'], OwnershipCost=block['OwnershipCost'], SaleType=block['SaleType'], SalePrice=block['SalePrice'], AggregatePerms=block['AggregatePerms'], AggregatePermTextures=block['AggregatePermTextures'], AggregatePermTexturesOwner=block['AggregatePermTexturesOwner'], Category=block['Category'], InventorySerial=block['InventorySerial'], ItemID=block['ItemID'], FolderID=block['FolderID'], FromTaskID=block['FromTaskID'], LastOwnerID=block['LastOwnerID'], Name=block['Name'], Description=block['Description'], TouchName=block['TouchName'], SitName=block['SitName'], TextureID=block['TextureID']))

        return Message('ObjectProperties', args)

class SetStartLocationPacket(object):
    ''' a template for a SetStartLocation packet '''

    def __init__(self, StartLocationDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SetStartLocation'

        if StartLocationDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.StartLocationData = {}    # New StartLocationData block
            self.StartLocationData['AgentID'] = None    # MVT_LLUUID
            self.StartLocationData['RegionID'] = None    # MVT_LLUUID
            self.StartLocationData['LocationID'] = None    # MVT_U32
            self.StartLocationData['RegionHandle'] = None    # MVT_U64
            self.StartLocationData['LocationPos'] = None    # MVT_LLVector3
            self.StartLocationData['LocationLookAt'] = None    # MVT_LLVector3
        else:
            self.StartLocationData = StartLocationDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('StartLocationData', AgentID=self.StartLocationData['AgentID'], RegionID=self.StartLocationData['RegionID'], LocationID=self.StartLocationData['LocationID'], RegionHandle=self.StartLocationData['RegionHandle'], LocationPos=self.StartLocationData['LocationPos'], LocationLookAt=self.StartLocationData['LocationLookAt']))

        return Message('SetStartLocation', args)

class EstateCovenantReplyPacket(object):
    ''' a template for a EstateCovenantReply packet '''

    def __init__(self, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EstateCovenantReply'

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['CovenantID'] = None    # MVT_LLUUID
            self.Data['CovenantTimestamp'] = None    # MVT_U32
            self.Data['EstateName'] = None    # MVT_VARIABLE
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Data', CovenantID=self.Data['CovenantID'], CovenantTimestamp=self.Data['CovenantTimestamp'], EstateName=self.Data['EstateName']))

        return Message('EstateCovenantReply', args)

class MapNameRequestPacket(object):
    ''' a template for a MapNameRequest packet '''

    def __init__(self, AgentDataBlock = {}, NameDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MapNameRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['Flags'] = None    # MVT_U32
            self.AgentData['EstateID'] = None    # MVT_U32
            self.AgentData['Godlike'] = None    # MVT_BOOL
        else:
            self.AgentData = AgentDataBlock

        if NameDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.NameData = {}    # New NameData block
            self.NameData['Name'] = None    # MVT_VARIABLE
        else:
            self.NameData = NameDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], Flags=self.AgentData['Flags'], EstateID=self.AgentData['EstateID'], Godlike=self.AgentData['Godlike']))
        args.append(Block('NameData', Name=self.NameData['Name']))

        return Message('MapNameRequest', args)

class AgentHeightWidthPacket(object):
    ''' a template for a AgentHeightWidth packet '''

    def __init__(self, AgentDataBlock = {}, HeightWidthBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentHeightWidth'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['CircuitCode'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

        if HeightWidthBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.HeightWidthBlock = {}    # New HeightWidthBlock block
            self.HeightWidthBlock['GenCounter'] = None    # MVT_U32
            self.HeightWidthBlock['Height'] = None    # MVT_U16
            self.HeightWidthBlock['Width'] = None    # MVT_U16
        else:
            self.HeightWidthBlock = HeightWidthBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], CircuitCode=self.AgentData['CircuitCode']))
        args.append(Block('HeightWidthBlock', GenCounter=self.HeightWidthBlock['GenCounter'], Height=self.HeightWidthBlock['Height'], Width=self.HeightWidthBlock['Width']))

        return Message('AgentHeightWidth', args)

class DeclineCallingCardPacket(object):
    ''' a template for a DeclineCallingCard packet '''

    def __init__(self, AgentDataBlock = {}, TransactionBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DeclineCallingCard'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if TransactionBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransactionBlock = {}    # New TransactionBlock block
            self.TransactionBlock['TransactionID'] = None    # MVT_LLUUID
        else:
            self.TransactionBlock = TransactionBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('TransactionBlock', TransactionID=self.TransactionBlock['TransactionID']))

        return Message('DeclineCallingCard', args)

class EventNotificationRemoveRequestPacket(object):
    ''' a template for a EventNotificationRemoveRequest packet '''

    def __init__(self, AgentDataBlock = {}, EventDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EventNotificationRemoveRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if EventDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.EventData = {}    # New EventData block
            self.EventData['EventID'] = None    # MVT_U32
        else:
            self.EventData = EventDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('EventData', EventID=self.EventData['EventID']))

        return Message('EventNotificationRemoveRequest', args)

class NeighborListPacket(object):
    ''' a template for a NeighborList packet '''

    def __init__(self, NeighborBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'NeighborList'

        if NeighborBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.NeighborBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.NeighborBlock = {}
            self.NeighborBlock['IP'] = None    # MVT_IP_ADDR
            self.NeighborBlock['Port'] = None    # MVT_IP_PORT
            self.NeighborBlock['PublicIP'] = None    # MVT_IP_ADDR
            self.NeighborBlock['PublicPort'] = None    # MVT_IP_PORT
            self.NeighborBlock['RegionID'] = None    # MVT_LLUUID
            self.NeighborBlock['Name'] = None    # MVT_VARIABLE
            self.NeighborBlock['SimAccess'] = None    # MVT_U8
        else:
            self.NeighborBlockBlocks = NeighborBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.NeighborBlockBlocks:
            args.append(Block('NeighborBlock', IP=block['IP'], Port=block['Port'], PublicIP=block['PublicIP'], PublicPort=block['PublicPort'], RegionID=block['RegionID'], Name=block['Name'], SimAccess=block['SimAccess']))

        return Message('NeighborList', args)

class AgentDataUpdateRequestPacket(object):
    ''' a template for a AgentDataUpdateRequest packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentDataUpdateRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('AgentDataUpdateRequest', args)

class GroupNoticeAddPacket(object):
    ''' a template for a GroupNoticeAdd packet '''

    def __init__(self, AgentDataBlock = {}, MessageBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupNoticeAdd'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MessageBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MessageBlock = {}    # New MessageBlock block
            self.MessageBlock['ToGroupID'] = None    # MVT_LLUUID
            self.MessageBlock['ID'] = None    # MVT_LLUUID
            self.MessageBlock['Dialog'] = None    # MVT_U8
            self.MessageBlock['FromAgentName'] = None    # MVT_VARIABLE
            self.MessageBlock['Message'] = None    # MVT_VARIABLE
            self.MessageBlock['BinaryBucket'] = None    # MVT_VARIABLE
        else:
            self.MessageBlock = MessageBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('MessageBlock', ToGroupID=self.MessageBlock['ToGroupID'], ID=self.MessageBlock['ID'], Dialog=self.MessageBlock['Dialog'], FromAgentName=self.MessageBlock['FromAgentName'], Message=self.MessageBlock['Message'], BinaryBucket=self.MessageBlock['BinaryBucket']))

        return Message('GroupNoticeAdd', args)

class CopyInventoryFromNotecardPacket(object):
    ''' a template for a CopyInventoryFromNotecard packet '''

    def __init__(self, AgentDataBlock = {}, NotecardDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CopyInventoryFromNotecard'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if NotecardDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.NotecardData = {}    # New NotecardData block
            self.NotecardData['NotecardItemID'] = None    # MVT_LLUUID
            self.NotecardData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.NotecardData = NotecardDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
            self.InventoryData['ItemID'] = None    # MVT_LLUUID
            self.InventoryData['FolderID'] = None    # MVT_LLUUID
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('NotecardData', NotecardItemID=self.NotecardData['NotecardItemID'], ObjectID=self.NotecardData['ObjectID']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', ItemID=block['ItemID'], FolderID=block['FolderID']))

        return Message('CopyInventoryFromNotecard', args)

class NearestLandingRegionRequestPacket(object):
    ''' a template for a NearestLandingRegionRequest packet '''

    def __init__(self, RequestingRegionDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'NearestLandingRegionRequest'

        if RequestingRegionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RequestingRegionData = {}    # New RequestingRegionData block
            self.RequestingRegionData['RegionHandle'] = None    # MVT_U64
        else:
            self.RequestingRegionData = RequestingRegionDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('RequestingRegionData', RegionHandle=self.RequestingRegionData['RegionHandle']))

        return Message('NearestLandingRegionRequest', args)

class ChildAgentUpdatePacket(object):
    ''' a template for a ChildAgentUpdate packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlocks = [], AnimationDataBlocks = [], GranterBlockBlocks = [], NVPairDataBlocks = [], VisualParamBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ChildAgentUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.GroupDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.GroupData = {}
            self.GroupData['GroupID'] = None    # MVT_LLUUID
            self.GroupData['GroupPowers'] = None    # MVT_U64
            self.GroupData['AcceptNotices'] = None    # MVT_BOOL
        else:
            self.GroupDataBlocks = GroupDataBlocks

        if AnimationDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.AnimationDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.AnimationData = {}
            self.AnimationData['Animation'] = None    # MVT_LLUUID
            self.AnimationData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.AnimationDataBlocks = AnimationDataBlocks

        if GranterBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.GranterBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.GranterBlock = {}
            self.GranterBlock['GranterID'] = None    # MVT_LLUUID
        else:
            self.GranterBlockBlocks = GranterBlockBlocks

        if NVPairDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.NVPairDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.NVPairData = {}
            self.NVPairData['NVPairs'] = None    # MVT_VARIABLE
        else:
            self.NVPairDataBlocks = NVPairDataBlocks

        if VisualParamBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.VisualParamBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.VisualParam = {}
            self.VisualParam['ParamValue'] = None    # MVT_U8
        else:
            self.VisualParamBlocks = VisualParamBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', RegionHandle=self.AgentData['RegionHandle'], ViewerCircuitCode=self.AgentData['ViewerCircuitCode'], AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], AgentPos=self.AgentData['AgentPos'], AgentVel=self.AgentData['AgentVel'], Center=self.AgentData['Center'], Size=self.AgentData['Size'], AtAxis=self.AgentData['AtAxis'], LeftAxis=self.AgentData['LeftAxis'], UpAxis=self.AgentData['UpAxis'], ChangedGrid=self.AgentData['ChangedGrid'], Far=self.AgentData['Far'], Aspect=self.AgentData['Aspect'], Throttles=self.AgentData['Throttles'], HeadRotation=self.AgentData['HeadRotation'], BodyRotation=self.AgentData['BodyRotation'], ControlFlags=self.AgentData['ControlFlags'], EnergyLevel=self.AgentData['EnergyLevel'], GodLevel=self.AgentData['GodLevel'], AlwaysRun=self.AgentData['AlwaysRun'], PreyAgent=self.AgentData['PreyAgent'], AgentAccess=self.AgentData['AgentAccess'], AgentTextures=self.AgentData['AgentTextures'], ActiveGroupID=self.AgentData['ActiveGroupID']))
        for block in self.GroupDataBlocks:
            args.append(Block('GroupData', GroupID=block['GroupID'], GroupPowers=block['GroupPowers'], AcceptNotices=block['AcceptNotices']))
        for block in self.AnimationDataBlocks:
            args.append(Block('AnimationData', Animation=block['Animation'], ObjectID=block['ObjectID']))
        for block in self.GranterBlockBlocks:
            args.append(Block('GranterBlock', GranterID=block['GranterID']))
        for block in self.NVPairDataBlocks:
            args.append(Block('NVPairData', NVPairs=block['NVPairs']))
        for block in self.VisualParamBlocks:
            args.append(Block('VisualParam', ParamValue=block['ParamValue']))

        return Message('ChildAgentUpdate', args)

class DirClassifiedQueryPacket(object):
    ''' a template for a DirClassifiedQuery packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirClassifiedQuery'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['QueryText'] = None    # MVT_VARIABLE
            self.QueryData['QueryFlags'] = None    # MVT_U32
            self.QueryData['Category'] = None    # MVT_U32
            self.QueryData['QueryStart'] = None    # MVT_S32
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], QueryText=self.QueryData['QueryText'], QueryFlags=self.QueryData['QueryFlags'], Category=self.QueryData['Category'], QueryStart=self.QueryData['QueryStart']))

        return Message('DirClassifiedQuery', args)

class GroupRoleUpdatePacket(object):
    ''' a template for a GroupRoleUpdate packet '''

    def __init__(self, AgentDataBlock = {}, RoleDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupRoleUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RoleDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.RoleDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.RoleData = {}
            self.RoleData['RoleID'] = None    # MVT_LLUUID
            self.RoleData['Name'] = None    # MVT_VARIABLE
            self.RoleData['Description'] = None    # MVT_VARIABLE
            self.RoleData['Title'] = None    # MVT_VARIABLE
            self.RoleData['Powers'] = None    # MVT_U64
            self.RoleData['UpdateType'] = None    # MVT_U8
        else:
            self.RoleDataBlocks = RoleDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        for block in self.RoleDataBlocks:
            args.append(Block('RoleData', RoleID=block['RoleID'], Name=block['Name'], Description=block['Description'], Title=block['Title'], Powers=block['Powers'], UpdateType=block['UpdateType']))

        return Message('GroupRoleUpdate', args)

class TestMessagePacket(object):
    ''' a template for a TestMessage packet '''

    def __init__(self, TestBlock1Block = {}, NeighborBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TestMessage'

        if TestBlock1Block == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TestBlock1 = {}    # New TestBlock1 block
            self.TestBlock1['Test1'] = None    # MVT_U32
        else:
            self.TestBlock1 = TestBlock1Block

        if NeighborBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.NeighborBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.NeighborBlock = {}
            self.NeighborBlock['Test0'] = None    # MVT_U32
            self.NeighborBlock['Test1'] = None    # MVT_U32
            self.NeighborBlock['Test2'] = None    # MVT_U32
        else:
            self.NeighborBlockBlocks = NeighborBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TestBlock1', Test1=self.TestBlock1['Test1']))
        for block in self.NeighborBlockBlocks:
            args.append(Block('NeighborBlock', Test0=block['Test0'], Test1=block['Test1'], Test2=block['Test2']))

        return Message('TestMessage', args)

class GroupAccountDetailsReplyPacket(object):
    ''' a template for a GroupAccountDetailsReply packet '''

    def __init__(self, AgentDataBlock = {}, MoneyDataBlock = {}, HistoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupAccountDetailsReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MoneyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MoneyData = {}    # New MoneyData block
            self.MoneyData['RequestID'] = None    # MVT_LLUUID
            self.MoneyData['IntervalDays'] = None    # MVT_S32
            self.MoneyData['CurrentInterval'] = None    # MVT_S32
            self.MoneyData['StartDate'] = None    # MVT_VARIABLE
        else:
            self.MoneyData = MoneyDataBlock

        if HistoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.HistoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.HistoryData = {}
            self.HistoryData['Description'] = None    # MVT_VARIABLE
            self.HistoryData['Amount'] = None    # MVT_S32
        else:
            self.HistoryDataBlocks = HistoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('MoneyData', RequestID=self.MoneyData['RequestID'], IntervalDays=self.MoneyData['IntervalDays'], CurrentInterval=self.MoneyData['CurrentInterval'], StartDate=self.MoneyData['StartDate']))
        for block in self.HistoryDataBlocks:
            args.append(Block('HistoryData', Description=block['Description'], Amount=block['Amount']))

        return Message('GroupAccountDetailsReply', args)

class UUIDNameRequestPacket(object):
    ''' a template for a UUIDNameRequest packet '''

    def __init__(self, UUIDNameBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UUIDNameRequest'

        if UUIDNameBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.UUIDNameBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.UUIDNameBlock = {}
            self.UUIDNameBlock['ID'] = None    # MVT_LLUUID
        else:
            self.UUIDNameBlockBlocks = UUIDNameBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.UUIDNameBlockBlocks:
            args.append(Block('UUIDNameBlock', ID=block['ID']))

        return Message('UUIDNameRequest', args)

class ObjectDropPacket(object):
    ''' a template for a ObjectDrop packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectDrop'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('ObjectDrop', args)

class AttachedSoundGainChangePacket(object):
    ''' a template for a AttachedSoundGainChange packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AttachedSoundGainChange'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['ObjectID'] = None    # MVT_LLUUID
            self.DataBlock['Gain'] = None    # MVT_F32
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', ObjectID=self.DataBlock['ObjectID'], Gain=self.DataBlock['Gain']))

        return Message('AttachedSoundGainChange', args)

class AssetUploadCompletePacket(object):
    ''' a template for a AssetUploadComplete packet '''

    def __init__(self, AssetBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AssetUploadComplete'

        if AssetBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AssetBlock = {}    # New AssetBlock block
            self.AssetBlock['UUID'] = None    # MVT_LLUUID
            self.AssetBlock['Type'] = None    # MVT_S8
            self.AssetBlock['Success'] = None    # MVT_BOOL
        else:
            self.AssetBlock = AssetBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AssetBlock', UUID=self.AssetBlock['UUID'], Type=self.AssetBlock['Type'], Success=self.AssetBlock['Success']))

        return Message('AssetUploadComplete', args)

class ParcelBuyPacket(object):
    ''' a template for a ParcelBuy packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelBuy'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['GroupID'] = None    # MVT_LLUUID
            self.Data['IsGroupOwned'] = None    # MVT_BOOL
            self.Data['RemoveContribution'] = None    # MVT_BOOL
            self.Data['LocalID'] = None    # MVT_S32
            self.Data['Final'] = None    # MVT_BOOL
        else:
            self.Data = DataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['Price'] = None    # MVT_S32
            self.ParcelData['Area'] = None    # MVT_S32
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', GroupID=self.Data['GroupID'], IsGroupOwned=self.Data['IsGroupOwned'], RemoveContribution=self.Data['RemoveContribution'], LocalID=self.Data['LocalID'], Final=self.Data['Final']))
        args.append(Block('ParcelData', Price=self.ParcelData['Price'], Area=self.ParcelData['Area']))

        return Message('ParcelBuy', args)

class RpcScriptReplyInboundPacket(object):
    ''' a template for a RpcScriptReplyInbound packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RpcScriptReplyInbound'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['TaskID'] = None    # MVT_LLUUID
            self.DataBlock['ItemID'] = None    # MVT_LLUUID
            self.DataBlock['ChannelID'] = None    # MVT_LLUUID
            self.DataBlock['IntValue'] = None    # MVT_U32
            self.DataBlock['StringValue'] = None    # MVT_VARIABLE
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', TaskID=self.DataBlock['TaskID'], ItemID=self.DataBlock['ItemID'], ChannelID=self.DataBlock['ChannelID'], IntValue=self.DataBlock['IntValue'], StringValue=self.DataBlock['StringValue']))

        return Message('RpcScriptReplyInbound', args)

class ObjectScalePacket(object):
    ''' a template for a ObjectScale packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectScale'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['Scale'] = None    # MVT_LLVector3
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], Scale=block['Scale']))

        return Message('ObjectScale', args)

class TransferInventoryAckPacket(object):
    ''' a template for a TransferInventoryAck packet '''

    def __init__(self, InfoBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TransferInventoryAck'

        if InfoBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.InfoBlock = {}    # New InfoBlock block
            self.InfoBlock['TransactionID'] = None    # MVT_LLUUID
            self.InfoBlock['InventoryID'] = None    # MVT_LLUUID
        else:
            self.InfoBlock = InfoBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('InfoBlock', TransactionID=self.InfoBlock['TransactionID'], InventoryID=self.InfoBlock['InventoryID']))

        return Message('TransferInventoryAck', args)

class ScriptDialogReplyPacket(object):
    ''' a template for a ScriptDialogReply packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptDialogReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['ObjectID'] = None    # MVT_LLUUID
            self.Data['ChatChannel'] = None    # MVT_S32
            self.Data['ButtonIndex'] = None    # MVT_S32
            self.Data['ButtonLabel'] = None    # MVT_VARIABLE
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', ObjectID=self.Data['ObjectID'], ChatChannel=self.Data['ChatChannel'], ButtonIndex=self.Data['ButtonIndex'], ButtonLabel=self.Data['ButtonLabel']))

        return Message('ScriptDialogReply', args)

class RezSingleAttachmentFromInvPacket(object):
    ''' a template for a RezSingleAttachmentFromInv packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RezSingleAttachmentFromInv'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.ObjectData = ObjectDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ObjectData', ItemID=self.ObjectData['ItemID'], OwnerID=self.ObjectData['OwnerID'], AttachmentPt=self.ObjectData['AttachmentPt'], ItemFlags=self.ObjectData['ItemFlags'], GroupMask=self.ObjectData['GroupMask'], EveryoneMask=self.ObjectData['EveryoneMask'], NextOwnerMask=self.ObjectData['NextOwnerMask'], Name=self.ObjectData['Name'], Description=self.ObjectData['Description']))

        return Message('RezSingleAttachmentFromInv', args)

class StartLurePacket(object):
    ''' a template for a StartLure packet '''

    def __init__(self, AgentDataBlock = {}, InfoBlock = {}, TargetDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'StartLure'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['LureType'] = None    # MVT_U8
            self.Info['Message'] = None    # MVT_VARIABLE
        else:
            self.Info = InfoBlock

        if TargetDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.TargetDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.TargetData = {}
            self.TargetData['TargetID'] = None    # MVT_LLUUID
        else:
            self.TargetDataBlocks = TargetDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Info', LureType=self.Info['LureType'], Message=self.Info['Message']))
        for block in self.TargetDataBlocks:
            args.append(Block('TargetData', TargetID=block['TargetID']))

        return Message('StartLure', args)

class UpdateInventoryFolderPacket(object):
    ''' a template for a UpdateInventoryFolder packet '''

    def __init__(self, AgentDataBlock = {}, FolderDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UpdateInventoryFolder'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if FolderDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.FolderDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.FolderData = {}
            self.FolderData['FolderID'] = None    # MVT_LLUUID
            self.FolderData['ParentID'] = None    # MVT_LLUUID
            self.FolderData['Type'] = None    # MVT_S8
            self.FolderData['Name'] = None    # MVT_VARIABLE
        else:
            self.FolderDataBlocks = FolderDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.FolderDataBlocks:
            args.append(Block('FolderData', FolderID=block['FolderID'], ParentID=block['ParentID'], Type=block['Type'], Name=block['Name']))

        return Message('UpdateInventoryFolder', args)

class TransferRequestPacket(object):
    ''' a template for a TransferRequest packet '''

    def __init__(self, TransferInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TransferRequest'

        if TransferInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransferInfo = {}    # New TransferInfo block
            self.TransferInfo['TransferID'] = None    # MVT_LLUUID
            self.TransferInfo['ChannelType'] = None    # MVT_S32
            self.TransferInfo['SourceType'] = None    # MVT_S32
            self.TransferInfo['Priority'] = None    # MVT_F32
            self.TransferInfo['Params'] = None    # MVT_VARIABLE
        else:
            self.TransferInfo = TransferInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TransferInfo', TransferID=self.TransferInfo['TransferID'], ChannelType=self.TransferInfo['ChannelType'], SourceType=self.TransferInfo['SourceType'], Priority=self.TransferInfo['Priority'], Params=self.TransferInfo['Params']))

        return Message('TransferRequest', args)

class KillObjectPacket(object):
    ''' a template for a KillObject packet '''

    def __init__(self, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'KillObject'

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ID=block['ID']))

        return Message('KillObject', args)

class DirFindQueryBackendPacket(object):
    ''' a template for a DirFindQueryBackend packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirFindQueryBackend'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['QueryText'] = None    # MVT_VARIABLE
            self.QueryData['QueryFlags'] = None    # MVT_U32
            self.QueryData['QueryStart'] = None    # MVT_S32
            self.QueryData['EstateID'] = None    # MVT_U32
            self.QueryData['Godlike'] = None    # MVT_BOOL
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], QueryText=self.QueryData['QueryText'], QueryFlags=self.QueryData['QueryFlags'], QueryStart=self.QueryData['QueryStart'], EstateID=self.QueryData['EstateID'], Godlike=self.QueryData['Godlike']))

        return Message('DirFindQueryBackend', args)

class ViewerStatsPacket(object):
    ''' a template for a ViewerStats packet '''

    def __init__(self):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ViewerStats'

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []

        return Message('ViewerStats', args)

class TelehubInfoPacket(object):
    ''' a template for a TelehubInfo packet '''

    def __init__(self, TelehubBlockBlock = {}, SpawnPointBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TelehubInfo'

        if TelehubBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TelehubBlock = {}    # New TelehubBlock block
            self.TelehubBlock['ObjectID'] = None    # MVT_LLUUID
            self.TelehubBlock['ObjectName'] = None    # MVT_VARIABLE
            self.TelehubBlock['TelehubPos'] = None    # MVT_LLVector3
            self.TelehubBlock['TelehubRot'] = None    # MVT_LLQuaternion
        else:
            self.TelehubBlock = TelehubBlockBlock

        if SpawnPointBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.SpawnPointBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.SpawnPointBlock = {}
            self.SpawnPointBlock['SpawnPointPos'] = None    # MVT_LLVector3
        else:
            self.SpawnPointBlockBlocks = SpawnPointBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TelehubBlock', ObjectID=self.TelehubBlock['ObjectID'], ObjectName=self.TelehubBlock['ObjectName'], TelehubPos=self.TelehubBlock['TelehubPos'], TelehubRot=self.TelehubBlock['TelehubRot']))
        for block in self.SpawnPointBlockBlocks:
            args.append(Block('SpawnPointBlock', SpawnPointPos=block['SpawnPointPos']))

        return Message('TelehubInfo', args)

class TallyVotesPacket(object):
    ''' a template for a TallyVotes packet '''

    def __init__(self):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TallyVotes'

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []

        return Message('TallyVotes', args)

class ScriptRunningReplyPacket(object):
    ''' a template for a ScriptRunningReply packet '''

    def __init__(self, ScriptBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptRunningReply'

        if ScriptBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Script = {}    # New Script block
            self.Script['ObjectID'] = None    # MVT_LLUUID
            self.Script['ItemID'] = None    # MVT_LLUUID
            self.Script['Running'] = None    # MVT_BOOL
        else:
            self.Script = ScriptBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Script', ObjectID=self.Script['ObjectID'], ItemID=self.Script['ItemID'], Running=self.Script['Running']))

        return Message('ScriptRunningReply', args)

class ObjectExportSelectedPacket(object):
    ''' a template for a ObjectExportSelected packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectExportSelected'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['RequestID'] = None    # MVT_LLUUID
            self.AgentData['VolumeDetail'] = None    # MVT_S16
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], RequestID=self.AgentData['RequestID'], VolumeDetail=self.AgentData['VolumeDetail']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectID=block['ObjectID']))

        return Message('ObjectExportSelected', args)

class JoinGroupRequestPacket(object):
    ''' a template for a JoinGroupRequest packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'JoinGroupRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
        else:
            self.GroupData = GroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID']))

        return Message('JoinGroupRequest', args)

class RemoveParcelPacket(object):
    ''' a template for a RemoveParcel packet '''

    def __init__(self, ParcelDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RemoveParcel'

        if ParcelDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParcelDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParcelData = {}
            self.ParcelData['ParcelID'] = None    # MVT_LLUUID
        else:
            self.ParcelDataBlocks = ParcelDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.ParcelDataBlocks:
            args.append(Block('ParcelData', ParcelID=block['ParcelID']))

        return Message('RemoveParcel', args)

class ObjectGroupPacket(object):
    ''' a template for a ObjectGroup packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectGroup'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('ObjectGroup', args)

class CreateInventoryItemPacket(object):
    ''' a template for a CreateInventoryItem packet '''

    def __init__(self, AgentDataBlock = {}, InventoryBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CreateInventoryItem'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.InventoryBlock = InventoryBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('InventoryBlock', CallbackID=self.InventoryBlock['CallbackID'], FolderID=self.InventoryBlock['FolderID'], TransactionID=self.InventoryBlock['TransactionID'], NextOwnerMask=self.InventoryBlock['NextOwnerMask'], Type=self.InventoryBlock['Type'], InvType=self.InventoryBlock['InvType'], WearableType=self.InventoryBlock['WearableType'], Name=self.InventoryBlock['Name'], Description=self.InventoryBlock['Description']))

        return Message('CreateInventoryItem', args)

class PickInfoReplyPacket(object):
    ''' a template for a PickInfoReply packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'PickInfoReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('Data', PickID=self.Data['PickID'], CreatorID=self.Data['CreatorID'], TopPick=self.Data['TopPick'], ParcelID=self.Data['ParcelID'], Name=self.Data['Name'], Desc=self.Data['Desc'], SnapshotID=self.Data['SnapshotID'], User=self.Data['User'], OriginalName=self.Data['OriginalName'], SimName=self.Data['SimName'], PosGlobal=self.Data['PosGlobal'], SortOrder=self.Data['SortOrder'], Enabled=self.Data['Enabled']))

        return Message('PickInfoReply', args)

class SystemMessagePacket(object):
    ''' a template for a SystemMessage packet '''

    def __init__(self, MethodDataBlock = {}, ParamListBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SystemMessage'

        if MethodDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MethodData = {}    # New MethodData block
            self.MethodData['Method'] = None    # MVT_VARIABLE
            self.MethodData['Invoice'] = None    # MVT_LLUUID
            self.MethodData['Digest'] = None    # MVT_FIXED
        else:
            self.MethodData = MethodDataBlock

        if ParamListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParamListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParamList = {}
            self.ParamList['Parameter'] = None    # MVT_VARIABLE
        else:
            self.ParamListBlocks = ParamListBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('MethodData', Method=self.MethodData['Method'], Invoice=self.MethodData['Invoice'], Digest=self.MethodData['Digest']))
        for block in self.ParamListBlocks:
            args.append(Block('ParamList', Parameter=block['Parameter']))

        return Message('SystemMessage', args)

class AgentResumePacket(object):
    ''' a template for a AgentResume packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentResume'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['SerialNum'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], SerialNum=self.AgentData['SerialNum']))

        return Message('AgentResume', args)

class InventoryAssetResponsePacket(object):
    ''' a template for a InventoryAssetResponse packet '''

    def __init__(self, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'InventoryAssetResponse'

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['AssetID'] = None    # MVT_LLUUID
            self.QueryData['IsReadable'] = None    # MVT_BOOL
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], AssetID=self.QueryData['AssetID'], IsReadable=self.QueryData['IsReadable']))

        return Message('InventoryAssetResponse', args)

class PayPriceReplyPacket(object):
    ''' a template for a PayPriceReply packet '''

    def __init__(self, ObjectDataBlock = {}, ButtonDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'PayPriceReply'

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
            self.ObjectData['DefaultPayPrice'] = None    # MVT_S32
        else:
            self.ObjectData = ObjectDataBlock

        if ButtonDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ButtonDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ButtonData = {}
            self.ButtonData['PayButton'] = None    # MVT_S32
        else:
            self.ButtonDataBlocks = ButtonDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ObjectData', ObjectID=self.ObjectData['ObjectID'], DefaultPayPrice=self.ObjectData['DefaultPayPrice']))
        for block in self.ButtonDataBlocks:
            args.append(Block('ButtonData', PayButton=block['PayButton']))

        return Message('PayPriceReply', args)

class ParcelPropertiesPacket(object):
    ''' a template for a ParcelProperties packet '''

    def __init__(self, ParcelDataBlock = {}, AgeVerificationBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelProperties'

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.ParcelData = ParcelDataBlock

        if AgeVerificationBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgeVerificationBlock = {}    # New AgeVerificationBlock block
            self.AgeVerificationBlock['RegionDenyAgeUnverified'] = None    # MVT_BOOL
        else:
            self.AgeVerificationBlock = AgeVerificationBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ParcelData', RequestResult=self.ParcelData['RequestResult'], SequenceID=self.ParcelData['SequenceID'], SnapSelection=self.ParcelData['SnapSelection'], SelfCount=self.ParcelData['SelfCount'], OtherCount=self.ParcelData['OtherCount'], PublicCount=self.ParcelData['PublicCount'], LocalID=self.ParcelData['LocalID'], OwnerID=self.ParcelData['OwnerID'], IsGroupOwned=self.ParcelData['IsGroupOwned'], AuctionID=self.ParcelData['AuctionID'], ClaimDate=self.ParcelData['ClaimDate'], ClaimPrice=self.ParcelData['ClaimPrice'], RentPrice=self.ParcelData['RentPrice'], AABBMin=self.ParcelData['AABBMin'], AABBMax=self.ParcelData['AABBMax'], Bitmap=self.ParcelData['Bitmap'], Area=self.ParcelData['Area'], Status=self.ParcelData['Status'], SimWideMaxPrims=self.ParcelData['SimWideMaxPrims'], SimWideTotalPrims=self.ParcelData['SimWideTotalPrims'], MaxPrims=self.ParcelData['MaxPrims'], TotalPrims=self.ParcelData['TotalPrims'], OwnerPrims=self.ParcelData['OwnerPrims'], GroupPrims=self.ParcelData['GroupPrims'], OtherPrims=self.ParcelData['OtherPrims'], SelectedPrims=self.ParcelData['SelectedPrims'], ParcelPrimBonus=self.ParcelData['ParcelPrimBonus'], OtherCleanTime=self.ParcelData['OtherCleanTime'], ParcelFlags=self.ParcelData['ParcelFlags'], SalePrice=self.ParcelData['SalePrice'], Name=self.ParcelData['Name'], Desc=self.ParcelData['Desc'], MusicURL=self.ParcelData['MusicURL'], MediaURL=self.ParcelData['MediaURL'], MediaID=self.ParcelData['MediaID'], MediaAutoScale=self.ParcelData['MediaAutoScale'], GroupID=self.ParcelData['GroupID'], PassPrice=self.ParcelData['PassPrice'], PassHours=self.ParcelData['PassHours'], Category=self.ParcelData['Category'], AuthBuyerID=self.ParcelData['AuthBuyerID'], SnapshotID=self.ParcelData['SnapshotID'], UserLocation=self.ParcelData['UserLocation'], UserLookAt=self.ParcelData['UserLookAt'], LandingType=self.ParcelData['LandingType'], RegionPushOverride=self.ParcelData['RegionPushOverride'], RegionDenyAnonymous=self.ParcelData['RegionDenyAnonymous'], RegionDenyIdentified=self.ParcelData['RegionDenyIdentified'], RegionDenyTransacted=self.ParcelData['RegionDenyTransacted']))
        args.append(Block('AgeVerificationBlock', RegionDenyAgeUnverified=self.AgeVerificationBlock['RegionDenyAgeUnverified']))

        return Message('ParcelProperties', args)

class DirClassifiedReplyPacket(object):
    ''' a template for a DirClassifiedReply packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}, QueryRepliesBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirClassifiedReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
        else:
            self.QueryData = QueryDataBlock

        if QueryRepliesBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.QueryRepliesBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.QueryReplies = {}
            self.QueryReplies['ClassifiedID'] = None    # MVT_LLUUID
            self.QueryReplies['Name'] = None    # MVT_VARIABLE
            self.QueryReplies['ClassifiedFlags'] = None    # MVT_U8
            self.QueryReplies['CreationDate'] = None    # MVT_U32
            self.QueryReplies['ExpirationDate'] = None    # MVT_U32
            self.QueryReplies['PriceForListing'] = None    # MVT_S32
        else:
            self.QueryRepliesBlocks = QueryRepliesBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID']))
        for block in self.QueryRepliesBlocks:
            args.append(Block('QueryReplies', ClassifiedID=block['ClassifiedID'], Name=block['Name'], ClassifiedFlags=block['ClassifiedFlags'], CreationDate=block['CreationDate'], ExpirationDate=block['ExpirationDate'], PriceForListing=block['PriceForListing']))

        return Message('DirClassifiedReply', args)

class GenericMessagePacket(object):
    ''' a template for a GenericMessage packet '''

    def __init__(self, AgentDataBlock = {}, MethodDataBlock = {}, ParamListBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GenericMessage'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MethodDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MethodData = {}    # New MethodData block
            self.MethodData['Method'] = None    # MVT_VARIABLE
            self.MethodData['Invoice'] = None    # MVT_LLUUID
        else:
            self.MethodData = MethodDataBlock

        if ParamListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParamListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParamList = {}
            self.ParamList['Parameter'] = None    # MVT_VARIABLE
        else:
            self.ParamListBlocks = ParamListBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], TransactionID=self.AgentData['TransactionID']))
        args.append(Block('MethodData', Method=self.MethodData['Method'], Invoice=self.MethodData['Invoice']))
        for block in self.ParamListBlocks:
            args.append(Block('ParamList', Parameter=block['Parameter']))

        return Message('GenericMessage', args)

class SimStatsPacket(object):
    ''' a template for a SimStats packet '''

    def __init__(self, RegionBlock = {}, StatBlocks = [], PidStatBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SimStats'

        if RegionBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Region = {}    # New Region block
            self.Region['RegionX'] = None    # MVT_U32
            self.Region['RegionY'] = None    # MVT_U32
            self.Region['RegionFlags'] = None    # MVT_U32
            self.Region['ObjectCapacity'] = None    # MVT_U32
        else:
            self.Region = RegionBlock

        if StatBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.StatBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Stat = {}
            self.Stat['StatID'] = None    # MVT_U32
            self.Stat['StatValue'] = None    # MVT_F32
        else:
            self.StatBlocks = StatBlocks

        if PidStatBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.PidStat = {}    # New PidStat block
            self.PidStat['PID'] = None    # MVT_S32
        else:
            self.PidStat = PidStatBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Region', RegionX=self.Region['RegionX'], RegionY=self.Region['RegionY'], RegionFlags=self.Region['RegionFlags'], ObjectCapacity=self.Region['ObjectCapacity']))
        for block in self.StatBlocks:
            args.append(Block('Stat', StatID=block['StatID'], StatValue=block['StatValue']))
        args.append(Block('PidStat', PID=self.PidStat['PID']))

        return Message('SimStats', args)

class FeatureDisabledPacket(object):
    ''' a template for a FeatureDisabled packet '''

    def __init__(self, FailureInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'FeatureDisabled'

        if FailureInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.FailureInfo = {}    # New FailureInfo block
            self.FailureInfo['ErrorMessage'] = None    # MVT_VARIABLE
            self.FailureInfo['AgentID'] = None    # MVT_LLUUID
            self.FailureInfo['TransactionID'] = None    # MVT_LLUUID
        else:
            self.FailureInfo = FailureInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('FailureInfo', ErrorMessage=self.FailureInfo['ErrorMessage'], AgentID=self.FailureInfo['AgentID'], TransactionID=self.FailureInfo['TransactionID']))

        return Message('FeatureDisabled', args)

class PacketAckPacket(object):
    ''' a template for a PacketAck packet '''

    def __init__(self, PacketsBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'PacketAck'

        if PacketsBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.PacketsBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Packets = {}
            self.Packets['ID'] = None    # MVT_U32
        else:
            self.PacketsBlocks = PacketsBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.PacketsBlocks:
            args.append(Block('Packets', ID=block['ID']))

        return Message('PacketAck', args)

class GroupRoleMembersReplyPacket(object):
    ''' a template for a GroupRoleMembersReply packet '''

    def __init__(self, AgentDataBlock = {}, MemberDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupRoleMembersReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
            self.AgentData['RequestID'] = None    # MVT_LLUUID
            self.AgentData['TotalPairs'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

        if MemberDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.MemberDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.MemberData = {}
            self.MemberData['RoleID'] = None    # MVT_LLUUID
            self.MemberData['MemberID'] = None    # MVT_LLUUID
        else:
            self.MemberDataBlocks = MemberDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], GroupID=self.AgentData['GroupID'], RequestID=self.AgentData['RequestID'], TotalPairs=self.AgentData['TotalPairs']))
        for block in self.MemberDataBlocks:
            args.append(Block('MemberData', RoleID=block['RoleID'], MemberID=block['MemberID']))

        return Message('GroupRoleMembersReply', args)

class LogoutReplyPacket(object):
    ''' a template for a LogoutReply packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LogoutReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
            self.InventoryData['ItemID'] = None    # MVT_LLUUID
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', ItemID=block['ItemID']))

        return Message('LogoutReply', args)

class EmailMessageReplyPacket(object):
    ''' a template for a EmailMessageReply packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EmailMessageReply'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['ObjectID'] = None    # MVT_LLUUID
            self.DataBlock['More'] = None    # MVT_U32
            self.DataBlock['Time'] = None    # MVT_U32
            self.DataBlock['FromAddress'] = None    # MVT_VARIABLE
            self.DataBlock['Subject'] = None    # MVT_VARIABLE
            self.DataBlock['Data'] = None    # MVT_VARIABLE
            self.DataBlock['MailFilter'] = None    # MVT_VARIABLE
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', ObjectID=self.DataBlock['ObjectID'], More=self.DataBlock['More'], Time=self.DataBlock['Time'], FromAddress=self.DataBlock['FromAddress'], Subject=self.DataBlock['Subject'], Data=self.DataBlock['Data'], MailFilter=self.DataBlock['MailFilter']))

        return Message('EmailMessageReply', args)

class CompleteAuctionPacket(object):
    ''' a template for a CompleteAuction packet '''

    def __init__(self, ParcelDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CompleteAuction'

        if ParcelDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParcelDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParcelData = {}
            self.ParcelData['ParcelID'] = None    # MVT_LLUUID
        else:
            self.ParcelDataBlocks = ParcelDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.ParcelDataBlocks:
            args.append(Block('ParcelData', ParcelID=block['ParcelID']))

        return Message('CompleteAuction', args)

class ObjectSelectPacket(object):
    ''' a template for a ObjectSelect packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectSelect'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('ObjectSelect', args)

class MultipleObjectUpdatePacket(object):
    ''' a template for a MultipleObjectUpdate packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MultipleObjectUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['Type'] = None    # MVT_U8
            self.ObjectData['Data'] = None    # MVT_VARIABLE
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], Type=block['Type'], Data=block['Data']))

        return Message('MultipleObjectUpdate', args)

class MoneyBalanceReplyPacket(object):
    ''' a template for a MoneyBalanceReply packet '''

    def __init__(self, MoneyDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MoneyBalanceReply'

        if MoneyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MoneyData = {}    # New MoneyData block
            self.MoneyData['AgentID'] = None    # MVT_LLUUID
            self.MoneyData['TransactionID'] = None    # MVT_LLUUID
            self.MoneyData['TransactionSuccess'] = None    # MVT_BOOL
            self.MoneyData['MoneyBalance'] = None    # MVT_S32
            self.MoneyData['SquareMetersCredit'] = None    # MVT_S32
            self.MoneyData['SquareMetersCommitted'] = None    # MVT_S32
            self.MoneyData['Description'] = None    # MVT_VARIABLE
        else:
            self.MoneyData = MoneyDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('MoneyData', AgentID=self.MoneyData['AgentID'], TransactionID=self.MoneyData['TransactionID'], TransactionSuccess=self.MoneyData['TransactionSuccess'], MoneyBalance=self.MoneyData['MoneyBalance'], SquareMetersCredit=self.MoneyData['SquareMetersCredit'], SquareMetersCommitted=self.MoneyData['SquareMetersCommitted'], Description=self.MoneyData['Description']))

        return Message('MoneyBalanceReply', args)

class RevokePermissionsPacket(object):
    ''' a template for a RevokePermissions packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RevokePermissions'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['ObjectID'] = None    # MVT_LLUUID
            self.Data['ObjectPermissions'] = None    # MVT_U32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', ObjectID=self.Data['ObjectID'], ObjectPermissions=self.Data['ObjectPermissions']))

        return Message('RevokePermissions', args)

class RpcChannelRequestPacket(object):
    ''' a template for a RpcChannelRequest packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RpcChannelRequest'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['GridX'] = None    # MVT_U32
            self.DataBlock['GridY'] = None    # MVT_U32
            self.DataBlock['TaskID'] = None    # MVT_LLUUID
            self.DataBlock['ItemID'] = None    # MVT_LLUUID
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', GridX=self.DataBlock['GridX'], GridY=self.DataBlock['GridY'], TaskID=self.DataBlock['TaskID'], ItemID=self.DataBlock['ItemID']))

        return Message('RpcChannelRequest', args)

class TeleportCancelPacket(object):
    ''' a template for a TeleportCancel packet '''

    def __init__(self, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TeleportCancel'

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['AgentID'] = None    # MVT_LLUUID
            self.Info['SessionID'] = None    # MVT_LLUUID
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Info', AgentID=self.Info['AgentID'], SessionID=self.Info['SessionID']))

        return Message('TeleportCancel', args)

class DeRezAckPacket(object):
    ''' a template for a DeRezAck packet '''

    def __init__(self, TransactionDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DeRezAck'

        if TransactionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransactionData = {}    # New TransactionData block
            self.TransactionData['TransactionID'] = None    # MVT_LLUUID
            self.TransactionData['Success'] = None    # MVT_BOOL
        else:
            self.TransactionData = TransactionDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TransactionData', TransactionID=self.TransactionData['TransactionID'], Success=self.TransactionData['Success']))

        return Message('DeRezAck', args)

class AvatarPropertiesReplyPacket(object):
    ''' a template for a AvatarPropertiesReply packet '''

    def __init__(self, AgentDataBlock = {}, PropertiesDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarPropertiesReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['AvatarID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if PropertiesDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.PropertiesData = PropertiesDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], AvatarID=self.AgentData['AvatarID']))
        args.append(Block('PropertiesData', ImageID=self.PropertiesData['ImageID'], FLImageID=self.PropertiesData['FLImageID'], PartnerID=self.PropertiesData['PartnerID'], AboutText=self.PropertiesData['AboutText'], FLAboutText=self.PropertiesData['FLAboutText'], BornOn=self.PropertiesData['BornOn'], ProfileURL=self.PropertiesData['ProfileURL'], CharterMember=self.PropertiesData['CharterMember'], Flags=self.PropertiesData['Flags']))

        return Message('AvatarPropertiesReply', args)

class ObjectUpdateCachedPacket(object):
    ''' a template for a ObjectUpdateCached packet '''

    def __init__(self, RegionDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectUpdateCached'

        if RegionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionData = {}    # New RegionData block
            self.RegionData['RegionHandle'] = None    # MVT_U64
            self.RegionData['TimeDilation'] = None    # MVT_U16
        else:
            self.RegionData = RegionDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ID'] = None    # MVT_U32
            self.ObjectData['CRC'] = None    # MVT_U32
            self.ObjectData['UpdateFlags'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('RegionData', RegionHandle=self.RegionData['RegionHandle'], TimeDilation=self.RegionData['TimeDilation']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ID=block['ID'], CRC=block['CRC'], UpdateFlags=block['UpdateFlags']))

        return Message('ObjectUpdateCached', args)

class LogTextMessagePacket(object):
    ''' a template for a LogTextMessage packet '''

    def __init__(self, DataBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LogTextMessage'

        if DataBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.DataBlock = {}
            self.DataBlock['FromAgentId'] = None    # MVT_LLUUID
            self.DataBlock['ToAgentId'] = None    # MVT_LLUUID
            self.DataBlock['GlobalX'] = None    # MVT_F64
            self.DataBlock['GlobalY'] = None    # MVT_F64
            self.DataBlock['Time'] = None    # MVT_U32
            self.DataBlock['Message'] = None    # MVT_VARIABLE
        else:
            self.DataBlockBlocks = DataBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.DataBlockBlocks:
            args.append(Block('DataBlock', FromAgentId=block['FromAgentId'], ToAgentId=block['ToAgentId'], GlobalX=block['GlobalX'], GlobalY=block['GlobalY'], Time=block['Time'], Message=block['Message']))

        return Message('LogTextMessage', args)

class DirLandReplyPacket(object):
    ''' a template for a DirLandReply packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}, QueryRepliesBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirLandReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
        else:
            self.QueryData = QueryDataBlock

        if QueryRepliesBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.QueryRepliesBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.QueryReplies = {}
            self.QueryReplies['ParcelID'] = None    # MVT_LLUUID
            self.QueryReplies['Name'] = None    # MVT_VARIABLE
            self.QueryReplies['Auction'] = None    # MVT_BOOL
            self.QueryReplies['ForSale'] = None    # MVT_BOOL
            self.QueryReplies['SalePrice'] = None    # MVT_S32
            self.QueryReplies['ActualArea'] = None    # MVT_S32
        else:
            self.QueryRepliesBlocks = QueryRepliesBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID']))
        for block in self.QueryRepliesBlocks:
            args.append(Block('QueryReplies', ParcelID=block['ParcelID'], Name=block['Name'], Auction=block['Auction'], ForSale=block['ForSale'], SalePrice=block['SalePrice'], ActualArea=block['ActualArea']))

        return Message('DirLandReply', args)

class RemoveInventoryItemPacket(object):
    ''' a template for a RemoveInventoryItem packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RemoveInventoryItem'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
            self.InventoryData['ItemID'] = None    # MVT_LLUUID
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', ItemID=block['ItemID']))

        return Message('RemoveInventoryItem', args)

class RegionHandshakeReplyPacket(object):
    ''' a template for a RegionHandshakeReply packet '''

    def __init__(self, AgentDataBlock = {}, RegionInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RegionHandshakeReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RegionInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionInfo = {}    # New RegionInfo block
            self.RegionInfo['Flags'] = None    # MVT_U32
        else:
            self.RegionInfo = RegionInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('RegionInfo', Flags=self.RegionInfo['Flags']))

        return Message('RegionHandshakeReply', args)

class AvatarPickerReplyPacket(object):
    ''' a template for a AvatarPickerReply packet '''

    def __init__(self, AgentDataBlock = {}, DataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarPickerReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['QueryID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Data = {}
            self.Data['AvatarID'] = None    # MVT_LLUUID
            self.Data['FirstName'] = None    # MVT_VARIABLE
            self.Data['LastName'] = None    # MVT_VARIABLE
        else:
            self.DataBlocks = DataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], QueryID=self.AgentData['QueryID']))
        for block in self.DataBlocks:
            args.append(Block('Data', AvatarID=block['AvatarID'], FirstName=block['FirstName'], LastName=block['LastName']))

        return Message('AvatarPickerReply', args)

class AgentIsNowWearingPacket(object):
    ''' a template for a AgentIsNowWearing packet '''

    def __init__(self, AgentDataBlock = {}, WearableDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentIsNowWearing'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if WearableDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.WearableDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.WearableData = {}
            self.WearableData['ItemID'] = None    # MVT_LLUUID
            self.WearableData['WearableType'] = None    # MVT_U8
        else:
            self.WearableDataBlocks = WearableDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.WearableDataBlocks:
            args.append(Block('WearableData', ItemID=block['ItemID'], WearableType=block['WearableType']))

        return Message('AgentIsNowWearing', args)

class SimulatorSetMapPacket(object):
    ''' a template for a SimulatorSetMap packet '''

    def __init__(self, MapDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SimulatorSetMap'

        if MapDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MapData = {}    # New MapData block
            self.MapData['RegionHandle'] = None    # MVT_U64
            self.MapData['Type'] = None    # MVT_S32
            self.MapData['MapImage'] = None    # MVT_LLUUID
        else:
            self.MapData = MapDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('MapData', RegionHandle=self.MapData['RegionHandle'], Type=self.MapData['Type'], MapImage=self.MapData['MapImage']))

        return Message('SimulatorSetMap', args)

class EjectGroupMemberRequestPacket(object):
    ''' a template for a EjectGroupMemberRequest packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}, EjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EjectGroupMemberRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
        else:
            self.GroupData = GroupDataBlock

        if EjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.EjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.EjectData = {}
            self.EjectData['EjecteeID'] = None    # MVT_LLUUID
        else:
            self.EjectDataBlocks = EjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID']))
        for block in self.EjectDataBlocks:
            args.append(Block('EjectData', EjecteeID=block['EjecteeID']))

        return Message('EjectGroupMemberRequest', args)

class LogParcelChangesPacket(object):
    ''' a template for a LogParcelChanges packet '''

    def __init__(self, AgentDataBlock = {}, RegionDataBlock = {}, ParcelDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LogParcelChanges'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RegionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionData = {}    # New RegionData block
            self.RegionData['RegionHandle'] = None    # MVT_U64
        else:
            self.RegionData = RegionDataBlock

        if ParcelDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParcelDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParcelData = {}
            self.ParcelData['ParcelID'] = None    # MVT_LLUUID
            self.ParcelData['OwnerID'] = None    # MVT_LLUUID
            self.ParcelData['IsOwnerGroup'] = None    # MVT_BOOL
            self.ParcelData['ActualArea'] = None    # MVT_S32
            self.ParcelData['Action'] = None    # MVT_S8
            self.ParcelData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.ParcelDataBlocks = ParcelDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('RegionData', RegionHandle=self.RegionData['RegionHandle']))
        for block in self.ParcelDataBlocks:
            args.append(Block('ParcelData', ParcelID=block['ParcelID'], OwnerID=block['OwnerID'], IsOwnerGroup=block['IsOwnerGroup'], ActualArea=block['ActualArea'], Action=block['Action'], TransactionID=block['TransactionID']))

        return Message('LogParcelChanges', args)

class ObjectDeGrabPacket(object):
    ''' a template for a ObjectDeGrab packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlock = {}, SurfaceInfoBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectDeGrab'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['LocalID'] = None    # MVT_U32
        else:
            self.ObjectData = ObjectDataBlock

        if SurfaceInfoBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.SurfaceInfoBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.SurfaceInfo = {}
            self.SurfaceInfo['UVCoord'] = None    # MVT_LLVector3
            self.SurfaceInfo['STCoord'] = None    # MVT_LLVector3
        else:
            self.SurfaceInfoBlocks = SurfaceInfoBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ObjectData', LocalID=self.ObjectData['LocalID']))
        for block in self.SurfaceInfoBlocks:
            args.append(Block('SurfaceInfo', UVCoord=block['UVCoord'], STCoord=block['STCoord']))

        return Message('ObjectDeGrab', args)

class ParcelPropertiesRequestPacket(object):
    ''' a template for a ParcelPropertiesRequest packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelPropertiesRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['SequenceID'] = None    # MVT_S32
            self.ParcelData['West'] = None    # MVT_F32
            self.ParcelData['South'] = None    # MVT_F32
            self.ParcelData['East'] = None    # MVT_F32
            self.ParcelData['North'] = None    # MVT_F32
            self.ParcelData['SnapSelection'] = None    # MVT_BOOL
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', SequenceID=self.ParcelData['SequenceID'], West=self.ParcelData['West'], South=self.ParcelData['South'], East=self.ParcelData['East'], North=self.ParcelData['North'], SnapSelection=self.ParcelData['SnapSelection']))

        return Message('ParcelPropertiesRequest', args)

class OfflineNotificationPacket(object):
    ''' a template for a OfflineNotification packet '''

    def __init__(self, AgentBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'OfflineNotification'

        if AgentBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.AgentBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.AgentBlock = {}
            self.AgentBlock['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentBlockBlocks = AgentBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.AgentBlockBlocks:
            args.append(Block('AgentBlock', AgentID=block['AgentID']))

        return Message('OfflineNotification', args)

class ParcelSelectObjectsPacket(object):
    ''' a template for a ParcelSelectObjects packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}, ReturnIDsBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelSelectObjects'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['LocalID'] = None    # MVT_S32
            self.ParcelData['ReturnType'] = None    # MVT_U32
        else:
            self.ParcelData = ParcelDataBlock

        if ReturnIDsBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ReturnIDsBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ReturnIDs = {}
            self.ReturnIDs['ReturnID'] = None    # MVT_LLUUID
        else:
            self.ReturnIDsBlocks = ReturnIDsBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', LocalID=self.ParcelData['LocalID'], ReturnType=self.ParcelData['ReturnType']))
        for block in self.ReturnIDsBlocks:
            args.append(Block('ReturnIDs', ReturnID=block['ReturnID']))

        return Message('ParcelSelectObjects', args)

class LandStatReplyPacket(object):
    ''' a template for a LandStatReply packet '''

    def __init__(self, RequestDataBlock = {}, ReportDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LandStatReply'

        if RequestDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RequestData = {}    # New RequestData block
            self.RequestData['ReportType'] = None    # MVT_U32
            self.RequestData['RequestFlags'] = None    # MVT_U32
            self.RequestData['TotalObjectCount'] = None    # MVT_U32
        else:
            self.RequestData = RequestDataBlock

        if ReportDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ReportDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ReportData = {}
            self.ReportData['TaskLocalID'] = None    # MVT_U32
            self.ReportData['TaskID'] = None    # MVT_LLUUID
            self.ReportData['LocationX'] = None    # MVT_F32
            self.ReportData['LocationY'] = None    # MVT_F32
            self.ReportData['LocationZ'] = None    # MVT_F32
            self.ReportData['Score'] = None    # MVT_F32
            self.ReportData['TaskName'] = None    # MVT_VARIABLE
            self.ReportData['OwnerName'] = None    # MVT_VARIABLE
        else:
            self.ReportDataBlocks = ReportDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('RequestData', ReportType=self.RequestData['ReportType'], RequestFlags=self.RequestData['RequestFlags'], TotalObjectCount=self.RequestData['TotalObjectCount']))
        for block in self.ReportDataBlocks:
            args.append(Block('ReportData', TaskLocalID=block['TaskLocalID'], TaskID=block['TaskID'], LocationX=block['LocationX'], LocationY=block['LocationY'], LocationZ=block['LocationZ'], Score=block['Score'], TaskName=block['TaskName'], OwnerName=block['OwnerName']))

        return Message('LandStatReply', args)

class AgentThrottlePacket(object):
    ''' a template for a AgentThrottle packet '''

    def __init__(self, AgentDataBlock = {}, ThrottleBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentThrottle'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['CircuitCode'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

        if ThrottleBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Throttle = {}    # New Throttle block
            self.Throttle['GenCounter'] = None    # MVT_U32
            self.Throttle['Throttles'] = None    # MVT_VARIABLE
        else:
            self.Throttle = ThrottleBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], CircuitCode=self.AgentData['CircuitCode']))
        args.append(Block('Throttle', GenCounter=self.Throttle['GenCounter'], Throttles=self.Throttle['Throttles']))

        return Message('AgentThrottle', args)

class ViewerEffectPacket(object):
    ''' a template for a ViewerEffect packet '''

    def __init__(self, AgentDataBlock = {}, EffectBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ViewerEffect'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if EffectBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.EffectBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Effect = {}
            self.Effect['ID'] = None    # MVT_LLUUID
            self.Effect['AgentID'] = None    # MVT_LLUUID
            self.Effect['Type'] = None    # MVT_U8
            self.Effect['Duration'] = None    # MVT_F32
            self.Effect['Color'] = None    # MVT_FIXED
            self.Effect['TypeData'] = None    # MVT_VARIABLE
        else:
            self.EffectBlocks = EffectBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.EffectBlocks:
            args.append(Block('Effect', ID=block['ID'], AgentID=block['AgentID'], Type=block['Type'], Duration=block['Duration'], Color=block['Color'], TypeData=block['TypeData']))

        return Message('ViewerEffect', args)

class OfferCallingCardPacket(object):
    ''' a template for a OfferCallingCard packet '''

    def __init__(self, AgentDataBlock = {}, AgentBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'OfferCallingCard'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if AgentBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentBlock = {}    # New AgentBlock block
            self.AgentBlock['DestID'] = None    # MVT_LLUUID
            self.AgentBlock['TransactionID'] = None    # MVT_LLUUID
        else:
            self.AgentBlock = AgentBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('AgentBlock', DestID=self.AgentBlock['DestID'], TransactionID=self.AgentBlock['TransactionID']))

        return Message('OfferCallingCard', args)

class EventInfoReplyPacket(object):
    ''' a template for a EventInfoReply packet '''

    def __init__(self, AgentDataBlock = {}, EventDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EventInfoReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if EventDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.EventData = EventDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('EventData', EventID=self.EventData['EventID'], Creator=self.EventData['Creator'], Name=self.EventData['Name'], Category=self.EventData['Category'], Desc=self.EventData['Desc'], Date=self.EventData['Date'], DateUTC=self.EventData['DateUTC'], Duration=self.EventData['Duration'], Cover=self.EventData['Cover'], Amount=self.EventData['Amount'], SimName=self.EventData['SimName'], GlobalPos=self.EventData['GlobalPos'], EventFlags=self.EventData['EventFlags']))

        return Message('EventInfoReply', args)

class AgentAnimationPacket(object):
    ''' a template for a AgentAnimation packet '''

    def __init__(self, AgentDataBlock = {}, AnimationListBlocks = [], PhysicalAvatarEventListBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentAnimation'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if AnimationListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.AnimationListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.AnimationList = {}
            self.AnimationList['AnimID'] = None    # MVT_LLUUID
            self.AnimationList['StartAnim'] = None    # MVT_BOOL
        else:
            self.AnimationListBlocks = AnimationListBlocks

        if PhysicalAvatarEventListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.PhysicalAvatarEventListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.PhysicalAvatarEventList = {}
            self.PhysicalAvatarEventList['TypeData'] = None    # MVT_VARIABLE
        else:
            self.PhysicalAvatarEventListBlocks = PhysicalAvatarEventListBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.AnimationListBlocks:
            args.append(Block('AnimationList', AnimID=block['AnimID'], StartAnim=block['StartAnim']))
        for block in self.PhysicalAvatarEventListBlocks:
            args.append(Block('PhysicalAvatarEventList', TypeData=block['TypeData']))

        return Message('AgentAnimation', args)

class AgentCachedTexturePacket(object):
    ''' a template for a AgentCachedTexture packet '''

    def __init__(self, AgentDataBlock = {}, WearableDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentCachedTexture'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['SerialNum'] = None    # MVT_S32
        else:
            self.AgentData = AgentDataBlock

        if WearableDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.WearableDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.WearableData = {}
            self.WearableData['ID'] = None    # MVT_LLUUID
            self.WearableData['TextureIndex'] = None    # MVT_U8
        else:
            self.WearableDataBlocks = WearableDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], SerialNum=self.AgentData['SerialNum']))
        for block in self.WearableDataBlocks:
            args.append(Block('WearableData', ID=block['ID'], TextureIndex=block['TextureIndex']))

        return Message('AgentCachedTexture', args)

class GroupNoticesListReplyPacket(object):
    ''' a template for a GroupNoticesListReply packet '''

    def __init__(self, AgentDataBlock = {}, DataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupNoticesListReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Data = {}
            self.Data['NoticeID'] = None    # MVT_LLUUID
            self.Data['Timestamp'] = None    # MVT_U32
            self.Data['FromName'] = None    # MVT_VARIABLE
            self.Data['Subject'] = None    # MVT_VARIABLE
            self.Data['HasAttachment'] = None    # MVT_BOOL
            self.Data['AssetType'] = None    # MVT_U8
        else:
            self.DataBlocks = DataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], GroupID=self.AgentData['GroupID']))
        for block in self.DataBlocks:
            args.append(Block('Data', NoticeID=block['NoticeID'], Timestamp=block['Timestamp'], FromName=block['FromName'], Subject=block['Subject'], HasAttachment=block['HasAttachment'], AssetType=block['AssetType']))

        return Message('GroupNoticesListReply', args)

class FetchInventoryPacket(object):
    ''' a template for a FetchInventory packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'FetchInventory'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
            self.InventoryData['OwnerID'] = None    # MVT_LLUUID
            self.InventoryData['ItemID'] = None    # MVT_LLUUID
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', OwnerID=block['OwnerID'], ItemID=block['ItemID']))

        return Message('FetchInventory', args)

class AvatarAppearancePacket(object):
    ''' a template for a AvatarAppearance packet '''

    def __init__(self, SenderBlock = {}, ObjectDataBlock = {}, VisualParamBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarAppearance'

        if SenderBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Sender = {}    # New Sender block
            self.Sender['ID'] = None    # MVT_LLUUID
            self.Sender['IsTrial'] = None    # MVT_BOOL
        else:
            self.Sender = SenderBlock

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['TextureEntry'] = None    # MVT_VARIABLE
        else:
            self.ObjectData = ObjectDataBlock

        if VisualParamBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.VisualParamBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.VisualParam = {}
            self.VisualParam['ParamValue'] = None    # MVT_U8
        else:
            self.VisualParamBlocks = VisualParamBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Sender', ID=self.Sender['ID'], IsTrial=self.Sender['IsTrial']))
        args.append(Block('ObjectData', TextureEntry=self.ObjectData['TextureEntry']))
        for block in self.VisualParamBlocks:
            args.append(Block('VisualParam', ParamValue=block['ParamValue']))

        return Message('AvatarAppearance', args)

class ChildAgentPositionUpdatePacket(object):
    ''' a template for a ChildAgentPositionUpdate packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ChildAgentPositionUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', RegionHandle=self.AgentData['RegionHandle'], ViewerCircuitCode=self.AgentData['ViewerCircuitCode'], AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], AgentPos=self.AgentData['AgentPos'], AgentVel=self.AgentData['AgentVel'], Center=self.AgentData['Center'], Size=self.AgentData['Size'], AtAxis=self.AgentData['AtAxis'], LeftAxis=self.AgentData['LeftAxis'], UpAxis=self.AgentData['UpAxis'], ChangedGrid=self.AgentData['ChangedGrid']))

        return Message('ChildAgentPositionUpdate', args)

class DirEventsReplyPacket(object):
    ''' a template for a DirEventsReply packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}, QueryRepliesBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirEventsReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
        else:
            self.QueryData = QueryDataBlock

        if QueryRepliesBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.QueryRepliesBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.QueryReplies = {}
            self.QueryReplies['OwnerID'] = None    # MVT_LLUUID
            self.QueryReplies['Name'] = None    # MVT_VARIABLE
            self.QueryReplies['EventID'] = None    # MVT_U32
            self.QueryReplies['Date'] = None    # MVT_VARIABLE
            self.QueryReplies['UnixTime'] = None    # MVT_U32
            self.QueryReplies['EventFlags'] = None    # MVT_U32
        else:
            self.QueryRepliesBlocks = QueryRepliesBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID']))
        for block in self.QueryRepliesBlocks:
            args.append(Block('QueryReplies', OwnerID=block['OwnerID'], Name=block['Name'], EventID=block['EventID'], Date=block['Date'], UnixTime=block['UnixTime'], EventFlags=block['EventFlags']))

        return Message('DirEventsReply', args)

class GroupTitlesReplyPacket(object):
    ''' a template for a GroupTitlesReply packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupTitlesReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
            self.AgentData['RequestID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.GroupDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.GroupData = {}
            self.GroupData['Title'] = None    # MVT_VARIABLE
            self.GroupData['RoleID'] = None    # MVT_LLUUID
            self.GroupData['Selected'] = None    # MVT_BOOL
        else:
            self.GroupDataBlocks = GroupDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], GroupID=self.AgentData['GroupID'], RequestID=self.AgentData['RequestID']))
        for block in self.GroupDataBlocks:
            args.append(Block('GroupData', Title=block['Title'], RoleID=block['RoleID'], Selected=block['Selected']))

        return Message('GroupTitlesReply', args)

class RegionPresenceRequestByHandlePacket(object):
    ''' a template for a RegionPresenceRequestByHandle packet '''

    def __init__(self, RegionDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RegionPresenceRequestByHandle'

        if RegionDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.RegionDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.RegionData = {}
            self.RegionData['RegionHandle'] = None    # MVT_U64
        else:
            self.RegionDataBlocks = RegionDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.RegionDataBlocks:
            args.append(Block('RegionData', RegionHandle=block['RegionHandle']))

        return Message('RegionPresenceRequestByHandle', args)

class GroupAccountSummaryReplyPacket(object):
    ''' a template for a GroupAccountSummaryReply packet '''

    def __init__(self, AgentDataBlock = {}, MoneyDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupAccountSummaryReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MoneyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.MoneyData = MoneyDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('MoneyData', RequestID=self.MoneyData['RequestID'], IntervalDays=self.MoneyData['IntervalDays'], CurrentInterval=self.MoneyData['CurrentInterval'], StartDate=self.MoneyData['StartDate'], Balance=self.MoneyData['Balance'], TotalCredits=self.MoneyData['TotalCredits'], TotalDebits=self.MoneyData['TotalDebits'], ObjectTaxCurrent=self.MoneyData['ObjectTaxCurrent'], LightTaxCurrent=self.MoneyData['LightTaxCurrent'], LandTaxCurrent=self.MoneyData['LandTaxCurrent'], GroupTaxCurrent=self.MoneyData['GroupTaxCurrent'], ParcelDirFeeCurrent=self.MoneyData['ParcelDirFeeCurrent'], ObjectTaxEstimate=self.MoneyData['ObjectTaxEstimate'], LightTaxEstimate=self.MoneyData['LightTaxEstimate'], LandTaxEstimate=self.MoneyData['LandTaxEstimate'], GroupTaxEstimate=self.MoneyData['GroupTaxEstimate'], ParcelDirFeeEstimate=self.MoneyData['ParcelDirFeeEstimate'], NonExemptMembers=self.MoneyData['NonExemptMembers'], LastTaxDate=self.MoneyData['LastTaxDate'], TaxDate=self.MoneyData['TaxDate']))

        return Message('GroupAccountSummaryReply', args)

class CheckParcelAuctionsPacket(object):
    ''' a template for a CheckParcelAuctions packet '''

    def __init__(self, RegionDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CheckParcelAuctions'

        if RegionDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.RegionDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.RegionData = {}
            self.RegionData['RegionHandle'] = None    # MVT_U64
        else:
            self.RegionDataBlocks = RegionDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.RegionDataBlocks:
            args.append(Block('RegionData', RegionHandle=block['RegionHandle']))

        return Message('CheckParcelAuctions', args)

class ObjectAttachPacket(object):
    ''' a template for a ObjectAttach packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectAttach'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['AttachmentPoint'] = None    # MVT_U8
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['Rotation'] = None    # MVT_LLQuaternion
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], AttachmentPoint=self.AgentData['AttachmentPoint']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], Rotation=block['Rotation']))

        return Message('ObjectAttach', args)

class RemoveAttachmentPacket(object):
    ''' a template for a RemoveAttachment packet '''

    def __init__(self, AgentDataBlock = {}, AttachmentBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RemoveAttachment'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if AttachmentBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AttachmentBlock = {}    # New AttachmentBlock block
            self.AttachmentBlock['AttachmentPoint'] = None    # MVT_U8
            self.AttachmentBlock['ItemID'] = None    # MVT_LLUUID
        else:
            self.AttachmentBlock = AttachmentBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('AttachmentBlock', AttachmentPoint=self.AttachmentBlock['AttachmentPoint'], ItemID=self.AttachmentBlock['ItemID']))

        return Message('RemoveAttachment', args)

class ParcelDividePacket(object):
    ''' a template for a ParcelDivide packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelDivide'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['West'] = None    # MVT_F32
            self.ParcelData['South'] = None    # MVT_F32
            self.ParcelData['East'] = None    # MVT_F32
            self.ParcelData['North'] = None    # MVT_F32
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', West=self.ParcelData['West'], South=self.ParcelData['South'], East=self.ParcelData['East'], North=self.ParcelData['North']))

        return Message('ParcelDivide', args)

class ObjectDuplicatePacket(object):
    ''' a template for a ObjectDuplicate packet '''

    def __init__(self, AgentDataBlock = {}, SharedDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectDuplicate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if SharedDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SharedData = {}    # New SharedData block
            self.SharedData['Offset'] = None    # MVT_LLVector3
            self.SharedData['DuplicateFlags'] = None    # MVT_U32
        else:
            self.SharedData = SharedDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('SharedData', Offset=self.SharedData['Offset'], DuplicateFlags=self.SharedData['DuplicateFlags']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('ObjectDuplicate', args)

class RegionIDAndHandleReplyPacket(object):
    ''' a template for a RegionIDAndHandleReply packet '''

    def __init__(self, ReplyBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RegionIDAndHandleReply'

        if ReplyBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ReplyBlock = {}    # New ReplyBlock block
            self.ReplyBlock['RegionID'] = None    # MVT_LLUUID
            self.ReplyBlock['RegionHandle'] = None    # MVT_U64
        else:
            self.ReplyBlock = ReplyBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ReplyBlock', RegionID=self.ReplyBlock['RegionID'], RegionHandle=self.ReplyBlock['RegionHandle']))

        return Message('RegionIDAndHandleReply', args)

class ScriptControlChangePacket(object):
    ''' a template for a ScriptControlChange packet '''

    def __init__(self, DataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptControlChange'

        if DataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Data = {}
            self.Data['TakeControls'] = None    # MVT_BOOL
            self.Data['Controls'] = None    # MVT_U32
            self.Data['PassToAgent'] = None    # MVT_BOOL
        else:
            self.DataBlocks = DataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.DataBlocks:
            args.append(Block('Data', TakeControls=block['TakeControls'], Controls=block['Controls'], PassToAgent=block['PassToAgent']))

        return Message('ScriptControlChange', args)

class DenyTrustedCircuitPacket(object):
    ''' a template for a DenyTrustedCircuit packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DenyTrustedCircuit'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['EndPointID'] = None    # MVT_LLUUID
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', EndPointID=self.DataBlock['EndPointID']))

        return Message('DenyTrustedCircuit', args)

class DataHomeLocationReplyPacket(object):
    ''' a template for a DataHomeLocationReply packet '''

    def __init__(self, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DataHomeLocationReply'

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['AgentID'] = None    # MVT_LLUUID
            self.Info['RegionHandle'] = None    # MVT_U64
            self.Info['Position'] = None    # MVT_LLVector3
            self.Info['LookAt'] = None    # MVT_LLVector3
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Info', AgentID=self.Info['AgentID'], RegionHandle=self.Info['RegionHandle'], Position=self.Info['Position'], LookAt=self.Info['LookAt']))

        return Message('DataHomeLocationReply', args)

class SaveAssetIntoInventoryPacket(object):
    ''' a template for a SaveAssetIntoInventory packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SaveAssetIntoInventory'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.InventoryData = {}    # New InventoryData block
            self.InventoryData['ItemID'] = None    # MVT_LLUUID
            self.InventoryData['NewAssetID'] = None    # MVT_LLUUID
        else:
            self.InventoryData = InventoryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('InventoryData', ItemID=self.InventoryData['ItemID'], NewAssetID=self.InventoryData['NewAssetID']))

        return Message('SaveAssetIntoInventory', args)

class EjectUserPacket(object):
    ''' a template for a EjectUser packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EjectUser'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['TargetID'] = None    # MVT_LLUUID
            self.Data['Flags'] = None    # MVT_U32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', TargetID=self.Data['TargetID'], Flags=self.Data['Flags']))

        return Message('EjectUser', args)

class SendXferPacketPacket(object):
    ''' a template for a SendXferPacket packet '''

    def __init__(self, XferIDBlock = {}, DataPacketBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SendXferPacket'

        if XferIDBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.XferID = {}    # New XferID block
            self.XferID['ID'] = None    # MVT_U64
            self.XferID['Packet'] = None    # MVT_U32
        else:
            self.XferID = XferIDBlock

        if DataPacketBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataPacket = {}    # New DataPacket block
            self.DataPacket['Data'] = None    # MVT_VARIABLE
        else:
            self.DataPacket = DataPacketBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('XferID', ID=self.XferID['ID'], Packet=self.XferID['Packet']))
        args.append(Block('DataPacket', Data=self.DataPacket['Data']))

        return Message('SendXferPacket', args)

class ClassifiedDeletePacket(object):
    ''' a template for a ClassifiedDelete packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ClassifiedDelete'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['ClassifiedID'] = None    # MVT_LLUUID
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', ClassifiedID=self.Data['ClassifiedID']))

        return Message('ClassifiedDelete', args)

class SimWideDeletesPacket(object):
    ''' a template for a SimWideDeletes packet '''

    def __init__(self, AgentDataBlock = {}, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SimWideDeletes'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['TargetID'] = None    # MVT_LLUUID
            self.DataBlock['Flags'] = None    # MVT_U32
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('DataBlock', TargetID=self.DataBlock['TargetID'], Flags=self.DataBlock['Flags']))

        return Message('SimWideDeletes', args)

class UnsubscribeLoadPacket(object):
    ''' a template for a UnsubscribeLoad packet '''

    def __init__(self):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UnsubscribeLoad'

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []

        return Message('UnsubscribeLoad', args)

class StartGroupProposalPacket(object):
    ''' a template for a StartGroupProposal packet '''

    def __init__(self, AgentDataBlock = {}, ProposalDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'StartGroupProposal'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ProposalDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ProposalData = {}    # New ProposalData block
            self.ProposalData['GroupID'] = None    # MVT_LLUUID
            self.ProposalData['Quorum'] = None    # MVT_S32
            self.ProposalData['Majority'] = None    # MVT_F32
            self.ProposalData['Duration'] = None    # MVT_S32
            self.ProposalData['ProposalText'] = None    # MVT_VARIABLE
        else:
            self.ProposalData = ProposalDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ProposalData', GroupID=self.ProposalData['GroupID'], Quorum=self.ProposalData['Quorum'], Majority=self.ProposalData['Majority'], Duration=self.ProposalData['Duration'], ProposalText=self.ProposalData['ProposalText']))

        return Message('StartGroupProposal', args)

class KillChildAgentsPacket(object):
    ''' a template for a KillChildAgents packet '''

    def __init__(self, IDBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'KillChildAgents'

        if IDBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.IDBlock = {}    # New IDBlock block
            self.IDBlock['AgentID'] = None    # MVT_LLUUID
        else:
            self.IDBlock = IDBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('IDBlock', AgentID=self.IDBlock['AgentID']))

        return Message('KillChildAgents', args)

class ObjectSpinUpdatePacket(object):
    ''' a template for a ObjectSpinUpdate packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectSpinUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
            self.ObjectData['Rotation'] = None    # MVT_LLQuaternion
        else:
            self.ObjectData = ObjectDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ObjectData', ObjectID=self.ObjectData['ObjectID'], Rotation=self.ObjectData['Rotation']))

        return Message('ObjectSpinUpdate', args)

class UpdateGroupInfoPacket(object):
    ''' a template for a UpdateGroupInfo packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UpdateGroupInfo'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
            self.GroupData['Charter'] = None    # MVT_VARIABLE
            self.GroupData['ShowInList'] = None    # MVT_BOOL
            self.GroupData['InsigniaID'] = None    # MVT_LLUUID
            self.GroupData['MembershipFee'] = None    # MVT_S32
            self.GroupData['OpenEnrollment'] = None    # MVT_BOOL
            self.GroupData['AllowPublish'] = None    # MVT_BOOL
            self.GroupData['MaturePublish'] = None    # MVT_BOOL
        else:
            self.GroupData = GroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID'], Charter=self.GroupData['Charter'], ShowInList=self.GroupData['ShowInList'], InsigniaID=self.GroupData['InsigniaID'], MembershipFee=self.GroupData['MembershipFee'], OpenEnrollment=self.GroupData['OpenEnrollment'], AllowPublish=self.GroupData['AllowPublish'], MaturePublish=self.GroupData['MaturePublish']))

        return Message('UpdateGroupInfo', args)

class RequestParcelTransferPacket(object):
    ''' a template for a RequestParcelTransfer packet '''

    def __init__(self, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RequestParcelTransfer'

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Data', TransactionID=self.Data['TransactionID'], TransactionTime=self.Data['TransactionTime'], SourceID=self.Data['SourceID'], DestID=self.Data['DestID'], OwnerID=self.Data['OwnerID'], Flags=self.Data['Flags'], TransactionType=self.Data['TransactionType'], Amount=self.Data['Amount'], BillableArea=self.Data['BillableArea'], ActualArea=self.Data['ActualArea'], Final=self.Data['Final']))

        return Message('RequestParcelTransfer', args)

class ObjectIncludeInSearchPacket(object):
    ''' a template for a ObjectIncludeInSearch packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectIncludeInSearch'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['IncludeInSearch'] = None    # MVT_BOOL
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], IncludeInSearch=block['IncludeInSearch']))

        return Message('ObjectIncludeInSearch', args)

class ObjectExtraParamsPacket(object):
    ''' a template for a ObjectExtraParams packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectExtraParams'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['ParamType'] = None    # MVT_U16
            self.ObjectData['ParamInUse'] = None    # MVT_BOOL
            self.ObjectData['ParamSize'] = None    # MVT_U32
            self.ObjectData['ParamData'] = None    # MVT_VARIABLE
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], ParamType=block['ParamType'], ParamInUse=block['ParamInUse'], ParamSize=block['ParamSize'], ParamData=block['ParamData']))

        return Message('ObjectExtraParams', args)

class UseCachedMuteListPacket(object):
    ''' a template for a UseCachedMuteList packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UseCachedMuteList'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))

        return Message('UseCachedMuteList', args)

class ParcelPropertiesUpdatePacket(object):
    ''' a template for a ParcelPropertiesUpdate packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelPropertiesUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', LocalID=self.ParcelData['LocalID'], Flags=self.ParcelData['Flags'], ParcelFlags=self.ParcelData['ParcelFlags'], SalePrice=self.ParcelData['SalePrice'], Name=self.ParcelData['Name'], Desc=self.ParcelData['Desc'], MusicURL=self.ParcelData['MusicURL'], MediaURL=self.ParcelData['MediaURL'], MediaID=self.ParcelData['MediaID'], MediaAutoScale=self.ParcelData['MediaAutoScale'], GroupID=self.ParcelData['GroupID'], PassPrice=self.ParcelData['PassPrice'], PassHours=self.ParcelData['PassHours'], Category=self.ParcelData['Category'], AuthBuyerID=self.ParcelData['AuthBuyerID'], SnapshotID=self.ParcelData['SnapshotID'], UserLocation=self.ParcelData['UserLocation'], UserLookAt=self.ParcelData['UserLookAt'], LandingType=self.ParcelData['LandingType']))

        return Message('ParcelPropertiesUpdate', args)

class ParcelRenamePacket(object):
    ''' a template for a ParcelRename packet '''

    def __init__(self, ParcelDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelRename'

        if ParcelDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParcelDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParcelData = {}
            self.ParcelData['ParcelID'] = None    # MVT_LLUUID
            self.ParcelData['NewName'] = None    # MVT_VARIABLE
        else:
            self.ParcelDataBlocks = ParcelDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.ParcelDataBlocks:
            args.append(Block('ParcelData', ParcelID=block['ParcelID'], NewName=block['NewName']))

        return Message('ParcelRename', args)

class UndoLandPacket(object):
    ''' a template for a UndoLand packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UndoLand'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('UndoLand', args)

class BulkUpdateInventoryPacket(object):
    ''' a template for a BulkUpdateInventory packet '''

    def __init__(self, AgentDataBlock = {}, FolderDataBlocks = [], ItemDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'BulkUpdateInventory'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if FolderDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.FolderDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.FolderData = {}
            self.FolderData['FolderID'] = None    # MVT_LLUUID
            self.FolderData['ParentID'] = None    # MVT_LLUUID
            self.FolderData['Type'] = None    # MVT_S8
            self.FolderData['Name'] = None    # MVT_VARIABLE
        else:
            self.FolderDataBlocks = FolderDataBlocks

        if ItemDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ItemDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ItemData = {}
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
        else:
            self.ItemDataBlocks = ItemDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], TransactionID=self.AgentData['TransactionID']))
        for block in self.FolderDataBlocks:
            args.append(Block('FolderData', FolderID=block['FolderID'], ParentID=block['ParentID'], Type=block['Type'], Name=block['Name']))
        for block in self.ItemDataBlocks:
            args.append(Block('ItemData', ItemID=block['ItemID'], CallbackID=block['CallbackID'], FolderID=block['FolderID'], CreatorID=block['CreatorID'], OwnerID=block['OwnerID'], GroupID=block['GroupID'], BaseMask=block['BaseMask'], OwnerMask=block['OwnerMask'], GroupMask=block['GroupMask'], EveryoneMask=block['EveryoneMask'], NextOwnerMask=block['NextOwnerMask'], GroupOwned=block['GroupOwned'], AssetID=block['AssetID'], Type=block['Type'], InvType=block['InvType'], Flags=block['Flags'], SaleType=block['SaleType'], SalePrice=block['SalePrice'], Name=block['Name'], Description=block['Description'], CreationDate=block['CreationDate'], CRC=block['CRC']))

        return Message('BulkUpdateInventory', args)

class ClearFollowCamPropertiesPacket(object):
    ''' a template for a ClearFollowCamProperties packet '''

    def __init__(self, ObjectDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ClearFollowCamProperties'

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.ObjectData = ObjectDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ObjectData', ObjectID=self.ObjectData['ObjectID']))

        return Message('ClearFollowCamProperties', args)

class ImageDataPacket(object):
    ''' a template for a ImageData packet '''

    def __init__(self, ImageIDBlock = {}, ImageDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ImageData'

        if ImageIDBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ImageID = {}    # New ImageID block
            self.ImageID['ID'] = None    # MVT_LLUUID
            self.ImageID['Codec'] = None    # MVT_U8
            self.ImageID['Size'] = None    # MVT_U32
            self.ImageID['Packets'] = None    # MVT_U16
        else:
            self.ImageID = ImageIDBlock

        if ImageDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ImageData = {}    # New ImageData block
            self.ImageData['Data'] = None    # MVT_VARIABLE
        else:
            self.ImageData = ImageDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ImageID', ID=self.ImageID['ID'], Codec=self.ImageID['Codec'], Size=self.ImageID['Size'], Packets=self.ImageID['Packets']))
        args.append(Block('ImageData', Data=self.ImageData['Data']))

        return Message('ImageData', args)

class ParcelInfoReplyPacket(object):
    ''' a template for a ParcelInfoReply packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelInfoReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('Data', ParcelID=self.Data['ParcelID'], OwnerID=self.Data['OwnerID'], Name=self.Data['Name'], Desc=self.Data['Desc'], ActualArea=self.Data['ActualArea'], BillableArea=self.Data['BillableArea'], Flags=self.Data['Flags'], GlobalX=self.Data['GlobalX'], GlobalY=self.Data['GlobalY'], GlobalZ=self.Data['GlobalZ'], SimName=self.Data['SimName'], SnapshotID=self.Data['SnapshotID'], Dwell=self.Data['Dwell'], SalePrice=self.Data['SalePrice'], AuctionID=self.Data['AuctionID']))

        return Message('ParcelInfoReply', args)

class GodlikeMessagePacket(object):
    ''' a template for a GodlikeMessage packet '''

    def __init__(self, AgentDataBlock = {}, MethodDataBlock = {}, ParamListBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GodlikeMessage'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MethodDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MethodData = {}    # New MethodData block
            self.MethodData['Method'] = None    # MVT_VARIABLE
            self.MethodData['Invoice'] = None    # MVT_LLUUID
        else:
            self.MethodData = MethodDataBlock

        if ParamListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParamListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParamList = {}
            self.ParamList['Parameter'] = None    # MVT_VARIABLE
        else:
            self.ParamListBlocks = ParamListBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], TransactionID=self.AgentData['TransactionID']))
        args.append(Block('MethodData', Method=self.MethodData['Method'], Invoice=self.MethodData['Invoice']))
        for block in self.ParamListBlocks:
            args.append(Block('ParamList', Parameter=block['Parameter']))

        return Message('GodlikeMessage', args)

class HealthMessagePacket(object):
    ''' a template for a HealthMessage packet '''

    def __init__(self, HealthDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'HealthMessage'

        if HealthDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.HealthData = {}    # New HealthData block
            self.HealthData['Health'] = None    # MVT_F32
        else:
            self.HealthData = HealthDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('HealthData', Health=self.HealthData['Health']))

        return Message('HealthMessage', args)

class UpdateSimulatorPacket(object):
    ''' a template for a UpdateSimulator packet '''

    def __init__(self, SimulatorInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UpdateSimulator'

        if SimulatorInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SimulatorInfo = {}    # New SimulatorInfo block
            self.SimulatorInfo['RegionID'] = None    # MVT_LLUUID
            self.SimulatorInfo['SimName'] = None    # MVT_VARIABLE
            self.SimulatorInfo['EstateID'] = None    # MVT_U32
            self.SimulatorInfo['SimAccess'] = None    # MVT_U8
        else:
            self.SimulatorInfo = SimulatorInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('SimulatorInfo', RegionID=self.SimulatorInfo['RegionID'], SimName=self.SimulatorInfo['SimName'], EstateID=self.SimulatorInfo['EstateID'], SimAccess=self.SimulatorInfo['SimAccess']))

        return Message('UpdateSimulator', args)

class CloseCircuitPacket(object):
    ''' a template for a CloseCircuit packet '''

    def __init__(self):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CloseCircuit'

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []

        return Message('CloseCircuit', args)

class GroupRoleDataReplyPacket(object):
    ''' a template for a GroupRoleDataReply packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}, RoleDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupRoleDataReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
            self.GroupData['RequestID'] = None    # MVT_LLUUID
            self.GroupData['RoleCount'] = None    # MVT_S32
        else:
            self.GroupData = GroupDataBlock

        if RoleDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.RoleDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.RoleData = {}
            self.RoleData['RoleID'] = None    # MVT_LLUUID
            self.RoleData['Name'] = None    # MVT_VARIABLE
            self.RoleData['Title'] = None    # MVT_VARIABLE
            self.RoleData['Description'] = None    # MVT_VARIABLE
            self.RoleData['Powers'] = None    # MVT_U64
            self.RoleData['Members'] = None    # MVT_U32
        else:
            self.RoleDataBlocks = RoleDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID'], RequestID=self.GroupData['RequestID'], RoleCount=self.GroupData['RoleCount']))
        for block in self.RoleDataBlocks:
            args.append(Block('RoleData', RoleID=block['RoleID'], Name=block['Name'], Title=block['Title'], Description=block['Description'], Powers=block['Powers'], Members=block['Members']))

        return Message('GroupRoleDataReply', args)

class DataServerLogoutPacket(object):
    ''' a template for a DataServerLogout packet '''

    def __init__(self, UserDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DataServerLogout'

        if UserDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.UserData = {}    # New UserData block
            self.UserData['AgentID'] = None    # MVT_LLUUID
            self.UserData['ViewerIP'] = None    # MVT_IP_ADDR
            self.UserData['Disconnect'] = None    # MVT_BOOL
            self.UserData['SessionID'] = None    # MVT_LLUUID
        else:
            self.UserData = UserDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('UserData', AgentID=self.UserData['AgentID'], ViewerIP=self.UserData['ViewerIP'], Disconnect=self.UserData['Disconnect'], SessionID=self.UserData['SessionID']))

        return Message('DataServerLogout', args)

class InviteGroupResponsePacket(object):
    ''' a template for a InviteGroupResponse packet '''

    def __init__(self, InviteDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'InviteGroupResponse'

        if InviteDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.InviteData = {}    # New InviteData block
            self.InviteData['AgentID'] = None    # MVT_LLUUID
            self.InviteData['InviteeID'] = None    # MVT_LLUUID
            self.InviteData['GroupID'] = None    # MVT_LLUUID
            self.InviteData['RoleID'] = None    # MVT_LLUUID
            self.InviteData['MembershipFee'] = None    # MVT_S32
        else:
            self.InviteData = InviteDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('InviteData', AgentID=self.InviteData['AgentID'], InviteeID=self.InviteData['InviteeID'], GroupID=self.InviteData['GroupID'], RoleID=self.InviteData['RoleID'], MembershipFee=self.InviteData['MembershipFee']))

        return Message('InviteGroupResponse', args)

class StartAuctionPacket(object):
    ''' a template for a StartAuction packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'StartAuction'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['ParcelID'] = None    # MVT_LLUUID
            self.ParcelData['SnapshotID'] = None    # MVT_LLUUID
            self.ParcelData['Name'] = None    # MVT_VARIABLE
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('ParcelData', ParcelID=self.ParcelData['ParcelID'], SnapshotID=self.ParcelData['SnapshotID'], Name=self.ParcelData['Name']))

        return Message('StartAuction', args)

class ObjectDescriptionPacket(object):
    ''' a template for a ObjectDescription packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectDescription'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['LocalID'] = None    # MVT_U32
            self.ObjectData['Description'] = None    # MVT_VARIABLE
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', LocalID=block['LocalID'], Description=block['Description']))

        return Message('ObjectDescription', args)

class ObjectPositionPacket(object):
    ''' a template for a ObjectPosition packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectPosition'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['Position'] = None    # MVT_LLVector3
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], Position=block['Position']))

        return Message('ObjectPosition', args)

class MoneyTransferBackendPacket(object):
    ''' a template for a MoneyTransferBackend packet '''

    def __init__(self, MoneyDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MoneyTransferBackend'

        if MoneyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.MoneyData = MoneyDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('MoneyData', TransactionID=self.MoneyData['TransactionID'], TransactionTime=self.MoneyData['TransactionTime'], SourceID=self.MoneyData['SourceID'], DestID=self.MoneyData['DestID'], Flags=self.MoneyData['Flags'], Amount=self.MoneyData['Amount'], AggregatePermNextOwner=self.MoneyData['AggregatePermNextOwner'], AggregatePermInventory=self.MoneyData['AggregatePermInventory'], TransactionType=self.MoneyData['TransactionType'], RegionID=self.MoneyData['RegionID'], GridX=self.MoneyData['GridX'], GridY=self.MoneyData['GridY'], Description=self.MoneyData['Description']))

        return Message('MoneyTransferBackend', args)

class ParcelDeedToGroupPacket(object):
    ''' a template for a ParcelDeedToGroup packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelDeedToGroup'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['GroupID'] = None    # MVT_LLUUID
            self.Data['LocalID'] = None    # MVT_S32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', GroupID=self.Data['GroupID'], LocalID=self.Data['LocalID']))

        return Message('ParcelDeedToGroup', args)

class MapItemReplyPacket(object):
    ''' a template for a MapItemReply packet '''

    def __init__(self, AgentDataBlock = {}, RequestDataBlock = {}, DataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MapItemReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['Flags'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

        if RequestDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RequestData = {}    # New RequestData block
            self.RequestData['ItemType'] = None    # MVT_U32
        else:
            self.RequestData = RequestDataBlock

        if DataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Data = {}
            self.Data['X'] = None    # MVT_U32
            self.Data['Y'] = None    # MVT_U32
            self.Data['ID'] = None    # MVT_LLUUID
            self.Data['Extra'] = None    # MVT_S32
            self.Data['Extra2'] = None    # MVT_S32
            self.Data['Name'] = None    # MVT_VARIABLE
        else:
            self.DataBlocks = DataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], Flags=self.AgentData['Flags']))
        args.append(Block('RequestData', ItemType=self.RequestData['ItemType']))
        for block in self.DataBlocks:
            args.append(Block('Data', X=block['X'], Y=block['Y'], ID=block['ID'], Extra=block['Extra'], Extra2=block['Extra2'], Name=block['Name']))

        return Message('MapItemReply', args)

class ImageNotInDatabasePacket(object):
    ''' a template for a ImageNotInDatabase packet '''

    def __init__(self, ImageIDBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ImageNotInDatabase'

        if ImageIDBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ImageID = {}    # New ImageID block
            self.ImageID['ID'] = None    # MVT_LLUUID
        else:
            self.ImageID = ImageIDBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ImageID', ID=self.ImageID['ID']))

        return Message('ImageNotInDatabase', args)

class ReplyTaskInventoryPacket(object):
    ''' a template for a ReplyTaskInventory packet '''

    def __init__(self, InventoryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ReplyTaskInventory'

        if InventoryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.InventoryData = {}    # New InventoryData block
            self.InventoryData['TaskID'] = None    # MVT_LLUUID
            self.InventoryData['Serial'] = None    # MVT_S16
            self.InventoryData['Filename'] = None    # MVT_VARIABLE
        else:
            self.InventoryData = InventoryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('InventoryData', TaskID=self.InventoryData['TaskID'], Serial=self.InventoryData['Serial'], Filename=self.InventoryData['Filename']))

        return Message('ReplyTaskInventory', args)

class AvatarPropertiesRequestPacket(object):
    ''' a template for a AvatarPropertiesRequest packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarPropertiesRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['AvatarID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], AvatarID=self.AgentData['AvatarID']))

        return Message('AvatarPropertiesRequest', args)

class AgentGroupDataUpdatePacket(object):
    ''' a template for a AgentGroupDataUpdate packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentGroupDataUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.GroupDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.GroupData = {}
            self.GroupData['GroupID'] = None    # MVT_LLUUID
            self.GroupData['GroupPowers'] = None    # MVT_U64
            self.GroupData['AcceptNotices'] = None    # MVT_BOOL
            self.GroupData['GroupInsigniaID'] = None    # MVT_LLUUID
            self.GroupData['Contribution'] = None    # MVT_S32
            self.GroupData['GroupName'] = None    # MVT_VARIABLE
        else:
            self.GroupDataBlocks = GroupDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        for block in self.GroupDataBlocks:
            args.append(Block('GroupData', GroupID=block['GroupID'], GroupPowers=block['GroupPowers'], AcceptNotices=block['AcceptNotices'], GroupInsigniaID=block['GroupInsigniaID'], Contribution=block['Contribution'], GroupName=block['GroupName']))

        return Message('AgentGroupDataUpdate', args)

class DirLandQueryPacket(object):
    ''' a template for a DirLandQuery packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirLandQuery'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['QueryFlags'] = None    # MVT_U32
            self.QueryData['SearchType'] = None    # MVT_U32
            self.QueryData['Price'] = None    # MVT_S32
            self.QueryData['Area'] = None    # MVT_S32
            self.QueryData['QueryStart'] = None    # MVT_S32
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], QueryFlags=self.QueryData['QueryFlags'], SearchType=self.QueryData['SearchType'], Price=self.QueryData['Price'], Area=self.QueryData['Area'], QueryStart=self.QueryData['QueryStart']))

        return Message('DirLandQuery', args)

class MoveInventoryItemPacket(object):
    ''' a template for a MoveInventoryItem packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MoveInventoryItem'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['Stamp'] = None    # MVT_BOOL
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
            self.InventoryData['ItemID'] = None    # MVT_LLUUID
            self.InventoryData['FolderID'] = None    # MVT_LLUUID
            self.InventoryData['NewName'] = None    # MVT_VARIABLE
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], Stamp=self.AgentData['Stamp']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', ItemID=block['ItemID'], FolderID=block['FolderID'], NewName=block['NewName']))

        return Message('MoveInventoryItem', args)

class TeleportLandingStatusChangedPacket(object):
    ''' a template for a TeleportLandingStatusChanged packet '''

    def __init__(self, RegionDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TeleportLandingStatusChanged'

        if RegionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionData = {}    # New RegionData block
            self.RegionData['RegionHandle'] = None    # MVT_U64
        else:
            self.RegionData = RegionDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('RegionData', RegionHandle=self.RegionData['RegionHandle']))

        return Message('TeleportLandingStatusChanged', args)

class AvatarPickerRequestPacket(object):
    ''' a template for a AvatarPickerRequest packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarPickerRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['QueryID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['Name'] = None    # MVT_VARIABLE
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], QueryID=self.AgentData['QueryID']))
        args.append(Block('Data', Name=self.Data['Name']))

        return Message('AvatarPickerRequest', args)

class AgentWearablesRequestPacket(object):
    ''' a template for a AgentWearablesRequest packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentWearablesRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('AgentWearablesRequest', args)

class AvatarTextureUpdatePacket(object):
    ''' a template for a AvatarTextureUpdate packet '''

    def __init__(self, AgentDataBlock = {}, WearableDataBlocks = [], TextureDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarTextureUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['TexturesChanged'] = None    # MVT_BOOL
        else:
            self.AgentData = AgentDataBlock

        if WearableDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.WearableDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.WearableData = {}
            self.WearableData['CacheID'] = None    # MVT_LLUUID
            self.WearableData['TextureIndex'] = None    # MVT_U8
            self.WearableData['HostName'] = None    # MVT_VARIABLE
        else:
            self.WearableDataBlocks = WearableDataBlocks

        if TextureDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.TextureDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.TextureData = {}
            self.TextureData['TextureID'] = None    # MVT_LLUUID
        else:
            self.TextureDataBlocks = TextureDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], TexturesChanged=self.AgentData['TexturesChanged']))
        for block in self.WearableDataBlocks:
            args.append(Block('WearableData', CacheID=block['CacheID'], TextureIndex=block['TextureIndex'], HostName=block['HostName']))
        for block in self.TextureDataBlocks:
            args.append(Block('TextureData', TextureID=block['TextureID']))

        return Message('AvatarTextureUpdate', args)

class GroupActiveProposalsRequestPacket(object):
    ''' a template for a GroupActiveProposalsRequest packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}, TransactionDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupActiveProposalsRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
        else:
            self.GroupData = GroupDataBlock

        if TransactionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransactionData = {}    # New TransactionData block
            self.TransactionData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.TransactionData = TransactionDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID']))
        args.append(Block('TransactionData', TransactionID=self.TransactionData['TransactionID']))

        return Message('GroupActiveProposalsRequest', args)

class UUIDGroupNameReplyPacket(object):
    ''' a template for a UUIDGroupNameReply packet '''

    def __init__(self, UUIDNameBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UUIDGroupNameReply'

        if UUIDNameBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.UUIDNameBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.UUIDNameBlock = {}
            self.UUIDNameBlock['ID'] = None    # MVT_LLUUID
            self.UUIDNameBlock['GroupName'] = None    # MVT_VARIABLE
        else:
            self.UUIDNameBlockBlocks = UUIDNameBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.UUIDNameBlockBlocks:
            args.append(Block('UUIDNameBlock', ID=block['ID'], GroupName=block['GroupName']))

        return Message('UUIDGroupNameReply', args)

class ObjectGrabPacket(object):
    ''' a template for a ObjectGrab packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlock = {}, SurfaceInfoBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectGrab'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['LocalID'] = None    # MVT_U32
            self.ObjectData['GrabOffset'] = None    # MVT_LLVector3
        else:
            self.ObjectData = ObjectDataBlock

        if SurfaceInfoBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.SurfaceInfoBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.SurfaceInfo = {}
            self.SurfaceInfo['UVCoord'] = None    # MVT_LLVector3
            self.SurfaceInfo['STCoord'] = None    # MVT_LLVector3
        else:
            self.SurfaceInfoBlocks = SurfaceInfoBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ObjectData', LocalID=self.ObjectData['LocalID'], GrabOffset=self.ObjectData['GrabOffset']))
        for block in self.SurfaceInfoBlocks:
            args.append(Block('SurfaceInfo', UVCoord=block['UVCoord'], STCoord=block['STCoord']))

        return Message('ObjectGrab', args)

class AttachedSoundPacket(object):
    ''' a template for a AttachedSound packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AttachedSound'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['SoundID'] = None    # MVT_LLUUID
            self.DataBlock['ObjectID'] = None    # MVT_LLUUID
            self.DataBlock['OwnerID'] = None    # MVT_LLUUID
            self.DataBlock['Gain'] = None    # MVT_F32
            self.DataBlock['Flags'] = None    # MVT_U8
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', SoundID=self.DataBlock['SoundID'], ObjectID=self.DataBlock['ObjectID'], OwnerID=self.DataBlock['OwnerID'], Gain=self.DataBlock['Gain'], Flags=self.DataBlock['Flags']))

        return Message('AttachedSound', args)

class ChangeUserRightsPacket(object):
    ''' a template for a ChangeUserRights packet '''

    def __init__(self, AgentDataBlock = {}, RightsBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ChangeUserRights'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RightsBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.RightsBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Rights = {}
            self.Rights['AgentRelated'] = None    # MVT_LLUUID
            self.Rights['RelatedRights'] = None    # MVT_S32
        else:
            self.RightsBlocks = RightsBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        for block in self.RightsBlocks:
            args.append(Block('Rights', AgentRelated=block['AgentRelated'], RelatedRights=block['RelatedRights']))

        return Message('ChangeUserRights', args)

class ParcelSetOtherCleanTimePacket(object):
    ''' a template for a ParcelSetOtherCleanTime packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelSetOtherCleanTime'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['LocalID'] = None    # MVT_S32
            self.ParcelData['OtherCleanTime'] = None    # MVT_S32
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', LocalID=self.ParcelData['LocalID'], OtherCleanTime=self.ParcelData['OtherCleanTime']))

        return Message('ParcelSetOtherCleanTime', args)

class ParcelMediaUpdatePacket(object):
    ''' a template for a ParcelMediaUpdate packet '''

    def __init__(self, DataBlockBlock = {}, DataBlockExtendedBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelMediaUpdate'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['MediaURL'] = None    # MVT_VARIABLE
            self.DataBlock['MediaID'] = None    # MVT_LLUUID
            self.DataBlock['MediaAutoScale'] = None    # MVT_U8
        else:
            self.DataBlock = DataBlockBlock

        if DataBlockExtendedBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlockExtended = {}    # New DataBlockExtended block
            self.DataBlockExtended['MediaType'] = None    # MVT_VARIABLE
            self.DataBlockExtended['MediaDesc'] = None    # MVT_VARIABLE
            self.DataBlockExtended['MediaWidth'] = None    # MVT_S32
            self.DataBlockExtended['MediaHeight'] = None    # MVT_S32
            self.DataBlockExtended['MediaLoop'] = None    # MVT_U8
        else:
            self.DataBlockExtended = DataBlockExtendedBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', MediaURL=self.DataBlock['MediaURL'], MediaID=self.DataBlock['MediaID'], MediaAutoScale=self.DataBlock['MediaAutoScale']))
        args.append(Block('DataBlockExtended', MediaType=self.DataBlockExtended['MediaType'], MediaDesc=self.DataBlockExtended['MediaDesc'], MediaWidth=self.DataBlockExtended['MediaWidth'], MediaHeight=self.DataBlockExtended['MediaHeight'], MediaLoop=self.DataBlockExtended['MediaLoop']))

        return Message('ParcelMediaUpdate', args)

class ObjectClickActionPacket(object):
    ''' a template for a ObjectClickAction packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectClickAction'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['ClickAction'] = None    # MVT_U8
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], ClickAction=block['ClickAction']))

        return Message('ObjectClickAction', args)

class FormFriendshipPacket(object):
    ''' a template for a FormFriendship packet '''

    def __init__(self, AgentBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'FormFriendship'

        if AgentBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentBlock = {}    # New AgentBlock block
            self.AgentBlock['SourceID'] = None    # MVT_LLUUID
            self.AgentBlock['DestID'] = None    # MVT_LLUUID
        else:
            self.AgentBlock = AgentBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentBlock', SourceID=self.AgentBlock['SourceID'], DestID=self.AgentBlock['DestID']))

        return Message('FormFriendship', args)

class AvatarPicksReplyPacket(object):
    ''' a template for a AvatarPicksReply packet '''

    def __init__(self, AgentDataBlock = {}, DataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarPicksReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['TargetID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Data = {}
            self.Data['PickID'] = None    # MVT_LLUUID
            self.Data['PickName'] = None    # MVT_VARIABLE
        else:
            self.DataBlocks = DataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], TargetID=self.AgentData['TargetID']))
        for block in self.DataBlocks:
            args.append(Block('Data', PickID=block['PickID'], PickName=block['PickName']))

        return Message('AvatarPicksReply', args)

class AgentSitPacket(object):
    ''' a template for a AgentSit packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentSit'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('AgentSit', args)

class CreateNewOutfitAttachmentsPacket(object):
    ''' a template for a CreateNewOutfitAttachments packet '''

    def __init__(self, AgentDataBlock = {}, HeaderDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CreateNewOutfitAttachments'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if HeaderDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.HeaderData = {}    # New HeaderData block
            self.HeaderData['NewFolderID'] = None    # MVT_LLUUID
        else:
            self.HeaderData = HeaderDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['OldItemID'] = None    # MVT_LLUUID
            self.ObjectData['OldFolderID'] = None    # MVT_LLUUID
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('HeaderData', NewFolderID=self.HeaderData['NewFolderID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', OldItemID=block['OldItemID'], OldFolderID=block['OldFolderID']))

        return Message('CreateNewOutfitAttachments', args)

class ParcelObjectOwnersReplyPacket(object):
    ''' a template for a ParcelObjectOwnersReply packet '''

    def __init__(self, DataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelObjectOwnersReply'

        if DataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Data = {}
            self.Data['OwnerID'] = None    # MVT_LLUUID
            self.Data['IsGroupOwned'] = None    # MVT_BOOL
            self.Data['Count'] = None    # MVT_S32
            self.Data['OnlineStatus'] = None    # MVT_BOOL
        else:
            self.DataBlocks = DataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.DataBlocks:
            args.append(Block('Data', OwnerID=block['OwnerID'], IsGroupOwned=block['IsGroupOwned'], Count=block['Count'], OnlineStatus=block['OnlineStatus']))

        return Message('ParcelObjectOwnersReply', args)

class FetchInventoryDescendentsPacket(object):
    ''' a template for a FetchInventoryDescendents packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'FetchInventoryDescendents'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.InventoryData = {}    # New InventoryData block
            self.InventoryData['FolderID'] = None    # MVT_LLUUID
            self.InventoryData['OwnerID'] = None    # MVT_LLUUID
            self.InventoryData['SortOrder'] = None    # MVT_S32
            self.InventoryData['FetchFolders'] = None    # MVT_BOOL
            self.InventoryData['FetchItems'] = None    # MVT_BOOL
        else:
            self.InventoryData = InventoryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('InventoryData', FolderID=self.InventoryData['FolderID'], OwnerID=self.InventoryData['OwnerID'], SortOrder=self.InventoryData['SortOrder'], FetchFolders=self.InventoryData['FetchFolders'], FetchItems=self.InventoryData['FetchItems']))

        return Message('FetchInventoryDescendents', args)

class RequestXferPacket(object):
    ''' a template for a RequestXfer packet '''

    def __init__(self, XferIDBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RequestXfer'

        if XferIDBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.XferID = {}    # New XferID block
            self.XferID['ID'] = None    # MVT_U64
            self.XferID['Filename'] = None    # MVT_VARIABLE
            self.XferID['FilePath'] = None    # MVT_U8
            self.XferID['DeleteOnCompletion'] = None    # MVT_BOOL
            self.XferID['UseBigPackets'] = None    # MVT_BOOL
            self.XferID['VFileID'] = None    # MVT_LLUUID
            self.XferID['VFileType'] = None    # MVT_S16
        else:
            self.XferID = XferIDBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('XferID', ID=self.XferID['ID'], Filename=self.XferID['Filename'], FilePath=self.XferID['FilePath'], DeleteOnCompletion=self.XferID['DeleteOnCompletion'], UseBigPackets=self.XferID['UseBigPackets'], VFileID=self.XferID['VFileID'], VFileType=self.XferID['VFileType']))

        return Message('RequestXfer', args)

class SoundTriggerPacket(object):
    ''' a template for a SoundTrigger packet '''

    def __init__(self, SoundDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SoundTrigger'

        if SoundDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SoundData = {}    # New SoundData block
            self.SoundData['SoundID'] = None    # MVT_LLUUID
            self.SoundData['OwnerID'] = None    # MVT_LLUUID
            self.SoundData['ObjectID'] = None    # MVT_LLUUID
            self.SoundData['ParentID'] = None    # MVT_LLUUID
            self.SoundData['Handle'] = None    # MVT_U64
            self.SoundData['Position'] = None    # MVT_LLVector3
            self.SoundData['Gain'] = None    # MVT_F32
        else:
            self.SoundData = SoundDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('SoundData', SoundID=self.SoundData['SoundID'], OwnerID=self.SoundData['OwnerID'], ObjectID=self.SoundData['ObjectID'], ParentID=self.SoundData['ParentID'], Handle=self.SoundData['Handle'], Position=self.SoundData['Position'], Gain=self.SoundData['Gain']))

        return Message('SoundTrigger', args)

class DirPlacesReplyPacket(object):
    ''' a template for a DirPlacesReply packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlocks = [], QueryRepliesBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirPlacesReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.QueryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.QueryData = {}
            self.QueryData['QueryID'] = None    # MVT_LLUUID
        else:
            self.QueryDataBlocks = QueryDataBlocks

        if QueryRepliesBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.QueryRepliesBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.QueryReplies = {}
            self.QueryReplies['ParcelID'] = None    # MVT_LLUUID
            self.QueryReplies['Name'] = None    # MVT_VARIABLE
            self.QueryReplies['ForSale'] = None    # MVT_BOOL
            self.QueryReplies['Auction'] = None    # MVT_BOOL
            self.QueryReplies['Dwell'] = None    # MVT_F32
        else:
            self.QueryRepliesBlocks = QueryRepliesBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        for block in self.QueryDataBlocks:
            args.append(Block('QueryData', QueryID=block['QueryID']))
        for block in self.QueryRepliesBlocks:
            args.append(Block('QueryReplies', ParcelID=block['ParcelID'], Name=block['Name'], ForSale=block['ForSale'], Auction=block['Auction'], Dwell=block['Dwell']))

        return Message('DirPlacesReply', args)

class AlertMessagePacket(object):
    ''' a template for a AlertMessage packet '''

    def __init__(self, AlertDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AlertMessage'

        if AlertDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AlertData = {}    # New AlertData block
            self.AlertData['Message'] = None    # MVT_VARIABLE
        else:
            self.AlertData = AlertDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AlertData', Message=self.AlertData['Message']))

        return Message('AlertMessage', args)

class SimulatorShutdownRequestPacket(object):
    ''' a template for a SimulatorShutdownRequest packet '''

    def __init__(self):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SimulatorShutdownRequest'

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []

        return Message('SimulatorShutdownRequest', args)

class GroupProfileReplyPacket(object):
    ''' a template for a GroupProfileReply packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupProfileReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.GroupData = GroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID'], Name=self.GroupData['Name'], Charter=self.GroupData['Charter'], ShowInList=self.GroupData['ShowInList'], MemberTitle=self.GroupData['MemberTitle'], PowersMask=self.GroupData['PowersMask'], InsigniaID=self.GroupData['InsigniaID'], FounderID=self.GroupData['FounderID'], MembershipFee=self.GroupData['MembershipFee'], OpenEnrollment=self.GroupData['OpenEnrollment'], Money=self.GroupData['Money'], GroupMembershipCount=self.GroupData['GroupMembershipCount'], GroupRolesCount=self.GroupData['GroupRolesCount'], AllowPublish=self.GroupData['AllowPublish'], MaturePublish=self.GroupData['MaturePublish'], OwnerRole=self.GroupData['OwnerRole']))

        return Message('GroupProfileReply', args)

class ScriptSensorRequestPacket(object):
    ''' a template for a ScriptSensorRequest packet '''

    def __init__(self, RequesterBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptSensorRequest'

        if RequesterBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.Requester = RequesterBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Requester', SourceID=self.Requester['SourceID'], RequestID=self.Requester['RequestID'], SearchID=self.Requester['SearchID'], SearchPos=self.Requester['SearchPos'], SearchDir=self.Requester['SearchDir'], SearchName=self.Requester['SearchName'], Type=self.Requester['Type'], Range=self.Requester['Range'], Arc=self.Requester['Arc'], RegionHandle=self.Requester['RegionHandle'], SearchRegions=self.Requester['SearchRegions']))

        return Message('ScriptSensorRequest', args)

class VelocityInterpolateOffPacket(object):
    ''' a template for a VelocityInterpolateOff packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'VelocityInterpolateOff'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('VelocityInterpolateOff', args)

class RemoveNameValuePairPacket(object):
    ''' a template for a RemoveNameValuePair packet '''

    def __init__(self, TaskDataBlock = {}, NameValueDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RemoveNameValuePair'

        if TaskDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TaskData = {}    # New TaskData block
            self.TaskData['ID'] = None    # MVT_LLUUID
        else:
            self.TaskData = TaskDataBlock

        if NameValueDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.NameValueDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.NameValueData = {}
            self.NameValueData['NVPair'] = None    # MVT_VARIABLE
        else:
            self.NameValueDataBlocks = NameValueDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TaskData', ID=self.TaskData['ID']))
        for block in self.NameValueDataBlocks:
            args.append(Block('NameValueData', NVPair=block['NVPair']))

        return Message('RemoveNameValuePair', args)

class ParcelClaimPacket(object):
    ''' a template for a ParcelClaim packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}, ParcelDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelClaim'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['GroupID'] = None    # MVT_LLUUID
            self.Data['IsGroupOwned'] = None    # MVT_BOOL
            self.Data['Final'] = None    # MVT_BOOL
        else:
            self.Data = DataBlock

        if ParcelDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParcelDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParcelData = {}
            self.ParcelData['West'] = None    # MVT_F32
            self.ParcelData['South'] = None    # MVT_F32
            self.ParcelData['East'] = None    # MVT_F32
            self.ParcelData['North'] = None    # MVT_F32
        else:
            self.ParcelDataBlocks = ParcelDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', GroupID=self.Data['GroupID'], IsGroupOwned=self.Data['IsGroupOwned'], Final=self.Data['Final']))
        for block in self.ParcelDataBlocks:
            args.append(Block('ParcelData', West=block['West'], South=block['South'], East=block['East'], North=block['North']))

        return Message('ParcelClaim', args)

class SetAlwaysRunPacket(object):
    ''' a template for a SetAlwaysRun packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SetAlwaysRun'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['AlwaysRun'] = None    # MVT_BOOL
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], AlwaysRun=self.AgentData['AlwaysRun']))

        return Message('SetAlwaysRun', args)

class EventLocationReplyPacket(object):
    ''' a template for a EventLocationReply packet '''

    def __init__(self, QueryDataBlock = {}, EventDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EventLocationReply'

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
        else:
            self.QueryData = QueryDataBlock

        if EventDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.EventData = {}    # New EventData block
            self.EventData['Success'] = None    # MVT_BOOL
            self.EventData['RegionID'] = None    # MVT_LLUUID
            self.EventData['RegionPos'] = None    # MVT_LLVector3
        else:
            self.EventData = EventDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID']))
        args.append(Block('EventData', Success=self.EventData['Success'], RegionID=self.EventData['RegionID'], RegionPos=self.EventData['RegionPos']))

        return Message('EventLocationReply', args)

class PickGodDeletePacket(object):
    ''' a template for a PickGodDelete packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'PickGodDelete'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['PickID'] = None    # MVT_LLUUID
            self.Data['QueryID'] = None    # MVT_LLUUID
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', PickID=self.Data['PickID'], QueryID=self.Data['QueryID']))

        return Message('PickGodDelete', args)

class MapBlockRequestPacket(object):
    ''' a template for a MapBlockRequest packet '''

    def __init__(self, AgentDataBlock = {}, PositionDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MapBlockRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['Flags'] = None    # MVT_U32
            self.AgentData['EstateID'] = None    # MVT_U32
            self.AgentData['Godlike'] = None    # MVT_BOOL
        else:
            self.AgentData = AgentDataBlock

        if PositionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.PositionData = {}    # New PositionData block
            self.PositionData['MinX'] = None    # MVT_U16
            self.PositionData['MaxX'] = None    # MVT_U16
            self.PositionData['MinY'] = None    # MVT_U16
            self.PositionData['MaxY'] = None    # MVT_U16
        else:
            self.PositionData = PositionDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], Flags=self.AgentData['Flags'], EstateID=self.AgentData['EstateID'], Godlike=self.AgentData['Godlike']))
        args.append(Block('PositionData', MinX=self.PositionData['MinX'], MaxX=self.PositionData['MaxX'], MinY=self.PositionData['MinY'], MaxY=self.PositionData['MaxY']))

        return Message('MapBlockRequest', args)

class TeleportProgressPacket(object):
    ''' a template for a TeleportProgress packet '''

    def __init__(self, AgentDataBlock = {}, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TeleportProgress'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['TeleportFlags'] = None    # MVT_U32
            self.Info['Message'] = None    # MVT_VARIABLE
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('Info', TeleportFlags=self.Info['TeleportFlags'], Message=self.Info['Message']))

        return Message('TeleportProgress', args)

class UpdateTaskInventoryPacket(object):
    ''' a template for a UpdateTaskInventory packet '''

    def __init__(self, AgentDataBlock = {}, UpdateDataBlock = {}, InventoryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UpdateTaskInventory'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if UpdateDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.UpdateData = {}    # New UpdateData block
            self.UpdateData['LocalID'] = None    # MVT_U32
            self.UpdateData['Key'] = None    # MVT_U8
        else:
            self.UpdateData = UpdateDataBlock

        if InventoryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.InventoryData = InventoryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('UpdateData', LocalID=self.UpdateData['LocalID'], Key=self.UpdateData['Key']))
        args.append(Block('InventoryData', ItemID=self.InventoryData['ItemID'], FolderID=self.InventoryData['FolderID'], CreatorID=self.InventoryData['CreatorID'], OwnerID=self.InventoryData['OwnerID'], GroupID=self.InventoryData['GroupID'], BaseMask=self.InventoryData['BaseMask'], OwnerMask=self.InventoryData['OwnerMask'], GroupMask=self.InventoryData['GroupMask'], EveryoneMask=self.InventoryData['EveryoneMask'], NextOwnerMask=self.InventoryData['NextOwnerMask'], GroupOwned=self.InventoryData['GroupOwned'], TransactionID=self.InventoryData['TransactionID'], Type=self.InventoryData['Type'], InvType=self.InventoryData['InvType'], Flags=self.InventoryData['Flags'], SaleType=self.InventoryData['SaleType'], SalePrice=self.InventoryData['SalePrice'], Name=self.InventoryData['Name'], Description=self.InventoryData['Description'], CreationDate=self.InventoryData['CreationDate'], CRC=self.InventoryData['CRC']))

        return Message('UpdateTaskInventory', args)

class GodKickUserPacket(object):
    ''' a template for a GodKickUser packet '''

    def __init__(self, UserInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GodKickUser'

        if UserInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.UserInfo = {}    # New UserInfo block
            self.UserInfo['GodID'] = None    # MVT_LLUUID
            self.UserInfo['GodSessionID'] = None    # MVT_LLUUID
            self.UserInfo['AgentID'] = None    # MVT_LLUUID
            self.UserInfo['KickFlags'] = None    # MVT_U32
            self.UserInfo['Reason'] = None    # MVT_VARIABLE
        else:
            self.UserInfo = UserInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('UserInfo', GodID=self.UserInfo['GodID'], GodSessionID=self.UserInfo['GodSessionID'], AgentID=self.UserInfo['AgentID'], KickFlags=self.UserInfo['KickFlags'], Reason=self.UserInfo['Reason']))

        return Message('GodKickUser', args)

class AvatarAnimationPacket(object):
    ''' a template for a AvatarAnimation packet '''

    def __init__(self, SenderBlock = {}, AnimationListBlocks = [], AnimationSourceListBlocks = [], PhysicalAvatarEventListBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarAnimation'

        if SenderBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Sender = {}    # New Sender block
            self.Sender['ID'] = None    # MVT_LLUUID
        else:
            self.Sender = SenderBlock

        if AnimationListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.AnimationListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.AnimationList = {}
            self.AnimationList['AnimID'] = None    # MVT_LLUUID
            self.AnimationList['AnimSequenceID'] = None    # MVT_S32
        else:
            self.AnimationListBlocks = AnimationListBlocks

        if AnimationSourceListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.AnimationSourceListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.AnimationSourceList = {}
            self.AnimationSourceList['ObjectID'] = None    # MVT_LLUUID
        else:
            self.AnimationSourceListBlocks = AnimationSourceListBlocks

        if PhysicalAvatarEventListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.PhysicalAvatarEventListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.PhysicalAvatarEventList = {}
            self.PhysicalAvatarEventList['TypeData'] = None    # MVT_VARIABLE
        else:
            self.PhysicalAvatarEventListBlocks = PhysicalAvatarEventListBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Sender', ID=self.Sender['ID']))
        for block in self.AnimationListBlocks:
            args.append(Block('AnimationList', AnimID=block['AnimID'], AnimSequenceID=block['AnimSequenceID']))
        for block in self.AnimationSourceListBlocks:
            args.append(Block('AnimationSourceList', ObjectID=block['ObjectID']))
        for block in self.PhysicalAvatarEventListBlocks:
            args.append(Block('PhysicalAvatarEventList', TypeData=block['TypeData']))

        return Message('AvatarAnimation', args)

class ClassifiedInfoReplyPacket(object):
    ''' a template for a ClassifiedInfoReply packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ClassifiedInfoReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('Data', ClassifiedID=self.Data['ClassifiedID'], CreatorID=self.Data['CreatorID'], CreationDate=self.Data['CreationDate'], ExpirationDate=self.Data['ExpirationDate'], Category=self.Data['Category'], Name=self.Data['Name'], Desc=self.Data['Desc'], ParcelID=self.Data['ParcelID'], ParentEstate=self.Data['ParentEstate'], SnapshotID=self.Data['SnapshotID'], SimName=self.Data['SimName'], PosGlobal=self.Data['PosGlobal'], ParcelName=self.Data['ParcelName'], ClassifiedFlags=self.Data['ClassifiedFlags'], PriceForListing=self.Data['PriceForListing']))

        return Message('ClassifiedInfoReply', args)

class GodUpdateRegionInfoPacket(object):
    ''' a template for a GodUpdateRegionInfo packet '''

    def __init__(self, AgentDataBlock = {}, RegionInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GodUpdateRegionInfo'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RegionInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionInfo = {}    # New RegionInfo block
            self.RegionInfo['SimName'] = None    # MVT_VARIABLE
            self.RegionInfo['EstateID'] = None    # MVT_U32
            self.RegionInfo['ParentEstateID'] = None    # MVT_U32
            self.RegionInfo['RegionFlags'] = None    # MVT_U32
            self.RegionInfo['BillableFactor'] = None    # MVT_F32
            self.RegionInfo['PricePerMeter'] = None    # MVT_S32
            self.RegionInfo['RedirectGridX'] = None    # MVT_S32
            self.RegionInfo['RedirectGridY'] = None    # MVT_S32
        else:
            self.RegionInfo = RegionInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('RegionInfo', SimName=self.RegionInfo['SimName'], EstateID=self.RegionInfo['EstateID'], ParentEstateID=self.RegionInfo['ParentEstateID'], RegionFlags=self.RegionInfo['RegionFlags'], BillableFactor=self.RegionInfo['BillableFactor'], PricePerMeter=self.RegionInfo['PricePerMeter'], RedirectGridX=self.RegionInfo['RedirectGridX'], RedirectGridY=self.RegionInfo['RedirectGridY']))

        return Message('GodUpdateRegionInfo', args)

class SetSimStatusInDatabasePacket(object):
    ''' a template for a SetSimStatusInDatabase packet '''

    def __init__(self, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SetSimStatusInDatabase'

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['RegionID'] = None    # MVT_LLUUID
            self.Data['HostName'] = None    # MVT_VARIABLE
            self.Data['X'] = None    # MVT_S32
            self.Data['Y'] = None    # MVT_S32
            self.Data['PID'] = None    # MVT_S32
            self.Data['AgentCount'] = None    # MVT_S32
            self.Data['TimeToLive'] = None    # MVT_S32
            self.Data['Status'] = None    # MVT_VARIABLE
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Data', RegionID=self.Data['RegionID'], HostName=self.Data['HostName'], X=self.Data['X'], Y=self.Data['Y'], PID=self.Data['PID'], AgentCount=self.Data['AgentCount'], TimeToLive=self.Data['TimeToLive'], Status=self.Data['Status']))

        return Message('SetSimStatusInDatabase', args)

class GroupVoteHistoryRequestPacket(object):
    ''' a template for a GroupVoteHistoryRequest packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}, TransactionDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupVoteHistoryRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
        else:
            self.GroupData = GroupDataBlock

        if TransactionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransactionData = {}    # New TransactionData block
            self.TransactionData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.TransactionData = TransactionDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID']))
        args.append(Block('TransactionData', TransactionID=self.TransactionData['TransactionID']))

        return Message('GroupVoteHistoryRequest', args)

class ChildAgentDyingPacket(object):
    ''' a template for a ChildAgentDying packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ChildAgentDying'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('ChildAgentDying', args)

class CreateGroupRequestPacket(object):
    ''' a template for a CreateGroupRequest packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CreateGroupRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['Name'] = None    # MVT_VARIABLE
            self.GroupData['Charter'] = None    # MVT_VARIABLE
            self.GroupData['ShowInList'] = None    # MVT_BOOL
            self.GroupData['InsigniaID'] = None    # MVT_LLUUID
            self.GroupData['MembershipFee'] = None    # MVT_S32
            self.GroupData['OpenEnrollment'] = None    # MVT_BOOL
            self.GroupData['AllowPublish'] = None    # MVT_BOOL
            self.GroupData['MaturePublish'] = None    # MVT_BOOL
        else:
            self.GroupData = GroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', Name=self.GroupData['Name'], Charter=self.GroupData['Charter'], ShowInList=self.GroupData['ShowInList'], InsigniaID=self.GroupData['InsigniaID'], MembershipFee=self.GroupData['MembershipFee'], OpenEnrollment=self.GroupData['OpenEnrollment'], AllowPublish=self.GroupData['AllowPublish'], MaturePublish=self.GroupData['MaturePublish']))

        return Message('CreateGroupRequest', args)

class ParcelDwellRequestPacket(object):
    ''' a template for a ParcelDwellRequest packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelDwellRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['LocalID'] = None    # MVT_S32
            self.Data['ParcelID'] = None    # MVT_LLUUID
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', LocalID=self.Data['LocalID'], ParcelID=self.Data['ParcelID']))

        return Message('ParcelDwellRequest', args)

class ObjectMaterialPacket(object):
    ''' a template for a ObjectMaterial packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectMaterial'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['Material'] = None    # MVT_U8
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], Material=block['Material']))

        return Message('ObjectMaterial', args)

class ObjectAddPacket(object):
    ''' a template for a ObjectAdd packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectAdd'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.ObjectData = ObjectDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('ObjectData', PCode=self.ObjectData['PCode'], Material=self.ObjectData['Material'], AddFlags=self.ObjectData['AddFlags'], PathCurve=self.ObjectData['PathCurve'], ProfileCurve=self.ObjectData['ProfileCurve'], PathBegin=self.ObjectData['PathBegin'], PathEnd=self.ObjectData['PathEnd'], PathScaleX=self.ObjectData['PathScaleX'], PathScaleY=self.ObjectData['PathScaleY'], PathShearX=self.ObjectData['PathShearX'], PathShearY=self.ObjectData['PathShearY'], PathTwist=self.ObjectData['PathTwist'], PathTwistBegin=self.ObjectData['PathTwistBegin'], PathRadiusOffset=self.ObjectData['PathRadiusOffset'], PathTaperX=self.ObjectData['PathTaperX'], PathTaperY=self.ObjectData['PathTaperY'], PathRevolutions=self.ObjectData['PathRevolutions'], PathSkew=self.ObjectData['PathSkew'], ProfileBegin=self.ObjectData['ProfileBegin'], ProfileEnd=self.ObjectData['ProfileEnd'], ProfileHollow=self.ObjectData['ProfileHollow'], BypassRaycast=self.ObjectData['BypassRaycast'], RayStart=self.ObjectData['RayStart'], RayEnd=self.ObjectData['RayEnd'], RayTargetID=self.ObjectData['RayTargetID'], RayEndIsIntersection=self.ObjectData['RayEndIsIntersection'], Scale=self.ObjectData['Scale'], Rotation=self.ObjectData['Rotation'], State=self.ObjectData['State']))

        return Message('ObjectAdd', args)

class DeactivateGesturesPacket(object):
    ''' a template for a DeactivateGestures packet '''

    def __init__(self, AgentDataBlock = {}, DataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DeactivateGestures'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['Flags'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

        if DataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Data = {}
            self.Data['ItemID'] = None    # MVT_LLUUID
            self.Data['GestureFlags'] = None    # MVT_U32
        else:
            self.DataBlocks = DataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], Flags=self.AgentData['Flags']))
        for block in self.DataBlocks:
            args.append(Block('Data', ItemID=block['ItemID'], GestureFlags=block['GestureFlags']))

        return Message('DeactivateGestures', args)

class ParcelOverlayPacket(object):
    ''' a template for a ParcelOverlay packet '''

    def __init__(self, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelOverlay'

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['SequenceID'] = None    # MVT_S32
            self.ParcelData['Data'] = None    # MVT_VARIABLE
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ParcelData', SequenceID=self.ParcelData['SequenceID'], Data=self.ParcelData['Data']))

        return Message('ParcelOverlay', args)

class UserInfoReplyPacket(object):
    ''' a template for a UserInfoReply packet '''

    def __init__(self, AgentDataBlock = {}, UserDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UserInfoReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if UserDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.UserData = {}    # New UserData block
            self.UserData['IMViaEMail'] = None    # MVT_BOOL
            self.UserData['DirectoryVisibility'] = None    # MVT_VARIABLE
            self.UserData['EMail'] = None    # MVT_VARIABLE
        else:
            self.UserData = UserDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('UserData', IMViaEMail=self.UserData['IMViaEMail'], DirectoryVisibility=self.UserData['DirectoryVisibility'], EMail=self.UserData['EMail']))

        return Message('UserInfoReply', args)

class UndoPacket(object):
    ''' a template for a Undo packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'Undo'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectID=block['ObjectID']))

        return Message('Undo', args)

class TransferInventoryPacket(object):
    ''' a template for a TransferInventory packet '''

    def __init__(self, InfoBlockBlock = {}, InventoryBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TransferInventory'

        if InfoBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.InfoBlock = {}    # New InfoBlock block
            self.InfoBlock['SourceID'] = None    # MVT_LLUUID
            self.InfoBlock['DestID'] = None    # MVT_LLUUID
            self.InfoBlock['TransactionID'] = None    # MVT_LLUUID
        else:
            self.InfoBlock = InfoBlockBlock

        if InventoryBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryBlock = {}
            self.InventoryBlock['InventoryID'] = None    # MVT_LLUUID
            self.InventoryBlock['Type'] = None    # MVT_S8
        else:
            self.InventoryBlockBlocks = InventoryBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('InfoBlock', SourceID=self.InfoBlock['SourceID'], DestID=self.InfoBlock['DestID'], TransactionID=self.InfoBlock['TransactionID']))
        for block in self.InventoryBlockBlocks:
            args.append(Block('InventoryBlock', InventoryID=block['InventoryID'], Type=block['Type']))

        return Message('TransferInventory', args)

class AvatarPropertiesUpdatePacket(object):
    ''' a template for a AvatarPropertiesUpdate packet '''

    def __init__(self, AgentDataBlock = {}, PropertiesDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarPropertiesUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if PropertiesDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.PropertiesData = {}    # New PropertiesData block
            self.PropertiesData['ImageID'] = None    # MVT_LLUUID
            self.PropertiesData['FLImageID'] = None    # MVT_LLUUID
            self.PropertiesData['AboutText'] = None    # MVT_VARIABLE
            self.PropertiesData['FLAboutText'] = None    # MVT_VARIABLE
            self.PropertiesData['AllowPublish'] = None    # MVT_BOOL
            self.PropertiesData['MaturePublish'] = None    # MVT_BOOL
            self.PropertiesData['ProfileURL'] = None    # MVT_VARIABLE
        else:
            self.PropertiesData = PropertiesDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('PropertiesData', ImageID=self.PropertiesData['ImageID'], FLImageID=self.PropertiesData['FLImageID'], AboutText=self.PropertiesData['AboutText'], FLAboutText=self.PropertiesData['FLAboutText'], AllowPublish=self.PropertiesData['AllowPublish'], MaturePublish=self.PropertiesData['MaturePublish'], ProfileURL=self.PropertiesData['ProfileURL']))

        return Message('AvatarPropertiesUpdate', args)

class LayerDataPacket(object):
    ''' a template for a LayerData packet '''

    def __init__(self, LayerIDBlock = {}, LayerDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LayerData'

        if LayerIDBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.LayerID = {}    # New LayerID block
            self.LayerID['Type'] = None    # MVT_U8
        else:
            self.LayerID = LayerIDBlock

        if LayerDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.LayerData = {}    # New LayerData block
            self.LayerData['Data'] = None    # MVT_VARIABLE
        else:
            self.LayerData = LayerDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('LayerID', Type=self.LayerID['Type']))
        args.append(Block('LayerData', Data=self.LayerData['Data']))

        return Message('LayerData', args)

class DirPopularReplyPacket(object):
    ''' a template for a DirPopularReply packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}, QueryRepliesBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirPopularReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
        else:
            self.QueryData = QueryDataBlock

        if QueryRepliesBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.QueryRepliesBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.QueryReplies = {}
            self.QueryReplies['ParcelID'] = None    # MVT_LLUUID
            self.QueryReplies['Name'] = None    # MVT_VARIABLE
            self.QueryReplies['Dwell'] = None    # MVT_F32
        else:
            self.QueryRepliesBlocks = QueryRepliesBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID']))
        for block in self.QueryRepliesBlocks:
            args.append(Block('QueryReplies', ParcelID=block['ParcelID'], Name=block['Name'], Dwell=block['Dwell']))

        return Message('DirPopularReply', args)

class RequestGodlikePowersPacket(object):
    ''' a template for a RequestGodlikePowers packet '''

    def __init__(self, AgentDataBlock = {}, RequestBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RequestGodlikePowers'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RequestBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RequestBlock = {}    # New RequestBlock block
            self.RequestBlock['Godlike'] = None    # MVT_BOOL
            self.RequestBlock['Token'] = None    # MVT_LLUUID
        else:
            self.RequestBlock = RequestBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('RequestBlock', Godlike=self.RequestBlock['Godlike'], Token=self.RequestBlock['Token']))

        return Message('RequestGodlikePowers', args)

class MeanCollisionAlertPacket(object):
    ''' a template for a MeanCollisionAlert packet '''

    def __init__(self, MeanCollisionBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MeanCollisionAlert'

        if MeanCollisionBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.MeanCollisionBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.MeanCollision = {}
            self.MeanCollision['Victim'] = None    # MVT_LLUUID
            self.MeanCollision['Perp'] = None    # MVT_LLUUID
            self.MeanCollision['Time'] = None    # MVT_U32
            self.MeanCollision['Mag'] = None    # MVT_F32
            self.MeanCollision['Type'] = None    # MVT_U8
        else:
            self.MeanCollisionBlocks = MeanCollisionBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.MeanCollisionBlocks:
            args.append(Block('MeanCollision', Victim=block['Victim'], Perp=block['Perp'], Time=block['Time'], Mag=block['Mag'], Type=block['Type']))

        return Message('MeanCollisionAlert', args)

class DirFindQueryPacket(object):
    ''' a template for a DirFindQuery packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirFindQuery'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['QueryText'] = None    # MVT_VARIABLE
            self.QueryData['QueryFlags'] = None    # MVT_U32
            self.QueryData['QueryStart'] = None    # MVT_S32
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], QueryText=self.QueryData['QueryText'], QueryFlags=self.QueryData['QueryFlags'], QueryStart=self.QueryData['QueryStart']))

        return Message('DirFindQuery', args)

class SetGroupAcceptNoticesPacket(object):
    ''' a template for a SetGroupAcceptNotices packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}, NewDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SetGroupAcceptNotices'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['GroupID'] = None    # MVT_LLUUID
            self.Data['AcceptNotices'] = None    # MVT_BOOL
        else:
            self.Data = DataBlock

        if NewDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.NewData = {}    # New NewData block
            self.NewData['ListInProfile'] = None    # MVT_BOOL
        else:
            self.NewData = NewDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', GroupID=self.Data['GroupID'], AcceptNotices=self.Data['AcceptNotices']))
        args.append(Block('NewData', ListInProfile=self.NewData['ListInProfile']))

        return Message('SetGroupAcceptNotices', args)

class CompleteAgentMovementPacket(object):
    ''' a template for a CompleteAgentMovement packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CompleteAgentMovement'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['CircuitCode'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], CircuitCode=self.AgentData['CircuitCode']))

        return Message('CompleteAgentMovement', args)

class LeaveGroupReplyPacket(object):
    ''' a template for a LeaveGroupReply packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LeaveGroupReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
            self.GroupData['Success'] = None    # MVT_BOOL
        else:
            self.GroupData = GroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID'], Success=self.GroupData['Success']))

        return Message('LeaveGroupReply', args)

class ParcelGodMarkAsContentPacket(object):
    ''' a template for a ParcelGodMarkAsContent packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelGodMarkAsContent'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['LocalID'] = None    # MVT_S32
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', LocalID=self.ParcelData['LocalID']))

        return Message('ParcelGodMarkAsContent', args)

class ObjectSaleInfoPacket(object):
    ''' a template for a ObjectSaleInfo packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectSaleInfo'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['LocalID'] = None    # MVT_U32
            self.ObjectData['SaleType'] = None    # MVT_U8
            self.ObjectData['SalePrice'] = None    # MVT_S32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', LocalID=block['LocalID'], SaleType=block['SaleType'], SalePrice=block['SalePrice']))

        return Message('ObjectSaleInfo', args)

class CoarseLocationUpdatePacket(object):
    ''' a template for a CoarseLocationUpdate packet '''

    def __init__(self, LocationBlocks = [], IndexBlock = {}, AgentDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CoarseLocationUpdate'

        if LocationBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.LocationBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Location = {}
            self.Location['X'] = None    # MVT_U8
            self.Location['Y'] = None    # MVT_U8
            self.Location['Z'] = None    # MVT_U8
        else:
            self.LocationBlocks = LocationBlocks

        if IndexBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Index = {}    # New Index block
            self.Index['You'] = None    # MVT_S16
            self.Index['Prey'] = None    # MVT_S16
        else:
            self.Index = IndexBlock

        if AgentDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.AgentDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.AgentData = {}
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentDataBlocks = AgentDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.LocationBlocks:
            args.append(Block('Location', X=block['X'], Y=block['Y'], Z=block['Z']))
        args.append(Block('Index', You=self.Index['You'], Prey=self.Index['Prey']))
        for block in self.AgentDataBlocks:
            args.append(Block('AgentData', AgentID=block['AgentID']))

        return Message('CoarseLocationUpdate', args)

class NetTestPacket(object):
    ''' a template for a NetTest packet '''

    def __init__(self, NetBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'NetTest'

        if NetBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.NetBlock = {}    # New NetBlock block
            self.NetBlock['Port'] = None    # MVT_IP_PORT
        else:
            self.NetBlock = NetBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('NetBlock', Port=self.NetBlock['Port']))

        return Message('NetTest', args)

class ForceObjectSelectPacket(object):
    ''' a template for a ForceObjectSelect packet '''

    def __init__(self, HeaderBlock = {}, DataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ForceObjectSelect'

        if HeaderBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Header = {}    # New Header block
            self.Header['ResetList'] = None    # MVT_BOOL
        else:
            self.Header = HeaderBlock

        if DataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Data = {}
            self.Data['LocalID'] = None    # MVT_U32
        else:
            self.DataBlocks = DataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Header', ResetList=self.Header['ResetList']))
        for block in self.DataBlocks:
            args.append(Block('Data', LocalID=block['LocalID']))

        return Message('ForceObjectSelect', args)

class MapBlockReplyPacket(object):
    ''' a template for a MapBlockReply packet '''

    def __init__(self, AgentDataBlock = {}, DataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MapBlockReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['Flags'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

        if DataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Data = {}
            self.Data['X'] = None    # MVT_U16
            self.Data['Y'] = None    # MVT_U16
            self.Data['Name'] = None    # MVT_VARIABLE
            self.Data['Access'] = None    # MVT_U8
            self.Data['RegionFlags'] = None    # MVT_U32
            self.Data['WaterHeight'] = None    # MVT_U8
            self.Data['Agents'] = None    # MVT_U8
            self.Data['MapImageID'] = None    # MVT_LLUUID
        else:
            self.DataBlocks = DataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], Flags=self.AgentData['Flags']))
        for block in self.DataBlocks:
            args.append(Block('Data', X=block['X'], Y=block['Y'], Name=block['Name'], Access=block['Access'], RegionFlags=block['RegionFlags'], WaterHeight=block['WaterHeight'], Agents=block['Agents'], MapImageID=block['MapImageID']))

        return Message('MapBlockReply', args)

class AgentSetAppearancePacket(object):
    ''' a template for a AgentSetAppearance packet '''

    def __init__(self, AgentDataBlock = {}, WearableDataBlocks = [], ObjectDataBlock = {}, VisualParamBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentSetAppearance'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['SerialNum'] = None    # MVT_U32
            self.AgentData['Size'] = None    # MVT_LLVector3
        else:
            self.AgentData = AgentDataBlock

        if WearableDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.WearableDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.WearableData = {}
            self.WearableData['CacheID'] = None    # MVT_LLUUID
            self.WearableData['TextureIndex'] = None    # MVT_U8
        else:
            self.WearableDataBlocks = WearableDataBlocks

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['TextureEntry'] = None    # MVT_VARIABLE
        else:
            self.ObjectData = ObjectDataBlock

        if VisualParamBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.VisualParamBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.VisualParam = {}
            self.VisualParam['ParamValue'] = None    # MVT_U8
        else:
            self.VisualParamBlocks = VisualParamBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], SerialNum=self.AgentData['SerialNum'], Size=self.AgentData['Size']))
        for block in self.WearableDataBlocks:
            args.append(Block('WearableData', CacheID=block['CacheID'], TextureIndex=block['TextureIndex']))
        args.append(Block('ObjectData', TextureEntry=self.ObjectData['TextureEntry']))
        for block in self.VisualParamBlocks:
            args.append(Block('VisualParam', ParamValue=block['ParamValue']))

        return Message('AgentSetAppearance', args)

class MoveTaskInventoryPacket(object):
    ''' a template for a MoveTaskInventory packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MoveTaskInventory'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['FolderID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.InventoryData = {}    # New InventoryData block
            self.InventoryData['LocalID'] = None    # MVT_U32
            self.InventoryData['ItemID'] = None    # MVT_LLUUID
        else:
            self.InventoryData = InventoryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], FolderID=self.AgentData['FolderID']))
        args.append(Block('InventoryData', LocalID=self.InventoryData['LocalID'], ItemID=self.InventoryData['ItemID']))

        return Message('MoveTaskInventory', args)

class EventGodDeletePacket(object):
    ''' a template for a EventGodDelete packet '''

    def __init__(self, AgentDataBlock = {}, EventDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EventGodDelete'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if EventDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.EventData = {}    # New EventData block
            self.EventData['EventID'] = None    # MVT_U32
        else:
            self.EventData = EventDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['QueryText'] = None    # MVT_VARIABLE
            self.QueryData['QueryFlags'] = None    # MVT_U32
            self.QueryData['QueryStart'] = None    # MVT_S32
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('EventData', EventID=self.EventData['EventID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], QueryText=self.QueryData['QueryText'], QueryFlags=self.QueryData['QueryFlags'], QueryStart=self.QueryData['QueryStart']))

        return Message('EventGodDelete', args)

class CompletePingCheckPacket(object):
    ''' a template for a CompletePingCheck packet '''

    def __init__(self, PingIDBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CompletePingCheck'

        if PingIDBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.PingID = {}    # New PingID block
            self.PingID['PingID'] = None    # MVT_U8
        else:
            self.PingID = PingIDBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('PingID', PingID=self.PingID['PingID']))

        return Message('CompletePingCheck', args)

class AgentDataUpdatePacket(object):
    ''' a template for a AgentDataUpdate packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentDataUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['FirstName'] = None    # MVT_VARIABLE
            self.AgentData['LastName'] = None    # MVT_VARIABLE
            self.AgentData['GroupTitle'] = None    # MVT_VARIABLE
            self.AgentData['ActiveGroupID'] = None    # MVT_LLUUID
            self.AgentData['GroupPowers'] = None    # MVT_U64
            self.AgentData['GroupName'] = None    # MVT_VARIABLE
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], FirstName=self.AgentData['FirstName'], LastName=self.AgentData['LastName'], GroupTitle=self.AgentData['GroupTitle'], ActiveGroupID=self.AgentData['ActiveGroupID'], GroupPowers=self.AgentData['GroupPowers'], GroupName=self.AgentData['GroupName']))

        return Message('AgentDataUpdate', args)

class TeleportRequestPacket(object):
    ''' a template for a TeleportRequest packet '''

    def __init__(self, AgentDataBlock = {}, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TeleportRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['RegionID'] = None    # MVT_LLUUID
            self.Info['Position'] = None    # MVT_LLVector3
            self.Info['LookAt'] = None    # MVT_LLVector3
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Info', RegionID=self.Info['RegionID'], Position=self.Info['Position'], LookAt=self.Info['LookAt']))

        return Message('TeleportRequest', args)

class UpdateInventoryItemPacket(object):
    ''' a template for a UpdateInventoryItem packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UpdateInventoryItem'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
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
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], TransactionID=self.AgentData['TransactionID']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', ItemID=block['ItemID'], FolderID=block['FolderID'], CallbackID=block['CallbackID'], CreatorID=block['CreatorID'], OwnerID=block['OwnerID'], GroupID=block['GroupID'], BaseMask=block['BaseMask'], OwnerMask=block['OwnerMask'], GroupMask=block['GroupMask'], EveryoneMask=block['EveryoneMask'], NextOwnerMask=block['NextOwnerMask'], GroupOwned=block['GroupOwned'], TransactionID=block['TransactionID'], Type=block['Type'], InvType=block['InvType'], Flags=block['Flags'], SaleType=block['SaleType'], SalePrice=block['SalePrice'], Name=block['Name'], Description=block['Description'], CreationDate=block['CreationDate'], CRC=block['CRC']))

        return Message('UpdateInventoryItem', args)

class NearestLandingRegionReplyPacket(object):
    ''' a template for a NearestLandingRegionReply packet '''

    def __init__(self, LandingRegionDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'NearestLandingRegionReply'

        if LandingRegionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.LandingRegionData = {}    # New LandingRegionData block
            self.LandingRegionData['RegionHandle'] = None    # MVT_U64
        else:
            self.LandingRegionData = LandingRegionDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('LandingRegionData', RegionHandle=self.LandingRegionData['RegionHandle']))

        return Message('NearestLandingRegionReply', args)

class EdgeDataPacketPacket(object):
    ''' a template for a EdgeDataPacket packet '''

    def __init__(self, EdgeDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EdgeDataPacket'

        if EdgeDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.EdgeData = {}    # New EdgeData block
            self.EdgeData['LayerType'] = None    # MVT_U8
            self.EdgeData['Direction'] = None    # MVT_U8
            self.EdgeData['LayerData'] = None    # MVT_VARIABLE
        else:
            self.EdgeData = EdgeDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('EdgeData', LayerType=self.EdgeData['LayerType'], Direction=self.EdgeData['Direction'], LayerData=self.EdgeData['LayerData']))

        return Message('EdgeDataPacket', args)

class EconomyDataRequestPacket(object):
    ''' a template for a EconomyDataRequest packet '''

    def __init__(self):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EconomyDataRequest'

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []

        return Message('EconomyDataRequest', args)

class LiveHelpGroupRequestPacket(object):
    ''' a template for a LiveHelpGroupRequest packet '''

    def __init__(self, RequestDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LiveHelpGroupRequest'

        if RequestDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RequestData = {}    # New RequestData block
            self.RequestData['RequestID'] = None    # MVT_LLUUID
            self.RequestData['AgentID'] = None    # MVT_LLUUID
        else:
            self.RequestData = RequestDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('RequestData', RequestID=self.RequestData['RequestID'], AgentID=self.RequestData['AgentID']))

        return Message('LiveHelpGroupRequest', args)

class AddCircuitCodePacket(object):
    ''' a template for a AddCircuitCode packet '''

    def __init__(self, CircuitCodeBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AddCircuitCode'

        if CircuitCodeBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.CircuitCode = {}    # New CircuitCode block
            self.CircuitCode['Code'] = None    # MVT_U32
            self.CircuitCode['SessionID'] = None    # MVT_LLUUID
            self.CircuitCode['AgentID'] = None    # MVT_LLUUID
        else:
            self.CircuitCode = CircuitCodeBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('CircuitCode', Code=self.CircuitCode['Code'], SessionID=self.CircuitCode['SessionID'], AgentID=self.CircuitCode['AgentID']))

        return Message('AddCircuitCode', args)

class GroupAccountTransactionsRequestPacket(object):
    ''' a template for a GroupAccountTransactionsRequest packet '''

    def __init__(self, AgentDataBlock = {}, MoneyDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupAccountTransactionsRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MoneyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MoneyData = {}    # New MoneyData block
            self.MoneyData['RequestID'] = None    # MVT_LLUUID
            self.MoneyData['IntervalDays'] = None    # MVT_S32
            self.MoneyData['CurrentInterval'] = None    # MVT_S32
        else:
            self.MoneyData = MoneyDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('MoneyData', RequestID=self.MoneyData['RequestID'], IntervalDays=self.MoneyData['IntervalDays'], CurrentInterval=self.MoneyData['CurrentInterval']))

        return Message('GroupAccountTransactionsRequest', args)

class UUIDNameReplyPacket(object):
    ''' a template for a UUIDNameReply packet '''

    def __init__(self, UUIDNameBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UUIDNameReply'

        if UUIDNameBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.UUIDNameBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.UUIDNameBlock = {}
            self.UUIDNameBlock['ID'] = None    # MVT_LLUUID
            self.UUIDNameBlock['FirstName'] = None    # MVT_VARIABLE
            self.UUIDNameBlock['LastName'] = None    # MVT_VARIABLE
        else:
            self.UUIDNameBlockBlocks = UUIDNameBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.UUIDNameBlockBlocks:
            args.append(Block('UUIDNameBlock', ID=block['ID'], FirstName=block['FirstName'], LastName=block['LastName']))

        return Message('UUIDNameReply', args)

class ObjectLinkPacket(object):
    ''' a template for a ObjectLink packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectLink'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('ObjectLink', args)

class PreloadSoundPacket(object):
    ''' a template for a PreloadSound packet '''

    def __init__(self, DataBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'PreloadSound'

        if DataBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.DataBlock = {}
            self.DataBlock['ObjectID'] = None    # MVT_LLUUID
            self.DataBlock['OwnerID'] = None    # MVT_LLUUID
            self.DataBlock['SoundID'] = None    # MVT_LLUUID
        else:
            self.DataBlockBlocks = DataBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.DataBlockBlocks:
            args.append(Block('DataBlock', ObjectID=block['ObjectID'], OwnerID=block['OwnerID'], SoundID=block['SoundID']))

        return Message('PreloadSound', args)

class EmailMessageRequestPacket(object):
    ''' a template for a EmailMessageRequest packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EmailMessageRequest'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['ObjectID'] = None    # MVT_LLUUID
            self.DataBlock['FromAddress'] = None    # MVT_VARIABLE
            self.DataBlock['Subject'] = None    # MVT_VARIABLE
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', ObjectID=self.DataBlock['ObjectID'], FromAddress=self.DataBlock['FromAddress'], Subject=self.DataBlock['Subject']))

        return Message('EmailMessageRequest', args)

class ParcelGodForceOwnerPacket(object):
    ''' a template for a ParcelGodForceOwner packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelGodForceOwner'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['OwnerID'] = None    # MVT_LLUUID
            self.Data['LocalID'] = None    # MVT_S32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', OwnerID=self.Data['OwnerID'], LocalID=self.Data['LocalID']))

        return Message('ParcelGodForceOwner', args)

class ScriptMailRegistrationPacket(object):
    ''' a template for a ScriptMailRegistration packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptMailRegistration'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['TargetIP'] = None    # MVT_VARIABLE
            self.DataBlock['TargetPort'] = None    # MVT_IP_PORT
            self.DataBlock['TaskID'] = None    # MVT_LLUUID
            self.DataBlock['Flags'] = None    # MVT_U32
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', TargetIP=self.DataBlock['TargetIP'], TargetPort=self.DataBlock['TargetPort'], TaskID=self.DataBlock['TaskID'], Flags=self.DataBlock['Flags']))

        return Message('ScriptMailRegistration', args)

class ObjectRotationPacket(object):
    ''' a template for a ObjectRotation packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectRotation'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['Rotation'] = None    # MVT_LLQuaternion
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], Rotation=block['Rotation']))

        return Message('ObjectRotation', args)

class AcceptFriendshipPacket(object):
    ''' a template for a AcceptFriendship packet '''

    def __init__(self, AgentDataBlock = {}, TransactionBlockBlock = {}, FolderDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AcceptFriendship'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if TransactionBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransactionBlock = {}    # New TransactionBlock block
            self.TransactionBlock['TransactionID'] = None    # MVT_LLUUID
        else:
            self.TransactionBlock = TransactionBlockBlock

        if FolderDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.FolderDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.FolderData = {}
            self.FolderData['FolderID'] = None    # MVT_LLUUID
        else:
            self.FolderDataBlocks = FolderDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('TransactionBlock', TransactionID=self.TransactionBlock['TransactionID']))
        for block in self.FolderDataBlocks:
            args.append(Block('FolderData', FolderID=block['FolderID']))

        return Message('AcceptFriendship', args)

class AvatarNotesReplyPacket(object):
    ''' a template for a AvatarNotesReply packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarNotesReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['TargetID'] = None    # MVT_LLUUID
            self.Data['Notes'] = None    # MVT_VARIABLE
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('Data', TargetID=self.Data['TargetID'], Notes=self.Data['Notes']))

        return Message('AvatarNotesReply', args)

class RezMultipleAttachmentsFromInvPacket(object):
    ''' a template for a RezMultipleAttachmentsFromInv packet '''

    def __init__(self, AgentDataBlock = {}, HeaderDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RezMultipleAttachmentsFromInv'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if HeaderDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.HeaderData = {}    # New HeaderData block
            self.HeaderData['CompoundMsgID'] = None    # MVT_LLUUID
            self.HeaderData['TotalObjects'] = None    # MVT_U8
            self.HeaderData['FirstDetachAll'] = None    # MVT_BOOL
        else:
            self.HeaderData = HeaderDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ItemID'] = None    # MVT_LLUUID
            self.ObjectData['OwnerID'] = None    # MVT_LLUUID
            self.ObjectData['AttachmentPt'] = None    # MVT_U8
            self.ObjectData['ItemFlags'] = None    # MVT_U32
            self.ObjectData['GroupMask'] = None    # MVT_U32
            self.ObjectData['EveryoneMask'] = None    # MVT_U32
            self.ObjectData['NextOwnerMask'] = None    # MVT_U32
            self.ObjectData['Name'] = None    # MVT_VARIABLE
            self.ObjectData['Description'] = None    # MVT_VARIABLE
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('HeaderData', CompoundMsgID=self.HeaderData['CompoundMsgID'], TotalObjects=self.HeaderData['TotalObjects'], FirstDetachAll=self.HeaderData['FirstDetachAll']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ItemID=block['ItemID'], OwnerID=block['OwnerID'], AttachmentPt=block['AttachmentPt'], ItemFlags=block['ItemFlags'], GroupMask=block['GroupMask'], EveryoneMask=block['EveryoneMask'], NextOwnerMask=block['NextOwnerMask'], Name=block['Name'], Description=block['Description']))

        return Message('RezMultipleAttachmentsFromInv', args)

class TeleportLureRequestPacket(object):
    ''' a template for a TeleportLureRequest packet '''

    def __init__(self, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TeleportLureRequest'

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['AgentID'] = None    # MVT_LLUUID
            self.Info['SessionID'] = None    # MVT_LLUUID
            self.Info['LureID'] = None    # MVT_LLUUID
            self.Info['TeleportFlags'] = None    # MVT_U32
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Info', AgentID=self.Info['AgentID'], SessionID=self.Info['SessionID'], LureID=self.Info['LureID'], TeleportFlags=self.Info['TeleportFlags']))

        return Message('TeleportLureRequest', args)

class MoveInventoryFolderPacket(object):
    ''' a template for a MoveInventoryFolder packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MoveInventoryFolder'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['Stamp'] = None    # MVT_BOOL
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
            self.InventoryData['FolderID'] = None    # MVT_LLUUID
            self.InventoryData['ParentID'] = None    # MVT_LLUUID
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], Stamp=self.AgentData['Stamp']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', FolderID=block['FolderID'], ParentID=block['ParentID']))

        return Message('MoveInventoryFolder', args)

class TransferInfoPacket(object):
    ''' a template for a TransferInfo packet '''

    def __init__(self, TransferInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TransferInfo'

        if TransferInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransferInfo = {}    # New TransferInfo block
            self.TransferInfo['TransferID'] = None    # MVT_LLUUID
            self.TransferInfo['ChannelType'] = None    # MVT_S32
            self.TransferInfo['TargetType'] = None    # MVT_S32
            self.TransferInfo['Status'] = None    # MVT_S32
            self.TransferInfo['Size'] = None    # MVT_S32
            self.TransferInfo['Params'] = None    # MVT_VARIABLE
        else:
            self.TransferInfo = TransferInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TransferInfo', TransferID=self.TransferInfo['TransferID'], ChannelType=self.TransferInfo['ChannelType'], TargetType=self.TransferInfo['TargetType'], Status=self.TransferInfo['Status'], Size=self.TransferInfo['Size'], Params=self.TransferInfo['Params']))

        return Message('TransferInfo', args)

class DirPlacesQueryPacket(object):
    ''' a template for a DirPlacesQuery packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirPlacesQuery'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['QueryText'] = None    # MVT_VARIABLE
            self.QueryData['QueryFlags'] = None    # MVT_U32
            self.QueryData['Category'] = None    # MVT_S8
            self.QueryData['SimName'] = None    # MVT_VARIABLE
            self.QueryData['QueryStart'] = None    # MVT_S32
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], QueryText=self.QueryData['QueryText'], QueryFlags=self.QueryData['QueryFlags'], Category=self.QueryData['Category'], SimName=self.QueryData['SimName'], QueryStart=self.QueryData['QueryStart']))

        return Message('DirPlacesQuery', args)

class ScriptAnswerYesPacket(object):
    ''' a template for a ScriptAnswerYes packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptAnswerYes'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['TaskID'] = None    # MVT_LLUUID
            self.Data['ItemID'] = None    # MVT_LLUUID
            self.Data['Questions'] = None    # MVT_S32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', TaskID=self.Data['TaskID'], ItemID=self.Data['ItemID'], Questions=self.Data['Questions']))

        return Message('ScriptAnswerYes', args)

class SimulatorPresentAtLocationPacket(object):
    ''' a template for a SimulatorPresentAtLocation packet '''

    def __init__(self, SimulatorPublicHostBlockBlock = {}, NeighborBlockBlocks = [], SimulatorBlockBlock = {}, TelehubBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SimulatorPresentAtLocation'

        if SimulatorPublicHostBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SimulatorPublicHostBlock = {}    # New SimulatorPublicHostBlock block
            self.SimulatorPublicHostBlock['Port'] = None    # MVT_IP_PORT
            self.SimulatorPublicHostBlock['SimulatorIP'] = None    # MVT_IP_ADDR
            self.SimulatorPublicHostBlock['GridX'] = None    # MVT_U32
            self.SimulatorPublicHostBlock['GridY'] = None    # MVT_U32
        else:
            self.SimulatorPublicHostBlock = SimulatorPublicHostBlockBlock

        if NeighborBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.NeighborBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.NeighborBlock = {}
            self.NeighborBlock['IP'] = None    # MVT_IP_ADDR
            self.NeighborBlock['Port'] = None    # MVT_IP_PORT
        else:
            self.NeighborBlockBlocks = NeighborBlockBlocks

        if SimulatorBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SimulatorBlock = {}    # New SimulatorBlock block
            self.SimulatorBlock['SimName'] = None    # MVT_VARIABLE
            self.SimulatorBlock['SimAccess'] = None    # MVT_U8
            self.SimulatorBlock['RegionFlags'] = None    # MVT_U32
            self.SimulatorBlock['RegionID'] = None    # MVT_LLUUID
            self.SimulatorBlock['EstateID'] = None    # MVT_U32
            self.SimulatorBlock['ParentEstateID'] = None    # MVT_U32
        else:
            self.SimulatorBlock = SimulatorBlockBlock

        if TelehubBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.TelehubBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.TelehubBlock = {}
            self.TelehubBlock['HasTelehub'] = None    # MVT_BOOL
            self.TelehubBlock['TelehubPos'] = None    # MVT_LLVector3
        else:
            self.TelehubBlockBlocks = TelehubBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('SimulatorPublicHostBlock', Port=self.SimulatorPublicHostBlock['Port'], SimulatorIP=self.SimulatorPublicHostBlock['SimulatorIP'], GridX=self.SimulatorPublicHostBlock['GridX'], GridY=self.SimulatorPublicHostBlock['GridY']))
        for block in self.NeighborBlockBlocks:
            args.append(Block('NeighborBlock', IP=block['IP'], Port=block['Port']))
        args.append(Block('SimulatorBlock', SimName=self.SimulatorBlock['SimName'], SimAccess=self.SimulatorBlock['SimAccess'], RegionFlags=self.SimulatorBlock['RegionFlags'], RegionID=self.SimulatorBlock['RegionID'], EstateID=self.SimulatorBlock['EstateID'], ParentEstateID=self.SimulatorBlock['ParentEstateID']))
        for block in self.TelehubBlockBlocks:
            args.append(Block('TelehubBlock', HasTelehub=block['HasTelehub'], TelehubPos=block['TelehubPos']))

        return Message('SimulatorPresentAtLocation', args)

class GroupMembersRequestPacket(object):
    ''' a template for a GroupMembersRequest packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupMembersRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
            self.GroupData['RequestID'] = None    # MVT_LLUUID
        else:
            self.GroupData = GroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID'], RequestID=self.GroupData['RequestID']))

        return Message('GroupMembersRequest', args)

class SetScriptRunningPacket(object):
    ''' a template for a SetScriptRunning packet '''

    def __init__(self, AgentDataBlock = {}, ScriptBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SetScriptRunning'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ScriptBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Script = {}    # New Script block
            self.Script['ObjectID'] = None    # MVT_LLUUID
            self.Script['ItemID'] = None    # MVT_LLUUID
            self.Script['Running'] = None    # MVT_BOOL
        else:
            self.Script = ScriptBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Script', ObjectID=self.Script['ObjectID'], ItemID=self.Script['ItemID'], Running=self.Script['Running']))

        return Message('SetScriptRunning', args)

class ModifyLandPacket(object):
    ''' a template for a ModifyLand packet '''

    def __init__(self, AgentDataBlock = {}, ModifyBlockBlock = {}, ParcelDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ModifyLand'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ModifyBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ModifyBlock = {}    # New ModifyBlock block
            self.ModifyBlock['Action'] = None    # MVT_U8
            self.ModifyBlock['BrushSize'] = None    # MVT_U8
            self.ModifyBlock['Seconds'] = None    # MVT_F32
            self.ModifyBlock['Height'] = None    # MVT_F32
        else:
            self.ModifyBlock = ModifyBlockBlock

        if ParcelDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParcelDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParcelData = {}
            self.ParcelData['LocalID'] = None    # MVT_S32
            self.ParcelData['West'] = None    # MVT_F32
            self.ParcelData['South'] = None    # MVT_F32
            self.ParcelData['East'] = None    # MVT_F32
            self.ParcelData['North'] = None    # MVT_F32
        else:
            self.ParcelDataBlocks = ParcelDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ModifyBlock', Action=self.ModifyBlock['Action'], BrushSize=self.ModifyBlock['BrushSize'], Seconds=self.ModifyBlock['Seconds'], Height=self.ModifyBlock['Height']))
        for block in self.ParcelDataBlocks:
            args.append(Block('ParcelData', LocalID=block['LocalID'], West=block['West'], South=block['South'], East=block['East'], North=block['North']))

        return Message('ModifyLand', args)

class SimCrashedPacket(object):
    ''' a template for a SimCrashed packet '''

    def __init__(self, DataBlock = {}, UsersBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SimCrashed'

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['RegionX'] = None    # MVT_U32
            self.Data['RegionY'] = None    # MVT_U32
        else:
            self.Data = DataBlock

        if UsersBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.UsersBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Users = {}
            self.Users['AgentID'] = None    # MVT_LLUUID
        else:
            self.UsersBlocks = UsersBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Data', RegionX=self.Data['RegionX'], RegionY=self.Data['RegionY']))
        for block in self.UsersBlocks:
            args.append(Block('Users', AgentID=block['AgentID']))

        return Message('SimCrashed', args)

class MergeParcelPacket(object):
    ''' a template for a MergeParcel packet '''

    def __init__(self, MasterParcelDataBlock = {}, SlaveParcelDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MergeParcel'

        if MasterParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MasterParcelData = {}    # New MasterParcelData block
            self.MasterParcelData['MasterID'] = None    # MVT_LLUUID
        else:
            self.MasterParcelData = MasterParcelDataBlock

        if SlaveParcelDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.SlaveParcelDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.SlaveParcelData = {}
            self.SlaveParcelData['SlaveID'] = None    # MVT_LLUUID
        else:
            self.SlaveParcelDataBlocks = SlaveParcelDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('MasterParcelData', MasterID=self.MasterParcelData['MasterID']))
        for block in self.SlaveParcelDataBlocks:
            args.append(Block('SlaveParcelData', SlaveID=block['SlaveID']))

        return Message('MergeParcel', args)

class ObjectBuyPacket(object):
    ''' a template for a ObjectBuy packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectBuy'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
            self.AgentData['CategoryID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
            self.ObjectData['SaleType'] = None    # MVT_U8
            self.ObjectData['SalePrice'] = None    # MVT_S32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID'], CategoryID=self.AgentData['CategoryID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID'], SaleType=block['SaleType'], SalePrice=block['SalePrice']))

        return Message('ObjectBuy', args)

class CreateLandmarkForEventPacket(object):
    ''' a template for a CreateLandmarkForEvent packet '''

    def __init__(self, AgentDataBlock = {}, EventDataBlock = {}, InventoryBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CreateLandmarkForEvent'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if EventDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.EventData = {}    # New EventData block
            self.EventData['EventID'] = None    # MVT_U32
        else:
            self.EventData = EventDataBlock

        if InventoryBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.InventoryBlock = {}    # New InventoryBlock block
            self.InventoryBlock['FolderID'] = None    # MVT_LLUUID
            self.InventoryBlock['Name'] = None    # MVT_VARIABLE
        else:
            self.InventoryBlock = InventoryBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('EventData', EventID=self.EventData['EventID']))
        args.append(Block('InventoryBlock', FolderID=self.InventoryBlock['FolderID'], Name=self.InventoryBlock['Name']))

        return Message('CreateLandmarkForEvent', args)

class PickInfoUpdatePacket(object):
    ''' a template for a PickInfoUpdate packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'PickInfoUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['PickID'] = None    # MVT_LLUUID
            self.Data['CreatorID'] = None    # MVT_LLUUID
            self.Data['TopPick'] = None    # MVT_BOOL
            self.Data['ParcelID'] = None    # MVT_LLUUID
            self.Data['Name'] = None    # MVT_VARIABLE
            self.Data['Desc'] = None    # MVT_VARIABLE
            self.Data['SnapshotID'] = None    # MVT_LLUUID
            self.Data['PosGlobal'] = None    # MVT_LLVector3d
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', PickID=self.Data['PickID'], CreatorID=self.Data['CreatorID'], TopPick=self.Data['TopPick'], ParcelID=self.Data['ParcelID'], Name=self.Data['Name'], Desc=self.Data['Desc'], SnapshotID=self.Data['SnapshotID'], PosGlobal=self.Data['PosGlobal']))

        return Message('PickInfoUpdate', args)

class MapLayerRequestPacket(object):
    ''' a template for a MapLayerRequest packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MapLayerRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['Flags'] = None    # MVT_U32
            self.AgentData['EstateID'] = None    # MVT_U32
            self.AgentData['Godlike'] = None    # MVT_BOOL
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], Flags=self.AgentData['Flags'], EstateID=self.AgentData['EstateID'], Godlike=self.AgentData['Godlike']))

        return Message('MapLayerRequest', args)

class TeleportLocalPacket(object):
    ''' a template for a TeleportLocal packet '''

    def __init__(self, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TeleportLocal'

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['AgentID'] = None    # MVT_LLUUID
            self.Info['LocationID'] = None    # MVT_U32
            self.Info['Position'] = None    # MVT_LLVector3
            self.Info['LookAt'] = None    # MVT_LLVector3
            self.Info['TeleportFlags'] = None    # MVT_U32
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Info', AgentID=self.Info['AgentID'], LocationID=self.Info['LocationID'], Position=self.Info['Position'], LookAt=self.Info['LookAt'], TeleportFlags=self.Info['TeleportFlags']))

        return Message('TeleportLocal', args)

class RemoveInventoryObjectsPacket(object):
    ''' a template for a RemoveInventoryObjects packet '''

    def __init__(self, AgentDataBlock = {}, FolderDataBlocks = [], ItemDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RemoveInventoryObjects'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if FolderDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.FolderDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.FolderData = {}
            self.FolderData['FolderID'] = None    # MVT_LLUUID
        else:
            self.FolderDataBlocks = FolderDataBlocks

        if ItemDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ItemDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ItemData = {}
            self.ItemData['ItemID'] = None    # MVT_LLUUID
        else:
            self.ItemDataBlocks = ItemDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.FolderDataBlocks:
            args.append(Block('FolderData', FolderID=block['FolderID']))
        for block in self.ItemDataBlocks:
            args.append(Block('ItemData', ItemID=block['ItemID']))

        return Message('RemoveInventoryObjects', args)

class KickUserPacket(object):
    ''' a template for a KickUser packet '''

    def __init__(self, TargetBlockBlock = {}, UserInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'KickUser'

        if TargetBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TargetBlock = {}    # New TargetBlock block
            self.TargetBlock['TargetIP'] = None    # MVT_IP_ADDR
            self.TargetBlock['TargetPort'] = None    # MVT_IP_PORT
        else:
            self.TargetBlock = TargetBlockBlock

        if UserInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.UserInfo = {}    # New UserInfo block
            self.UserInfo['AgentID'] = None    # MVT_LLUUID
            self.UserInfo['SessionID'] = None    # MVT_LLUUID
            self.UserInfo['Reason'] = None    # MVT_VARIABLE
        else:
            self.UserInfo = UserInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TargetBlock', TargetIP=self.TargetBlock['TargetIP'], TargetPort=self.TargetBlock['TargetPort']))
        args.append(Block('UserInfo', AgentID=self.UserInfo['AgentID'], SessionID=self.UserInfo['SessionID'], Reason=self.UserInfo['Reason']))

        return Message('KickUser', args)

class CameraConstraintPacket(object):
    ''' a template for a CameraConstraint packet '''

    def __init__(self, CameraCollidePlaneBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CameraConstraint'

        if CameraCollidePlaneBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.CameraCollidePlane = {}    # New CameraCollidePlane block
            self.CameraCollidePlane['Plane'] = None    # MVT_LLVector4
        else:
            self.CameraCollidePlane = CameraCollidePlaneBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('CameraCollidePlane', Plane=self.CameraCollidePlane['Plane']))

        return Message('CameraConstraint', args)

class AvatarClassifiedReplyPacket(object):
    ''' a template for a AvatarClassifiedReply packet '''

    def __init__(self, AgentDataBlock = {}, DataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarClassifiedReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['TargetID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Data = {}
            self.Data['ClassifiedID'] = None    # MVT_LLUUID
            self.Data['Name'] = None    # MVT_VARIABLE
        else:
            self.DataBlocks = DataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], TargetID=self.AgentData['TargetID']))
        for block in self.DataBlocks:
            args.append(Block('Data', ClassifiedID=block['ClassifiedID'], Name=block['Name']))

        return Message('AvatarClassifiedReply', args)

class MuteListRequestPacket(object):
    ''' a template for a MuteListRequest packet '''

    def __init__(self, AgentDataBlock = {}, MuteDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MuteListRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MuteDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MuteData = {}    # New MuteData block
            self.MuteData['MuteCRC'] = None    # MVT_U32
        else:
            self.MuteData = MuteDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('MuteData', MuteCRC=self.MuteData['MuteCRC']))

        return Message('MuteListRequest', args)

class RequestRegionInfoPacket(object):
    ''' a template for a RequestRegionInfo packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RequestRegionInfo'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('RequestRegionInfo', args)

class LogFailedMoneyTransactionPacket(object):
    ''' a template for a LogFailedMoneyTransaction packet '''

    def __init__(self, TransactionDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LogFailedMoneyTransaction'

        if TransactionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.TransactionData = TransactionDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TransactionData', TransactionID=self.TransactionData['TransactionID'], TransactionTime=self.TransactionData['TransactionTime'], TransactionType=self.TransactionData['TransactionType'], SourceID=self.TransactionData['SourceID'], DestID=self.TransactionData['DestID'], Flags=self.TransactionData['Flags'], Amount=self.TransactionData['Amount'], SimulatorIP=self.TransactionData['SimulatorIP'], GridX=self.TransactionData['GridX'], GridY=self.TransactionData['GridY'], FailureType=self.TransactionData['FailureType']))

        return Message('LogFailedMoneyTransaction', args)

class GroupTitlesRequestPacket(object):
    ''' a template for a GroupTitlesRequest packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupTitlesRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
            self.AgentData['RequestID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID'], RequestID=self.AgentData['RequestID']))

        return Message('GroupTitlesRequest', args)

class ImprovedInstantMessagePacket(object):
    ''' a template for a ImprovedInstantMessage packet '''

    def __init__(self, AgentDataBlock = {}, MessageBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ImprovedInstantMessage'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MessageBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.MessageBlock = MessageBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('MessageBlock', FromGroup=self.MessageBlock['FromGroup'], ToAgentID=self.MessageBlock['ToAgentID'], ParentEstateID=self.MessageBlock['ParentEstateID'], RegionID=self.MessageBlock['RegionID'], Position=self.MessageBlock['Position'], Offline=self.MessageBlock['Offline'], Dialog=self.MessageBlock['Dialog'], ID=self.MessageBlock['ID'], Timestamp=self.MessageBlock['Timestamp'], FromAgentName=self.MessageBlock['FromAgentName'], Message=self.MessageBlock['Message'], BinaryBucket=self.MessageBlock['BinaryBucket']))

        return Message('ImprovedInstantMessage', args)

class ScriptDataRequestPacket(object):
    ''' a template for a ScriptDataRequest packet '''

    def __init__(self, DataBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptDataRequest'

        if DataBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.DataBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.DataBlock = {}
            self.DataBlock['Hash'] = None    # MVT_U64
            self.DataBlock['RequestType'] = None    # MVT_S8
            self.DataBlock['Request'] = None    # MVT_VARIABLE
        else:
            self.DataBlockBlocks = DataBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.DataBlockBlocks:
            args.append(Block('DataBlock', Hash=block['Hash'], RequestType=block['RequestType'], Request=block['Request']))

        return Message('ScriptDataRequest', args)

class ParcelAccessListReplyPacket(object):
    ''' a template for a ParcelAccessListReply packet '''

    def __init__(self, DataBlock = {}, ListBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelAccessListReply'

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['AgentID'] = None    # MVT_LLUUID
            self.Data['SequenceID'] = None    # MVT_S32
            self.Data['Flags'] = None    # MVT_U32
            self.Data['LocalID'] = None    # MVT_S32
        else:
            self.Data = DataBlock

        if ListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.List = {}
            self.List['ID'] = None    # MVT_LLUUID
            self.List['Time'] = None    # MVT_S32
            self.List['Flags'] = None    # MVT_U32
        else:
            self.ListBlocks = ListBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Data', AgentID=self.Data['AgentID'], SequenceID=self.Data['SequenceID'], Flags=self.Data['Flags'], LocalID=self.Data['LocalID']))
        for block in self.ListBlocks:
            args.append(Block('List', ID=block['ID'], Time=block['Time'], Flags=block['Flags']))

        return Message('ParcelAccessListReply', args)

class ObjectDeselectPacket(object):
    ''' a template for a ObjectDeselect packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectDeselect'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('ObjectDeselect', args)

class RequestMultipleObjectsPacket(object):
    ''' a template for a RequestMultipleObjects packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RequestMultipleObjects'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['CacheMissType'] = None    # MVT_U8
            self.ObjectData['ID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', CacheMissType=block['CacheMissType'], ID=block['ID']))

        return Message('RequestMultipleObjects', args)

class RoutedMoneyBalanceReplyPacket(object):
    ''' a template for a RoutedMoneyBalanceReply packet '''

    def __init__(self, TargetBlockBlock = {}, MoneyDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RoutedMoneyBalanceReply'

        if TargetBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TargetBlock = {}    # New TargetBlock block
            self.TargetBlock['TargetIP'] = None    # MVT_IP_ADDR
            self.TargetBlock['TargetPort'] = None    # MVT_IP_PORT
        else:
            self.TargetBlock = TargetBlockBlock

        if MoneyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MoneyData = {}    # New MoneyData block
            self.MoneyData['AgentID'] = None    # MVT_LLUUID
            self.MoneyData['TransactionID'] = None    # MVT_LLUUID
            self.MoneyData['TransactionSuccess'] = None    # MVT_BOOL
            self.MoneyData['MoneyBalance'] = None    # MVT_S32
            self.MoneyData['SquareMetersCredit'] = None    # MVT_S32
            self.MoneyData['SquareMetersCommitted'] = None    # MVT_S32
            self.MoneyData['Description'] = None    # MVT_VARIABLE
        else:
            self.MoneyData = MoneyDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TargetBlock', TargetIP=self.TargetBlock['TargetIP'], TargetPort=self.TargetBlock['TargetPort']))
        args.append(Block('MoneyData', AgentID=self.MoneyData['AgentID'], TransactionID=self.MoneyData['TransactionID'], TransactionSuccess=self.MoneyData['TransactionSuccess'], MoneyBalance=self.MoneyData['MoneyBalance'], SquareMetersCredit=self.MoneyData['SquareMetersCredit'], SquareMetersCommitted=self.MoneyData['SquareMetersCommitted'], Description=self.MoneyData['Description']))

        return Message('RoutedMoneyBalanceReply', args)

class LoadURLPacket(object):
    ''' a template for a LoadURL packet '''

    def __init__(self, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LoadURL'

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['ObjectName'] = None    # MVT_VARIABLE
            self.Data['ObjectID'] = None    # MVT_LLUUID
            self.Data['OwnerID'] = None    # MVT_LLUUID
            self.Data['OwnerIsGroup'] = None    # MVT_BOOL
            self.Data['Message'] = None    # MVT_VARIABLE
            self.Data['URL'] = None    # MVT_VARIABLE
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Data', ObjectName=self.Data['ObjectName'], ObjectID=self.Data['ObjectID'], OwnerID=self.Data['OwnerID'], OwnerIsGroup=self.Data['OwnerIsGroup'], Message=self.Data['Message'], URL=self.Data['URL']))

        return Message('LoadURL', args)

class RpcChannelReplyPacket(object):
    ''' a template for a RpcChannelReply packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RpcChannelReply'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['TaskID'] = None    # MVT_LLUUID
            self.DataBlock['ItemID'] = None    # MVT_LLUUID
            self.DataBlock['ChannelID'] = None    # MVT_LLUUID
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', TaskID=self.DataBlock['TaskID'], ItemID=self.DataBlock['ItemID'], ChannelID=self.DataBlock['ChannelID']))

        return Message('RpcChannelReply', args)

class TeleportStartPacket(object):
    ''' a template for a TeleportStart packet '''

    def __init__(self, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TeleportStart'

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['TeleportFlags'] = None    # MVT_U32
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Info', TeleportFlags=self.Info['TeleportFlags']))

        return Message('TeleportStart', args)

class RezObjectPacket(object):
    ''' a template for a RezObject packet '''

    def __init__(self, AgentDataBlock = {}, RezDataBlock = {}, InventoryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RezObject'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RezDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.RezData = RezDataBlock

        if InventoryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.InventoryData = InventoryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('RezData', FromTaskID=self.RezData['FromTaskID'], BypassRaycast=self.RezData['BypassRaycast'], RayStart=self.RezData['RayStart'], RayEnd=self.RezData['RayEnd'], RayTargetID=self.RezData['RayTargetID'], RayEndIsIntersection=self.RezData['RayEndIsIntersection'], RezSelected=self.RezData['RezSelected'], RemoveItem=self.RezData['RemoveItem'], ItemFlags=self.RezData['ItemFlags'], GroupMask=self.RezData['GroupMask'], EveryoneMask=self.RezData['EveryoneMask'], NextOwnerMask=self.RezData['NextOwnerMask']))
        args.append(Block('InventoryData', ItemID=self.InventoryData['ItemID'], FolderID=self.InventoryData['FolderID'], CreatorID=self.InventoryData['CreatorID'], OwnerID=self.InventoryData['OwnerID'], GroupID=self.InventoryData['GroupID'], BaseMask=self.InventoryData['BaseMask'], OwnerMask=self.InventoryData['OwnerMask'], GroupMask=self.InventoryData['GroupMask'], EveryoneMask=self.InventoryData['EveryoneMask'], NextOwnerMask=self.InventoryData['NextOwnerMask'], GroupOwned=self.InventoryData['GroupOwned'], TransactionID=self.InventoryData['TransactionID'], Type=self.InventoryData['Type'], InvType=self.InventoryData['InvType'], Flags=self.InventoryData['Flags'], SaleType=self.InventoryData['SaleType'], SalePrice=self.InventoryData['SalePrice'], Name=self.InventoryData['Name'], Description=self.InventoryData['Description'], CreationDate=self.InventoryData['CreationDate'], CRC=self.InventoryData['CRC']))

        return Message('RezObject', args)

class AvatarInterestsReplyPacket(object):
    ''' a template for a AvatarInterestsReply packet '''

    def __init__(self, AgentDataBlock = {}, PropertiesDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarInterestsReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['AvatarID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if PropertiesDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.PropertiesData = {}    # New PropertiesData block
            self.PropertiesData['WantToMask'] = None    # MVT_U32
            self.PropertiesData['WantToText'] = None    # MVT_VARIABLE
            self.PropertiesData['SkillsMask'] = None    # MVT_U32
            self.PropertiesData['SkillsText'] = None    # MVT_VARIABLE
            self.PropertiesData['LanguagesText'] = None    # MVT_VARIABLE
        else:
            self.PropertiesData = PropertiesDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], AvatarID=self.AgentData['AvatarID']))
        args.append(Block('PropertiesData', WantToMask=self.PropertiesData['WantToMask'], WantToText=self.PropertiesData['WantToText'], SkillsMask=self.PropertiesData['SkillsMask'], SkillsText=self.PropertiesData['SkillsText'], LanguagesText=self.PropertiesData['LanguagesText']))

        return Message('AvatarInterestsReply', args)

class ObjectUpdateCompressedPacket(object):
    ''' a template for a ObjectUpdateCompressed packet '''

    def __init__(self, RegionDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectUpdateCompressed'

        if RegionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionData = {}    # New RegionData block
            self.RegionData['RegionHandle'] = None    # MVT_U64
            self.RegionData['TimeDilation'] = None    # MVT_U16
        else:
            self.RegionData = RegionDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['UpdateFlags'] = None    # MVT_U32
            self.ObjectData['Data'] = None    # MVT_VARIABLE
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('RegionData', RegionHandle=self.RegionData['RegionHandle'], TimeDilation=self.RegionData['TimeDilation']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', UpdateFlags=block['UpdateFlags'], Data=block['Data']))

        return Message('ObjectUpdateCompressed', args)

class DirPopularQueryPacket(object):
    ''' a template for a DirPopularQuery packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirPopularQuery'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['QueryFlags'] = None    # MVT_U32
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], QueryFlags=self.QueryData['QueryFlags']))

        return Message('DirPopularQuery', args)

class ChangeInventoryItemFlagsPacket(object):
    ''' a template for a ChangeInventoryItemFlags packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ChangeInventoryItemFlags'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
            self.InventoryData['ItemID'] = None    # MVT_LLUUID
            self.InventoryData['Flags'] = None    # MVT_U32
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', ItemID=block['ItemID'], Flags=block['Flags']))

        return Message('ChangeInventoryItemFlags', args)

class SimulatorViewerTimeMessagePacket(object):
    ''' a template for a SimulatorViewerTimeMessage packet '''

    def __init__(self, TimeInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SimulatorViewerTimeMessage'

        if TimeInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TimeInfo = {}    # New TimeInfo block
            self.TimeInfo['UsecSinceStart'] = None    # MVT_U64
            self.TimeInfo['SecPerDay'] = None    # MVT_U32
            self.TimeInfo['SecPerYear'] = None    # MVT_U32
            self.TimeInfo['SunDirection'] = None    # MVT_LLVector3
            self.TimeInfo['SunPhase'] = None    # MVT_F32
            self.TimeInfo['SunAngVelocity'] = None    # MVT_LLVector3
        else:
            self.TimeInfo = TimeInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TimeInfo', UsecSinceStart=self.TimeInfo['UsecSinceStart'], SecPerDay=self.TimeInfo['SecPerDay'], SecPerYear=self.TimeInfo['SecPerYear'], SunDirection=self.TimeInfo['SunDirection'], SunPhase=self.TimeInfo['SunPhase'], SunAngVelocity=self.TimeInfo['SunAngVelocity']))

        return Message('SimulatorViewerTimeMessage', args)

class PlacesQueryPacket(object):
    ''' a template for a PlacesQuery packet '''

    def __init__(self, AgentDataBlock = {}, TransactionDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'PlacesQuery'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['QueryID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if TransactionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransactionData = {}    # New TransactionData block
            self.TransactionData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.TransactionData = TransactionDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryText'] = None    # MVT_VARIABLE
            self.QueryData['QueryFlags'] = None    # MVT_U32
            self.QueryData['Category'] = None    # MVT_S8
            self.QueryData['SimName'] = None    # MVT_VARIABLE
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], QueryID=self.AgentData['QueryID']))
        args.append(Block('TransactionData', TransactionID=self.TransactionData['TransactionID']))
        args.append(Block('QueryData', QueryText=self.QueryData['QueryText'], QueryFlags=self.QueryData['QueryFlags'], Category=self.QueryData['Category'], SimName=self.QueryData['SimName']))

        return Message('PlacesQuery', args)

class ActivateGroupPacket(object):
    ''' a template for a ActivateGroup packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ActivateGroup'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))

        return Message('ActivateGroup', args)

class SubscribeLoadPacket(object):
    ''' a template for a SubscribeLoad packet '''

    def __init__(self):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SubscribeLoad'

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []

        return Message('SubscribeLoad', args)

class EjectGroupMemberReplyPacket(object):
    ''' a template for a EjectGroupMemberReply packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}, EjectDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EjectGroupMemberReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
        else:
            self.GroupData = GroupDataBlock

        if EjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.EjectData = {}    # New EjectData block
            self.EjectData['Success'] = None    # MVT_BOOL
        else:
            self.EjectData = EjectDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID']))
        args.append(Block('EjectData', Success=self.EjectData['Success']))

        return Message('EjectGroupMemberReply', args)

class CheckParcelSalesPacket(object):
    ''' a template for a CheckParcelSales packet '''

    def __init__(self, RegionDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CheckParcelSales'

        if RegionDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.RegionDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.RegionData = {}
            self.RegionData['RegionHandle'] = None    # MVT_U64
        else:
            self.RegionDataBlocks = RegionDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.RegionDataBlocks:
            args.append(Block('RegionData', RegionHandle=block['RegionHandle']))

        return Message('CheckParcelSales', args)

class DerezContainerPacket(object):
    ''' a template for a DerezContainer packet '''

    def __init__(self, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DerezContainer'

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['ObjectID'] = None    # MVT_LLUUID
            self.Data['Delete'] = None    # MVT_BOOL
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Data', ObjectID=self.Data['ObjectID'], Delete=self.Data['Delete']))

        return Message('DerezContainer', args)

class ConfirmEnableSimulatorPacket(object):
    ''' a template for a ConfirmEnableSimulator packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ConfirmEnableSimulator'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('ConfirmEnableSimulator', args)

class SetStartLocationRequestPacket(object):
    ''' a template for a SetStartLocationRequest packet '''

    def __init__(self, AgentDataBlock = {}, StartLocationDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SetStartLocationRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if StartLocationDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.StartLocationData = {}    # New StartLocationData block
            self.StartLocationData['SimName'] = None    # MVT_VARIABLE
            self.StartLocationData['LocationID'] = None    # MVT_U32
            self.StartLocationData['LocationPos'] = None    # MVT_LLVector3
            self.StartLocationData['LocationLookAt'] = None    # MVT_LLVector3
        else:
            self.StartLocationData = StartLocationDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('StartLocationData', SimName=self.StartLocationData['SimName'], LocationID=self.StartLocationData['LocationID'], LocationPos=self.StartLocationData['LocationPos'], LocationLookAt=self.StartLocationData['LocationLookAt']))

        return Message('SetStartLocationRequest', args)

class EstateCovenantRequestPacket(object):
    ''' a template for a EstateCovenantRequest packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EstateCovenantRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('EstateCovenantRequest', args)

class ErrorPacket(object):
    ''' a template for a Error packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'Error'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['Code'] = None    # MVT_S32
            self.Data['Token'] = None    # MVT_VARIABLE
            self.Data['ID'] = None    # MVT_LLUUID
            self.Data['System'] = None    # MVT_VARIABLE
            self.Data['Message'] = None    # MVT_VARIABLE
            self.Data['Data'] = None    # MVT_VARIABLE
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('Data', Code=self.Data['Code'], Token=self.Data['Token'], ID=self.Data['ID'], System=self.Data['System'], Message=self.Data['Message'], Data=self.Data['Data']))

        return Message('Error', args)

class AgentFOVPacket(object):
    ''' a template for a AgentFOV packet '''

    def __init__(self, AgentDataBlock = {}, FOVBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentFOV'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['CircuitCode'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

        if FOVBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.FOVBlock = {}    # New FOVBlock block
            self.FOVBlock['GenCounter'] = None    # MVT_U32
            self.FOVBlock['VerticalAngle'] = None    # MVT_F32
        else:
            self.FOVBlock = FOVBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], CircuitCode=self.AgentData['CircuitCode']))
        args.append(Block('FOVBlock', GenCounter=self.FOVBlock['GenCounter'], VerticalAngle=self.FOVBlock['VerticalAngle']))

        return Message('AgentFOV', args)

class AcceptCallingCardPacket(object):
    ''' a template for a AcceptCallingCard packet '''

    def __init__(self, AgentDataBlock = {}, TransactionBlockBlock = {}, FolderDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AcceptCallingCard'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if TransactionBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransactionBlock = {}    # New TransactionBlock block
            self.TransactionBlock['TransactionID'] = None    # MVT_LLUUID
        else:
            self.TransactionBlock = TransactionBlockBlock

        if FolderDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.FolderDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.FolderData = {}
            self.FolderData['FolderID'] = None    # MVT_LLUUID
        else:
            self.FolderDataBlocks = FolderDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('TransactionBlock', TransactionID=self.TransactionBlock['TransactionID']))
        for block in self.FolderDataBlocks:
            args.append(Block('FolderData', FolderID=block['FolderID']))

        return Message('AcceptCallingCard', args)

class EventNotificationAddRequestPacket(object):
    ''' a template for a EventNotificationAddRequest packet '''

    def __init__(self, AgentDataBlock = {}, EventDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EventNotificationAddRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if EventDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.EventData = {}    # New EventData block
            self.EventData['EventID'] = None    # MVT_U32
        else:
            self.EventData = EventDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('EventData', EventID=self.EventData['EventID']))

        return Message('EventNotificationAddRequest', args)

class AgentUpdatePacket(object):
    ''' a template for a AgentUpdate packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], BodyRotation=self.AgentData['BodyRotation'], HeadRotation=self.AgentData['HeadRotation'], State=self.AgentData['State'], CameraCenter=self.AgentData['CameraCenter'], CameraAtAxis=self.AgentData['CameraAtAxis'], CameraLeftAxis=self.AgentData['CameraLeftAxis'], CameraUpAxis=self.AgentData['CameraUpAxis'], Far=self.AgentData['Far'], ControlFlags=self.AgentData['ControlFlags'], Flags=self.AgentData['Flags']))

        return Message('AgentUpdate', args)

class AgentCachedTextureResponsePacket(object):
    ''' a template for a AgentCachedTextureResponse packet '''

    def __init__(self, AgentDataBlock = {}, WearableDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentCachedTextureResponse'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['SerialNum'] = None    # MVT_S32
        else:
            self.AgentData = AgentDataBlock

        if WearableDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.WearableDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.WearableData = {}
            self.WearableData['TextureID'] = None    # MVT_LLUUID
            self.WearableData['TextureIndex'] = None    # MVT_U8
            self.WearableData['HostName'] = None    # MVT_VARIABLE
        else:
            self.WearableDataBlocks = WearableDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], SerialNum=self.AgentData['SerialNum']))
        for block in self.WearableDataBlocks:
            args.append(Block('WearableData', TextureID=block['TextureID'], TextureIndex=block['TextureIndex'], HostName=block['HostName']))

        return Message('AgentCachedTextureResponse', args)

class GroupNoticeRequestPacket(object):
    ''' a template for a GroupNoticeRequest packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupNoticeRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['GroupNoticeID'] = None    # MVT_LLUUID
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', GroupNoticeID=self.Data['GroupNoticeID']))

        return Message('GroupNoticeRequest', args)

class RemoveMuteListEntryPacket(object):
    ''' a template for a RemoveMuteListEntry packet '''

    def __init__(self, AgentDataBlock = {}, MuteDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RemoveMuteListEntry'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MuteDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MuteData = {}    # New MuteData block
            self.MuteData['MuteID'] = None    # MVT_LLUUID
            self.MuteData['MuteName'] = None    # MVT_VARIABLE
        else:
            self.MuteData = MuteDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('MuteData', MuteID=self.MuteData['MuteID'], MuteName=self.MuteData['MuteName']))

        return Message('RemoveMuteListEntry', args)

class SetFollowCamPropertiesPacket(object):
    ''' a template for a SetFollowCamProperties packet '''

    def __init__(self, ObjectDataBlock = {}, CameraPropertyBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SetFollowCamProperties'

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.ObjectData = ObjectDataBlock

        if CameraPropertyBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.CameraPropertyBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.CameraProperty = {}
            self.CameraProperty['Type'] = None    # MVT_S32
            self.CameraProperty['Value'] = None    # MVT_F32
        else:
            self.CameraPropertyBlocks = CameraPropertyBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ObjectData', ObjectID=self.ObjectData['ObjectID']))
        for block in self.CameraPropertyBlocks:
            args.append(Block('CameraProperty', Type=block['Type'], Value=block['Value']))

        return Message('SetFollowCamProperties', args)

class ChildAgentAlivePacket(object):
    ''' a template for a ChildAgentAlive packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ChildAgentAlive'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['RegionHandle'] = None    # MVT_U64
            self.AgentData['ViewerCircuitCode'] = None    # MVT_U32
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', RegionHandle=self.AgentData['RegionHandle'], ViewerCircuitCode=self.AgentData['ViewerCircuitCode'], AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('ChildAgentAlive', args)

class DirGroupsReplyPacket(object):
    ''' a template for a DirGroupsReply packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}, QueryRepliesBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirGroupsReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
        else:
            self.QueryData = QueryDataBlock

        if QueryRepliesBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.QueryRepliesBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.QueryReplies = {}
            self.QueryReplies['GroupID'] = None    # MVT_LLUUID
            self.QueryReplies['GroupName'] = None    # MVT_VARIABLE
            self.QueryReplies['Members'] = None    # MVT_S32
            self.QueryReplies['SearchOrder'] = None    # MVT_F32
        else:
            self.QueryRepliesBlocks = QueryRepliesBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID']))
        for block in self.QueryRepliesBlocks:
            args.append(Block('QueryReplies', GroupID=block['GroupID'], GroupName=block['GroupName'], Members=block['Members'], SearchOrder=block['SearchOrder']))

        return Message('DirGroupsReply', args)

class GroupTitleUpdatePacket(object):
    ''' a template for a GroupTitleUpdate packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupTitleUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
            self.AgentData['TitleRoleID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID'], TitleRoleID=self.AgentData['TitleRoleID']))

        return Message('GroupTitleUpdate', args)

class GroupAccountDetailsRequestPacket(object):
    ''' a template for a GroupAccountDetailsRequest packet '''

    def __init__(self, AgentDataBlock = {}, MoneyDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupAccountDetailsRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MoneyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MoneyData = {}    # New MoneyData block
            self.MoneyData['RequestID'] = None    # MVT_LLUUID
            self.MoneyData['IntervalDays'] = None    # MVT_S32
            self.MoneyData['CurrentInterval'] = None    # MVT_S32
        else:
            self.MoneyData = MoneyDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('MoneyData', RequestID=self.MoneyData['RequestID'], IntervalDays=self.MoneyData['IntervalDays'], CurrentInterval=self.MoneyData['CurrentInterval']))

        return Message('GroupAccountDetailsRequest', args)

class ParcelAuctionsPacket(object):
    ''' a template for a ParcelAuctions packet '''

    def __init__(self, ParcelDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelAuctions'

        if ParcelDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParcelDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParcelData = {}
            self.ParcelData['ParcelID'] = None    # MVT_LLUUID
            self.ParcelData['WinnerID'] = None    # MVT_LLUUID
        else:
            self.ParcelDataBlocks = ParcelDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.ParcelDataBlocks:
            args.append(Block('ParcelData', ParcelID=block['ParcelID'], WinnerID=block['WinnerID']))

        return Message('ParcelAuctions', args)

class ObjectDetachPacket(object):
    ''' a template for a ObjectDetach packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectDetach'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('ObjectDetach', args)

class AssetUploadRequestPacket(object):
    ''' a template for a AssetUploadRequest packet '''

    def __init__(self, AssetBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AssetUploadRequest'

        if AssetBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AssetBlock = {}    # New AssetBlock block
            self.AssetBlock['TransactionID'] = None    # MVT_LLUUID
            self.AssetBlock['Type'] = None    # MVT_S8
            self.AssetBlock['Tempfile'] = None    # MVT_BOOL
            self.AssetBlock['StoreLocal'] = None    # MVT_BOOL
            self.AssetBlock['AssetData'] = None    # MVT_VARIABLE
        else:
            self.AssetBlock = AssetBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AssetBlock', TransactionID=self.AssetBlock['TransactionID'], Type=self.AssetBlock['Type'], Tempfile=self.AssetBlock['Tempfile'], StoreLocal=self.AssetBlock['StoreLocal'], AssetData=self.AssetBlock['AssetData']))

        return Message('AssetUploadRequest', args)

class ParcelReleasePacket(object):
    ''' a template for a ParcelRelease packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelRelease'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['LocalID'] = None    # MVT_S32
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', LocalID=self.Data['LocalID']))

        return Message('ParcelRelease', args)

class RpcScriptRequestInboundForwardPacket(object):
    ''' a template for a RpcScriptRequestInboundForward packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RpcScriptRequestInboundForward'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['RPCServerIP'] = None    # MVT_IP_ADDR
            self.DataBlock['RPCServerPort'] = None    # MVT_IP_PORT
            self.DataBlock['TaskID'] = None    # MVT_LLUUID
            self.DataBlock['ItemID'] = None    # MVT_LLUUID
            self.DataBlock['ChannelID'] = None    # MVT_LLUUID
            self.DataBlock['IntValue'] = None    # MVT_U32
            self.DataBlock['StringValue'] = None    # MVT_VARIABLE
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', RPCServerIP=self.DataBlock['RPCServerIP'], RPCServerPort=self.DataBlock['RPCServerPort'], TaskID=self.DataBlock['TaskID'], ItemID=self.DataBlock['ItemID'], ChannelID=self.DataBlock['ChannelID'], IntValue=self.DataBlock['IntValue'], StringValue=self.DataBlock['StringValue']))

        return Message('RpcScriptRequestInboundForward', args)

class ObjectDuplicateOnRayPacket(object):
    ''' a template for a ObjectDuplicateOnRay packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectDuplicateOnRay'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID'], RayStart=self.AgentData['RayStart'], RayEnd=self.AgentData['RayEnd'], BypassRaycast=self.AgentData['BypassRaycast'], RayEndIsIntersection=self.AgentData['RayEndIsIntersection'], CopyCenters=self.AgentData['CopyCenters'], CopyRotates=self.AgentData['CopyRotates'], RayTargetID=self.AgentData['RayTargetID'], DuplicateFlags=self.AgentData['DuplicateFlags']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('ObjectDuplicateOnRay', args)

class MoneyTransferRequestPacket(object):
    ''' a template for a MoneyTransferRequest packet '''

    def __init__(self, AgentDataBlock = {}, MoneyDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MoneyTransferRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MoneyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MoneyData = {}    # New MoneyData block
            self.MoneyData['SourceID'] = None    # MVT_LLUUID
            self.MoneyData['DestID'] = None    # MVT_LLUUID
            self.MoneyData['Flags'] = None    # MVT_U8
            self.MoneyData['Amount'] = None    # MVT_S32
            self.MoneyData['AggregatePermNextOwner'] = None    # MVT_U8
            self.MoneyData['AggregatePermInventory'] = None    # MVT_U8
            self.MoneyData['TransactionType'] = None    # MVT_S32
            self.MoneyData['Description'] = None    # MVT_VARIABLE
        else:
            self.MoneyData = MoneyDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('MoneyData', SourceID=self.MoneyData['SourceID'], DestID=self.MoneyData['DestID'], Flags=self.MoneyData['Flags'], Amount=self.MoneyData['Amount'], AggregatePermNextOwner=self.MoneyData['AggregatePermNextOwner'], AggregatePermInventory=self.MoneyData['AggregatePermInventory'], TransactionType=self.MoneyData['TransactionType'], Description=self.MoneyData['Description']))

        return Message('MoneyTransferRequest', args)

class ScriptDialogPacket(object):
    ''' a template for a ScriptDialog packet '''

    def __init__(self, DataBlock = {}, ButtonsBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ScriptDialog'

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['ObjectID'] = None    # MVT_LLUUID
            self.Data['FirstName'] = None    # MVT_VARIABLE
            self.Data['LastName'] = None    # MVT_VARIABLE
            self.Data['ObjectName'] = None    # MVT_VARIABLE
            self.Data['Message'] = None    # MVT_VARIABLE
            self.Data['ChatChannel'] = None    # MVT_S32
            self.Data['ImageID'] = None    # MVT_LLUUID
        else:
            self.Data = DataBlock

        if ButtonsBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ButtonsBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.Buttons = {}
            self.Buttons['ButtonLabel'] = None    # MVT_VARIABLE
        else:
            self.ButtonsBlocks = ButtonsBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Data', ObjectID=self.Data['ObjectID'], FirstName=self.Data['FirstName'], LastName=self.Data['LastName'], ObjectName=self.Data['ObjectName'], Message=self.Data['Message'], ChatChannel=self.Data['ChatChannel'], ImageID=self.Data['ImageID']))
        for block in self.ButtonsBlocks:
            args.append(Block('Buttons', ButtonLabel=block['ButtonLabel']))

        return Message('ScriptDialog', args)

class RequestTrustedCircuitPacket(object):
    ''' a template for a RequestTrustedCircuit packet '''

    def __init__(self):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RequestTrustedCircuit'

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []

        return Message('RequestTrustedCircuit', args)

class TeleportFinishPacket(object):
    ''' a template for a TeleportFinish packet '''

    def __init__(self, InfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TeleportFinish'

        if InfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Info = {}    # New Info block
            self.Info['AgentID'] = None    # MVT_LLUUID
            self.Info['LocationID'] = None    # MVT_U32
            self.Info['SimIP'] = None    # MVT_IP_ADDR
            self.Info['SimPort'] = None    # MVT_IP_PORT
            self.Info['RegionHandle'] = None    # MVT_U64
            self.Info['SeedCapability'] = None    # MVT_VARIABLE
            self.Info['SimAccess'] = None    # MVT_U8
            self.Info['TeleportFlags'] = None    # MVT_U32
        else:
            self.Info = InfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Info', AgentID=self.Info['AgentID'], LocationID=self.Info['LocationID'], SimIP=self.Info['SimIP'], SimPort=self.Info['SimPort'], RegionHandle=self.Info['RegionHandle'], SeedCapability=self.Info['SeedCapability'], SimAccess=self.Info['SimAccess'], TeleportFlags=self.Info['TeleportFlags']))

        return Message('TeleportFinish', args)

class CreateInventoryFolderPacket(object):
    ''' a template for a CreateInventoryFolder packet '''

    def __init__(self, AgentDataBlock = {}, FolderDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CreateInventoryFolder'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if FolderDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.FolderData = {}    # New FolderData block
            self.FolderData['FolderID'] = None    # MVT_LLUUID
            self.FolderData['ParentID'] = None    # MVT_LLUUID
            self.FolderData['Type'] = None    # MVT_S8
            self.FolderData['Name'] = None    # MVT_VARIABLE
        else:
            self.FolderData = FolderDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('FolderData', FolderID=self.FolderData['FolderID'], ParentID=self.FolderData['ParentID'], Type=self.FolderData['Type'], Name=self.FolderData['Name']))

        return Message('CreateInventoryFolder', args)

class DisableSimulatorPacket(object):
    ''' a template for a DisableSimulator packet '''

    def __init__(self):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DisableSimulator'

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []

        return Message('DisableSimulator', args)

class TransferPacketPacket(object):
    ''' a template for a TransferPacket packet '''

    def __init__(self, TransferDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TransferPacket'

        if TransferDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TransferData = {}    # New TransferData block
            self.TransferData['TransferID'] = None    # MVT_LLUUID
            self.TransferData['ChannelType'] = None    # MVT_S32
            self.TransferData['Packet'] = None    # MVT_S32
            self.TransferData['Status'] = None    # MVT_S32
            self.TransferData['Data'] = None    # MVT_VARIABLE
        else:
            self.TransferData = TransferDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TransferData', TransferID=self.TransferData['TransferID'], ChannelType=self.TransferData['ChannelType'], Packet=self.TransferData['Packet'], Status=self.TransferData['Status'], Data=self.TransferData['Data']))

        return Message('TransferPacket', args)

class ClassifiedGodDeletePacket(object):
    ''' a template for a ClassifiedGodDelete packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ClassifiedGodDelete'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['ClassifiedID'] = None    # MVT_LLUUID
            self.Data['QueryID'] = None    # MVT_LLUUID
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', ClassifiedID=self.Data['ClassifiedID'], QueryID=self.Data['QueryID']))

        return Message('ClassifiedGodDelete', args)

class TrackAgentPacket(object):
    ''' a template for a TrackAgent packet '''

    def __init__(self, AgentDataBlock = {}, TargetDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TrackAgent'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if TargetDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TargetData = {}    # New TargetData block
            self.TargetData['PreyID'] = None    # MVT_LLUUID
        else:
            self.TargetData = TargetDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('TargetData', PreyID=self.TargetData['PreyID']))

        return Message('TrackAgent', args)

class SimulatorReadyPacket(object):
    ''' a template for a SimulatorReady packet '''

    def __init__(self, SimulatorBlockBlock = {}, TelehubBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SimulatorReady'

        if SimulatorBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.SimulatorBlock = {}    # New SimulatorBlock block
            self.SimulatorBlock['SimName'] = None    # MVT_VARIABLE
            self.SimulatorBlock['SimAccess'] = None    # MVT_U8
            self.SimulatorBlock['RegionFlags'] = None    # MVT_U32
            self.SimulatorBlock['RegionID'] = None    # MVT_LLUUID
            self.SimulatorBlock['EstateID'] = None    # MVT_U32
            self.SimulatorBlock['ParentEstateID'] = None    # MVT_U32
        else:
            self.SimulatorBlock = SimulatorBlockBlock

        if TelehubBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TelehubBlock = {}    # New TelehubBlock block
            self.TelehubBlock['HasTelehub'] = None    # MVT_BOOL
            self.TelehubBlock['TelehubPos'] = None    # MVT_LLVector3
        else:
            self.TelehubBlock = TelehubBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('SimulatorBlock', SimName=self.SimulatorBlock['SimName'], SimAccess=self.SimulatorBlock['SimAccess'], RegionFlags=self.SimulatorBlock['RegionFlags'], RegionID=self.SimulatorBlock['RegionID'], EstateID=self.SimulatorBlock['EstateID'], ParentEstateID=self.SimulatorBlock['ParentEstateID']))
        args.append(Block('TelehubBlock', HasTelehub=self.TelehubBlock['HasTelehub'], TelehubPos=self.TelehubBlock['TelehubPos']))

        return Message('SimulatorReady', args)

class GroupProposalBallotPacket(object):
    ''' a template for a GroupProposalBallot packet '''

    def __init__(self, AgentDataBlock = {}, ProposalDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupProposalBallot'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ProposalDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ProposalData = {}    # New ProposalData block
            self.ProposalData['ProposalID'] = None    # MVT_LLUUID
            self.ProposalData['GroupID'] = None    # MVT_LLUUID
            self.ProposalData['VoteCast'] = None    # MVT_VARIABLE
        else:
            self.ProposalData = ProposalDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ProposalData', ProposalID=self.ProposalData['ProposalID'], GroupID=self.ProposalData['GroupID'], VoteCast=self.ProposalData['VoteCast']))

        return Message('GroupProposalBallot', args)

class GetScriptRunningPacket(object):
    ''' a template for a GetScriptRunning packet '''

    def __init__(self, ScriptBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GetScriptRunning'

        if ScriptBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Script = {}    # New Script block
            self.Script['ObjectID'] = None    # MVT_LLUUID
            self.Script['ItemID'] = None    # MVT_LLUUID
        else:
            self.Script = ScriptBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('Script', ObjectID=self.Script['ObjectID'], ItemID=self.Script['ItemID']))

        return Message('GetScriptRunning', args)

class ObjectSpinStopPacket(object):
    ''' a template for a ObjectSpinStop packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectSpinStop'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.ObjectData = ObjectDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ObjectData', ObjectID=self.ObjectData['ObjectID']))

        return Message('ObjectSpinStop', args)

class GroupRoleChangesPacket(object):
    ''' a template for a GroupRoleChanges packet '''

    def __init__(self, AgentDataBlock = {}, RoleChangeBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupRoleChanges'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RoleChangeBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.RoleChangeBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.RoleChange = {}
            self.RoleChange['RoleID'] = None    # MVT_LLUUID
            self.RoleChange['MemberID'] = None    # MVT_LLUUID
            self.RoleChange['Change'] = None    # MVT_U32
        else:
            self.RoleChangeBlocks = RoleChangeBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        for block in self.RoleChangeBlocks:
            args.append(Block('RoleChange', RoleID=block['RoleID'], MemberID=block['MemberID'], Change=block['Change']))

        return Message('GroupRoleChanges', args)

class UpdateParcelPacket(object):
    ''' a template for a UpdateParcel packet '''

    def __init__(self, ParcelDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UpdateParcel'

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.ParcelData = ParcelDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ParcelData', ParcelID=self.ParcelData['ParcelID'], RegionHandle=self.ParcelData['RegionHandle'], OwnerID=self.ParcelData['OwnerID'], GroupOwned=self.ParcelData['GroupOwned'], Status=self.ParcelData['Status'], Name=self.ParcelData['Name'], Description=self.ParcelData['Description'], MusicURL=self.ParcelData['MusicURL'], RegionX=self.ParcelData['RegionX'], RegionY=self.ParcelData['RegionY'], ActualArea=self.ParcelData['ActualArea'], BillableArea=self.ParcelData['BillableArea'], ShowDir=self.ParcelData['ShowDir'], IsForSale=self.ParcelData['IsForSale'], Category=self.ParcelData['Category'], SnapshotID=self.ParcelData['SnapshotID'], UserLocation=self.ParcelData['UserLocation'], SalePrice=self.ParcelData['SalePrice'], AuthorizedBuyerID=self.ParcelData['AuthorizedBuyerID'], AllowPublish=self.ParcelData['AllowPublish'], MaturePublish=self.ParcelData['MaturePublish']))

        return Message('UpdateParcel', args)

class RezRestoreToWorldPacket(object):
    ''' a template for a RezRestoreToWorld packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RezRestoreToWorld'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.InventoryData = InventoryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('InventoryData', ItemID=self.InventoryData['ItemID'], FolderID=self.InventoryData['FolderID'], CreatorID=self.InventoryData['CreatorID'], OwnerID=self.InventoryData['OwnerID'], GroupID=self.InventoryData['GroupID'], BaseMask=self.InventoryData['BaseMask'], OwnerMask=self.InventoryData['OwnerMask'], GroupMask=self.InventoryData['GroupMask'], EveryoneMask=self.InventoryData['EveryoneMask'], NextOwnerMask=self.InventoryData['NextOwnerMask'], GroupOwned=self.InventoryData['GroupOwned'], TransactionID=self.InventoryData['TransactionID'], Type=self.InventoryData['Type'], InvType=self.InventoryData['InvType'], Flags=self.InventoryData['Flags'], SaleType=self.InventoryData['SaleType'], SalePrice=self.InventoryData['SalePrice'], Name=self.InventoryData['Name'], Description=self.InventoryData['Description'], CreationDate=self.InventoryData['CreationDate'], CRC=self.InventoryData['CRC']))

        return Message('RezRestoreToWorld', args)

class ObjectOwnerPacket(object):
    ''' a template for a ObjectOwner packet '''

    def __init__(self, AgentDataBlock = {}, HeaderDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectOwner'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if HeaderDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.HeaderData = {}    # New HeaderData block
            self.HeaderData['Override'] = None    # MVT_BOOL
            self.HeaderData['OwnerID'] = None    # MVT_LLUUID
            self.HeaderData['GroupID'] = None    # MVT_LLUUID
        else:
            self.HeaderData = HeaderDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('HeaderData', Override=self.HeaderData['Override'], OwnerID=self.HeaderData['OwnerID'], GroupID=self.HeaderData['GroupID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('ObjectOwner', args)

class RezScriptPacket(object):
    ''' a template for a RezScript packet '''

    def __init__(self, AgentDataBlock = {}, UpdateBlockBlock = {}, InventoryBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RezScript'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if UpdateBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.UpdateBlock = {}    # New UpdateBlock block
            self.UpdateBlock['ObjectLocalID'] = None    # MVT_U32
            self.UpdateBlock['Enabled'] = None    # MVT_BOOL
        else:
            self.UpdateBlock = UpdateBlockBlock

        if InventoryBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.InventoryBlock = InventoryBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], GroupID=self.AgentData['GroupID']))
        args.append(Block('UpdateBlock', ObjectLocalID=self.UpdateBlock['ObjectLocalID'], Enabled=self.UpdateBlock['Enabled']))
        args.append(Block('InventoryBlock', ItemID=self.InventoryBlock['ItemID'], FolderID=self.InventoryBlock['FolderID'], CreatorID=self.InventoryBlock['CreatorID'], OwnerID=self.InventoryBlock['OwnerID'], GroupID=self.InventoryBlock['GroupID'], BaseMask=self.InventoryBlock['BaseMask'], OwnerMask=self.InventoryBlock['OwnerMask'], GroupMask=self.InventoryBlock['GroupMask'], EveryoneMask=self.InventoryBlock['EveryoneMask'], NextOwnerMask=self.InventoryBlock['NextOwnerMask'], GroupOwned=self.InventoryBlock['GroupOwned'], TransactionID=self.InventoryBlock['TransactionID'], Type=self.InventoryBlock['Type'], InvType=self.InventoryBlock['InvType'], Flags=self.InventoryBlock['Flags'], SaleType=self.InventoryBlock['SaleType'], SalePrice=self.InventoryBlock['SalePrice'], Name=self.InventoryBlock['Name'], Description=self.InventoryBlock['Description'], CreationDate=self.InventoryBlock['CreationDate'], CRC=self.InventoryBlock['CRC']))

        return Message('RezScript', args)

class ParcelReturnObjectsPacket(object):
    ''' a template for a ParcelReturnObjects packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}, TaskIDsBlocks = [], OwnerIDsBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelReturnObjects'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['LocalID'] = None    # MVT_S32
            self.ParcelData['ReturnType'] = None    # MVT_U32
        else:
            self.ParcelData = ParcelDataBlock

        if TaskIDsBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.TaskIDsBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.TaskIDs = {}
            self.TaskIDs['TaskID'] = None    # MVT_LLUUID
        else:
            self.TaskIDsBlocks = TaskIDsBlocks

        if OwnerIDsBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.OwnerIDsBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.OwnerIDs = {}
            self.OwnerIDs['OwnerID'] = None    # MVT_LLUUID
        else:
            self.OwnerIDsBlocks = OwnerIDsBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', LocalID=self.ParcelData['LocalID'], ReturnType=self.ParcelData['ReturnType']))
        for block in self.TaskIDsBlocks:
            args.append(Block('TaskIDs', TaskID=block['TaskID']))
        for block in self.OwnerIDsBlocks:
            args.append(Block('OwnerIDs', OwnerID=block['OwnerID']))

        return Message('ParcelReturnObjects', args)

class InitiateDownloadPacket(object):
    ''' a template for a InitiateDownload packet '''

    def __init__(self, AgentDataBlock = {}, FileDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'InitiateDownload'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if FileDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.FileData = {}    # New FileData block
            self.FileData['SimFilename'] = None    # MVT_VARIABLE
            self.FileData['ViewerFilename'] = None    # MVT_VARIABLE
        else:
            self.FileData = FileDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('FileData', SimFilename=self.FileData['SimFilename'], ViewerFilename=self.FileData['ViewerFilename']))

        return Message('InitiateDownload', args)

class AgentPausePacket(object):
    ''' a template for a AgentPause packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentPause'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['SerialNum'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], SerialNum=self.AgentData['SerialNum']))

        return Message('AgentPause', args)

class RequestInventoryAssetPacket(object):
    ''' a template for a RequestInventoryAsset packet '''

    def __init__(self, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RequestInventoryAsset'

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['AgentID'] = None    # MVT_LLUUID
            self.QueryData['OwnerID'] = None    # MVT_LLUUID
            self.QueryData['ItemID'] = None    # MVT_LLUUID
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], AgentID=self.QueryData['AgentID'], OwnerID=self.QueryData['OwnerID'], ItemID=self.QueryData['ItemID']))

        return Message('RequestInventoryAsset', args)

class RequestPayPricePacket(object):
    ''' a template for a RequestPayPrice packet '''

    def __init__(self, ObjectDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RequestPayPrice'

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.ObjectData = ObjectDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ObjectData', ObjectID=self.ObjectData['ObjectID']))

        return Message('RequestPayPrice', args)

class RequestImagePacket(object):
    ''' a template for a RequestImage packet '''

    def __init__(self, AgentDataBlock = {}, RequestImageBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RequestImage'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RequestImageBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.RequestImageBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.RequestImage = {}
            self.RequestImage['Image'] = None    # MVT_LLUUID
            self.RequestImage['DiscardLevel'] = None    # MVT_S8
            self.RequestImage['DownloadPriority'] = None    # MVT_F32
            self.RequestImage['Packet'] = None    # MVT_U32
            self.RequestImage['Type'] = None    # MVT_U8
        else:
            self.RequestImageBlocks = RequestImageBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.RequestImageBlocks:
            args.append(Block('RequestImage', Image=block['Image'], DiscardLevel=block['DiscardLevel'], DownloadPriority=block['DownloadPriority'], Packet=block['Packet'], Type=block['Type']))

        return Message('RequestImage', args)

class DirClassifiedQueryBackendPacket(object):
    ''' a template for a DirClassifiedQueryBackend packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirClassifiedQueryBackend'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['QueryText'] = None    # MVT_VARIABLE
            self.QueryData['QueryFlags'] = None    # MVT_U32
            self.QueryData['Category'] = None    # MVT_U32
            self.QueryData['EstateID'] = None    # MVT_U32
            self.QueryData['Godlike'] = None    # MVT_BOOL
            self.QueryData['QueryStart'] = None    # MVT_S32
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], QueryText=self.QueryData['QueryText'], QueryFlags=self.QueryData['QueryFlags'], Category=self.QueryData['Category'], EstateID=self.QueryData['EstateID'], Godlike=self.QueryData['Godlike'], QueryStart=self.QueryData['QueryStart']))

        return Message('DirClassifiedQueryBackend', args)

class EstateOwnerMessagePacket(object):
    ''' a template for a EstateOwnerMessage packet '''

    def __init__(self, AgentDataBlock = {}, MethodDataBlock = {}, ParamListBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EstateOwnerMessage'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MethodDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MethodData = {}    # New MethodData block
            self.MethodData['Method'] = None    # MVT_VARIABLE
            self.MethodData['Invoice'] = None    # MVT_LLUUID
        else:
            self.MethodData = MethodDataBlock

        if ParamListBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ParamListBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ParamList = {}
            self.ParamList['Parameter'] = None    # MVT_VARIABLE
        else:
            self.ParamListBlocks = ParamListBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], TransactionID=self.AgentData['TransactionID']))
        args.append(Block('MethodData', Method=self.MethodData['Method'], Invoice=self.MethodData['Invoice']))
        for block in self.ParamListBlocks:
            args.append(Block('ParamList', Parameter=block['Parameter']))

        return Message('EstateOwnerMessage', args)

class ChatFromSimulatorPacket(object):
    ''' a template for a ChatFromSimulator packet '''

    def __init__(self, ChatDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ChatFromSimulator'

        if ChatDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ChatData = {}    # New ChatData block
            self.ChatData['FromName'] = None    # MVT_VARIABLE
            self.ChatData['SourceID'] = None    # MVT_LLUUID
            self.ChatData['OwnerID'] = None    # MVT_LLUUID
            self.ChatData['SourceType'] = None    # MVT_U8
            self.ChatData['ChatType'] = None    # MVT_U8
            self.ChatData['Audible'] = None    # MVT_U8
            self.ChatData['Position'] = None    # MVT_LLVector3
            self.ChatData['Message'] = None    # MVT_VARIABLE
        else:
            self.ChatData = ChatDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ChatData', FromName=self.ChatData['FromName'], SourceID=self.ChatData['SourceID'], OwnerID=self.ChatData['OwnerID'], SourceType=self.ChatData['SourceType'], ChatType=self.ChatData['ChatType'], Audible=self.ChatData['Audible'], Position=self.ChatData['Position'], Message=self.ChatData['Message']))

        return Message('ChatFromSimulator', args)

class LogDwellTimePacket(object):
    ''' a template for a LogDwellTime packet '''

    def __init__(self, DwellInfoBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LogDwellTime'

        if DwellInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DwellInfo = {}    # New DwellInfo block
            self.DwellInfo['AgentID'] = None    # MVT_LLUUID
            self.DwellInfo['SessionID'] = None    # MVT_LLUUID
            self.DwellInfo['Duration'] = None    # MVT_F32
            self.DwellInfo['SimName'] = None    # MVT_VARIABLE
            self.DwellInfo['RegionX'] = None    # MVT_U32
            self.DwellInfo['RegionY'] = None    # MVT_U32
            self.DwellInfo['AvgAgentsInView'] = None    # MVT_U8
            self.DwellInfo['AvgViewerFPS'] = None    # MVT_U8
        else:
            self.DwellInfo = DwellInfoBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DwellInfo', AgentID=self.DwellInfo['AgentID'], SessionID=self.DwellInfo['SessionID'], Duration=self.DwellInfo['Duration'], SimName=self.DwellInfo['SimName'], RegionX=self.DwellInfo['RegionX'], RegionY=self.DwellInfo['RegionY'], AvgAgentsInView=self.DwellInfo['AvgAgentsInView'], AvgViewerFPS=self.DwellInfo['AvgViewerFPS']))

        return Message('LogDwellTime', args)

class GroupRoleMembersRequestPacket(object):
    ''' a template for a GroupRoleMembersRequest packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupRoleMembersRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
            self.GroupData['RequestID'] = None    # MVT_LLUUID
        else:
            self.GroupData = GroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID'], RequestID=self.GroupData['RequestID']))

        return Message('GroupRoleMembersRequest', args)

class LogoutRequestPacket(object):
    ''' a template for a LogoutRequest packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LogoutRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('LogoutRequest', args)

class GroupProfileRequestPacket(object):
    ''' a template for a GroupProfileRequest packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupProfileRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
        else:
            self.GroupData = GroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID']))

        return Message('GroupProfileRequest', args)

class ConfirmAuctionStartPacket(object):
    ''' a template for a ConfirmAuctionStart packet '''

    def __init__(self, AuctionDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ConfirmAuctionStart'

        if AuctionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AuctionData = {}    # New AuctionData block
            self.AuctionData['ParcelID'] = None    # MVT_LLUUID
            self.AuctionData['AuctionID'] = None    # MVT_U32
        else:
            self.AuctionData = AuctionDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AuctionData', ParcelID=self.AuctionData['ParcelID'], AuctionID=self.AuctionData['AuctionID']))

        return Message('ConfirmAuctionStart', args)

class ObjectCategoryPacket(object):
    ''' a template for a ObjectCategory packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectCategory'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['LocalID'] = None    # MVT_U32
            self.ObjectData['Category'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', LocalID=block['LocalID'], Category=block['Category']))

        return Message('ObjectCategory', args)

class RequestObjectPropertiesFamilyPacket(object):
    ''' a template for a RequestObjectPropertiesFamily packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RequestObjectPropertiesFamily'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['RequestFlags'] = None    # MVT_U32
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
        else:
            self.ObjectData = ObjectDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ObjectData', RequestFlags=self.ObjectData['RequestFlags'], ObjectID=self.ObjectData['ObjectID']))

        return Message('RequestObjectPropertiesFamily', args)

class MoneyBalanceRequestPacket(object):
    ''' a template for a MoneyBalanceRequest packet '''

    def __init__(self, AgentDataBlock = {}, MoneyDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'MoneyBalanceRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if MoneyDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MoneyData = {}    # New MoneyData block
            self.MoneyData['TransactionID'] = None    # MVT_LLUUID
        else:
            self.MoneyData = MoneyDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('MoneyData', TransactionID=self.MoneyData['TransactionID']))

        return Message('MoneyBalanceRequest', args)

class ForceScriptControlReleasePacket(object):
    ''' a template for a ForceScriptControlRelease packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ForceScriptControlRelease'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('ForceScriptControlRelease', args)

class SendPostcardPacket(object):
    ''' a template for a SendPostcard packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SendPostcard'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], AssetID=self.AgentData['AssetID'], PosGlobal=self.AgentData['PosGlobal'], To=self.AgentData['To'], From=self.AgentData['From'], Name=self.AgentData['Name'], Subject=self.AgentData['Subject'], Msg=self.AgentData['Msg'], AllowPublish=self.AgentData['AllowPublish'], MaturePublish=self.AgentData['MaturePublish']))

        return Message('SendPostcard', args)

class RebakeAvatarTexturesPacket(object):
    ''' a template for a RebakeAvatarTextures packet '''

    def __init__(self, TextureDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RebakeAvatarTextures'

        if TextureDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TextureData = {}    # New TextureData block
            self.TextureData['TextureID'] = None    # MVT_LLUUID
        else:
            self.TextureData = TextureDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TextureData', TextureID=self.TextureData['TextureID']))

        return Message('RebakeAvatarTextures', args)

class DeRezObjectPacket(object):
    ''' a template for a DeRezObject packet '''

    def __init__(self, AgentDataBlock = {}, AgentBlockBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DeRezObject'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if AgentBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentBlock = {}    # New AgentBlock block
            self.AgentBlock['GroupID'] = None    # MVT_LLUUID
            self.AgentBlock['Destination'] = None    # MVT_U8
            self.AgentBlock['DestinationID'] = None    # MVT_LLUUID
            self.AgentBlock['TransactionID'] = None    # MVT_LLUUID
            self.AgentBlock['PacketCount'] = None    # MVT_U8
            self.AgentBlock['PacketNumber'] = None    # MVT_U8
        else:
            self.AgentBlock = AgentBlockBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['ObjectLocalID'] = None    # MVT_U32
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('AgentBlock', GroupID=self.AgentBlock['GroupID'], Destination=self.AgentBlock['Destination'], DestinationID=self.AgentBlock['DestinationID'], TransactionID=self.AgentBlock['TransactionID'], PacketCount=self.AgentBlock['PacketCount'], PacketNumber=self.AgentBlock['PacketNumber']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', ObjectLocalID=block['ObjectLocalID']))

        return Message('DeRezObject', args)

class AvatarPropertiesRequestBackendPacket(object):
    ''' a template for a AvatarPropertiesRequestBackend packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarPropertiesRequestBackend'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['AvatarID'] = None    # MVT_LLUUID
            self.AgentData['GodLevel'] = None    # MVT_U8
            self.AgentData['WebProfilesDisabled'] = None    # MVT_BOOL
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], AvatarID=self.AgentData['AvatarID'], GodLevel=self.AgentData['GodLevel'], WebProfilesDisabled=self.AgentData['WebProfilesDisabled']))

        return Message('AvatarPropertiesRequestBackend', args)

class ImprovedTerseObjectUpdatePacket(object):
    ''' a template for a ImprovedTerseObjectUpdate packet '''

    def __init__(self, RegionDataBlock = {}, ObjectDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ImprovedTerseObjectUpdate'

        if RegionDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionData = {}    # New RegionData block
            self.RegionData['RegionHandle'] = None    # MVT_U64
            self.RegionData['TimeDilation'] = None    # MVT_U16
        else:
            self.RegionData = RegionDataBlock

        if ObjectDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ObjectDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ObjectData = {}
            self.ObjectData['Data'] = None    # MVT_VARIABLE
            self.ObjectData['TextureEntry'] = None    # MVT_VARIABLE
        else:
            self.ObjectDataBlocks = ObjectDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('RegionData', RegionHandle=self.RegionData['RegionHandle'], TimeDilation=self.RegionData['TimeDilation']))
        for block in self.ObjectDataBlocks:
            args.append(Block('ObjectData', Data=block['Data'], TextureEntry=block['TextureEntry']))

        return Message('ImprovedTerseObjectUpdate', args)

class AgentDropGroupPacket(object):
    ''' a template for a AgentDropGroup packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentDropGroup'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['GroupID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], GroupID=self.AgentData['GroupID']))

        return Message('AgentDropGroup', args)

class DirLandQueryBackendPacket(object):
    ''' a template for a DirLandQueryBackend packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirLandQueryBackend'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
            self.QueryData['QueryFlags'] = None    # MVT_U32
            self.QueryData['SearchType'] = None    # MVT_U32
            self.QueryData['Price'] = None    # MVT_S32
            self.QueryData['Area'] = None    # MVT_S32
            self.QueryData['QueryStart'] = None    # MVT_S32
            self.QueryData['EstateID'] = None    # MVT_U32
            self.QueryData['Godlike'] = None    # MVT_BOOL
        else:
            self.QueryData = QueryDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID'], QueryFlags=self.QueryData['QueryFlags'], SearchType=self.QueryData['SearchType'], Price=self.QueryData['Price'], Area=self.QueryData['Area'], QueryStart=self.QueryData['QueryStart'], EstateID=self.QueryData['EstateID'], Godlike=self.QueryData['Godlike']))

        return Message('DirLandQueryBackend', args)

class CopyInventoryItemPacket(object):
    ''' a template for a CopyInventoryItem packet '''

    def __init__(self, AgentDataBlock = {}, InventoryDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'CopyInventoryItem'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if InventoryDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.InventoryDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.InventoryData = {}
            self.InventoryData['CallbackID'] = None    # MVT_U32
            self.InventoryData['OldAgentID'] = None    # MVT_LLUUID
            self.InventoryData['OldItemID'] = None    # MVT_LLUUID
            self.InventoryData['NewFolderID'] = None    # MVT_LLUUID
            self.InventoryData['NewName'] = None    # MVT_VARIABLE
        else:
            self.InventoryDataBlocks = InventoryDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        for block in self.InventoryDataBlocks:
            args.append(Block('InventoryData', CallbackID=block['CallbackID'], OldAgentID=block['OldAgentID'], OldItemID=block['OldItemID'], NewFolderID=block['NewFolderID'], NewName=block['NewName']))

        return Message('CopyInventoryItem', args)

class RegionHandshakePacket(object):
    ''' a template for a RegionHandshake packet '''

    def __init__(self, RegionInfoBlock = {}, RegionInfo2Block = {}, RegionInfo3Block = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'RegionHandshake'

        if RegionInfoBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.RegionInfo = RegionInfoBlock

        if RegionInfo2Block == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionInfo2 = {}    # New RegionInfo2 block
            self.RegionInfo2['RegionID'] = None    # MVT_LLUUID
        else:
            self.RegionInfo2 = RegionInfo2Block

        if RegionInfo3Block == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RegionInfo3 = {}    # New RegionInfo3 block
            self.RegionInfo3['CPUClassID'] = None    # MVT_S32
            self.RegionInfo3['CPURatio'] = None    # MVT_S32
            self.RegionInfo3['ColoName'] = None    # MVT_VARIABLE
            self.RegionInfo3['ProductSKU'] = None    # MVT_VARIABLE
            self.RegionInfo3['ProductName'] = None    # MVT_VARIABLE
        else:
            self.RegionInfo3 = RegionInfo3Block

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('RegionInfo', RegionFlags=self.RegionInfo['RegionFlags'], SimAccess=self.RegionInfo['SimAccess'], SimName=self.RegionInfo['SimName'], SimOwner=self.RegionInfo['SimOwner'], IsEstateManager=self.RegionInfo['IsEstateManager'], WaterHeight=self.RegionInfo['WaterHeight'], BillableFactor=self.RegionInfo['BillableFactor'], CacheID=self.RegionInfo['CacheID'], TerrainBase0=self.RegionInfo['TerrainBase0'], TerrainBase1=self.RegionInfo['TerrainBase1'], TerrainBase2=self.RegionInfo['TerrainBase2'], TerrainBase3=self.RegionInfo['TerrainBase3'], TerrainDetail0=self.RegionInfo['TerrainDetail0'], TerrainDetail1=self.RegionInfo['TerrainDetail1'], TerrainDetail2=self.RegionInfo['TerrainDetail2'], TerrainDetail3=self.RegionInfo['TerrainDetail3'], TerrainStartHeight00=self.RegionInfo['TerrainStartHeight00'], TerrainStartHeight01=self.RegionInfo['TerrainStartHeight01'], TerrainStartHeight10=self.RegionInfo['TerrainStartHeight10'], TerrainStartHeight11=self.RegionInfo['TerrainStartHeight11'], TerrainHeightRange00=self.RegionInfo['TerrainHeightRange00'], TerrainHeightRange01=self.RegionInfo['TerrainHeightRange01'], TerrainHeightRange10=self.RegionInfo['TerrainHeightRange10'], TerrainHeightRange11=self.RegionInfo['TerrainHeightRange11']))
        args.append(Block('RegionInfo2', RegionID=self.RegionInfo2['RegionID']))
        args.append(Block('RegionInfo3', CPUClassID=self.RegionInfo3['CPUClassID'], CPURatio=self.RegionInfo3['CPURatio'], ColoName=self.RegionInfo3['ColoName'], ProductSKU=self.RegionInfo3['ProductSKU'], ProductName=self.RegionInfo3['ProductName']))

        return Message('RegionHandshake', args)

class AvatarPickerRequestBackendPacket(object):
    ''' a template for a AvatarPickerRequestBackend packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AvatarPickerRequestBackend'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['QueryID'] = None    # MVT_LLUUID
            self.AgentData['GodLevel'] = None    # MVT_U8
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['Name'] = None    # MVT_VARIABLE
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], QueryID=self.AgentData['QueryID'], GodLevel=self.AgentData['GodLevel']))
        args.append(Block('Data', Name=self.Data['Name']))

        return Message('AvatarPickerRequestBackend', args)

class AgentWearablesUpdatePacket(object):
    ''' a template for a AgentWearablesUpdate packet '''

    def __init__(self, AgentDataBlock = {}, WearableDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentWearablesUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
            self.AgentData['SerialNum'] = None    # MVT_U32
        else:
            self.AgentData = AgentDataBlock

        if WearableDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.WearableDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.WearableData = {}
            self.WearableData['ItemID'] = None    # MVT_LLUUID
            self.WearableData['AssetID'] = None    # MVT_LLUUID
            self.WearableData['WearableType'] = None    # MVT_U8
        else:
            self.WearableDataBlocks = WearableDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID'], SerialNum=self.AgentData['SerialNum']))
        for block in self.WearableDataBlocks:
            args.append(Block('WearableData', ItemID=block['ItemID'], AssetID=block['AssetID'], WearableType=block['WearableType']))

        return Message('AgentWearablesUpdate', args)

class SimulatorMapUpdatePacket(object):
    ''' a template for a SimulatorMapUpdate packet '''

    def __init__(self, MapDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'SimulatorMapUpdate'

        if MapDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.MapData = {}    # New MapData block
            self.MapData['Flags'] = None    # MVT_U32
        else:
            self.MapData = MapDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('MapData', Flags=self.MapData['Flags']))

        return Message('SimulatorMapUpdate', args)

class JoinGroupReplyPacket(object):
    ''' a template for a JoinGroupReply packet '''

    def __init__(self, AgentDataBlock = {}, GroupDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'JoinGroupReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if GroupDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.GroupData = {}    # New GroupData block
            self.GroupData['GroupID'] = None    # MVT_LLUUID
            self.GroupData['Success'] = None    # MVT_BOOL
        else:
            self.GroupData = GroupDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('GroupData', GroupID=self.GroupData['GroupID'], Success=self.GroupData['Success']))

        return Message('JoinGroupReply', args)

class ChatPassPacket(object):
    ''' a template for a ChatPass packet '''

    def __init__(self, ChatDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ChatPass'

        if ChatDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.ChatData = ChatDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ChatData', Channel=self.ChatData['Channel'], Position=self.ChatData['Position'], ID=self.ChatData['ID'], OwnerID=self.ChatData['OwnerID'], Name=self.ChatData['Name'], SourceType=self.ChatData['SourceType'], Type=self.ChatData['Type'], Radius=self.ChatData['Radius'], SimAccess=self.ChatData['SimAccess'], Message=self.ChatData['Message']))

        return Message('ChatPass', args)

class ObjectGrabUpdatePacket(object):
    ''' a template for a ObjectGrabUpdate packet '''

    def __init__(self, AgentDataBlock = {}, ObjectDataBlock = {}, SurfaceInfoBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectGrabUpdate'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ObjectData = {}    # New ObjectData block
            self.ObjectData['ObjectID'] = None    # MVT_LLUUID
            self.ObjectData['GrabOffsetInitial'] = None    # MVT_LLVector3
            self.ObjectData['GrabPosition'] = None    # MVT_LLVector3
            self.ObjectData['TimeSinceLast'] = None    # MVT_U32
        else:
            self.ObjectData = ObjectDataBlock

        if SurfaceInfoBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.SurfaceInfoBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.SurfaceInfo = {}
            self.SurfaceInfo['UVCoord'] = None    # MVT_LLVector3
            self.SurfaceInfo['STCoord'] = None    # MVT_LLVector3
        else:
            self.SurfaceInfoBlocks = SurfaceInfoBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ObjectData', ObjectID=self.ObjectData['ObjectID'], GrabOffsetInitial=self.ObjectData['GrabOffsetInitial'], GrabPosition=self.ObjectData['GrabPosition'], TimeSinceLast=self.ObjectData['TimeSinceLast']))
        for block in self.SurfaceInfoBlocks:
            args.append(Block('SurfaceInfo', UVCoord=block['UVCoord'], STCoord=block['STCoord']))

        return Message('ObjectGrabUpdate', args)

class ObjectPropertiesFamilyPacket(object):
    ''' a template for a ObjectPropertiesFamily packet '''

    def __init__(self, ObjectDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ObjectPropertiesFamily'

        if ObjectDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
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
        else:
            self.ObjectData = ObjectDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('ObjectData', RequestFlags=self.ObjectData['RequestFlags'], ObjectID=self.ObjectData['ObjectID'], OwnerID=self.ObjectData['OwnerID'], GroupID=self.ObjectData['GroupID'], BaseMask=self.ObjectData['BaseMask'], OwnerMask=self.ObjectData['OwnerMask'], GroupMask=self.ObjectData['GroupMask'], EveryoneMask=self.ObjectData['EveryoneMask'], NextOwnerMask=self.ObjectData['NextOwnerMask'], OwnershipCost=self.ObjectData['OwnershipCost'], SaleType=self.ObjectData['SaleType'], SalePrice=self.ObjectData['SalePrice'], Category=self.ObjectData['Category'], LastOwnerID=self.ObjectData['LastOwnerID'], Name=self.ObjectData['Name'], Description=self.ObjectData['Description']))

        return Message('ObjectPropertiesFamily', args)

class OnlineNotificationPacket(object):
    ''' a template for a OnlineNotification packet '''

    def __init__(self, AgentBlockBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'OnlineNotification'

        if AgentBlockBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.AgentBlockBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.AgentBlock = {}
            self.AgentBlock['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentBlockBlocks = AgentBlockBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        for block in self.AgentBlockBlocks:
            args.append(Block('AgentBlock', AgentID=block['AgentID']))

        return Message('OnlineNotification', args)

class ParcelDisableObjectsPacket(object):
    ''' a template for a ParcelDisableObjects packet '''

    def __init__(self, AgentDataBlock = {}, ParcelDataBlock = {}, TaskIDsBlocks = [], OwnerIDsBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ParcelDisableObjects'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ParcelDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ParcelData = {}    # New ParcelData block
            self.ParcelData['LocalID'] = None    # MVT_S32
            self.ParcelData['ReturnType'] = None    # MVT_U32
        else:
            self.ParcelData = ParcelDataBlock

        if TaskIDsBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.TaskIDsBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.TaskIDs = {}
            self.TaskIDs['TaskID'] = None    # MVT_LLUUID
        else:
            self.TaskIDsBlocks = TaskIDsBlocks

        if OwnerIDsBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.OwnerIDsBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.OwnerIDs = {}
            self.OwnerIDs['OwnerID'] = None    # MVT_LLUUID
        else:
            self.OwnerIDsBlocks = OwnerIDsBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ParcelData', LocalID=self.ParcelData['LocalID'], ReturnType=self.ParcelData['ReturnType']))
        for block in self.TaskIDsBlocks:
            args.append(Block('TaskIDs', TaskID=block['TaskID']))
        for block in self.OwnerIDsBlocks:
            args.append(Block('OwnerIDs', OwnerID=block['OwnerID']))

        return Message('ParcelDisableObjects', args)

class LandStatRequestPacket(object):
    ''' a template for a LandStatRequest packet '''

    def __init__(self, AgentDataBlock = {}, RequestDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'LandStatRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if RequestDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.RequestData = {}    # New RequestData block
            self.RequestData['ReportType'] = None    # MVT_U32
            self.RequestData['RequestFlags'] = None    # MVT_U32
            self.RequestData['Filter'] = None    # MVT_VARIABLE
            self.RequestData['ParcelLocalID'] = None    # MVT_S32
        else:
            self.RequestData = RequestDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('RequestData', ReportType=self.RequestData['ReportType'], RequestFlags=self.RequestData['RequestFlags'], Filter=self.RequestData['Filter'], ParcelLocalID=self.RequestData['ParcelLocalID']))

        return Message('LandStatRequest', args)

class ChatFromViewerPacket(object):
    ''' a template for a ChatFromViewer packet '''

    def __init__(self, AgentDataBlock = {}, ChatDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'ChatFromViewer'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ChatDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ChatData = {}    # New ChatData block
            self.ChatData['Message'] = None    # MVT_VARIABLE
            self.ChatData['Type'] = None    # MVT_U8
            self.ChatData['Channel'] = None    # MVT_S32
        else:
            self.ChatData = ChatDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ChatData', Message=self.ChatData['Message'], Type=self.ChatData['Type'], Channel=self.ChatData['Channel']))

        return Message('ChatFromViewer', args)

class InternalScriptMailPacket(object):
    ''' a template for a InternalScriptMail packet '''

    def __init__(self, DataBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'InternalScriptMail'

        if DataBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.DataBlock = {}    # New DataBlock block
            self.DataBlock['From'] = None    # MVT_VARIABLE
            self.DataBlock['To'] = None    # MVT_LLUUID
            self.DataBlock['Subject'] = None    # MVT_VARIABLE
            self.DataBlock['Body'] = None    # MVT_VARIABLE
        else:
            self.DataBlock = DataBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('DataBlock', From=self.DataBlock['From'], To=self.DataBlock['To'], Subject=self.DataBlock['Subject'], Body=self.DataBlock['Body']))

        return Message('InternalScriptMail', args)

class TerminateFriendshipPacket(object):
    ''' a template for a TerminateFriendship packet '''

    def __init__(self, AgentDataBlock = {}, ExBlockBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'TerminateFriendship'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if ExBlockBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.ExBlock = {}    # New ExBlock block
            self.ExBlock['OtherID'] = None    # MVT_LLUUID
        else:
            self.ExBlock = ExBlockBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('ExBlock', OtherID=self.ExBlock['OtherID']))

        return Message('TerminateFriendship', args)

class EventInfoRequestPacket(object):
    ''' a template for a EventInfoRequest packet '''

    def __init__(self, AgentDataBlock = {}, EventDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'EventInfoRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if EventDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.EventData = {}    # New EventData block
            self.EventData['EventID'] = None    # MVT_U32
        else:
            self.EventData = EventDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('EventData', EventID=self.EventData['EventID']))

        return Message('EventInfoRequest', args)

class AgentRequestSitPacket(object):
    ''' a template for a AgentRequestSit packet '''

    def __init__(self, AgentDataBlock = {}, TargetObjectBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentRequestSit'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if TargetObjectBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TargetObject = {}    # New TargetObject block
            self.TargetObject['TargetID'] = None    # MVT_LLUUID
            self.TargetObject['Offset'] = None    # MVT_LLVector3
        else:
            self.TargetObject = TargetObjectBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('TargetObject', TargetID=self.TargetObject['TargetID'], Offset=self.TargetObject['Offset']))

        return Message('AgentRequestSit', args)

class UserInfoRequestPacket(object):
    ''' a template for a UserInfoRequest packet '''

    def __init__(self, AgentDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'UserInfoRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))

        return Message('UserInfoRequest', args)

class GroupNoticesListRequestPacket(object):
    ''' a template for a GroupNoticesListRequest packet '''

    def __init__(self, AgentDataBlock = {}, DataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'GroupNoticesListRequest'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['SessionID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if DataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.Data = {}    # New Data block
            self.Data['GroupID'] = None    # MVT_LLUUID
        else:
            self.Data = DataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], SessionID=self.AgentData['SessionID']))
        args.append(Block('Data', GroupID=self.Data['GroupID']))

        return Message('GroupNoticesListRequest', args)

class InventoryDescendentsPacket(object):
    ''' a template for a InventoryDescendents packet '''

    def __init__(self, AgentDataBlock = {}, FolderDataBlocks = [], ItemDataBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'InventoryDescendents'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
            self.AgentData['FolderID'] = None    # MVT_LLUUID
            self.AgentData['OwnerID'] = None    # MVT_LLUUID
            self.AgentData['Version'] = None    # MVT_S32
            self.AgentData['Descendents'] = None    # MVT_S32
        else:
            self.AgentData = AgentDataBlock

        if FolderDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.FolderDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.FolderData = {}
            self.FolderData['FolderID'] = None    # MVT_LLUUID
            self.FolderData['ParentID'] = None    # MVT_LLUUID
            self.FolderData['Type'] = None    # MVT_S8
            self.FolderData['Name'] = None    # MVT_VARIABLE
        else:
            self.FolderDataBlocks = FolderDataBlocks

        if ItemDataBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.ItemDataBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.ItemData = {}
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
        else:
            self.ItemDataBlocks = ItemDataBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID'], FolderID=self.AgentData['FolderID'], OwnerID=self.AgentData['OwnerID'], Version=self.AgentData['Version'], Descendents=self.AgentData['Descendents']))
        for block in self.FolderDataBlocks:
            args.append(Block('FolderData', FolderID=block['FolderID'], ParentID=block['ParentID'], Type=block['Type'], Name=block['Name']))
        for block in self.ItemDataBlocks:
            args.append(Block('ItemData', ItemID=block['ItemID'], FolderID=block['FolderID'], CreatorID=block['CreatorID'], OwnerID=block['OwnerID'], GroupID=block['GroupID'], BaseMask=block['BaseMask'], OwnerMask=block['OwnerMask'], GroupMask=block['GroupMask'], EveryoneMask=block['EveryoneMask'], NextOwnerMask=block['NextOwnerMask'], GroupOwned=block['GroupOwned'], AssetID=block['AssetID'], Type=block['Type'], InvType=block['InvType'], Flags=block['Flags'], SaleType=block['SaleType'], SalePrice=block['SalePrice'], Name=block['Name'], Description=block['Description'], CreationDate=block['CreationDate'], CRC=block['CRC']))

        return Message('InventoryDescendents', args)

class AbortXferPacket(object):
    ''' a template for a AbortXfer packet '''

    def __init__(self, XferIDBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AbortXfer'

        if XferIDBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.XferID = {}    # New XferID block
            self.XferID['ID'] = None    # MVT_U64
            self.XferID['Result'] = None    # MVT_S32
        else:
            self.XferID = XferIDBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('XferID', ID=self.XferID['ID'], Result=self.XferID['Result']))

        return Message('AbortXfer', args)

class AtomicPassObjectPacket(object):
    ''' a template for a AtomicPassObject packet '''

    def __init__(self, TaskDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AtomicPassObject'

        if TaskDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.TaskData = {}    # New TaskData block
            self.TaskData['TaskID'] = None    # MVT_LLUUID
            self.TaskData['AttachmentNeedsSave'] = None    # MVT_BOOL
        else:
            self.TaskData = TaskDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('TaskData', TaskID=self.TaskData['TaskID'], AttachmentNeedsSave=self.TaskData['AttachmentNeedsSave']))

        return Message('AtomicPassObject', args)

class DirPeopleReplyPacket(object):
    ''' a template for a DirPeopleReply packet '''

    def __init__(self, AgentDataBlock = {}, QueryDataBlock = {}, QueryRepliesBlocks = []):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'DirPeopleReply'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if QueryDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.QueryData = {}    # New QueryData block
            self.QueryData['QueryID'] = None    # MVT_LLUUID
        else:
            self.QueryData = QueryDataBlock

        if QueryRepliesBlocks == []:
            # initialize an empty list for blocks that may occur > 1 time in the packet
            self.QueryRepliesBlocks = []    # list to store multiple and variable block types

            # a sample block instance that may be appended to the list
            self.QueryReplies = {}
            self.QueryReplies['FirstName'] = None    # MVT_VARIABLE
            self.QueryReplies['LastName'] = None    # MVT_VARIABLE
            self.QueryReplies['Group'] = None    # MVT_VARIABLE
            self.QueryReplies['Online'] = None    # MVT_BOOL
            self.QueryReplies['Reputation'] = None    # MVT_S32
        else:
            self.QueryRepliesBlocks = QueryRepliesBlocks

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('QueryData', QueryID=self.QueryData['QueryID']))
        for block in self.QueryRepliesBlocks:
            args.append(Block('QueryReplies', FirstName=block['FirstName'], LastName=block['LastName'], Group=block['Group'], Online=block['Online'], Reputation=block['Reputation']))

        return Message('DirPeopleReply', args)

class AgentAlertMessagePacket(object):
    ''' a template for a AgentAlertMessage packet '''

    def __init__(self, AgentDataBlock = {}, AlertDataBlock = {}):
        """ allow passing in lists or dictionaries of block data """
        self.name = 'AgentAlertMessage'

        if AgentDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AgentData = {}    # New AgentData block
            self.AgentData['AgentID'] = None    # MVT_LLUUID
        else:
            self.AgentData = AgentDataBlock

        if AlertDataBlock == {}:
            # initialize an empty block like dict for blocks that occur only once in the packet
            self.AlertData = {}    # New AlertData block
            self.AlertData['Modal'] = None    # MVT_BOOL
            self.AlertData['Message'] = None    # MVT_VARIABLE
        else:
            self.AlertData = AlertDataBlock

    def __call__(self):
        ''' transforms the object into a Message '''

        args = []
        args.append(Block('AgentData', AgentID=self.AgentData['AgentID']))
        args.append(Block('AlertData', Modal=self.AlertData['Modal'], Message=self.AlertData['Message']))

        return Message('AgentAlertMessage', args)

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

