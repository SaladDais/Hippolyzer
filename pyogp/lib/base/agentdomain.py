from agent import Agent
from interfaces import ISerialization
from caps import SeedCapability
import urllib2
from indra.base import llsd


# URL Opener for the agent domain login
# 
class RedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_302(self, req, fp, code, msg, headers):
        #ignore the redirect, grabbing the seed cap url from the headers
        # TODO: add logging and error handling
        return headers['location']


# post to auth.cgi, ignoring the built in redirect
AgentDomainLoginOpener = urllib2.build_opener(RedirectHandler())


class AgentDomain(object):
    """an agent domain endpoint"""
    
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
        # 
        request = urllib2.Request(self.uri,payload,headers)        
        res = AgentDomainLoginOpener.open(request)        
        if type(res)!=type(""):            
            seed_cap_url_data = res.read() # it might be an addinfourl object
            seed_cap_url = llsd.parse(seed_cap_url_data)['agent_seed_capability']
        else:
            # this only happens in the Linden Lab Agent Domain with their redirect
            seed_cap_url = res        
        self.seed_cap = SeedCapability('seed_cap', seed_cap_url)
        return Agent(self)
        
        
