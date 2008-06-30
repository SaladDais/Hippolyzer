#!/usr/bin/python
"""
@file test.py
@author Linden Lab
@date 2008-06-13
@brief Iniitializes path directories

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
$/LicenseInfo$
"""

# intend to build suites out of each of the subdirs, and to execute the suites...
# this is just getting started, as is a lot of the rest....

import unittest
import sys
import os

suites = []
# grab path and import all tests
for root, dirs, files in os.walk(os.getcwd):
    
    sys.path.append(dir)
    
    suites.append[dir]
    
    for file in files:
        import file


# todo: um, make a test framework?

if __name__ = '__main__':
    unittest.main()
