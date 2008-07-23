#standard libraries
import unittest, doctest

#local libraries
from pyogp.lib.base.data import msg_tmpl
from pyogp.lib.base.message_template import MessageTemplate, MessageTemplateBlock, MessageTemplateVariable
from pyogp.lib.base.message_template_parser import MessageTemplateParser
from pyogp.lib.base.message_template_builder import MessageTemplateBuilder
from pyogp.lib.base.message_template_dict import TemplateDictionary
from pyogp.lib.base.message_types import MsgType
from indra.base.lluuid import UUID

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
            
        assert builder.get_current_message() == None, "Created a message despite its non-existence"

    def test_create_message(self):
        builder = MessageTemplateBuilder(self.template_dict)
        assert builder.get_current_message() == None, "Message exists before it was created"
        builder.new_message('AddCircuitCode')
        assert builder.get_current_message() != None, "Create message failed"

    def test_create_message_blocks(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('AvatarTextureUpdate')
        blocks = builder.get_current_message().blocks
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
        assert builder.get_current_block() == None, "Message block exists before  it was created"
        builder.next_block('AgentData')
        assert builder.get_current_block() != None, "Setting next block failed"
        assert builder.get_current_block().name == 'AgentData', "Wrong block set"        

    def test_next_block_fail(self):
        builder = MessageTemplateBuilder(self.template_dict)

        builder.new_message('AvatarTextureUpdate')
        try:
            builder.next_block('AgentSocialIdeas')
            assert False, "Using block AgentSocialIdeas that doesn't exist"
        except:
            assert True
        assert builder.get_current_block() == None, "Set block without one existing"        

    def test_next_block_variables(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('AvatarTextureUpdate')
        builder.next_block('AgentData')
        variables = builder.get_current_block().variables

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
        assert builder.get_current_block().variables['TexturesChanged'].data == True,\
               "Data not set correctly"

    def test_add_lluuid(self):
        builder = MessageTemplateBuilder(self.template_dict)
        builder.new_message('AvatarTextureUpdate')
        builder.next_block('AgentData')
        builder.add_data('AgentID', UUID("550e8400-e29b-41d4-a716-446655440000"), MsgType.MVT_LLUUID)
        assert builder.get_current_block().variables['AgentID'].data == UUID("550e8400-e29b-41d4-a716-446655440000"),\
               "Data not set correctly"
        #assert builder.get_current_block().variables['AgentID'].get_size() == ?
        

        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplateBuilder))
    return suite
