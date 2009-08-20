
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
import unittest

# pyogp
from pyogp.lib.base.login import Login, LegacyLoginParams
from pyogp.lib.base.exc import *

# pyogp tests
from pyogp.lib.base.tests.mock_xmlrpc import MockXMLRPC
from pyogp.lib.base.tests.base import MockXMLRPCLogin
import pyogp.lib.base.tests.config 

class TestLegacyLogin(unittest.TestCase):

    def setUp(self):

        self.legacy_loginuri = 'http://localhost:12345/login.cgi'
        self.login_params = LegacyLoginParams('firstname', 'lastname', 'secret')

        self.login = Login()

        # override the network client with the mock client pointed at the mock login handler
        self.loginhandler = MockXMLRPC(MockXMLRPCLogin(), self.legacy_loginuri)

    def tearDown(self):

        pass

    def test_legacy_login(self):

        self.login.login(self.legacy_loginuri, self.login_params, 'start_location', handler = self.loginhandler)

        self.assertNotEquals(self.login.response, None, 'Login response is empty when it should be populated')
        self.assertEquals(self.login.response['login'], 'true', 'Successful login response not be parsed correctly for \'login\'')

    def test_legacy_login_return(self):

        result = self.login.login(self.legacy_loginuri, self.login_params, 'start_location', handler = self.loginhandler)
        self.assertEquals(self.login.response, result, 'Login.login should return response in the result set')

    def test_failed_legacy_login(self):

        self.login_params.password = 'badpassword'

        self.assertRaises(LoginError, self.login.login, self.legacy_loginuri, self.login_params, 'start_location', handler = self.loginhandler)

        self.assertEquals(self.login.response['message'], 'key')
        self.assertEquals(self.login.response['login'], 'false', 'Failed login is not being handled properly')

    def test_handle_transform(self):

        # build a custom response
        transform_result = {'next_url':'http://localhost:12345/transform.cgi', 'next_method':'login_to_simulator', 'message':'Roll out!'}

        self.login._init_legacy_login_params(self.legacy_loginuri, self.login_params, 'start')
        self.login.login_params = self.login_params.serialize()
        self.login.handler = self.loginhandler
        self.login._handle_transform(transform_result)

        self.assertNotEquals(self.login.transform_response, None, 'Transform was not followed by login code')
        self.assertEquals(self.login.transform_response, transform_result)

    def test_login_attributes(self):

        self.login.login(self.legacy_loginuri, self.login_params, 'start_location', handler = self.loginhandler)

        for k in self.login_params.serialize():
            self.assert_(self.login.login_params.has_key(k))
        self.assertEquals(self.login.type, 'legacy')
        self.assertEquals(self.login.transform_response, None)
        self.assertEquals(self.login.response, {'region_y': '256', 'region_x': '256', 'first_name': '"first"', 'secure_session_id': '00000000-0000-0000-0000-000000000000', 'sim_ip': '127.0.0.1', 'agent_access': 'M', 'circuit_code': '600000000', 'look_at': '[r0.9963859999999999939,r-0.084939700000000006863,r0]', 'session_id': '00000000-0000-0000-0000-000000000000', 'udp_blacklist': 'EnableSimulator,TeleportFinish,CrossedRegion', 'seed_capability': 'https://somesim:12043/cap/00000000-0000-0000-0000-000000000000', 'agent_id': '00000000-0000-0000-0000-000000000000', 'last_name': 'last', 'inventory_host': 'someinvhost', 'start_location': 'last', 'sim_port': '13001', 'message': 'message', 'login': 'true', 'seconds_since_epoch': '1234567890'})

    def test_unknown_loginuri(self):

        self.fake_loginuri = 'http://localhost:12345/fake.cgi'

        self.assertRaises(LoginError, self.login.login, self.fake_loginuri, self.login_params, 'start_location', handler = self.loginhandler)

    def test_parse_legacy_start_location_tuple(self):

        startloc = self.login._parse_legacy_start_location(('region', 128, 128, 32))

        self.assertEquals(startloc, 'uri:region&128&128&32')

    def test_parse_legacy_start_location_bad_tuple(self):

        startloc = self.login._parse_legacy_start_location(('region', 128, 128, '32'))

        self.assertEquals(startloc, self.login.settings.DEFAULT_START_LOCATION)

    def test_parse_legacy_start_location_bad_tuple2(self):

        startloc = self.login._parse_legacy_start_location(('region', 128, 128))

        self.assertEquals(startloc, self.login.settings.DEFAULT_START_LOCATION)

    def test_parse_legacy_start_location_string(self):

        startloc = self.login._parse_legacy_start_location('region')

        self.assertEquals(startloc, 'uri:region&128&128&30')

    def test_parse_legacy_start_location_string_2(self):

        startloc = self.login._parse_legacy_start_location('region/128')

        self.assertEquals(startloc, 'uri:region&128&128&30')

    def test_parse_legacy_start_location_string_3(self):

        startloc = self.login._parse_legacy_start_location('region/128/128')

        self.assertEquals(startloc, 'uri:region&128&128&30')

    def test_parse_legacy_start_location_string_4(self):

        startloc = self.login._parse_legacy_start_location('region/128/128/30')

        self.assertEquals(startloc, 'uri:region&128&128&30')

    def test_parse_legacy_start_location_uri_string(self):

        startloc = self.login._parse_legacy_start_location('URI:Region&128&128&30')

        self.assertEquals(startloc, 'uri:Region&128&128&30')

    def test_parse_legacy_start_location_uri_string_region_only(self):

        startloc = self.login._parse_legacy_start_location('URI:Region')

        self.assertEquals(startloc, 'uri:Region&128&128&30')

    def test_parse_legacy_start_location_default(self):

        startloc = self.login._parse_legacy_start_location(21)

        self.assertEquals(startloc, self.login.settings.DEFAULT_START_LOCATION)

    def test_init_legacy_login_params(self):

        loginuri = 'http://localhost:12345/login.cgi'
        start_location = 'region'

        self.login._init_legacy_login_params(loginuri, self.login_params, start_location)

        self.assertEquals(self.login.loginuri, loginuri)
        self.assertEquals(self.login.login_params['passwd'], 'secret')
        self.assertEquals(self.login.start_location, 'uri:region&128&128&30')
        self.assertEquals(self.login.login_params['start'], 'uri:region&128&128&30')

    def test_init_legacy_login_params_keys(self):

        loginuri = 'http://localhost:12345/login.cgi'
        #login_params = {'first' : 'firstname', 'last' : 'lastname', 'passwd' : 'secret'}
        start_location = 'region'

        self.login._init_legacy_login_params(loginuri, self.login_params, start_location)

        {'read_critical': True, 'last': 'lastname', 'passwd': 'secret', 'id0': '', 'agree_to_tos': True, 'start': 'uri:region&128&128&30', 'mac': '', 'version': 'pyogp 0.1', 'channel': 'pyogp', 'first': 'firstname'}

        self.assert_(self.login.login_params.has_key('read_critical') and
            self.login.login_params.has_key('last') and
            self.login.login_params.has_key('passwd') and
            self.login.login_params.has_key('id0') and
            self.login.login_params.has_key('agree_to_tos') and
            self.login.login_params.has_key('start') and 
            self.login.login_params.has_key('mac') and
            self.login.login_params.has_key('version') and
            self.login.login_params.has_key('channel') and
            self.login.login_params.has_key('first'))

    def test_preserved_login_input_params(self):

        result = self.login.login(self.legacy_loginuri, self.login_params, 'start_location', handler = self.loginhandler)

        self.assertEquals(self.login_params.serialize()['first'], self.login.input_params['firstname'])
        self.assertEquals(self.login_params.serialize()['last'], self.login.input_params['lastname'])
        self.assertEquals(self.login_params.serialize()['passwd'], self.login.input_params['password'])

    def test_LegacyLoginParams(self):

        login_params = LegacyLoginParams('first', 'last', 'password')

        self.assertEquals(login_params.firstname, 'first')
        self.assertEquals(login_params.lastname, 'last')
        self.assertEquals(login_params.password, 'password')

        serialized = login_params.serialize()

        self.assertEquals(serialized, {'passwd': 'password', 'last': 'last', 'first': 'first'})

# ToDo:
# 1. front to back transform

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLegacyLogin))
    return suite


