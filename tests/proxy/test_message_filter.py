import unittest

from mitmproxy.test import tflow, tutils

from hippolyzer.lib.base.datatypes import Vector3, UUID
from hippolyzer.lib.base.message.message import Block, Message as Message
from hippolyzer.lib.base.message.udpdeserializer import UDPMessageDeserializer
from hippolyzer.lib.base.settings import Settings
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.proxy.caps import SerializedCapData
from hippolyzer.lib.proxy.message_logger import LLUDPMessageLogEntry, HTTPMessageLogEntry, export_log_entries, \
    import_log_entries
from hippolyzer.lib.proxy.message_filter import compile_filter
from hippolyzer.lib.proxy.sessions import SessionManager
from hippolyzer.lib.proxy.settings import ProxySettings

OBJECT_UPDATE = b'\xc0\x00\x00\x00Q\x00\x0c\x00\x01\xea\x03\x00\x02\xe6\x03\x00\x01\xbe\xff\x01\x06\xbc\x8e\x0b\x00' \
                b'\x01i\x94\x8cjM"\x1bf\xec\xe4\xac1c\x93\xcbKW\x89\x98\x01\t\x03\x00\x01Q@\x88>Q@\x88>Q@\x88><\xa2D' \
                b'\xb3B\x9ah+B\xc8[\xd1A\x00\x18K\x8c\xff>\xbdv\xff\xbe\xc5D\x00\x01\xbf\x00\x10P\x04\x00\x01\x10 ' \
                b'\x05\x00\x04dd\x00\x0f.\x00\x01\xa13\xdcw\n\x1a\xbb\'\xa7.xdc\xab\x94\xab\x00\x08\x80?\x00\x03\x80' \
                b'?\x00\x0f\x10\x13\xff\x00\x08\x80?\x8f\xc2\xf5=\x00\nVoC\xcc\x00\x01\x02\x00\x03\x04\x00\x02\x04' \
                b'\x00\x02d&\x00\x03\x0e\x00\x01\x0e\x00\x01\x19\x00\x01\x80\x00\x01\x80\x00\x01\x80\x00\x01\x80\x00' \
                b'\x01\x80\x00\x01\x80\x91\x11\xd2^/\x12\x8f\x81U\xa7@:x\xb3\x0e-\x00\x10\x03\x01\x00\x03\x1e%n\xa2' \
                b'\xff\xc5\xe0\x83\x00\x01\x06\x00\x01\r\r\x01\x00\x11\x0e\xdc\x9b\x83\x98\x9aJv\xac\xc3\xdb\xbf7Ta' \
                b'\x88\x00"'


class MessageFilterTests(unittest.IsolatedAsyncioTestCase):
    def _filter_matches(self, filter_str, message):
        compiled = compile_filter(filter_str)
        return compiled.match(message)

    def test_basic(self):
        msg = LLUDPMessageLogEntry(Message(name="Bar"), None, None)
        self.assertFalse(self._filter_matches("Foo", msg))
        msg.message.name = "Foo"
        self.assertTrue(self._filter_matches("Foo", msg))

    def test_unary_not(self):
        msg = LLUDPMessageLogEntry(Message(name="Bar"), None, None)
        self.assertTrue(self._filter_matches("!Foo", msg))
        msg.message.name = "Foo"
        self.assertFalse(self._filter_matches("!Foo", msg))

    def test_or(self):
        msg = LLUDPMessageLogEntry(Message(name="Bar"), None, None)
        self.assertTrue(self._filter_matches("(Foo || Bar)", msg))
        msg.message.name = "Baz"
        self.assertFalse(self._filter_matches("(Foo || Bar)", msg))

    def test_equality(self):
        msg = LLUDPMessageLogEntry(Message("Foo", Block("Bar", Baz=1)), None, None)
        self.assertTrue(self._filter_matches("Foo.Bar.Baz == 1", msg))
        self.assertTrue(self._filter_matches("Foo.Bar.Baz == 0x1", msg))
        msg.message["Bar"]["Baz"] = 2
        self.assertFalse(self._filter_matches("Foo.Bar.Baz == 1", msg))
        self.assertFalse(self._filter_matches("Foo.Bar.Baz == 0x1", msg))

    def test_and(self):
        msg = LLUDPMessageLogEntry(Message("Foo", Block("Bar", Baz=1)), None, None)
        self.assertTrue(self._filter_matches("Foo && Foo.Bar.Baz == 1", msg))
        self.assertFalse(self._filter_matches("Bar && Foo.Bar.Baz == 1", msg))

    def test_meta_equality(self):
        msg = Message("Foo", Block("Bar", Baz=1))
        msg.meta["AgentLocal"] = 2
        entry = LLUDPMessageLogEntry(msg, None, None)
        self.assertFalse(self._filter_matches("Foo.Bar.Baz == Meta.AgentLocal", entry))
        entry.message["Bar"]["Baz"] = 2
        self.assertTrue(self._filter_matches("Foo.Bar.Baz == Meta.AgentLocal", entry))

    def test_meta_truthy(self):
        msg = Message("Foo", Block("Bar", Baz=1))
        msg.meta["Quux"] = 2
        entry = LLUDPMessageLogEntry(msg, None, None)
        self.assertTrue(self._filter_matches("Meta.Quux", entry))
        self.assertFalse(self._filter_matches("!Meta.Quux", entry))
        del msg.meta["Quux"]
        self.assertFalse(self._filter_matches("Meta.Quux", entry))
        self.assertTrue(self._filter_matches("!Meta.Quux", entry))

    def test_meta_not(self):
        msg = Message("Foo", Block("Bar", Baz=1))
        msg.meta["AgentID"] = "foo"
        entry = LLUDPMessageLogEntry(msg, None, None)
        self.assertFalse(self._filter_matches("Meta.AgentID == None", entry))
        self.assertTrue(self._filter_matches("Meta.AgentID != None", entry))

    def test_vector_equality(self):
        msg = LLUDPMessageLogEntry(Message("Foo", Block("Bar", Baz=(0, 1, 0))), None, None)
        self.assertTrue(self._filter_matches("Foo.Bar.Baz == (0, 1, 0)", msg))
        msg.message["Bar"]["Baz"] = (0, 2, 0)
        self.assertFalse(self._filter_matches("Foo.Bar.Baz == (0, 1, 0)", msg))

    def test_vector_gt(self):
        msg = LLUDPMessageLogEntry(Message("Foo", Block("Bar", Baz=Vector3(0, 0, 0))), None, None)
        self.assertTrue(self._filter_matches("Foo.Bar.Baz < (1, 1, 1)", msg))
        self.assertFalse(self._filter_matches("Foo.Bar.Baz > (0, 1, 0)", msg))
        msg.message["Bar"]["Baz"] = Vector3(2, 2, 2)
        self.assertFalse(self._filter_matches("Foo.Bar.Baz < (0, 0, 0)", msg))
        # Must be greater on all axes
        self.assertFalse(self._filter_matches("Foo.Bar.Baz < (0, 3, 0)", msg))
        self.assertTrue(self._filter_matches("Foo.Bar.Baz > (0, 0, 0)", msg))

    def test_enum_specifier(self):
        # 2 is the enum val for SculptType.TORUS
        msg = LLUDPMessageLogEntry(Message("Foo", Block("Bar", Baz=2)), None, None)
        self.assertTrue(self._filter_matches("Foo.Bar.Baz == SculptType.TORUS", msg))
        # bitwise AND should work as well
        self.assertTrue(self._filter_matches("Foo.Bar.Baz & SculptType.TORUS", msg))
        self.assertFalse(self._filter_matches("Foo.Bar.Baz == SculptType.SPHERE", msg))

    def test_tagged_union_subfield(self):
        settings = Settings()
        settings.ENABLE_DEFERRED_PACKET_PARSING = False
        deser = UDPMessageDeserializer(settings=settings)
        update_msg = deser.deserialize(OBJECT_UPDATE)
        entry = LLUDPMessageLogEntry(update_msg, None, None)
        self.assertTrue(self._filter_matches("ObjectUpdate.ObjectData.ObjectData.Position > (88, 41, 25)", entry))
        self.assertTrue(self._filter_matches("ObjectUpdate.ObjectData.ObjectData.Position < (90, 43, 27)", entry))

    def test_import_export_message(self):
        msg = LLUDPMessageLogEntry(Message(
            "Foo",
            Block("Bar", Baz=1, Quux=UUID.random(), Foo=0xFFffFFffFF)
        ), None, None)
        msg.freeze()
        msg = import_log_entries(export_log_entries([msg]))[0]
        self.assertTrue(self._filter_matches("Foo.Bar.Baz == 1", msg))
        # Make sure numbers outside 32bit range come through
        self.assertTrue(self._filter_matches("Foo.Bar.Foo == 0xFFffFFffFF", msg))

    async def test_http_flow(self):
        session_manager = SessionManager(ProxySettings())
        fake_flow = tflow.tflow(req=tutils.treq(), resp=tutils.tresp())
        fake_flow.metadata["cap_data_ser"] = SerializedCapData(
            cap_name="FakeCap",
        )
        flow = HippoHTTPFlow.from_state(fake_flow.get_state(), session_manager)
        entry = HTTPMessageLogEntry(flow)
        self.assertTrue(self._filter_matches("FakeCap", entry))
        self.assertFalse(self._filter_matches("NotFakeCap", entry))

    async def test_http_header_filter(self):
        session_manager = SessionManager(ProxySettings())
        fake_flow = tflow.tflow(req=tutils.treq(), resp=tutils.tresp())
        fake_flow.request.headers["Cookie"] = 'foo="bar"'
        flow = HippoHTTPFlow.from_state(fake_flow.get_state(), session_manager)
        entry = HTTPMessageLogEntry(flow)
        # The header map is case-insensitive!
        self.assertTrue(self._filter_matches('Meta.ReqHeaders.cookie ~= "foo"', entry))
        self.assertFalse(self._filter_matches('Meta.ReqHeaders.foobar ~= "foo"', entry))

    async def test_export_import_http_flow(self):
        fake_flow = tflow.tflow(req=tutils.treq(), resp=tutils.tresp())
        fake_flow.metadata["cap_data_ser"] = SerializedCapData(
            cap_name="FakeCap",
        )
        flow = HippoHTTPFlow.from_state(fake_flow.get_state(), None)
        new_entry = import_log_entries(export_log_entries([HTTPMessageLogEntry(flow)]))[0]
        self.assertEqual("FakeCap", new_entry.name)
