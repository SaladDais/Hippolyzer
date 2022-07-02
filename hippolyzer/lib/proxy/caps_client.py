from __future__ import annotations

import re
import sys
from typing import *

from hippolyzer.lib.base.network.caps_client import CapsClient, CAPS_DICT
from hippolyzer.lib.proxy.settings import ProxySettings

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion


class ProxyCapsClient(CapsClient):
    def __init__(self, settings: ProxySettings, region: Optional[ProxiedRegion] = None):
        super().__init__(None)
        self._region = region
        self._settings = settings

    def _get_caps(self) -> Optional[CAPS_DICT]:
        if not self._region:
            return None
        return self._region.cap_urls

    def _request_fixups(self, cap_or_url: str, headers: Dict, proxy: Optional[bool], ssl: Any):
        # We want to proxy this through Hippolyzer
        if proxy is None:
            # We go through the proxy by default, tack on a header letting mitmproxy know the
            # request came from us so we can tag the request as injected. The header will be popped
            # off before passing through to the server.
            if "X-Hippo-Injected" not in headers:
                headers["X-Hippo-Injected"] = "1"
            proxy_port = self._settings.HTTP_PROXY_PORT
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
        return cap_or_url, headers, proxy, ssl
