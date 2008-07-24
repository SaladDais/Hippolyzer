#standard libraries
import unittest, doctest
from uuid import UUID

#local libraries
from pyogp.lib.base.data import msg_tmpl
from pyogp.lib.base.message_template import MessageTemplate, MessageTemplateBlock, MessageTemplateVariable
from pyogp.lib.base.message_template_parser import MessageTemplateParser
from pyogp.lib.base.message_template_builder import MessageTemplateBuilder
from pyogp.lib.base.message_template_dict import TemplateDictionary
from pyogp.lib.base.message_types import MsgType
#from indra.base.lluuid import UUID

class TestTemplateBuilder(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        self.template_file = msg_tmpl
        parser = MessageTemplateParser(self.template_file)
        self.template_list = parser.message_templates
        self.template_dict = TemplateDictionary(self.template_list)
        
    def test_builder(self):
        try:
            builder = MessageTemplateBuilder(None)
            assert False, "Template builder fail case list==None not caught"
        except:
            assert True

    def test_create_message_fail(self):
        builder = MessageTemplateBuilder(self.template_dict)
        try:
            builder.new_message('CreateFakeLindenMessage')
            assert False, "Creating a message that doesn't exist"
        except:
            assert True
            
        assert builder.current_msg == None, "Created a message despite its non-existence"

    def test_create_message(self):
        builder = MessageTemplateBuilder(self.template_dict)
        assert builder.current_msg == None, "Message exists before it was created"
        builder.new_message('AddCircuitCode')
        assert builder.current_msg != None, "Create message failed"

    def test_create_message_blocks(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('AvatarTextureUpdate')
        blocks = builder.current_msg.block_map
        assert len(blocks) == 3, "Blocks not added to the message"
        try:
            t_block = blocks['AgentData']
            assert t_block != None,"Message doesn't have AgentData block"
        except KeyError:
            assert False, "Message doesn't have AgentData block"

        try:
            t_block = blocks['WearableData']
            assert t_block != None, "Message doesn't have WearableData block"
        except KeyError:
            assert False, "Message doesn't have WearableData block"

        try:
            t_block = blocks['TextureData']
            assert t_block != None, "Message doesn't have TextureData block"
        except KeyError:
            assert False, "Message doesn't have TextureData block"

    def test_next_block(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('AvatarTextureUpdate')
        assert builder.current_block == None, "Message block exists before  it was created"
        builder.next_block('AgentData')
        assert builder.current_block != None, "Setting next block failed"
        assert builder.current_block.name == 'AgentData', "Wrong block set"        

    def test_next_block_fail(self):
        builder = MessageTemplateBuilder(self.template_dict)

        builder.new_message('AvatarTextureUpdate')
        try:
            builder.next_block('AgentSocialIdeas')
            assert False, "Using block AgentSocialIdeas that doesn't exist"
        except:
            assert True
        assert builder.current_block == None, "Set block without one existing"        

    def test_next_single(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('TestMessage')
        builder.next_block('TestBlock1')
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        try:
            builder.next_block('TestBlock1')
            assert False, "Adding 2 blocks of the same type to a MBT_SINGLE block"
        except:
            assert True

    def test_nextmultiple_exceed(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('TestMessage')
        builder.next_block('TestBlock1')
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.next_block('NeighborBlock')
        builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        builder.next_block('NeighborBlock')
        builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        builder.next_block('NeighborBlock')
        builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        builder.next_block('NeighborBlock')
        builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        try:
            builder.next_block('NeighborBlock')
            assert False, "Allowed to add more than specified number of blocks"
        except:
            assert True

    def test_build_variable(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('PacketAck')
        builder.next_block('Packets')
        builder.add_data('ID', 0x00000001, MsgType.MVT_U32)
        builder.next_block('Packets')
        builder.add_data('ID', 0x00000001, MsgType.MVT_U32)
        msg, size = builder.build_message()
        assert msg == '\xff\xff\xff\xfb' + '\x02' + \
                    '\x00\x00\x00\x01\x00\x00\x00\x01', \
                    "Building variable block failed"
        
    def test_build_empty_var(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('PacketAck')
        builder.next_block('Packets')
        try:
            msg, size = builder.build_message()
            assert False, "Building with a variable that wasn't set"
        except:
            assert True

    def test_build_variable_var(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('UpdateSimulator')
        builder.next_block('SimulatorInfo')
        builder.add_data('RegionID', UUID("550e8400-e29b-41d4-a716-446655440000"), MsgType.MVT_LLUUID)
        builder.add_data('SimName', "Testing", MsgType.MVT_VARIABLE)
        builder.add_data('EstateID', 0x00000001, MsgType.MVT_U32)
        builder.add_data('SimAccess', 0x01, MsgType.MVT_U8)
        msg, size = builder.build_message()

        assert_string = '\xff\xff\x00\x11' + UUID("550e8400-e29b-41d4-a716-446655440000").bytes + \
                    '\x07' + 'Testing' + '\x00\x00\x00\x01' + '\x01'
        assert msg == assert_string, "Building variable block failed"


    def test_next_block_variables(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('AvatarTextureUpdate')
        builder.next_block('AgentData')
        variables = builder.current_block.variable_map

        assert len(variables) == 2, "Variables not added to the block"
        try:
            t_var = variables['AgentID']
            assert t_var != None,"Block doesn't have AgentID variable"
            assert t_var.name == 'AgentID', "AgentID name incorrect"
            assert t_var.type == MsgType.MVT_LLUUID, "AgentID type incorrect"
        except KeyError:
            assert False, "Block doesn't have AgentID variable"

        try:
            t_var = variables['TexturesChanged']
            assert t_var != None,"Block doesn't have TexturesChanged variable"
            assert t_var.name == 'TexturesChanged', "Name incorrect"
            assert t_var.type == MsgType.MVT_BOOL, "Type incorrect"
        except KeyError:
            assert False, "Block doesn't have TexturesChanged variable"

    def test_add_bool(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('AvatarTextureUpdate')
        builder.next_block('AgentData')
        builder.add_data('TexturesChanged', True, MsgType.MVT_BOOL)
        #need a way to determine the right variable data is sent compared to the type
        assert builder.current_block.variable_map['TexturesChanged'].data == True,\
               "Data not set correctly"

    def test_add_lluuid(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('AvatarTextureUpdate')
        builder.next_block('AgentData')
        builder.add_data('AgentID', UUID("550e8400-e29b-41d4-a716-446655440000"), MsgType.MVT_LLUUID)
        assert builder.current_block.variable_map['AgentID'].data == UUID("550e8400-e29b-41d4-a716-446655440000"),\
               "Data not set correctly"
        #assert builder.current_block.variables['AgentID'].get_size() == ?
        
    #test should go with the packer mostly
    def test_serialize_u8_fail(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('AvatarTextureUpdate')
        builder.next_block('AgentData')

        try:
            builder.add_data('AgentID', 0x01, MsgType.MVT_U8)
            assert False, "Adding U8 to a variable that should be UUID"
        except:
            assert True
        
    def test_build_fail(self):
        builder = MessageTemplateBuilder(self.template_dict)
        msg = builder.build_message()
        assert msg == None, "Got a message without calling new first"


    def test_build_multiple_fail(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('TestMessage')
        builder.next_block('TestBlock1')
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.next_block('NeighborBlock')
        builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        try:
            msg, size = builder.build_message()
            assert False, "Message block should be 1, where it should be 4"
        except:
            assert True

    def test_build_multiple(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('TestMessage')
        builder.next_block('TestBlock1')
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.next_block('NeighborBlock')
        builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        builder.next_block('NeighborBlock')
        builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        builder.next_block('NeighborBlock')
        builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        builder.next_block('NeighborBlock')
        builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)

        msg = None
        size = 0
        
        try:
            msg, size = builder.build_message()

        except Exception, e:
            assert False, "Multiple blocks not working correctly"

        assert msg == '\xff\xff\x00\x01' + '\x00\x00\x00\x01' + \
                    '\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01' + \
                    '\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01' + \
                    '\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01' + \
                    '\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01', \
                    'TestMessage data not built correctly'
        
    def test_serialize_u8(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('CompletePingCheck')
        builder.next_block('PingID')
        builder.add_data('PingID', 0x01, MsgType.MVT_U8)
        msg, size = builder.build_message()
        assert msg == "\x02\x01", "U8 not packed correctly"
        assert size == 2, "U8 size not correct"
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplateBuilder))
    return suite
