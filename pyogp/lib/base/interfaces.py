"""
@file interfaces.py
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

# preserving contents as comments
pass

'''
from zope.interface import Interface, Attribute

class ICredential(Interface):
    """base interface for credentials"""
    
class IPlainPasswordCredential(ICredential):
    """a plain password credential"""
    
    firstname = Attribute("""first name of avatar""")
    lastname = Attribute("""last name of avatar""")
    password = Attribute("""plain password""")

class IMD5PasswordCredential(ICredential):
    """an md5 password credential"""
    
    firstname = Attribute("""first name of avatar""")
    lastname = Attribute("""last name of avatar""")
    password = Attribute("""password as md5 hexdigest""")
   
    
class ISerialization(Interface):
    """serialization functions"""
    
    def serialize():
        """return the serialized version of the context"""
        
    content_type = Attribute("""the content type of the serializer""")
    
class IDeserialization(Interface):
    """deserialization functions"""
    
    def deserlialize():
        """deserialize the context"""
    
    
class ICredentialDeserialization(Interface):
    """converts a credential to a serialized format for sending it over the network"""
    
    def deserialize():
        """deserialize the context"""
                

class IAgent(Interface):
    """models an agent"""
    
    agentdomain = Attribute("""the agent domain endpoint""")
    

class IAgentDomain(Interface):
    """an agent domain"""
    seed_cap = Attribute("""the seed capability""")
        
class IRegion(Interface):
    """a region endpoint"""
    
    def place_avatar(agent):
        """place an avatar on this region, returns IAvatar"""
        
class IAvatar(Interface):
    """an OGP avatar (region representation of an agent)"""
    
    def establish_presence():
        """for now it will do a loop to establish a presence on a region"""
        
        
class IPlaceAvatar(Interface):
    """adapts an agents to a method which can place an avatar on a region"""
    
    def __call__(region):
        """takes a region objects and tries to place the agent there as an avatar
        
        return an IAvatar"""
        
class IEventQueueGet(Interface):
    """adapts an agent domain to the event queue get functionality"""

    def __call__(payload={}):
        """call the event queue and try to get some event via long poll.

        Optionally post some payload to it
        """
    
        
class ICapability(Interface):
    """a capability"""
    
    name = Attribute('''name of the capability''')
    private_url = Attribute('''private url of this capability''')
    
    def __call__(payload):
        """call this capability
        
        payload  -- the payload as python dictionary
        returns a python dictionary with the results
        
        """
    
class ISeedCapability(ICapability):
    """a seed capability which is able to retrieve further capabilities"""
    
    def get(names=[]):
        """retrieve the given set of named capabilities
        
        returns a dict of ICapabilty objects keyed by their name"""
'''
