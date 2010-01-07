
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
from pyogp.lib.base.event_queue import EventQueueClient
from pyogp.lib.base.exc import DataParsingError, HTTPError

# initialize logging
logger = getLogger('pyogp.lib.base.caps_proxy')

class CapabilitiesProxy(object):
    """ an application class for wsgiref.simple_server which handles 
    proxyied http requests and responses for capabilities """

    def __init__(self,
                seed_cap_url, 
                proxy_host_ip, 
                proxy_host_port,
                message_handler = None, 
                restclient = None):

        # populated initially via the login response
        self.seed_cap_url = seed_cap_url

        # the local proxy info, needed for building urls to send to the viewer
        self.proxy_host_ip = proxy_host_ip
        self.proxy_host_port = proxy_host_port

        # allow the message handler to be passed in
        # otherwise, just set one up
        if message_handler != None:
            self.message_handler = message_handler
        else:
            from pyogp.lib.base.message.message_handler import MessageHandler
            self.message_handler = MessageHandler()

        # we may in the future use something other than urllib2 (StdLibClient)
        if restclient == None:
            from pyogp.lib.base.network.stdlib_client import StdLibClient
            self.restclient = StdLibClient() 
        else:
            self.restclient = restclient

        # stores the capability url <-> proxy uuid combo
        self.proxy_map = {}

        # stored the url:cap name map
        self.capability_map = {}

        # stores the event_queue info for parsing special data
        self.event_queue_client = EventQueueClient()
        self.event_queue_url = None

        # init the seed cap proxy
        self.add_proxy(self.seed_cap_url, 'seed_capability')

        logger.info("Initialized the CapabilitiesProxy for %s" %
                    (self.seed_cap_url))

    def add_proxy(self, url, capname):
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

            # store the url:capname 
            self.capability_map[url] = capname

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
            del self.capability_map[val]
        except KeyError:
            pass
        
    def swap_cap_urls(self, cap_map):
        """ takes the response to a seed_cap request for cap urls
        and maps proxy urls in place of the ones for the sim 
        """

        # we expect a dict of {'capname':'url'}
        for cap in cap_map:

            # store the EventQueueGet url separately
            if cap == 'EventQueueGet':
                self.event_queue_url = cap_map[cap]
            cap_proxy_uuid = self.add_proxy(cap_map[cap], cap)
            cap_map[cap] = "http://%s:%s/%s" % (self.proxy_host_ip, 
                                                self.proxy_host_port,                
                                                cap_proxy_uuid)

            # store the url:capname 
            self.capability_map[cap_map[cap]] = cap

        return cap_map

    def __call__(self, environ, start_response):
        """ handle a specific cap request and response using webob objects"""

        self.environ = environ
        self.start = start_response
        self.request = Request(environ)
        self.response = Response()

        logger.info("Calling cap %s (%s) via %s with body of: %s" % 
                    (self.capability_map[self.proxy_map[self.request.path[1:]]],
                    self.proxy_map[self.request.path[1:]], 
                    self.request.method, 
                    self.request.body))

        # urllib2 will return normally if the reponse status = 200
        # returns HTTPError if not
        # trap and send back to the viewer in either case
        try:

            if self.request.method=="GET":

                proxy_response = self.restclient.GET(self.proxy_map[self.request.path[1:]])

            elif self.request.method == "POST":

                proxy_response = self.restclient.POST(self.proxy_map[self.request.path[1:]],
                                                        self.request.body)

            logger.info("Cap %s (%s) responded with status %s and body of: %s" % 
                        (self.capability_map[self.proxy_map[self.request.path[1:]]],
                        self.proxy_map[self.request.path[1:]], 
                        proxy_response.status, 
                        proxy_response.body))

            # build the webob.Response to send to the viewer
            status = proxy_response.status

            # if we are parsing the seed cap response, swap the cap urls
            # with our proxied ones
            if self.proxy_map[self.request.path[1:]] == self.seed_cap_url:

                cap_map = self.swap_cap_urls(llsd.parse(proxy_response.body))
                data = llsd.format_xml(cap_map)

            # if we are parsing the event queue, decode the data
            # then curry it on out 
            elif self.proxy_map[self.request.path[1:]] == self.event_queue_url:
                
                self.event_queue_client._parse_result(llsd.parse(proxy_response.body))
                data = proxy_response.body

            # otherwise, just proxy the data
            else:

                data = proxy_response.body

        # trap the HTTPError and build the appropriate response for the caller
        except HTTPError, error:
            status = error.code
            data = error.msg

        return self.send_response(status, data)        


    def send_response(self, status, body=''):
        """ send the response back to the caller """

        logger.debug("Sending cap response to viewer: Status:%s Body:%s" % (status, body))

        self.response.status = status
        self.response.body = body
        return self.response(self.environ, self.start)