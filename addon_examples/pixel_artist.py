"""
Import a small image (like a nintendo sprite) and create it out of cube prims

Inefficient and doesn't even do line fill, expect it to take `width * height`
prims for whatever image you import!
"""

import asyncio
import struct
from typing import *

from PySide6.QtGui import QImage

from hippolyzer.lib.base.datatypes import UUID, Vector3, Quaternion
from hippolyzer.lib.base.helpers import to_chunks
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.templates import ObjectUpdateFlags, PCode, MCode, MultipleObjectUpdateFlags, \
    TextureEntryCollection, JUST_CREATED_FLAGS
from hippolyzer.lib.client.object_manager import ObjectEvent, ObjectUpdateType
from hippolyzer.lib.proxy.addon_utils import BaseAddon
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


PRIM_SCALE = 0.2


class PixelArtistAddon(BaseAddon):
    @handle_command()
    async def import_pixel_art(self, session: Session, region: ProxiedRegion):
        """
        Import a small image (like a nintendo sprite) and create it out of cube prims
        """
        filename = await AddonManager.UI.open_file(
            "Open an image",
            filter_str="Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if not filename:
            return
        img = QImage()
        with open(filename, "rb") as f:
            img.loadFromData(f.read(), format=None)
        img = img.convertToFormat(QImage.Format_RGBA8888)
        height = img.height()
        width = img.width()
        pixels: List[Optional[bytes]] = []
        needed_prims = 0
        for y in range(height):
            for x in range(width):
                color: int = img.pixel(x, y)
                # This will be ARGB, SL wants RGBA
                alpha = (color & 0xFF000000) >> 24
                color = color & 0x00FFFFFF
                if alpha > 20:
                    # Repack RGBA to the bytes format we use for colors
                    pixels.append(struct.pack("!I", (color << 8) | alpha))
                    needed_prims += 1
                else:
                    # Pretty transparent, skip it
                    pixels.append(None)

        if not await AddonManager.UI.confirm("Confirm prim use", f"This will take {needed_prims} prims"):
            return

        agent_obj = region.objects.lookup_fullid(session.agent_id)
        agent_pos = agent_obj.RegionPosition

        created_prims = []
        # Watch for any newly created prims, this is basically what the viewer does to find
        # prims that it just created with the build tool.
        with session.objects.events.subscribe_async(
                (ObjectUpdateType.UPDATE,),
                predicate=lambda e: e.object.UpdateFlags & JUST_CREATED_FLAGS and "LocalID" in e.updated
        ) as get_events:
            # Create a pool of prims to use for building the pixel art
            for _ in range(needed_prims):
                # TODO: Can't get land group atm, just tries to rez with the user's active group
                group_id = session.active_group
                region.circuit.send(Message(
                    'ObjectAdd',
                    Block('AgentData', AgentID=session.agent_id, SessionID=session.id, GroupID=group_id),
                    Block(
                        'ObjectData',
                        PCode=PCode.PRIMITIVE,
                        Material=MCode.WOOD,
                        AddFlags=ObjectUpdateFlags.CREATE_SELECTED,
                        PathCurve=16,
                        ProfileCurve=1,
                        PathScaleX=100,
                        PathScaleY=100,
                        BypassRaycast=1,
                        RayStart=agent_obj.RegionPosition + Vector3(0, 0, 2),
                        RayEnd=agent_obj.RegionPosition + Vector3(0, 0, 2),
                        RayTargetID=UUID(),
                        RayEndIsIntersection=0,
                        Scale=Vector3(PRIM_SCALE, PRIM_SCALE, PRIM_SCALE),
                        Rotation=Quaternion(0.0, 0.0, 0.0, 1.0),
                        fill_missing=True,
                    ),
                ))
                # Don't spam a ton of creates at once
                await asyncio.sleep(0.02)

            # Read any creation events that queued up while we were creating the objects
            # So we can figure out the newly-created objects' IDs
            for _ in range(needed_prims):
                evt: ObjectEvent = await asyncio.wait_for(get_events(), 1.0)
                created_prims.append(evt.object)

        # Drawing origin starts at the top left, should be positioned just above the
        # avatar on Z and centered on Y.
        top_left = Vector3(0, (width * PRIM_SCALE) * -0.5, (height * PRIM_SCALE) + 2.0) + agent_pos
        positioning_blocks = []
        prim_idx = 0
        for i, pixel_color in enumerate(pixels):
            # Transparent, skip
            if pixel_color is None:
                continue
            x = i % width
            y = i // width
            obj = created_prims[prim_idx]
            # Set a blank texture on all faces
            te = TextureEntryCollection()
            te.Textures[None] = UUID('5748decc-f629-461c-9a36-a35a221fe21f')
            # Set the prim color to the color from the pixel
            te.Color[None] = pixel_color
            # Set the prim texture and color
            region.circuit.send(Message(
                'ObjectImage',
                Block('AgentData', AgentID=session.agent_id, SessionID=session.id),
                Block('ObjectData', ObjectLocalID=obj.LocalID, MediaURL=b'', TextureEntry_=te),
                direction=Direction.OUT,
            ))
            # Save the repositioning data for later since it uses a different message,
            # but it can be set in batches.
            positioning_blocks.append(Block(
                'ObjectData',
                ObjectLocalID=obj.LocalID,
                Type=MultipleObjectUpdateFlags.POSITION,
                Data_={'POSITION': top_left + Vector3(0, x * PRIM_SCALE, y * -PRIM_SCALE)},
            ))
            await asyncio.sleep(0.01)
            # We actually used a prim for this, so increment the index
            prim_idx += 1

        # Move the "pixels" to their correct position in chunks
        for chunk in to_chunks(positioning_blocks, 25):
            region.circuit.send(Message(
                'MultipleObjectUpdate',
                Block('AgentData', AgentID=session.agent_id, SessionID=session.id),
                *chunk,
                direction=Direction.OUT,
            ))
            await asyncio.sleep(0.01)


addons = [PixelArtistAddon()]
