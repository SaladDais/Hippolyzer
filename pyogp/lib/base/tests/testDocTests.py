import unittest
import doctest

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS

# setup functions

def setUp(self):
    from pyogp.lib.base.registration import init
    init()
    
def tearDown(self):
    pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
            doctest.DocFileSuite(
                "login.txt",
                "caps.txt",
                package="pyogp.lib.base.tests",
                setUp = setUp,
                tearDown = tearDown,
                optionflags=optionflags,
                )
            )
    suite.addTest(doctest.DocTestSuite('pyogp.lib.base.caps', optionflags=optionflags))
    suite.addTest(doctest.DocTestSuite('pyogp.lib.base.credentials', optionflags=optionflags))
    suite.addTest(doctest.DocTestSuite('pyogp.lib.base.api', optionflags=optionflags))
    
    
    return suite
