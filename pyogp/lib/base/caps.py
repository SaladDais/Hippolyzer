import urllib2

from zope.interface import implements
from zope.component import queryUtility, adapts, getUtility
import grokcore.component as grok
from indra.base import llsd

from interfaces import ICapability, ISeedCapability
from interfaces import ISerialization, IDeserialization
from network import IRESTClient, HTTPError


class Capability(object):
    """models a capability"""
    
    implements(ICapability)
    
    def __init__(self, name, public_url):
        """initialize the capability"""
        
        self.name = name
        self.public_url = public_url
        
    def POST(self,payload,custom_headers={}):
        """call this capability, return the parsed result"""
        
        # serialize the data
        serializer = ISerialization(payload)
        content_type = serializer.content_type
        serialized_payload = serializer.serialize()
        
        headers = {"Content-type" : content_type}
        headers.update(custom_headers)  # give the user the ability to add headers 
        
        # TODO: better errorhandling with own exceptions
        try:
            restclient = getUtility(IRESTClient)
            response = restclient.POST(self.public_url, serialized_payload, headers=headers)
        except HTTPError, e:
            print "** failure while calling cap:",
            print e.fp.read()
            raise
            
        # now deserialize the data again, we ask for a utility with the content type
        # as the name
        content_type_charset = response.headers['Content-Type']
        content_type = content_type_charset.split(";")[0] # remove the charset part
        
        deserializer = queryUtility(IDeserialization,name=content_type)
        if deserializer is None:
            # TODO: do better error handling here
            raise "deserialization for %s not supported" %(content_type)
        return deserializer.deserialize_string(response.body)
        
    def __repr__(self):
        return "<Capability for %s>" %self.public_url
        
class SeedCapability(Capability):
    """a seed capability which is able to retrieve other capabilities"""
    
    implements(ISeedCapability)
        
    def get(self, names=[]):
        """if this is a seed cap we can retrieve other caps here"""
        payload = {'caps':names} 
        parsed_result = self.POST(payload)['caps']
        
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
    
    """
    grok.implements(IDeserialization)
    grok.name('application/llsd+xml')
    
    def deserialize_string(self, data):
        """deserialize a string"""
        return llsd.parse(data)
        
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



