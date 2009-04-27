"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

try:

    from pkg_resources import resource_stream, resource_string

except ImportError:

    import urllib2
    import tempfile

    tmpeggs = tempfile.mkdtemp()

    ez = {}
    exec urllib2.urlopen('http://peak.telecommunity.com/dist/ez_setup.py'
        ).read() in ez
    ez['use_setuptools'](to_dir=tmpeggs, download_delay=0)

    from pkg_resources import resource_stream, resource_string

msg_tmpl = resource_stream(__name__, 'message_template.msg')
msg_details = resource_string(__name__, 'message.xml')
