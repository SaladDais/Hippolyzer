from zope.interface import implements
import grokcore.component as grok

from interfaces import IRegion
from pyogp.lib.base.interfaces import ISeedCapability
from pyogp.lib.base.caps import Capability

class Region(object):
    """models a region endpoint"""
    
    implements(IRegion)
    
    def __init__(self, uri):
        """initialize the region with the region uri"""
        self.uri = uri
        self.seed_cap_url = ''
        self.seed_cap = None
        self.details = {}

    def set_seed_cap_url(self, url):
        self.seed_cap_url = url
        self.seed_cap = RegionSeedCapability('seed_cap', self.seed_cap_url)

class RegionSeedCapability(Capability):
    """a seed capability which is able to retrieve other capabilities"""
    
    implements(ISeedCapability)
        
    def get(self, names=[]):
        """if this is a seed cap we can retrieve other caps here"""
        payload = names
        parsed_result = self.POST(payload)  #['caps']
        print parsed_result
        
        caps = {}
        for name in names:
            # TODO: some caps might be seed caps, how do we know? 
            caps[name]=Capability(name, parsed_result[name])
            
        return caps
             
        
    def __repr__(self):
        return "<RegionSeedCapability for %s>" %self.public_url
    
from interfaces import IEventQueueGet
class EventQueueGet(grok.Adapter):
    """an event queue get capability"""
    grok.implements(IEventQueueGet)
    grok.context(IRegion)
    
    def __init__(self, context):
        """initialize this adapter"""
        self.context = context 
        
        # let's retrieve the cap we need
        self.seed_cap = self.context.seed_cap # ISeedCapability
        print self.seed_cap
        self.cap = self.seed_cap.get(['EventQueueGet'])['EventQueueGet']

        
    def __call__(self, data = {}):
        """initiate the event queue get request"""
        result = self.cap.POST(data)
        return result
