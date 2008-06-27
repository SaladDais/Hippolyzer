from agent import Agent
from interfaces import ICredentialSerializer
from caps import SeedCapability
import urllib2


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
        serializer = ICredentialSerializer(credentials) # convert to string via adapter
        payload = serializer.serialize()
        headers = serializer.headers
        print payload, headers
        
        # now create the request. We assume for now that self.uri is the login uri
        # TODO: make this pluggable so we can use other transports like eventlet in the future
        # TODO: add logging and error handling
        request = urllib2.Request(self.uri,payload,headers)
        seed_cap_url = AgentDomainLoginOpener.open(request)
        self.seed_cap = SeedCapability('seed_cap', seed_cap_url)
        return Agent(self)
        
        
