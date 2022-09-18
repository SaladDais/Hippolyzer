"""
Simple stub for testing receiving inbound LEAP connections over TCP

To be removed at some point once this is supported by the proxy itself.
"""

import asyncio
import logging
import multiprocessing
import pprint

from hippolyzer.lib.proxy.leap import LEAPBridgeServer, LEAPClient, LLWindowWrapper, UIPath, LLUIWrapper


async def client_connected(client: LEAPClient):
    # Kick off a request to get ops for each API supported by the viewer
    # Won't wait for a response from the viewer between each send
    api_futs = {}
    for api_name in (await client.sys_command("getAPIs")).keys():
        api_fut = client.sys_command("getAPI", {"api": api_name})
        api_futs[api_fut] = api_name

    # Wait for all of our commands to complete in parallel
    for fut in (await asyncio.wait(api_futs.keys()))[0]:
        # Figure out which API this future even relates to
        print("=" * 5, api_futs[fut], "=" * 5)
        # List supported ops for this api
        pprint.pprint(await fut)

    # Subscribe to StartupState events within this scope
    async with client.listen_scoped("StartupState") as get_event:
        # Get a single StartupState event then continue
        pprint.pprint(await get_event())

    # More manual version of above that gives you a Queue you can pass around
    # A None gets posted to the mainloop every time the viewer restarts the main loop,
    # so we can rely on _something_ being published to this.
    llapp_queue = await client.listen("mainloop")
    try:
        pprint.pprint(await llapp_queue.get())
        llapp_queue.task_done()
    finally:
        await client.stop_listening(llapp_queue)

    # A simple command with a reply
    pprint.pprint(await client.command("LLFloaterReg", "getBuildMap"))

    # A simple command that has no reply, or has a reply we don't care about.
    client.void_command("LLFloaterReg", "showInstance", {"name": "preferences"})

    # Some commands must be executed against the dynamically assigned command
    # pump that's specific to our LEAP listener. `sys_command()` is the same as
    # `command()` except it internally addresses whatever the system command pump is.
    await client.sys_command("ping")

    # Spawn the test textbox floater
    client.void_command("LLFloaterReg", "showInstance", {"name": "test_textbox"})

    window_api = LLWindowWrapper(client)

    # LEAP allows addressing UI elements by "path". We expose that through a pathlib-like interface
    # to allow composing UI element paths.
    textbox_path = UIPath.for_floater("floater_test_textbox") / "long_text_editor"
    # Click the "long_text_editor" in the test textbox floater.
    await window_api.mouse_click(button="LEFT", path=textbox_path)

    # Type some text in it
    window_api.text_input("Also I can type in here pretty good.")

    # Print out the value of the textbox we just typed in
    ui_api = LLUIWrapper(client)
    pprint.pprint(await ui_api.get_value(textbox_path))

    # But you don't need to explicitly give input focus like above, you can send keypresses
    # directly to a path.
    # TODO: clearing a textbox isn't so nice. CTL+A doesn't work as expected even without a path,
    #  it leaves a capital "A" in the text editor.
    monospace_path = UIPath.for_floater("floater_test_textbox") / "monospace_text_editor"
    window_api.text_input("I typed in here by path.", path=monospace_path)


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
