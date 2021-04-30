from __future__ import annotations

import asyncio
import copy
import dataclasses
import os
import re
import sys
from types import TracebackType
from typing import *

import aiohttp

from hippolyzer.lib.base import llsd as llsd_lib
from hippolyzer.lib.base.helpers import proxify

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion


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


class CapsClient:
    def __init__(self, region: Optional[ProxiedRegion] = None):
        self._region: Optional[ProxiedRegion] = proxify(region)

    def request(self, method: str, cap_or_url: str, *, path: str = "", data: Any = None,
                headers: Optional[dict] = None, session: Optional[aiohttp.ClientSession] = None,
                llsd: Any = dataclasses.MISSING, params: Optional[Dict[str, Any]] = None,
                proxy: Optional[str] = None, skip_auto_headers: Optional[Sequence[str]] = None,
                **kwargs) -> _HippoSessionRequestContextManager:
        if cap_or_url.startswith("http"):
            if path:
                raise ValueError("Specifying both path and a full URL not supported")
        else:
            if self._region is None:
                raise RuntimeError(f"Need a region to request a Cap like {cap_or_url}")
            if cap_or_url not in self._region.caps:
                raise KeyError(f"{cap_or_url} is not a full URL and not a Cap")
            cap_or_url = self._region.caps[cap_or_url]
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
        # We go through the proxy by default, tack on a header letting mitmproxy know the
        # request came from us so we can tag the request as injected. The header will be popped
        # off before passing through to the server.
        ssl = kwargs.pop('ssl', None)
        # We want to proxy this through Hippolyzer
        if proxy is None:
            # Always set this so we know this request was from the proxy
            headers["X-Hippo-Injected"] = "1"
            # TODO: Have a setting for this
            proxy_port = int(os.environ.get("HIPPO_HTTP_PORT", 9062))
            proxy = f"http://127.0.0.1:{proxy_port}"
            # TODO: set up the SSLContext to validate mitmproxy's cert
            ssl = ssl or False
            # https://github.com/aio-libs/aiohttp/issues/4536
            # https://github.com/aio-libs/aiohttp/issues/4268
            # TLS + HTTP proxy is broken under proactor event loops under windows
            # qasync's event loop is based on the proactor event loop under windows.
            # aiohttp has no intention of fixing this anytime soon and I don't
            # want to screw around with qasync, so rewrite the URL to be HTTP
            # and ask mitmproxy to transparently rewrite the request URI to HTTPS
            # Will break on 3xx redirs but you can write a new qasync event loop wrapper
            # if you care about Windows. I don't.
            if sys.platform == "win32" and cap_or_url.startswith("https:"):
                headers["X-Hippo-Windows-SSL-Hack"] = "1"
                cap_or_url = re.sub(r"^https:", "http:", cap_or_url)

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
