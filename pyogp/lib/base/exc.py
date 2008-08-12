"""
Exceptions for the pyogp library

"""


class Error(Exception):
    """base exception for all pyogp related exceptions"""
    
    
#### Network errors
    
class NetworkError(Error):
    """general network exception"""
    
class ResourceNotFound(NetworkError):
    """raised if a resource couldn't be found
    
    the URL to that resource is stored inside a ``url`` attribute.
    
    """
    def __init__(self, url = ''):
        self.url = url
        
class ResourceError(NetworkError):
    """raised if any other error occurred (usually a 500)
    
    contains ``url`` to the resource and ``code`` and ``message`` and ``body``
    
    """
    
    def __init__(self, url='', code='', message='', body=''):
        self.url = url
        self.code = code
        self.message = message
        self.body = body



### Serialization errors

class SerializationError(Error):
    """serialization related exceptions"""
    


### Deserialization errors
    
class DeserializationError(Error):
    """deserialization related exception"""
    
class DeserializerNotFound(DeserializationError):
    """raised if a deserializer for a certain content type couldn't be found
    
    stores the content type inside a ``content_type`` attribute.
    """
    
    def __init__(self, content_type=''):
        self.content_type = content_type

class DeserializationFailed(DeserializationError):
    """raised if a deserializer couldn't deserialize a payload
    
    stores the payload inside a ``payload`` attribute and the error message
    inside a ``reason`` attribute.
    """
    
    def __init__(self, payload='', reason=''):
        self.payload = payload
        self.reason = reason
      
        
        
### Message System related errors

class MessageSystemError(Error):
    """message system related exception"""
    


##########################
### high level exceptions
##########################

### Agent Domain related errors

class AgentDomainError(Error):
    """base exception for all errors which can occur on an agent domain"""
    
class UserNotFound(AgentDomainError):
    """user couldn't be found
    
    This exception stores the credentials used inside a ``credentials`` attribute
    """
    
    def __init__(self, credentials = None):
        """initialize this exception"""
        self.credentials = credentials
        

class UserNotAuthorized(AgentDomainError):
    """an error raised in case a user couldn't be authorized
    
    stores the credentials used inside a ``credentials`` attribute
    
    """

    def __init__(self, credentials = None):
        """initialize this exception"""
        self.credentials = credentials
    

