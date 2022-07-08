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

import ast
import enum
import hashlib
from logging import getLogger
import uuid
import math
from typing import *

import recordclass

logger = getLogger('hippolyzer.lib.base.datatypes')


class _IterableStub:
    """Only to help type system realize TupleCoords are iterable"""
    __iter__: Callable


class TupleCoord(recordclass.datatuple, _IterableStub):  # type: ignore
    __options__ = {
        "fast_new": False,
    }

    def __init__(self, *args):
        pass

    @classmethod
    def parse(cls, s):
        s = s.replace('<', '(').replace('>', ')')
        return cls(*ast.literal_eval(s))

    def data(self, wanted_components=None) -> tuple:
        raise NotImplementedError()

    def __copy__(self):
        return self.__class__(*self)

    def __abs__(self):
        return self.__class__(*(abs(x) for x in self))

    def __neg__(self):
        return self.__class__(*(-x for x in self))

    def __add__(self, other):
        return self.__class__(*(x + y for x, y in zip(self, other)))

    def __sub__(self, other):
        return self.__class__(*(x - y for x, y in zip(self, other)))

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            other = (other,) * len(self)
        return self.__class__(*(x * y for x, y in zip(self, other)))

    def __truediv__(self, other):
        if isinstance(other, (float, int)):
            other = (other,) * len(self)
        return self.__class__(*(x / y for x, y in zip(self, other)))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return other == self.data()
        return other.data() == self.data()

    def __gt__(self, other):
        return all(x > y for x, y in zip(self, other))

    def __lt__(self, other):
        return all(x < y for x, y in zip(self, other))

    def __ge__(self, other):
        return all(x >= y for x, y in zip(self, other))

    def __le__(self, other):
        return all(x <= y for x, y in zip(self, other))

    def __repr__(self):
        return f"{self.__class__.__name__}{tuple(self)!r}"

    def __str__(self):
        return f"<{repr(tuple(self))[1:-1]}>"

    def interpolate(self, lower, upper):
        # assumes each component is 0.0<->1.0
        # Should be replaced for classes where linterp makes no sense
        return self.__class__(
            *((l * (1. - t) + u * t) for l, u, t in zip(lower, upper, self))
        )

    def within_domain(self, lower, upper):
        # each component will be 0.0<->1.0
        return self.__class__(
            *(((t - l) / (u - l)) for l, u, t in zip(lower, upper, self))
        )


class Vector3(TupleCoord):
    """ represents a vector as a tuple"""

    X: float = 0.0
    Y: float = 0.0
    Z: float = 0.0

    def __init__(self, X=0.0, Y=0.0, Z=0.0):
        super().__init__()
        self.X = float(X)
        self.Y = float(Y)
        self.Z = float(Z)

    def data(self, wanted_components=None):
        return self.X, self.Y, self.Z

    def rotated(self, rot: "Quaternion") -> "Vector3":
        rw = -rot.X * self.X - rot.Y * self.Y - rot.Z * self.Z
        rx = rot.W * self.X + rot.Y * self.Z - rot.Z * self.Y
        ry = rot.W * self.Y + rot.Z * self.X - rot.X * self.Z
        rz = rot.W * self.Z + rot.X * self.Y - rot.Y * self.X

        return Vector3(
            X=-rw * rot.X + rx * rot.W - ry * rot.Z + rz * rot.Y,
            Y=-rw * rot.Y + ry * rot.W - rz * rot.X + rx * rot.Z,
            Z=-rw * rot.Z + rz * rot.W - rx * rot.Y + ry * rot.X,
        )

    @staticmethod
    def dist_squared(a, b):
        x = a.X - b.X
        y = a.Y - b.Y
        z = a.Z - b.Z
        return x * x + y * y + z * z

    @classmethod
    def dist(cls, a, b):
        return math.sqrt(cls.dist_squared(a, b))


class Vector2(TupleCoord):
    X: float = 0.0
    Y: float = 0.0

    def __init__(self, X=0.0, Y=0.0):
        super().__init__()
        self.X = float(X)
        self.Y = float(Y)

    def data(self, wanted_components=None):
        return self.X, self.Y


class Vector4(TupleCoord):
    X: float = 0.0
    Y: float = 0.0
    Z: float = 0.0
    W: float = 0.0

    def __init__(self, X=0.0, Y=0.0, Z=0.0, W=0.0):
        super().__init__()
        self.X = float(X)
        self.Y = float(Y)
        self.Z = float(Z)
        self.W = float(W)

    def data(self, wanted_components=None):
        return self.X, self.Y, self.Z, self.W


class Quaternion(TupleCoord):
    """ represents a quaternion as a tuple"""
    X: float = 0.0
    Y: float = 0.0
    Z: float = 0.0
    W: float = 1.0

    def __init__(self, X=0.0, Y=0.0, Z=0.0, W=None):
        super().__init__()
        self.X = float(X)
        self.Y = float(Y)
        self.Z = float(Z)

        # Unpack from vector3
        if W is None:
            t = 1.0 - (X * X + Y * Y + Z * Z)
            if t > 0:
                self.W = math.sqrt(t)
            else:
                # Avoid sqrt(-episilon)
                self.W = 0.0
        else:
            self.W = float(W)

    def __mul__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(
                other.W * self.X + other.X * self.W + other.Y * self.Z - other.Z * self.Y,
                other.W * self.Y + other.Y * self.W + other.Z * self.X - other.X * self.Z,
                other.W * self.Z + other.Z * self.W + other.X * self.Y - other.Y * self.X,
                other.W * self.W - other.X * self.X - other.Y * self.Y - other.Z * self.Z
            )
        return super().__mul__(other)

    @classmethod
    def from_euler(cls, roll, pitch, yaw, degrees=False):
        if degrees:
            roll *= math.pi / 180
            pitch *= math.pi / 180
            yaw *= math.pi / 180

        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)

        w = cy * cr * cp + sy * sr * sp
        x = cy * sr * cp - sy * cr * sp
        y = cy * cr * sp + sy * sr * cp
        z = sy * cr * cp - cy * sr * sp

        return cls(X=x, Y=y, Z=z, W=w)

    def data(self, wanted_components=None):
        if wanted_components == 3:
            return self.X, self.Y, self.Z
        return self.X, self.Y, self.Z, self.W


class UUID(uuid.UUID):
    _NULL_UUID_STR = '00000000-0000-0000-0000-000000000000'
    ZERO: UUID
    __slots__ = ()

    def __init__(self, val: Union[uuid.UUID, str, None] = None, bytes=None, int=None):
        if isinstance(val, uuid.UUID):
            val = str(val)
        if val is None and bytes is None and int is None:
            val = self._NULL_UUID_STR
        super().__init__(hex=val, bytes=bytes, int=int)

    @classmethod
    def random(cls):
        return cls(uuid.uuid4())

    @classmethod
    def combine(cls, first: "UUID", other: "UUID"):
        h = hashlib.new("md5")
        h.update(first.bytes)
        h.update(other.bytes)
        return UUID(bytes=h.digest())

    def __xor__(self, other: "UUID"):
        return self.__class__(int=self.int ^ other.int)


UUID.ZERO = UUID()


class JankStringyBytes(bytes):
    """
    Treat bytes as UTF8 if used in string context

    Sinful, but necessary evil for now since templates don't specify what's
    binary and what's a string. There are also certain fields where the value
    may be either binary _or_ a string, depending on the context.
    """
    __slots__ = ()

    def __str__(self):
        return self.rstrip(b"\x00").decode("utf8", errors="replace")

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        return super().__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, item):
        if isinstance(item, str):
            return item in str(self)
        return item in bytes(self)


class RawBytes(bytes):
    __slots__ = ()
    pass


_T = TypeVar("_T")


class Pretty(Generic[_T]):
    """Wrapper for var values so Messages will know to serialize"""
    __slots__ = ("value",)

    def __init__(self, value: _T):
        self.value: _T = value


class StringEnum(str, enum.Enum):
    def __str__(self):
        return self.value


class IntEnum(enum.IntEnum):
    # Give a special repr() that'll eval in a REPL.
    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class IntFlag(enum.IntFlag):
    def __repr__(self):
        # Make an ORed together version of the flags based on the POD version
        flags = flags_to_pod(type(self), self)
        flags = " | ".join(
            (f"{self.__class__.__name__}.{v}" if isinstance(v, str) else str(v))
            for v in flags
        )
        return f"({flags})"


def flags_to_pod(flag_cls: Type[enum.IntFlag], val: int) -> Tuple[Union[str, int], ...]:
    # Shove any bits not represented in the IntFlag into an int
    left_over = val
    for flag in iter(flag_cls):
        left_over &= ~flag.value
    extra = (int(left_over),) if left_over else ()
    return tuple(flag.name for flag in iter(flag_cls) if val & flag.value) + extra


class TaggedUnion(recordclass.datatuple):  # type: ignore
    tag: Any
    value: Any


__all__ = [
    "Vector3", "Vector4", "Vector2", "Quaternion", "TupleCoord",
    "UUID", "RawBytes", "StringEnum", "JankStringyBytes", "TaggedUnion",
    "IntEnum", "IntFlag", "flags_to_pod", "Pretty"
]
