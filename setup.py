"""
@file setup.py
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

from setuptools import setup, find_packages

version = '0.1'

setup(name='pyogp.lib.base',
     version=version,
     description="basic pyogp library package",
     long_description=open('README.txt').read(),
     # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
     classifiers=[
       "Programming Language :: Python",
       "Topic :: Software Development :: Libraries :: Python Modules",
       ],
     keywords='pyogp login awg virtualworlds',
     author='Pyogp collective',
     author_email='pyogp@lists.lindenlab.com',
     url='http://wiki.secondlife.com/wiki/Pyogp',
     license='Apache2',
     packages=find_packages(exclude=['ez_setup']),
     package_data={'pyogp.lib.base': ['message/data/message_template.msg', 'message/data/message.xml']},
     namespace_packages=['pyogp', 'pyogp.lib'],
     zip_safe=False,
     install_requires=[
         'setuptools',
         # -*- Extra requirements: -*-
         'uuid',
         'elementtree',
         'llbase',
         'WebOb==0.8',
         'wsgiref',
         'eventlet'

     ]
     )
