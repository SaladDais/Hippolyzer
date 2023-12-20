from typing import NamedTuple, List, Sequence

from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.templates import ChatType


class RLVCommand(NamedTuple):
    behaviour: str
    param: str
    options: List[str]


class RLVParser:
    @staticmethod
    def is_rlv_message(msg: Message) -> bool:
        chat: str = msg["ChatData"]["Message"]
        chat_type: int = msg["ChatData"]["ChatType"]
        return chat and chat.startswith("@") and chat_type == ChatType.OWNER

    @staticmethod
    def parse_chat(chat: str) -> List[RLVCommand]:
        assert chat.startswith("@")
        chat = chat.lstrip("@")
        commands = []
        for command_str in chat.split(","):
            if not command_str:
                continue
            # RLV-style command, `<cmd>(:<option1>;<option2>)?(=<param>)?`
            # Roughly (?<behaviour>[^:=]+)(:(?<option>[^=]*))?=(?<param>\w+)
            options, _, param = command_str.partition("=")
            behaviour, _, options = options.partition(":")
            # TODO: Not always correct, commands can specify their own parsing for the option field
            #  maybe special-case these?
            options = options.split(";") if options else []
            commands.append(RLVCommand(behaviour, param, options))
        return commands

    @staticmethod
    def format_chat(commands: Sequence[RLVCommand]) -> str:
        assert commands
        chat = ""
        for command in commands:
            if chat:
                chat += ","

            chat += command.behaviour
            if command.options:
                chat += ":" + ";".join(command.options)
            if command.param:
                chat += "=" + command.param
        return "@" + chat
