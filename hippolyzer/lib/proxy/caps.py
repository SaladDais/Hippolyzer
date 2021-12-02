from __future__ import annotations

import enum
import typing
from weakref import ref
from typing import *

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion
    from hippolyzer.lib.proxy.sessions import Session, SessionManager


def is_asset_server_cap_name(cap_name):
    return cap_name and (
        cap_name.startswith("GetMesh")
        or cap_name.startswith("GetTexture")
        or cap_name.startswith("ViewerAsset")
    )


class CapType(enum.Enum):
    NORMAL = enum.auto()
    TEMPORARY = enum.auto()
    WRAPPER = enum.auto()
    PROXY_ONLY = enum.auto()

    @property
    def fake(self) -> bool:
        return self == CapType.PROXY_ONLY or self == CapType.WRAPPER


class SerializedCapData(typing.NamedTuple):
    cap_name: typing.Optional[str] = None
    region_addr: typing.Optional[str] = None
    session_id: typing.Optional[str] = None
    base_url: typing.Optional[str] = None
    type: str = "NORMAL"

    def __bool__(self):
        return bool(self.cap_name or self.session_id)

    @property
    def asset_server_cap(self):
        return is_asset_server_cap_name(self.cap_name)


class CapData(NamedTuple):
    cap_name: Optional[str] = None
    # Actually they're weakrefs but the type sigs suck.
    region: Optional[Callable[[], Optional[ProxiedRegion]]] = None
    session: Optional[Callable[[], Optional[Session]]] = None
    base_url: Optional[str] = None
    type: CapType = CapType.NORMAL

    def __bool__(self):
        return bool(self.cap_name or self.session)

    def serialize(self) -> "SerializedCapData":
        return SerializedCapData(
            cap_name=self.cap_name,
            region_addr=str(self.region().circuit_addr) if self.region and self.region() else None,
            session_id=str(self.session().id) if self.session and self.session() else None,
            base_url=self.base_url,
            type=self.type.name,
        )

    @classmethod
    def deserialize(
            cls,
            ser_cap_data: "SerializedCapData",
            session_mgr: Optional[SessionManager],
    ) -> "CapData":
        cap_session = None
        cap_region = None
        if session_mgr and ser_cap_data.session_id:
            for session in session_mgr.sessions:
                if ser_cap_data.session_id == str(session.id):
                    cap_session = session
        if cap_session and ser_cap_data.region_addr:
            for region in cap_session.regions:
                if ser_cap_data.region_addr == str(region.circuit_addr):
                    cap_region = region
        return cls(
            cap_name=ser_cap_data.cap_name,
            region=ref(cap_region) if cap_region else None,
            session=ref(cap_session) if cap_session else None,
            base_url=ser_cap_data.base_url,
            type=CapType[ser_cap_data.type],
        )

    @property
    def asset_server_cap(self) -> bool:
        return is_asset_server_cap_name(self.cap_name)
