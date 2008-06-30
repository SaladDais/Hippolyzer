#!/usr/bin/python
"""
@file login.py
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

from urlparse import urlparse
import xmlrpclib
import httplib, urllib2
import os.path

if os.path.exists("../../../setup_path.py"):
	execfile("../../../setup_path.py")

from indra.base import llsd

from pyogp.lib.agent import Agent
from pyogp.lib.capabilities import Capabilities

class Login():

    def  __init__(self, agent=None):
        """ initialize base login class """
        
        self.agent = agent
        self.loginstatus = False
        self.loginparams = {}
        self.loginuri = ''

    def login(self):
        """ common api for logging in an agent to a grid  """

        self.loginparams = self.agent.getLoginParams()
        
        self.loginuri = self.agent.loginuri

        seedcap = self.onLogin()

        """urlbits = urlparse(self.agent.loginuri) 
        # support agent domain login and legacy login
        
        if (urlbits.path == '/cgi-bin/auth.cgi'):
            seedcap = self.ogpLogin()
        elif (urlbits.path == '/cgi-bin/login.cgi'):
            seedcap = self.legacyLogin()
        """
        
        return seedcap

    def onLogin(self):
        """ Just the abstract method that will do all the login work. To be derived. """

        pass
         
    def loginStatus(self):
        """ returns login status of agent """

        return self.loginstatus

    def updateLoginStatus(self, status):
        """ toggle the loginstatus var value  """

        self.loginstatus = status
