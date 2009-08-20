
"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""

# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

# pyogp

# pyogp messaging

# initialize logging
logger = getLogger('pyogp.lib.base.permissions')
log = logger.log

class PermissionsMask(object):
    """ permissions flags mappings """

    # the types of permissions
    Transfer = 1 << 13     # 0x00002000
    Modify = 1 << 14       # 0x00004000
    Copy = 1 << 15         # 0x00008000
    Move = 1 << 19         # 0x00080000
    _None = 0              # 0x00000000
    All = 0x7FFFFFFF
    # Reserved
    #Unrestricted = Modify | Copy | Transfer

class PermissionsTarget(object):
    """ who the permissions apply to """

    Base = 0x01
    Owner = 0x02
    Group = 0x04
    Everyone = 0x08
    NextOwner = 0x10

class Permissions(object):
    """ class representing the permissions of an object or inventory item """

    def __init__(self, BaseMask = None, OwnerMask = None, GroupMask = None, EveryoneMask = None, NextOwnerMask = None):
        """ store the values of the various targets permissions """

        self.BaseMask = BaseMask
        self.OwnerMask = OwnerMask
        self.GroupMask = GroupMask
        self.EveryoneMask = EveryoneMask
        self.NextOwnerMask = NextOwnerMask



