"""
Make most object textures monochrome.

Avoids affecting materials and profile pictures and the like by
replacing textures in TEs with an alias and only mutating requests
for those alias IDs.

Demonstrates a multiprocessing / queue consumer pattern for addons that
need to do expensive, potentially blocking work in the background.

This will make your CPU fan go crazy so enjoy that.
"""

import copy
import ctypes
import multiprocessing
import queue
import secrets
import statistics
import time
import traceback

import glymur
import numpy as np
from mitmproxy.http import HTTPFlow

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.jp2_utils import BufferedJp2k
from hippolyzer.lib.base.multiprocessing_utils import ParentProcessWatcher
from hippolyzer.lib.base.templates import TextureEntryCollection
from hippolyzer.lib.proxy.addon_utils import AssetAliasTracker, BaseAddon, GlobalProperty, AddonProcess
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager


glymur.set_option('lib.num_threads', 4)

# These should never be replaced, they're only used as aliases to tell the viewer
# it should fetch the relevant texture from the appearance service
BAKES_ON_MESH_TEXTURE_IDS = {UUID(x) for x in (
    "5a9f4a74-30f2-821c-b88d-70499d3e7183",
    "ae2de45c-d252-50b8-5c6e-19f39ce79317",
    "24daea5f-0539-cfcf-047f-fbc40b2786ba",
    "52cc6bb6-2ee5-e632-d3ad-50197b1dcb8a",
    "43529ce8-7faa-ad92-165a-bc4078371687",
    "09aac1fb-6bce-0bee-7d44-caac6dbb6c63",
    "ff62763f-d60a-9855-890b-0c96f8f8cd98",
    "8e915e25-31d1-cc95-ae08-d58a47488251",
    "9742065b-19b5-297c-858a-29711d539043",
    "03642e83-2bd1-4eb9-34b4-4c47ed586d2d",
    "edd51b77-fc10-ce7a-4b3d-011dfc349e4f",
)}


def _modify_crc(crc_tweak: int, crc_val: int):
    return ctypes.c_uint32(crc_val ^ crc_tweak).value


class MonochromeAddon(BaseAddon):
    NUM_CONSUMERS = 6
    mono_crc_xor: int = GlobalProperty()
    mono_tracker: AssetAliasTracker = GlobalProperty(AssetAliasTracker)

    def __init__(self):
        # These are global and should die whenever the addon reloads,
        # so they can live on the instance rather than in addon context
        self.mono_addon_shutdown_signal = multiprocessing.Event()
        self.image_resp_queue = multiprocessing.Queue()

    def handle_init(self, session_manager: SessionManager):
        to_proxy_queue = session_manager.flow_context.to_proxy_queue
        for _ in range(self.NUM_CONSUMERS):
            # We must use AddonProcess rather than multiprocessing.Process because our
            # target function is in a dynamically loaded addon. See AddonProcess' docstring.
            AddonProcess(
                target=_process_image_queue,
                args=(self.mono_addon_shutdown_signal, self.image_resp_queue, to_proxy_queue),
                daemon=True,
            ).start()

        # We want CRCs that are stable for the duration of the addon's life, but will
        # cause a cache miss for objects cached before. Generate a random value
        # to XOR all CRCs with.
        self.mono_crc_xor = secrets.randbits(32)
        self.mono_tracker.invalidate_aliases()

    def handle_session_init(self, session: Session):
        # We loaded while this session was active, re-request all objects we
        # know about so we can process them
        if session.main_region:
            object_manager = session.main_region.objects
            object_manager.request_missing_objects()
            object_manager.request_objects([o.LocalID for o in object_manager.all_objects])

    def handle_unload(self, session_manager: SessionManager):
        # Tell queue consumers to shut down
        self.mono_addon_shutdown_signal.set()

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        tracker = self.mono_tracker
        if message.name == "ObjectUpdateCached":
            for block in message["ObjectData"]:
                # Cached only really has a CRC, this will force the cache miss.
                block["CRC"] = _modify_crc(self.mono_crc_xor, block["CRC"])
        elif message.name == "ObjectUpdate":
            for block in message["ObjectData"]:
                block["CRC"] = _modify_crc(self.mono_crc_xor, block["CRC"])
                parsed_te = block.deserialize_var("TextureEntry")
                if not parsed_te:
                    continue

                parsed_te = self._make_te_monochrome(tracker, parsed_te)
                block.serialize_var("TextureEntry", parsed_te)
        elif message.name == "ImprovedTerseObjectUpdate":
            for block in message["ObjectData"]:
                parsed_te = block.deserialize_var("TextureEntry")
                if not parsed_te:
                    continue
                parsed_te = self._make_te_monochrome(tracker, parsed_te)
                block.serialize_var("TextureEntry", parsed_te)
        elif message.name == "AvatarAppearance":
            for block in message["ObjectData"]:
                parsed_te = block.deserialize_var("TextureEntry")
                if not parsed_te:
                    continue
                # Have to hook AppearanceService for this to work.
                parsed_te = self._make_te_monochrome(tracker, parsed_te)
                block.serialize_var("TextureEntry", parsed_te)
        elif message.name == "ObjectUpdateCompressed":
            for block in message["ObjectData"]:
                update_data = block.deserialize_var("Data")
                if not update_data:
                    continue
                update_data["CRC"] = _modify_crc(self.mono_crc_xor, update_data["CRC"])
                if not update_data.get("TextureEntry"):
                    continue

                update_data["TextureEntry"] = self._make_te_monochrome(
                    tracker,
                    update_data["TextureEntry"],
                )
                block.serialize_var("Data", update_data)
        elif message.name == "RegionHandshake":
            for field_name, val in message["RegionInfo"][0].items():
                if field_name.startswith("Terrain") and isinstance(val, UUID):
                    message["RegionInfo"][field_name] = tracker.get_alias_uuid(val)

    @staticmethod
    def _make_te_monochrome(tracker: AssetAliasTracker, parsed_te: TextureEntryCollection):
        # Need a deepcopy because TEs are owned by the ObjectManager
        # and we don't want to change the canonical view.
        parsed_te = copy.deepcopy(parsed_te)
        for k, v in parsed_te.Textures.items():
            if v in BAKES_ON_MESH_TEXTURE_IDS:
                continue
            # Replace textures with their alias to bust the viewer cache
            parsed_te.Textures[k] = tracker.get_alias_uuid(v)
        for k, v in parsed_te.Color.items():
            # Convert face colors to monochrome, keeping alpha byte the same
            avg_val = int(round(statistics.mean((v[0], v[1], v[2]))))
            parsed_te.Color[k] = bytes((avg_val,) * 3 + (v[3],))
        return parsed_te

    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        cap_data = flow.cap_data
        if not cap_data:
            return
        is_appearance = cap_data.cap_name == "AppearanceService"
        if not (cap_data.asset_server_cap or is_appearance):
            return

        if is_appearance:
            # Baked layers come from the sim-local appearance service, not the asset server.
            # Its request URIs look a little different.
            texture_id = flow.request.url.split('/')[-1]
        else:
            texture_id = flow.request.query.get("texture_id")

        if not texture_id:
            return

        orig_texture_id = self.mono_tracker.get_orig_uuid(UUID(texture_id))
        if not orig_texture_id:
            return
        if orig_texture_id in BAKES_ON_MESH_TEXTURE_IDS:
            return

        # The request was for a fake texture ID we created, rewrite the request to
        # request the real asset and mark the flow for modification once we receive
        # the image.
        if is_appearance:
            split_url = flow.request.url.split('/')
            split_url[-1] = str(orig_texture_id)
            flow.request.url = '/'.join(split_url)
        else:
            flow.request.query["texture_id"] = str(orig_texture_id)

        flow.can_stream = False
        flow.metadata["make_monochrome"] = True
        # We can't parse a partial J2C. This is probably a little inefficient since we're
        # liable to have multiple in-flight requests for different ranges of a file at any
        # given time, and we'll have to re-encode multiple times. Meh.
        flow.request.headers.pop("Range", None)

    def handle_http_response(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        if not flow.metadata.get("make_monochrome"):
            return

        if flow.response.status_code not in (200, 206):
            return

        # Don't send the callback to the proxy immediately, our queue consumer is
        # messing with the image data and will send the callback itself.
        flow.take()
        # Put the serialized HTTP flow on the queue for one of the consumers to pick up
        self.image_resp_queue.put(flow.get_state())
        return True


def _process_image_queue(
        shutdown_signal: multiprocessing.Event,
        image_resp_queue: multiprocessing.Queue,
        to_proxy_queue: multiprocessing.Queue
):
    watcher = ParentProcessWatcher(shutdown_signal)
    while not watcher.check_shutdown_needed():
        try:
            flow_state = image_resp_queue.get(False)
        except queue.Empty:
            # Ok to block since we're in our own process
            time.sleep(0.01)
            continue

        # Use HTTPFlow since we don't have a session manager and don't need
        # to understand any Hippolyzer-specific fields
        flow: HTTPFlow = HTTPFlow.from_state(flow_state)
        try:
            flow.response.content = _make_jp2_monochrome(flow.response.content)
            # Not a range anymore, update the headers and status.
            flow.response.headers.pop("Content-Range", None)
            flow.response.status_code = 200
        except:
            # Just log the exception and pass the image through unmodified
            traceback.print_exc()

        # Put our modified response directly on the mitmproxy response queue,
        # no point sending it back to the addon.
        to_proxy_queue.put(("callback", flow.id, flow.get_state()))


def _make_jp2_monochrome(jp2_data: bytes) -> bytes:
    j = BufferedJp2k(jp2_data)
    # Less than three components? Probably monochrome already.
    if len(j.shape) < 3 or j.shape[2] < 3:
        return jp2_data

    # Downscale if it'll be a huge image, compression is slow.
    if any(c >= 1024 for c in j.shape[0:2]):
        pixels = j[::4, ::4]
    elif any(c >= 512 for c in j.shape[0:2]):
        pixels = j[::2, ::2]
    else:
        pixels = j[::]

    for row in pixels:
        for col in row:
            # Simple average value monochrome conversion
            # Don't touch any component after the third. Those
            # have alpha and baked layer related data.
            col[0:3] = np.mean(col[0:3])

    # RGB, we can convert this to a single monochrome channel since
    # we don't have to worry about messing with alpha.
    if pixels.shape[2] == 3:
        pixels = pixels[:, :, 0:1]
        # Inform glymur of the new array shape
        j.shape = (pixels.shape[0], pixels.shape[1], 1)

    j[::] = pixels
    return bytes(j)


addons = [MonochromeAddon()]
