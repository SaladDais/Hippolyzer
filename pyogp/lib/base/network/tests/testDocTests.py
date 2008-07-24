import unittest
import doctest

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS

# setup functions

def setUp(self):
    # override the default
    from pyogp.lib.base.network import IRESTClient, MockupClient
    from zope.component import provideUtility
    from pyogp.lib.base.tests.base import AgentDomain
    provideUtility(MockupClient(AgentDomain()), IRESTClient)
    
def tearDown(self):
    print "down"

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
            doctest.DocFileSuite("basics.txt",
                package="pyogp.lib.base.network.tests",
                setUp = setUp,
                tearDown = tearDown,  
                )
            )
    return suite
