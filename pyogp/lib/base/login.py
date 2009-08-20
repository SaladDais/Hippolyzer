
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

# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import xmlrpclib
import re
import sys

# related
from indra.base import llsd

# pyogp
from pyogp.lib.base.exc import LoginError, ParseStartLocError, HTTPError, ResourceError, ResourceNotFound
from pyogp.lib.base.tests.mock_xmlrpc import MockXMLRPC
from pyogp.lib.base.tests.base import MockXMLRPCLogin
from pyogp.lib.base.network.stdlib_client import StdLibClient

# initialize globals
logger = getLogger('login')
log = logger.log

class Login(object):
    """ logs into a login endpoint 

    There are 2 cases here: 'legacy' login and 'OGP' login.
        Legacy = standard Second Life/OpenSim login
        OGP = Open Grid Protocol enabled grid, where one logs into an agent domain

    Example (legacy oriented):

    The login type is determined by parsing the login uri
    'legacy' = login.cgi
    'ogp' = auth.cgi

    Initialize the login class
    >>> login = Login()

    Setup some login parameters.
    >>> login_params = LegacyLoginParams('firstname', 'lastname', 'password')
    >>> login_params = login_params.serialize()

    login stores & returns the response from the loginuri (in our example a mock response)
    >>> login.login('http://localhost:12345/login.cgi', login_params, 'region')
    {'login': 'true', 'seed_capability': 'http://127.0.0.1:12345/seed_cap'}

    >>> login.response['login']
    true

    Sample implementations: examples/sample_login.py
    Tests: tests/login.txt, tests/test_legacy_login.py, tests/test_ogp_login.py
    """

    def __init__(self, settings = None, handler = None):
        """ initialize the login object """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        # this can be either 'legacy' or 'ogp'
        self.type = None

        # storage containers for login attributes
        self.loginuri = None
        self.login_params = {}
        self.input_params = {}
        self.start_location = None

        # this will hold the reponse from the loginuri
        self.response = None

        # holds the transform response if there is one
        self.transform_response = None

        # if we are testing, we can initialize a mock handler 
        self.handler = None

        if self.settings.LOG_VERBOSE: log(INFO, 'Initializing login')

    def login(self, loginuri = None, login_params = None, start_location = None, handler = None):
        """ high level login initiator, returns the login response as a dict"""

        if (re.search('auth.cgi$', loginuri)):

            self.type = 'ogp'

            # prep the login parameters object
            self._init_ogp_login_params(loginuri, login_params, start_location)

            if handler == None and self.handler == None:

                self.handler = StdLibClient()
            else:

                self.handler = handler

            self._post_to_ogp_loginuri()

        elif (re.search('login.cgi$', loginuri)):

            self.type = 'legacy'

            # prep the login parameters object
            self._init_legacy_login_params(loginuri, login_params, start_location)

            # handler can be a mock endpoint for testing, otherwise it's xmlrpc
            if handler == None and self.handler == None:

                # If we are running normally, we need xmlrpc for legacy login
                self._init_legacy_login_handler(self.loginuri)

            else:

                self.handler = handler

            self._post_to_legacy_loginuri()

        else:
            log(WARNING, 'Unknown loginuri type: %s' % (self.loginuri))
            raise LoginError('Unknown loginuri type: %s' % (self.loginuri))

        return self.response

    def _init_legacy_login_handler(self, loginuri):
        """ sets up the xmlrpc handler """

        # MockXMLRPC is the test handler, retain it
        if type(self.handler) == type(MockXMLRPC(MockXMLRPCLogin(), self.loginuri)):
            pass
        else:
            self.handler = xmlrpclib.ServerProxy(self.loginuri)

    def _init_legacy_login_params(self, loginuri = None, login_params = None, start_location = None):
        """ prepares the login attributes for submission """

        if (loginuri != None):
            self.loginuri = loginuri

        if (login_params != None):

            # now store the account data
            self.login_params = login_params.serialize()

            # store the input params
            self.input_params['firstname'] = self.login_params['first']
            self.input_params['lastname'] = self.login_params['last']
            self.input_params['password'] = self.login_params['passwd']

        if (start_location != None):
            self.start_location = self._parse_legacy_start_location(start_location)
        else:
            self.start_location = self.settings.DEFAULT_START_LOCATION

        self.login_params['start'] = self.start_location

        # add some additonal details to the login_params based on what is specified in settings
        # do not overwrite specified settings        
        self._get_extended_legacy_params()

    def _init_ogp_login_params(self, loginuri = None, login_params = None, start_location = None):
        """ prepares the login attributes for submission """

        if (loginuri != None):
            self.loginuri = loginuri

        if (login_params != None):

            # we use content_type for http calls here
            self.content_type = login_params.content_type

            # now store the account data
            self.login_params = login_params.serialize()

            # store the input params
            self.input_params['firstname'] = login_params.firstname
            self.input_params['lastname'] = login_params.lastname
            self.input_params['password'] = login_params.password

        if (start_location != None):
            self.start_location = start_location
        else:
            self.start_location = self.settings.DEFAULT_START_LOCATION

    def _post_to_legacy_loginuri(self, loginuri = None, login_params = None, login_method = 'login_to_simulator'):
        """ post to a login uri and return the results """

        if loginuri != None:
            self.loginuri = loginuri

        if login_params != None:
            self.login_params = login_params.serialize()

        self._init_legacy_login_handler(loginuri)

        log(INFO, 'Logging \'%s %s\' into %s with method: %s' % (self.login_params['first'], self.login_params['last'], self.loginuri, login_method))
        if self.settings.LOG_VERBOSE: log(DEBUG, '\'%s %s\' has the following login parameters: %s' % (self.login_params['first'], self.login_params['last'], self.login_params))

        # This handles the standard 'login_to_simulator' case
        # plus, all the transforms that may need to be followed
        login_handler = self.handler.__getattr__(login_method)

        try:
            self.response = login_handler(self.login_params)
        except Exception, error:
            raise LoginError('Failed to login agent due to: %s' % (error))

        if self.response['login'] in ('true', 'false'):

            self._parse_response()

        else:
            # handle transformation
            self._handle_transform(self.response)

    def _handle_transform(self, transform):
        """ follows a transform """

        if self.settings.LOG_VERBOSE: log(DEBUG, 'Login response for \'%s %s\' is: %s' % (self.input_params['firstname'], self.input_params['lastname'], transform))

        # store the response in the transform response attribute
        self.transform_response = transform

        log(INFO, 'Following a login redirect to %s with method: %s. Message: %s' % (transform['next_url'], transform['next_method'], transform['message']))

        self._post_to_legacy_loginuri(loginuri = transform['next_url'], login_method = transform['next_method'])

    def _get_extended_legacy_params(self):
        """ get the extra bits needed for login """

        # do not overwrite existing settings
        default_login_params = self.settings.get_default_xmlrpc_login_parameters()

        if not self.login_params.has_key('channel'): self.login_params['channel'] = default_login_params['channel']
        if not self.login_params.has_key('version'): self.login_params['version'] = default_login_params['version']
        if not self.login_params.has_key('mac'): self.login_params['mac'] = default_login_params['mac']
        if not self.login_params.has_key('agree_to_tos'): self.login_params['agree_to_tos'] = default_login_params['agree_to_tos']
        if not self.login_params.has_key('read_critical'): self.login_params['read_critical'] = default_login_params['read_critical']
        if not self.login_params.has_key('id0'): self.login_params['id0'] = default_login_params['id0']
        if not self.login_params.has_key('options'): self.login_params['options'] = default_login_params['options']

        log(DEBUG, 'Initializing login parameters for \'%s %s\'' % (self.login_params['first'], self.login_params['last']))

    def _parse_response(self):
        """ evaluates the data contained in the login response 
        This is just a lot of logging for the most part...
        """

        if self.type == 'legacy':

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Login response for \'%s %s\' is: %s' % (self.input_params['firstname'], self.input_params['lastname'], self.response))

            if self.response['login'] == 'true':

                log(INFO, 'Logged in \'%s %s\'' % (self.input_params['firstname'], self.input_params['lastname']))

                if self.response.has_key('message'): log(INFO, 'Login message: %s' % (self.response['message']))

            elif self.response == None:

                log(WARNING, 'Failed to login \'%s %s\' due to %s' % (self.input_params['firstname'], self.input_params['lastname'], 'empty response from loginuri'))

                raise LoginError('Failed login due to empty response from loginuri')

            elif self.response['login'] == 'false':

                log(WARNING, 'Failed login for \'%s %s\', Reason: %s' % (self.input_params['firstname'], self.input_params['lastname'], self.response['message']))

                raise LoginError('Failed login due to: %s' % (self.response['message']))

            else:

                raise LoginError('Unknown error during login')

        elif self.type == 'ogp':

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Login response for \'%s %s\' is: %s' % (self.input_params['firstname'], self.input_params['lastname'], self.response.body))

            if self.response == None:
                log(WARNING, 'Failed to login \'%s %s\' due to %s' % (self.input_params['firstname'], self.input_params['lastname'], 'empty response from loginuri'))
                raise LoginError('Failed login due to empty response from loginuri')
            elif self.response._status == '200 OK':

                self.response = llsd.parse(self.response.body)

                if self.response['authenticated']:
                    log(INFO, 'Logged in \'%s %s\'' % (self.input_params['firstname'], self.input_params['lastname']))
                elif not self.response['authenticated']:
                    log(WARNING, 'Failed login for \'%s %s\', Reason: %s' % (self.input_params['firstname'], self.input_params['lastname'], self.response['message']))
                    raise LoginError('Failed login due to: %s' % (self.response['message']))
            else:

                raise LoginError('Unknown error during login')

        else:

            return

    def _parse_legacy_start_location(self, start_location):
        """ make sure a user specified start location is in the correct form """

        # for now, we accept a region name, or a tuple containing region name, x, y, z
        # x, y, and z must be integers

        if type(start_location) == tuple:
            try:
                return 'uri:%s&%i&%i&%i' % (start_location[0], start_location[1], start_location[2], start_location[3])
            except IndexError, error:
                log(WARNING, 'Invalid start_location specified (%s), using default of \'%s\'' % (start_location, self.settings.DEFAULT_START_LOCATION))
                return self.settings.DEFAULT_START_LOCATION
            except TypeError, error:
                log(WARNING, 'Invalid start_location specified (%s), using default of \'%s\'' % (start_location, self.settings.DEFAULT_START_LOCATION))
                return self.settings.DEFAULT_START_LOCATION
        elif type(start_location) == str and re.match("uri:", start_location[0:4].lower()):
            location = start_location.split(":")[1]
            mg = location.split('&',3)
            # try forcing to ints
            if len(mg) == 4:
                return 'uri:%s&%i&%i&%i' % (mg[0],int(mg[1]),int(mg[2]),int(mg[3]))
            elif len(mg) == 3:
                return 'uri:%s&%i&%i&30' % (mg[0],int(mg[1]),int(mg[2]))
            elif len(mg) == 2:
                return 'uri:%s&%i&128&30' % (mg[0],int(mg[1]))
            elif len(mg) == 1:
                return 'uri:%s&128&128&30' % mg[0]
            else:
                return self.settings.DEFAULT_START_LOCATION

        elif type(start_location) == str:
            mg = start_location.split('/',3)
            # try forcing to ints
            if len(mg) == 4:
                return 'uri:%s&%i&%i&%i' % (mg[0],int(mg[1]),int(mg[2]),int(mg[3]))
            elif len(mg) == 3:
                return 'uri:%s&%i&%i&30' % (mg[0],int(mg[1]),int(mg[2]))
            elif len(mg) == 2:
                return 'uri:%s&%i&128&30' % (mg[0],int(mg[1]))
            elif len(mg) == 1:
                return 'uri:%s&128&128&30' % mg[0]
            else:
                return self.settings.DEFAULT_START_LOCATION
        else:
            # if we cannot make sense of what is passed in, use the settings default
            return self.settings.DEFAULT_START_LOCATION

    def _post_to_ogp_loginuri(self, loginuri = None, login_params = None, start_location = None):
        """ logs in to an agent domain's loginuri """

        if loginuri != None:
            self.loginuri = loginuri

        # we expect an OGPLoginParams object here
        if login_params != None:
            self.login_params = login_params.serialize()
            # store the input params
            for k in self.login_params:
                self.input_params[k] = login_params[k]

        headers = {'Content-Type': self.content_type}

        log(INFO, 'Logging in to %s as %s %s' % (self.loginuri, self.input_params['firstname'], self.input_params['lastname']))
        if self.settings.LOG_VERBOSE: log(DEBUG, '\'%s %s\' has the following login parameters: %s with headers of: %s' % (self.input_params['firstname'], self.input_params['lastname'], self.login_params, headers))

        try:
            self.response = self.handler.POST(self.loginuri, self.login_params, headers=headers)
            self._parse_response()
        except HTTPError, error:
            if error.code==404:
                raise ResourceNotFound(self.login_uri)
            else:
                raise ResourceError(self.loginuri, error.code, error.msg, error.fp.read(), method="POST")

class LegacyLoginParams(object):
    """ a legacy plain password credential """

    def __init__(self, firstname, lastname, password):
        """ initialize this credential """

        self.firstname = firstname
        self.lastname = lastname
        self.password = password

    def __repr__(self):
        """ return a string representation """

        return 'Legacy login instance for \'%s %s\'' %(self.firstname, self.lastname)

    def serialize(self):
        """ return a dictionary of login params """

        login_params = {
            'first': self.firstname,
            'last': self.lastname,
            'passwd': self.password
        }

        return login_params

class OGPLoginParams(object):
    """ an OGP plain password credential """

    def __init__(self, firstname, lastname, password):
        """ initialize this credential """

        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.content_type = 'application/llsd+xml'

    def __repr__(self):
        """ return a string representation """

        return 'OGP login parameters for \'%s %s\'' % (self.firstname, self.lastname)

    def serialize(self):
        """ return a dictionary of login params """

        login_params = {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'password': self.password
        }

        llsd_params = llsd.format_xml(login_params)

        return llsd_params



