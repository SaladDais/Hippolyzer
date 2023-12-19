"""
Connect to a voice session at 0, 0, 0 for 20 seconds, then exit.
"""

import asyncio
from contextlib import aclosing
import os

from hippolyzer.lib.base.datatypes import Vector3
from hippolyzer.lib.voice.client import VoiceClient


VOICE_PATH = os.environ["SLVOICE_PATH"]


async def amain():
    client = await VoiceClient.simple_init(VOICE_PATH)
    async with aclosing(client):
        print("Capture Devices:", client.capture_devices)
        print("Render Devices:", client.render_devices)
        await client.set_mic_muted(True)
        await client.set_mic_volume(60)
        print(await client.login(os.environ["SLVOICE_USERNAME"], os.environ["SLVOICE_PASSWORD"]))

        await client.join_session(os.environ["SLVOICE_URI"], int(os.environ["SLVOICE_HANDLE"]))

        await client.set_region_3d_pos(Vector3(0, 0, 0))
        print(client.region_pos)

        # leave running for 20 seconds, then exit
        await asyncio.sleep(20.0)
        print("Bye!")


if __name__ == "__main__":
    asyncio.run(amain())
