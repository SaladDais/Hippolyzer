
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

import unittest
import doctest

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS

# setup functions

def setUp(self):
    pass

def tearDown(self):
    pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
            doctest.DocFileSuite(
                "agent.txt",
                "login.txt",
                "caps.txt",
                "message_handler.txt",
                package="pyogp.lib.base.tests",
                setUp = setUp,
                tearDown = tearDown,
                optionflags=optionflags,
                )
            )
    #suite.addTest(doctest.DocTestSuite('pyogp.lib.base.caps', optionflags=optionflags))
    suite.addTest(doctest.DocTestSuite('pyogp.lib.base.utilities.helpers', optionflags=optionflags))
    #suite.addTest(doctest.DocTestSuite('pyogp.lib.base.api', optionflags=optionflags))


    return suite


