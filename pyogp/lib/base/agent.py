from zope.interface import implements
from zope.component import adapts

from interfaces import IAgent, IPlaceAvatarAdapter

class Agent(object):
    """an OGP agent"""
    
    implements(IAgent)
    
    def __init__(self, agentdomain):
        """initialize this agent"""
        self.agentdomain = agentdomain
        


class PlaceAvatarAdapter(object):
    """handles placing an avatar for an agent object"""
    implements(IPlaceAvatarAdapter)
    adapts(IAgent)
    
    def __init__(self, agent):
        """initialize this adapter"""
        self.agent = agent 
        
        # let's retrieve the cap we need
        self.seed_cap = self.agent.agentdomain.seed_cap # ISeedCapability
        self.place_avatar_cap = self.seed_cap.get(['place_avatar'])['place_avatar']
    
    def __call__(self, region):
        """initiate the placing process"""
        region_uri = region.uri
        payload = {'region_url' : region_uri } 
        result = self.place_avatar_cap(payload)

        return result

# now we register this adapter so it can be used later:
from zope.component import provideAdapter

# register adapters for the HTML node
provideAdapter(PlaceAvatarAdapter)

        
        
    