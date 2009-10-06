// pyogp test message_template.msg


// *************************************************************************
// Test Message
// *************************************************************************

// Test Message

{
	TestMessage Low 1 NotTrusted Zerocoded
	{
		TestBlock1		Single
		{	Test1		U32	}
	}
	{
		NeighborBlock		Multiple		4
		{	Test0		U32	}
		{	Test1		U32	}
		{	Test2		U32	}
	}
}

// *************************************************************************
// Messaging Internal Data Management Message
// *************************************************************************

// *************************
// List fixed messages first
// *************************


// Packet Ack - Ack a list of packets sent reliable
{
	PacketAck Fixed 0xFFFFFFFB NotTrusted Unencoded
	{
		Packets			Variable		
		{	ID			U32	}
	}
}


// OpenCircuit - Tells the recipient's messaging system to open the descibed circuit
{
	OpenCircuit Fixed 0xFFFFFFFC NotTrusted Unencoded
	{
		CircuitInfo		Single
		{	IP			IPADDR	}
		{	Port		IPPORT	}
	}
}


// CloseCircuit - Tells the recipient's messaging system to close the descibed circuit
{
	CloseCircuit Fixed 0xFFFFFFFD NotTrusted Unencoded
}


// ******************
// End fixed messages
// ******************

// StartPingCheck - used to measure circuit ping times
// PingID is used to determine how backlogged the ping was that was
// returned (or how hosed the other side is)
{
	StartPingCheck High 1 NotTrusted Unencoded
	{
		PingID Single
		{	PingID	U8	}
		{	OldestUnacked	U32	}	// Current oldest "unacked" packet on the sender side
	}
}

// CompletePingCheck - used to measure circuit ping times

{
	CompletePingCheck High 2 NotTrusted Unencoded
	{
		PingID Single
		{	PingID	U8	}
	}
}

// space->sim
// sim->sim
// AddCircuitCode - Tells the recipient's messaging system that this code
// is for a legal circuit
{
	AddCircuitCode Low 2 Trusted Unencoded
	{
		CircuitCode		Single
		{	Code		U32		}
		{	SessionID	LLUUID	}
		{	AgentID		LLUUID	} // WARNING - may be null in valid message
	}
}

// viewer->sim
// UseCircuitCode - Attempts to provide the recipient with IP and Port
// info. In the case of viewers, the id is the session id. For other
// machines it may be null. The session id will always be the session
// id of the process, which every server will generate on startup and
// the viewer will be handed after login.
{
	UseCircuitCode Low 3 NotTrusted Unencoded
	{
		CircuitCode		Single
		{	Code		U32		}
		{	SessionID	LLUUID	}
		{	ID			LLUUID	} // agent id
	}
}


// *************************************************************************
// SpaceServer to Simulator Messages
// ************************************************************************

// Neighbor List - Passed anytime neighbors change
{
	NeighborList High 3 Trusted Unencoded
	{
		NeighborBlock	Multiple		4
		{	IP			IPADDR	}
		{	Port		IPPORT	}
		{	PublicIP    IPADDR	}
		{	PublicPort  IPPORT	}
		{	RegionID	LLUUID	}
		{	Name		Variable		1	}	// string
		{	SimAccess	U8	}
	}
}


// AvatarTextureUpdate
// simulator -> dataserver
// reliable
{
	AvatarTextureUpdate Low 4 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	TexturesChanged	BOOL	}
	}
	{
		WearableData		Variable
		{	CacheID			LLUUID }
		{	TextureIndex	U8 }
		{	HostName		Variable	1	}
	}
	{
		TextureData		Variable
		{	TextureID		LLUUID	}
	}
}


// SimulatorMapUpdate
// simulator -> dataserver
// reliable
{
	SimulatorMapUpdate Low 5 Trusted Unencoded
	{
		MapData		Single
		{	Flags		U32		}
	}
}

// SimulatorSetMap
// simulator -> dataserver
// reliable
// Used to upload a map image into the database (currently used only for Land For Sale)
{
	SimulatorSetMap Low 6 Trusted Unencoded
	{
		MapData		Single
		{	RegionHandle	U64		}
		{	Type			S32		}
		{	MapImage		LLUUID	}
	}
}

// SubscribeLoad
// spaceserver -> simulator
// reliable
{
	SubscribeLoad	Low	7 Trusted Unencoded
}

// UnsubscribeLoad
// spaceserver -> simulator
// reliable
{
	UnsubscribeLoad Low 8 Trusted Unencoded
}


// ************************************************************************
// Simulator to SpaceServer Messages
// ************************************************************************

// SimulatorReady - indicates the sim has finished loading its state
// and is ready to receive updates from others
{
	SimulatorReady Low 9 Trusted Zerocoded
	{
		SimulatorBlock		Single
		{	SimName			Variable	1	}
		{	SimAccess		U8	}
		{	RegionFlags		U32	}
		{	RegionID		LLUUID	}
		{	EstateID		U32	}
		{	ParentEstateID	U32	}
	}
	{
		TelehubBlock		Single
		{	HasTelehub		BOOL		}
		{	TelehubPos		LLVector3	}
	}
}

// TelehubInfo - fill in the UI for telehub creation floater.
// sim -> viewer
// reliable
{
	TelehubInfo	Low	10 Trusted Unencoded
	{
		TelehubBlock		Single
		{	ObjectID		LLUUID			}	// null if no telehub
		{	ObjectName		Variable 1		}	// string
		{	TelehubPos		LLVector3		}	// fallback if viewer can't find object
		{	TelehubRot		LLQuaternion	}
	}
	{
		SpawnPointBlock		Variable
		{	SpawnPointPos	LLVector3		}	// relative to telehub position
	}
}

// SimulatorPresentAtLocation - indicates that the sim is present at a grid
// location and passes what it believes its neighbors are
{
	SimulatorPresentAtLocation Low 11 Trusted Unencoded
	{
		SimulatorPublicHostBlock	Single
		{	Port        IPPORT }
		{	SimulatorIP IPADDR }
		{   GridX       U32	   }
		{	GridY       U32    }
	}
	{
		NeighborBlock	Multiple		4
		{	IP			IPADDR	}
		{	Port		IPPORT	}
	}
	{
		SimulatorBlock		Single
		{	SimName			Variable	1	}
		{	SimAccess		U8	}
		{	RegionFlags		U32	}
		{	RegionID		LLUUID	}
		{	EstateID		U32	}
		{	ParentEstateID	U32	}
	}
	{
		TelehubBlock		Variable
		{	HasTelehub		BOOL		}
		{	TelehubPos		LLVector3	}
	}
}

// SimulatorLoad
// simulator -> spaceserver
// reliable
{
	SimulatorLoad Low 12 Trusted Unencoded
	{
		SimulatorLoad		Single
		{	TimeDilation 	F32 }
		{	AgentCount 		S32 }
		{	CanAcceptAgents	BOOL	}
	}
	{
		AgentList	Variable
		{	CircuitCode		U32	}
		{	X				U8	}
		{	Y				U8	}
	}
}

// Simulator Shutdown Request - Tells spaceserver that a simulator is trying to shutdown
{
	SimulatorShutdownRequest Low 13 Trusted Unencoded
}

// ****************************************************************************
// Presense messages
// ****************************************************************************

// sim -> dataserver
{
	RegionPresenceRequestByRegionID Low 14 Trusted Unencoded
	{
		RegionData		Variable
		{	RegionID	LLUUID	}
	}
}

// sim -> dataserver
{
	RegionPresenceRequestByHandle Low 15 Trusted Unencoded
	{
		RegionData		Variable
		{	RegionHandle	U64	}
	}
}

// dataserver -> sim
{
	RegionPresenceResponse Low 16 Trusted Zerocoded
	{
		RegionData		Variable
		{	RegionID			LLUUID	}
		{	RegionHandle		U64	}
		{	InternalRegionIP	IPADDR	}
		{	ExternalRegionIP	IPADDR	}
		{	RegionPort			IPPORT	}
		{	ValidUntil			F64	}
		{	Message				Variable	1	}
	}
}
 

// ****************************************************************************
// Simulator to dataserver messages
// ****************************************************************************

// Updates SimName, EstateID and SimAccess using RegionID as a key
{
	UpdateSimulator Low 17 Trusted Unencoded
	{
		SimulatorInfo	Single
		{	RegionID	LLUUID	}
		{	SimName		Variable	1	}
		{	EstateID	U32		}
		{	SimAccess	U8		}
	}
}


// record dwell time.
{
	LogDwellTime	Low	18 Trusted Unencoded
	{
		DwellInfo	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	Duration	F32		}
		{	SimName		Variable	1 }
		{	RegionX		U32		}
		{	RegionY		U32		}
		{	AvgAgentsInView U8  }
		{	AvgViewerFPS U8		}
	}
}

// Disabled feature response message
{
	FeatureDisabled	Low 19 Trusted Unencoded
	{
		FailureInfo			Single
		{	ErrorMessage	Variable	1	}
		{	AgentID			LLUUID			}
		{	TransactionID	LLUUID			}
	}
}


// record lost money transactions.  This message could be generated
// from either the simulator or the dataserver, depending on how
// the transaction failed.
{
	LogFailedMoneyTransaction	Low 20 Trusted Unencoded
	{
		TransactionData	Single
		{	TransactionID	LLUUID	}
		{ 	TransactionTime	U32		} // utc seconds since epoch
		{	TransactionType	S32		}	// see lltransactiontypes.h
		{	SourceID		LLUUID  }
		{	DestID			LLUUID	}	// destination of the transfer
		{	Flags			U8		}
		{	Amount			S32		}
		{	SimulatorIP		IPADDR	}	// U32 encoded IP
		{	GridX			U32		}
		{	GridY			U32		}
		{	FailureType		U8		}
	}
}

// complaint/bug-report - sim -> dataserver. see UserReport for details.
// reliable
{
	UserReportInternal Low 21 Trusted Zerocoded
	{
		ReportData	Single
		{   ReportType		U8   }
		{   Category		U8   }
		{   ReporterID		LLUUID  }
		{	ViewerPosition	LLVector3	}
		{	AgentPosition	LLVector3	}
		{   ScreenshotID	LLUUID  }
		{   ObjectID		LLUUID  }
		{   OwnerID			LLUUID  }
		{   LastOwnerID		LLUUID  }
		{   CreatorID		LLUUID  }
		{	RegionID		LLUUID	}
		{   AbuserID		LLUUID  }
		{	AbuseRegionName	Variable	1	}
		{	AbuseRegionID	LLUUID	}
		{   Summary			Variable	1   }
		{   Details 		Variable	2   }
		{	VersionString	Variable	1	}
	}
}

// SetSimStatusInDatabase
// alters the "simulator" table in the database
// sim -> dataserver
// reliable
{
	SetSimStatusInDatabase Low 22 Trusted Unencoded
	{
		Data	Single
		{	RegionID	LLUUID	}
		{   HostName 	Variable 1	}
		{	X			S32	}
		{	Y			S32	}
		{	PID			S32	}
		{	AgentCount	S32	}
		{	TimeToLive  S32 } // in seconds
		{	Status		Variable	1	}
	}
}

// SetSimPresenceInDatabase
// updates the "presence" table in the database to ensure
// that a given simulator is present and valid for a set amount of
// time
{
	SetSimPresenceInDatabase Low 23 Trusted Unencoded
	{
		SimData Single
		{   RegionID 	LLUUID	}
		{   HostName 	Variable 1	}
		{	GridX		U32	}
		{	GridY		U32	}
		{	PID			S32	}
		{	AgentCount	S32	}
		{	TimeToLive  S32 } // in seconds
		{	Status		Variable	1	}
	}
}

// ***************************************************************************
// Economy messages
// ***************************************************************************

// once we use local stats, this will include a region handle
{
	EconomyDataRequest Low 24 NotTrusted Unencoded
}

// dataserver to sim, response w/ econ data
{
	EconomyData Low 25 Trusted Zerocoded
	{
		Info					Single
		{	ObjectCapacity			S32	}
		{	ObjectCount				S32	}
		{	PriceEnergyUnit			S32	}
		{	PriceObjectClaim		S32	}
		{	PricePublicObjectDecay	S32	}
		{	PricePublicObjectDelete	S32	}
		{	PriceParcelClaim		S32	}
		{	PriceParcelClaimFactor	F32	}
		{	PriceUpload				S32	}
		{	PriceRentLight			S32	}
		{	TeleportMinPrice		S32	}
		{	TeleportPriceExponent 	F32	}
		{	EnergyEfficiency		F32	}
		{	PriceObjectRent			F32	}
		{	PriceObjectScaleFactor 	F32	}
		{	PriceParcelRent			S32	}
		{	PriceGroupCreate		S32	}
	}
}

// ***************************************************************************
// Search messages
// ***************************************************************************

// AvatarPickerRequest
// Get a list of names to select a person
// viewer -> sim -> data
// reliable
{
	AvatarPickerRequest Low 26 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID		}
		{	SessionID	LLUUID		}
		{	QueryID		LLUUID		}
	}
	{
		Data			Single
		{	Name		Variable 1	}
	}
}

// backend implementation which tracks if the user is a god.
{
	AvatarPickerRequestBackend Low 27 Trusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID		}
		{	SessionID	LLUUID		}
		{	QueryID		LLUUID		}
		{	GodLevel	U8	}
	}
	{
		Data			Single
		{	Name		Variable 1	}
	}
}

// AvatarPickerReply
// List of names to select a person
// reliable
{
	AvatarPickerReply Low 28 Trusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID		}
		{	QueryID		LLUUID		}
	}
	{
		Data			Variable
		{	AvatarID	LLUUID		}
		{	FirstName	Variable 1	}
		{	LastName	Variable 1	}
	}
}

// PlacesQuery
// Used for getting a list of places for the group land panel
// and the user land holdings panel.  NOT for the directory.
{
	PlacesQuery Low 29 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID		}
		{	SessionID	LLUUID		}
		{	QueryID		LLUUID		}
	}
	{
		TransactionData Single
		{	TransactionID	LLUUID	}
	}
	{
		QueryData		Single
		{	QueryText	Variable	1	}
		{	QueryFlags	U32				}
		{	Category	S8				}
		{	SimName		Variable	1	}
	}
}

// PlacesReply
// dataserver -> simulator -> viewer
// If the user has specified a location, use that to compute
// global x,y,z.  Otherwise, use center of the AABB.
// reliable
{
	PlacesReply Low 30 Trusted Zerocoded UDPDeprecated
	{
		AgentData		Single
		{	AgentID		LLUUID		}
		{	QueryID		LLUUID		}
	}
	{
		TransactionData Single
		{	TransactionID	LLUUID	}
	}
	{
		QueryData		Variable
		{	OwnerID			LLUUID			}
		{	Name			Variable	1	}
		{	Desc			Variable	1	}
		{	ActualArea		S32				}
		{	BillableArea	S32				}
		{	Flags			U8				}
		{	GlobalX			F32				}	// meters
		{	GlobalY			F32				}	// meters
		{	GlobalZ			F32				}	// meters
		{	SimName			Variable	1	}
		{	SnapshotID		LLUUID			}
		{	Dwell			F32				}
		{	Price			S32				}
		//{	ProductSKU		Variable	1	}
	}
}

// DirFindQuery viewer->sim
// Message to start asking questions for the directory 
{
	DirFindQuery Low 31 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID		}
		{	SessionID	LLUUID		}
	}
	{
		QueryData		Single
		{	QueryID		LLUUID		}
		{	QueryText	Variable 1	}
		{	QueryFlags	U32			}
		{	QueryStart	S32			}	// prev/next page support
	}
}

// DirFindQueryBackend sim->data
// Trusted message generated by receipt of DirFindQuery to sim.
{
	DirFindQueryBackend Low 32 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID		}
	}
	{
		QueryData		Single
		{	QueryID		LLUUID		}
		{	QueryText	Variable 1	}
		{	QueryFlags	U32			}
		{	QueryStart	S32			}	// prev/next page support
		{	EstateID	U32			}
		{	Godlike		BOOL		}
	}
}


// DirPlacesQuery viewer->sim
// Used for the Find directory of places
{
	DirPlacesQuery Low 33 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID		}
		{	SessionID	LLUUID		}
	}
	{
		QueryData		Single
		{	QueryID		LLUUID		}
		{	QueryText	Variable	1	}
		{	QueryFlags	U32				}
		{	Category	S8				}
		{	SimName		Variable	1	}
		{	QueryStart	S32			}
	}
}

// DirPlacesQueryBackend sim->dataserver
// Used for the Find directory of places.
{
	DirPlacesQueryBackend Low 34 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID		}
	}
	{
		QueryData		Single
		{	QueryID		LLUUID		}
		{	QueryText	Variable	1	}
		{	QueryFlags	U32				}
		{	Category	S8				}
		{	SimName		Variable	1	}
		{	EstateID	U32				}
		{	Godlike		BOOL			}
		{	QueryStart	S32			}
	}
}

// DirPlacesReply dataserver->sim->viewer
// If the user has specified a location, use that to compute
// global x,y,z.  Otherwise, use center of the AABB.
// reliable
{
	DirPlacesReply Low 35 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID		}
	}
	{
		QueryData		Variable
		{	QueryID		LLUUID		}
	}
	{
		QueryReplies            Variable
		{	ParcelID		LLUUID		}
		{	Name			Variable 1	}
		{	ForSale			BOOL		}
		{	Auction			BOOL		}
		{	Dwell			F32			}
	}
	{
		StatusData            Variable
		{	Status		U32		}
	}
}

// DirPeopleReply
{
	DirPeopleReply Low 36 Trusted Zerocoded
	{
		AgentData				Single
		{	AgentID				LLUUID	}
	}
	{
		QueryData		        Single
		{	QueryID		        LLUUID	}
	}
	{
		QueryReplies            Variable
 		{	AgentID	  	 	    LLUUID			}
		{	FirstName	        Variable	1	}
		{	LastName	        Variable	1	}
		{	Group		        Variable	1	}
		{	Online  	        BOOL			}
		{	Reputation	        S32				}
	}
}

// DirEventsReply
{
	DirEventsReply Low 37 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID		}
	}
	{
		QueryData		Single
		{	QueryID		LLUUID		}
	}
	{
		QueryReplies	Variable
		{	OwnerID		LLUUID			}
		{	Name		Variable	1	}
		{	EventID		U32				}
		{	Date		Variable	1	}
		{	UnixTime	U32				}
		{	EventFlags	U32				}
	}
	{
		StatusData Variable
		{	Status		U32			}
	}
}

// DirGroupsReply
// dataserver -> userserver -> viewer
// reliable
{
	DirGroupsReply Low 38 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID			}
	}
	{
		QueryData		Single
		{	QueryID		LLUUID			}
	}
	{
		QueryReplies	Variable
		{	GroupID			LLUUID			}
		{	GroupName		Variable	1	}	// string
		{	Members			S32				}
		{	SearchOrder		F32				}
	}
}


// DirClassifiedQuery viewer->sim
// reliable
{
	DirClassifiedQuery Low 39 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		QueryData			Single
		{	QueryID			LLUUID			}
		{	QueryText		Variable	1	}
		{	QueryFlags		U32				}
		{	Category		U32				}
		{	QueryStart	S32					}
	}
}

// DirClassifiedQueryBackend sim->dataserver
// reliable
{
	DirClassifiedQueryBackend Low 40 Trusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
	}
	{
		QueryData			Single
		{	QueryID			LLUUID			}
		{	QueryText		Variable	1	}
		{	QueryFlags		U32				}
		{	Category		U32				}
		{	EstateID		U32				}
		{	Godlike			BOOL			}
		{	QueryStart	S32					}
	}
}

// DirClassifiedReply dataserver->sim->viewer
// reliable
{
	DirClassifiedReply Low 41 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID		}
	}
	{
		QueryData		Single
		{	QueryID		LLUUID		}
	}
	{
		QueryReplies	Variable
		{	ClassifiedID	LLUUID		}
		{	Name			Variable 1	}
		{	ClassifiedFlags	U8			}
		{	CreationDate	U32			}
		{	ExpirationDate	U32			}
		{	PriceForListing	S32			}
	}
	{
		StatusData Variable
		{	Status			U32		}
	}
}


// AvatarClassifiedReply
// dataserver -> simulator -> viewer
// Send the header information for this avatar's classifieds
// This fills in the tabs of the Classifieds panel.
// reliable
{
	AvatarClassifiedReply Low 42 Trusted Unencoded
	{
		AgentData		Single
		{	AgentID			LLUUID		}
		{	TargetID		LLUUID		}
	}
	{
		Data			Variable
		{	ClassifiedID	LLUUID		}
		{	Name			Variable 1	}
	}
}


// ClassifiedInfoRequest
// viewer -> simulator
// simulator -> dataserver
// reliable
{
	ClassifiedInfoRequest Low 43 NotTrusted Zerocoded
	{
		AgentData        Single
		{    AgentID        LLUUID		}
		{    SessionID      LLUUID		}
	}
	{
		Data        Single
		{	ClassifiedID	LLUUID		}
	}
}


// ClassifiedInfoReply
// dataserver -> simulator
// simulator -> viewer
// reliable
{
	ClassifiedInfoReply Low 44 Trusted Unencoded
    {
        AgentData    Single
        {	AgentID			LLUUID		}
    }
    {
		Data        Single
		{	ClassifiedID	LLUUID		}
		{	CreatorID		LLUUID		}
		{	CreationDate	U32			}
		{	ExpirationDate	U32			}
		{	Category		U32			}
		{	Name			Variable 1	}
        {	Desc			Variable 2	}
		{	ParcelID		LLUUID		}
		{	ParentEstate	U32			}
        {	SnapshotID		LLUUID		}
        {	SimName			Variable 1	}
        {	PosGlobal		LLVector3d	}
        {	ParcelName		Variable 1	}
		{	ClassifiedFlags	U8			}
		{	PriceForListing	S32			}
    }
}


// ClassifiedInfoUpdate
// Update a classified.  ParcelID and EstateID are set
// on the simulator as the message passes through.
// viewer -> simulator -> dataserver
// reliable
{
	ClassifiedInfoUpdate Low 45 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
	}
	{
		Data		Single
		{	ClassifiedID	LLUUID		}
		{	Category		U32			}
		{	Name			Variable 1	}
		{	Desc			Variable 2	}
		{	ParcelID		LLUUID		}
		{	ParentEstate	U32			}
		{	SnapshotID		LLUUID		}
		{	PosGlobal		LLVector3d	}
		{	ClassifiedFlags	U8			}
		{	PriceForListing	S32			}
	}
}


// ClassifiedDelete
// Delete a classified from the database.
// viewer -> simulator -> dataserver
// reliable
{
	ClassifiedDelete Low 46 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
	}
	{
		Data	Single
		{	ClassifiedID	LLUUID		}
	}
}

// ClassifiedGodDelete
// Delete a classified from the database.
// QueryID is needed so database can send a repeat list of 
// classified.
// viewer -> simulator -> dataserver
// reliable
{
	ClassifiedGodDelete Low 47 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
	}
	{
		Data	Single
		{	ClassifiedID	LLUUID		}
		{	QueryID			LLUUID		}
	}
}


// DirLandQuery viewer->sim
// Special query for the land for sale/auction panel.
// reliable
{
	DirLandQuery Low 48 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		QueryData			Single
		{	QueryID			LLUUID	}
		{	QueryFlags		U32		}
		{	SearchType		U32		}
		{	Price			S32		}
		{	Area			S32		}
		{	QueryStart		S32		}
	}
}

// DirLandQueryBackend sim->dataserver
// Special query for the land for sale/auction panel.
{
	DirLandQueryBackend Low 49 Trusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
	}
	{
		QueryData			Single
		{	QueryID			LLUUID	}
		{	QueryFlags		U32		}
		{	SearchType		U32		}
		{	Price			S32		}
		{	Area			S32		}
		{	QueryStart		S32		}
		{	EstateID		U32		}
		{	Godlike			BOOL	}
	}
}

// DirLandReply
// dataserver -> simulator -> viewer
// reliable
{
	DirLandReply Low 50 Trusted Zerocoded UDPDeprecated
	{
		AgentData			Single
		{	AgentID			LLUUID	}
	}
	{
		QueryData			Single
		{	QueryID			LLUUID		}
	}
	{
		QueryReplies		Variable
		{	ParcelID		LLUUID		}
		{	Name			Variable 1	}
		{	Auction			BOOL		}
		{	ForSale			BOOL		}
		{	SalePrice		S32			}
		{	ActualArea		S32			}
		//{	ProductSKU		Variable 1	}
	}
}

// DEPRECATED: DirPopularQuery viewer->sim
// Special query for the land for sale/auction panel.
// reliable
{
	DirPopularQuery Low 51 NotTrusted Zerocoded Deprecated
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		QueryData			Single
		{	QueryID			LLUUID	}
		{	QueryFlags		U32		}
	}
}

// DEPRECATED: DirPopularQueryBackend sim->dataserver
// Special query for the land for sale/auction panel.
// reliable
{
	DirPopularQueryBackend Low 52 Trusted Zerocoded Deprecated
	{
		AgentData			Single
		{	AgentID			LLUUID	}
	}
	{
		QueryData			Single
		{	QueryID			LLUUID	}
		{	QueryFlags		U32		}
		{	EstateID		U32		}
		{	Godlike			BOOL	}
	}
}

// DEPRECATED: DirPopularReply
// dataserver -> simulator -> viewer
// reliable
{
	DirPopularReply Low 53 Trusted Zerocoded Deprecated
	{
		AgentData			Single
		{	AgentID			LLUUID	}
	}
	{
		QueryData			Single
		{	QueryID			LLUUID		}
	}
	{
		QueryReplies		Variable
		{	ParcelID		LLUUID		}
		{	Name			Variable 1	}
		{	Dwell			F32			}
	}
}

// ParcelInfoRequest
// viewer -> simulator -> dataserver
// reliable
{
	ParcelInfoRequest Low 54 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID	}
	}
	{
		Data			Single
		{	ParcelID		LLUUID		}
	}
}

// ParcelInfoReply
// dataserver -> simulator -> viewer
// reliable
{
	ParcelInfoReply Low 55 Trusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID		}
	}
	{
		Data			Single
		{	ParcelID		LLUUID			}
		{	OwnerID			LLUUID			}
		{	Name			Variable	1	}
		{	Desc			Variable	1	}
		{	ActualArea		S32				}
		{	BillableArea	S32				}
		{	Flags			U8				}
		{	GlobalX			F32				}	// meters
		{	GlobalY			F32				}	// meters
		{	GlobalZ			F32				}	// meters
		{	SimName			Variable	1	}
		{	SnapshotID		LLUUID			}
		{	Dwell			F32				}
		{	SalePrice		S32				}
		{	AuctionID		S32				}
	}
}


// ParcelObjectOwnersRequest
// viewer -> simulator
// reliable
{
	ParcelObjectOwnersRequest Low 56 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID	}
	}
	{
		ParcelData		Single
		{	LocalID			S32		}
	}
}


// ParcelObjectOwnersReply
// simulator -> viewer
// reliable
{
	ParcelObjectOwnersReply Low 57 Trusted Zerocoded UDPDeprecated
	{
		Data			Variable
		{	OwnerID			LLUUID			}
		{	IsGroupOwned	BOOL			}
		{	Count			S32				}
		{	OnlineStatus	BOOL			}
	}
}

// GroupNoticeListRequest
// viewer -> simulator -> dataserver
// reliable
{
	GroupNoticesListRequest	Low	58 NotTrusted	Unencoded
	{
		AgentData        Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
	}
	{
		Data        Single
		{	GroupID			LLUUID		}
	}
}

// GroupNoticesListReply
// dataserver -> simulator -> viewer
// reliable
{
	GroupNoticesListReply	Low	59 Trusted	Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID		}
		{	GroupID			LLUUID		}
	}
	{
		Data		Variable
		{	NoticeID		LLUUID		}
		{	Timestamp		U32			}
		{	FromName		Variable 2	}
		{	Subject			Variable 2	}
		{	HasAttachment	BOOL		}
		{	AssetType		U8			}
	}
}

// GroupNoticeRequest
// viewer -> simulator
// simulator -> dataserver
// reliable
{
	GroupNoticeRequest Low 60 NotTrusted Unencoded
	{
		AgentData        Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
	}
	{
		Data        Single
		{	GroupNoticeID	LLUUID		}
	}
}

// GroupNoticeAdd
// Add a group notice. 
// simulator -> dataserver
// reliable
{
	GroupNoticeAdd Low 61 Trusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID		}
	}
	{
		MessageBlock		Single
		{	ToGroupID		LLUUID	}
		{	ID				LLUUID	}
		{	Dialog			U8	}
		{	FromAgentName	Variable	1	}
		{	Message			Variable	2	}
		{	BinaryBucket	Variable	2	}
	}
}


// ****************************************************************************
// Teleport messages
//
// The teleport messages are numerous, so I have attempted to give them a 
// consistent naming convention. Since there is a bit of glob pattern
// aliasing, the rules are applied in order.
//
// Teleport* - viewer->sim or sim->viewer message which announces a 
//             teleportation request, progrees, start, or end.
// Data* - sim->data or data->sim trusted message.
// Space* - sim->space or space->sim trusted messaging
// *Lure - A lure message to pass around information.
//
// All actual viewer teleports will begin with a Teleport* message and
// end in a TeleportStart, TeleportLocal or TeleportFailed message. The TeleportFailed
// message may be returned by any process and must be routed through the
// teleporting agent's simulator and back to the viewer.
// ****************************************************************************

// TeleportRequest
// viewer -> sim specifying exact teleport destination
{
	TeleportRequest	Low	62 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID		}
		{	SessionID	LLUUID		}
	}
	{
		Info		Single
		{	RegionID	LLUUID		}
		{	Position	LLVector3	}
		{	LookAt		LLVector3	}
	}
}

// TeleportLocationRequest
// viewer -> sim specifying exact teleport destination
{
	TeleportLocationRequest	Low	63 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID		}
		{	SessionID	LLUUID		}
	}
	{
		Info	Single
		{	RegionHandle	U64			}
		{	Position		LLVector3	}
		{	LookAt			LLVector3	}
	}
}

// TeleportLocal
// sim -> viewer reply telling the viewer that we've successfully TP'd
// to somewhere else within the sim
{
	TeleportLocal Low 64 Trusted Unencoded
	{
		Info		Single
		{	AgentID			LLUUID			}
		{	LocationID		U32				}
		{	Position		LLVector3		}	// region
		{	LookAt			LLVector3		}
		{	TeleportFlags 	U32				}
	}
}

// TeleportLandmarkRequest viewer->sim
// teleport to landmark asset ID destination. use LLUUD::null for home.
{
	TeleportLandmarkRequest Low 65 NotTrusted Zerocoded
	{
		Info		Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
		{	LandmarkID		LLUUID	}
	}
}

// TeleportProgress sim->viewer
// Tell the agent how the teleport is going.
{
	TeleportProgress Low 66 Trusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
	}
	{
		Info			Single
		{	TeleportFlags	U32			}
		{	Message		Variable	1	}  // string
	}
}

// DataHomeLocationRequest sim->data
// Request 
{
	DataHomeLocationRequest Low 67 Trusted Zerocoded
	{
		Info		Single
		{	AgentID			LLUUID	}
		{	KickedFromEstateID	U32	}
	}
}

// DataHomeLocationReply data->sim
// response is the location of agent home.
{
	DataHomeLocationReply Low 68 Trusted Unencoded
	{
		Info		Single
		{	AgentID			LLUUID		}
		{	RegionHandle	U64			}
		{	Position		LLVector3	}	// region coords
		{	LookAt			LLVector3	}
	}
}


// TeleportFinish sim->viewer
// called when all of the information has been collected and readied for 
// the agent.
{
	TeleportFinish Low 69 Trusted Unencoded UDPBlackListed
	{
		Info		Single
		{	AgentID			LLUUID			}
		{	LocationID		U32				}
		{	SimIP			IPADDR			}
		{	SimPort			IPPORT			}
		{	RegionHandle	U64				}
		{	SeedCapability	Variable	2	}	// URL
		{	SimAccess		U8				}
		{	TeleportFlags 	U32				}
	}
}

// StartLure viewer->sim
// Sent from viewer to the local simulator to lure target id to near 
// agent id. This will generate an instant message that will be routed 
// through the space server and out to the userserver. When that IM 
// goes through the userserver and the TargetID is online, the 
// userserver will send an InitializeLure to the spaceserver. When that
// packet is acked, the original instant message is finally forwarded to 
// TargetID.
{
	StartLure	Low	70 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID		LLUUID			}
	}
	{
		Info	Single
		{	LureType 		U8	 			}
		{	Message			Variable	1	}
	}
	{
		TargetData Variable
		{	TargetID		LLUUID			}
	}
}

// TeleportLureRequest viewer->sim
// Message from target of lure to begin the teleport process on the 
// local simulator.
{
	TeleportLureRequest	Low	71 NotTrusted Unencoded
	{
		Info	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	LureID		LLUUID	}
		{	TeleportFlags 	U32				}
	}
}

// TeleportCancel viewer->sim
// reliable
{
	TeleportCancel	Low	72 NotTrusted Unencoded
	{
		Info	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
}


// TeleportStart sim->viewer
// announce a successful teleport request to the viewer.
{
	TeleportStart Low 73 Trusted Unencoded
	{
		Info	Single
		{	TeleportFlags	U32		}
	}
}

// TeleportFailed somewhere->sim->viewer
// announce failure of teleport request
{
	TeleportFailed Low 74 Trusted Unencoded
	{
		Info		Single
		{	AgentID		LLUUID			}
		{	Reason		Variable	1	}  // string
	}
	{
		AlertInfo			Variable
		{	Message			Variable	1	}	// string id
		{	ExtraParams		Variable	1	}	// llsd extra parameters
	}
}


// ***************************************************************************
// Viewer to Simulator Messages
// ***************************************************************************

// Undo
{
	Undo Low 75 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectID	LLUUID	}
	}
}


// Redo
{
	Redo Low 76 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectID	LLUUID	}
	}
}

// UndoLand
{
	UndoLand Low 77 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
}


// AgentPause - viewer occasionally will block, inform simulator of this fact
{
	AgentPause Low 78 NotTrusted Unencoded
	{
		AgentData			Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	SerialNum	U32		}	// U32, used by both pause and resume. Non-increasing numbers are ignored.
	}
}

// AgentResume - unblock the agent
{
	AgentResume Low 79 NotTrusted Unencoded
	{
		AgentData			Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	SerialNum	U32		}	// U32, used by both pause and resume. Non-increasing numbers are ignored.
	}
}


// AgentUpdate - Camera info sent from viewer to simulator
// or, more simply, two axes and compute cross product
// State data is temporary, indicates current behavior state:
//	0 = walking
//  1 = mouselook
//  2 = typing 
//  
// Center is region local (JNC 8.16.2001)
// Camera center is region local (JNC 8.29.2001)
{
	AgentUpdate High 4 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
		{	BodyRotation	LLQuaternion	}
		{	HeadRotation	LLQuaternion	}
		{	State			U8	}
		{	CameraCenter	LLVector3	}
		{	CameraAtAxis	LLVector3	}
		{	CameraLeftAxis	LLVector3	}
		{	CameraUpAxis	LLVector3	}
		{	Far				F32	}
		{	ControlFlags	U32	}
		{	Flags			U8	}
	}
}

// ChatFromViewer
// Specifies the text to be said and the "type", 
// normal speech, shout, whisper.
// with the specified radius
{
	ChatFromViewer Low 80 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
	}
	{
		ChatData			Single
		{	Message			Variable 2	}
		{	Type			U8			}
		{	Channel			S32			}
	}
}


// AgentThrottle
{
	AgentThrottle Low 81 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
		{	CircuitCode		U32		}
	}
	{
		Throttle			Single
		{	GenCounter		U32		}
		{	Throttles		Variable 1	}
	}
}


// AgentFOV - Update to agent's field of view, angle is vertical, single F32 float in radians
{
	AgentFOV Low 82 NotTrusted Unencoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
		{	CircuitCode		U32		}
	}
	{
		FOVBlock			Single
		{	GenCounter		U32		}
		{	VerticalAngle	F32	}
	}
}


// AgentHeightWidth - Update to height and aspect, sent as height/width to save space
// Usually sent when window resized or created
{
	AgentHeightWidth Low 83 NotTrusted Unencoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
		{	CircuitCode		U32		}
	}
	{
		HeightWidthBlock	Single
		{	GenCounter		U32		}
		{	Height			U16	}
		{	Width			U16	}
	}
}


// AgentSetAppearance - Update to agent appearance
{
	AgentSetAppearance Low 84 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
		{	SerialNum		U32	}	// U32, Increases every time the appearance changes. A value of 0 resets.
		{ 	Size			LLVector3	}
	}
	{
		WearableData		Variable
		{	CacheID			LLUUID }
		{	TextureIndex	U8 }
	}
	{
		ObjectData			Single
		{	TextureEntry	Variable	2	}
	}
	{
		VisualParam			Variable
		{	ParamValue		U8	}
	}
}

// AgentAnimation - Update animation state
// viewer --> simulator
{
	AgentAnimation High 5 NotTrusted Unencoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
	}
	{
		AnimationList Variable
		{ AnimID		LLUUID }
		{ StartAnim		BOOL }
	}
	{
		PhysicalAvatarEventList Variable
		{ TypeData		Variable	1 }
	}
}

// AgentRequestSit - Try to sit on an object
{
	AgentRequestSit		High 6  NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
	}
	{
		TargetObject	Single
		{	TargetID	LLUUID	}
		{	Offset		LLVector3	}
	}
}

// AgentSit - Actually sit on object
{
	AgentSit			High 7  NotTrusted Unencoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
	}
}


// quit message sent between simulators
{
	AgentQuitCopy Low 85 NotTrusted Unencoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
	}
	{
		FuseBlock			Single
		{	ViewerCircuitCode	U32	}
	}
}


// Request Image - Sent by the viewer to request a specified image at a specified resolution

{
	RequestImage High 8 NotTrusted Unencoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}
		{	SessionID		LLUUID		}
	}
	{
		RequestImage			Variable
		{	Image				LLUUID	}
		{	DiscardLevel		S8	}
		{	DownloadPriority	F32	}
		{	Packet				U32	}
		{	Type				U8	}
	}
}

// ImageNotInDatabase
// Simulator informs viewer that a requsted image definitely does not exist in the asset database
{
	ImageNotInDatabase Low 86 Trusted Unencoded
	{
		ImageID				Single
		{	ID				LLUUID	}
	}
}

// RebakeAvatarTextures
// simulator -> viewer request when a temporary baked avatar texture is not found
{
	RebakeAvatarTextures Low 87 Trusted Unencoded
	{
		TextureData			Single
		{	TextureID		LLUUID	}
	}
}


// SetAlwaysRun
// Lets the viewer choose between running and walking
{
	SetAlwaysRun Low 88 NotTrusted Unencoded
	{
		AgentData				Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
		{	AlwaysRun		BOOL	}
	}
}

// ObjectAdd - create new object in the world
// Simulator will assign ID and send message back to signal
// object actually created.
//
// AddFlags (see also ObjectUpdate)
// 0x01 - use physics
// 0x02 - create selected
//
// If only one ImageID is sent for an object type that has more than
// one face, the same image is repeated on each subsequent face.
// 
// Data field is opaque type-specific data for this object
{
	ObjectAdd Medium 1 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID			LLUUID	}
	}
	{
		ObjectData			Single
		{	PCode			U8	}
		{	Material		U8	}
		{	AddFlags		U32	}	// see object_flags.h

		{	PathCurve		U8	}
		{	ProfileCurve	U8	}
		{	PathBegin		U16	}	// 0 to 1, quanta = 0.01
		{	PathEnd			U16	}	// 0 to 1, quanta = 0.01
		{	PathScaleX		U8	}	// 0 to 1, quanta = 0.01
		{	PathScaleY		U8	}	// 0 to 1, quanta = 0.01
		{	PathShearX		U8	}	// -.5 to .5, quanta = 0.01
		{	PathShearY		U8	}	// -.5 to .5, quanta = 0.01
		{	PathTwist		S8	}	// -1 to 1, quanta = 0.01
		{	PathTwistBegin		S8	}	// -1 to 1, quanta = 0.01
		{ 	PathRadiusOffset 	S8	} 	// -1 to 1, quanta = 0.01
		{ 	PathTaperX		S8	}	// -1 to 1, quanta = 0.01
		{	PathTaperY		S8	}	// -1 to 1, quanta = 0.01
		{	PathRevolutions		U8	}	// 0 to 3, quanta = 0.015
		{	PathSkew		S8	}	// -1 to 1, quanta = 0.01
		{	ProfileBegin	U16	}	// 0 to 1, quanta = 0.01
		{	ProfileEnd		U16	}	// 0 to 1, quanta = 0.01
		{	ProfileHollow	U16	}	// 0 to 1, quanta = 0.01

		{	BypassRaycast	U8	}
		{	RayStart		LLVector3	}
		{	RayEnd			LLVector3	}
		{	RayTargetID		LLUUID	}
		{	RayEndIsIntersection	U8	}

		{	Scale			LLVector3	}
		{	Rotation		LLQuaternion	}

		{	State			U8	}
	}
}


// ObjectDelete
// viewer -> simulator
{
	ObjectDelete Low 89 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	Force		BOOL	}	// BOOL, god trying to force delete
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}
}


// ObjectDuplicate
// viewer -> simulator
// Makes a copy of a set of objects, offset by a given amount
{
	ObjectDuplicate Low 90 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		SharedData			Single
		{	Offset			LLVector3	}
		{	DuplicateFlags	U32			}	// see object_flags.h
	}
	{
		ObjectData			Variable
		{	ObjectLocalID		U32		}
	}
}


// ObjectDuplicateOnRay
// viewer -> simulator
// Makes a copy of an object, using the add object raycast
// code to abut it to other objects.
{
	ObjectDuplicateOnRay Low 91 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID					LLUUID	}
		{	SessionID				LLUUID	}
		{	GroupID					LLUUID	}
		{	RayStart				LLVector3	}	// region local
		{	RayEnd					LLVector3	}	// region local
		{	BypassRaycast			BOOL	}
		{	RayEndIsIntersection	BOOL	}
		{	CopyCenters				BOOL	}
		{	CopyRotates				BOOL	}
		{	RayTargetID				LLUUID	}
		{	DuplicateFlags			U32		}	// see object_flags.h
	}
	{
		ObjectData			Variable
		{	ObjectLocalID			U32		}
	}
}


// MultipleObjectUpdate
// viewer -> simulator
// updates position, rotation and scale in one message
// positions sent as region-local floats
{
	MultipleObjectUpdate Medium 2 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData		Variable 
		{	ObjectLocalID	U32		}
		{   Type			U8		}
		{	Data			Variable	1	}	// custom type
	}
}

// RequestMultipleObjects
// viewer -> simulator
// reliable
//
// When the viewer gets a local_id/crc for an object that
// it either doesn't have, or doesn't have the current version
// of, it sends this upstream get get an update.
//
// CacheMissType 0 => full object (viewer doesn't have it)
// CacheMissType 1 => CRC mismatch only
{
	RequestMultipleObjects Medium 3 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData	Variable 
		{	CacheMissType	U8	}
		{	ID				U32	}
	}
}


// DEPRECATED: ObjectPosition
// == Old Behavior ==
// Set the position on objects
//
// == Reason for deprecation ==
// Unused code path was removed in the move to Havok4
// Object position, scale and rotation messages were already unified
// to MultipleObjectUpdate and this message was unused cruft.
//
// == New Location ==
// MultipleObjectUpdate can be used instead.
{
	ObjectPosition Medium 4 NotTrusted Zerocoded Deprecated
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32			}
		{	Position		LLVector3	}	// region
	}
}


// DEPRECATED: ObjectScale
// == Old Behavior ==
// Set the scale on objects
//
// == Reason for deprecation ==
// Unused code path was removed in the move to Havok4
// Object position, scale and rotation messages were already unified
// to MultipleObjectUpdate and this message was unused cruft.
//
// == New Location ==
// MultipleObjectUpdate can be used instead.
{
	ObjectScale Low 92 NotTrusted Zerocoded Deprecated
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32			}
		{	Scale			LLVector3	}
	}
}


// ObjectRotation
// viewer -> simulator
{
	ObjectRotation Low 93 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32				}
		{	Rotation		LLQuaternion	}
	}
}


// ObjectFlagUpdate
// viewer -> simulator
{
	ObjectFlagUpdate Low 94 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	ObjectLocalID	U32		}
		{	UsePhysics		BOOL	}
		{	IsTemporary		BOOL	}
		{	IsPhantom		BOOL	}
		{	CastsShadows	BOOL	}
	}
}


// ObjectClickAction
// viewer -> simulator
{
	ObjectClickAction Low 95 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32		}
		{	ClickAction		U8		}
	}
}


// ObjectImage
// viewer -> simulator
{
	ObjectImage Low 96 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData			Variable
		{	ObjectLocalID		U32				}
		{	MediaURL			Variable	1	}
		{	TextureEntry		Variable	2	}
	}
}


{
	ObjectMaterial Low 97 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
		{	Material	U8	}
	}
}


{
	ObjectShape Low 98 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData			Variable
		{	ObjectLocalID	U32	}
		{	PathCurve		U8	}
		{	ProfileCurve	U8	}
		{	PathBegin		U16	}	// 0 to 1, quanta = 0.01
		{	PathEnd			U16	}	// 0 to 1, quanta = 0.01
		{	PathScaleX		U8	}	// 0 to 1, quanta = 0.01
		{	PathScaleY		U8	}	// 0 to 1, quanta = 0.01
		{	PathShearX		U8	}	// -.5 to .5, quanta = 0.01
		{	PathShearY		U8	}	// -.5 to .5, quanta = 0.01
		{	PathTwist		S8	}	// -1 to 1, quanta = 0.01
		{	PathTwistBegin		S8	}	// -1 to 1, quanta = 0.01
		{ 	PathRadiusOffset 	S8	} 	// -1 to 1, quanta = 0.01
		{ 	PathTaperX		S8	}	// -1 to 1, quanta = 0.01
		{	PathTaperY		S8	}	// -1 to 1, quanta = 0.01
		{	PathRevolutions		U8	}	// 0 to 3, quanta = 0.015
		{	PathSkew		S8	}	// -1 to 1, quanta = 0.01
		{	ProfileBegin	U16	}	// 0 to 1, quanta = 0.01
		{	ProfileEnd		U16	}	// 0 to 1, quanta = 0.01
		{	ProfileHollow	U16	}	// 0 to 1, quanta = 0.01
	}
}

{
	ObjectExtraParams Low 99 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData			Variable
		{	ObjectLocalID	U32				}
		{	ParamType		U16				}
		{	ParamInUse		BOOL			}
		{	ParamSize		U32				}
		{	ParamData		Variable	1	}
	}
}


// ObjectOwner
// To make public, set OwnerID to LLUUID::null.
// TODO: Eliminate god-bit. Maybe not. God-bit is ok, because it's
// known on the server.
{
	ObjectOwner Low 100 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		HeaderData		Single
		{	Override	BOOL	}	// BOOL, God-bit.
		{	OwnerID		LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		ObjectData	Variable
		{	ObjectLocalID	U32	}
	}
}

// ObjectGroup
// To make the object part of no group, set GroupID = LLUUID::null.
// This call only works if objectid.ownerid == agentid.
{
	ObjectGroup	Low	101 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
	}
	{
		ObjectData	Variable
		{	ObjectLocalID	U32	}
	}
}

// Attempt to buy an object. This will only pack root objects.
{
	ObjectBuy Low 102 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	GroupID		LLUUID	}
		{	CategoryID	LLUUID	}	// folder where it goes (if derezed)
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
		{	SaleType		U8	}   // U8 -> EForSale
		{	SalePrice		S32	}
	}
}

// viewer -> simulator

// buy object inventory. If the transaction succeeds, it will add
// inventory to the agent, and potentially remove the original.
{
	BuyObjectInventory	Low	103 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		Data	Single
		{	ObjectID	LLUUID	}
		{	ItemID		LLUUID	}
		{	FolderID	LLUUID	}
	}
}

// sim -> viewer
// Used to propperly handle buying asset containers
{
	DerezContainer		Low	104 	Trusted Zerocoded
	{
		Data			Single
		{	ObjectID	LLUUID	}
		{	Delete		BOOL	}  // BOOL
	}
}

// ObjectPermissions
// Field - see llpermissionsflags.h
// If Set is true, tries to turn on bits in mask.
// If set is false, tries to turn off bits in mask.
// BUG: This just forces the permissions field.
{
	ObjectPermissions Low 105 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		HeaderData		Single
		{	Override	BOOL	}	// BOOL, God-bit.
	}
	{
		ObjectData	Variable
		{	ObjectLocalID	U32	}
		{	Field		U8	}
		{	Set			U8	}
		{	Mask		U32	}
	}
}

// set object sale information
{
	ObjectSaleInfo Low 106 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData			Variable
		{	LocalID			U32	}
		{	SaleType		U8	}   // U8 -> EForSale
		{	SalePrice		S32	}
	}
}


// set object names
{
	ObjectName Low 107 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	LocalID		U32	}
		{	Name		Variable	1	}
	}
}

// set object descriptions
{
	ObjectDescription Low 108 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	LocalID		U32	}
		{	Description	Variable	1	}
	}
}

// set object category
{
	ObjectCategory Low 109 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	LocalID		U32	}
		{	Category	U32	}
	}
}

// ObjectSelect
// Variable object data because rectangular selection can
// generate a large list very quickly.
{
	ObjectSelect Low 110 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}

}


// ObjectDeselect
{
	ObjectDeselect Low 111 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}

}

// ObjectAttach
{
	ObjectAttach Low 112 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	AttachmentPoint	U8	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32				}
		{	Rotation		LLQuaternion	}
	}
}

// ObjectDetach -- derezzes an attachment, marking its item in your inventory as not "(worn)"
{
	ObjectDetach Low 113 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}
}


// ObjectDrop -- drops an attachment from your avatar onto the ground
{
	ObjectDrop Low 114 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}
}


// ObjectLink
{
	ObjectLink Low 115 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}
}

// ObjectDelink
{
	ObjectDelink Low 116 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Variable
		{	ObjectLocalID	U32	}
	}
}


// ObjectGrab
{
	ObjectGrab Low 117 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData			Single
		{	LocalID				U32  }
		{	GrabOffset			LLVector3 }
	}
	{
		SurfaceInfo     Variable
		{   UVCoord     LLVector3 }
		{   STCoord     LLVector3 }
       	{   FaceIndex   S32 }
       	{   Position    LLVector3 }
       	{   Normal      LLVector3 }
       	{   Binormal    LLVector3 }
	}
}


// ObjectGrabUpdate
// TODO: Quantize this data, reduce message size.
// TimeSinceLast could go to 1 byte, since capped
// at 100 on sim.
{
	ObjectGrabUpdate Low 118 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData	Single
		{	ObjectID			LLUUID	}
		{	GrabOffsetInitial	LLVector3	}	// LLVector3
		{	GrabPosition		LLVector3	}	// LLVector3, region local
		{	TimeSinceLast		U32	}
	}
	{
		SurfaceInfo     Variable
		{   UVCoord     LLVector3 }
		{   STCoord     LLVector3 }
       	{   FaceIndex   S32 }
       	{   Position    LLVector3 }
       	{   Normal      LLVector3 }
       	{   Binormal    LLVector3 }
	}

}


// ObjectDeGrab				
{
	ObjectDeGrab Low 119 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData			Single
		{	LocalID				U32  }
	}
	{
		SurfaceInfo     Variable
		{   UVCoord     LLVector3 }
		{   STCoord     LLVector3 }
       	{   FaceIndex   S32 }
       	{   Position    LLVector3 }
       	{   Normal      LLVector3 }
       	{   Binormal    LLVector3 }
	}
}


// ObjectSpinStart
{
	ObjectSpinStart Low 120 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData			Single
		{	ObjectID		LLUUID	}
	}
}


// ObjectSpinUpdate
{
	ObjectSpinUpdate Low 121 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData			Single
		{	ObjectID		LLUUID	}
		{	Rotation		LLQuaternion }
	}
}


// ObjectSpinStop
{
	ObjectSpinStop Low 122 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ObjectData			Single
		{	ObjectID		LLUUID	}
	}
}

// Export selected objects
// viewer->sim
{
	ObjectExportSelected Low 123 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	RequestID		LLUUID  }
		{	VolumeDetail	S16		}
	}
	{
		ObjectData			Variable
		{	ObjectID		LLUUID	}
	}
}


// ModifyLand - sent to modify a piece of land on a simulator.
// viewer -> sim
{
	ModifyLand Low 124 NotTrusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		ModifyBlock			Single
		{	Action			U8	}
		{	BrushSize		U8	}
		{	Seconds			F32	}
		{	Height			F32	}
	}
	{
		ParcelData			Variable
		{	LocalID			S32		}
		{	West			F32		}
		{	South			F32		}
		{	East			F32		}
		{	North			F32		}
	}
	{
		ModifyBlockExtended Variable
		{   BrushSize       F32 }
	}
}


// VelocityInterpolateOn
// viewer->sim
// requires administrative access
{
	VelocityInterpolateOn Low 125 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID		LLUUID	}
	}
}


// VelocityInterpolateOff
// viewer->sim
// requires administrative access
{
	VelocityInterpolateOff Low 126 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID		LLUUID	}
	}
}

// Save State
// viewer->sim
// requires administrative access
{
	StateSave Low 127 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		DataBlock		Single
		{	Filename	Variable	1	}
	}
}

// ReportAutosaveCrash
// sim->launcher
{
	ReportAutosaveCrash Low 128 NotTrusted Unencoded
	{
		AutosaveData	Single
		{	PID		S32	}
		{	Status	S32 }
	}
}

// SimWideDeletes
{
	SimWideDeletes Low 129 NotTrusted Unencoded
	{
		AgentData			Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		DataBlock			Single
		{	TargetID		LLUUID	}
		{	Flags			U32	}
	}
}

// RequestObjectPropertiesFamily
// Ask for extended information, such as creator, permissions, resources, etc.
// Medium frequency because it is driven by mouse hovering over objects, which
// occurs at high rates.
{
	RequestObjectPropertiesFamily Medium 5 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ObjectData		Single
		{	RequestFlags		U32	}
		{	ObjectID			LLUUID	}
	}
}


// Track agent - this information is used when sending out the
// coarse location update so that we know who you are tracking. 
// To stop tracking - send a null uuid as the prey.
{
	TrackAgent		Low	130 	NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		TargetData		Single
		{	PreyID		LLUUID	}
	}
}

// end viewer to simulator section

{
       ViewerStats Low 131 NotTrusted Zerocoded UDPDeprecated
       {
               AgentData                       Single
               {       AgentID                 LLUUID      }
               {       SessionID               LLUUID      }
               {       IP                      IPADDR       }
               {       StartTime               U32       }
               {       RunTime                 F32       }  // F32
               {       SimFPS                  F32       }  // F32
               {       FPS                     F32       }  // F32
               {       AgentsInView			   U8 } //
               {       Ping                    F32       }  // F32
               {       MetersTraveled  F64       }
               {       RegionsVisited  S32       }
               {       SysRAM                  U32       }
               {       SysOS                   Variable        1       }  // String
               {       SysCPU                  Variable        1       }  // String
               {       SysGPU                  Variable        1       }  // String
       }

       {
               DownloadTotals          Single
               {       World                   U32       }
               {       Objects                 U32       }
               {       Textures                U32       }
       }

       {
               NetStats                        Multiple        2
               {       Bytes                   U32       }
               {       Packets                 U32       }
               {       Compressed              U32       }
               {       Savings                 U32       }
       }

       {       
               FailStats                       Single
               {       SendPacket              U32       }
               {       Dropped                 U32       }
               {       Resent                  U32       }
               {       FailedResends   U32       }
               {       OffCircuit              U32       }
               {       Invalid                 U32       }
       }

       {
               MiscStats                       Variable
               {       Type                    U32       }
               {       Value                   F64       }
       }
}
		
// ScriptAnswerYes
// reliable
{
	ScriptAnswerYes Low 132 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}			   
	{
		Data	Single
		{	TaskID			LLUUID	}
		{	ItemID			LLUUID	}
		{	Questions		S32	}
	}
}


// complaint/bug-report
// reliable
{
	UserReport	Low	133 	NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		ReportData	Single
		{   ReportType		U8   }   // BUG=1, COMPLAINT=2
		{   Category		U8   }   // see sequence.user_report_category
		{	Position		LLVector3	} // screenshot position, region-local
		{   CheckFlags		U8	} // checkboxflags
		{   ScreenshotID	LLUUID  }
		{   ObjectID		LLUUID  }
		{   AbuserID		LLUUID  }
		{	AbuseRegionName	Variable	1	}
		{	AbuseRegionID	LLUUID	}
		{   Summary			Variable	1   }
		{   Details 		Variable	2   }
		{	VersionString	Variable	1	}
	}
}


// ***************************************************************************
// Simulator to Viewer Messages
// ***************************************************************************

// AlertMessage
// Specifies the text to be posted in an alert dialog
{
	AlertMessage Low 134 Trusted Unencoded
	{
		AlertData			Single
		{	Message			Variable	1	}
	}
	{
		AlertInfo			Variable
		{	Message			Variable	1	}
		{	ExtraParams		Variable	1	}
	}
}

// Send an AlertMessage to the named agent.
// usually dataserver->simulator
{
	AgentAlertMessage	Low	135 Trusted	Unencoded
	{
		AgentData	Single
		{	AgentID		LLUUID	}
	}
	{
		AlertData			Single
		{	Modal			BOOL			}
		{	Message			Variable	1	}
	}
}


// MeanCollisionAlert
// Specifies the text to be posted in an alert dialog
{
	MeanCollisionAlert Low 136 Trusted Zerocoded
	{
		MeanCollision		Variable
		{	Victim			LLUUID	}
		{	Perp			LLUUID	}
		{	Time			U32		}
		{	Mag				F32		}
		{	Type			U8		}
	}
}

// ViewerFrozenMessage
// Specifies the text to be posted in an alert dialog
{
	ViewerFrozenMessage Low 137 Trusted Unencoded
	{
		FrozenData			Single
		{	Data			BOOL	}
	}
}

// Health Message
// Tells viewer what agent health is
{
	HealthMessage Low 138 Trusted Zerocoded
	{
		HealthData			Single
		{	Health			F32	}
	}
}

// ChatFromSimulator
// Chat text to appear on a user's screen
// Position is region local.
// Viewer can optionally use position to animate
// If audible is CHAT_NOT_AUDIBLE, message will not be valid
{
	ChatFromSimulator Low 139 Trusted Unencoded
	{
		ChatData			Single
		{	FromName		Variable 1	}
		{	SourceID		LLUUID		}	// agent id or object id
		{	OwnerID			LLUUID		}	// object's owner
		{	SourceType		U8			}
		{	ChatType		U8			}
		{	Audible			U8			}
		{	Position		LLVector3	}
		{	Message			Variable 2	}	// UTF-8 text
	}
}


// Simulator statistics packet (goes out to viewer and dataserver/spaceserver)
{
	SimStats Low 140 Trusted Unencoded
	{
		Region Single
		{	RegionX				U32				}
		{	RegionY				U32				}
		{	RegionFlags			U32				}
		{	ObjectCapacity		U32				}
	}
	{
		Stat	Variable
		{	StatID		U32	}
		{	StatValue	F32	}
	}
	{
		PidStat Single
		{	PID					S32				}
	}
}

// viewer -> sim
// reliable
{
	RequestRegionInfo Low 141 NotTrusted Unencoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID		LLUUID			}
	}
}

// RegionInfo
// Used to populate UI for both region/estate floater
// and god tools floater
// sim -> viewer
// reliable
{
	RegionInfo Low 142 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID		LLUUID			}
	}
	{
		RegionInfo	Single
		{	SimName			Variable	1	}	// string
		{	EstateID		U32				}
		{	ParentEstateID	U32				}
		{	RegionFlags		U32				}
		{	SimAccess		U8				}
		{	MaxAgents		U8				}
		{	BillableFactor		F32			}
		{	ObjectBonusFactor 	F32			}
		{	WaterHeight			F32			}
		{   TerrainRaiseLimit	F32 		}
		{	TerrainLowerLimit	F32 		}
		{	PricePerMeter 		S32			}
		{	RedirectGridX 		S32			}
		{	RedirectGridY 		S32			}
		{	UseEstateSun		BOOL		}
		{	SunHour				F32			}	// last value set by estate or region controls JC
	}
	{
		RegionInfo2		Single
		{	ProductSKU			Variable 1	}	// string
		{	ProductName			Variable 1	}	// string
		{	MaxAgents32			U32			}	// Identical to RegionInfo.MaxAgents but allows greater range
		{	HardMaxAgents		U32			}
		{	HardMaxObjects		U32			}
	}
}

// GodUpdateRegionInfo
// Sent from viewer to sim after a god has changed some
// of the parameters in the god tools floater
// viewer -> sim
// reliable
{
	GodUpdateRegionInfo Low 143 NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID		LLUUID			}
	}
	{
		RegionInfo	Single
		{	SimName			Variable	1	}	// string
		{	EstateID		U32				}
		{	ParentEstateID	U32				}
		{	RegionFlags		U32				}
		{	BillableFactor		F32			}
		{	PricePerMeter 		S32			}
		{	RedirectGridX 		S32			}
		{	RedirectGridY 		S32			}
	}
}

//NearestLandingRegionRequest
//sim->dataserver
//Sent from the region to the data server
//to request the most up to date region for the requesting
//region to redirect teleports to
{
	NearestLandingRegionRequest Low 144 Trusted Unencoded
	{
		RequestingRegionData Single
		{	RegionHandle 		U64			}
	}
}

//NearestLandingPointReply
//dataserver->sim
//Sent from the data server to a region in reply
//to the redirectregion request stating which region
//the requesting region should redirect teleports to if necessary
{
	NearestLandingRegionReply Low 145 Trusted Unencoded
	{
		LandingRegionData Single
		{	RegionHandle		U64			}
	}
}

//NearestLandingPointUpdated
//sim->dataserver
//Sent from a region to the data server
//to have the dataserver note/clear in the db
//that the region has updated it's nearest landing point
{
	NearestLandingRegionUpdated Low 146 Trusted Unencoded
	{
		RegionData Single
		{	RegionHandle		U64			}
	}
}


//TeleportLandingStatusChanged
//sim->dataserver
//Sent from the region to the data server
//to note that the region's teleportation landing status has changed
{
	TeleportLandingStatusChanged Low 147 Trusted Unencoded
	{
		RegionData Single
		{	RegionHandle		U64			}
	}
}

// RegionHandshake
// Sent by region to viewer after it has received UseCircuitCode
// from that viewer.
// sim -> viewer
// reliable
{
	RegionHandshake			Low	148 	Trusted Zerocoded
	{
		RegionInfo	Single
		{	RegionFlags		U32	}
		{	SimAccess		U8	}
		{	SimName			Variable	1	} // string
		{	SimOwner		LLUUID	}
		{	IsEstateManager	BOOL	}	// this agent, for this sim
		{	WaterHeight		F32	}
		{	BillableFactor	F32	}
		{	CacheID			LLUUID }
		{	TerrainBase0		LLUUID		}
		{	TerrainBase1		LLUUID		}
		{	TerrainBase2		LLUUID		}
		{	TerrainBase3		LLUUID		}
		{	TerrainDetail0		LLUUID		}
		{	TerrainDetail1		LLUUID		}
		{	TerrainDetail2		LLUUID		}
		{	TerrainDetail3		LLUUID		}
		{	TerrainStartHeight00	F32		}
		{	TerrainStartHeight01	F32		}
		{	TerrainStartHeight10	F32		}
		{	TerrainStartHeight11	F32		}
		{	TerrainHeightRange00	F32		}
		{	TerrainHeightRange01	F32		}
		{	TerrainHeightRange10	F32		}
		{	TerrainHeightRange11	F32		}
	}
	{
		RegionInfo2	Single
		{	RegionID		LLUUID	}
	}
	{
		RegionInfo3	Single
		{	CPUClassID				S32		}
		{	CPURatio				S32		}
		{	ColoName				Variable	1	}	// string
		{	ProductSKU				Variable	1	}	// string
		{	ProductName				Variable	1	}	// string
	}
}

// RegionHandshakeReply
// viewer -> sim
// reliable
// Sent after viewer has initialized the (pre-existing)
// LLViewerRegion with the name, access level, etc. and
// has loaded the cache for the region.
// After the simulator receives this, it will start sending
// data about objects.
{
	RegionHandshakeReply			Low	149 	NotTrusted Zerocoded
	{
		AgentData	Single
		{	AgentID			LLUUID			}
		{	SessionID		LLUUID			}
	}
	{
		RegionInfo	Single
		{	Flags			U32		}
	}
}

// The CoarseLocationUpdate message is sent to notify the viewer of 
// the location of mappable objects in the region. 1 meter resolution is
// sufficient for this. The index block is used to show where you are, 
// and where someone you are tracking is located. They are -1 if not
// applicable.
{
	CoarseLocationUpdate Medium 6 Trusted Unencoded
	{
		Location	Variable
		{	X		U8	}
		{	Y		U8	}
		{	Z		U8	}	// Z in meters / 4
	}
	{
		Index 		Single
		{	You		S16	}
		{	Prey	S16	}
	}
    {
         AgentData       Variable
         {       AgentID                 LLUUID                  }
    }
}

// ImageData - sent to viewer to transmit information about an image 
{
	ImageData High 9 Trusted Unencoded
	{
		ImageID				Single
		{	ID				LLUUID	}
		{	Codec			U8	}
		{	Size			U32	}
		{	Packets			U16	}
	}
	{
		ImageData			Single
		{	Data			Variable	2	}
	}
}

// ImagePacket - follow on image data for images having > 1 packet of data 
{
	ImagePacket High 10 Trusted Unencoded
	{
		ImageID				Single
		{	ID				LLUUID	}
		{	Packet			U16	}
	}
	{
		ImageData			Single
		{	Data			Variable	2	}
	}
}

// LayerData - Sent to viewer - encodes layer data

{
	LayerData High 11 Trusted Unencoded
	{
		LayerID				Single
		{	Type			U8	}

	}
	{
		LayerData			Single
		{	Data			Variable	2	}
	}
}

// ObjectUpdate - Sent by objects from the simulator to the viewer
//
// If only one ImageID is sent for an object type that has more than
// one face, the same image is repeated on each subsequent face.
// 
// NameValue is a list of name-value strings, separated by \n characters,
// terminated by \0
//
// Data is type-specific opaque data for this object
{
	ObjectUpdate High 12 Trusted Zerocoded
	{
		RegionData			Single
		{	RegionHandle	U64	}
		{   TimeDilation	U16   }
	}
	{
		ObjectData			Variable
		{	ID				U32	}
		{	State			U8	}

		{	FullID			LLUUID	}
		{	CRC				U32	}	// TEMPORARY HACK FOR JAMES
		{	PCode			U8	}
		{	Material		U8	}
		{	ClickAction		U8	}
		{	Scale			LLVector3	}
		{	ObjectData		Variable	1	}

		{	ParentID		U32	}
		{	UpdateFlags		U32	}	// U32, see object_flags.h

		{	PathCurve		U8	}
		{	ProfileCurve	U8	}
		{	PathBegin		U16	}	// 0 to 1, quanta = 0.01
		{	PathEnd			U16	}	// 0 to 1, quanta = 0.01
		{	PathScaleX		U8	}	// 0 to 1, quanta = 0.01
		{	PathScaleY		U8	}	// 0 to 1, quanta = 0.01
		{	PathShearX		U8	}	// -.5 to .5, quanta = 0.01
		{	PathShearY		U8	}	// -.5 to .5, quanta = 0.01
		{	PathTwist		S8	}	// -1 to 1, quanta = 0.01
		{	PathTwistBegin		S8	}	// -1 to 1, quanta = 0.01
		{ 	PathRadiusOffset 	S8	} 	// -1 to 1, quanta = 0.01
		{ 	PathTaperX		S8	}	// -1 to 1, quanta = 0.01
		{	PathTaperY		S8	}	// -1 to 1, quanta = 0.01
		{	PathRevolutions		U8	}	// 0 to 3, quanta = 0.015
		{	PathSkew		S8	}	// -1 to 1, quanta = 0.01
		{	ProfileBegin	U16	}	// 0 to 1, quanta = 0.01
		{	ProfileEnd		U16	}	// 0 to 1, quanta = 0.01
		{	ProfileHollow	U16	}	// 0 to 1, quanta = 0.01

		{	TextureEntry	Variable	2	}
		{	TextureAnim		Variable	1	}

		{	NameValue		Variable	2	}
		{	Data			Variable	2	}
		{	Text			Variable	1	}	// llSetText() hovering text
		{	TextColor		Fixed		4	}	// actually, a LLColor4U
		{	MediaURL		Variable	1	}	// URL for web page, movie, etc.

		// Info for particle systems
		{	PSBlock			Variable	1	}
		
		// Extra parameters
		{	ExtraParams		Variable	1	}
		
		// info for looped attached sounds
        // because these are almost always all zero
		// the hit after zero-coding is only 2 bytes
		// not the 42 you see here
		{	Sound           LLUUID  }
		{	OwnerID			LLUUID	}	// HACK object's owner id, only set if non-null sound, for muting
		{	Gain            F32		}
		{	Flags           U8		}
		{	Radius          F32		}  // cutoff radius

		// joint info -- is sent in the update of each joint-child-root
		{	JointType 			U8		}
		{	JointPivot			LLVector3	}
		{	JointAxisOrAnchor 	LLVector3	}
	}
}


// ObjectUpdateCompressed
{
	ObjectUpdateCompressed High 13 Trusted Unencoded
	{
		RegionData			Single
		{	RegionHandle	U64		}
		{   TimeDilation	U16		}
	}
	{
		ObjectData			Variable
		{   UpdateFlags			U32	}
		{	Data			Variable   2	}
	}
}

// ObjectUpdateCached
// reliable
{
	ObjectUpdateCached High 14 Trusted Unencoded
	{
		RegionData			Single
		{	RegionHandle	U64		}
		{   TimeDilation	U16		}
	}
	{
		ObjectData			Variable
		{   ID				U32		}
		{	CRC				U32		}
		{   UpdateFlags		U32	}
	}
}

// packed terse object update format
{
	ImprovedTerseObjectUpdate High 15 Trusted Unencoded
	{
		RegionData			Single
		{	RegionHandle	U64	}
		{   TimeDilation	U16   }
	}
	{
		ObjectData			Variable
		{	Data			Variable	1	}
		{	TextureEntry	Variable	2	}
	}
}

// KillObject - Sent by objects to the viewer to tell them to kill themselves

{
	KillObject High 16 Trusted Unencoded
	{
		ObjectData			Variable
		{	ID				U32	}
	}
}


// CrossedRegion - new way to tell a viewer it has gone across a region 
// boundary
{
	CrossedRegion Medium 7 Trusted Unencoded UDPBlackListed
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
	}
	{
		RegionData		Single
		{	SimIP			IPADDR	}
		{	SimPort			IPPORT	}
		{	RegionHandle	U64	}
		{	SeedCapability	Variable	2	}	// URL
	}
	{
		Info			Single
		{	Position		LLVector3	}
		{	LookAt			LLVector3	}
	}
}

// SimulatorViewerTimeMessage - Allows viewer to resynch to world time

{
	SimulatorViewerTimeMessage Low 150 Trusted Unencoded
	{
		TimeInfo		Single
		{	UsecSinceStart	U64	}
		{	SecPerDay		U32	}
		{	SecPerYear		U32	}
		{	SunDirection	LLVector3	}
		{	SunPhase		F32	}
		{	SunAngVelocity	LLVector3	}
	}
}

// EnableSimulator - Preps a viewer to receive data from a simulator

{
	EnableSimulator Low 151 Trusted Unencoded UDPBlackListed
	{
		SimulatorInfo	Single
		{	Handle		U64	}
		{	IP			IPADDR	}
		{	Port		IPPORT	}
	}
}

// DisableThisSimulator - Tells a viewer not to expect data from this simulator anymore

{
	DisableSimulator Low 152 Trusted Unencoded
}

// ConfirmEnableSimulator - A confirmation message sent from simulator to neighbors that the simulator
// has successfully been enabled by the viewer

{
	ConfirmEnableSimulator Medium 8 Trusted Unencoded
	{
		AgentData				Single
		{	AgentID				LLUUID	}
		{	SessionID			LLUUID	}
	}
}

//-----------------------------------------------------------------------------
// New Transfer system
//-----------------------------------------------------------------------------

// Request a new transfer (target->source)
{
	TransferRequest Low 153 NotTrusted Zerocoded
	{
		TransferInfo		Single
		{	TransferID		LLUUID	}
		{	ChannelType		S32	}
		{	SourceType		S32	}
		{	Priority		F32	}
		{	Params			Variable	2	}
	}
}

// Return info about a transfer/initiate transfer (source->target)
// Possibly should have a Params field like above
{
	TransferInfo Low 154 NotTrusted Zerocoded
	{
		TransferInfo		Single
		{	TransferID		LLUUID	}
		{	ChannelType		S32	}
		{	TargetType		S32	}
		{	Status			S32	}
		{	Size			S32	}
		{	Params			Variable	2	}
	}
}

{
	TransferPacket High 17 NotTrusted Unencoded
	{
		TransferData Single
		{	TransferID	LLUUID	}
		{	ChannelType	S32	}
		{	Packet		S32	}
		{	Status		S32	}
		{	Data		Variable 2	}
	}
}

// Abort a transfer in progress (either from target->source or source->target)
{
	TransferAbort Low 155 NotTrusted Zerocoded
	{
		TransferInfo		Single
		{	TransferID		LLUUID	}
		{	ChannelType		S32	}
	}
}


//-----------------------------------------------------------------------------
// General file transfer
//-----------------------------------------------------------------------------

// RequestXfer - request an arbitrary xfer
{
	RequestXfer Low 156 NotTrusted Zerocoded
	{
		XferID				Single
		{	ID				U64	}
		{	Filename		Variable	1	}
		{	FilePath		U8	} // ELLPath
		{	DeleteOnCompletion BOOL	} // BOOL
		{	UseBigPackets	BOOL	} // BOOL
		{	VFileID			LLUUID	}
		{	VFileType		S16	}
	}
}

// SendXferPacket - send an additional packet of an arbitrary xfer from sim -> viewer 
{
	SendXferPacket High 18 NotTrusted Unencoded
	{
		XferID				Single
		{	ID				U64	}
		{	Packet			U32	}
	}
	{
		DataPacket			Single
		{	Data			Variable	2	}
	}
}

// ConfirmXferPacket
{
	ConfirmXferPacket High 19 NotTrusted Unencoded
	{
		XferID				Single
		{	ID				U64	}
		{	Packet			U32	}
	}
}

// AbortXfer
{
	AbortXfer Low 157 NotTrusted Unencoded
	{
		XferID				Single
		{	ID				U64	}
		{	Result			S32	}
	}
}

//-----------------------------------------------------------------------------
// Avatar information
//-----------------------------------------------------------------------------


// AvatarAnimation - Update animation state
// simulator --> viewer 
{
	AvatarAnimation High 20 Trusted Unencoded
	{
		Sender			Single
		{	ID			LLUUID	}
	}
	{
		AnimationList Variable
		{ AnimID		LLUUID }
		{ AnimSequenceID S32 }
	}
	{
		AnimationSourceList Variable
		{ ObjectID		LLUUID }
	}
	{
		PhysicalAvatarEventList Variable
		{ TypeData		Variable	1 }
	}

}

// AvatarAppearance - Update visual params
{
	AvatarAppearance Low 158 Trusted Zerocoded
	{
		Sender				Single
		{	ID				LLUUID	}
		{	IsTrial			BOOL    }
	}
	{	
		ObjectData			Single
		{	TextureEntry	Variable	2	}
	}
	{
		VisualParam			Variable
		{	ParamValue		U8	}
	}
}

// AvatarSitResponse - response to a request to sit on an object
{
	AvatarSitResponse	High 21 Trusted Zerocoded
	{
		SitObject			Single
		{	ID				LLUUID	}
	}
	{
		SitTransform		Single
		{	AutoPilot		BOOL }
		{	SitPosition		LLVector3	}
		{	SitRotation		LLQuaternion	}
		{	CameraEyeOffset	LLVector3	}
		{	CameraAtOffset	LLVector3	}
		{	ForceMouselook	BOOL }
	}
}

// SetFollowCamProperties
{ 
	SetFollowCamProperties		Low	159 Trusted	Unencoded
	{
		ObjectData			Single
		{	ObjectID				LLUUID	}
	}
	{
		CameraProperty	Variable
		{ 	Type 	S32 }
		{ 	Value 	F32 }
	}
}

// ClearFollowCamProperties
{
	ClearFollowCamProperties	Low 160 Trusted Unencoded
	{
		ObjectData			Single
		{	ObjectID				LLUUID	}
	}
}

// CameraConstraint - new camera distance limit (based on collision with objects)
{
	CameraConstraint High 22 Trusted Zerocoded
	{
		CameraCollidePlane	Single
		{	Plane		LLVector4 }
	}
}

// ObjectProperties
// Extended information such as creator, permissions, etc.
// Medium because potentially driven by mouse hover events.
{
	ObjectProperties Medium 9 Trusted Zerocoded
	{
		ObjectData			Variable
		{	ObjectID		LLUUID	}
		{	CreatorID		LLUUID	}
		{	OwnerID			LLUUID	}
		{	GroupID			LLUUID	}
		{	CreationDate	U64	}
		{	BaseMask		U32	}
		{	OwnerMask		U32	}
		{	GroupMask		U32	}
		{	EveryoneMask	U32	}
		{	NextOwnerMask	U32	}
		{	OwnershipCost	S32	}
//		{	TaxRate			F32	}	// F32
		{	SaleType		U8	}   // U8 -> EForSale
		{	SalePrice		S32	}
		{	AggregatePerms	U8	}
		{	AggregatePermTextures		U8	}
		{	AggregatePermTexturesOwner	U8	}
		{	Category		U32	}	// LLCategory
		{	InventorySerial	S16	}	// S16
		{	ItemID			LLUUID	}
		{	FolderID		LLUUID	}
		{	FromTaskID		LLUUID	}
		{	LastOwnerID		LLUUID	}
		{	Name			Variable	1	}
		{	Description		Variable	1	}
		{	TouchName		Variable	1	}
		{	SitName			Variable	1	}
		{	TextureID		Variable	1	}
	}
}

// ObjectPropertiesFamily
// Medium because potentially driven by mouse hover events.
{
	ObjectPropertiesFamily Medium 10 Trusted Zerocoded
	{
		ObjectData			Single
		{	RequestFlags	U32	}
		{	ObjectID		LLUUID	}
		{	OwnerID			LLUUID	}
		{	GroupID			LLUUID	}
		{	BaseMask		U32	}
		{	OwnerMask		U32	}
		{	GroupMask		U32	}
		{	EveryoneMask	U32	}
		{	NextOwnerMask	U32	}
		{	OwnershipCost	S32	}
		{	SaleType		U8	}   // U8 -> EForSale
		{	SalePrice		S32	}
		{	Category		U32	}	// LLCategory
		{	LastOwnerID		LLUUID	}
		{	Name			Variable	1	}
		{	Description		Variable	1	}
	}
}

// RequestPayPrice
// viewer -> sim
{
	RequestPayPrice Low 161 NotTrusted Unencoded
	{
		ObjectData		Single
		{	ObjectID	LLUUID	}
	}
}

// PayPriceReply
// sim -> viewer
{
	PayPriceReply Low 162 Trusted Unencoded
	{
		ObjectData		Single
		{	ObjectID	LLUUID }
		{	DefaultPayPrice	S32	}
	}
	{
		ButtonData		Variable
		
		{	PayButton	S32	}
	}
}

// KickUser
// *FIXME*
// Kick off a logged-in user, such as when two people log in with the
// same account name.
// ROUTED dataserver -> userserver -> spaceserver -> simulator -> viewer
// reliable, but that may not matter if a system component is quitting
{
	KickUser Low 163 Trusted Unencoded
	{
		TargetBlock			Single
		{	TargetIP		IPADDR	}	// U32 encoded IP
		{	TargetPort		IPPORT	}
	}
	{
		UserInfo		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
		{	Reason		Variable	2	}	// string
	}
}

// ack sent from the simulator up to the main database so that login
// can continue.
{
	KickUserAck Low 164 Trusted Unencoded
	{
		UserInfo		Single
		{	SessionID	LLUUID	}
		{	Flags		U32		}
	}
}

// GodKickUser
// When a god wants someone kicked
// viewer -> sim
// reliable
{
	GodKickUser Low 165 NotTrusted Unencoded
	{
		UserInfo		Single
		{	GodID			LLUUID	}
		{	GodSessionID	LLUUID	}
		{	AgentID			LLUUID	}
		{	KickFlags		U32	}
		{	Reason			Variable	2	}	// string
	}
}

// SystemKickUser
// user->space, reliable
{
	SystemKickUser	Low	166 Trusted Unencoded
	{
		AgentInfo	Variable
		{	AgentID	LLUUID	}
	}
}

// EjectUser
// viewer -> sim
// reliable
{
	EjectUser	Low	167 	NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		Data		Single
		{	TargetID	LLUUID	}
		{	Flags		U32		}
	}
}

// FreezeUser
// Freeze someone who is on my land.
// viewer -> sim
// reliable
{
	FreezeUser	Low	168 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		Data		Single
		{	TargetID	LLUUID	}
		{	Flags		U32		}
	}
}


// AvatarPropertiesRequest
// viewer -> simulator
// reliable
{
	AvatarPropertiesRequest Low 169 NotTrusted Unencoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	SessionID		LLUUID	}
		{	AvatarID		LLUUID	}
	}
}

// AvatarPropertiesRequestBackend
// simulator -> dataserver
// reliable
{
	AvatarPropertiesRequestBackend Low 170 Trusted Unencoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	AvatarID		LLUUID	}
		{	GodLevel		U8		}
		{	WebProfilesDisabled		BOOL	}
	}
}
// AvatarPropertiesReply
// dataserver -> simulator
// simulator -> viewer
// reliable
{
	AvatarPropertiesReply Low 171 Trusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}	// your id
		{	AvatarID		LLUUID		}	// avatar you're asking about
	}
	{
		PropertiesData		Single
		{	ImageID			LLUUID		}
		{	FLImageID		LLUUID		}
		{	PartnerID		LLUUID		}
		{	AboutText		Variable 2	}	// string, up to 512
		{	FLAboutText		Variable 1	}	// string
		{	BornOn			Variable 1	}	// string
		{	ProfileURL		Variable 1	}	// string
		{	CharterMember	Variable 1	}	// special - usually U8
		{	Flags			U32			}
	}
}

{
	AvatarInterestsReply Low 172 Trusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}	// your id
		{	AvatarID		LLUUID		}	// avatar you're asking about
	}
	{
		PropertiesData		Single
		{	WantToMask		U32			}
		{	WantToText		Variable 1	}	// string
		{	SkillsMask		U32			}
		{	SkillsText		Variable 1	}	// string
		{	LanguagesText	Variable 1	}	// string
	}
}

// AvatarGroupsReply
// dataserver -> simulator
// simulator -> viewer
// reliable
{
	AvatarGroupsReply Low 173 Trusted Zerocoded
	{
		AgentData			Single
		{	AgentID			LLUUID		}	// your id
		{	AvatarID		LLUUID		}	// avatar you're asking about
	}
	{
		GroupData			Variable
		{	GroupPowers			U64			}
		{	AcceptNotices		BOOL		}
		{	GroupTitle			Variable 1	}
		{	GroupID				LLUUID		}
		{	GroupName			Variable 1	}
		{	GroupInsigniaID		LLUUID		}
	}
	{
		NewGroupData		Single
		{	ListInProfile	BOOL		}	// whether group displays in profile
	}
}


// AvatarPropertiesUpdate
// viewer -> simulator
// reliable
{
	AvatarPropertiesUpdate Low 174 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID		LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		PropertiesData	Single
		{	ImageID			LLUUID			}
		{	FLImageID		LLUUID			}
		{	AboutText		Variable	2	}	// string, up to 512
		{	FLAboutText		Variable	1	}
		{	AllowPublish		BOOL			}	// whether profile is externally visible or not
		{	MaturePublish		BOOL		}	// profile is "mature"
		{	ProfileURL		Variable	1	}	// string
	}
}

// AvatarInterestsUpdate
// viewer -> simulator
// reliable
{
	AvatarInterestsUpdate Low 175 NotTrusted Zerocoded
	{
		AgentData		Single
		{	AgentID			LLUUID	}
		{	SessionID	LLUUID	}
	}
	{
		PropertiesData	Single
		{	WantToMask		U32				}
		{	WantToText		Variable	1	}	// string
		{	SkillsMask		U32				}
		{	SkillsText		Variable	1	}	// string
		{	LanguagesText	Variable	1	}	// string	
	}
}

