"""
@file datatypes.py
@date 2009-03-18
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

# standard python libs
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import uuid
import struct

# pyogp
from pyogp.lib.base.exc import DataParsingError

# pyogp messaging

# initialize logging
logger = getLogger('pyogp.lib.base.datatypes')
log = logger.log

class Vector3(object):
    """ represents a vector as a tuple"""

    def __init__(self, bytes = None, offset = 0, X = 0.0, Y = 0.0, Z = 0.0):

        if bytes != None:

            self.unpack_from_bytes(bytes, offset)

        else:

            self.X = X
            self.Y = Y
            self.Z = Z

    def unpack_from_bytes(self, bytes, offset):
        """ unpack floats from binary """

        # unpack from binary as Little Endian
        self.X = struct.unpack("<f", bytes[offset:offset+4])[0]
        self.Y = struct.unpack("<f", bytes[offset+4:offset+8])[0]
        self.Z = struct.unpack("<f", bytes[offset+8:offset+12])[0]

    def data(self):

        return ((self.X, self.Y, self.Z))

    def __repr__(self):
        """ represent a vector as a string """

        return str((self.X, self.Y, self.Z))

    def __call__(self):
        """ represent a vector as a tuple """

        return ((self.X, self.Y, self.Z))

class Quaternion(object):
    """ represents a quaternion as a tuple"""

    def __init__(self, bytes = None, offset = 0, X = 0.0, Y = 0.0, Z = 0.0, W = 0.0):

        if bytes != None:

            self.unpack_from_bytes(bytes, offset)

        else:

            self.X = X
            self.Y = Y
            self.Z = Z
            self.W = W

    def unpack_from_bytes(self, bytes, offset):
        """ unpack floats from binary """

        # unpack from binary as Little Endian
        self.X = struct.unpack("<f", bytes[offset:offset+4])[0]
        self.Y = struct.unpack("<f", bytes[offset+4:offset+8])[0]
        self.Z = struct.unpack("<f", bytes[offset+8:offset+12])[0]
        self.W = struct.unpack("<f", bytes[offset+12:offset+16])[0]


    def data(self):

        return ((self.X, self.Y, self.Z, self.W))

    def __repr__(self):
        """ represent a quaternion as a string """

        return str((self.X, self.Y, self.Z, self.W))

    def __call__(self):
        """ represent a quaternion as a tuple """

        return ((self.X, self.Y, self.Z, self.W))

class UUID(object):
    """ represents a uuid as, well, a uuid 

    inbound LLUUID data from packets is already UUID(), they are 
    already the same 'datatype'
    """

    def __init__(self, bytes = None, offset = 0, string = '00000000-0000-0000-0000-000000000000'):

        if bytes != None:

            self.unpack_from_bytes(bytes, offset)

        else:

            self.uuid = uuid.UUID(string)

    def unpack_from_bytes(self, bytes, offset):
        """ unpack uuid from binary """

        # unpack from binary
        self.uuid = uuid.UUID(bytes = bytes[offset:offset+16])

    def data(self):
        """ represent a uuid as, well, a uuid """

        return self.uuid

    def __repr__(self):
        """ represent a uuid as a string """

        return str(self.uuid)

    def __call__(self):
        """ represent a uuid as, well, a uuid """

        return self.uuid

