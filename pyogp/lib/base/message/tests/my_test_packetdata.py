#!/Library/Frameworks/Python.framework/Versions/2.5/Resources/Python.app/Contents/MacOS/Python

"""this is quick and dirty test of packets including pretty printing and timing of the ObjectUpdate packet,
which gave us such hassles originally. Should be a drop-in replacement for the original test_packet.py script 
with the sys.path info below deleted"""

import sys
sys.path[0:0] = [
  '/Users/lawsonenglish/libdev/eggs/zope.interface-3.4.1-py2.5-macosx-10.3-fat.egg',
  '/Users/lawsonenglish/libdev/eggs/uuid-1.30-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/indra.base-1.0-py2.5.egg',
  '/Users/lawsonenglish/libdev/src/pyogp.lib.base',
  '/Users/lawsonenglish/libdev/eggs/zope.testing-3.7.0-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/setuptools-0.6c9-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/grokcore.component-1.5.1-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/wsgiref-0.1.2-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/WebOb-0.9.3-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.component-3.5.1-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/indra.util-1.0-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.event-3.4.0-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.configuration-3.4.0-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/martian-0.11-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.i18nmessageid-3.4.3-py2.5-macosx-10.3-fat.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.proxy-3.4.2-py2.5-macosx-10.3-fat.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.security-3.5.2-py2.5-macosx-10.3-fat.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.deferredimport-3.4.0-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.deprecation-3.4.0-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.schema-3.5.0a1-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.location-3.4.0-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.exceptions-3.5.2-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/pytz-2008h-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.traversing-3.5.0a4-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.publisher-3.5.4-py2.5.egg',
  '/Users/lawsonenglish/libdev/eggs/zope.i18n-3.5.0-py2.5.egg',
  ]

"""
@file test_packetdata.py
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

#standard libraries
import unittest, doctest
import pprint
import binascii
import datetime, re

from zope.component import getUtility

#local libraries
from pyogp.lib.base.message.data import msg_tmpl
from pyogp.lib.base.message.interfaces import IUDPDispatcher
from pyogp.lib.base.interfaces import IDeserialization
from pyogp.lib.base.message.template_parser import MessageTemplateParser
from pyogp.lib.base.message.template_dict import TemplateDictionary
from pyogp.lib.base.registration import init
from pyogp.lib.base.message.types import MsgType

AGENT_DATA_UPDATE="C0 00 00 00 02 00 FF FF 01 83 1C 8A 77 67 E3 7B 42 2E AF B3 85 09 31 97 CA D1 03 4A 42 00 01 06 4B 72 61 66 74 00 01 01 00 1A"
AGENT_DATA_UPDATE =  binascii.unhexlify(''.join(AGENT_DATA_UPDATE.split()))

AGENT_ANIMATION="40 00 00 00 0A 00 05 1C 8A 77 67 E3 7B 42 2E AF B3 85 09 31 97 CA D1 4B 6F FF 1F B5 67 41 FD 85 EF A1 98 3B F2 B5 77 01 EF CF 67 0C 2D 18 81 28 97 3A 03 4E BC 80 6B 67 00 01 00"
AGENT_ANIMATION =  binascii.unhexlify(''.join(AGENT_ANIMATION.split()))

OBJECT_UPDATE = "C0 00 00 00 51 00 0C 00 01 EA 03 00 02 E6 03 00 01 BE FF 01 06 BC 8E 0B 00 01 69 94 8C 6A 4D 22 1B 66 EC E4 AC 31 63 93 CB 4B 57 89 98 01 09 03 00 01 51 40 88 3E 51 40 88 3E 51 40 88 3E 3C A2 44 B3 42 9A 68 2B 42 C8 5B D1 41 00 18 4B 8C FF 3E BD 76 FF BE C5 44 00 01 BF 00 10 50 04 00 01 10 20 05 00 04 64 64 00 0F 2E 00 01 A1 33 DC 77 0A 1A BB 27 A7 2E 78 64 63 AB 94 AB 00 08 80 3F 00 03 80 3F 00 0F 10 13 FF 00 08 80 3F 8F C2 F5 3D 00 0A 56 6F 43 CC 00 01 02 00 03 04 00 02 04 00 02 64 26 00 03 0E 00 01 0E 00 01 19 00 01 80 00 01 80 00 01 80 00 01 80 00 01 80 00 01 80 91 11 D2 5E 2F 12 8F 81 55 A7 40 3A 78 B3 0E 2D 00 10 03 01 00 03 1E 25 6E A2 FF C5 E0 83 00 01 06 00 01 0D 0D 01 00 11 0E DC 9B 83 98 9A 4A 76 AC C3 DB BF 37 54 61 88 00 22"
OBJECT_UPDATE =  binascii.unhexlify(''.join(OBJECT_UPDATE.split()))


class TestPacketDecode(object):



    def __init__(self):
        print "start =", str(datetime.datetime.now())
        init()
        self.template_file = msg_tmpl
        parser = MessageTemplateParser(self.template_file)
        self.template_list = parser.message_templates        
        self.template_dict = TemplateDictionary(self.template_list)
        print "end =", str(datetime.datetime.now())

    def test_agent_data_update(self):
        """test if the agent data update packet can be decoded"""
        message = AGENT_DATA_UPDATE
        size = len(message)
        deserializer = IDeserialization(message)
        packet = deserializer.deserialize()
        assert packet != None, "Wrong data"
        assert packet.message_data.name == 'AgentDataUpdate', "Wrong packet"
        assert packet.message_data.blocks['AgentData'][0].vars['LastName'].data == 'Kraft\x00', \
               "Wrong last name for agent update"
        assert packet.message_data.blocks['AgentData'][0].vars['FirstName'].data == 'JB\x00', \
               "Wrong first name for agent update"
        for ablock in packet.message_data.blocks.keys():
            print packet.message_data.blocks[ablock]

    def test_object_update(self):
        """test if the object update packet can be decoded"""



        message = OBJECT_UPDATE
        size = len(message)

        deserializer = IDeserialization(message)
        #geeneric timing code, should work 99% of the time unless we're at start time xx:xx:59.9 seconds or thereabouts

        secsearch= re.compile('([0-90-9]+)\.([0-9]+)')
        start = str(datetime.datetime.now())
        matchobj = secsearch.search(start)
        startsecs = float(matchobj.group(1)+'.'+matchobj.group(2))

        packet = deserializer.deserialize()
        assert packet != None, "Wrong data"
        assert packet.message_data.name == 'ObjectUpdate', "Wrong packet"

        #pretty printer for packets. Should work with any (not tested though).

        print "Packetname is:", packet.name
        for ablock in packet.message_data.blocks:
            print "\tblockname is:", ablock

            for somevars in packet.message_data.blocks[ablock]:
                for avar in somevars.var_list:
                    zvar = somevars.get_variable(avar)
                    print "\t\t"+ zvar.name, zvar.get_var_type_as_string(), zvar.get_data_as_string()

        #finish off timing code
        matchobj = secsearch.search(str(datetime.datetime.now()))
        print "TIME =", float(matchobj.group(1)+'.'+matchobj.group(2)) - startsecs     




    def test_agent_animation(self):
        """test if the agent data update packet can be decoded"""
        message = AGENT_ANIMATION
        size = len(message)
        deserializer = IDeserialization(message)
        packet = deserializer.deserialize()
        assert packet != None, "Wrong data 2"


def main():
    testpackets = TestPacketDecode()
    testpackets.test_agent_data_update()
    testpackets.test_object_update()
    testpackets.test_agent_animation()


if __name__ == "__main__":
    main()