"""
@file regiondomain.py
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
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import re
from urllib import quote
from urlparse import urlparse, urljoin

# ZCA
from zope.interface import implements
from zope.component import getUtility, queryUtility
import grokcore.component as grok

# pyogp
from interfaces import IRegion
from pyogp.lib.base.interfaces import ISeedCapability, ISerialization, IDeserialization
from pyogp.lib.base.caps import Capability
from network import IRESTClient, HTTPError
import exc

logger = getLogger('pyogp.lib.base.regiondomain')
log = logger.log

class Region(object):
    """models a region endpoint"""
    
    implements(IRegion)
    
    def __init__(self, uri):
        """initialize the region with the region uri"""
        
        self.uri = self.parse_region_uri(uri)
        self.seed_cap_url = ''
        self.seed_cap = None
        self.details = {}
        
        log(DEBUG, 'initializing region domain: %s' %self)

    def set_seed_cap_url(self, url):
    
        self.seed_cap_url = url
        self.seed_cap = RegionSeedCapability('seed_cap', self.seed_cap_url)
        
        log(DEBUG, 'setting region domain seed cap: %s' % (self.seed_cap_url))
    
    def parse_region_uri(self, uri):     
        """ parse a region uri and returns one formatted appropriately
        
        Note: new region name requirements when posting region_uri moving from Draft 2 to Draft 3
        see http://wiki.secondlife.com/wiki/Open_Grid_Public_Beta/Changes_20080923
        
        """
        
        # test if it is a lindenlab.com domain name
        if (re.search('lindenlab', urlparse(uri)[1])):
            region_uri = uri + '/public_seed'
        else:
            # this is a crappy test to see if it's already been urlencoded, it only checkes for spaces
            if re.search('%20', urlparse(uri)[2]):
                region_uri = uri
            else:
                region_uri = urljoin(uri, quote(urlparse(uri)[2]))
        
        return region_uri

    def get_region_public_seed(self,custom_headers={'Accept' : 'application/llsd+xml'}):
        """call this capability, return the parsed result"""
        
        log(DEBUG, 'Getting region public_seed %s' %(self.uri))

        try:
            restclient = getUtility(IRESTClient)
            response = restclient.GET(self.uri, custom_headers)
        except HTTPError, e:
            if e.code==404:
                raise exc.ResourceNotFound(self.uri)
            else:
                raise exc.ResourceError(self.uri, e.code, e.msg, e.fp.read(), method="GET")
  
        # now deserialize the data again, we ask for a utility with the content type
        # as the name
        content_type_charset = response.headers['Content-Type']
        content_type = content_type_charset.split(";")[0] # remove the charset part
        
        deserializer = queryUtility(IDeserialization,name=content_type)
        
        if deserializer is None:
            raise exc.DeserializerNotFound(content_type)

        data = deserializer.deserialize_string(response.body)
        log(DEBUG, 'Get of cap %s response is: %s' % (self.uri, data))        
        
        return data


class RegionSeedCapability(Capability):
    """a seed capability which is able to retrieve other capabilities"""
    
    implements(ISeedCapability)
        
    def get(self, names=[]):
        """if this is a seed cap we can retrieve other caps here"""
        
        log(INFO, 'requesting from the region domain the following caps: %s' % (names))
        
        payload = names
        parsed_result = self.POST(payload)  #['caps']
        log(INFO, 'request for caps returned: %s' % (names))
        
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
