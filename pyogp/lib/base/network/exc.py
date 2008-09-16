"""
@file exc.py
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


class HTTPError(Exception):
    """an HTTP error"""
    
    def __init__(self, code, msg, fp, details=""):
        """initialize this exception"""
        self.code = code
        self.msg = msg
        self.details = details
        self.fp = fp
        
    def __str__(self):
        """return a string representation"""
        return "%s %s" %(self.code, self.msg)
    
