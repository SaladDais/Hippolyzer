# std lib
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

# ZCA
from zope.interface import implements
import grokcore.component as grok

# pyogp
from interfaces import IRegion
from pyogp.lib.base.interfaces import ISeedCapability
from pyogp.lib.base.caps import Capability
import exc

logger = getLogger('pyogp.lib.base.regiondomain')
log = logger.log

class Region(object):
    """models a region endpoint"""
    
    implements(IRegion)
    
    def __init__(self, uri):
        """initialize the region with the region uri"""
        
        self.uri = uri
        self.seed_cap_url = ''
        self.seed_cap = None
        self.details = {}
        
        log(DEBUG, 'initializing region domain: %s' %self)

    def set_seed_cap_url(self, url):
    
        self.seed_cap_url = url
        self.seed_cap = RegionSeedCapability('seed_cap', self.seed_cap_url)
        
        log(DEBUG, 'setting region domain seed cap: %s' % (self.seed_cap_url))

class RegionSeedCapability(Capability):
    """a seed capability which is able to retrieve other capabilities"""
    
    implements(ISeedCapability)
        
    def get(self, names=[]):
        """if this is a seed cap we can retrieve other caps here"""
        
        log(INFO, 'requesting from the region domain the following caps: %s' % (names))
        
        payload = names
        parsed_result = self.POST(payload)  #['caps']
        log(INFO, 'reques for caps returned: %s' % (names))
        
        caps = {}
        for name in names:
            # TODO: some caps might be seed caps, how do we know? 
            caps[name]=Capability(name, parsed_result[name])
            #log(INFO, 'got cap: %s' % (name))
            
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
        self.last_id = -1
        
        # let's retrieve the cap we need
        self.seed_cap = self.context.seed_cap # ISeedCapability
        
        log(DEBUG, 'intitializing region domain event queue via the seed cap: %s' % (self.seed_cap))
        
        self.cap = self.seed_cap.get(['EventQueueGet'])['EventQueueGet']
        
        if self.cap == {}:
            raise exc.RegionCapNotAvailable('EventQueueGet')
        else:
            log(DEBUG, 'region event queue cap is: %s' % (self.cap.public_url))

        
    def __call__(self, data = {}):
        """initiate the event queue get request"""
        
        if self.last_id != -1:
            data = {'ack':self.last_id, 'done':False}
            
        result = self.cap.POST(data)
        
        self.last_id = result['id']
        
        log(DEBUG, 'region event queue cap called, returned id: %s' % (self.last_id))
        
        return result
