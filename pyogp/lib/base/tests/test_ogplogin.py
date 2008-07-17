import unittest, doctest
from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region

from pyogp.lib.base.interfaces import IPlaceAvatarAdapter

from pyogp.lib.base.OGPLogin import OGPLogin

class testAuthOGPLogin(unittest.TestCase):
    auth_uri = None
    region_uri = None

    def setUp(self):
        auth_uri = 'https://login1.aditi.lindenlab.com/cgi-bin/auth.cgi'
        region_uri = 'http://sim1.vaak.lindenlab.com:13000'

    def tearDown(self):
        # essentially logout by deleting presence... etc.
        
    def test_base(self):
        credentials = PlainPasswordCredential('firstname', 'lastname', 'password')
        ogpLogin = OGPLogin(credentials, auth_uri, region_uri)

        #gets seedcap, and an agent that can be placed in a region
        agentdomain, agent = ogpLogin.loginToAgentD()
        assert agentdomain.seed_cap != None or agentdomain.seed_cap != {}, "Login to agent domain failed"

        #attempts to place the agent in a region
        avatar = ogpLogin.placeAvatarCap()
        assert avatar['connect'] == True, "Place avatar failed"

    def test_banned(self):
        credentials = PlainPasswordCredential('BannedTester', 'Tester', 'banned_password')
        ogpLogin = OGPLogin(credentials, auth_uri, region_uri)

        #gets seedcap, and an agent that can be placed in a region
        try:
            agentdomain, agent = ogpLogin.loginToAgentD()
            assert False, "Login to banned account should fail"
        except Exception, e:
            pass
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testBaseOGPLogin))
    return suite
