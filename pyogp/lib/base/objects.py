"""
@file object.py
@date 2009-03-03
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

# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

# related

# pyogp

# initialize logging
logger = getLogger('pyogp.lib.base.inventory')
log = logger.log

class Objects(object):
    """ is an Object Manager 

    Initialize the event queue client class
    >>> objects = Objects()

    Sample implementations: region.py
    Tests: tests/test_objects.py
    """

    def __init__(self, agent = None):
        """ set up the inventory manager """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

class Object(object):
    """ represents an Inventory item 

    Initialize the event queue client class
    >>> inventoryitem = InventoryItem()

    Sample implementations: inventory.py
    Tests: tests/test_inventory.py
    """

    def __init__(self):
        """ set up the event queue attributes """

        pass