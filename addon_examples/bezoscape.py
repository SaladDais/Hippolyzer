"""
Make all object textures Jeff Bezos

Helpful for migrating your region to AWS
"""

import copy
import ctypes
import random
import secrets

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.proxy.addon_utils import BaseAddon, SessionProperty
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


BEZOS_UUIDS = [UUID(x) for x in [
    "b8b8dcf9-758a-4539-ba63-793a01407236",
    "0010533a-cd41-44de-9a74-ab2125cbef8f",
]]


def _modify_crc(crc_tweak: int, crc_val: int):
    return ctypes.c_uint32(crc_val ^ crc_tweak).value


def _bezosify_te(local_id, parsed_te):
    parsed_te = copy.copy(parsed_te)
    parsed_te.Textures = {None: BEZOS_UUIDS[local_id % len(BEZOS_UUIDS)]}
    return parsed_te


class BezosifyAddon(BaseAddon):
    bezos_crc_xor: int = SessionProperty()

    def handle_session_init(self, session: Session):
        # We want CRCs that are stable for the duration of the session, but will
        # cause a cache miss for objects cached before this session. Generate a
        # random value to XOR all CRCs with
        self.bezos_crc_xor = secrets.randbits(32)

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if message.name == "ObjectUpdateCached":
            for block in message["ObjectData"]:
                # Cached only really has a CRC, this will force the cache miss.
                block["CRC"] = _modify_crc(self.bezos_crc_xor, block["CRC"])
        elif message.name == "ObjectUpdate":
            for block in message["ObjectData"]:
                block["CRC"] = _modify_crc(self.bezos_crc_xor, block["CRC"])
                parsed_te = block.deserialize_var("TextureEntry")
                if not parsed_te:
                    continue

                parsed_te = _bezosify_te(block["ID"], parsed_te)
                block.serialize_var("TextureEntry", parsed_te)
        elif message.name == "ImprovedTerseObjectUpdate":
            for block in message["ObjectData"]:
                parsed_te = block.deserialize_var("TextureEntry")
                if not parsed_te:
                    continue
                update_data = block.deserialize_var("Data")

                parsed_te = _bezosify_te(update_data["ID"], parsed_te)
                block.serialize_var("TextureEntry", parsed_te)
        elif message.name == "AvatarAppearance":
            for block in message["ObjectData"]:
                parsed_te = block.deserialize_var("TextureEntry")
                if not parsed_te:
                    continue
                # Need an integer ID to choose a bezos texture, just use
                # the last byte of the sender's UUID.
                sender_id = message["Sender"]["ID"]
                parsed_te = _bezosify_te(sender_id.bytes[-1], parsed_te)
                block.serialize_var("TextureEntry", parsed_te)
        elif message.name == "ObjectUpdateCompressed":
            for block in message["ObjectData"]:
                update_data = block.deserialize_var("Data")
                if not update_data:
                    continue
                update_data["CRC"] = _modify_crc(self.bezos_crc_xor, update_data["CRC"])
                if not update_data.get("TextureEntry"):
                    continue

                update_data["TextureEntry"] = _bezosify_te(
                    update_data["ID"],
                    update_data["TextureEntry"],
                )
                block.serialize_var("Data", update_data)
        elif message.name == "RegionHandshake":
            for field_name, val in message["RegionInfo"][0].items():
                if field_name.startswith("Terrain") and isinstance(val, UUID):
                    message["RegionInfo"][field_name] = random.choice(BEZOS_UUIDS)


addons = [BezosifyAddon()]
