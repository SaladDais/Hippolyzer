#standard libraries
import unittest, doctest
from uuid import UUID

#local libraries
from pyogp.lib.base.data import msg_tmpl
from pyogp.lib.base.message.message_template import MessageTemplate, MessageTemplateBlock, MessageTemplateVariable
from pyogp.lib.base.message.message_template_parser import MessageTemplateParser
from pyogp.lib.base.message.message_template_builder import MessageTemplateBuilder
from pyogp.lib.base.message.message_template_reader import MessageTemplateReader
from pyogp.lib.base.message.message_template_dict import TemplateDictionary
from pyogp.lib.base.message.message_types import MsgType, PackFlags

class TestTemplateReader(unittest.TestCase):
    
    def tearDown(self):
        pass

    def setUp(self):
        self.template_file = msg_tmpl
        parser = MessageTemplateParser(self.template_file)
        self.template_list = parser.message_templates
        self.template_dict = TemplateDictionary(self.template_list)
        self.builder = MessageTemplateBuilder(self.template_dict)
        self.reader = MessageTemplateReader(self.template_dict)

    def test_validation(self):
        self.reader.clear_message()
        self.builder.new_message('CompletePingCheck')
        self.builder.next_block('PingID')
        self.builder.add_data('PingID', 0x01, MsgType.MVT_U8)
        message, size = self.builder.build_message()
        message = '\x00' + '\x00\x00\x00\x00' +'\x00' + message
        size = len(message)
        assert self.reader.validate_message(message, size) == True, \
               "Validation failed"
        assert self.reader.current_template.name == 'CompletePingCheck', \
               "Validation failed to get current template"

    def test_clear_message(self):
        self.reader.clear_message()
        self.builder.new_message('CompletePingCheck')
        self.builder.next_block('PingID')
        self.builder.add_data('PingID', 0x01, MsgType.MVT_U8)
        message, size = self.builder.build_message()
        message = '\x00' + '\x00\x00\x00\x00' +'\x00' + message
        size = len(message)
        self.reader.validate_message(message, size)
        assert self.reader.current_template != None, "Validate failed"
        self.reader.clear_message()
        assert self.reader.current_template == None, "Clear message failed"

    def test_validation_fail_size(self):
        self.reader.clear_message()
        try:
            self.reader.validate_message('\x00\x00\x00\x00', 4)
            assert False, "Validation held with packet being too small"
        except:
            assert True

    def test_validation_fail(self):
        self.reader.clear_message()
        message = '\x00' + '\x00\x00\x00\x01' + '\x00'
        message += '\xff\xff\x01\xC2'
        assert self.reader.validate_message(message, len(message)) == False, \
              "Validation passed with incorrect message"
            
    def test_validation_except(self):
        self.reader.clear_message()
        try:
            self.reader.validate_message('\x00\x00\x00\x00\x00\x00\x00', 7)
            assert False, "Validation held with packet being not correct"
        except:
            assert True
            
    def test_read(self):
        self.reader.clear_message()
        self.builder.new_message('CompletePingCheck')
        self.builder.next_block('PingID')
        self.builder.add_data('PingID', 0x01, MsgType.MVT_U8)
        message, size = self.builder.build_message()
        message = '\x00' + '\x00\x00\x00\x01' + '\x00' + message
        size = len(message)
        assert self.reader.validate_message(message, size), "Validation failed for test_read"
        assert self.reader.read_message(message), "Read failed"
        assert self.reader.get_data('PingID', 'PingID', MsgType.MVT_U8) == 1, \
               "Read error: PingID incorrect"
        
    def test_read_fail(self):
        self.reader.clear_message()
        self.builder.new_message('CompletePingCheck')
        self.builder.next_block('PingID')
        self.builder.add_data('PingID', 0x01, MsgType.MVT_U8)
        message, size = self.builder.build_message()
        message = '\x00' + '\x00\x00\x00\x01' + '\x00' + message
        size = len(message)
        try:
            self.reader.read_message(message)
            assert False, "Message read without being validated"
        except:
            assert True
        
    def test_read_no_validate(self):
        self.reader.clear_message()
        message = '\x00' + '\x00\x00\x00\x01' + '\x00' + 'Sweetmessage'

        try:
            assert self.reader.receive_size == -1, "Receive size incorrect"
            self.reader.get_data('CompletePingCheck', 'PingID', MsgType.MVT_U8)
            assert False, "Got data without having one read"
        except:
            assert True

        assert self.reader.validate_message(message, 10) == False, \
               "Invalid message determined valid"

        try:
            self.reader.get_data('CompletePingCheck', 'PingID', MsgType.MVT_U8)
            assert self.reader.receive_size != -1, "Receive size incorrect, should not be -1"
            assert False, "Able to get data without having a valid template"
        except:
            assert True


    def test_read_read(self):
        self.reader.clear_message()
        self.builder.new_message('CompletePingCheck')
        self.builder.next_block('PingID')
        self.builder.add_data('PingID', 0x01, MsgType.MVT_U8)
        message, size = self.builder.build_message()
        message = '\x00' + '\x00\x00\x00\x01' + '\x00' + message
        size = len(message)
        self.reader.validate_message(message, size)
        self.reader.read_message(message)
        #attempt to read it again without clearing
        assert self.reader.read_message(message), "Read should work without clearing"

    def test_read_variable(self):
        self.builder.new_message('PacketAck')
        self.builder.next_block('Packets')
        self.builder.add_data('ID', 0x00000001, MsgType.MVT_U32)
        self.builder.next_block('Packets')
        self.builder.add_data('ID', 0x00000001, MsgType.MVT_U32)
        self.builder.next_block('Packets')
        self.builder.add_data('ID', 0x00000001, MsgType.MVT_U32)
        message, size = self.builder.build_message()
        message = '\x00' + '\x00\x00\x00\x01' + '\x00' + message
        size = len(message)

        assert self.reader.validate_message(message, size), \
               "Variable block not valid"
        
        self.reader.read_message(message)

        assert self.reader.get_data('Packets', 'ID', MsgType.MVT_U32) == 0x00000001,\
            "Packets block ID not read from data"
        assert self.reader.get_data('Packets', 'ID', MsgType.MVT_U32, 1) == 0x00000001,\
            "Packets block 1 ID not read from data"
        assert self.reader.get_data('Packets', 'ID', MsgType.MVT_U32, 2) == 0x00000001,\
            "Packets block 2 ID not read from data"

    def test_read_multiple(self):
        self.builder.new_message('TestMessage')
        self.builder.next_block('TestBlock1')
        self.builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        self.builder.next_block('NeighborBlock')
        self.builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        self.builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        self.builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        self.builder.next_block('NeighborBlock')
        self.builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        self.builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        self.builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        self.builder.next_block('NeighborBlock')
        self.builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        self.builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        self.builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        self.builder.next_block('NeighborBlock')
        self.builder.add_data('Test0', 0x00000001, MsgType.MVT_U32)
        self.builder.add_data('Test1', 0x00000001, MsgType.MVT_U32)
        self.builder.add_data('Test2', 0x00000001, MsgType.MVT_U32)
        message, size = self.builder.build_message()
        message = '\x00' + '\x00\x00\x00\x01' + '\x00' + message
        size = len(message)
        assert self.reader.validate_message(message, size), "Multiple invalid"
        assert self.reader.read_message(message), "Multiple read fail"

        assert self.reader.get_data('TestBlock1', 'Test1', MsgType.MVT_U32) == 0x00000001,\
            "Test block not read from data"
        
        assert self.reader.get_data('NeighborBlock', 'Test0', MsgType.MVT_U32) == 0x00000001,\
            "NeightborBlock test0 not read from data"
        assert self.reader.get_data('NeighborBlock', 'Test1', MsgType.MVT_U32) == 0x00000001,\
            "NeightborBlock test1 not read from data"
        assert self.reader.get_data('NeighborBlock', 'Test2', MsgType.MVT_U32) == 0x00000001,\
            "Test block test2 not read from data"
        
        assert self.reader.get_data('NeighborBlock', 'Test0', MsgType.MVT_U32, 1) == 0x00000001,\
            "NeightborBlock 1 test0 not read from data"
        assert self.reader.get_data('NeighborBlock', 'Test1', MsgType.MVT_U32, 1) == 0x00000001,\
            "NeightborBlock 1 test1 not read from data"
        assert self.reader.get_data('NeighborBlock', 'Test2', MsgType.MVT_U32, 1) == 0x00000001,\
            "NeightborBlock 1 test2 not read from data"
        
        assert self.reader.get_data('NeighborBlock', 'Test0', MsgType.MVT_U32, 2) == 0x00000001,\
            "NeightborBlock 2 test0 not read from data"
        assert self.reader.get_data('NeighborBlock', 'Test1', MsgType.MVT_U32, 2) == 0x00000001,\
            "NeightborBlock 2 test1 not read from data"
        assert self.reader.get_data('NeighborBlock', 'Test2', MsgType.MVT_U32, 2) == 0x00000001,\
            "NeightborBlock 2 test2 not read from data"

        assert self.reader.get_data('NeighborBlock', 'Test0', MsgType.MVT_U32, 3) == 0x00000001,\
            "NeightborBlock 2 test0 not read from data"
        assert self.reader.get_data('NeighborBlock', 'Test1', MsgType.MVT_U32, 3) == 0x00000001,\
            "NeightborBlock 2 test1 not read from data"
        assert self.reader.get_data('NeighborBlock', 'Test2', MsgType.MVT_U32, 3) == 0x00000001,\
            "NeightborBlock 2 test2 not read from data"

        #some fail cases
        try:
            self.reader.get_data('NeighborBlock', 'Test0', MsgType.MVT_U32, 4)
            assert False, "Non-existing block read"
        except:
            assert True
        assert self.reader.get_data('NeighborBlock', 'Test1', MsgType.MVT_U8, 3) == None,\
            "NeightborBlock mismatch type still works, not supposed to"
        assert self.reader.get_data('NeighborBlock', 'Test2', MsgType.MVT_U32, 3) == 0x00000001,\
            "NeightborBlock 2 test2 not read from data"

    def test_read_var(self):
        self.builder.new_message('UpdateSimulator')
        self.builder.next_block('SimulatorInfo')
        self.builder.add_data('RegionID', UUID("550e8400-e29b-41d4-a716-446655440000"), MsgType.MVT_LLUUID)
        self.builder.add_data('SimName', "Testing", MsgType.MVT_VARIABLE)
        self.builder.add_data('EstateID', 0x00000001, MsgType.MVT_U32)
        self.builder.add_data('SimAccess', 0x01, MsgType.MVT_U8)
        message, size = self.builder.build_message()
        message = '\x00' + '\x00\x00\x00\x01' + '\x00' + message
        size = len(message)
        assert self.reader.validate_message(message, size), "Variable invalid"
        assert self.reader.read_message(message), "Variable read fail"

        assert self.reader.get_data('SimulatorInfo', 'SimName', MsgType.MVT_VARIABLE) == "Testing",\
            "SimName variable not read correctly"


    def test_read_var2(self):
        self.builder.new_message('TeleportFinish')
        self.builder.next_block('Info')
        self.builder.add_data('AgentID', UUID("550e8400-e29b-41d4-a716-446655440000"), MsgType.MVT_LLUUID)
        self.builder.add_data('LocationID', 0x00000001, MsgType.MVT_U32)
        self.builder.add_data('SimIP', '.com', MsgType.MVT_IP_ADDR)
        self.builder.add_data('SimPort', 80, MsgType.MVT_IP_PORT)        
        self.builder.add_data('RegionHandle', 0x0000000000000001, MsgType.MVT_U64)
        self.builder.add_data('SeedCapability', "Testing", MsgType.MVT_VARIABLE)
        self.builder.add_data('SimAccess', 0x01, MsgType.MVT_U8)
        self.builder.add_data('TeleportFlags', 0x00000001, MsgType.MVT_U32)
        message, size = self.builder.build_message()
        message = '\x00' + '\x00\x00\x00\x01' + '\x00' + message
        size = len(message)
        assert self.reader.validate_message(message, size), "Variable invalid"
        assert self.reader.read_message(message), "Variable read fail"

        assert self.reader.get_data('Info', 'SeedCapability', MsgType.MVT_VARIABLE) == "Testing",\
            "TeleportFinish variable not read correctly"        
        assert self.reader.get_data('Info', 'SimPort', MsgType.MVT_IP_PORT) == 80,\
            "TeleportFinish variable not read correctly"        

    def test_read_medium(self):
        self.builder.new_message('ConfirmEnableSimulator')
        self.builder.next_block('AgentData')
        self.builder.add_data('AgentID', UUID("550e8400-e29b-41d4-a716-446655440000"), MsgType.MVT_LLUUID)
        self.builder.add_data('SessionID', UUID("550e8400-e29b-41d4-a716-446655440000"), MsgType.MVT_LLUUID)
        message, size = self.builder.build_message()
        message = '\x00' + '\x00\x00\x00\x01' + '\x00' + message
        size = len(message)
        
        assert self.reader.validate_message(message, size), "Variable invalid"
        assert self.reader.read_message(message), "Variable read fail"

    def test_get_bad_data(self):
        self.reader.clear_message()
        self.builder.new_message('CompletePingCheck')
        self.builder.next_block('PingID')
        self.builder.add_data('PingID', 0x01, MsgType.MVT_U8)
        message, size = self.builder.build_message()
        message = '\x00' + '\x00\x00\x00\x01' + '\x00' + message
        size = len(message)
        self.reader.validate_message(message, size)
        self.reader.read_message(message)
        try:
            self.reader.get_data('BADBLOCK', 'PingID', MsgType.MVT_U8)
            assert False, "Got non-existent block"
        except:
            assert True
        try:
            self.reader.get_data('PingID', 'PingID', MsgType.MVT_U8, 1)
            assert False, "Got non-existent block num"
        except:
            assert True
        try:
            self.reader.get_data('PingID', 'BADDATA', MsgType.MVT_U8)
            assert False, "Got non-existent data"
        except:
            assert True
         
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplateReader))
    return suite
