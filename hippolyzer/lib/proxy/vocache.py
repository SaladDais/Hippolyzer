"""
Viewer object cache implementation

Important to have because if we're debugging potential state management issues
in the viewer's scene graph, we need an idea of what it's scene graph _should_
look like at the current point in time. We can get that by hooking into its
VOCache so we know about its cache hits, and then compare whats in the proxy's
ObjectManager vs the viewer's (through GDB or something.)

Everything little-endian unless otherwise specified.
These use native struct alignment and padding, which is the reason for the
native address size being stored in the header. They should have just packed
the structs properly instead.

object.cache index file:
    IndexMetaHeader:
        U32 version = 15;
        U32 address_size = 32 or 64;
        CacheIndex entries[128];

    Exactly 128 region entries allowed, if any are missing they will have `time == 0`
    and should be skipped.

    CacheIndex:
        S32 index = i; // redundant, but helpful
        U64 handle; // ORed together global X and Y
        U32 time;


objects_<grid_x>_<grix_y>.slc:
    ObjectsMetaHeader:
        // must match ID sent in RegionHandshake. Filenames do not include grid ID so this may be
        // a file for a region at the same coords on a completely different grid!
        UUID cache_id;
        S32 num_entries;

    VOCacheEntry:
        U32 local_id;
        U32 crc;
        S32 hit_count;
        S32 dupe_count;
        S32 crc_change_count;
        // must be <= 10000 and > 0. Failing this continues parsing without reading data.
        S32 size;
        if (size <= 10000 && entry.size > 0)
            U8 data[size]; // same representation as "data" in ObjectUpdateCompressed
        else
            U8 data[0];


    ObjectsMetaHeader header;
    for i in range(header.num_entries) {
        VOCacheEntry entry;
    }
"""

from __future__ import annotations

import io
import logging
import pathlib
from pathlib import Path
from typing import *

import recordclass

import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.objects import handle_to_gridxy
from hippolyzer.lib.proxy.viewer_settings import iter_viewer_cache_dirs

LOG = logging.getLogger(__name__)


class ViewerObjectCache:
    VERSION = 15
    MAX_REGIONS = 128

    def __init__(self, base_path: Union[str, Path]):
        self.base_path = Path(base_path)
        # handle -> updated
        self.regions: Dict[int, int] = {}

    @classmethod
    def from_path(cls, base_path: Union[str, Path]):
        base_path = pathlib.Path(base_path)
        cache = cls(base_path)
        with open(cache.base_path / "object.cache", "rb") as fh:
            reader = se.BufferReader("<", fh.read())
        version = reader.read(se.U32)
        if version != cls.VERSION:
            LOG.error(f"Unsupported vocache version {version} in {cache.base_path}")
            return
        address_size = reader.read(se.U32)
        if address_size not in (32, 64):
            LOG.error(f"Unsupported address size {address_size}")
            return

        # HACK: VOCache writes structs directly to disk from memory. It doesn't specify
        # any packing rules, so the struct gets written with whatever the platform
        # defaults are. In my case, everything is 8 byte aligned because there's a
        # U64 member for the handle. I'm not an expert in this sort of thing, so we
        # try to guess the arrangement of the struct by scanning ahead.
        int_spec = se.U32
        for i in range(cls.MAX_REGIONS):
            entry_index = reader.read(int_spec) & 0xFFffFFff
            if entry_index != i:
                LOG.warning(f"Expected region entry index to be {i}, got {entry_index}")
            # Sniff padding alignment on the first cache entry
            if i == 0:
                # Seek to where the next index would be if everything was 8 byte aligned
                with reader.scoped_seek(20, io.SEEK_CUR):
                    next_i = reader.read(se.U32)

                # If it's 1 then we're using 8 byte alignment. Just read 8 bytes for all ints.
                # If there was no padding then this would read into the region handle, but
                # that could never have 4 bytes == 1 because both x and y will be multiples of 256.
                if next_i == 1:
                    # Trash the extra few bits and switch to reading U64s
                    _ = reader.read(se.U32)
                    int_spec = se.U64

            handle = reader.read(se.U64)
            # Mask off any junk bits that might have been written in the padding
            time = reader.read(int_spec) & 0xFFffFFff
            # If there's no time then this is an empty slot.
            if not time:
                continue
            cache.regions[handle] = time
        return cache

    def read_region(self, handle: int) -> Optional[RegionViewerObjectCache]:
        if handle not in self.regions:
            return None
        grid_x, grid_y = handle_to_gridxy(handle)
        objects_file = self.base_path / f"objects_{grid_x}_{grid_y}.slc"
        if not objects_file.exists():
            return None
        return RegionViewerObjectCache.from_file(objects_file)


class ViewerObjectCacheEntry(recordclass.datatuple):   # type: ignore
    local_id: int
    crc: int
    data: bytes


def is_valid_vocache_dir(cache_dir):
    return (pathlib.Path(cache_dir) / "objectcache" / "object.cache").exists()


class RegionViewerObjectCache:
    """Parser and container for .slc files"""
    def __init__(self, cache_id: UUID, entries: List[ViewerObjectCacheEntry]):
        self.cache_id: UUID = cache_id
        self.entries: Dict[int, ViewerObjectCacheEntry] = {
            e.local_id: e for e in entries
        }

    @classmethod
    def from_file(cls, objects_path: Union[str, Path]):
        # These files are only a few megabytes max so fine to slurp in
        with open(objects_path, "rb") as fh:
            reader = se.BufferReader("<", fh.read())
        cache_id: UUID = reader.read(se.UUID)

        num_entries = reader.read(se.S32)
        entries = []
        for _ in range(num_entries):
            # EOF, the viewer specifically allows for this.
            if not len(reader):
                break
            local_id = reader.read(se.U32)
            crc = reader.read(se.U32)
            # Not important to us
            _ = reader.read(se.U32)
            _ = reader.read(se.U32)
            _ = reader.read(se.U32)
            size = reader.read(se.U32)
            if not size or size > 10_000:
                continue
            data = reader.read_bytes(size, to_bytes=True)
            entries.append(ViewerObjectCacheEntry(
                local_id=local_id,
                crc=crc,
                data=data,
            ))
        return RegionViewerObjectCache(cache_id, entries)

    def lookup_object_data(self, local_id: int, crc: int) -> Optional[bytes]:
        entry = self.entries.get(local_id)
        if entry and entry.crc == crc:
            return entry.data
        return None


class RegionViewerObjectCacheChain:
    """Wrapper for the checking the same region in multiple cache locations"""
    def __init__(self, region_caches: List[RegionViewerObjectCache]):
        self.region_caches = region_caches

    def lookup_object_data(self, local_id: int, crc: int) -> Optional[bytes]:
        for cache in self.region_caches:
            data = cache.lookup_object_data(local_id, crc)
            if data:
                return data
        return None

    @classmethod
    def for_region(cls, handle: int, cache_id: UUID, cache_dir: Optional[str] = None):
        """
        Get a cache chain for a specific region, called on region connection

        We don't know what viewer the user is currently using, or where its cache lives
        so we have to try every region object cache file for every viewer installed.
        """
        caches = []
        if cache_dir is None:
            cache_dirs = iter_viewer_cache_dirs()
        else:
            cache_dirs = [pathlib.Path(cache_dir)]

        for cache_dir in cache_dirs:
            if not is_valid_vocache_dir(cache_dir):
                continue
            cache = ViewerObjectCache.from_path(cache_dir / "objectcache")
            if cache:
                caches.append(cache)
        regions = []
        for cache in caches:
            region = cache.read_region(handle)
            if not region:
                continue
            if region.cache_id != cache_id:
                continue
            regions.append(region)
        return RegionViewerObjectCacheChain(regions)
