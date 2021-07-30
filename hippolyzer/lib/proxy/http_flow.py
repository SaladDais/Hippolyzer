from __future__ import annotations

import copy
from typing import *
from typing import Optional

import mitmproxy.http
from mitmproxy.http import HTTPFlow

from hippolyzer.lib.proxy.caps import CapData

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.sessions import SessionManager


class HippoHTTPFlow:
    """
    Wrapper for Hippolyzer-side mitmproxy flows

    Hides the nastiness of writing to flow.metadata so we can pass
    state back and forth between the two proxies
    """
    __slots__ = ("flow",)

    def __init__(self, flow: HTTPFlow):
        self.flow: HTTPFlow = flow
        meta = self.flow.metadata
        meta.setdefault("taken", False)
        meta.setdefault("can_stream", True)
        meta.setdefault("response_injected", False)
        meta.setdefault("request_injected", False)
        meta.setdefault("cap_data", None)
        meta.setdefault("from_browser", False)

    @property
    def request(self) -> mitmproxy.http.Request:
        return self.flow.request

    @property
    def response(self) -> Optional[mitmproxy.http.Response]:
        return self.flow.response

    @property
    def id(self) -> str:
        return self.flow.id

    @response.setter
    def response(self, val: Optional[mitmproxy.http.Response]):
        self.flow.metadata["response_injected"] = True
        self.flow.response = val

    @property
    def response_injected(self) -> bool:
        return self.flow.metadata["response_injected"]

    @property
    def request_injected(self) -> bool:
        # Populated by mitmproxy side based on X-Hippo-Injected header
        return self.flow.metadata["request_injected"]

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.flow.metadata

    @property
    def cap_data(self) -> Optional[CapData]:
        return self.metadata["cap_data"]

    @cap_data.setter
    def cap_data(self, val: Optional[CapData]):
        self.metadata["cap_data"] = val

    @property
    def can_stream(self) -> bool:
        return self.metadata["can_stream"]

    @can_stream.setter
    def can_stream(self, val: bool):
        # can != will, only applies to asset server reqs
        self.metadata["can_stream"] = val

    @property
    def from_browser(self) -> bool:
        return self.metadata["from_browser"]

    @property
    def name(self) -> Optional[str]:
        if self.cap_data:
            return self.cap_data.cap_name
        return None

    def take(self) -> HippoHTTPFlow:
        """Don't automatically pass this flow back to mitmproxy"""
        self.metadata["taken"] = True
        return self

    @property
    def taken(self) -> bool:
        return self.metadata["taken"]

    @property
    def is_replay(self) -> bool:
        return bool(self.flow.is_replay)

    def get_state(self) -> Dict:
        flow = self.flow
        # Not serializable, so we have to pop it off to send across the wire.
        cap_data: Optional[CapData] = flow.metadata.pop("cap_data", None)
        if cap_data is not None:
            flow.metadata["cap_data_ser"] = cap_data.serialize()
        else:
            flow.metadata["cap_data_ser"] = None
        state = self.flow.get_state()
        # Shove it back on
        flow.metadata["cap_data"] = cap_data
        return state

    @classmethod
    def from_state(cls, flow_state: Dict, session_manager: Optional[SessionManager]) -> HippoHTTPFlow:
        flow: Optional[HTTPFlow] = HTTPFlow.from_state(flow_state)
        assert flow is not None
        cap_data_ser = flow.metadata.get("cap_data_ser")
        if cap_data_ser is not None:
            flow.metadata["cap_data"] = CapData.deserialize(cap_data_ser, session_manager)
        else:
            flow.metadata["cap_data"] = None
        return cls(flow)

    def copy(self) -> HippoHTTPFlow:
        # HACK: flow.copy() expects the flow to be fully JSON serializable, but
        # our cap data won't be due to the session objects. Deal with that manually.
        flow = self.flow
        cap_data = flow.metadata.pop("cap_data")
        new_flow = self.__class__(self.flow.copy())
        flow.metadata["cap_data"] = cap_data
        new_flow.metadata["cap_data"] = copy.copy(cap_data)
        return new_flow
