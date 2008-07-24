
class HTTPError(Exception):
    """an HTTP error"""
    
    def __init__(self, code, msg, fp, details=""):
        """initialize this exception"""
        self.code = code
        self.msg = msg
        self.details = details
        self.fp = fp
        
    def __str__(self):
        """return a string representation"""
        return "%s %s" %(self.code, self.msg)
    
