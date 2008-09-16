"""
@file mockup_client.py
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

from zope.interface import implements
import urlparse

from pyogp.lib.base.network.interfaces import IRESTClient
from exc import HTTPError

from webob import Request, Response
from webob.exc import HTTPException, HTTPExceptionMiddleware

from cStringIO import StringIO

class MockupClient(object):
    """implement a REST client on top of urllib2"""
    
    def __init__(self, wsgi_app):
        self.app=wsgi_app
        
    def strip_url(self, url):
        """remove server/host from the URL"""
        o = urlparse.urlparse(url)
        p=o[2]
        if o[4]:
            p=p+"?"+o[4]
        if o[5]:
            p=p+"#"+o[5]
        return url

    def GET(self, url, headers={}):
        """GET a resource"""
        request = Request.blank(self.strip_url(url))
        request.method="GET"
        response = request.get_response(self.app)
        if not response.status.startswith("2"):
            parts = response.status.split(" ")
            msg = " ".join(parts[1:])
            raise HTTPError(response.status_int, msg, StringIO(response.body))
        return response

    def POST(self, url, data, headers={}):
        """POST data to a resource"""        
        request = Request.blank(self.strip_url(url))
        request.body = data
        request.method="POST"
        response = request.get_response(self.app)
        if not response.status.startswith("2"):
            parts = response.status.split(" ")
            msg = " ".join(parts[1:])
            raise HTTPError(response.status_int, msg, StringIO(response.body))
        return response
