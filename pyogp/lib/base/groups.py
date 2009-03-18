"""
@file groups.py
@date 2009-03-12
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import uuid

# pyogp
from pyogp.lib.base.exc import DataParsingError

# pyogp messaging
from pyogp.lib.base.message.packets import CreateGroupRequestPacket

# initialize logging
logger = getLogger('pyogp.lib.base.groups')
log = logger.log

class GroupManager(object):
    """ a storage bin for groups

    also, a functional area for group creation operations
    """

    def __init__(self, agent, settings = None):
        """ initialize the group manager """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        self.agent = agent

        # the group store consists of a list
        # of Group() instances
        self.group_store = []

        # ~~~~~~~~~
        # Callbacks
        # ~~~~~~~~~

        if self.settings.LOG_VERBOSE: log(DEBUG, "Initialized the Group Manager")

    def store_group(self, _group):
        """ append to or replace a group in self.group_store """

        # replace an existing list member, else, append

        try:

            index = [self.group_store.index(_object_) for _group_ in self.group_store if _group_.ID == _group.GroupID]

            self.group_store[index[0]] = _group

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Replacing a stored group: \'%s\'' % (_group.GroupID))

        except:

            self.group_store.append(_group)

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Stored a new group: \'%s\'' % (_group.GroupID))

    def create_group(self, AgentID = None, SessionID = None, Name = None, Charter = '', ShowInList = True, InsigniaID = uuid.UUID('00000000-0000-0000-0000-000000000000'), MembershipFee = 0, OpenEnrollment = False, AllowPublish = False, MaturePublish = False):
        """ sends a message to the agent's current region requesting to create a group

        enables a callback (which should be unsubscribed from once we get a response)
        """

        if Name != None:

            log(INFO, "Sending a request to create group with a name of \'%s\'" % (Name))

            if AgentID == None: AgentID = self.agent.agent_id
            if SessionID == None: SessionID = self.agent.session_id

            packet = CreateGroupRequestPacket()

            # populate the AgentData block
            packet.AgentData['AgentID'] = uuid.UUID(str(AgentID))       # MVT_LLUUID
            packet.AgentData['SessionID'] = uuid.UUID(str(SessionID)) # MVT_LLUUID

            # populate the GroupData block
            packet.GroupData['Name'] = Name    # MVT_VARIABLE
            packet.GroupData['Charter'] = Charter    # MVT_VARIABLE
            packet.GroupData['ShowInList'] = ShowInList    # MVT_BOOL
            packet.GroupData['InsigniaID'] = uuid.UUID(str(InsigniaID))    # MVT_LLUUID
            packet.GroupData['MembershipFee'] = MembershipFee    # MVT_S32
            packet.GroupData['OpenEnrollment'] = OpenEnrollment    # MVT_BOOL
            packet.GroupData['AllowPublish'] = AllowPublish    # MVT_BOOL
            packet.GroupData['MaturePublish'] = MaturePublish    # MVT_BOOL

            self.agent.region.enqueue_message(packet(), True)

            if self.settings.HANDLE_PACKETS:
                # enable the callback to watch for the CreateGroupReply packet
                self.onCreateGroupReply_received = self.agent.packet_handler._register('CreateGroupReply')
                self.onCreateGroupReply_received.subscribe(onCreateGroupReply, self)
        else:

            raise DataParsingError('Failed to create a group, please specify a name')

class Group(object):
    """ representation of a group """

    def __init__(self, AcceptNotices, GroupPowers, GroupID, GroupName, ListInProfile, Contribution, GroupInsigniaID):

        self.AcceptNotices =AcceptNotices
        self.GroupPowers = GroupPowers
        self.GroupID = uuid.UUID(str(GroupID))
        self.GroupName = GroupName
        self.ListInProfile = ListInProfile
        self.Contribution = Contribution
        self.GroupInsigniaID = uuid.UUID(str(GroupInsigniaID))

class ChatterBoxInvitation_Message(object):
    """ a group chat message sent over the event queue """

    def __init__(self, session_name = None, from_name = None, session_id = None, _type = None, region_id = None, offline = None, timestamp = None, ttl = None, to_id = None, source = None, from_group = None, position = None, parent_estate_id = None, message = None, binary_bucket = None, _id = None, god_level = None, limited_to_estate = None, check_estate = None, agent_id = None, from_id = None, ChatterBoxInvitation_Data = None):

        if ChatterBoxInvitation_Data != None:

            self.session_name = ChatterBoxInvitation_Data['session_name']
            self.from_name = ChatterBoxInvitation_Data['from_name']
            self.session_id = uuid.UUID(str(ChatterBoxInvitation_Data['session_id']))
            #self.from_name = ChatterBoxInvitation_Data['session_name']
            self._type = ChatterBoxInvitation_Data['instantmessage']['message_params']['type']
            self.region_id = uuid.UUID(str(ChatterBoxInvitation_Data['instantmessage']['message_params']['region_id']))
            self.offline = ChatterBoxInvitation_Data['instantmessage']['message_params']['offline']
            self.timestamp = ChatterBoxInvitation_Data['instantmessage']['message_params']['timestamp']
            self.ttl = ChatterBoxInvitation_Data['instantmessage']['message_params']['ttl']
            self.to_id = uuid.UUID(str(ChatterBoxInvitation_Data['instantmessage']['message_params']['to_id']))
            self.source = ChatterBoxInvitation_Data['instantmessage']['message_params']['source']
            self.from_group = ChatterBoxInvitation_Data['instantmessage']['message_params']['from_group']
            self.position = ChatterBoxInvitation_Data['instantmessage']['message_params']['position']
            self.parent_estate_id = ChatterBoxInvitation_Data['instantmessage']['message_params']['parent_estate_id']
            self.message = ChatterBoxInvitation_Data['instantmessage']['message_params']['message']
            self.binary_bucket = ChatterBoxInvitation_Data['instantmessage']['message_params']['data']['binary_bucket']
            self._id = uuid.UUID(str(ChatterBoxInvitation_Data['instantmessage']['message_params']['id']))
            #self.from_id = ChatterBoxInvitation_Data['instantmessage']['message_params']['from_id']
            self.god_level = ChatterBoxInvitation_Data['instantmessage']['agent_params']['god_level']
            self.limited_to_estate = ChatterBoxInvitation_Data['instantmessage']['agent_params']['limited_to_estate']
            self.check_estate = ChatterBoxInvitation_Data['instantmessage']['agent_params']['check_estate']
            self.agent_id = uuid.UUID(str(ChatterBoxInvitation_Data['instantmessage']['agent_params']['agent_id']))
            self.from_id = uuid.UUID(str(ChatterBoxInvitation_Data['from_id']))
            #self.message = ChatterBoxInvitation_Data['message']

            self.name = 'ChatterBoxInvitation'

        else:

            self.session_name = session_name
            self.from_name = from_name
            self.session_id = session_id
            #self.from_name = from_name
            self._type = _type
            self.region_id = region_id
            self.offline = offline
            self.timestamp = timestamp
            self.ttl = ttl
            self.to_id = to_id
            self.source = source
            self.from_group = from_group
            self.position = position
            self.parent_estate_id = parent_estate_id
            self.message = message
            self.binary_bucket = binary_bucket
            self._id = _id
            #self.from_id = from_id
            self.god_level = god_level
            self.limited_to_estate = limited_to_estate
            self.check_estate = check_estate
            self.agent_id = agent_id
            self.from_id = from_id
            #self.message = message

            self.name = 'ChatterBoxInvitation'

# ~~~~~~~~~~~~~~~~~~
# Callback functions
# ~~~~~~~~~~~~~~~~~~

def onCreateGroupReply(packet, group_manager):
    """ when we get a CreateGroupReply packet, log Success, and if True, request the group details. remove the callback in any case """

    # remove the monitor
    group_manager.onCreateGroupReply_received.unsubscribe(onCreateGroupReply, group_manager)

    AgentID = packet.message_data.blocks['AgentData'][0].get_variable('AgentID').data
    GroupID = packet.message_data.blocks['ReplyData'][0].get_variable('GroupID').data
    Success = packet.message_data.blocks['ReplyData'][0].get_variable('Success').data
    Message = packet.message_data.blocks['ReplyData'][0].get_variable('Message').data

    if Success:
        log(INFO, "Created group %s. Message data is: %s" % (GroupID, Message))
        log(WARNING, "We now need to request the group data...")
    else:
        log(INFO, "Failed to create group due to: %s" % (Message))

'''
Groups related messages:

//-----------------------------------------------------------------------------
// Group messages
//-----------------------------------------------------------------------------

                        // CreateGroupRequest
                        // viewer -> simulator
                        // simulator -> dataserver
                        // reliable
                        {
                        	CreateGroupRequest Low 339 NotTrusted Zerocoded
                        	{
                        		AgentData		Single
                        		{	AgentID			LLUUID	}
                        		{	SessionID		LLUUID	}
                        	}
                        	{
                        		GroupData		Single
                        		{	Name			Variable	1	}	// string
                        		{	Charter			Variable	2	}	// string
                        		{	ShowInList		BOOL	}
                        		{	InsigniaID		LLUUID	}
                        		{	MembershipFee	S32				}	// S32		
                        		{	OpenEnrollment	BOOL			}   // BOOL (U8)
                        		{	AllowPublish	BOOL		}	// whether profile is externally visible or not
                        		{	MaturePublish	BOOL		}	// profile is "mature"
                        	}
                        }

                        // CreateGroupReply
                        // dataserver -> simulator
                        // simulator -> viewer
                        // reliable
                        {
                        	CreateGroupReply Low 340 Trusted Unencoded
                        	{
                        		AgentData		Single
                        		{	AgentID			LLUUID	}
                        	}
                        	{
                        		ReplyData		Single
                        		{	GroupID			LLUUID	}
                        		{	Success			BOOL	}
                        		{	Message			Variable	1	}	// string
                        	}
                        }

// UpdateGroupInfo
// viewer -> simulator
// simulator -> dataserver
// reliable
{
	UpdateGroupInfo Low 341 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID			LLUUID	}
		{	Charter			Variable	2	}	// string
		{	ShowInList		BOOL			}
		{	InsigniaID		LLUUID	}
		{	MembershipFee	S32				}
		{	OpenEnrollment	BOOL			}
		{	AllowPublish	BOOL	}
		{	MaturePublish	BOOL	}
	}
}

// GroupRoleChanges
// viewer -> simulator -> dataserver
// reliable
{
	GroupRoleChanges	Low	342 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID	LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		RoleChange	Variable
		{	RoleID		LLUUID	}
		{	MemberID	LLUUID	}
		{	Change		U32		}
	}
}

// JoinGroupRequest
// viewer -> simulator -> dataserver
// reliable
{
	JoinGroupRequest Low 343 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID		LLUUID	}
	}
}

// JoinGroupReply
// dataserver -> simulator -> viewer
{
	JoinGroupReply Low 344 Trusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID		LLUUID	}
		{	Success		BOOL	}
	}
}


// EjectGroupMemberRequest
// viewer -> simulator -> dataserver
// reliable
{
	EjectGroupMemberRequest Low 345 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
	}
	{
		EjectData		Variable
		{	EjecteeID	LLUUID	}
	}
}

// EjectGroupMemberReply
// dataserver -> simulator -> viewer
// reliable
{
	EjectGroupMemberReply Low 346 Trusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
	}
	{
		EjectData		Single
		{	Success		BOOL	}
	}
}

// LeaveGroupRequest
// viewer -> simulator -> dataserver
// reliable
{
	LeaveGroupRequest Low 347 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
	}
}

// LeaveGroupReply
// dataserver -> simulator -> viewer
{
	LeaveGroupReply Low 348 Trusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID		LLUUID	}
		{	Success		BOOL	}
	}
}

// InviteGroupRequest
// viewer -> simulator -> dataserver
// reliable
{
	InviteGroupRequest Low 349 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}	// UUID of inviting agent
		{	SessionID	LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID		LLUUID	}
	}
	{
		InviteData	Variable
		{	InviteeID	LLUUID	}
		{	RoleID		LLUUID	}
	}
}

// InviteGroupResponse
// simulator -> dataserver
// reliable
{
	InviteGroupResponse	Low	350 Trusted	Unencoded
	{
		InviteData	Single
		{	AgentID		LLUUID	}
		{	InviteeID	LLUUID	}
		{	GroupID			LLUUID	}
		{	RoleID		LLUUID	}
		{	MembershipFee S32	}
	}
}

// GroupProfileRequest
// viewer-> simulator -> dataserver
// reliable
{
	GroupProfileRequest Low 351 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID	LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID			LLUUID			}
	}
}

// GroupProfileReply
// dataserver -> simulator -> viewer
// reliable
{
	GroupProfileReply Low 352 Trusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
	}
	{
		GroupData		Single
		{	GroupID			LLUUID			}
		{	Name			Variable	1	}	// string
		{	Charter			Variable	2	}	// string
		{	ShowInList		BOOL	}
		{	MemberTitle		Variable	1	}	// string
		{	PowersMask		U64	}	// U32 mask
		{	InsigniaID		LLUUID			}
		{	FounderID		LLUUID			}
		{	MembershipFee	S32				}
		{	OpenEnrollment	BOOL			}   // BOOL (U8)
		{	Money			S32	}
		{	GroupMembershipCount	S32	}
		{	GroupRolesCount			S32	}
		{	AllowPublish	BOOL	}
		{	MaturePublish	BOOL	}
		{	OwnerRole		LLUUID	}
	}
}

// CurrentInterval = 0  =>  this period (week, day, etc.)
// CurrentInterval = 1  =>  last period
// viewer -> simulator -> dataserver
// reliable
{
	GroupAccountSummaryRequest Low 353 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID		LLUUID	}
		{	GroupID			LLUUID	}
	}
	{
		MoneyData			Single
		{	RequestID		LLUUID	}
		{	IntervalDays	S32	}
		{	CurrentInterval	S32	}
	}
}


// dataserver -> simulator -> viewer
// Reliable
{
	GroupAccountSummaryReply Low 354 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	GroupID			LLUUID		}
	}
	{
		MoneyData			Single
		{	RequestID			LLUUID	}
		{	IntervalDays		S32	}
		{	CurrentInterval		S32	}
		{	StartDate			Variable	1	}	// string
		{	Balance				S32	}
		{	TotalCredits		S32	}
		{	TotalDebits			S32	}
		{	ObjectTaxCurrent	S32	}
		{	LightTaxCurrent		S32	}
		{	LandTaxCurrent		S32	}
		{	GroupTaxCurrent		S32	}
		{	ParcelDirFeeCurrent	S32	}
		{	ObjectTaxEstimate	S32	}
		{	LightTaxEstimate	S32	}
		{	LandTaxEstimate		S32	}
		{	GroupTaxEstimate	S32	}
		{	ParcelDirFeeEstimate	S32	}
		{	NonExemptMembers	S32	}
		{	LastTaxDate			Variable	1	}	// string
		{	TaxDate				Variable	1	}	// string
	}
}


// Reliable
{
	GroupAccountDetailsRequest Low 355 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
		{	GroupID			LLUUID	}
	}
	{
		MoneyData			Single
		{	RequestID		LLUUID	}
		{	IntervalDays	S32	}
		{	CurrentInterval	S32	}
	}
}

// Reliable
{
	GroupAccountDetailsReply Low 356 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	GroupID			LLUUID		}
	}
	{
		MoneyData			Single
		{	RequestID		LLUUID	}
		{	IntervalDays	S32	}
		{	CurrentInterval	S32	}
		{	StartDate		Variable	1	}	// string
	}
	{
		HistoryData			Variable
		{	Description		Variable	1	}	// string
		{	Amount			S32	}
	}
}


// Reliable
{
	GroupAccountTransactionsRequest Low 357 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
		{	GroupID			LLUUID		}
	}
	{
		MoneyData			Single
		{	RequestID		LLUUID	}
		{	IntervalDays	S32	}
		{	CurrentInterval	S32	}
	}
}

// Reliable
{
	GroupAccountTransactionsReply Low 358 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	GroupID			LLUUID		}
	}
	{
		MoneyData			Single
		{	RequestID		LLUUID	}
		{	IntervalDays	S32	}
		{	CurrentInterval	S32	}
		{	StartDate		Variable	1	}	// string
	}
	{
		HistoryData			Variable
		{	Time			Variable	1	}	// string
		{	User			Variable	1	}	// string
		{	Type			S32	}
		{	Item			Variable	1	}	// string
		{	Amount			S32	}
	}
}

// GroupActiveProposalsRequest
// viewer -> simulator -> dataserver
//reliable
{
	GroupActiveProposalsRequest Low 359 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID		LLUUID			}
	}
	{
		GroupData	Single
		{	GroupID			LLUUID			}
	}
	{
		TransactionData Single
		{	TransactionID	LLUUID	}
	}
}

// GroupActiveProposalItemReply
// dataserver -> simulator -> viewer
// reliable
{
	GroupActiveProposalItemReply Low 360 Trusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	GroupID			LLUUID			}
	}
	{
		TransactionData Single
		{	TransactionID	LLUUID	}
		{	TotalNumItems	U32		}
	}
	{
		ProposalData	Variable
		{	VoteID			LLUUID			}
		{	VoteInitiator	LLUUID			}
		{	TerseDateID		Variable	1	} // string
		{	StartDateTime	Variable	1	}	// string
		{	EndDateTime		Variable	1	}	// string
		{	AlreadyVoted	BOOL			}
		{	VoteCast		Variable	1	}	// string
		{	Majority	F32		}
		{	Quorum		S32		}
		{	ProposalText	Variable	1	}	// string
	}
}

// GroupVoteHistoryRequest
// viewer -> simulator -> dataserver
//reliable
{
	GroupVoteHistoryRequest Low 361 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID		LLUUID			}
	}
	{
		GroupData	Single
		{	GroupID			LLUUID			}
	}
	{
		TransactionData Single
		{	TransactionID	LLUUID	}
	}
}

// GroupVoteHistoryItemReply
// dataserver -> simulator -> viewer
// reliable
{
	GroupVoteHistoryItemReply Low 362 Trusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	GroupID			LLUUID			}
	}
	{
		TransactionData Single
		{	TransactionID	LLUUID	}
		{	TotalNumItems	U32		}
	}
	{
		HistoryItemData	Single
		{	VoteID			LLUUID			}
		{	TerseDateID		Variable	1	} // string
		{	StartDateTime	Variable	1	}	// string
		{	EndDateTime		Variable	1	}	// string
		{	VoteInitiator	LLUUID			}
		{	VoteType		Variable	1	}	// string
		{	VoteResult		Variable	1	}	// string
		{	Majority	F32		}
		{	Quorum		S32		}
		{	ProposalText	Variable	2	}	// string
	}
	{
		VoteItem	Variable
		{	CandidateID		LLUUID		}
		{	VoteCast		Variable	1	}	// string
		{	NumVotes		S32		}
	}
}

// StartGroupProposal
// viewer -> simulator -> dataserver
// reliable
{
	StartGroupProposal Low 363 NotTrusted Zerocoded UDPDeprecated
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ProposalData		Single
		{	GroupID			LLUUID			}
		{	Quorum			S32				}
		{	Majority		F32				}	// F32
		{	Duration		S32				}	// S32, seconds
		{	ProposalText	Variable	1	}	// string
	}
}

// GroupProposalBallot
// viewer -> simulator -> dataserver
// reliable
{
	GroupProposalBallot Low 364 NotTrusted Unencoded UDPDeprecated
	{
		AgentData		Single
		{	AgentID		LLUUID			}
		{	SessionID	LLUUID	}
	}
	{
		ProposalData		Single
		{	ProposalID		LLUUID			}
		{	GroupID			LLUUID			}
		{	VoteCast		Variable	1	}	// string
	}
}

// TallyVotes userserver -> dataserver
// reliable
{
	TallyVotes	Low	365 Trusted Unencoded
}



// GroupMembersRequest
// get the group members
// simulator -> dataserver
// reliable
{
	GroupMembersRequest Low 366 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
		{   RequestID	LLUUID	}
	}
}

// GroupMembersReply
// list of uuids for the group members
// dataserver -> simulator
// reliable
{
	GroupMembersReply Low 367 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
		{   RequestID	LLUUID	}
		{	MemberCount	S32		}
	}
	{
		MemberData		Variable
		{	AgentID		LLUUID	}
		{	Contribution	S32	}
		{	OnlineStatus	Variable	1	}	// string
		{	AgentPowers		U64	}
		{	Title			Variable	1	}	// string
		{	IsOwner			BOOL	}
	}
}

// used to switch an agent's currently active group.
// viewer -> simulator -> dataserver -> AgentDataUpdate...
{
	ActivateGroup	Low	368 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
}

// viewer -> simulator -> dataserver
{
	SetGroupContribution Low 369 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		Data	Single
		{	GroupID		LLUUID	}
		{	Contribution	S32	}
	}
}

// viewer -> simulator -> dataserver
{
	SetGroupAcceptNotices Low 370 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		Data	Single
		{	GroupID		LLUUID	}
		{	AcceptNotices	BOOL	}
	}
	{
		NewData				Single
		{	ListInProfile	BOOL	}
	}
}

// GroupRoleDataRequest
// viewer -> simulator -> dataserver
{
	GroupRoleDataRequest Low	371 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		GroupData	Single
		{	GroupID		LLUUID	}
		{	RequestID	LLUUID	}
	}
}


// GroupRoleDataReply
// All role data for this group
// dataserver -> simulator -> agent
{
	GroupRoleDataReply Low	372 Trusted	Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
	}
	{
		GroupData		Single
		{	GroupID			LLUUID	}
		{	RequestID	LLUUID	}
		{	RoleCount	S32		}
	}
	{
		RoleData	Variable
		{	RoleID		LLUUID	}
		{	Name		Variable	1	}
		{	Title		Variable	1	}
		{	Description	Variable	1	}
		{	Powers		U64		}
		{	Members		U32		}
	}
}

// GroupRoleMembersRequest
// viewer -> simulator -> dataserver
{
	GroupRoleMembersRequest Low	373 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID	LLUUID	}
	}
	{
		GroupData		Single
		{	GroupID		LLUUID	}
		{	RequestID	LLUUID	}
	}
}

// GroupRoleMembersReply
// All role::member pairs for this group.
// dataserver -> simulator -> agent
{
	GroupRoleMembersReply Low	374 Trusted	Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	GroupID		LLUUID	}
		{	RequestID	LLUUID	}
		{	TotalPairs	U32		}
	}
	{
		MemberData		Variable
		{	RoleID		LLUUID	}
		{	MemberID	LLUUID	}
	}
}

// GroupTitlesRequest
// viewer -> simulator -> dataserver
{
	GroupTitlesRequest Low	375 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
		{	RequestID	LLUUID	}
	}
}


// GroupTitlesReply
// dataserver -> simulator -> viewer
{
	GroupTitlesReply Low 376 Trusted	Zerocoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	GroupID		LLUUID	}
		{	RequestID	LLUUID	}
	}
	{
		GroupData	Variable
		{	Title		Variable	1	} // string
		{	RoleID		LLUUID			}
		{	Selected	BOOL			}
	}
}

// GroupTitleUpdate
// viewer -> simulator -> dataserver
{
	GroupTitleUpdate	Low	377 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
		{	TitleRoleID	LLUUID	}
	}
}

// GroupRoleUpdate
// viewer -> simulator -> dataserver
{
	GroupRoleUpdate		Low	378 NotTrusted	Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		RoleData	Variable
		{	RoleID		LLUUID	}
		{	Name		Variable	1	}
		{	Description	Variable	1	}
		{	Title		Variable	1	}
		{	Powers		U64		}
		{	UpdateType	U8		}
	}
}
			


// Request the members of the live help group needed for requesting agent.
// userserver -> dataserver
{
	LiveHelpGroupRequest Low 379 Trusted Unencoded
	{
		RequestData 	Single
		{	RequestID	LLUUID	}
		{	AgentID		LLUUID	}
	}
}

// Send down the group
// dataserver -> userserver
{
	LiveHelpGroupReply Low 380 Trusted Unencoded
	{
		ReplyData	 	Single
		{	RequestID	LLUUID	}
		{	GroupID		LLUUID	}
		{	Selection	Variable 	1	} // selection criteria all or active
	}
}

'''
