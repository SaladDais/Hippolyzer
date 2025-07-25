from __future__ import annotations

import asyncio
import codecs
import functools
import logging
import os

import lazy_object_proxy
import pkg_resources
import re
import weakref
from pprint import PrettyPrinter
from typing import *

from hippolyzer.lib.base.multidict import MultiDict


def _with_patched_multidict(f):
    @functools.wraps(f)
    def _wrapper(*args, **kwargs):
        # There's no way to tell pprint "hey, this is a dict,
        # this is how you access its items." A lot of the formatting logic
        # is in the module-level `_safe_repr()` which we don't want to mess with.
        # Instead, pretend our MultiDict has dict's __repr__ while we're inside
        # calls to pprint. Hooray.
        orig_repr = MultiDict.__repr__
        if orig_repr is dict.__repr__:
            return f(*args, **kwargs)

        MultiDict.__repr__ = dict.__repr__
        try:
            return f(*args, **kwargs)
        finally:
            MultiDict.__repr__ = orig_repr

    return _wrapper


class HippoPrettyPrinter(PrettyPrinter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, sort_dicts=False, **kwargs)

    # Only touch the public APIs, the private pprint APIs are unstable.
    format = _with_patched_multidict(PrettyPrinter.format)
    pprint = _with_patched_multidict(PrettyPrinter.pprint)
    _base_pformat = _with_patched_multidict(PrettyPrinter.pformat)

    def _str_format(self, obj: Union[str, bytes]):
        """
        Make multi-line string literal repr()s actually multi-line

        but only if it'll actually make them easier to read
        """
        sep: Union[str, bytes]
        if isinstance(obj, str):
            sep = "\n"
        else:
            sep = b"\n"

        if obj.count(sep) < 5:
            return self._base_pformat(obj)

        split = []
        while obj:
            left, mid, obj = obj.partition(sep)
            split.append(left + mid)

        reprs = "\n".join(repr(x) for x in split)
        return f"({reprs})"

    def pformat(self, obj: object, *args, **kwargs) -> str:
        # Unwrap lazy object proxies before pprinting them
        if isinstance(obj, lazy_object_proxy.Proxy):
            obj = obj.__wrapped__
        if isinstance(obj, (bytes, str)):
            return self._str_format(obj)
        return self._base_pformat(obj, *args, **kwargs)


class BitField:
    """
    Utility class for packing a bitfield into an arbitrarily large integer

    Used like BitField({"name1": num_bits, "name2": num_bits, ...})
    """
    def __init__(self, schema: Dict[str, int], shift: bool = True):
        self._schema = schema
        self.shift = shift

    def pack(self, vals):
        packed = 0
        cur_bit = 0
        for name, bits in self._schema.items():
            val = vals[name]
            mask = self._bits_mask(bits)
            if self.shift:
                if val > mask:
                    raise ValueError("%r larger than max %r" % (val, mask))
                packed |= val << cur_bit
            else:
                mask = (mask << cur_bit)
                if val != val & mask:
                    raise ValueError("%r doesn't fit within mask %r" % (val, mask))
                packed |= val
            cur_bit += bits
        return packed

    def unpack(self, packed):
        vals = {}
        cur_bit = 0
        for name, bits in self._schema.items():
            val = (packed >> cur_bit) & self._bits_mask(bits)
            # We're not supposed to return the un-shifted val, so shift back.
            if not self.shift:
                val = val << cur_bit
            vals[name] = val
            cur_bit += bits
        return vals

    @staticmethod
    def _bits_mask(bits):
        return (2 ** bits) - 1


_T = TypeVar("_T")


def proxify(obj: Union[Callable[[], _T], weakref.ReferenceType, _T]) -> _T:
    if isinstance(obj, weakref.ReferenceType):
        obj = obj()
    if obj is not None and not isinstance(obj, weakref.ProxyTypes):
        return weakref.proxy(obj)
    return obj


class BiDiDict(Generic[_T]):
    """Dictionary for bidirectional lookups"""
    def __init__(self, values: Dict[_T, _T]):
        self.forward = {**values}
        self.backward = {value: key for (key, value) in values.items()}


def bytes_unescape(val: bytes) -> bytes:
    # Only in CPython. bytes -> bytes with escape decoding.
    # https://stackoverflow.com/a/23151714
    return codecs.escape_decode(val)[0]  # type: ignore


def bytes_escape(val: bytes) -> bytes:
    # Try to keep newlines as-is
    return re.sub(rb"(?<!\\)\\n", b"\n", codecs.escape_encode(val)[0])  # type: ignore


def get_resource_filename(resource_filename: str):
    return pkg_resources.resource_filename("hippolyzer", resource_filename)


def to_chunks(chunkable: Sequence[_T], chunk_size: int) -> Generator[Sequence[_T], None, None]:
    while chunkable:
        yield chunkable[:chunk_size]
        chunkable = chunkable[chunk_size:]


def get_mtime(path):
    try:
        return os.stat(path).st_mtime
    except:
        return None


def fut_logger(name: str, logger: logging.Logger, fut: asyncio.Future, *args) -> None:
    """Callback suitable for exception logging in `Future.add_done_callback()`"""
    if not fut.cancelled() and fut.exception():
        if isinstance(fut.exception(), asyncio.CancelledError):
            # Don't really care if the task was just cancelled
            return
        logger.exception(f"Failed in task for {name}", exc_info=fut.exception())


def add_future_logger(
        fut: asyncio.Future,
        name: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
):
    """Add a logger to Futures that will never be directly `await`ed, logging exceptions"""
    fut.add_done_callback(functools.partial(fut_logger, name, logger or logging.getLogger()))


def create_logged_task(
        coro: Coroutine,
        name: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
) -> asyncio.Task:
    task = asyncio.create_task(coro, name=name)
    add_future_logger(task, name, logger)
    return task


def reorient_coord(coord, new_orientation, min_val: int | float = 0):
    """
    Reorient a coordinate instance such that its components are negated and transposed appropriately.

    For ex:
        reorient_coord((1,2,3), (3,-2,-1)) == (3,-2,-1)
    """
    min_val = abs(min_val)
    coords = []
    for axis in new_orientation:
        axis_idx = abs(axis) - 1
        new_coord = coord[axis_idx] if axis >= 0 else min_val - coord[axis_idx]
        coords.append(new_coord)
    if coord.__class__ in (list, tuple):
        return coord.__class__(coords)
    return coord.__class__(*coords)
