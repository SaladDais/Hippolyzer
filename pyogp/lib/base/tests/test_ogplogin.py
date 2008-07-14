import unittest, doctest
from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region

from pyogp.lib.base.interfaces import IPlaceAvatarAdapter

from pyogp.lib.base.OGPLogin import OGPLogin

class TestOGPLogin(unittest.TestCase):
    def test_login(self):
        credentials = PlainPasswordCredential('firstname', 'lastname', 'password')
        #create a login, giving it the credentials, the loginuri, and the regionuri
        ogpLogin = OGPLogin(credentials, 'https://login1.aditi.lindenlab.com/cgi-bin/auth.cgi', 'http://sim1.vaak.lindenlab.com:13000')

        #gets seedcap, and an agent that can be placed in a region
        agentdomain, agent = ogpLogin.loginToAgentD()
        assert agentdomain.seed_cap != None or agentdomain.seed_cap != {}, "Login to agent domain failed"

        #attempts to place the agent in a region
        avatar = ogpLogin.placeAvatarCap()
        assert avatar['connect'] == True, "Place avatar failed"
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestOGPLogin))
    return suite
