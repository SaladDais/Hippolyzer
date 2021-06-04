from __future__ import annotations

import asyncio
import copy
import dataclasses
from types import TracebackType
from typing import *

import aiohttp
import multidict

from hippolyzer.lib.base import llsd as llsd_lib


class CapsClientResponse(aiohttp.ClientResponse):
    """
    Not actually instantiated, used for lying to the type system
    since we'll dynamically put this onto a ClientResponse instance
    Will fail isinstance().
    """
    async def read_llsd(self) -> Any:
        raise NotImplementedError()


class _HippoSessionRequestContextManager:
    """
    _SessionRequestContextManager but with a symmetrical API

    aiohttp.request() and aiohttp.ClientSession.request() have different APIs.
    One is sync returning a context manager, one is async returning a coro.
    aiohttp.request() also doesn't accept the arguments that we need for custom
    SSL contexts. To deal with requests that have existing sessions and those without,
    just give them both the same wrapper and don't close the session on context manager
    exit if it wasn't our session.
    """
    __slots__ = ("_coro", "_resp", "_session", "_session_owned")

    def __init__(
        self,
        coro: Coroutine[asyncio.Future[Any], None, aiohttp.ClientResponse],
        session: aiohttp.ClientSession,
        session_owned: bool = True,
    ) -> None:
        self._coro = coro
        self._resp: Optional[aiohttp.ClientResponse] = None
        self._session = session
        self._session_owned = session_owned

    async def __aenter__(self) -> CapsClientResponse:
        try:
            self._resp = await self._coro

            # We don't control creation of the ClientResponse, so tack on
            # a convenience method for reading LLSD.
            async def _read_llsd():
                return llsd_lib.parse_xml(await self._resp.read())
            self._resp.read_llsd = _read_llsd
        except BaseException:
            if self._session_owned:
                await self._session.close()
            raise
        else:
            # intentionally fooling the type system
            return self._resp  # type: ignore

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        assert self._resp is not None
        self._resp.close()
        if self._session_owned:
            await self._session.close()


CAPS_DICT = Union[
    Mapping[str, str],
    multidict.MultiDict[str],
]


class CapsClient:
    def __init__(self, caps: Optional[CAPS_DICT] = None):
        self._caps = caps

    def _request_fixups(self, cap_or_url: str, headers: Dict, proxy: Optional[bool], ssl: Any):
        return cap_or_url, headers, proxy, ssl

    def _get_caps(self) -> Optional[CAPS_DICT]:
        return self._caps

    def request(self, method: str, cap_or_url: str, *, path: str = "", data: Any = None,
                headers: Optional[Dict] = None, session: Optional[aiohttp.ClientSession] = None,
                llsd: Any = dataclasses.MISSING, params: Optional[Dict[str, Any]] = None,
                proxy: Optional[str] = None, skip_auto_headers: Optional[Sequence[str]] = None,
                **kwargs) -> _HippoSessionRequestContextManager:
        if cap_or_url.startswith("http"):
            if path:
                raise ValueError("Specifying both path and a full URL not supported")
        else:
            caps = self._get_caps()
            if caps is None:
                raise RuntimeError(f"Need a caps dict to request a Cap like {cap_or_url}")
            if cap_or_url not in caps:
                raise KeyError(f"{cap_or_url} is not a full URL and not a Cap")
            cap_or_url = caps[cap_or_url]
        if path:
            cap_or_url += path

        if params is not None:
            for pname, pval in params.items():
                if not isinstance(pval, str):
                    params[pname] = str(pval)

        session_owned = False
        # Use an existing session if we have one to take advantage of connection pooling
        # otherwise create one
        if session is None:
            session_owned = True
            session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(force_close=True),
                connector_owner=True
            )

        if headers is None:
            headers = {}
        else:
            headers = copy.copy(headers)

        # Use sentinel val so explicit `None` can be passed
        if llsd is not dataclasses.MISSING:
            data = llsd_lib.format_xml(llsd)
        # Sometimes needed even on GETs.
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/llsd+xml"
        # Always present, usually ignored by the server.
        if "Accept" not in headers:
            headers["Accept"] = "application/llsd+xml"
        # Ask to keep the connection open if we're sharing a session
        if not session_owned:
            headers["Connection"] = "keep-alive"
            headers["Keep-alive"] = "300"

        ssl = kwargs.pop('ssl', None)
        cap_or_url, headers, proxy, ssl = self._request_fixups(cap_or_url, headers, proxy, ssl)

        resp = session._request(method, cap_or_url, data=data, headers=headers,  # noqa: need internal call
                                params=params, ssl=ssl, proxy=proxy,
                                skip_auto_headers=skip_auto_headers or ("User-Agent",), **kwargs)
        return _HippoSessionRequestContextManager(resp, session, session_owned=session_owned)

    def get(self, cap_or_url: str, *, path: str = "", headers: Optional[dict] = None,
            session: Optional[aiohttp.ClientSession] = None, params: Optional[Dict[str, Any]] = None,
            proxy: Optional[str] = None, **kwargs) -> _HippoSessionRequestContextManager:
        return self.request("GET", cap_or_url=cap_or_url, path=path, headers=headers,
                            session=session, params=params, proxy=proxy, **kwargs)

    def post(self, cap_or_url: str, *, path: str = "", data: Any = None,
             headers: Optional[dict] = None, session: Optional[aiohttp.ClientSession] = None,
             llsd: Any = dataclasses.MISSING, params: Optional[Dict[str, Any]] = None,
             proxy: Optional[str] = None, **kwargs) -> _HippoSessionRequestContextManager:
        return self.request("POST", cap_or_url=cap_or_url, path=path, headers=headers, data=data,
                            llsd=llsd, session=session, params=params, proxy=proxy, **kwargs)

    def put(self, cap_or_url: str, *, path: str = "", data: Any = None,
            headers: Optional[dict] = None, session: Optional[aiohttp.ClientSession] = None,
            llsd: Any = dataclasses.MISSING, params: Optional[Dict[str, Any]] = None,
            proxy: Optional[str] = None, **kwargs) -> _HippoSessionRequestContextManager:
        return self.request("PUT", cap_or_url=cap_or_url, path=path, headers=headers, data=data,
                            llsd=llsd, session=session, params=params, proxy=proxy, **kwargs)
