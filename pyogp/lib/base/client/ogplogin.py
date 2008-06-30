#!/usr/bin/python
"""
@file ogplogin.py
@author Linden Lab
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
$/LicenseInf
"""

import sys, struct
import socket
from urlparse import urlparse
import xmlrpclib
import httplib, urllib2
import os.path
import pprint

# linden provided libs
from indra.base import llsd
from indra.ipc import llsdhttp
from indra.base import lluuid

# lib classes
from pyogp.lib.agent import Agent
from pyogp.lib.capabilities import Capabilities
from pyogp.client.login import Login

# defaults for the purpose of this test script
debug = True

class OGPLogin(Login):

    def onLogin(self):
        """ logs in an agent to the ogp agent domain """

        # todo: work with password or md5pass
        loginparams={#'type'       : 'agent',
                    'password'  : self.loginparams['password'],   # md5-password '$1$' + md5hash
                    'lastname'  : self.loginparams['lastname'],
                    'firstname' : self.loginparams['firstname'],
        }
        
        # format the llsd to post to the loginuri
        llsdloginparams = llsd.format_xml(loginparams)

        # define the header for the post
        headers = {"Content-type" : "application/llsd+xml"}

        seedcap  = self.postOGPLogin(llsdloginparams, headers)

        if seedcap == None:
            print 'Login failed!'
            return None
        
        if debug:
            print 'Login complete, agent_seed_cap is: ' + seedcap

        # is this where we update loginstatus var? we are authenticated, i'm going to say yes
        self.updateLoginStatus(True)

        capabilities = Capabilities(self.agent, 30)

        capabilities.appendCap('agent_seed_cap', seedcap)
        
        if debug:
            print 'Logged in status = ' + str(self.loginStatus()) 
            print capabilities.printCaps()

        # post to seed cap a req for place avatar
        headers = {"Content-type" : "application/llsd+xml"}
        data = {'TESTINGPOST': None, 'caps':{'place_avatar':True, 'event_queue': True, 'rez_avatar':True}}
        data = llsd.format_xml(data)

        if debug:
            print ''
            print 'Posting to seedcap for place_avatar_cap'

        result = capabilities.postToCap(capabilities.capabilities['agent_seed_cap'], headers, data)

        print 'Caps returned are: ' + str(llsd.parse(result)['caps'])
        capabilities.updateCaps(llsd.parse(result)['caps'])    
        #capabilities.appendCap('place_avatar', llsd.parse(result)['caps']['place_avatar'])

        if debug:
            print 'Result of seedcap post for place avatar = '
            print pprint.pprint(llsd.parse(result))
            print capabilities.printCaps()
            print ''

        # post to event_queue_cap to set up reverse_HTTP
        #headers = {"Upgrade" : "PTTH/0.9"}
        #data = {}
        #print 'Posting to event_queue'
        #result = capabilities.postToCap(capabilities.capabilities['event_queue'], headers, data)

        #print "\nThe result of upgrade is: "
        #print result
        #print ''
            
        # post to place avatar cap with region uri
        headers = {"Content-type" : "application/llsd+xml"}
        data = {'region_url':self.agent.regionuri}#, 'position' : [0.0,0.0,0.0]}
        data = llsd.format_xml(data)

        print 'Posting to seedcap place_avatar with region_url'    
        result = capabilities.postToCap(capabilities.capabilities['place_avatar'], headers, data)
        if result == None:
            print 'Post to place_avatar failed'
            return

        if debug:
            print 'Result of seedcap post to place avatar = '
            print pprint.pprint(llsd.parse(result))
            print capabilities.printCaps()
            print ''

        capabilities.appendCap('sim_seed_cap', llsd.parse(result)['seed_capability'])
        
        #post to seed cap for sim to get placed
        #from here, it is the same as legacy

##	print 'Posting to simulator to get placed'
##	headers = {"Content-type" : "application/llsd+xml"}
##	data = {'region_url':agent.regionuri}
##	data = llsd.format_xml(data)
##       
##	result = capabilities.postToCap(capabilities.capabilities['sim_seed_cap'], headers, data)
##
##	if debug:
##	    print 'Result of seedcap post for place_avatar = '
##	    print pprint.pprint(llsd.parse(result))

        results = llsd.parse(result)
        print "Results"
        pprint.pprint(results)
        session_id = lluuid.UUID(results['session_id'])
        secure_session_id = lluuid.UUID(results['secure_session_id'])
        agent_id = lluuid.UUID(results['agent_id'])

        host = results['sim_ip']
        port = results['sim_port']
        circuit_code = struct.pack("I", results['circuit_code'])
        seed_capability_url = results['seed_capability']

        agent_movement_header = '\x40\x00\x00\x00\x03\x00\xff\xff\x00\xf9'
        circuit_code_header = '\x40\x00\x00\x00\x01\x00\xff\xff\x00\x03'

        agent_move_packet = agent_movement_header + agent_id._bits + session_id._bits + circuit_code
        circuit_use_packet = circuit_code_header + circuit_code + session_id._bits + agent_id._bits

        sim_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sim_udp.sendto(circuit_use_packet, (host, port))
        sim_udp.sendto(agent_move_packet, (host, port))
        #sim_udp.close()
        
        return results

    def postOGPLogin(self, llsdloginparams, headers):
        """ handles the post to the Second Life's agent domain login uri, and the redirect upon success  """
        
        request = urllib2.Request(self.loginuri, llsdloginparams, headers)

        # todo: handle non 302 cases! there's plenty, and lots are test cases
        # per the protocol, a successful authentication returns a 302 with the seedcap embedded in the headers 
        class RedirectHandler(urllib2.HTTPRedirectHandler):

            def http_error_302(self, req, fp, code, msg, headers):
                #parse the redirect, grabbing the seed cap url from the headers
                if True:
                    print ''
                    print 'contents of response = '
                    print headers
                    print msg
                    print ''
                

                # per the protocol, the seedcap is in the 'location' in headers
                return headers['location']

        # post to auth.cgi, ignoring the built in redirect
        opener = urllib2.build_opener(RedirectHandler())

        try:
            seed_cap = opener.open(request)
            return seed_cap
        except urllib2.HTTPError, e:
            print 'HTTP Error: ', e.code
        except urllib2.URLError, e:
            print 'URL Error: ', e.reason

        return None
    
