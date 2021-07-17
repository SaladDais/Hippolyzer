from __future__ import annotations

import collections
import datetime as dt
from typing import *

from mitmproxy import http

from hippolyzer.lib.base.datatypes import UUID
if TYPE_CHECKING:
    from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow


class AssetData(NamedTuple):
    data: bytes
    expires: Optional[dt.datetime]


class HTTPAssetRepo(collections.UserDict):
    data: Dict[UUID, AssetData]

    def create_asset(self, data, one_shot=False) -> UUID:
        asset_id = UUID.random()
        expires = None
        if one_shot:
            # If there are multiple concurrent sessions then we may see multiple
            # requests for an asset even if we only really need one per-client.
            # Deal with that by evicting after a short period instead of immediately
            # evicting on first request.
            expires = dt.datetime.now() + dt.timedelta(seconds=5)
        self.data[asset_id] = AssetData(data, expires)
        return asset_id

    def collect_garbage(self):
        for k in tuple(self.data.keys()):
            v = self.data[k]
            if not v.expires:
                continue
            if v.expires <= dt.datetime.now():
                del self.data[k]

    def try_serve_asset(self, flow: HippoHTTPFlow) -> bool:
        self.collect_garbage()

        if not flow.cap_data.asset_server_cap:
            return False

        asset_id = None
        for name, val in flow.request.query.items():
            if name.endswith("_id"):
                try:
                    asset_id = UUID(val)
                    break
                except ValueError:
                    pass

        if not asset_id or asset_id not in self.data:
            return False

        asset = self[asset_id]
        flow.response = http.Response.make(
            content=asset.data,
            headers={
                "Content-Type": "application/octet-stream",
            }
        )
        return True
