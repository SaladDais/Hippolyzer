from zope.interface import implements

from interfaces import IRegion

class Region(object):
    """models a region endpoint"""
    
    implements(IRegion)
    
    def __init__(self, uri):
        """initialize the region with the region uri"""
        self.uri = uri
    
        