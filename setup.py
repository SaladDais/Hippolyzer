from setuptools import setup, find_packages
import os

version = '1.0'

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
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pyogp', 'pyogp.lib'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          'zope.component'
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'console_scripts': [
            'login = pyogp.lib.base.example:main',
        ],
      },
      
      )
