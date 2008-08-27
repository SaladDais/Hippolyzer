"""
High level API
"""

from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region

from pyogp.lib.base.interfaces import IPlaceAvatar

### login methods
def login_with_plainpassword(agentdomain_url, firstname, lastname, password):
    """logs an agent into the agent domain and returns an agent handle
    
    takes firstname, lastname and plain password and returns an agent object
    
    Using it is simple:
    >>> agent = login_with_plainpassword("http://localhost:12345/","Firstname","Lastname","secret")
    
    Now this agent should contain an agentdomain object
    >>> agent.agentdomain
    <pyogp.lib.base.agentdomain.AgentDomain object at ...>
    
    And this again a seed capability:
    >>> agent.agentdomain.seed_cap
    <SeedCapability for http://127.0.0.1:12345/seed_cap>
    
    """

    credentials = PlainPasswordCredential(firstname, lastname, password)
    agentdomain = AgentDomain(agentdomain_url)
    agent = agentdomain.login(credentials)
    return agent
    

### place avatar
def place_avatar(agent, region_url):
    """place an avatar on a region
    
    Placing an avatar is simple. We just need an agent object and a region url.

    We get an agent object via the login:
    >>> agent = login_with_plainpassword("http://localhost:12345/","Firstname","Lastname","secret")
    
    And now we can call it:
    >>> avatar = place_avatar(agent, "http://localhost:12345/region")
    
    The avatar should now contain the region:
    >>> avatar.region
    <pyogp.lib.base.regiondomain.Region object at ...>
    
    and this in turn the region details:
    >>> avatar.region.details
    {'sim_port': 12345, 'seed_capability': '/region_seed_cap', 'sim_ip': '127.0.0.1'}
    
    """    
    place = IPlaceAvatar(agent.agentdomain)
    region = Region(region_url)
    avatar = place(region)
    
    return avatar
    
def run_loop(avatar):
    """run the UDP loop for the avatar
    
    First we create one as seen above:
    >>> agent = login_with_plainpassword("http://localhost:12345/","Firstname","Lastname","secret")
    >>> avatar = place_avatar(agent, "http://localhost:12345/region")

    And now we can run the loop:
    >>> run_loop(avatar)
    
    
    """
    
    
