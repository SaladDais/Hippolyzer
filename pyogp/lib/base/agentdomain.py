from agent import Agent
from interfaces import ISerialization
from caps import SeedCapability

import urllib2

from zope.interface import implements
import grokcore.component as grok

from indra.base import llsd

from interfaces import IPlaceAvatar, IAgentDomain
from network import IRESTClient, HTTPError
from zope.component import queryUtility, adapts, getUtility

from agent import Agent
from avatar import Avatar
from caps import SeedCapability

class AgentDomain(object):
    """an agent domain endpoint"""
    
    implements(IAgentDomain)
    
    def __init__(self,uri):
        """initialize the agent domain endpoint"""
        self.uri = uri
        
    def login(self, credentials):
        """login to the agent domain and return an agent object"""
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
	    print "error", error.code, error.msg
	    print error.fp.read()
	    raise
    
	seed_cap_url_data = response.body
	seed_cap_url = llsd.parse(seed_cap_url_data)['agent_seed_capability']
	self.seed_cap = SeedCapability('seed_cap', seed_cap_url)
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
        self.place_avatar_cap = self.seed_cap.get(['place_avatar'])['place_avatar']
    
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

        
    def __call__(self, data = {}):
        """initiate the event queue get request"""
        result = self.cap.POST(data)
        return result
        
    
    
