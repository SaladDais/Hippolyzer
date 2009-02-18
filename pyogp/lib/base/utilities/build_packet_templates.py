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
    blocks_dict = {}
    message_String = "Message(\'%s\'" % (name, )
    
    for block in blocks:
        blocks_dict[block] = block.get_variables()

    #print 'class %sPacket(MsgData):' % (name)
    print 'class %sPacket(object):' % (name)
    print '    \'\'\' a template for a %s packet \'\'\'' % (name)
    print ''
    print '    def __init__(self):'
    #print ''
    print '        self.name = \'%s\'' % (name)
    #print '        self.blocks = []'
    for block in blocks:
        message_String = message_String + ", Block(\'%s\'" % (block.get_name())
        print ''
        #print '        # New %s block' % (block.get_name())
        #print '        # should this move to a self.%s = MsgBlockData(\'%s\') model?' % (block.get_name(), block.get_name())
        print '        self.%s = {}    # New %s block' % (block.get_name(), block.get_name())
        #print '        self.%s = MsgBlockData(\'%s\')' % (block.get_name(), block.get_name())
        #print ''
        for var in block.get_variables():
            message_String = message_String + ", %s = self.%s[\'%s\']" % (var.name, block.get_name(), var.name)

            print '        self.%s[\'%s\'] = %s    # %s' % (block.get_name(), var.name, 'None', var.get_type_as_string())
        message_String = message_String + ')'
        #print ''
        #print '        self.blocks.append(self.%s)' % (block.get_name())
        #print ''
    message_String = message_String + ')'
    print ''
    print '    def __call__(self):'
    print '        \'\'\' transforms the attributes into a Message \'\'\''
    print ''
    print '        return %s' % (message_String)
    #print message_String
    print ''
 
