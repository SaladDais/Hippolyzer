
"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""

import urllib2
import os

from pyogp.lib.base.exc import HTTPError

from webob import Request, Response

class StdLibClient(object):
    """ implement a REST client on top of urllib2 """

    def GET(self, url, headers={}):
        """ GET a resource """ 

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
        """ POST data to a resource """

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

