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

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

version = '0.11.1'

with open(path.join(here, 'README.md')) as readme_fh:
    readme = readme_fh.read()

setup(
    name='hippolyzer',
    version=version,
    description="Analysis tools for SL-compatible virtual worlds",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    author='Salad Dais',
    author_email='83434023+SaladDais@users.noreply.github.com',
    url='https://github.com/SaladDais/Hippolyzer/',
    license='LGPLv3',
    packages=find_packages(include=["hippolyzer", "hippolyzer.*"]),
    package_data={
        'hippolyzer': [
            'apps/message_builder.ui',
            'apps/proxy_mainwindow.ui',
            'apps/filter_dialog.ui',
            'apps/addon_dialog.ui',
            'lib/base/message/data/message_template.msg',
            'lib/base/message/data/message.xml',
            'lib/base/network/data/ca-bundle.crt',
            'lib/base/data/static_data.db2',
            'lib/base/data/static_index.db2',
            'lib/base/data/avatar_lad.xml',
            'lib/base/data/male_collada_joints.xml',
            'lib/base/data/avatar_skeleton.xml',
            'lib/base/data/LICENSE-artwork.txt',
        ],
    },
    entry_points={
        'console_scripts': {
            'hippolyzer-gui = hippolyzer.apps.proxy_gui:gui_main',
            'hippolyzer-cli = hippolyzer.apps.proxy:main'
        }
    },
    zip_safe=False,
    python_requires='>=3.8',
    install_requires=[
        'llbase>=1.2.5',
        'defusedxml',
        'aiohttp<4.0.0',
        'recordclass<0.15',
        'lazy-object-proxy',
        'arpeggio',
        # requests breaks with newer idna
        'idna<3,>=2.5',
        # 7.x will be a major change.
        'mitmproxy>=8.0.0,<8.1',
        # For REPLs
        'ptpython<4.0',
        # JP2 codec
        'Glymur<0.9.7',
        'numpy<2.0',
        # These could be in extras_require if you don't want a GUI.
        'pyside6',
        'qasync',
        # Needed for mesh format conversion tooling
        'pycollada',
        'transformations',
    ],
    tests_require=[
        "pytest",
        "aioresponses",
    ],
)
