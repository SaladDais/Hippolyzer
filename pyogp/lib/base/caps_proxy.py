
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

# standard
from logging import getLogger
from webob import Request, Response

# related
from indra.base import llsd
from eventlet import util

# the following makes socket calls nonblocking. magic
util.wrap_socket_with_coroutine_socket()

# pyogp
from pyogp.lib.base.datatypes import UUID
from pyogp.lib.base.exc import DataParsingError
from pyogp.lib.base.network.stdlib_client import StdLibClient

# initialize logging
logger = getLogger('pyogp.lib.base.caps_proxy')

class CapabilitiesProxy(object):
    """ a manager class for proxyied http requests and responses"""

    def __init__(self,
                seed_cap_url, 
                proxy_host_ip, 
                proxy_host_port, 
                restclient = None):

        self.seed_cap_url = seed_cap_url
        self.proxy_host_ip = proxy_host_ip
        self.proxy_host_port = proxy_host_port
        
        if restclient == None: 
            self.restclient = StdLibClient() 
        else:
            self.restclient = restclient

        self.proxy_map = {}

        self.add_proxy(self.seed_cap_url)

        logger.info("Initialized the CapabilitiesProxy for %s" %
                    (seed_cap_url))

    def add_proxy(self, url):
        """ adds the url and it's proxy, and the proxy and it's url"""

        # make available UUID <-> url dicts
        # we map each since the pairs are unique
        # and since we need to do lookups both ways (?)
        try:
            test = self.proxy_map[url]
        except KeyError:
            uuid = str(UUID().random())
            self.proxy_map[url] = uuid
            self.proxy_map[uuid] = url

        return uuid

    def remove_proxy(self, proxied):
        """ removes the url and it's proxy, and the proxy and it's url"""

        val = self.proxy_map[proxied]
        
        try:
            del self.proxy_map[proxied]
        except KeyError:
            pass

        try:
            del self.proxy_map[val]
        except KeyError:
            pass
        
    '''
    class HTTPProxyApp(object):
        """ a app for handling proxied http requests to capabilities"""
    '''

    def swap_cap_urls(self, cap_map):
        """ takes the response to a seed_cap request for cap urls
        and maps proxy urls in place of the ones for the sim 
        """

        # we expect a dict of {'capname':'url'}
        for cap in cap_map:
            cap_proxy_uuid = self.add_proxy(cap_map[cap])
            cap_map[cap] = "http://%s:%s/%s" % (self.proxy_host_ip, 
                                                self.proxy_host_port,                
                                                cap_proxy_uuid)

        return cap_map

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start = start_response
        self.request = Request(environ)
        self.response = Response()

        logger.debug("Calling cap %s via %s with body of: %s" % 
                    (self.proxy_map[self.request.path[1:]], 
                    self.request.method, 
                    self.request.body))

        # todo: catch 404 and 500s

        if self.request.method=="GET":
            proxy_response = self.restclient.GET(self.proxy_map[self.request.path[1:]])
        elif self.request.method == "POST":
            proxy_response = self.restclient.POST(self.proxy_map[self.request.path[1:]], self.request.body)

        logger.debug("Cap %s responded with status %s and body of: %s" % 
                    (self.proxy_map[self.request.path[1:]], 
                    proxy_response.status, 
                    proxy_response.body))

        # build the response to the viewer
        status = proxy_response.status

        # if we are responding to the seed cap, swap the cap urls
        if self.proxy_map[self.request.path[1:]] == self.seed_cap_url:
            cap_map = self.swap_cap_urls(llsd.parse(proxy_response.body))
            data = llsd.format_xml(cap_map)
        else:
            data = proxy_response.body
            
        
        return self.send_response(status, data)        
        '''
        data = self.request.body

        if self.request.path=="/network/get" and self.request.method=="GET":
            self.response.status=200
            self.response.body="Hello, World"
            return self.response(self.environ, self.start)
        elif self.request.path=="/network/post" and self.request.method=="POST":
            data = self.request.body
            self.response.status=200
            self.response.body="returned: %s" %data
            return self.response(self.environ, self.start)
        else:
            return self.send_response(404, 'resource not found.')
        '''

    def send_response(self, status, body=''):
        logger.debug(body)
        self.response.status = status
        self.response.body = body
        return self.response(self.environ, self.start)