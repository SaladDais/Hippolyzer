"""
@file __init__.py
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


from stdlib_client import StdLibClient
from mockup_client import MockupClient
from mockup_net import MockupUDPClient

from interfaces import IRESTClient, IUDPClient

from exc import HTTPError

from zope.component import provideUtility
provideUtility(StdLibClient(), IRESTClient)
provideUtility(MockupUDPClient(), IUDPClient)
