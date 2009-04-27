# standard python modules
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

# pyogp
from pyogp.lib.base.settings import Settings

# pyogp messaging

# pyogp utilities

# initialize logging
logger = getLogger('pyogp.lib.base.parcel')
log = logger.log

# unhandled related messages
#   ForceObjectSelect
#   ParcelBuyPass
#   ParcelAccessListUpdate
#   ParcelDwellRequest
#   ParcelDwellReply
#   ParcelGodMarkAsContent
#   ViewerStartAuction

# non client oriented related messages
#   #RequestParcelTransfer (sim->dataserver)
#   #UpdateParcel (sim->dataserver)
#   #RemoveParcel (sim->dataserver)
#   #MergeParcel (sim->dataserver)
#   #LogParcelChanges (sim->dataserver)
#   #CheckParcelSales (sim->dataserver)
#   #ParcelSales (dataserver->sim)
#   #StartAuction (sim->dataserver)
#   #ConfirmAuctionStart (dataserver->sim)
#   #CompleteAuction (sim->dataserver)
#   #CancelAuction (sim->dataserver)
#   #CheckParcelAuctions (sim->dataserver)
#   #ParcelAuctions (dataserver->sim)

class ParcelManager(object):
    """ a parcel manager, generally used as an attribute of a region """

    def __init__(self, region, agent, packet_handler, event_system, settings = None):
        """ initialize the parcel manager """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        # store the incoming parameters
        self.region = region
        self.agent = agent
        self.packet_handler = packet_handler
        self.event_system = event_system

        # initialize the parcel storage container
        self.parcels = []

        # set up callbacks for parcel related packets
        self.onParcelOverlay_received = self.packet_handler._register('ParcelOverlay')
        self.onParcelOverlay_received.subscribe(self.onParcelOverlay)

        self.onParcelProperties_received = self.packet_handler._register('ParcelProperties')
        self.onParcelProperties_received.subscribe(self.onParcelProperties)

        self.onParcelPropertiesUpdate_received = self.packet_handler._register('ParcelPropertiesUpdate')
        self.onParcelPropertiesUpdate_received.subscribe(self.onParcelPropertiesUpdate)

    def onParcelOverlay(self, packet):
        """ parse and handle an incoming ParcelOverlay packet """

        pass

        '''
        // ParcelOverlay
        // We send N packets per region to the viewer.
        // N = 4, currently.  At 256x256 meter regions, 4x4 meter parcel grid,
        // there are 4096 parcel units per region.  At N = 4, that's 1024 units
        // per packet, allowing 8 bit bytes.
        // sim -> viewer
        // reliable
        {
        	ParcelOverlay Low 196 Trusted Zerocoded
        	{
        		ParcelData		Single
        		{	SequenceID	S32				}	// 0...3, which piece of region
        		{	Data		Variable	2	}	// packed bit-field, (grids*grids)/N
        	}
        }
        '''

    def onParcelProperties(self, packet):
        """ parse and handle an incoming ParcelProperties packet """

        pass

        '''
        // ParcelProperties
        // sequence id = -1 for parcels that you explicitly selected
        // For agents, sequence id increments every time the agent transits into
        // a new parcel.  It is used to detect out-of-order agent parcel info updates.
        // Bitmap = packed bit field, one bit per parcel grid, on if that grid is
        //        part of the selected parcel.
        // sim -> viewer
        // WARNING: This packet is potentially large.  With max length name,
        // description, music URL and media URL, it is 1526 + sizeof ( LLUUID ) bytes.
        {
        	ParcelProperties High 23 Trusted Zerocoded
        	{
        		ParcelData			Single
        		{	RequestResult	S32				}
        		{	SequenceID		S32				}
        		{	SnapSelection	BOOL			}
        		{	SelfCount		S32				}
        		{	OtherCount		S32				}
        		{	PublicCount		S32				}
        		{	LocalID			S32				}
        		{	OwnerID			LLUUID			}
        		{	IsGroupOwned	BOOL			}
        		{	AuctionID		U32				}
        		{	ClaimDate		S32				}	// time_t
        		{	ClaimPrice		S32				}
        		{	RentPrice		S32				}
        		{	AABBMin			LLVector3		}
        		{	AABBMax			LLVector3		}
        		{	Bitmap			Variable	2	}	// packed bit-field
        		{	Area			S32				}
        		{	Status			U8	}  // owned vs. pending
        		{	SimWideMaxPrims		S32			}
        		{	SimWideTotalPrims	S32			}
        		{	MaxPrims		S32				}
        		{	TotalPrims		S32				}
        		{	OwnerPrims		S32				}
        		{	GroupPrims		S32				}
        		{	OtherPrims		S32				}
        		{	SelectedPrims	S32				}
        		{	ParcelPrimBonus	F32				}

        		{	OtherCleanTime	S32				}

        		{	ParcelFlags		U32				}
        		{	SalePrice		S32				}
        		{	Name			Variable	1	}	// string
        		{	Desc			Variable	1	}	// string
        		{	MusicURL		Variable	1	}	// string
        		{	MediaURL		Variable	1	}	// string
        		{	MediaID			LLUUID			}
        		{	MediaAutoScale	U8				}
        		{	GroupID			LLUUID			}
        		{	PassPrice		S32				}
        		{	PassHours		F32				}
        		{	Category		U8				}
        		{	AuthBuyerID		LLUUID			}
        		{	SnapshotID		LLUUID			}
        		{	UserLocation	LLVector3		}
        		{	UserLookAt		LLVector3		}
        		{	LandingType		U8				}
        		{	RegionPushOverride	BOOL		}
        		{	RegionDenyAnonymous	BOOL		}
        		{	RegionDenyIdentified	BOOL		}
        		{	RegionDenyTransacted	BOOL		}
        	}
        	{
        		AgeVerificationBlock Single
        		{   RegionDenyAgeUnverified BOOL    }
        	}
        }
        '''

    def onParcelPropertiesUpdate(self, packet):
        """ parse and handle an incoming ParcelPropertiesUpdate packet """

        pass

        '''
        // ParcelPropertiesUpdate
        // viewer -> sim
        // reliable
        {
        	ParcelPropertiesUpdate Low 198 NotTrusted Zerocoded
        	{
        		AgentData		Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	Flags			U32				}

        		{	ParcelFlags		U32				}
        		{	SalePrice		S32				}
        		{	Name			Variable	1	}	// string
        		{	Desc			Variable	1	}	// string
        		{	MusicURL		Variable	1	}	// string
        		{	MediaURL		Variable	1	}	// string
        		{	MediaID			LLUUID			}
        		{	MediaAutoScale	U8				}
        		{	GroupID			LLUUID			}
        		{	PassPrice		S32				}
        		{	PassHours		F32				}
        		{	Category		U8				}
        		{	AuthBuyerID		LLUUID			}
        		{	SnapshotID		LLUUID			}
        		{	UserLocation	LLVector3		}
        		{	UserLookAt		LLVector3		}
        		{	LandingType		U8				}
        	}
        }
        '''

    def request_estate_covenant(self, ):
        """ request the estate covenant (for the current estate)"""

        self.onEstateCovenantReply_received = self.packet_handler._register('EstateCovenantReply')
        self.onEstateCovenantReply_received.subscribe(self.onEstateCovenantReply)

        pass

        '''
        // EstateCovenantRequest
        // viewer -> sim
        // reliable
        {
        	EstateCovenantRequest Low 203 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        }
        '''

    def sendEstateCovenantRequest(self):
        """ send an EstateCovenantRequest packet """

        pass

        '''
        // EstateCovenantRequest
        // viewer -> sim
        // reliable
        {
        	EstateCovenantRequest Low 203 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        }
        '''

    def onEstateCovenantReply(self, packet):
        """ parse and handle an EstateCovenantReply packet """

        self.self.onEstateCovenantReply_received.unsubscribe(self.onEstateCovenantReply)

        pass

        '''
        // EstateCovenantReply
        // sim -> viewer
        // reliable
        {
        	EstateCovenantReply Low 204 Trusted Unencoded
        	{
        		Data        Single
        		{	CovenantID		    LLUUID		    }
        		{	CovenantTimestamp	U32 		    }
        		{	EstateName		    Variable    1	}   // string
                {   EstateOwnerID       LLUUID          }
            }
        }
        '''

    def sendParcelPropertiesRequest(self, ):
        """ sends a ParcelPropertiesRequest packet """

        pass

        '''
        // ParcelPropertiesRequest
        // SequenceID should be -1 or -2, and is echoed back in the
        // parcel properties message.
        // viewer -> sim
        // reliable
        {
        	ParcelPropertiesRequest Medium 11 NotTrusted Zerocoded
        	{
        		AgentData		Single
        		{	AgentID		LLUUID	}
        		{	SessionID	LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	SequenceID	S32	}
        		{	West		F32	}
        		{	South		F32	}
        		{	East		F32	}
        		{	North		F32	}
        		{	SnapSelection	BOOL	}
        	}
        }
        '''

    def sendParcelPropertiesRequestByID(self, ):
        """ sends a ParcelPropertiesRequestByID packet """

        pass

        '''
        // ParcelPropertiesRequestByID
        // viewer -> sim
        // reliable
        {
        	ParcelPropertiesRequestByID Low 197 NotTrusted Zerocoded
        	{
        		AgentData		Single
        		{	AgentID		LLUUID	}
        		{	SessionID	LLUUID	}
        	}
        	{
        		ParcelData		Single
        		{	SequenceID	S32		}
        		{	LocalID		S32		}
        	}
        }
        
        '''

    def return_parcel_objects(self, ):
        """ return the specified objects for the specified parcel """

        pass

        '''
        // ParcelReturnObjects
        // viewer -> sim
        // reliable
        {
        	ParcelReturnObjects Low 199 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		TaskIDs			Variable
        		{	TaskID			LLUUID			}
        	}
        	{
        		OwnerIDs			Variable
        		{	OwnerID			LLUUID			}
        	}
        }
        '''

    def disable_objects(self, ):
        """ set objects nonphysical and disable scripts for the specified parcel """

        pass

        '''
        // Disable makes objects nonphysical and turns off their scripts.
        // ParcelDisableObjects
        // viewer -> sim
        // reliable
        {
        	ParcelDisableObjects Low 201 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
            {
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		TaskIDs			Variable
        		{	TaskID			LLUUID			}
        	}
        	{
        		OwnerIDs			Variable
        		{	OwnerID			LLUUID			}
        	}
        }
        '''

    def sendParcelDisableObjects(self, ):
        """ send a ParcelDisableObjects packet """

        pass

        '''
        // Disable makes objects nonphysical and turns off their scripts.
        // ParcelDisableObjects
        // viewer -> sim
        // reliable
        {
        	ParcelDisableObjects Low 201 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
            {
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		TaskIDs			Variable
        		{	TaskID			LLUUID			}
        	}
        	{
        		OwnerIDs			Variable
        		{	OwnerID			LLUUID			}
        	}
        }
        '''

    def join_parcels(self, ):
        """ joins the specified parcels """

        pass

        '''
        // ParcelJoin - Take all parcels which are owned by agent and inside
        // rectangle, and make them 1 parcel if they all are leased.
        // viewer -> sim
        // reliable
        {
        	ParcelJoin Low 210 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	West		F32		}
        		{	South		F32		}
        		{	East		F32		}
        		{	North		F32		}
        	}
        }
        
        '''

    def sendParcelJoin(self, ):
        """ send a ParcelJoin packet """

        pass

        '''
        // ParcelJoin - Take all parcels which are owned by agent and inside
        // rectangle, and make them 1 parcel if they all are leased.
        // viewer -> sim
        // reliable
        {
        	ParcelJoin Low 210 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	West		F32		}
        		{	South		F32		}
        		{	East		F32		}
        		{	North		F32		}
        	}
        }
        '''

    def divide_parcel(self, ):
        """ divide the selection into a new parcel """

        pass

        '''
        // ParcelDivide
        // If the selection is a subsection of exactly one parcel,
        // chop out that section and make a new parcel of it.
        // viewer -> sim
        // reliable
        {
        	ParcelDivide Low 211 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	West		F32		}
        		{	South		F32		}
        		{	East		F32		}
        		{	North		F32		}
        	}
        }
        '''

    def sendParcelDivide(self, ):
        """ send a ParcelDivide packet """

        pass

        '''
        // ParcelDivide
        // If the selection is a subsection of exactly one parcel,
        // chop out that section and make a new parcel of it.
        // viewer -> sim
        // reliable
        {
        	ParcelDivide Low 211 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	West		F32		}
        		{	South		F32		}
        		{	East		F32		}
        		{	North		F32		}
        	}
        }
        '''

    def request_parcel_access_list(self, ):
        """ request an access list for the specified parcel """

        self.onParcelAccessListReply_received = self.packet_handler._register('ParcelAccessListReply')
        self.onParcelAccessListReply_received.subscribe(self.onParcelAccessListReply)

        pass

        '''
        // ParcelAccessListRequest
        {
        	ParcelAccessListRequest Low 215 NotTrusted Zerocoded
        	{
        		AgentData		Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data	Single
        		{	SequenceID		S32		}
        		{	Flags			U32		}
        		{	LocalID			S32		}
        	}
        }
        '''

    def sendParcelAccessListRequest(self, ):
        """ send a ParcelAccessListRequest packet """

        pass

        '''
        // ParcelAccessListRequest
        {
        	ParcelAccessListRequest Low 215 NotTrusted Zerocoded
        	{
        		AgentData		Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data	Single
        		{	SequenceID		S32		}
        		{	Flags			U32		}
        		{	LocalID			S32		}
        	}
        }
        '''

    def onParcelAccessListReply(self, packet):
        """ parse and handle a ParcelAccessListReply packet """

        self.onParcelAccessListReply_received.unsubscribe(self.onParcelAccessListReply)

        pass

        '''
        // sim -> viewer
        // ParcelAccessListReply
        {
        	ParcelAccessListReply Low 216 Trusted Zerocoded
        	{
        		Data	Single
        		{	AgentID			LLUUID	}
        		{	SequenceID		S32		}
        		{	Flags			U32		}
        		{	LocalID			S32		}
        	}
        	{
        		List	Variable
        		{	ID			LLUUID		}
        		{	Time		S32			} // time_t
        		{	Flags		U32			}
        	}
        }
        '''

class Parcel(object):
    """ a representation of a parcel """

    def __init__(self, region, agent, settings = None):
        """ initialize the parcel manager """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        self.region = region
        self.agent = agent

        '''
        {
        	ParcelProperties High 23 Trusted Zerocoded
        	{
        		ParcelData			Single
        		{	RequestResult	S32				}
        		{	SequenceID		S32				}
        		{	SnapSelection	BOOL			}
        		{	SelfCount		S32				}
        		{	OtherCount		S32				}
        		{	PublicCount		S32				}
        		{	LocalID			S32				}
        		{	OwnerID			LLUUID			}
        		{	IsGroupOwned	BOOL			}
        		{	AuctionID		U32				}
        		{	ClaimDate		S32				}	// time_t
        		{	ClaimPrice		S32				}
        		{	RentPrice		S32				}
        		{	AABBMin			LLVector3		}
        		{	AABBMax			LLVector3		}
        		{	Bitmap			Variable	2	}	// packed bit-field
        		{	Area			S32				}
        		{	Status			U8	}  // owned vs. pending
        		{	SimWideMaxPrims		S32			}
        		{	SimWideTotalPrims	S32			}
        		{	MaxPrims		S32				}
        		{	TotalPrims		S32				}
        		{	OwnerPrims		S32				}
        		{	GroupPrims		S32				}
        		{	OtherPrims		S32				}
        		{	SelectedPrims	S32				}
        		{	ParcelPrimBonus	F32				}

        		{	OtherCleanTime	S32				}

        		{	ParcelFlags		U32				}
        		{	SalePrice		S32				}
        		{	Name			Variable	1	}	// string
        		{	Desc			Variable	1	}	// string
        		{	MusicURL		Variable	1	}	// string
        		{	MediaURL		Variable	1	}	// string
        		{	MediaID			LLUUID			}
        		{	MediaAutoScale	U8				}
        		{	GroupID			LLUUID			}
        		{	PassPrice		S32				}
        		{	PassHours		F32				}
        		{	Category		U8				}
        		{	AuthBuyerID		LLUUID			}
        		{	SnapshotID		LLUUID			}
        		{	UserLocation	LLVector3		}
        		{	UserLookAt		LLVector3		}
        		{	LandingType		U8				}
        		{	RegionPushOverride	BOOL		}
        		{	RegionDenyAnonymous	BOOL		}
        		{	RegionDenyIdentified	BOOL		}
        		{	RegionDenyTransacted	BOOL		}
        	}
        	{
        		AgeVerificationBlock Single
        		{   RegionDenyAgeUnverified BOOL    }
        	}
        }
        '''

    def return_objects(self, ):
        """ return the specified objects for this parcel """

        pass

        '''
        // ParcelReturnObjects
        // viewer -> sim
        // reliable
        {
        	ParcelReturnObjects Low 199 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		TaskIDs			Variable
        		{	TaskID			LLUUID			}
        	}
        	{
        		OwnerIDs			Variable
        		{	OwnerID			LLUUID			}
        	}
        }
        '''

    def set_other_clean_time(self, ):
        """ sends a SetOtherCleanTime packet for this parcel """

        pass

        '''
        // ParcelSetOtherCleanTime
        // viewer -> sim
        // reliable
        {
        	ParcelSetOtherCleanTime Low 200 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	OtherCleanTime	S32				}
        	}
        }
        '''

    def disable_objects(self, ):
        """ set objects nonphysical and disable scripts for this parcel """

        pass

        '''
        // Disable makes objects nonphysical and turns off their scripts.
        // ParcelDisableObjects
        // viewer -> sim
        // reliable
        {
        	ParcelDisableObjects Low 201 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		TaskIDs			Variable
        		{	TaskID			LLUUID			}
        	}
        	{
        		OwnerIDs			Variable
        		{	OwnerID			LLUUID			}
        	}
        }
        '''

    def select_objects(self, ):
        """ selects the specified objects for this parcel """

        pass

        '''
        // ParcelSelectObjects
        // viewer -> sim
        // reliable
        {
        	ParcelSelectObjects Low 202 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		ReturnIDs			Variable
        		{	ReturnID		LLUUID	}
        	}
        }
        '''

    def deed_to_group(self, ):
        """ deed this parcel to a group """

        pass

        '''
        // ParcelDeedToGroup - deed a patch of land to a group
        // viewer -> sim
        // reliable
        {
        	ParcelDeedToGroup Low 207 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data				Single
        		{	GroupID			LLUUID	}
        		{	LocalID			S32		}	// parcel id
        	}
        }
        '''

    def reclaim(self, ):
        """ reclaim this parcel"""

        pass

        '''
        // reserved for when island owners force re-claim parcel
        {
        	ParcelReclaim Low 208 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data				Single
        		{	LocalID			S32		}	// parcel id
        	}
        }
        '''

    def claim(self, ):
        """ change the owner of a parcel """

        pass

        '''
        // ParcelClaim - change the owner of a patch of land
        // viewer -> sim
        // reliable
        {
        	ParcelClaim Low 209 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data				Single
        		{	GroupID			LLUUID	}
        		{	IsGroupOwned	BOOL 	}
        		{	Final			BOOL	} // true if buyer is in tier
        	}
        	{
        		ParcelData			Variable
        		{	West			F32		}
        		{	South			F32		}
        		{	East			F32		}
        		{	North			F32		}
        	}
        }
        '''

    def release(self, ):
        """ release this parcel to the public """

        pass

        '''
        // ParcelRelease
        // Release a parcel to public
        // viewer -> sim
        // reliable
        {
        	ParcelRelease Low 212 NotTrusted Unencoded
        	{
        		AgentData		Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data			Single
        		{	LocalID			S32		}	// parcel ID
        	}
        }
        '''

    def buy(self, ):
        """ buy this parcel """

        pass

        '''
        // ParcelBuy - change the owner of a patch of land.
        // viewer -> sim
        // reliable
        {
        	ParcelBuy Low 213 NotTrusted Zerocoded
        	{
        		AgentData		Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data			Single
        		{	GroupID			LLUUID	}
        		{	IsGroupOwned	BOOL 	}
        		{	RemoveContribution BOOL	}
        		{	LocalID			S32		}
        		{	Final			BOOL	} // true if buyer is in tier
        	}
        	{
        		ParcelData		Single
        		{	Price			S32		}
        		{	Area			S32		}
        	}
        }
        '''

    def godforce_owner(self, ):
        """ god force own this parcel """

        pass

        '''
        // ParcelGodForceOwner Unencoded
        {
        	ParcelGodForceOwner	Low	214 NotTrusted Zerocoded
        	{
        		AgentData		Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data			Single
        		{	OwnerID			LLUUID	}
        		{	LocalID			S32		}	// parcel ID
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
