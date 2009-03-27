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
import os

version = '0.1'

setup(name='pyogp.lib.base',
     version=version,
     description="basic pyogp library package",
     long_description="skipping",
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
     #namespace_packages=['pyogp', 'pyogp.lib'],
     include_package_data=True,
     zip_safe=False,
     install_requires=[
         'setuptools',
         # -*- Extra requirements: -*-
         'uuid',
         'elementtree',
         'indra.base',
         'WebOb',
         'wsgiref',
         'eventlet'

     ],
     entry_points={
       'console_scripts': [
           'login = pyogp.lib.base.examples.sample_login:main',
           'agent_login = pyogp.lib.base.examples.sample_agent_login:main',
           'region_connect = pyogp.lib.base.examples.sample_region_connect:main',
           'inventory_handling = pyogp.lib.base.examples.sample_inventory_handling:main',
           'object_tracking = pyogp.lib.base.examples.sample_object_tracking:main',
           'object_creation = pyogp.lib.base.examples.sample_object_creation:main',
           'object_create_edit = pyogp.lib.base.examples.sample_object_create_edit:main',
           'object_create_permissions = pyogp.lib.base.examples.sample_object_create_permissions:main',
           'object_properties = pyogp.lib.base.examples.sample_object_properties:main',
           'chat_and_instant_messaging = pyogp.lib.base.examples.sample_chat_and_instant_messaging:main',
           'group_creation = pyogp.lib.base.examples.sample_group_creation:main',
           'group_chat = pyogp.lib.base.examples.sample_group_chat:main',
           'agent_manager = pyogp.lib.base.examples.sample_agent_manager:main'
       ],
     },

     )
