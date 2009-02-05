"""
@file agent.py
@date 2008-09-16
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
import re
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

from credentials import PlainPasswordCredential
from legacy_login import LegacyLogin
from regiondomain import Region

logger = getLogger('pyogp.lib.base.agent')
log = logger.log

class Agent(object):
    """ an OGP agent """

    def __init__(self):
        """ initialize this agent """

        self.login_uri = None
        self.region_uri = None # this should move out, supports login
        self.regionname = None # this should move out, supports login

        self.firstname = None
        self.lastname = None
        self.password = None
        self.credentials = None

        #these maybe don't belong here
        self.agentdomain = None
        self.regions = []     # all known regions
        self.region = None    # the host simulation for the agent

        log(DEBUG, 'initializing agent: %s' %self)

    def setCredentials(self, firstname, lastname, password):
        """ establish the agent's identifying attributes """

        # todo: accomodate md5password
        self.firstname = firstname
        self.lastname = lastname
        self.password = password

        self.credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)

    def login(self, login_uri, region_uri=None, firstname=None, lastname=None, password=None, restclient=None, regionname=None):
        """ login to a login endpoint. this should move to a login class in time """

        if (firstname != None):
            self.firstname = firstname

        if (lastname != None):
            self.lastname = lastname

        if (password != None):
            self.password = password

        if (regionname != None):
            self.regionname = regionname

        if (self.credentials == None):
            self.setCredentials(self.firstname, self.lastname, self.password)

        #todo: accomodate both legacy login and OGP login, for now OGP only
        if (re.search('auth.cgi$', login_uri)):

            log(INFO, "Login context is OGP")

            from agentdomain import AgentDomain

            self.agentdomain = AgentDomain(login_uri, restclient)
            self.agentdomain.login(self.credentials)

            self.region = Region(region_uri)
            self.region.details = self.agentdomain.place_avatar(self.region.region_uri)
            self.region.set_seed_cap_url(self.region.details['region_seed_capability'])
        else:
            self.thingy = LegacyLogin(login_uri)

            login_params = PlainPasswordCredential(self.firstname, self.lastname, self.password).get_xmlrpc_login_params()
            if (self.regionname != None): 
                login_params['start'] = self.regionname
            else:
                login_params['start'] = "last"

            self.region = Region(regionname = self.region)
            self.region.details = self.thingy.login(login_params, self.region)

        
