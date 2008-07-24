import BaseHTTPServer
from indra.base import llsd
from webob import Request, Response

import md5

#PW = "$1$"+md5.new("secret").hexdigest()
PW="secret"


class AgentDomain(object):
    
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
        except:
            self.response.status=500
            return self.response(self.environ, self.start)
        if self.request.path=="/":
            return self.handle_login(data)
        elif self.request.path=="/network/get" and self.request.method=="GET":
            self.response.status=200
            self.response.body="Hello, World"
            return self.response(self.environ, self.start)
        elif self.request.path=="/network/post" and self.request.method=="POST":
            data = self.request.body
            self.response.status=200
            self.response.body="returned: %s" %data
            return self.response(self.environ, self.start)
        elif self.request.path=="/seed_cap":
            return self.handle_seedcap(data)
        elif self.request.path=="/seed_cap_wrong_content_type":
            return self.handle_seedcap(data,content_type="text/html")
        elif self.request.path=="/cap/place_avatar":
            return self.place_avatar(data)
        elif self.request.path=="/cap/some_capability":
            return self.some_capability(data)        
        else:
            return self.send_response(404, 'resource not found.')

    def handle_seedcap(self, data, content_type="application/llsd+xml"):
        """return some other caps"""
        caps = data.get("caps",[])
        d = {'lastname': 'lastname', 'firstname': 'firstname'}
        return_caps = {}
        for cap in caps:
            # simple mapping from capname => host/cap/<capname> instead of UUIDs
            return_caps[cap]="http://localhost:12345/cap/%s" %cap
        d['caps'] = return_caps
        data = llsd.format_xml(d)
        self.response.status=200
        self.response.content_type=content_type
        self.response.body = data
        return self.response(self.environ, self.start)

    def place_avatar(self, data):
        """place the avatar in a dummy way"""
        url = data.get("region_url",'')
        d={'sim_ip':'127.0.0.1',
           'sim_port' : 12345}
        data = llsd.format_xml(d)
        self.response.status=200
        self.response.content_type='application/llsd+xml'
        self.response.body = data
        return self.response(self.environ, self.start)

    def some_capability(self, data):
        """handle a dummy test capabilty"""
        d={'something':'else',
           'some' : 12345}
        data = llsd.format_xml(d)
        self.response.status=200
        self.response.content_type='application/llsd+xml'
        self.response.body = data
        return self.response(self.environ, self.start)

        
    def handle_login(self,data):
        """handle the login string"""
        # TODO: test for all the correct fields in the data
        password = data.get('password')
        if password!=PW:
            self.send_response(403)
            return
        
        data={'agent_seed_capability':"http://127.0.0.1:12345/seed_cap"}
        data = llsd.format_xml(data)
        
        self.response.status=200
        self.response.content_type='application/llsd+xml'
        self.response.body=data
        return self.response(self.environ, self.start)
            
    def send_response(self, status, body=''):
        self.response.status = status
        self.response.body = body
        return self.response(self.environ, self.start)


def main():
    from wsgiref.simple_server import make_server
    httpd = make_server('', 12345, AgentDomain())
    
    # Respond to requests until process is killed
    httpd.serve_forever()

if __name__=="__main__":
    main()
