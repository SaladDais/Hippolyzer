import os
from typing import *

from hippolyzer.lib.base.settings import Settings, SettingDescriptor

_T = TypeVar("_T")


class EnvSettingDescriptor(SettingDescriptor):
    """A setting that prefers to pull its value from the environment"""
    __slots__ = ("_env_name", "_env_callable")

    def __init__(self, default: Union[Callable[[], _T], _T], env_name: str, spec: Callable[[str], _T]):
        super().__init__(default)
        self._env_name = env_name
        self._env_callable = spec

    def __get__(self, obj, owner=None) -> _T:
        val = os.getenv(self._env_name)
        if val is not None:
            return self._env_callable(val)
        return super().__get__(obj, owner)


class ProxySettings(Settings):
    SOCKS_PROXY_PORT: int = EnvSettingDescriptor(9061, "HIPPO_UDP_PORT", int)
    HTTP_PROXY_PORT: int = EnvSettingDescriptor(9062, "HIPPO_HTTP_PORT", int)
    PROXY_BIND_ADDR: str = EnvSettingDescriptor("127.0.0.1", "HIPPO_BIND_HOST", str)
    REMOTELY_ACCESSIBLE: bool = SettingDescriptor(False)
    USE_VIEWER_OBJECT_CACHE: bool = SettingDescriptor(False)
    # Whether having the proxy do automatic internal requests objects is allowed at all
    ALLOW_AUTO_REQUEST_OBJECTS: bool = SettingDescriptor(True)
    # Whether the viewer should request any directly referenced objects it didn't know about.
    AUTOMATICALLY_REQUEST_MISSING_OBJECTS: bool = SettingDescriptor(False)
    ADDON_SCRIPTS: List[str] = SettingDescriptor(list)
    FILTERS: Dict[str, str] = SettingDescriptor(dict)
