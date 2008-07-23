from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region

from pyogp.lib.base.interfaces import IPlaceAvatar

import getpass, sys
from optparse import OptionParser

import pprint

class OGPLogin(object):
    """ This class can be used to log in to an agent domain and start communicating with a region domain """

    def __init__(self, credents, loginuri, regionuri):
        self.credentials = credents #PlainPasswordCredential(credents.firstname, credents.lastname, credents.password)
        self.loginuri = loginuri
        self.regionuri = regionuri
    
    def login(self):

        print "login to the agent domain: " + self.loginuri
        agentd, agent = self.loginToAgentD()
        print "logged in, we now have an agent: ", agent
        print "and a domain: ", agentd

        print "now we try to place the avatar on a region"
        avatar = self.placeAvatarCap()
        print "placed avatar cap, got back: ", avatar

        #avatar.establish_presence()

    def loginToAgentD(self):
        """ Logs into the agent domain, getting the agentd seed cap """
        self.agentdomain = AgentDomain(self.loginuri)
        self.agent = self.agentdomain.login(self.credentials)
        return self.agentdomain, self.agent
    
    def getCapabilities(self, seed_cap, caps):
        """ This is the method that SHOULD be used (but isn't) to get capabilities from the seedcap """
        pass

    def placeAvatarCap(self):
        """ actually gets the place_avatar cap and posts to it """
        region = Region(self.regionuri)
        place = IPlaceAvatar(self.agent)
        self.avatar = place(region)
        return self.avatar
        
def main():
    parser = OptionParser()

    parser.add_option("-a", "--agentdomain", dest="loginuri", default="https://login1.aditi.lindenlab.com/cgi-bin/auth.cgi",
                      help="URI of Agent Domain")
    parser.add_option("-r", "--region", dest="regionuri", default="http://sim1.vaak.lindenlab.com:13000",
                      help="URI of Region to connect to")

    (options, args) = parser.parse_args()

    options.firstname = args[0]
    options.lastname = args[1]
    options.password = getpass.getpass()
    
    pprint.pprint(options)
    credents = PlainPasswordCredential(options.firstname, options.lastname, options.password)
    
    return OGPLogin(credents, options.loginuri, options.regionuri).login()    

if __name__=="__main__":
    main()
