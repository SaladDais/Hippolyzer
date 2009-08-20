
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

# standard python modules
import unittest

#related

# pyogp
from pyogp.lib.base.parcel import *
from pyogp.lib.base.settings import Settings

# pyogp tests
import pyogp.lib.base.tests.config 

class TestParcels(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):

        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestParcels))
    return suite

