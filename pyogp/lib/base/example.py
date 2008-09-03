from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region
from pyogp.lib.base import registration

from pyogp.lib.base.interfaces import IPlaceAvatar, IEventQueueGet

import getpass, sys, logging
from optparse import OptionParser



def login():
    """login an agent and place it on a region"""    
    registration.init()
    parser = OptionParser()
    
    logger = logging.getLogger("pyogp.lib.base.example")

    parser.add_option("-a", "--agentdomain", dest="loginuri", default="https://login1.aditi.lindenlab.com/cgi-bin/auth.cgi",
                      help="URI of Agent Domain")
    parser.add_option("-r", "--region", dest="regionuri", default="http://sim1.vaak.lindenlab.com:13000",
                      help="URI of Region to connect to")
    parser.add_option("-q", "--quiet", dest="verbose", default=True, action="store_false",
                    help="enable verbose mode")
                      

    (options, args) = parser.parse_args()
    
    if options.verbose:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG) # seems to be a no op, set it for the logger
        formatter = logging.Formatter('%(name)-30s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        # setting the level for the handler above seems to be a no-op
        # it needs to be set for the logger, here the root logger
        # otherwise it is NOTSET(=0) which means to log nothing.
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        print "Attention: This script will print nothing if you use -q. So it might be boring to use it like that ;-)"

    firstname = args[0]
    lastname = args[1]
    password = getpass.getpass()

    credentials = PlainPasswordCredential(firstname, lastname, password)

    agentdomain = AgentDomain(options.loginuri)
    agent = agentdomain.login(credentials)

    logger.info("logged in, we now have an agent: %s" %agent)

    place = IPlaceAvatar(agentdomain)
    region = Region(options.regionuri)

    
    logger.info("now we try to place the avatar on a region")
    avatar = place(region)
    logger.info("got region details: %s", avatar.region.details)
    
    # now get an event_queue_get cap
    eqg = IEventQueueGet(agentdomain)
    logger.info("received an event queue cap: %s", eqg.cap)

    for i in range(1,4):
        logger.info("calling EQG cap")
        result = eqg()
        logger.info("it returned: %s", result)

def main():
    return login()    

if __name__=="__main__":
    main()
