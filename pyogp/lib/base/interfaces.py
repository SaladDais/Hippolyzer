from zope.interface import Interface, Attribute

class ICredential(Interface):
    """base interface for credentials"""
    
class IPlainPasswordCredential(ICredential):
    """a plain password credential"""
    
    firstname = Attribute("""first name of avatar""")
    lastname = Attribute("""last name of avatar""")
    password = Attribute("""plain password""")
    
class ICredentialSerializer(Interface):
    """converts a credential to a serialized format for sending it over the network"""
    
    def serialize():
        """return a serialized string"""
        
    def headers():
        """return headers eventually needed for sending it out"""


class IAgent(Interface):
    """models an agent"""
    
    agentdomain = Attribute("""the agent domain endpoint""")
    
        
class IRegion(Interface):
    """a region endpoint"""
    
    def place_avatar(agent):
        """place an avatar on this region, returns IAvatar"""
        
class IAvatar(Interface):
    """an OGP avatar (region representation of an agent)"""
    
    def establish_presence():
        """for now it will do a loop to establish a presence on a region"""
        
class IPlaceAvatarAdapter(Interface):
    """adapts an agents to a method which can place an avatar on a region"""
    
    def __call__(region):
        """takes a region objects and tries to place the agent there as an avatar
        
        return an IAvatar"""
        
class ICapability(Interface):
    """a capability"""
    
    name = Attribute('''name of the capability''')
    private_url = Attribute('''private url of this capability''')
    
    def __call__(payload):
        """call this capability
        
        payload  -- the payload as python dictionary
        returns a python dictionary with the results
        
        """
    
class ISeedCapability(ICapability):
    """a seed capability which is able to retrieve further capabilities"""
    
    def get(names=[]):
        """retrieve the given set of named capabilities
        
        returns a dict of ICapabilty objects keyed by their name"""