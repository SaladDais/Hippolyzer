"""
@file caps.py
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
from zope.interface import implements
from zope.component import queryUtility, adapts, getUtility
import grokcore.component as grok

# related
from indra.base import llsd

# pyogp
from interfaces import ICapability, ISeedCapability
from interfaces import ISerialization, IDeserialization
from network import IRESTClient, HTTPError
import exc

logger = getLogger('pyogp.lib.base.caps')
log = logger.log

class Capability(object):
    """models a capability"""
    
    implements(ICapability)
    
    def __init__(self, name, public_url):
        """initialize the capability"""
        
        self.name = name
        self.public_url = public_url
        log(INFO, 'instantiated cap %s' %self)
        
    def GET(self,custom_headers={}):
        """call this capability, return the parsed result"""
        
        log(DEBUG, '%s: GETing %s' %(self.name, self.public_url))

        try:
            restclient = getUtility(IRESTClient)
            response = restclient.GET(self.public_url)
        except HTTPError, e:
            if e.code==404:
                raise exc.ResourceNotFound(self.public_url)
            else:
                raise exc.ResourceError(self.public_url, e.code, e.msg, e.fp.read(), method="GET")
  
        # now deserialize the data again, we ask for a utility with the content type
        # as the name
        content_type_charset = response.headers['Content-Type']
        content_type = content_type_charset.split(";")[0] # remove the charset part
        
        deserializer = queryUtility(IDeserialization,name=content_type)
        
        if deserializer is None:
            raise exc.DeserializerNotFound(content_type)

        data = deserializer.deserialize_string(response.body)
        log(DEBUG, 'Get of cap %s response is: %s' % (self.public_url, data))        
        
        return data


    def POST(self,payload,custom_headers={}):
        """call this capability, return the parsed result"""
        
        log(DEBUG, 'Sending to cap %s the following payload: %s' %(self.public_url, payload))        
        
        # serialize the data
        serializer = ISerialization(payload)
        content_type = serializer.content_type
        serialized_payload = serializer.serialize()
        
        headers = {"Content-type" : content_type}
        headers.update(custom_headers)  # give the user the ability to add headers 

        try:
            restclient = getUtility(IRESTClient)
            response = restclient.POST(self.public_url, serialized_payload, headers=headers)
        except HTTPError, e:
            if e.code==404:
                raise exc.ResourceNotFound(self.public_url)
            else:
                raise exc.ResourceError(self.public_url, e.code, e.msg, e.fp.read(), method="POST")
 
        # now deserialize the data again, we ask for a utility with the content type
        # as the name
        content_type_charset = response.headers['Content-Type']
        content_type = content_type_charset.split(";")[0] # remove the charset part
        
        deserializer = queryUtility(IDeserialization,name=content_type)
        
        if deserializer is None:
            raise exc.DeserializerNotFound(content_type)

        data = deserializer.deserialize_string(response.body)
        log(DEBUG, 'Post to cap %s response is: %s' % (self.public_url, data))        
        
        return data
        
    def __repr__(self):
        return "<Capability '%s' for %s>" %(self.name, self.public_url)
        
class SeedCapability(Capability):
    """a seed capability which is able to retrieve other capabilities"""
    
    implements(ISeedCapability)
        
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
            caps[name]=Capability(name, parsed_result[name])
            
        return caps
             
        
    def __repr__(self):
        return "<SeedCapability for %s>" %self.public_url
        
####
#### Serialization adapters
####
class ListLLSDSerializer(grok.Adapter):
    """adapter for serializing a dictionary to LLSD
    
    An example:
    >>> d={'foo':'bar', 'test':1234}
    >>> serializer = ISerialization(d)
    >>> serializer.serialize()
    '<?xml version="1.0" ?><llsd><map><key>test</key><integer>1234</integer><key>foo</key><string>bar</string></map></llsd>'
    >>> serializer.content_type
    'application/llsd+xml'
    
    """
    grok.implements(ISerialization)
    grok.context(list)
    
    def __init__(self, context):
        self.context = context
        
    def serialize(self):
        """convert the payload to LLSD"""
        return llsd.format_xml(self.context)
        
    @property
    def content_type(self):
        """return the content type of this serializer"""
        return "application/llsd+xml"


class DictLLSDSerializer(grok.Adapter):
    """adapter for serializing a dictionary to LLSD
    
    An example:
    >>> d={'foo':'bar', 'test':1234}
    >>> serializer = ISerialization(d)
    >>> serializer.serialize()
    '<?xml version="1.0" ?><llsd><map><key>test</key><integer>1234</integer><key>foo</key><string>bar</string></map></llsd>'
    >>> serializer.content_type
    'application/llsd+xml'
    
    """
    grok.implements(ISerialization)
    grok.context(dict)
    
    def __init__(self, context):
        self.context = context
        
    def serialize(self):
        """convert the payload to LLSD"""
        return llsd.format_xml(self.context)
        
    @property
    def content_type(self):
        """return the content type of this serializer"""
        return "application/llsd+xml"
        
class LLSDDeserializer(grok.GlobalUtility):
    """utility for deserializing LLSD data
    
    The deserialization component is defined as a utility because the input
    data can be a string or a file. It might be possible to define this as 
    an adapter on a string but a string is too generic for this. So that's 
    why it is a utility.
    
    You can use it like this:
    
    >>> s='<?xml version="1.0" ?><llsd><map><key>test</key><integer>1234</integer><key>foo</key><string>bar</string></map></llsd>'
    
    We use queryUtility because this returns None instead of an exception
    when a utility is not registered. We use the content type we received
    as the name of the utility. Another option would of course be to subclas
    string to some LLSDString class and use an adapter. We then would need some
    factory for generating the LLSDString class from whatever came back from
    the HTTP call.
    
    So here is how you use that utility:
    >>> deserializer = queryUtility(IDeserialization,name="application/llsd+xml")
    >>> llsd = deserializer.deserialize_string(s)
    >>> llsd
    {'test': 1234, 'foo': 'bar'}

    We can also test this with some non-LLSD string:

    >>> llsd = deserializer.deserialize_string('mumpitz')   # this is not LLSD
    Traceback (most recent call last):
    ...
    DeserializationFailed: deserialization failed for 'mumpitz', reason: 'invalid token at index 0: 109'

    >>> llsd = deserializer.deserialize_string('barfoo') 
    Traceback (most recent call last):
    ...
    DeserializationFailed: deserialization failed for 'barfoo', reason: 'binary notation not yet supported'

    
    """
    grok.implements(IDeserialization)
    grok.name('application/llsd+xml')
    
    def deserialize_string(self, data):
        """deserialize a string"""
    try:
        r = llsd.parse(data)
    except llsd.LLSDParseError, e:
        raise exc.DeserializationFailed(data, str(e))
    if r==False:
        raise exc.DeserializationFailed(data, 'result was False')
    return r
        
    def deserialize_file(self, fp):
        """deserialize a file"""
        data = fp.read()
        return self.deserialize_string(data)
        
# TODO: remove this again! Just a workaround for SVC-2682
grok.global_utility(LLSDDeserializer,
                                  provides=IDeserialization,
                                  name='text/html',
                                  direct=False)

# TODO: remove this again! Just a workaround for SVC-2720
grok.global_utility(LLSDDeserializer,
                                  provides=IDeserialization,
                                  name='application/xml',
                                  direct=False)


