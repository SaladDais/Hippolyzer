# std lib
import urllib2
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

from agent import Agent
from interfaces import ISerialization
from caps import SeedCapability

# ZCA
from zope.component import queryUtility, adapts, getUtility
from zope.interface import implements
import grokcore.component as grok

# related
from indra.base import llsd

# pyogp
from interfaces import IPlaceAvatar, IAgentDomain
from network import IRESTClient, HTTPError
from agent import Agent
from avatar import Avatar
from caps import SeedCapability
import exc

logger = getLogger('pyogp.lib.base.agentdomain')
log = logger.log

class AgentDomain(object):
    """an agent domain endpoint"""
    
    implements(IAgentDomain)
    
    def __init__(self,uri):
        """initialize the agent domain endpoint"""
        self.uri = uri
        log(DEBUG, 'initializing agent domain: %s' %self)
        
    def login(self, credentials):
        """login to the agent domain and return an agent object"""
        
        log(INFO, 'logging in to %s as %s %s' % (self.uri, credentials.firstname, credentials.lastname))
        
        serializer = ISerialization(credentials) # convert to string via adapter
        payload = serializer.serialize()
        content_type = serializer.content_type
        headers = {'Content-Type': content_type}
        
        # now create the request. We assume for now that self.uri is the login uri
        # TODO: make this pluggable so we can use other transports like eventlet in the future
        # TODO: add logging and error handling
        restclient = getUtility(IRESTClient)

        try:
            response = restclient.POST(self.uri, payload, headers=headers)
        except HTTPError, error:
            if e.code==404:
                raise exc.ResourceNotFound(self.uri)
            else:
                raise exc.ResourceError(self.uri, error.code, error.msg, error.fp.read(), method="POST")
   
        seed_cap_url_data = response.body
        seed_cap_url = llsd.parse(seed_cap_url_data)['agent_seed_capability']
        self.seed_cap = SeedCapability('seed_cap', seed_cap_url)
	
        if self.seed_cap is None:
            raise exc.UserNotAuthorized(self.credentials)
        else:
            log(INFO, 'logged in to %s' % (self.uri))
	
        return Agent(self)
        
        
class PlaceAvatar(grok.Adapter):
    """handles placing an avatar for an agent object"""
    grok.implements(IPlaceAvatar)
    grok.context(IAgentDomain)
    
    def __init__(self, context):
        """initialize this adapter"""
        self.context = context 
        
        # let's retrieve the cap we need
        self.seed_cap = self.context.seed_cap # ISeedCapability
        self.place_avatar_cap = self.seed_cap.get(['rez_avatar/place'])['rez_avatar/place']
        
        log(DEBUG, 'initializing rez_avatar/place: %s' % (self.place_avatar_cap))
        
    def __call__(self, region, position=[117,73,21]):
        """initiate the placing process"""
        
        region_uri = region.uri
        payload = {'region_url' : region_uri, 'position':position} 
        result = self.place_avatar_cap.POST(payload)
        
        avatar = Avatar(region)
        #extract some data out of the results and put into region
        seed_cap_url = result['seed_capability']
        region.set_seed_cap_url(seed_cap_url)
        #region.seed_cap = SeedCapability('seed_cap', seed_cap_url)
        
        if seed_cap_url is None:
            raise exc.UserRezFailed(region)
        else:
            log(INFO, 'Region_uri %s returned a seed_cap of %s' % (region_uri, seed_cap_url))
        
        #AND THE REST
        region.details = result
        return avatar
    
from interfaces import IEventQueueGet
class EventQueueGet(grok.Adapter):
    """an event queue get capability"""
    grok.implements(IEventQueueGet)
    grok.context(IAgentDomain)
    
    def __init__(self, context):
        """initialize this adapter"""
        self.context = context 
        
        # let's retrieve the cap we need
        self.seed_cap = self.context.seed_cap # ISeedCapability
        self.cap = self.seed_cap.get(['event_queue'])['event_queue']
        
        log(DEBUG, 'initializing event_queue for agent domain: %s' % (self.cap.public_url))

        
    def __call__(self, data = {}):
        """initiate the event queue get request"""
        result = self.cap.POST(data)
        return result
        
    
    
