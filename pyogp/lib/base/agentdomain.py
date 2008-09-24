"""
@file agentdomain.py
@date 2008-09-16
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

# std lib
import urllib2
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

# ZCA
from zope.component import queryUtility, adapts, getUtility
from zope.interface import implements
import grokcore.component as grok

# related
from indra.base import llsd

# pyogp
from interfaces import IPlaceAvatar, IAgentDomain, ISerialization
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
        self.credentials = None
        self.loginStatus = False
        log(DEBUG, 'initializing agent domain: %s' %self)
        
    def login(self, credentials):
        """login to the agent domain and return an agent object"""
        
        response = self.post_to_loginuri(credentials)
        
        self.eval_login_response(response)   
	
        return Agent(self)
        
    def post_to_loginuri(self, credentials):
        """post to login_uri and return response"""
        
        self.credentials = credentials
        log(INFO, 'logging in to %s as %s %s' % (self.uri, self.credentials.firstname, self.credentials.lastname))
        
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
            if error.code==404:
                raise exc.ResourceNotFound(self.uri)
            else:
                raise exc.ResourceError(self.uri, error.code, error.msg, error.fp.read(), method="POST")
        
        return response

    def eval_login_response(self, response):
        """ parse the login uri response and return an agent object """
    
        seed_cap_url_data = self.parse_login_response(response)
        try:
            seed_cap_url = seed_cap_url_data['agent_seed_capability']
            self.seed_cap = SeedCapability('seed_cap', seed_cap_url)
            self.loginStatus = True
            log(INFO, 'logged in to %s' % (self.uri))
        except KeyError:
            raise exc.UserNotAuthorized(self.credentials)
	
        return Agent(self)
        
    def parse_login_response(self, response):   
        """ parse the login uri response and returns deserialized data """
       
        data = llsd.parse(response.body)
        
        log(DEBUG, 'deserialized login response body = %s' % (data))
        try:
            seed_cap_url = data['agent_seed_capability']
            self.seed_cap = SeedCapability('seed_cap', seed_cap_url)
            self.loginStatus = True
            log(INFO, 'logged in to %s' % (self.uri))
        except KeyError:
            pass
            
        return data
                
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
        
        ''' 
        Note: Changed 'seed_capability' to 'region_seed_capability' per changes moving from Draft 2 to Draft 3 of the OGP spec.
        see http://wiki.secondlife.com/wiki/OGP_Teleport_Draft_3#POST_Interface
        '''
        
        seed_cap_url = result['region_seed_capability']
        region.set_seed_cap_url(seed_cap_url)
        #region.seed_cap = SeedCapability('seed_cap', seed_cap_url)
        
        if seed_cap_url is None:
            raise exc.UserRezFailed(region)
        else:
            log(INFO, 'Region_uri %s returned a seed_cap of %s' % (region_uri, seed_cap_url))
        
        #AND THE REST
        region.details = result
        
        log(DEBUG, 'Full rez_avatar/place response is: %s' % (result))
        
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
        
    
    
