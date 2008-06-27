from zope.interface import implements
from zope.component import adapts

from indra.base import llsd


from interfaces import IPlainPasswordCredential, ICredentialSerializer

class PlainPasswordCredential(object):
    """a plain password credential"""
    
    implements(IPlainPasswordCredential)
    
    def __init__(self, firstname, lastname, password):
        """initialize this credential"""
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        

# an adapter to serialize this to LLSD

class PlainPasswordLLSDSerializer(object):
    """converts a plain password credential to LLSD"""
    
    implements(ICredentialSerializer)
    adapts(IPlainPasswordCredential)
    
    def __init__(self, context):
        """initialize this adapter by storing the context (the credential)"""
        self.context = context

    def serialize(self):
        """return the credential as a string"""
        
        loginparams={
               'password'   : self.context.password,
               'lastname'   : self.context.lastname,
               'firstname'  : self.context.firstname
        }

        llsdlist = llsd.format_xml(loginparams)
        return llsdlist
    
    @property
    def headers(self):
        """return HTTP headers needed here"""
        return {"Content-type" : "application/llsd+xml"}

# now we register this adapter so it can be used later:
from zope.component import provideAdapter

# register adapters for the HTML node
provideAdapter(PlainPasswordLLSDSerializer)
