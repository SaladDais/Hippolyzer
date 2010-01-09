
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

# standard
import re
import BaseHTTPServer
import md5

# related
from llbase import llsd
from webob import Request, Response

#PW = "$1$"+md5.new("secret").hexdigest()
PW="secret"

class StdLibClient(object):

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start = start_response
        self.request = Request(environ)
        self.response = Response()

        l = self.request.headers.get('Content-Length','0')
        if l=='':
            l='0'
        l = int(l)
        data = self.request.body

        # we assume it's LLSD for now and try to parse it
        # TODO: check headers
        try:
            data = llsd.parse(data)
            if data is False:	# might happen with GET
                data={}
        except:
            self.response.status=500
            return self.response(self.environ, self.start)

        if self.request.path=="/network/get" and self.request.method=="GET":
            self.response.status=200
            self.response.body="Hello, World"
            return self.response(self.environ, self.start)
        elif self.request.path=="/network/post" and self.request.method=="POST":
            data = self.request.body
            self.response.status=200
            self.response.body="returned: %s" %data
            return self.response(self.environ, self.start)
        else:
            return self.send_response(404, 'resource not found.')

    def send_response(self, status, body=''):
        self.response.status = status
        self.response.body = body
        return self.response(self.environ, self.start)

class MockXMLRPCLogin(object):
    def __call__(self, environ, start_response):
        self.environ = environ
        self.start = start_response
        self.request = Request(environ)
        self.response = Response()

        l = self.request.headers.get('Content-Length','0')
        if l=='':
            l='0'
        l = int(l)
        data = self.request.body

        # ToDo: we should really parse the data we receive in the string and respond nicely

        if self.request.path=="/cgi-bin/login.cgi":
            return self.handle_legacy_login(data)
        else:
            return self.send_response(404, 'resource not found.')

    def handle_legacy_login(self,data):
        """handle the login string"""

        if re.search('badpassword', self.request.body):
            data = {'login' :'false', 'message' : 'key'}
            self.response.status = 200
        else:
            data={'region_y': 256, 'region_x': 256, 'first_name': '"first"', 'secure_session_id': '00000000-0000-0000-0000-000000000000', 'sim_ip': '127.0.0.1', 'seed_capability': 'https://somesim:12043/cap/00000000-0000-0000-0000-000000000000', 'agent_access': 'M', 'circuit_code': 600000000, 'look_at': '[r0.9963859999999999939,r-0.084939700000000006863,r0]', 'session_id': '00000000-0000-0000-0000-000000000000', 'udp_blacklist': 'EnableSimulator,TeleportFinish,CrossedRegion', 'last_name': 'last', 'agent_id': '00000000-0000-0000-0000-000000000000', 'sim_port': 13001, 'inventory_host': 'someinvhost', 'start_location': 'last', 'message': "message", 'login': 'true', 'seconds_since_epoch': 1234567890}
            self.response.status = 200

        result = ''
        for k in data:
            result += '%s %s '% (k, data[k])
        self.response.body = result
        return self.response(self.environ, self.start)

    def send_response(self, status, body=''):
        self.response.status = status
        self.response.body = body
        return self.response(self.environ, self.start)   

class MockAgentDomainLogin(object):

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start = start_response
        self.request = Request(environ)
        self.response = Response()

        l = self.request.headers.get('Content-Length','0')
        if l=='':
            l='0'
        l = int(l)
        data = self.request.body

        # we assume it's LLSD for now and try to parse it
        # TODO: check headers
        try:
            data = llsd.parse(data)
            if data is False:	# might happen with GET
                data={}
        except:
            self.response.status=500
            return self.response(self.environ, self.start)

        if self.request.path=="/auth.cgi":
            return self.handle_ogp_login(data)
        else:
            return self.send_response(404, 'resource not found.')

    def handle_ogp_login(self,data):
        """handle the login string"""

        # TODO: This is inadequate, need to handle the cases properly 
        password = data.get('password')
        if password!=PW:
            self.send_response(403)
            return

        data={'agent_seed_capability':"http://127.0.0.1:12345/seed_cap", 'authenticated':True}
        data = llsd.format_xml(data)

        self.response.status=200
        self.response.content_type='application/llsd+xml'
        self.response.body=data
        return self.response(self.environ, self.start)

    def handle_legacy_login(self,data):
        """handle the login string"""

        # TODO: This is inadequate, need to handle the cases properly 
        password = data.get('password')
        if password!=PW:
            self.send_response(403)
            return

        data={'seed_capability':"http://127.0.0.1:12345/seed_cap",'login':'true'}
        data = llsd.format_xml(data)

        self.response.status=200
        self.response.content_type='application/llsd+xml'
        self.response.body=data
        return self.response(self.environ, self.start)

    def send_response(self, status, body=''):
        self.response.status = status
        self.response.body = body
        return self.response(self.environ, self.start)

# Todo: rename this from AgentDomain to specific stuffs and break it out
class MockAgentDomain(object):

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start = start_response
        self.request = Request(environ)
        self.response = Response()

        l = self.request.headers.get('Content-Length','0')
        if l=='':
            l='0'
        l = int(l)
        data = self.request.body

        # we assume it's LLSD for now and try to parse it
        # TODO: check headers
        try:
            data = llsd.parse(data)
            if data is False:	# might happen with GET
                data={}
        except:
            self.response.status=500
            return self.response(self.environ, self.start)

        if self.request.path=="/seed_cap":
            return self.handle_seedcap(data)
        elif self.request.path=="/seed_cap_wrong_content_type":
            return self.handle_seedcap(data,content_type="text/foobar")
        elif self.request.path=="/cap_wrong_content_type":
            return self.some_capability({},content_type="text/foobar")
        elif self.request.path=="/cap/error":
            return self.send_response(500,'error')
        elif self.request.path=="/cap/rez_avatar/place":
            return self.place_avatar(data)
        elif self.request.path=="/cap/some_capability":
            return self.some_capability(data)        
        else:
            return self.send_response(404, 'resource not found.')

    def handle_seedcap(self, data, content_type="application/llsd+xml"):
        """return some other caps"""
        caps = data.get("capabilities",[])
        d = {'lastname': 'lastname', 'firstname': 'firstname'}
        return_caps = {}
        for cap in caps:
            # simple mapping from capname => host/cap/<capname> instead of UUIDs
            return_caps[cap]="http://localhost:12345/cap/%s" %cap
        d['capabilities'] = return_caps
        data = llsd.format_xml(d)
        self.response.status=200
        self.response.content_type=content_type
        self.response.body = data
        return self.response(self.environ, self.start)

    def place_avatar(self, data):
        """place the avatar in a dummy way"""
        url = data.get("region_url",'')
        d={'sim_ip':'127.0.0.1',
           'sim_port' : 12345,
           'region_seed_capability':'/region_seed_cap'}
        data = llsd.format_xml(d)
        self.response.status=200
        self.response.content_type='application/llsd+xml'
        self.response.body = data
        return self.response(self.environ, self.start)

    def some_capability(self, data, content_type="application/llsd+xml"):
        """handle a dummy test capabilty"""
        d={'something':'else',
           'some' : 12345}
        d.update(data)
        data = llsd.format_xml(d)
        self.response.status=200
        self.response.content_type=content_type
        self.response.body = data
        return self.response(self.environ, self.start)

    def send_response(self, status, body=''):
        self.response.status = status
        self.response.body = body
        return self.response(self.environ, self.start)

def main():
    from wsgiref.simple_server import make_server
    print 'I am here'
    httpd = make_server('', 12345, AgentDomain())

    # Respond to requests until process is killed
    httpd.serve_forever()

if __name__=="__main__":
    main()



