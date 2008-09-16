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
        


