
"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""

# std lib
import urllib2
from types import *
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import re
# related

# pyogp
from pyogp.lib.base.network.stdlib_client import StdLibClient, HTTPError
from pyogp.lib.base.exc import ResourceNotFound, ResourceError, DeserializerNotFound
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.utilities.helpers import LLSDDeserializer, ListLLSDSerializer, DictLLSDSerializer

# initialize logging
logger = getLogger('pyogp.lib.base.caps')
log = logger.log

class Capability(object):
    """ models a capability 
    A capability is a web resource which enables functionality for a client
    The seed capability is a special type, through which other capabilities 
    are procured

    A capability in pyogp provides a GET and a POST method

    Sample implementations: region.py
    Tests: tests/caps.txt, tests/test_caps.py

    """

    def __init__(self, name, public_url, restclient = None, settings = None):
        """ initialize the capability """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        if restclient == None: 
            self.restclient = StdLibClient() 
        else:
            self.restclient = restclient 

        self.name = name
        self.public_url = public_url
        #log(DEBUG, 'instantiated cap %s' %self)

    def GET(self,custom_headers={}):
        """call this capability, return the parsed result"""

        if self.settings.ENABLE_CAPS_LOGGING: log(DEBUG, '%s: GETing %s' %(self.name, self.public_url))

        try:
            response = self.restclient.GET(self.public_url)
        except HTTPError, e:
            if e.code==404:
                raise ResourceNotFound(self.public_url)
            else:
                raise ResourceError(self.public_url, e.code, e.msg, e.fp.read(), method="GET")

        # now deserialize the data again
        content_type_charset = response.headers['Content-Type']
        content_type = content_type_charset.split(";")[0] # remove the charset part

        # ToDo: write a generic serializer/deserializer
        if (content_type == 'application/llsd+xml'):
            deserializer = LLSDDeserializer()
        else:
            raise DeserializerNotFound(content_type)
	
        data = deserializer.deserialize(response.body)

        if self.settings.LOG_VERBOSE and self.settings.ENABLE_CAPS_LLSD_LOGGING: log(DEBUG, 'Received the following llsd from %s: %s' % (self.public_url, response.body.strip()))
        if self.settings.ENABLE_CAPS_LOGGING: log(DEBUG, 'Get of cap %s response is: %s' % (self.public_url, data))        

        return data

    def POST(self,payload,custom_headers={}):
        """call this capability, return the parsed result"""

        if self.settings.ENABLE_CAPS_LOGGING: log(DEBUG, 'Sending to cap %s the following payload: %s' %(self.public_url, payload))        

        # serialize the data
        if (type(payload) is ListType):
            serializer = ListLLSDSerializer(payload)
        elif (type(payload) is DictType):
            serializer = DictLLSDSerializer(payload)
        else:
            raise DeserializerNotFound(type(payload))

        content_type = serializer.content_type
        serialized_payload = serializer.serialize()

        if self.settings.LOG_VERBOSE and self.settings.ENABLE_CAPS_LLSD_LOGGING: log(DEBUG, 'Posting the following payload to %s: %s' % (self.public_url, serialized_payload))

        headers = {"Content-type" : content_type}
        headers.update(custom_headers)  # give the user the ability to add headers 

        try:
            response = self.restclient.POST(self.public_url, serialized_payload, headers=headers)
        except HTTPError, e:
            if e.code==404:
                raise ResourceNotFound(self.public_url)
            else:
                raise ResourceError(self.public_url, e.code, e.msg, e.fp.read(), method="POST")

        return self._response_handler(response)
        
    def POST_FILE(self, file_name, custom_headers={}):
        """ Opens file at file_name and posts contents to this cap. """
        headers = {"Content-type" : "application/octet-stream"}
        fd = open(file_name)
        payload = fd.read()
        fd.close
        
        try:
            response = self.restclient.POST(self.public_url,
                                            payload, headers=headers)
        except HTTPError, e:
            if e.code==404:
                raise ResourceNotFound(self.public_url)
            else:
                raise ResourceError(self.public_url, e.code, e.msg,
                                    e.fp.read(), method="POST")

        return self._response_handler(response)
        
    def _response_handler(self, response):
        # now deserialize the data again, we ask for a utility with the content type
        # as the name
        content_type_charset = response.headers['Content-Type']
        content_type = content_type_charset.split(";")[0] # remove the charset part

        pattern = re.compile('<\?xml\sversion="1.0"\s\?><llsd>.*?</llsd>')
        # ToDo: write a generic serializer/deserializer
        if (content_type == 'application/llsd+xml') or \
               (content_type == 'application/xml') or \
               (content_type == 'text/html' and \
                pattern.match(response.body) != None):
            deserializer = LLSDDeserializer()
        else:
            print response
            raise DeserializerNotFound(content_type)
	
        data = deserializer.deserialize(response.body)

        if self.settings.ENABLE_CAPS_LLSD_LOGGING: log(DEBUG, 'Received the following llsd from %s: %s' % (self.public_url, response.body.strip()))
        if self.settings.ENABLE_CAPS_LOGGING: log(DEBUG, 'Post to cap %s response is: %s' % (self.public_url, data))        

        return data


    def __repr__(self):
        return "<Capability '%s' for %s>" %(self.name, self.public_url)

class SeedCapability(Capability):
    """ a seed capability which is able to retrieve other capabilities """

    def get(self, names=[]):
        """ if this is a seed cap we can retrieve other caps here

        Note: changing post key from 'caps' to 'capabilities' for OGP spec updates in Draft 3
        see http://wiki.secondlife.com/wiki/OGP_Base_Draft_3#Seed_Capability_.28Resource_Class.29
        """

        payload = {'capabilities':names} 
        parsed_result = self.POST(payload)['capabilities']

        caps = {}
        for name in names:
            # TODO: some caps might be seed caps, how do we know? 
            caps[name]=Capability(name, parsed_result[name], self.restclient)

        return caps

    def __repr__(self):
        return "<SeedCapability for %s>" %self.public_url



