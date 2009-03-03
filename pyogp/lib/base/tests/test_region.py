"""
@file test_region.py
@date 2009-2-20
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

# standard python libs
import unittest

# pyogp
from pyogp.lib.base.exc import *

# pyogp tests
import pyogp.lib.base.tests.config 

class TestRegion(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):

        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRegion))
    return suite
