#!/usr/bin/python
"""
@file ogplogin.py
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
$/LicenseInf
"""

from urlparse import urlparse
import xmlrpclib
import httplib, urllib2
import os.path

from indra.base import llsd

from pyogp.lib.agent import Agent
from pyogp.lib.capabilities import Capabilities
from pyogp.client.login import Login

class LegacyLogin(Login):

    def onLogin(self):
        """ logs in an agent to the ogp agent domain """
        
        pass
    
    def legacyLogin(self, llsdloginparams, headers):
        """ handles post to Second Life's legacy login uri  """

        pass

