#!/usr/bin/python
"""
@file makepacketdict.py
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

import re

def makereversepacketdict():
    rev_dict = {}
    for line in open("../../linden/scripts/messages/message_template.msg", ).xreadlines():
        results = re.match("^\t([^\t{}]+.+)",line)
        if results:
            aline = results.group(1)
            aline = aline.split()
            if aline[1] == "Fixed": 
                rev_dict[aline[0]] = (aline[1],int("0x"+aline[2][8:],16))
                
            else:
                rev_dict[aline[0]] = (aline[1],int(aline[2]))

    return rev_dict

def makepacketdict():
    dict = {}
    for line in open("../../linden/scripts/messages/message_template.msg", ).xreadlines():
        results = re.match("^\t([^\t{}]+.+)",line)
        if results:
            aline = results.group(1)
            aline = aline.split()
            if aline[1] == "Fixed": 
                dict[(aline[1],int("0x"+aline[2][8:],16))] = (aline[0],aline[3], aline[4])
                
            else:
                dict[(aline[1],int(aline[2]))] = (aline[0],aline[3], aline[4])

    return dict
