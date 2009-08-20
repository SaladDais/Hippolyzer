
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
import uuid
import struct
import math

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

            if type(X) != float: 
                self.X = float(X)
            else:
                self.X = X
            if type(Y) != float:
                self.Y = float(Y)
            else:
                self.Y = Y
            if type(Z) != float:
                self.Z = float(Z)
            else:
                self.Z = Z

    def unpack_from_bytes(self, bytes, offset):
        """ unpack floats from binary """

        # unpack from binary as Little Endian
        self.X = struct.unpack("<f", bytes[offset:offset+4])[0]
        self.Y = struct.unpack("<f", bytes[offset+4:offset+8])[0]
        self.Z = struct.unpack("<f", bytes[offset+8:offset+12])[0]

    def get_bytes(self):
        """ get bytes """

        return struct.pack("<3f", self.X, self.Y, self.Z)

    def data(self):

        return ((self.X, self.Y, self.Z))

    def copy(self):
        return Vector3( X = self.X, Y = self.Y, Z = self.Z )

    def __repr__(self):
        """ represent a vector as a string """

        return str((self.X, self.Y, self.Z))

    def __call__(self):
        """ represent a vector as a tuple """

        return ((self.X, self.Y, self.Z))

    def dist_squared(a, b):
        x = a.X - b.X
        y = a.Y - b.Y
        z = a.Z - b.Z
        return x*x + y*y + z*z
    dist_squared = staticmethod(dist_squared)
    

class Quaternion(object):
    """ represents a quaternion as a tuple"""

    def __init__(self, bytes = None, offset = 0, length = 4, X = 0.0, Y = 0.0, Z = 0.0, W = 0.0):

        if bytes != None:

            self.unpack_from_bytes(bytes, offset, length)

        else:

            if type(X) != float:
                self.X = float(X)
            else:
                self.X = X
            if type(Y) != float:
                self.Y = float(Y)
            else:
                self.Y = Y            
            if type(Z) != float: 
                self.Z = float(Z)
            else:
                self.Z = Z
            if type(W) != float: 
                self.W = float(W)
            else:
                self.W = W

    def unpack_from_bytes(self, bytes, offset, length=4):
        """ unpack floats from binary """

        # unpack from binary as Little Endian
        self.X = struct.unpack("<f", bytes[offset:offset+4])[0]
        self.Y = struct.unpack("<f", bytes[offset+4:offset+8])[0]
        self.Z = struct.unpack("<f", bytes[offset+8:offset+12])[0]

        if length == 4:
            self.W = struct.unpack("<f", bytes[offset+12:offset+16])[0]

        else:
            # Unpack from vector3 
            t = 1.0 - (self.X*self.X + self.Y*self.Y + self.Z*self.Z)
            if t > 0:
                self.W = math.sqrt(t)
            else:
                # Avoid sqrt(-episilon)
                self.W = 0           

    def get_bytes(self):
        """ get bytes """

        return struct.pack("<4f", self.X, self.Y, self.Z, self.W)

    def data(self):

        return ((self.X, self.Y, self.Z, self.W))

    def copy(self):
        return Quaternion(X=self.X, Y=self.Y, Z=self.Z, W=self.W)

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

    def __init__(self, string = '00000000-0000-0000-0000-000000000000', bytes = None, offset = 0):

        if bytes != None:

            self.unpack_from_bytes(bytes, offset)

        else:

            self.uuid = uuid.UUID(string)

    def random(self):

        if str(self.uuid) == '00000000-0000-0000-0000-000000000000':
            self.uuid = uuid.uuid4()
            return self.uuid

        else:
            log(WARNING, "Attempted to overwrite a stored uuid %s with a random, that is a bad idea..." % (str(self.uuid)))

    def unpack_from_bytes(self, bytes, offset):
        """ unpack uuid from binary """

        # unpack from binary
        self.uuid = uuid.UUID(bytes = bytes[offset:offset+16])

    def get_bytes(self):
        """ get bytes """

        return str(self.uuid.bytes)

    def data(self):
        """ represent a uuid as, well, a uuid """

        return self.uuid

    def copy(self):
        return UUID(string=str(self.uuid))

    def __repr__(self):
        """ represent a uuid as a string """

        return str(self.uuid)

    def __call__(self):
        """ represent a uuid as, well, a uuid """

        return self.uuid


    def __eq__(self, other):
        if hasattr(other,'uuid'):
            return self.uuid == other.uuid
        else:
            return False
    

    def __xor__(self, arg):
        """ the xor of two UUIDs """
        temp = self.uuid.int ^ arg.uuid.int
        result = uuid.UUID(int = temp)
        return UUID(result.__str__())
        



