
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
from pyogp.lib.base.agent import Agent, Home
from pyogp.lib.base.login import LegacyLoginParams, OGPLoginParams
from pyogp.lib.base.exc import *

# pyogp tests
from pyogp.lib.base.tests.mock_xmlrpc import MockXMLRPC
from pyogp.lib.base.tests.base import MockXMLRPCLogin, MockAgentDomainLogin
from pyogp.lib.base.network.tests.mockup_client import MockupClient
import pyogp.lib.base.tests.config 

class TestAgent(unittest.TestCase):

    def setUp(self):

        self.legacy_loginuri = 'http://localhost:12345/login.cgi'
        self.ogp_loginuri = 'http://localhost:12345/auth.cgi'
        self.firstname = 'firstname'
        self.lastname = 'lastname'
        self.password = 'secret'

        self.client = Agent()

    def tearDown(self):

        pass

    def test_agent_legacy_login_via_variables(self):

        # override the network client with the mock client pointed at the mock login handler
        self.loginhandler = MockXMLRPC(MockXMLRPCLogin(), self.legacy_loginuri)  

        self.client.login(self.legacy_loginuri, self.firstname, self.lastname, self.password, start_location = 'start', handler = self.loginhandler, connect_region = False)

        self.assertEquals(self.client.login_response, {'region_y': '256', 'region_x': '256', 'first_name': '"first"', 'secure_session_id': '00000000-0000-0000-0000-000000000000', 'sim_ip': '127.0.0.1', 'agent_access': 'M', 'circuit_code': '600000000', 'look_at': '[r0.9963859999999999939,r-0.084939700000000006863,r0]', 'session_id': '00000000-0000-0000-0000-000000000000', 'udp_blacklist': 'EnableSimulator,TeleportFinish,CrossedRegion', 'seed_capability': 'https://somesim:12043/cap/00000000-0000-0000-0000-000000000000', 'agent_id': '00000000-0000-0000-0000-000000000000', 'last_name': 'last', 'inventory_host': 'someinvhost', 'start_location': 'last', 'sim_port': '13001', 'message': 'message', 'login': 'true', 'seconds_since_epoch': '1234567890'})

    def test_agent_legacy_login_via_params(self):

        # override the network client with the mock client pointed at the mock login handler
        self.loginhandler = MockXMLRPC(MockXMLRPCLogin(), self.legacy_loginuri)

        login_params = LegacyLoginParams(self.firstname, self.lastname, self.password)

        self.client.login(self.legacy_loginuri, login_params = login_params, start_location = 'start', handler = self.loginhandler, connect_region = False)

        self.assertEquals(self.client.login_response, {'region_y': '256', 'region_x': '256', 'first_name': '"first"', 'secure_session_id': '00000000-0000-0000-0000-000000000000', 'sim_ip': '127.0.0.1', 'agent_access': 'M', 'circuit_code': '600000000', 'look_at': '[r0.9963859999999999939,r-0.084939700000000006863,r0]', 'session_id': '00000000-0000-0000-0000-000000000000', 'udp_blacklist': 'EnableSimulator,TeleportFinish,CrossedRegion', 'seed_capability': 'https://somesim:12043/cap/00000000-0000-0000-0000-000000000000', 'agent_id': '00000000-0000-0000-0000-000000000000', 'last_name': 'last', 'inventory_host': 'someinvhost', 'start_location': 'last', 'sim_port': '13001', 'message': 'message', 'login': 'true', 'seconds_since_epoch': '1234567890'})

    def test_agent_ogp_login_via_variables(self):

        # override the network client with the mock client pointed at the mock login handler
        self.loginhandler = MockupClient(MockAgentDomainLogin())

        self.client.login(self.ogp_loginuri, self.firstname, self.lastname, self.password, start_location = 'start', handler = self.loginhandler, connect_region = False)

        self.assertEquals(self.client.login_response,  {'agent_seed_capability': 'http://127.0.0.1:12345/seed_cap', 'authenticated': True})

    def test_agent_ogp_login_via_params(self):

        # override the network client with the mock client pointed at the mock login handler
        self.loginhandler = MockupClient(MockAgentDomainLogin())

        login_params = OGPLoginParams(self.firstname, self.lastname, self.password)

        self.client.login(self.ogp_loginuri, self.firstname, self.lastname, self.password, start_location = 'start', handler = self.loginhandler, connect_region = False)

        self.assertEquals(self.client.login_response,  {'agent_seed_capability': 'http://127.0.0.1:12345/seed_cap', 'authenticated': True})

    def test_agent_login_no_account_info(self):

        self.assertRaises(LoginError, self.client.login, self.ogp_loginuri)

    def test_legacy_get_login_params(self):

        self.client.grid_type = 'Legacy'
        params = self.client._get_login_params(self.firstname, self.lastname, self.password)

        self.assertEquals(type(params), type(LegacyLoginParams(self.firstname, self.lastname, self.password)))

    def test_ogp_get_login_params(self):

        self.client.grid_type = 'OGP'
        params = self.client._get_login_params(self.firstname, self.lastname, self.password)

        self.assertEquals(type(params), type(OGPLoginParams(self.firstname, self.lastname, self.password)))

    def test_failed_legacy_login(self):

        self.password = 'badpassword'

        # override the network client with the mock client pointed at the mock login handler
        self.loginhandler = MockXMLRPC(MockXMLRPCLogin(), self.legacy_loginuri)  

        self.assertRaises(LoginError, self.client.login, self.legacy_loginuri, self.firstname, self.lastname, self.password, start_location = 'start', handler = self.loginhandler)

    def test_agent_home_class(self):

        home_string = "{'region_handle':[r261120, r247040], 'position':[r171.622, r148.26, r79.3938], 'look_at':[r0, r1, r0]}"

        home = Home(home_string)

        # Note: have not yet worked out precision on floats. Kinda need to
        self.assertEquals(home.region_handle, [261120, 247040])
        self.assertEquals(home.position.X, 171.62200000000001)
        self.assertEquals(home.position.Y, 148.25999999999999)
        self.assertEquals(home.position.Z, 79.393799999999999)
        self.assertEquals(home.look_at.X, 0)
        self.assertEquals(home.look_at.Y, 1)
        self.assertEquals(home.look_at.Z, 0)
        self.assertEquals(home.global_x, 261120)
        self.assertEquals(home.global_y, 247040)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAgent))
    return suite



