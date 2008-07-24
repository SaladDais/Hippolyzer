from zope.interface import implements
from zope.component import adapts

from interfaces import IAgent

import grokcore.component as grok

class Agent(object):
    """an OGP agent"""
    
    implements(IAgent)
    
    def __init__(self, agentdomain):
        """initialize this agent"""
        self.agentdomain = agentdomain
        


