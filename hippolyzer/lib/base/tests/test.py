
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

import sys
import os
import nose

eggs_dir = os.path.join(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.realpath(__file__)))))))), 'eggs')

client_package_path = os.path.join(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.realpath(__file__))))))), 'pyogp.lib.client')

base_package_path = os.path.join(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.dirname(
    os.path.realpath(__file__))))))), 'pyogp.lib.base')

sys.path.append(client_package_path)
sys.path.append(base_package_path)

if os.path.exists(eggs_dir):

    print 'Adding eggs to sys.path...'

    for directory in os.listdir(eggs_dir):
        sys.path.append(os.path.join(eggs_dir, directory))

else:

    print 'No eggs dir to add to path. Make sure to add the necessary module dependencies to your python path prior to running.'

if __name__ == '__main__':
    nose.main(argv=['nose']+sys.argv[1:])