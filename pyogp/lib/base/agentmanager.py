"""
@file agent_manager.py
@date 2009-03-26
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

# standard python libraries
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import signal
import sys

# related
from eventlet import api

# pyogp
from pyogp.lib.base.datatypes import *
from pyogp.lib.base.utilities.helpers import Wait

# initialize logging
logger = getLogger('pyogp.lib.base.agentmanager')
log = logger.log

class AgentManager(object):
    """ a simple class to track multiple agents
    
    This class can perhaps begin to manage sessions in time.
    """

    def __init__(self):

        # store the agents in a dictionary keyed by a uuid
        # this could be agent_id, if we know it ahead of time
        # or, create a new one
        self.agents = {}

        # signal handler to capture erm signals
        self.signal_handler = signal.signal(signal.SIGINT, self.sigint_handler)

    def initialize(self, agents):
        """ accept a list of Agent() instances, and store them in the agents attribute """

        if type(agents) != list:
            log(WARNING, "The AgentManager requires a list of Agent instances to initialize. Stopping.")
            return False

        for agent in agents:

            self.store_agent(agent)

    def store_agent(self, agent):
        """ adds an agent to the store """

        if str(type(agent)) != '<class \'pyogp.lib.base.agent.Agent\'>':
            log(WARNING, "The AgentManager stores only Agent instances to initialize. Stopping.")
            return False

        # check if the agent is on the store
        if self._is_stored(agent) == False:

            if agent.agent_id == None:
                key = UUID().random()
            else:
                key = agent.agent_id

            self.agents[key] = agent

            log(INFO, "Stored agent %s with a key of %s" % (agent.name, key))

        else: 

            if agent.firstname != None and agent.lastname != None:
                uniq = ' named ' + agent.Name()

            log(WARNING, "The AgentManager is already storing an agent%s. Stopping." % (uniq))

    def _is_stored(self, agent):
        """ returns True if an agent is already stored, False if not """

        if agent.Name() in self._stored_names():
            return True
        elif agent.agent_id in self._stored_agent_ids():
            return True
        else:
            return False

    def _stored_names(self):
        """ returns the stored agent's names in a list """

        names = []

        for key in self.agents:
            names.append(self.agents[key].Name())

        return names

    def _stored_agent_ids(self):
        """ returns the stored agent's names in a list """

        ids = []

        for key in self.agents:
            if self.agents[key].agent_id != None:
                ids.append(self.agents[key].agent_id)

        return ids

    def login(self, key, loginuri, start_location):
        """ spawns a new agent via an eventlet coroutine """

        api.spawn(self.agents[key].login, loginuri = loginuri, start_location = start_location)

    def has_agents_running(self):
        """ returns true if there is a client who's running value = True """

        for key in self.agents:
            if self.agents[key].running:
                return True

        return False

    def get_active_agents(self):
        """ returns a list of agents that are connected to a grid """

        active = []

        for key in self.agents:
            active.append(self.agents[key])

        return active

    def sigint_handler(self, signal, frame):

        log(INFO, "Caught signal... %d. Stopping" % signal)

        for agent in self.get_active_agents():
            agent.logout()

        Wait(10)

        if self.has_agents_running():
            log(WARNING, "These agents have not yet shut down. Killing the process hard.\n\t\t%s" % (self.get_active_agents()))
            sys.exit(1)