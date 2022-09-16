"""
Simple stub for testing receiving inbound LEAP connections over TCP

To be removed at some point once this is supported by the proxy itself.
"""

import asyncio
import logging
import multiprocessing
import pprint

from hippolyzer.lib.proxy.leap import LEAPBridgeServer, LEAPClient


async def client_connected(client: LEAPClient):
    # Not awaiting is totally ok if you don't care about the response,
    # but your linter may complain.
    await client.sys_command("ping")

    # For each API supported by the viewer
    for api in await client.sys_command("getAPIs"):
        print("=" * 5, api, "=" * 5)
        # List supported OPs
        pprint.pprint(await client.sys_command("getAPI", {"api": api}))


def receiver_main():
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()

    server = LEAPBridgeServer(client_connected)
    coro = asyncio.start_server(server.handle_connection, "127.0.0.1", 9063)
    loop.run_until_complete(coro)
    loop.run_forever()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    receiver_main()
