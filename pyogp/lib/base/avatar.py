"""
@file avatar.py
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


class Avatar(object):
    """an avatar - the agent representation in 3D on a region"""
    
    def __init__(self, region):
        """initialize the avatar with the actual region we are on
        
        we need to instantiate the avatar after place_avatar
        """
        self.region = region