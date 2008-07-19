import unittest
import doctest

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS

# setup functions

def setUp(self):
    print "ok"
    
def tearDown(self):
    print "down"

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
            doctest.DocFileSuite("login.txt","caps.txt",
                package="pyogp.lib.base.tests",
                setUp = setUp,
                tearDown = tearDown,  
                )
            )
    suite.addTest(doctest.DocTestSuite('pyogp.lib.base.caps', optionflags=optionflags))
    suite.addTest(doctest.DocTestSuite('pyogp.lib.base.credentials', optionflags=optionflags))
    
    return suite
