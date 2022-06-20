import asyncio
import gc
import logging
import multiprocessing
import os
import sys
import time
from typing import Optional

import mitmproxy.ctx
import mitmproxy.exceptions

from hippolyzer.lib.base import llsd
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.ca_utils import setup_ca
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.http_proxy import create_http_proxy, create_proxy_master, HTTPFlowContext
from hippolyzer.lib.proxy.http_event_manager import MITMProxyEventManager
from hippolyzer.lib.proxy.lludp_proxy import SLSOCKS5Server
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import SessionManager, Session
from hippolyzer.lib.proxy.settings import ProxySettings

LOG = logging.getLogger(__name__)


class SelectionManagerAddon(BaseAddon):
    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        selected = session.selected
        if message.name == "ObjectSelect":
            # ObjectDeselect intentionally ignored to deal with messages that
            # won't work while the object is still selected
            selected.object_local = message["ObjectData"][-1]["ObjectLocalID"]
            needed_objects = set()
            selected.object_locals = tuple(b["ObjectLocalID"] for b in message["ObjectData"])
            for local_id in selected.object_locals:
                obj = region.objects.lookup_localid(local_id)
                if obj:
                    if not obj.ParentID:
                        selected.object_local = obj.LocalID
                else:
                    LOG.debug(f"Don't know about selected {local_id}, requesting object")
                    needed_objects.add(local_id)

            if needed_objects and session.session_manager.settings.ALLOW_AUTO_REQUEST_OBJECTS:
                region.objects.request_objects(needed_objects)
        # ParcelDwellRequests are sent whenever "about land" is opened. This gives us a
        # decent mechanism for selecting parcels.
        elif message.name == "ParcelDwellReply":
            block = message["Data"]
            selected.parcel_full = block["ParcelID"]
            selected.parcel_local = block["LocalID"]
        elif message.name == "UpdateTaskInventory":
            # This isn't quite right because UpdateTaskInventory is basically an
            # upsert, and takes on the insert behaviour if ItemID isn't in the task
            # already. The insert behaviour will give it a _new_ ItemID.
            # We have no way to distinguish the two without additional context.
            # You can always tick the share to group box though, and that should trigger
            # an update with the correct, new item ID.
            selected.task_item = message["InventoryData"]["ItemID"]

    def handle_http_request(self, session_manager, flow):
        cap_data = flow.cap_data
        if not cap_data:
            return
        if not cap_data.session:
            return
        selected = cap_data.session().selected
        # GetMetadata gets called whenever you open a script in a task, so we
        # can use it to guess which script you last opened.
        if cap_data.cap_name == "GetMetadata":
            parsed = llsd.parse_xml(flow.request.content)
            selected.script_item = parsed["item-id"]
            selected.task_item = parsed["item-id"]


class REPLAddon(BaseAddon):
    @handle_command()
    async def spawn_repl(self, session: Session, region: ProxiedRegion):
        """Spawn a REPL"""
        if not AddonManager.have_active_repl():
            AddonManager.spawn_repl()


def run_http_proxy_process(proxy_host, http_proxy_port, flow_context: HTTPFlowContext):
    mitm_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(mitm_loop)

    async def mitmproxy_loop():
        mitmproxy_master = create_http_proxy(proxy_host, http_proxy_port, flow_context)
        gc.freeze()
        await mitmproxy_master.run()

    asyncio.run(mitmproxy_loop())


def start_proxy(session_manager: SessionManager, extra_addons: Optional[list] = None,
                extra_addon_paths: Optional[list] = None, proxy_host=None):
    extra_addons = extra_addons or []
    extra_addon_paths = extra_addon_paths or []
    extra_addons.append(SelectionManagerAddon())
    extra_addons.append(REPLAddon())

    root_log = logging.getLogger()
    root_log.addHandler(logging.StreamHandler())
    root_log.setLevel(logging.INFO)
    logging.basicConfig()

    loop = asyncio.get_event_loop_policy().get_event_loop()

    udp_proxy_port = session_manager.settings.SOCKS_PROXY_PORT
    http_proxy_port = session_manager.settings.HTTP_PROXY_PORT
    if proxy_host is None:
        proxy_host = session_manager.settings.PROXY_BIND_ADDR

    flow_context = session_manager.flow_context
    session_manager.name_cache.load_viewer_caches()

    # TODO: argparse
    if len(sys.argv) == 3:
        if sys.argv[1] == "--setup-ca":
            try:
                mitmproxy_master = create_http_proxy(proxy_host, http_proxy_port, flow_context)
            except mitmproxy.exceptions.MitmproxyException:
                # Proxy already running, create the master so we don't try to bind to a port
                mitmproxy_master = create_proxy_master(proxy_host, http_proxy_port, flow_context)
            setup_ca(sys.argv[2], mitmproxy_master)
            return sys.exit(0)

    http_proc = multiprocessing.Process(
        target=run_http_proxy_process,
        args=(proxy_host, http_proxy_port, flow_context),
        daemon=True,
    )
    http_proc.start()
    # These need to be set for mitmproxy's ASGIApp serving code to work.
    mitmproxy.ctx.master = None
    mitmproxy.ctx.log = logging.getLogger("mitmproxy log")

    server = SLSOCKS5Server(session_manager)
    coro = asyncio.start_server(server.handle_connection, proxy_host, udp_proxy_port)
    async_server = loop.run_until_complete(coro)

    event_manager = MITMProxyEventManager(session_manager, flow_context)
    loop.create_task(event_manager.run())

    addon_paths = sys.argv[1:]
    addon_paths.extend(extra_addon_paths)
    AddonManager.init(addon_paths, session_manager, addon_objects=extra_addons)

    # Everything in memory at this point should stay
    gc.freeze()
    gc.set_threshold(5000, 50, 10)

    # Serve requests until Ctrl+C is pressed
    print(f"SOCKS and HTTP proxies running on {proxy_host}")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    print("Asking mitmproxy to shut down")

    # Shut down mitmproxy
    flow_context.shutdown_signal.set()

    # Close the server
    print("Closing SOCKS server")
    async_server.close()
    print("Shutting down addons")
    AddonManager.shutdown()
    print("Waiting for SOCKS server to close")
    loop.run_until_complete(async_server.wait_closed())
    print("Closing event loop")
    if sys.platform == "win32":
        # Hack around some bug with qasync's event loop hanging on win32
        p = multiprocessing.Process(
            target=_windows_timeout_killer,
            args=(os.getpid(),)
        )
        p.daemon = True
        p.start()
    loop.close()


def _windows_timeout_killer(pid: int):
    time.sleep(2.0)
    print("Killing hanging event loop")
    os.kill(pid, 9)


def main():
    multiprocessing.set_start_method("spawn")
    start_proxy(SessionManager(ProxySettings()))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
