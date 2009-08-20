
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

import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', '..', '..', '..')))

from pyogp.lib.base.message.template_dict import TemplateDictionary



'''
msg = Message('AgentUpdate',
      Block('AgentData', AgentID=uuid.UUID(self.details['agent_id']),
            SessionID=uuid.UUID(self.details['session_id']),
            BodyRotation=(0.0,0.0,0.0,0.0),
            HeadRotation=(0.0,0.0,0.0,0.0),
            State=0x00,
            CameraCenter=(0.0,0.0,0.0),
            CameraAtAxis=(0.0,0.0,0.0),
            CameraLeftAxis=(0.0,0.0,0.0),
            CameraUpAxis=(0.0,0.0,0.0),
            Far=0,
            ControlFlags=0x00,
            Flags=0x00))
'''

print '"""'
print '@file packets.py'
print '@date 2009-02-04'
print 'Contributors can be viewed at:'
print 'http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt '
print ''
print '$LicenseInfo:firstyear=2008&license=apachev2$'
print ''
print 'Copyright 2008, Linden Research, Inc.'
print ''
print 'Licensed under the Apache License, Version 2.0 (the "License").'
print 'You may obtain a copy of the License at'
print ''
print 'http://www.apache.org/licenses/LICENSE-2.0'
print 'or in '
print 'http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt'
print ''
print '$/LicenseInfo$'
print '"""'
print ''
print 'from pyogp.lib.base.message.message import Message, Block'
print ''
template = TemplateDictionary()

for i in template.message_dict:

    name = template.message_dict[i].get_name()

    blocks = template.message_dict[i].get_blocks()

    block_variables = {}

    call_instance_contents_string = ''
    class_block_parameters_string = ''

    for block in blocks:
        block_variables[block] = block.get_variables()
        if block.get_block_type_as_string() == 'Single':
            class_block_parameters_string += ', %sBlock = {}' % (block.get_name())
        else:
            # if there may be multiple blocks of one type, accept a list
            class_block_parameters_string += ', %sBlocks = []' % (block.get_name())

    print 'class %sPacket(object):' % (name)
    print '    \'\'\' a template for a %s packet \'\'\'' % (name)
    print ''
    print '    def __init__(self%s):' % (class_block_parameters_string)
    print '        \"\"\" allow passing in lists or dictionaries of block data \"\"\"'
    print '        self.name = \'%s\'' % (name)

    for block in blocks:

        print ''

        if block.get_block_type_as_string() == 'Single':

            call_instance_contents_string += '        args.append(Block(\'%s\'' % (block.get_name())

            print '        if %sBlock == {}:' % (block.get_name())
            print '            # initialize an empty block like dict for blocks that occur only once in the packet'
            print '            self.%s = {}    # New %s block' % (block.get_name(), block.get_name())

            for var in block.get_variables():
                print '            self.%s[\'%s\'] = %s    # %s' % (block.get_name(), var.name, 'None', var.get_type_as_string())
                call_instance_contents_string += ', %s=self.%s[\'%s\']' % (var.name, block.get_name(), var.name)

            print '        else:'
            print '            self.%s = %sBlock' % (block.get_name(), block.get_name())

            call_instance_contents_string += '))\n'

        else:

            call_instance_contents_string += '        for block in self.%sBlocks:\n' % (block.get_name())
            call_instance_contents_string += '            args.append(Block(\'%s\'' % (block.get_name(),)

            print '        if %sBlocks == []:' % (block.get_name())
            print '            # initialize an empty list for blocks that may occur > 1 time in the packet'
            print '            self.%sBlocks = []    # list to store multiple and variable block types' % (block.get_name())
            print ''
            print '            # a sample block instance that may be appended to the list'
            #print '            \'\'\''
            print '            self.%s = {}' % (block.get_name())

            for var in block.get_variables():
                print '            self.%s[\'%s\'] = %s    # %s' % (block.get_name(), var.name, 'None', var.get_type_as_string())
                call_instance_contents_string += ', %s=%s[\'%s\']' % (var.name, 'block', var.name)

            #print '            \'\'\''
            print '        else:'
            print '            self.%sBlocks = %sBlocks' % (block.get_name(), block.get_name())

            call_instance_contents_string += '))\n'

    print ''
    print '    def __call__(self):'
    print '        \'\'\' transforms the object into a Message \'\'\''
    print ''
    print '        args = []'
    print '%s' % (call_instance_contents_string)
    print '        return Message(\'%s\', args)' % (name)

    print ''
