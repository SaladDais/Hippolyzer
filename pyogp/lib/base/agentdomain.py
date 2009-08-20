
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

# std lib
import urllib2
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

# related
from indra.base import llsd

# pyogp
from pyogp.lib.base.network.stdlib_client import StdLibClient, HTTPError
from pyogp.lib.base.caps import SeedCapability
import pyogp.lib.base.exc
from pyogp.lib.base.settings import Settings

# initialize logging
logger = getLogger('pyogp.lib.base.agentdomain')
log = logger.log

class AgentDomain(object):
    """an agent domain endpoint"""

    def __init__(self, uri, restclient = None):
        """ initialize the agent domain endpoint """

        if restclient == None: 
            self.restclient = StdLibClient() 
        else:
            self.restclient = restclient 


        self.settings = Settings()
        self.login_uri = uri
        self.credentials = None

        self.connectedStatus = False

        self.capabilities = {}
        self.agentdomain_caps_list = ['rez_avatar/place']
        self._isEventQueueRunning = False

        self.seed_cap = None
        log(DEBUG, 'initializing agent domain: %s' %self)

    def login(self, credentials):
        """ login to the agent domain """

        response = self.post_to_loginuri(credentials)

        self.eval_login_response(response)   

    def post_to_loginuri(self, credentials):
        """ post to login_uri and return response """

        self.credentials = credentials
        log(INFO, 'Logging in to %s as %s %s' % (self.login_uri, self.credentials.firstname, self.credentials.lastname))

        payload = credentials.serialize()
        content_type = credentials.content_type
        headers = {'Content-Type': content_type}

        # now create the request. We assume for now that self.uri is the login uri
        # TODO: make this pluggable so we can use other transports like eventlet in the future
        # TODO: add logging and error handling

        try:
            response = self.restclient.POST(self.login_uri, payload, headers=headers)
        except HTTPError, error:
            if error.code==404:
                raise ResourceNotFound(self.login_uri)
            else:
                raise ResourceError(self.login_uri, error.code, error.msg, error.fp.read(), method="POST")

        return response

    def eval_login_response(self, response):
        """ parse the login uri response """

        seed_cap_url_data = self.parse_login_response(response)
        try:
            seed_cap_url = seed_cap_url_data['agent_seed_capability']
            self.seed_cap = SeedCapability('seed_cap', seed_cap_url, self.restclient)
            self.connectedStatus = True
            log(INFO, 'logged in to %s' % (self.login_uri))
        except KeyError:
            raise UserNotAuthorized(self.credentials)

    def parse_login_response(self, response):   
        """ parse the login uri response and returns deserialized data """

        data = llsd.parse(response.body)

        log(DEBUG, 'deserialized login response body = %s' % (data))

        return data

    def place_avatar(self, region_uri, position=[117,73,21]):
        """ handles the rez_avatar/place cap on the agent domain, populates some initial region attributes """

        # wow, this needs some thought... place avatar should really move to the region domain...

        if not self.capabilities.has_key('rez_avatar/place'):
            self.capabilities['rez_avatar/place'] = self.seed_cap.get(['rez_avatar/place'])['rez_avatar/place']

        payload = {'public_region_seed_capability' : region_uri, 'position':position} 
        result = self.capabilities['rez_avatar/place'].POST(payload)

        if result['region_seed_capability'] is None:
            raise UserRezFailed(region)
        else:
            log(INFO, 'Region_uri %s returned a seed_cap of %s' % (region_uri, result['region_seed_capability']))

        log(DEBUG, 'Full rez_avatar/place response is: %s' % (result))

        return result

    def get_agentdomain_capabilities(self):
        """ queries the region seed cap for capabilities """

        if (self.seed_cap == None):
            raise RegionSeedCapNotAvailable("querying for agents's agent domain capabilities")
            # well then get it
            # return something?
        else:

            log(INFO, 'Getting caps from agent domain seed cap %s' % (self.seed_cap))

            # use self.region_caps.keys() to pass a list to be parsed into LLSD            
            self.capabilities = self.seed_cap.get(self.agentdomain_caps_list)

    def _processEventQueue(self):

        self._isEventQueueRunning = True


        if self.capabilities['event_queue'] == None:
            raise RegionCapNotAvailable('event_queue')
            # change the exception here (add a new one)
        else:
            while self._isEventQueueRunning:

                # need to be able to pull data from a queue somewhere
                data = {}
                api.sleep(self.settings.agentdomain_event_queue_interval)

                #if self.last_id != -1:
                    #data = {'ack':self.last_id, 'done':False}

                result = self.capabilities['event_queue'].POST(data)

                self.last_id = result['id']

                #log(DEBUG, 'region event queue cap called, returned id: %s' % (self.last_id))

                log(DEBUG, 'AgentDomain EventQueueGet result: %s' % (result))



