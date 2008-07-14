from zope.interface import implements

import urllib2
from indra.base import llsd

from interfaces import ICapability, ISeedCapability

class Capability(object):
    """models a capability"""
    
    implements(ICapability)
    
    def __init__(self, name, private_url):
        """initialize the capability"""
        
        self.name = name
        self.private_url = private_url
        
    def __call__(self,payload,custom_headers={}):
        """call this capability, return the parsed result"""
        
        headers = {"Content-type" : "application/llsd+xml"}
        headers.update(custom_headers)
        llsd_payload = llsd.format_xml(payload)
        
        # TODO: better errorhandling with own exceptions
        try:
            request = urllib2.Request(self.private_url, llsd_payload, headers)
            result = urllib2.urlopen(request).read()
        except urllib2.HTTPError, e:
            print "** failure while calling cap:",
            print e.read()
            raise
        return llsd.parse(result)
        
    def __repr__(self):
        return "<Capability for %s>" %self.private_url
        
class SeedCapability(Capability):
    """a seed capability which is able to retrieve other capabilities"""
    
    implements(ISeedCapability)
        
    def get(self, names=[]):
        """if this is a seed cap we can retrieve other caps here"""
        payload = {'caps':names} 
        parsed_result = self(payload)['caps']
        
        caps = {}
        for name in names:
            # TODO: some caps might be seed caps, how do we know? 
            caps[name]=Capability(name, parsed_result[name])
            
        return caps
             
        
    def __repr__(self):
        return "<SeedCapability for %s>" %self.private_url

        
        
        
