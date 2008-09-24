"""
@file settings.py
@date 2008-09-22
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

class Settings():
    
    # parameters for xmplrpc login
    def get_default_xmlrpc_login_parameters(self):
        """ returns some default login params """
    
        params = {   
            'major': '1',
            'minor': '20',
            'patch': '15',
            'build': '3',
            'platform': 'Win',
            'options': [],
            'user-agent': 'pyogp 0.1',
            'id0': '',
            'viewer_digest': '09d93740-8f37-c418-fbf2-2a78c7b0d1ea',
            'version': 'pyogp 0.1',
            'channel': 'pyogp',
            'mac': '',
            'agree_to_tos': True,
            'read_critical': True
        }
    
        return params