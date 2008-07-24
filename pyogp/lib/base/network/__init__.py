
from stdlib_client import StdLibClient
from mockup_client import MockupClient

from interfaces import IRESTClient

from exc import HTTPError

from zope.component import provideUtility
provideUtility(StdLibClient(), IRESTClient)
