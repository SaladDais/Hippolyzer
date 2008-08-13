from zope.interface import implements
import grokcore.component as grok

from interfaces import IRegion

class Region(object):
    """models a region endpoint"""
    
    implements(IRegion)
    
    def __init__(self, uri):
        """initialize the region with the region uri"""
        self.uri = uri
        self.seed_cap = None
        self.details = {}
    
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
