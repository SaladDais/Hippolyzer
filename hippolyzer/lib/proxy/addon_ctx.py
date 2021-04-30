"""
Global context for use within Addon callbacks
"""
from __future__ import annotations

import contextlib
from contextvars import ContextVar, Token
from typing import *

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion
    from hippolyzer.lib.proxy.sessions import Session

# By using ContextVar, coroutines retain the context as it was when
# they were created.
session: ContextVar[Optional[Session]] = ContextVar("session", default=None)
region: ContextVar[Optional[ProxiedRegion]] = ContextVar("region", default=None)


@contextlib.contextmanager
def push(new_session: Optional[Session] = None, new_region: Optional[ProxiedRegion] = None):
    session_token: Token = session.set(new_session)
    region_token: Token = region.set(new_region)
    try:
        yield
    finally:
        session.reset(session_token)
        region.reset(region_token)
