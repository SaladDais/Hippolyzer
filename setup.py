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
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='pyogp login awg virtualworlds',
      author='Christian Scholz',
      author_email='mrtopf@gmail.com',
      url='http://pyogp.net',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pyogp', 'pyogp.lib'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zope.interface>=3.4',
          'zope.component [zcml]',
          'uuid',
          'elementtree',
          'indra.base',
          'WebOb',
          'wsgiref',
          'grokcore.component',
          
      ],
      entry_points={
        'console_scripts': [
            'login = pyogp.lib.base.example:main',
            'OGPlogin = pyogp.lib.base.OGPLogin:main',
            'packets = pyogp.lib.base.message_template_parser:main',
            'testserver = pyogp.lib.base.tests.base:main'
        ],
      },
      
      )
