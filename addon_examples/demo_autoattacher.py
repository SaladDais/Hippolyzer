"""
Detect receipt of a marketplace order for a demo, and auto-attach the most appropriate object
"""

import asyncio
import re
from typing import List, Tuple, Dict, Optional, Sequence

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.templates import InventoryType, Permissions, FolderType
from hippolyzer.lib.proxy.addon_utils import BaseAddon, show_message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


MARKETPLACE_TRANSACTION_ID = UUID('ffffffff-ffff-ffff-ffff-ffffffffffff')


class DemoAutoAttacher(BaseAddon):
    def handle_eq_event(self, session: Session, region: ProxiedRegion, event: dict):
        if event["message"] != "BulkUpdateInventory":
            return
        # Check that this update even possibly came from the marketplace
        if event["body"]["AgentData"][0]["TransactionID"] != MARKETPLACE_TRANSACTION_ID:
            return
        # Make sure that the transaction targeted our real received items folder
        folders = event["body"]["FolderData"]
        received_folder = folders[0]
        if received_folder["Name"] != "Received Items":
            return
        skel = session.login_data['inventory-skeleton']
        actual_received = [x for x in skel if x['type_default'] == FolderType.INBOX]
        assert actual_received
        if UUID(actual_received[0]['folder_id']) != received_folder["FolderID"]:
            show_message(f"Strange received folder ID spoofing? {folders!r}")
            return

        if not re.match(r".*\bdemo\b.*", folders[1]["Name"], flags=re.I):
            return
        # Alright, so we have a demo... thing from the marketplace. What now?
        items = event["body"]["ItemData"]
        object_items = [x for x in items if x["InvType"] == InventoryType.OBJECT]
        if not object_items:
            return
        self._schedule_task(self._attach_best_object(session, region, object_items))

    async def _attach_best_object(self, session: Session, region: ProxiedRegion, object_items: List[Dict]):
        own_body_type = await self._guess_own_body(session, region)
        show_message(f"Trying to find demo for {own_body_type}")
        guess_patterns = self.BODY_CLOTHING_PATTERNS.get(own_body_type)
        to_attach = []
        if own_body_type and guess_patterns:
            matching_items = self._get_matching_items(object_items, guess_patterns)
            if matching_items:
                # Only take the first one
                to_attach.append(matching_items[0])
        if not to_attach:
            # Don't know what body's being used or couldn't figure out what item
            # would work best with our body. Just attach the first object in the folder.
            to_attach.append(object_items[0])

        # Also attach whatever HUDs, maybe we need them.
        for hud in self._get_matching_items(object_items, ("hud",)):
            if hud not in to_attach:
                to_attach.append(hud)

        region.circuit.send(Message(
            'RezMultipleAttachmentsFromInv',
            Block('AgentData', AgentID=session.agent_id, SessionID=session.id),
            Block('HeaderData', CompoundMsgID=UUID.random(), TotalObjects=len(to_attach), FirstDetachAll=0),
            *[Block(
                'ObjectData',
                ItemID=o["ItemID"],
                OwnerID=session.agent_id,
                # 128 = "add", uses whatever attachmentpt was defined on the object
                AttachmentPt=128,
                ItemFlags_=(),
                GroupMask_=(),
                EveryoneMask_=(),
                NextOwnerMask_=(Permissions.COPY | Permissions.MOVE),
                Name=o["Name"],
                Description=o["Description"],
            ) for o in to_attach]
        ))

    def _get_matching_items(self, items: List[dict], patterns: Sequence[str]):
        # Loop over patterns to search for our body type, in order of preference
        matched = []
        for guess_pattern in patterns:
            # Check each item for that pattern
            for item in items:
                if re.match(rf".*\b{guess_pattern}\b.*", item["Name"], re.I):
                    matched.append(item)
        return matched

    # We scan the agent's attached objects to guess what kind of body they use
    BODY_PREFIXES = {
        "-Belleza- Jake ": "jake",
        "-Belleza- Freya ": "freya",
        "-Belleza- Isis ": "isis",
        "-Belleza- Venus ": "venus",
        "[Signature] Gianni Body": "gianni",
        "[Signature] Geralt Body": "geralt",
        "Maitreya Mesh Body - Lara": "maitreya",
        "Slink Physique Hourglass Petite": "hg_petite",
        "Slink Physique Mesh Body Hourglass": "hourglass",
        "Slink Physique Original Petite": "phys_petite",
        "Slink Physique Mesh Body Original": "physique",
        "[BODY] Legacy (f)": "legacy_f",
        "[BODY] Legacy (m)": "legacy_m",
        "[Signature] Alice Body": "sig_alice",
        "Slink Physique MALE Mesh Body": "slink_male",
        "AESTHETIC - [Mesh Body]": "aesthetic",
    }

    # Different bodies' clothes have different naming conventions according to different merchants.
    # These are common naming patterns we use to choose objects to attach, in order of preference.
    BODY_CLOTHING_PATTERNS: Dict[str, Tuple[str, ...]] = {
        "jake": ("jake", "belleza"),
        "freya": ("freya", "belleza"),
        "isis": ("isis", "belleza"),
        "venus": ("venus", "belleza"),
        "gianni": ("gianni", "signature", "sig"),
        "geralt": ("geralt", "signature", "sig"),
        "hg_petite": ("hourglass petite", "hg petite", "hourglass", "hg", "slink"),
        "hourglass": ("hourglass", "hg", "slink"),
        "phys_petite": ("physique petite", "phys petite", "physique", "phys", "slink"),
        "physique": ("physique", "phys", "slink"),
        "legacy_f": ("legacy",),
        "legacy_m": ("legacy",),
        "sig_alice": ("alice", "signature"),
        "slink_male": ("physique", "slink"),
        "aesthetic": ("aesthetic",),
    }

    async def _guess_own_body(self, session: Session, region: ProxiedRegion) -> Optional[str]:
        agent_obj = region.objects.lookup_fullid(session.agent_id)
        if not agent_obj:
            return None
        # We probably won't know the names for all of our attachments, request them.
        # Could be obviated by looking at the COF, not worth it for this.
        try:
            await asyncio.wait(region.objects.request_object_properties(agent_obj.Children), timeout=0.5)
        except asyncio.TimeoutError:
            # We expect that we just won't ever receive some property requests, that's fine
            pass

        for prefix, body_type in self.BODY_PREFIXES.items():
            for obj in agent_obj.Children:
                if not obj.Name:
                    continue
                if obj.Name.startswith(prefix):
                    return body_type
        return None


addons = [DemoAutoAttacher()]
