"""
A simple client that just says hello to people
"""

import asyncio
from contextlib import aclosing
import os

from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.templates import ChatType, ChatSourceType
from hippolyzer.lib.client.hippo_client import HippoClient


async def amain():
    client = HippoClient()

    async def _respond_to_chat(message: Message):
        if message["ChatData"]["SourceID"] == client.session.agent_id:
            return
        if message["ChatData"]["SourceType"] != ChatSourceType.AGENT:
            return
        if "hello" not in str(message["ChatData"]["Message"]).lower():
            return
        await client.session.main_region.circuit.send_reliable(
            Message(
                "ChatFromViewer",
                Block("AgentData", SessionID=client.session.id, AgentID=client.session.agent_id),
                Block("ChatData", Message=f'Hello {message["ChatData"]["FromName"]}!', Channel=0, Type=ChatType.SHOUT),
            )
        )

    async with aclosing(client):
        await client.login(
            username=os.environ["HIPPO_USERNAME"],
            password=os.environ["HIPPO_PASSWORD"],
            start_location=os.environ.get("HIPPO_START_LOCATION", "home"),
        )
        print("I'm here")
        await client.session.main_region.circuit.send_reliable(
            Message(
                "ChatFromViewer",
                Block("AgentData", SessionID=client.session.id, AgentID=client.session.agent_id),
                Block("ChatData", Message="Hello World!", Channel=0, Type=ChatType.SHOUT),
            )
        )
        client.session.message_handler.subscribe("ChatFromSimulator", _respond_to_chat)
        while True:
            try:
                await asyncio.sleep(0.001)
            except (KeyboardInterrupt, asyncio.CancelledError):
                await client.session.main_region.circuit.send_reliable(
                    Message(
                        "ChatFromViewer",
                        Block("AgentData", SessionID=client.session.id, AgentID=client.session.agent_id),
                        Block("ChatData", Message="Goodbye World!", Channel=0, Type=ChatType.SHOUT),
                    )
                )
                return

if __name__ == "__main__":
    asyncio.run(amain())
