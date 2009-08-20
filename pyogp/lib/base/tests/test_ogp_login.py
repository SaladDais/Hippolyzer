
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
from pyogp.lib.base.login import Login, OGPLoginParams
from pyogp.lib.base.exc import *

# pyogp tests
from pyogp.lib.base.tests.base import MockAgentDomainLogin
from pyogp.lib.base.network.tests.mockup_client import MockupClient
import pyogp.lib.base.tests.config 

class TestOGPLogin(unittest.TestCase):

    def setUp(self):

        self.ogp_loginuri = 'http://localhost:12345/auth.cgi'
        self.login_params = OGPLoginParams('firstname', 'lastname', 'secret')

        self.login = Login()

        # override the network client with the mock client pointed at the mock login handler
        self.loginhandler = MockupClient(MockAgentDomainLogin())

    def tearDown(self):

        pass

    def test_OGPLogin(self):

        response = self.login.login(self.ogp_loginuri, self.login_params, 'region', handler = self.loginhandler)

        self.assertEquals(response, {'authenticated': True, 'agent_seed_capability': 'http://127.0.0.1:12345/seed_cap'})
        self.assertEquals(self.login.response['authenticated'], True)
        self.assertEquals(self.login.response['agent_seed_capability'], 'http://127.0.0.1:12345/seed_cap')

    def test_ogp_login_return(self):

        result = self.login.login(self.ogp_loginuri, self.login_params, 'start_location', handler = self.loginhandler)
        self.assertEquals(self.login.response, result, 'Login.login should return response in the result set')

    def test_OGPParams(self):

        login_params = OGPLoginParams('first', 'last', 'password')

        self.assertEquals(login_params.firstname, 'first')
        self.assertEquals(login_params.lastname, 'last')
        self.assertEquals(login_params.password, 'password')

        serialized = login_params.serialize()

        self.assertEquals(serialized, '<?xml version="1.0" ?><llsd><map><key>lastname</key><string>last</string><key>password</key><string>password</string><key>firstname</key><string>first</string></map></llsd>')

    def test_failed_ogp_login(self):

        self.login_params.password = 'badpassword'

        self.assertRaises(ResourceError, self.login.login, self.ogp_loginuri, self.login_params, 'start_location', handler = self.loginhandler)

    def test_login_attributes(self):

        self.login.login(self.ogp_loginuri, self.login_params, 'start_location', handler = self.loginhandler)

        self.assertEquals(self.login_params.serialize(), self.login.login_params)
        self.assertEquals(self.login.type, 'ogp')
        self.assertEquals(self.login.transform_response, None)
        self.assertEquals(self.login.response, {'agent_seed_capability': 'http://127.0.0.1:12345/seed_cap', 'authenticated': True} )

    def test_unknown_loginuri(self):

        self.fake_loginuri = 'http://localhost:12345/fake.cgi'

        self.assertRaises(LoginError, self.login.login, self.fake_loginuri, self.login_params, 'start_location', handler = self.loginhandler)

    def test_init_ogp_login_params(self):

        loginuri = 'http://localhost:12345/login.cgi'
        start_location = 'region'

        self.login._init_ogp_login_params(loginuri, self.login_params, start_location)

        self.assertEquals(self.login.loginuri, loginuri)
        self.assertEquals(self.login.start_location, 'region')
        self.assertEquals(self.login.login_params, '<?xml version="1.0" ?><llsd><map><key>lastname</key><string>lastname</string><key>password</key><string>secret</string><key>firstname</key><string>firstname</string></map></llsd>')

    def test_preserved_login_input_params(self):

        result = self.login.login(self.ogp_loginuri, self.login_params, 'start_location', handler = self.loginhandler)

        self.assertEquals('firstname', self.login.input_params['firstname'])
        self.assertEquals('lastname', self.login.input_params['lastname'])
        self.assertEquals('secret', self.login.input_params['password'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestOGPLogin))
    return suite

"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$

"""