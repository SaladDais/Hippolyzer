from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region

from pyogp.lib.base.interfaces import IPlaceAvatarAdapter

import getpass, sys
from optparse import OptionParser


class ExampleLogin(object):
    
    def login(self):
        parser = OptionParser()

        parser.add_option("-a", "--agentdomain", dest="loginuri", default="https://login1.aditi.lindenlab.com/cgi-bin/auth.cgi",
                          help="URI of Agent Domain")
        parser.add_option("-r", "--region", dest="regionuri", default="http://sim1.vaak.lindenlab.com:13000",
                          help="URI of Region to connect to")

        (options, args) = parser.parse_args()

        firstname = args[0]
        lastname = args[1]
        password = getpass.getpass()

        credentials = PlainPasswordCredential(firstname, lastname, password)

        agentdomain = AgentDomain(options.loginuri)
        agent = agentdomain.login(credentials)

        print "logged in, we now have an agent: ", agent

        place = IPlaceAvatarAdapter(agent)
        region = Region(options.regionuri)

        print "now we try to place the avatar on a region"
        avatar = place(region)

        #avatar.establish_presence()
        # 
def main():
    return ExampleLogin().login()    

if __name__=="__main__":
    main()
