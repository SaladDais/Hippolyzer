import asyncio
import dataclasses
import logging
from typing import *

import numpy as np

from hippolyzer.lib.base.datatypes import UUID, Vector3, Vector2
from hippolyzer.lib.base.message.message import Message, Block
from hippolyzer.lib.base.templates import ParcelGridFlags, ParcelFlags
from hippolyzer.lib.client.state import BaseClientRegion


LOG = logging.getLogger(__name__)


@dataclasses.dataclass
class Parcel:
    local_id: int
    name: str
    flags: ParcelFlags
    group_id: UUID
    # TODO: More properties


class ParcelManager:
    # We expect to receive this number of ParcelOverlay messages
    NUM_CHUNKS = 4
    # No, we don't support varregion or whatever.
    REGION_SIZE = 256
    # Basically, the minimum parcel size is 4 on either axis so each "point" in the
    # ParcelOverlay represents an area this size
    GRID_STEP = 4
    GRIDS_PER_EDGE = REGION_SIZE // GRID_STEP

    def __init__(self, region: BaseClientRegion):
        # dimensions are south to north, west to east
        self.overlay = np.zeros((self.GRIDS_PER_EDGE, self.GRIDS_PER_EDGE), dtype=np.uint8)
        # 1-indexed parcel list index
        self.parcel_indices = np.zeros((self.GRIDS_PER_EDGE, self.GRIDS_PER_EDGE), dtype=np.uint16)
        self.parcels: List[Optional[Parcel]] = []
        self.overlay_chunks: List[Optional[bytes]] = [None] * self.NUM_CHUNKS
        self.overlay_complete = asyncio.Event()
        self.parcels_downloaded = asyncio.Event()
        self._parcels_dirty: bool = True
        self._region = region
        self._next_seq = 1
        self._region.message_handler.subscribe("ParcelOverlay", self._handle_parcel_overlay)

    def _handle_parcel_overlay(self, message: Message):
        self.add_overlay_chunk(message["ParcelData"]["Data"], message["ParcelData"]["SequenceID"])

    def add_overlay_chunk(self, chunk: bytes, chunk_num: int) -> bool:
        self.overlay_chunks[chunk_num] = chunk
        # Still have some pending chunks, don't try to parse this yet
        if not all(self.overlay_chunks):
            return False

        new_overlay_data = b"".join(self.overlay_chunks)
        self.overlay_chunks = [None] * self.NUM_CHUNKS
        self._parcels_dirty = False
        if new_overlay_data != self.overlay.data[:]:
            # If the raw data doesn't match, then we have to parse again
            new_data = np.frombuffer(new_overlay_data, dtype=np.uint8).reshape(self.overlay.shape)
            np.copyto(self.overlay, new_data)
            self._parse_overlay()
            # We could optimize this by just marking specific squares dirty
            # if the parcel indices have changed between parses, but I don't care
            # to do that.
            self._parcels_dirty = True
            self.parcels_downloaded.clear()
        if not self.overlay_complete.is_set():
            self.overlay_complete.set()
        return True

    @classmethod
    def _pos_to_grid_coords(cls, pos: Vector3) -> Tuple[int, int]:
        return round(pos.Y // cls.GRID_STEP), round(pos.X // cls.GRID_STEP)

    def _parse_overlay(self):
        # Zero out all parcel indices
        self.parcel_indices[:, :] = 0
        next_parcel_idx = 1
        for y in range(0, self.GRIDS_PER_EDGE):
            for x in range(0, self.GRIDS_PER_EDGE):
                # We already have a parcel index for this grid, continue
                if self.parcel_indices[y, x]:
                    continue

                # Fill all adjacent grids with this parcel index
                self._flood_fill_parcel_index(y, x, next_parcel_idx)
                # SL doesn't allow disjoint grids to be part of the same parcel, so
                # whatever grid we find next without a parcel index must be a new parcel
                next_parcel_idx += 1

        # Should have found at least one parcel
        assert next_parcel_idx >= 2

        # Have a different number of parcels now, we can't use the existing parcel objects
        # because it's unlikely that just parcel boundaries have changed.
        if len(self.parcels) != next_parcel_idx - 1:
            # We don't know about any of these parcels yet, fill with none
            self.parcels = [None] * (next_parcel_idx - 1)

    def _flood_fill_parcel_index(self, start_y, start_x, parcel_idx):
        """Flood fill all neighboring grids with the parcel index, being mindful of parcel boundaries"""
        # We know the start grid is assigned to this parcel index
        self.parcel_indices[start_y, start_x] = parcel_idx
        # Queue of grids to test the neighbors of, start with the start grid.
        neighbor_test_queue: List[Tuple[int, int]] = [(start_y, start_x)]

        while neighbor_test_queue:
            to_test = neighbor_test_queue.pop(0)
            test_grid = self.overlay[to_test]

            for direction in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                new_pos = to_test[0] + direction[0], to_test[1] + direction[1]

                if any(x < 0 or x >= self.GRIDS_PER_EDGE for x in new_pos):
                    # Outside bounds
                    continue
                if self.parcel_indices[new_pos]:
                    # Already set, skip
                    continue

                if direction[0] == -1 and test_grid & ParcelGridFlags.SOUTH_LINE:
                    # Test grid is already on a south line, can't go south.
                    continue
                if direction[1] == -1 and test_grid & ParcelGridFlags.WEST_LINE:
                    # Test grid is already on a west line, can't go west.
                    continue

                grid = self.overlay[new_pos]

                if direction[0] == 1 and grid & ParcelGridFlags.SOUTH_LINE:
                    # Hit a south line going north, this is outside the current parcel
                    continue
                if direction[1] == 1 and grid & ParcelGridFlags.WEST_LINE:
                    # Hit a west line going east, this is outside the current parcel
                    continue
                # This grid is within the current parcel, set the parcel index
                self.parcel_indices[new_pos] = parcel_idx
                # Append the grid to the neighbour testing queue
                neighbor_test_queue.append(new_pos)

    async def request_dirty_parcels(self) -> Tuple[Parcel, ...]:
        if self._parcels_dirty:
            return await self.request_all_parcels()
        return tuple(self.parcels)

    async def request_all_parcels(self) -> Tuple[Parcel, ...]:
        await self.overlay_complete.wait()
        # Because of how we build up the parcel index map, it's safe for us to
        # do this instead of keeping track of seen IDs in a set or similar
        last_seen_parcel_index = 0
        futs = []
        for y in range(0, self.GRIDS_PER_EDGE):
            for x in range(0, self.GRIDS_PER_EDGE):
                parcel_index = self.parcel_indices[y, x]
                assert parcel_index != 0
                if parcel_index <= last_seen_parcel_index:
                    continue
                assert parcel_index == last_seen_parcel_index + 1
                last_seen_parcel_index = parcel_index
                # Request a position within the parcel
                futs.append(self.request_parcel_properties(
                    Vector2(x * self.GRID_STEP + 1.0, y * self.GRID_STEP + 1.0)
                ))

        # Wait for all parcel properties to come in
        await asyncio.gather(*futs)
        self.parcels_downloaded.set()
        self._parcels_dirty = False
        return tuple(self.parcels)

    async def request_parcel_properties(self, pos: Vector2) -> Parcel:
        await self.overlay_complete.wait()
        seq_id = self._next_seq
        # Register a wait on a ParcelProperties matching this seq
        parcel_props_fut = self._region.message_handler.wait_for(
            ("ParcelProperties",),
            predicate=lambda msg: msg["ParcelData"]["SequenceID"] == seq_id,
            timeout=10.0,
        )
        # We don't care about when we receive an ack, we only care about when we receive the parcel props
        _ = self._region.circuit.send_reliable(Message(
            "ParcelPropertiesRequest",
            Block("AgentData", AgentID=self._region.session().agent_id, SessionID=self._region.session().id),
            Block(
                "ParcelData",
                SequenceID=seq_id,
                West=pos.X,
                East=pos.X,
                North=pos.Y,
                South=pos.Y,
                # What does this even mean?
                SnapSelection=0,
            ),
        ))
        self._next_seq += 1

        return self._process_parcel_properties(await parcel_props_fut, pos)

    def _process_parcel_properties(self, parcel_props: Message, pos: Optional[Vector2] = None) -> Parcel:
        data_block = parcel_props["ParcelData"][0]
        grid_coord = None
        # Parcel indices are one-indexed, convert to zero-indexed.
        if pos is not None:
            # We have a pos, figure out where in the grid we should look for the parcel index
            grid_coord = self._pos_to_grid_coords(pos)
        else:
            # Need to look at the parcel bitmap to figure out a valid grid coord.
            # This is a boolean array where each bit says whether the parcel occupies that grid.
            parcel_bitmap = data_block.deserialize_var("Bitmap")

            for y in range(self.GRIDS_PER_EDGE):
                for x in range(self.GRIDS_PER_EDGE):
                    if parcel_bitmap[y, x]:
                        # This is the first grid the parcel occupies per the bitmap
                        grid_coord = y, x
                        break
                if grid_coord:
                    break

        parcel = Parcel(
            local_id=data_block["LocalID"],
            name=data_block["Name"],
            flags=ParcelFlags(data_block["ParcelFlags"]),
            group_id=data_block["GroupID"],
            # Parcel UUID isn't in this response :/
        )

        # I guess the bitmap _could_ be empty, but probably not.
        if grid_coord is not None:
            parcel_idx = self.parcel_indices[grid_coord] - 1
            if len(self.parcels) > parcel_idx >= 0:
                # Okay, parcels list is sane, place the parcel in there.
                self.parcels[parcel_idx] = parcel
            else:
                LOG.warning(f"Received ParcelProperties with incomplete overlay for {grid_coord!r}")

        return parcel

    async def get_parcel_at(self, pos: Vector2, request_if_missing: bool = True) -> Optional[Parcel]:
        grid_coord = self._pos_to_grid_coords(pos)
        parcel = None
        if parcel_idx := self.parcel_indices[grid_coord]:
            parcel = self.parcels[parcel_idx - 1]
        if request_if_missing and parcel is None:
            return await self.request_parcel_properties(pos)
        return parcel
