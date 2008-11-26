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

# related
from indra.base import llsd

# pyogp
from network.stdlib_client import StdLibClient, HTTPError
from caps import SeedCapability
import exc

# initialize logging
logger = getLogger('pyogp.lib.base.agentdomain')
log = logger.log

class AgentDomain(object):
    """an agent domain endpoint"""
    
    def __init__(self, uri, restclient = None):
        """ initialize the agent domain endpoint """

        if restclient == None: 
            self.restclient = StdLibClient() 
        else:
            self.restclient = restclient 

        self.login_uri = uri
        self.credentials = None
        self.connectedStatus = False
        self.seed_cap = None
        log(DEBUG, 'initializing agent domain: %s' %self)
        
    def login(self, credentials):
        """ login to the agent domain """
        
        response = self.post_to_loginuri(credentials)
        
        self.eval_login_response(response)   
        
    def post_to_loginuri(self, credentials):
        """ post to login_uri and return response """
        
        self.credentials = credentials
        log(INFO, 'Logging in to %s as %s %s' % (self.login_uri, self.credentials.firstname, self.credentials.lastname))
        
        payload = credentials.serialize()
        content_type = credentials.content_type
        headers = {'Content-Type': content_type}
        
        # now create the request. We assume for now that self.uri is the login uri
        # TODO: make this pluggable so we can use other transports like eventlet in the future
        # TODO: add logging and error handling

        try:
            response = self.restclient.POST(self.login_uri, payload, headers=headers)
        except HTTPError, error:
            if error.code==404:
                raise exc.ResourceNotFound(self.login_uri)
            else:
                raise exc.ResourceError(self.login_uri, error.code, error.msg, error.fp.read(), method="POST")
        
        return response

    def eval_login_response(self, response):
        """ parse the login uri response """
    
        seed_cap_url_data = self.parse_login_response(response)
        try:
            seed_cap_url = seed_cap_url_data['agent_seed_capability']
            self.seed_cap = SeedCapability('seed_cap', seed_cap_url, self.restclient)
            self.connectedStatus = True
            log(INFO, 'logged in to %s' % (self.login_uri))
        except KeyError:
            raise exc.UserNotAuthorized(self.credentials)
        
    def parse_login_response(self, response):   
        """ parse the login uri response and returns deserialized data """
       
        data = llsd.parse(response.body)
        
        log(DEBUG, 'deserialized login response body = %s' % (data))
            
        return data
                
    def place_avatar(self, region_uri, position=[117,73,21]):
        """ handles the rez_avatar/place cap on the agent domain, populates some initial region attributes """

        place_avatar_cap = self.seed_cap.get(['rez_avatar/place'])['rez_avatar/place']

        payload = {'public_region_seed_capability' : region_uri, 'position':position} 
        result = place_avatar_cap.POST(payload)

        if result['region_seed_capability'] is None:
            raise exc.UserRezFailed(region)
        else:
            log(INFO, 'Region_uri %s returned a seed_cap of %s' % (region_uri, result['region_seed_capability']))

        log(DEBUG, 'Full rez_avatar/place response is: %s' % (result))
        
        return result

class EventQueue(AgentDomain):
    """ an event queue get capability 

    this is a temporary solution. ideally we'd have a generic event queue object
    that would be integrated into the ad and region separately
    """

    def __init__(self, context):
        """initialize this adapter"""
        self.context = context 
        
        # let's retrieve the cap we need
        self.seed_cap = self.context.seed_cap
        self.cap = self.seed_cap.get(['event_queue'])['event_queue']
        
        log(DEBUG, 'initializing event_queue for agent domain: %s' % (self.cap.public_url))

        
    def __call__(self, data = {}):
        """initiate the event queue get request"""
        result = self.cap.POST(data)
        return result
        
    
    
