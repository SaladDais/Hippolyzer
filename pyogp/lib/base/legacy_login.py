"""
@file legacy_login.py
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

# standard python modules
from time import sleep
import xmlrpclib
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

# linden python modules
from indra.base import llsd, lluuid

# pyogp.lib.base
import exc
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.caps import SeedCapability

# initialize logging
logger = getLogger('pyogp.lib.base.legacy_login')
log = logger.log

'''
get an agent 
enable login via llsd
enable login via xmlrpc
populate region with the return value
'''

# ToDo: update this in the post ZCA context
class LegacyLogin(object):
    """ enables login to an environment not implementing the OGP protocols """

    def __init__(self, uri):
        """ initialize the login endpoint """

        self.uri = uri
        self.credentials = None
        self.loginStatus = None
        self.login_response = {}
        
        #log(DEBUG, 'initializing legacy login to legacy endpoint %s' % (self.uri))
        
    def login(self, credentials, region):
        """ login to the environment and return an agent object via xmlrpc """

        login_params = self.get_extended_credentials(credentials)
        #response = self.post_to_loginuri(login_params)
        self.post_to_loginuri(self.uri)
        data = self.eval_login_response(self.login_response, region) 

        return data
        
    def get_extended_credentials(self, credentials):
        """ get the extra bits needed for login """

        self.credentials = credentials

        settings = Settings()
        default_login_params = settings.get_default_xmlrpc_login_parameters()

        self.credentials['channel'] = default_login_params['channel']
        self.credentials['version'] = default_login_params['version']
        self.credentials['mac'] = default_login_params['mac']
        self.credentials['agree_to_tos'] = default_login_params['agree_to_tos']
        self.credentials['read_critical'] = default_login_params['read_critical']
        self.credentials['id0'] = default_login_params['id0']
                 
        log(DEBUG, 'Initializing legacy login parameters for %s %s' % (self.credentials['first'], self.credentials['last']))

        return self.credentials
       
    def post_to_loginuri(self, login_uri, login_method='login_to_simulator'):
        """ post to a login uri and return the results """

        log(DEBUG, 'Logging %s %s into %s' % (self.credentials['first'], self.credentials['last'], login_uri))

        login = xmlrpclib.Server(login_uri)
        login_handler = login.__getattr__(login_method)
        results = login_handler(self.credentials)

        if results['login'] in ('true', 'false'):
            self.login_response = results
        else:
            # handle transformation

            log(INFO, 'Following a login redirect to %s with method %s. Message: %s' % (results['next_url'], results['next_method'], results['message']))
            self.login_response = self.post_to_loginuri(results['next_url'], results['next_method'])

    def eval_login_response(self, response, region):
        """ parse the login uri response and return an avatar object """
    
        log(DEBUG, 'deserialized login response body = %s' % (response))
        
        try:
            seed_cap_url = response['seed_capability']
            region.set_seed_cap_url(seed_cap_url)
            self.loginStatus = True
            log(INFO, 'logged in to %s' % (self.uri))
        except KeyError:
            raise exc.UserNotAuthorized(self.credentials)
    
        #agent = Agent(region)       
        
        if seed_cap_url is None:
            raise exc.UserRezFailed(region)
        else:
            log(INFO, 'Region %s returned a seed_cap of %s' % (region.regionname, seed_cap_url))
        
        #AND THE REST
        #region.details = response
        
        return response
