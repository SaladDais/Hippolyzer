import unittest
import doctest

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS

# setup functions

def setUp(self):
    from pyogp.lib.base.registration import init
    init()
    print "ok"
    
def tearDown(self):
    print "down"

def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite("login.txt",
                package="pyogp.lib.base.tests",
                setUp = setUp,
                tearDown = tearDown,
                
                )
            ))