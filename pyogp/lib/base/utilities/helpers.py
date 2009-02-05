"""
@file helpers.py
@date 2009-02-05
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

class Helpers():
    """ contains useful helper functions """

    def bytes_to_hex(self, data):
        """ converts bytes to hex format """

        #from binascii import hexlify
        #return hex_string
        #hex_string = hexlify(data)
        return ''.join(["%02X " % ord(x) for x in data]).strip()

    def bytes_to_ascii(self, data):
        " converts bytes to ascii format "

        from binascii import b2a_uu

        ascii_string = b2a_uu(data)

        return ascii_string

    def bytes_to_base64(self, data):
        " converts bytes to ascii format "

        from binascii import b2a_base64

        base64_string = b2a_base64(data)

        return base64_string