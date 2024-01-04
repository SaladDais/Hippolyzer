"""
A simple client that just says hello to people
"""

import asyncio
import pprint
from contextlib import aclosing
import os

from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.templates import ChatType, ChatSourceType
from hippolyzer.lib.client.hippo_client import HippoClient


async def amain():
    client = HippoClient()

    async def _respond_to_chat(message: Message):
        if message["ChatData"]["SourceID"] == client.session.agent_id:
            return
        if message["ChatData"]["SourceType"] != ChatSourceType.AGENT:
            return
        if "hello" not in message["ChatData"]["Message"].lower():
            return
        await client.send_chat(f'Hello {message["ChatData"]["FromName"]}!', chat_type=ChatType.SHOUT)

    async with aclosing(client):
        await client.login(
            username=os.environ["HIPPO_USERNAME"],
            password=os.environ["HIPPO_PASSWORD"],
            start_location=os.environ.get("HIPPO_START_LOCATION", "last"),
        )
        print("I'm here")

        # Wait until we have details about parcels and print them
        await client.main_region.parcel_manager.parcels_downloaded.wait()
        pprint.pprint(client.main_region.parcel_manager.parcels)

        await client.send_chat("Hello World!", chat_type=ChatType.SHOUT)
        client.session.message_handler.subscribe("ChatFromSimulator", _respond_to_chat)
        # Example of how to work with caps
        async with client.main_caps_client.get("SimulatorFeatures") as features_resp:
            print("Features:", await features_resp.read_llsd())

        while True:
            try:
                await asyncio.sleep(0.001)
            except (KeyboardInterrupt, asyncio.CancelledError):
                await client.send_chat("Goodbye World!", chat_type=ChatType.SHOUT)
                return

if __name__ == "__main__":
    asyncio.run(amain())
