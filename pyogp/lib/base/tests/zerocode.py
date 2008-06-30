#!/usr/bin/python
"""
@file zerocode.py
@author Lawson English
@date 2008-06-13
@brief Iniitializes path directories

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
$/LicenseInfo$
"""

# From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/510399
# From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/510399
def ByteToHex( byteStr ):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """
 
    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #   
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()        
 
    return ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()
 
 
def HexToByte( hexStr ):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    """
    # The list comprehension implementation is fractionally slower in this case    
    #
    #    hexStr = ''.join( hexStr.split(" ") )
    #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
    #                                   for i in range(0, len( hexStr ), 2) ] )
 
    bytes = []
 
    hexStr = ''.join( hexStr.split(" ") )
 
    for i in range(0, len(hexStr), 2):
        bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )
 
    return ''.join( bytes )
 
 
def zero_encode(inputbuf):
    newstring =""
    zero = False
    zero_count = 0            
    for c in inputbuf:
        if c != '\0':
            if zero_count != 0:
                newstring = newstring + chr(zero_count)
                zero_count = 0
                zero = False
 
            newstring = newstring + c
 
        else:
            if zero == False:
                newstring = newstring + c
                zero = True
 
            zero_count = zero_count + 1
    if zero_count != 0:
        newstring = newstring + chr(zero_count)
 
 
    return newstring
 
def zero_decode(inputbuf):
    newstring =""
    in_zero = False
    for c in inputbuf:
        if c != '\0':
            if in_zero == True:
                zero_count = ord(c)
                zero_count = zero_count -1
                while zero_count>0:
 
                    newstring = newstring + '\0'
                    zero_count = zero_count -1
                in_zero = False
            else:
                newstring = newstring + c
        else:
            newstring = newstring + c
            in_zero = True
    return newstring
 
def zero_decode_ID(inputbuf):
    newstring =""
    in_zero = False
    #print "in encode, input is", ByteToHex(inputbuf)
    for c in inputbuf:
        if c != '\0':
            if in_zero == True:
                zero_count = ord(c)
                zero_count = zero_count -1
                while zero_count>0:
 
                    newstring = newstring + '\0'
                    zero_count = zero_count -1
                in_zero = False
            else:
                newstring = newstring + c
        else:
            newstring = newstring + c
            in_zero = True
    return newstring[:4]
