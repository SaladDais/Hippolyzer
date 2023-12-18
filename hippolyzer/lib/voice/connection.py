# TODO: some fancy parser that parses everything into
#  dicts or objects using schemas.
from __future__ import annotations

import asyncio
import weakref
from typing import Any, Optional, Coroutine, NamedTuple

import defusedxml.lxml
import lxml.etree


class VivoxMessage(NamedTuple):
    type: str
    name: str
    request_id: Optional[str]
    data: dict


def xml_to_dict(element):
    return element.tag, dict(map(xml_to_dict, element)) or element.text


def buildxml(r, d, list_elem_name='i'):
    if isinstance(d, dict):
        for k, v in d.items():
            s = lxml.etree.SubElement(r, k)
            buildxml(s, v, list_elem_name)
    elif isinstance(d, (list, tuple, set)):
        for v in d:
            if isinstance(v, lxml.etree._Element):  # noqa
                s = r
            else:
                s = lxml.etree.SubElement(r, list_elem_name)
            buildxml(s, v, list_elem_name)
    elif isinstance(d, str):
        r.text = d
    elif isinstance(d, lxml.etree._Element):  # noqa
        r.append(d)
    elif d is None:
        r.text = ""
    else:
        r.text = str(d)
    return r


_VIVOX_NS = b' xmlns="http://www.vivox.com"'  # noqa


def _remove_vivox_ns(data):
    return data.replace(_VIVOX_NS, b"").strip()


def _clean_message(msg_action: str, parsed, dict_msg: dict):
    # TODO: refactor this into some XML -> dict schema, some XML is ambiguous
    if msg_action == "Aux.GetCaptureDevices.1":
        devices = []
        for device in parsed.find('Results/CaptureDevices'):
            devices.append(xml_to_dict(device)[1])
        dict_msg["Results"]["CaptureDevices"] = devices
    if msg_action == "Account.WebCall.1":
        results = dict_msg["Results"]
        content_type = results.get("ContentType") or ""
        if content_type.startswith("text/xml"):
            xml_content = _remove_vivox_ns(results["Content"].encode("utf8"))
            parsed_content = defusedxml.lxml.fromstring(xml_content)
            body = parsed_content.xpath("//body")[0]
            results["Content"] = body
    if "ReturnCode" in dict_msg:
        dict_msg["ReturnCode"] = int(dict_msg["ReturnCode"])
    return dict_msg


def _build_webcall_params(params: dict) -> list:
    params_list = []
    elem = lxml.etree.Element('base')
    for name, val in params.items():
        params_list.append({"Name": name, "Value": val})
    buildxml(elem, params_list, 'Parameter')
    return list(elem)


class VivoxConnection:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, owned=True):
        self._reader: Optional[asyncio.StreamReader] = reader
        self._writer: Optional[asyncio.StreamWriter] = writer
        self._owned = owned

    def close(self):
        if self._owned and self._writer:
            self._writer.close()
        self._writer = None
        self._reader = None

    def __del__(self):
        self.close()

    async def read_messages(self):
        # TODO: handle interrupted read
        while self._reader and not self._reader.at_eof() and not self._writer.is_closing():
            yield await self.read_message()

    async def read_message(self):
        msg = await self._reader.readuntil(b"\n\n\n")
        return self.parse(msg[:-3])

    def parse(self, raw_msg) -> VivoxMessage:
        parsed_msg = defusedxml.lxml.fromstring(raw_msg.decode("utf8"))
        msg_type = parsed_msg.tag
        request_id = parsed_msg.attrib.get("requestId", None)

        # There may be no params, just use an empty dict if that's the case
        dict_msg = xml_to_dict(parsed_msg)[1] or {}

        if msg_type == "Event":
            msg_action = parsed_msg.attrib.get("type")
        elif msg_type == "Response":
            msg_action = parsed_msg.attrib.get("action")
            # This is pretty useless, get rid of it because it gunks up repr()s.
            if 'InputXml' in dict_msg:
                del dict_msg['InputXml']
            dict_msg = _clean_message(msg_action, parsed_msg, dict_msg)
        elif msg_type == "Request":
            msg_action = parsed_msg.attrib.get("action")
        else:
            raise Exception("Unknown Vivox message type %r?" % msg_type)
        return VivoxMessage(msg_type, msg_action, request_id, dict_msg)

    def send_raw(self, buf: bytes) -> Coroutine[Any, Any, None]:
        self._writer.write(buf + b"\n\n\n")
        drain_coro = self._writer.drain()
        # Don't whine if this isn't awaited, we may not always want to flush immediately.
        weakref.finalize(drain_coro, drain_coro.close)
        return drain_coro

    def send_request(self, request_id: str, action: str, data: Any) -> Coroutine[Any, Any, None]:
        if action == "Account.WebCall.1":
            data = dict(data)
            data["Parameters"] = _build_webcall_params(data["Parameters"])
        return self._send_request_response("Request", request_id, action, data)

    def send_response(self, request_id: str, action: str, data: Any) -> Coroutine[Any, Any, None]:
        return self._send_request_response("Response", request_id, action, data)

    def _send_request_response(self, msg_type: str, request_id: str, action: str, data: Any):
        elem = lxml.etree.Element(msg_type)
        elem.attrib["requestId"] = request_id
        elem.attrib["action"] = action
        serialized = lxml.etree.tostring(buildxml(elem, data))
        return self.send_raw(serialized)

    def send_event(self, event_type: str, data: Any) -> Coroutine[Any, Any, None]:
        elem = lxml.etree.Element("Event")
        elem.attrib["type"] = event_type
        serialized = lxml.etree.tostring(buildxml(elem, data))
        return self.send_raw(serialized)
