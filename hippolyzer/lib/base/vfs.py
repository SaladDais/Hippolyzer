import dataclasses
from typing import *

import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.helpers import get_resource_filename
from hippolyzer.lib.base.templates import AssetType


@dataclasses.dataclass
class VFSBlock:
    location: int = se.dataclass_field(se.U32)
    length: int = se.dataclass_field(se.U32)
    access_time: int = se.dataclass_field(se.U32)
    file_id: UUID = se.dataclass_field(se.UUID)
    asset_type: AssetType = se.dataclass_field(se.IntEnum(AssetType, se.U16))
    size: int = se.dataclass_field(se.U32)


class VFS:
    def __init__(self, index_path):
        self._data_fh = None
        self.blocks: List[VFSBlock] = []
        self._uuid_lookup: Dict[UUID, VFSBlock] = {}

        assert "index.db2" in index_path
        self._index_path = index_path
        self.reload()

    def reload(self):
        self.blocks.clear()
        self._uuid_lookup.clear()
        if self._data_fh:
            self._data_fh.close()
            self._data_fh = None
        self._data_fh = open(self._index_path.replace("index.db2", "data.db2"), "rb")

        with open(self._index_path, "rb") as index_fh:
            reader = se.FHReader("<", index_fh)
            while reader:
                block: VFSBlock = reader.read(se.Dataclass(VFSBlock))
                if not block.size:
                    continue
                self.blocks.append(block)
                self._uuid_lookup[block.file_id] = block

    def __iter__(self) -> Iterator[VFSBlock]:
        return iter(self.blocks)

    def __getitem__(self, item: UUID) -> VFSBlock:
        return self._uuid_lookup[item]

    def __contains__(self, item: UUID):
        return item in self._uuid_lookup

    def __del__(self):
        if self._data_fh:
            self._data_fh.close()
            self._data_fh = None

    def read_block(self, block: VFSBlock) -> bytes:
        self._data_fh.seek(block.location)
        return self._data_fh.read(block.size)


_static_path = get_resource_filename("lib/base/data/static_index.db2")
STATIC_VFS = VFS(_static_path)
