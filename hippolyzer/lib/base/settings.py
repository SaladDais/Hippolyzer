"""
Copyright 2009, Linden Research, Inc.
  See NOTICE.md for previous contributors
Copyright 2021, Salad Dais
All Rights Reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from __future__ import annotations

import dataclasses
from typing import *


_T = TypeVar("_T")


class SettingDescriptor(Generic[_T]):
    __slots__ = ("name", "default")

    def __init__(self, default: Union[Callable[[], _T], _T]):
        self.default = default
        self.name: Optional[str] = None

    def __set_name__(self, owner: Settings, name: str):
        self.name = name

    def _make_default(self) -> _T:
        if callable(self.default):
            return self.default()
        return self.default

    def __get__(self, obj: Settings, owner: Optional[Type] = None) -> _T:
        val: Union[_T, dataclasses.MISSING] = obj.get_setting(self.name)
        if val is dataclasses.MISSING:
            val = self._make_default()
        return val

    def __set__(self, obj: Settings, value: _T) -> None:
        obj.set_setting(self.name, value)


class Settings:
    ENABLE_DEFERRED_PACKET_PARSING: bool = SettingDescriptor(True)

    def __init__(self):
        self._settings: Dict[str, Any] = {}

    def get_setting(self, name: str) -> Any:
        return self._settings.get(name, dataclasses.MISSING)

    def set_setting(self, name: str, val: Any):
        self._settings[name] = val
