"""
Copyright 2008, Linden Research, Inc.
  See NOTICE.md for previous contributors
Copyright 2021, Salad Dais
All Rights Reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

version = '0.1'

with open(path.join(here, 'README.md')) as readme_fh:
    readme = readme_fh.read()

setup(
    name='hippolyzer',
    version=version,
    description="Analysis tools for SL-compatible virtual worlds",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    author='Salad Dais',
    license='LGPLv3',
    packages=["hippolyzer.lib.base", "hippolyzer.lib.proxy"],
    package_data={
        'hippolyzer.lib.base': [
            'message/data/message_template.msg',
            'message/data/message.xml',
            'network/tests/*.txt',
            'network/data/ca-bundle.crt',
            'tests/doctests/*.*',
            'tests/test_resources/*.*'
        ],
        'hippolyzer.lib.proxy': [
            'data/*',
        ],
    },
    namespace_packages=['hippolyzer', 'hippolyzer.lib'],
    zip_safe=False,
    python_requires='>=3.8',
    install_requires=[
        'setuptools',
        'llbase>=1.2.5',
        'defusedxml',
        'mitmproxy',
        'qasync',
        'aiohttp',
        'pyside2',
        'recordclass',
        'lazy-object-proxy',
    ],
)
