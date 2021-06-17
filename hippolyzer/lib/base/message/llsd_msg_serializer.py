import copy
from typing import *

from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.message.data_packer import LLSDDataPacker
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.message.template import MessageTemplateVariable
from hippolyzer.lib.base.message.template_dict import TemplateDictionary, DEFAULT_TEMPLATE_DICT

VAR_PAIR = Tuple[dict, MessageTemplateVariable]


class LLSDMessageSerializer:
    DEFAULT_TEMPLATE = DEFAULT_TEMPLATE_DICT

    def __init__(self, message_template=None, message_cls: Type[Message] = Message):
        if message_template is not None:
            self.template_dict = TemplateDictionary(message_template=message_template)
        else:
            self.template_dict = self.DEFAULT_TEMPLATE
        self._message_cls = message_cls

    def _yield_vars(self, msg_dict: dict) -> Generator[VAR_PAIR, None, None]:
        # Things that deserialize to distinct types already have
        # defined serializers in LLSD, but for some types we need
        # to look at the template to figure out how to pack them.
        # See U64, IPADDR and friends.
        template = self.template_dict.get_template_by_name(msg_dict['message'])
        for tmpl_block in template.blocks:
            for block in msg_dict['body'].get(tmpl_block.name, ()):
                for tmpl_var in tmpl_block.variables:
                    if tmpl_var.type in LLSDDataPacker.SPECS:
                        yield block, tmpl_var

    def can_handle(self, msg_name: str):
        return msg_name in self.template_dict

    def serialize(self, msg: Message, as_dict=False) -> dict:
        msg_dict = msg.to_dict()
        for block, tmpl_var in self._yield_vars(msg_dict):
            val = block[tmpl_var.name]
            block[tmpl_var.name] = LLSDDataPacker.pack(val, tmpl_var.type)
        if as_dict:
            return msg_dict
        return llsd.format_xml(msg_dict)

    def deserialize(self, llsd_val: Union[dict, bytes]) -> Message:
        if isinstance(llsd_val, bytes):
            llsd_val = llsd.parse(llsd_val)
        else:
            llsd_val = copy.deepcopy(llsd_val)
        if not isinstance(llsd_val, dict):
            raise ValueError(f"Bad LLSD message: {llsd_val!r}")

        for block, tmpl_var in self._yield_vars(llsd_val):
            val = block[tmpl_var.name]
            block[tmpl_var.name] = LLSDDataPacker.unpack(val, tmpl_var.type)
        return self._message_cls.from_dict(llsd_val)
