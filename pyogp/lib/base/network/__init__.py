
from stdlib_client import StdLibClient
from mockup_client import MockupClient
from mockup_net import MockupUDPClient

from interfaces import IRESTClient, IUDPClient

from exc import HTTPError

from zope.component import provideUtility
provideUtility(StdLibClient(), IRESTClient)
provideUtility(MockupUDPClient(), IUDPClient)
