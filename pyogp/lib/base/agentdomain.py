from agent import Agent
from interfaces import ISerialization
from caps import SeedCapability

USE_REDIRECT=True

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


# URL Opener for the agent domain login
#

if USE_REDIRECT: 
    # REMOVE THIS WHEN THE REDIRECT IS NOT NEEDED ANYMORE FOR LINDEN LAB!
    class RedirectHandler(urllib2.HTTPRedirectHandler):

        def http_error_302(self, req, fp, code, msg, headers):
            #ignore the redirect, grabbing the seed cap url from the headers
            # TODO: add logging and error handling
            return headers['location']


    # post to auth.cgi, ignoring the built in redirect
    AgentDomainLoginOpener = urllib2.build_opener(RedirectHandler())


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
        if USE_REDIRECT:
            request = urllib2.Request(self.uri,payload,headers)        
            try:
                res = AgentDomainLoginOpener.open(request)        
            except urllib2.HTTPError,e:
                print e.read()
                raise
            if type(res)!=type(""):            
                seed_cap_url_data = res.read() # it might be an addinfourl object
                seed_cap_url = llsd.parse(seed_cap_url_data)['agent_seed_capability']
            else:
                # this only happens in the Linden Lab Agent Domain with their redirect
                seed_cap_url = res        
        else:
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
    
    def __call__(self, region):
        """initiate the placing process"""
        region_uri = region.uri
        payload = {'region_url' : region_uri } 
        result = self.place_avatar_cap.POST(payload)
        
        region.details = result
        avatar = Avatar(region)

        return avatar
