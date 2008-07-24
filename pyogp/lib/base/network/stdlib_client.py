from zope.interface import implements
import urllib2

from pyogp.lib.base.network.interfaces import IRESTClient
from exc import HTTPError

from webob import Request, Response

class StdLibClient(object):
    """implement a REST client on top of urllib2"""
    
    def GET(self, url, headers={}):
        """GET a resource"""        
        request = urllib2.Request(url, headers=headers)
        try:
            result = urllib2.urlopen(request)
        except urllib2.HTTPError, error:
            raise HTTPError(error.code,error.msg,error.fp)
        
        # convert back to webob
        headerlist = result.headers.items()
        status = "%s %s" %(result.code, result.msg)
        response = Response(body = result.read(), status = status, headerlist = headerlist)
        return response

    def POST(self, url, data, headers={}):
        """POST data to a resource"""        
        request = urllib2.Request(url, data, headers=headers)
        try:
            result = urllib2.urlopen(request)
        except urllib2.HTTPError, error:
            raise HTTPError(error.code,error.msg,error.fp)
        
        # convert back to webob
        headerlist = result.headers.items()
        status = "%s %s" %(result.code, result.msg)
        response = Response(body = result.read(), status = status, headerlist = headerlist)
        return response
        
        
        
        
                
        
        
        
        