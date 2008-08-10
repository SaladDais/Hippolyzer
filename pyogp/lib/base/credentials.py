from zope.interface import implements
from zope.component import adapts

import md5

from indra.base import llsd

import grokcore.component as grok

from interfaces import IPlainPasswordCredential, IMD5PasswordCredential
from interfaces import ISerialization, ICredentialDeserialization

class PlainPasswordCredential(object):
    """a plain password credential"""
    
    implements(IPlainPasswordCredential)
    
    def __init__(self, firstname, lastname, password):
        """initialize this credential"""
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
    
    def __repr__(self):
        """return a string represenation"""
        return "PlainPasswordCredential for '%s %s'" %(self.firstname, self.lastname)

class MD5PasswordCredential(object):
    """a md5 password credential"""
    
    implements(IMD5PasswordCredential)
    
    def __init__(self, firstname, lastname, plainpw='', md5pw=None):
        """initialize this credential"""
        self.firstname = firstname
        self.lastname = lastname
        if md5pw is not None:
            self.password = md5pw
        else:
            self.password = md5.new(plainpw).hexdigest()
    
    def __repr__(self):
        """return a string represenation"""
        return "MD5PasswordCredential for '%s %s'" %(self.firstname, self.lastname)



class PlainPasswordLLSDSerializer(grok.Adapter):
    """converts a plain password credential to LLSD
    
    Here is how you can use it:
    >>> credential = PlainPasswordCredential('Firstname','Lastname','password')
    >>> serializer = ISerialization(credential)
    >>> serializer.serialize()
    '<?xml version="1.0" ?><llsd><map><key>lastname</key><string>Lastname</string><key>password</key><string>password</string><key>firstname</key><string>Firstname</string></map></llsd>'
    >>> serializer.content_type
    'application/llsd+xml'
    """
    
    grok.implements(ISerialization)
    grok.context(IPlainPasswordCredential)
    
    def __init__(self, context):
        """initialize this adapter by storing the context (the credential)"""
        self.context = context

    def serialize(self):
        """return the credential as a string"""
        
        loginparams={
                'password'      : self.context.password,
                'lastname'     : self.context.lastname,
                'firstname'    : self.context.firstname
        }

        llsdlist = llsd.format_xml(loginparams)
        return llsdlist

    @property
    def content_type(self):
        """return HTTP headers needed here"""
        return "application/llsd+xml"

class MD5PasswordLLSDSerializer(PlainPasswordLLSDSerializer):
    """converts a md5 credential object to LLSD XML
    """
    
    grok.implements(ISerialization)
    grok.context(IMD5PasswordCredential)
    
    
    def serialize(self):
        """return the credential as a string"""
        
        loginparams={
                'md5-password' : self.context.password,
                'lastname'     : self.context.lastname,
                'firstname'    : self.context.firstname
        }

        llsdlist = llsd.format_xml(loginparams)
        return llsdlist


class CredentialLLSDDeserializer(grok.GlobalUtility):
    """take an LLSD string and create a credential object

    This is a utility
    """
    grok.implements(ICredentialDeserialization)
    grok.name('application/llsd+xml')

    def deserialize(self, s):
        payload = llsd.parse(s)
        
        # now we dispatch which credential object we need to instantiate
        # this simply depends whether it's md5-password or password we find
        keys = payload.keys()
        if 'firstname' in keys and 'lastname' in keys:
            if payload.has_key("password"):
                return PlainPasswordCredential(payload['firstname'], payload['lastname'], payload['password'])
            elif payload.has_key("md5-password"):
                return MD5PasswordCredential(payload['firstname'], payload['lastname'], md5pw=payload['md5-password'])
        raise Exception("couldn't deserialize credential payload '%s' because no matching format was found!" %str(payload))