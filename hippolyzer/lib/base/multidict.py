"""
Main Multidict Implementation:
Copyright 2007 Pallets

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1.  Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

2.  Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

3.  Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Dict View Implementations:
Copyright 2016-2017 Andrew Svetlov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Copyright 2021 Salad Dais
This specific file is BSD 3-clause.
"""

# This is a heavily modified version of Werkzeug's multidict implementation,
# mashed together with the dict views from aio-lib's multidict implementation.
# We needed a multidict that would support all hashable types as keys.
# aio-lib's MultiDict does not. Werkzeug's does, but doesn't behave like a proper
# `dict` subclass in many cases which breaks some consumers, mostly around
# Keys/Items/ValuesViews. I wish this file wasn't necessary, but here we are.

from typing import *
from copy import deepcopy


# https://github.com/aio-libs/multidict/blob/3aabe3b9f1c0f110d4bae0c9333f25ab6f2756f1/multidict/_multidict_py.py#L29
class _Iter:
    __slots__ = ("_size", "_iter")

    def __init__(self, size, iterator):
        self._size = size
        self._iter = iterator

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._iter)

    def __length_hint__(self):
        return self._size


class _ViewBase:
    def __init__(self, impl):
        self._impl: "MultiDict" = impl
        # self._version = impl._version

    def __len__(self):
        return len(self._impl)


class _ItemsView(_ViewBase, ItemsView):
    def __init__(self, impl, multi=False):
        super().__init__(impl)
        self._multi = multi

    def __contains__(self, item):
        assert isinstance(item, tuple) or isinstance(item, list)
        assert len(item) == 2
        for k, v in self._impl.gen_items(multi=True):
            if item[0] == k and item[1] == v:
                return True
        return False

    def __iter__(self):
        return _Iter(len(self), self._iter())

    def _iter(self):
        for k, v in self._impl.gen_items(multi=self._multi):
            # NB: No iterator invalidation checks, hopefully the
            # underlying iterators from the dict & list get invalidated.
            yield k, v

    def __repr__(self):
        lst = []
        for item in self._impl.gen_items(multi=True):
            lst.append("{!r}: {!r}".format(item[0], item[1]))
        body = ", ".join(lst)
        return "{}({})".format(self.__class__.__name__, body)


class _ValuesView(_ViewBase, ValuesView):
    def __contains__(self, value):
        for item in self._impl.gen_items(multi=True):
            if item[1] == value:
                return True
        return False

    def __iter__(self):
        return _Iter(len(self), self._iter())

    def _iter(self):
        for item in self._impl.gen_items(multi=True):
            yield item[1]

    def __repr__(self):
        lst = []
        for item in self._impl.gen_items(multi=True):
            lst.append("{!r}".format(item[1]))
        body = ", ".join(lst)
        return "{}({})".format(self.__class__.__name__, body)


VALID_KEY = Union[Hashable, None]
_K = TypeVar("K", bound=VALID_KEY)
_T = TypeVar("T")


class _Missing:
    def __repr__(self):
        return "no value"

    def __reduce__(self):
        return "_missing"


_missing = _Missing()


def iter_multi_items(mapping: Union[Mapping, Iterable]) -> Iterator[Any]:
    """Iterates over the items of a mapping yielding keys and values
    without dropping any from more complex structures.
    """
    if isinstance(mapping, MultiDict):
        yield from mapping.items(multi=True)
    elif isinstance(mapping, dict):
        for key, value in mapping.items():
            if isinstance(value, (tuple, list)):
                for v in value:
                    yield key, v
            else:
                yield key, value
    else:
        yield from mapping


class MultiDict(Dict[_K, _T]):
    """A :class:`MultiDict` is a dictionary subclass customized to deal with
    multiple values for the same key which is for example used by the parsing
    functions in the wrappers.  This is necessary because some HTML form
    elements pass multiple values for the same key.
    :class:`MultiDict` implements all standard dictionary methods.
    Internally, it saves all values for a key as a list, but the standard dict
    access methods will only return the first value for a key. If you want to
    gain access to the other values, too, you have to use the `list` methods as
    explained below.
    Basic Usage:
    >>> d = MultiDict([('a', 'b'), ('a', 'c')])
    >>> d
    MultiDict([('a', 'b'), ('a', 'c')])
    >>> d['a']
    'b'
    >>> d.getlist('a')
    ['b', 'c']
    >>> 'a' in d
    True
    It behaves like a normal dict thus all dict functions will only return the
    first value when multiple values for one key are found.
    From Werkzeug 0.3 onwards, the `KeyError` raised by this class is also a
    subclass of the :exc:`~exceptions.BadRequest` HTTP exception and will
    render a page for a ``400 BAD REQUEST`` if caught in a catch-all for HTTP
    exceptions.
    A :class:`MultiDict` can be constructed from an iterable of
    ``(key, value)`` tuples, a dict, a :class:`MultiDict` or from Werkzeug 0.2
    onwards some keyword parameters.
    :param mapping: the initial value for the :class:`MultiDict`.  Either a
                    regular dict, an iterable of ``(key, value)`` tuples
                    or `None`.
    """

    def __init__(self, mapping: Optional[Any] = None) -> None:
        if isinstance(mapping, MultiDict):
            dict.__init__(self, ((k, l[:]) for k, l in mapping.lists()))
        elif isinstance(mapping, dict):
            tmp = {}
            for key, value in mapping.items():
                if isinstance(value, (tuple, list)):
                    if len(value) == 0:
                        continue
                    value = list(value)
                else:
                    value = [value]
                tmp[key] = value
            dict.__init__(self, tmp)
        else:
            tmp = {}
            for key, value in mapping or ():
                tmp.setdefault(key, []).append(value)
            dict.__init__(self, tmp)

    def __getstate__(self) -> Dict[bytes, Union[List[int], List[bytes]]]:
        return dict(self.lists())  # noqa

    def __setstate__(self, value: Dict[Any, Any]) -> None:
        dict.clear(self)
        dict.update(self, value)

    def __len__(self):
        size = 0
        for key in dict.keys(self):
            size += len(dict.__getitem__(self, key))
        return size

    def __getitem__(self, key: _K) -> _T:
        """Return the first data value for this key;
        raises KeyError if not found.
        :param key: The key to be looked up.
        :raise KeyError: if the key does not exist.
        """

        if key in self:
            lst = dict.__getitem__(self, key)
            if len(lst) > 0:
                return lst[0]
        raise KeyError(key)

    def __setitem__(self, key: _K, value: _T) -> None:
        """Like :meth:`add` but removes an existing key first.
        :param key: the key for the value.
        :param value: the value to set.
        """
        dict.__setitem__(self, key, [value])

    def add(self, key: _K, value: _T) -> None:
        """Adds a new value for the key.
        .. versionadded:: 0.6
        :param key: the key for the value.
        :param value: the value to add.
        """
        dict.setdefault(self, key, []).append(value)

    def get(self, key: _K, default: Any = None) -> Union[_T, Any]:
        try:
            return self[key]
        except KeyError:
            return default

    def getlist(
        self, key: _K, elem_type: Optional[Callable[[Any], _T]] = None
    ) -> List[Union[_T, Any]]:
        """Return the list of items for a given key. If that key is not in the
        `MultiDict`, the return value will be an empty list.  Just like `get`,
        `getlist` accepts a `type` parameter.  All items will be converted
        with the callable defined there.
        :param key: The key to be looked up.
        :param elem_type: A callable that is used to cast the value in the
                          :class:`MultiDict`.  If a :exc:`ValueError` is raised
                          by this callable the value will be removed from the list.
        :return: a :class:`list` of all the values for the key.
        """
        try:
            rv = dict.__getitem__(self, key)
        except KeyError:
            return []
        if elem_type is None:
            return list(rv)
        result = []
        for item in rv:
            try:
                result.append(elem_type(item))
            except ValueError:
                pass
        return result

    def setlist(self, key: _K, new_list: List[_T]) -> None:
        """Remove the old values for a key and add new ones.  Note that the list
        you pass the values in will be shallow-copied before it is inserted in
        the dictionary.
        >>> d = MultiDict()
        >>> d.setlist('foo', ['1', '2'])
        >>> d['foo']
        '1'
        >>> d.getlist('foo')
        ['1', '2']
        :param key: The key for which the values are set.
        :param new_list: An iterable with the new values for the key.  Old values
                         are removed first.
        """
        dict.__setitem__(self, key, list(new_list))

    def setdefault(self, key: _K, default: Optional[_T] = None) -> Optional[_T]:
        """Returns the value for the key if it is in the dict, otherwise it
        returns `default` and sets that value for `key`.
        :param key: The key to be looked up.
        :param default: The default value to be returned if the key is not
                        in the dict.  If not further specified it's `None`.
        """
        if key not in self:
            self[key] = default
        else:
            default = self[key]
        return default

    def setlistdefault(
        self, key: _K, default_list: Optional[List[_T]] = None
    ) -> List[_T]:
        """Like `setdefault` but sets multiple values.  The list returned
        is not a copy, but the list that is actually used internally.  This
        means that you can put new values into the dict by appending items
        to the list:
        >>> d = MultiDict({"foo": 1})
        >>> d.setlistdefault("foo").extend([2, 3])
        >>> d.getlist("foo")
        [1, 2, 3]
        :param key: The key to be looked up.
        :param default_list: An iterable of default values.  It is either copied
                             (in case it was a list) or converted into a list
                             before returned.
        :return: a :class:`list`
        """
        if key not in self:
            default_list = list(default_list or ())
            dict.__setitem__(self, key, default_list)
        else:
            default_list = dict.__getitem__(self, key)
        return default_list

    def keys(self) -> KeysView[_K]:
        return dict.keys(self)

    def items(
            self, multi: bool = True
    ) -> ItemsView[_K, _T]:
        return _ItemsView(self, multi=multi)

    def gen_items(
        self, multi: bool = False
    ) -> Iterator[Tuple[_K, _T]]:
        """Return an iterator of ``(key, value)`` pairs.
        :param multi: If set to `True` the iterator returned will have a pair
                      for each value of each key.  Otherwise it will only
                      contain pairs for the first value of each key.
        """
        for key, values in dict.items(self):
            if multi:
                for value in values:
                    yield key, value
            else:
                yield key, values[0]

    def lists(self,) -> Iterator[Tuple[_K, List[_T]]]:
        """Return a iterator of ``(key, values)`` pairs, where values is the list
        of all values associated with the key."""
        for key, values in dict.items(self):
            yield key, list(values)

    def values(self) -> ValuesView[_T]:
        """Returns an iterator of the first value on every key's value list."""
        return _ValuesView(self)

    def listvalues(self):
        """Return an iterator of all values associated with a key.  Zipping
        :meth:`keys` and this is the same as calling :meth:`lists`:
        >>> d = MultiDict({"foo": [1, 2, 3]})
        >>> zip(d.keys(), d.listvalues()) == d.lists()
        True
        """
        return dict.values(self)

    def copy(self) -> Union["MultiDict", "OrderedMultiDict"]:
        """Return a shallow copy of this object."""
        return self.__class__(self)

    def deepcopy(self, memo: None = None) -> Union["MultiDict", "OrderedMultiDict"]:
        """Return a deep copy of this object."""
        return self.__class__(deepcopy(self.to_dict(flat=False), memo))  # noqa

    def to_dict(self, flat: bool = True) -> Dict[_K, _T]:
        """Return the contents as regular dict.  If `flat` is `True` the
        returned dict will only have the first item present, if `flat` is
        `False` all values will be returned as lists.
        :param flat: If set to `False` the dict returned will have lists
                     with all the values in it.  Otherwise it will only
                     contain the first value for each key.
        :return: a :class:`dict`
        """
        if flat:
            return dict(self.items(multi=False))
        return dict(self.lists())

    def update(self, *args, **kwargs) -> None:
        """update() extends rather than replaces existing key lists:
        >>> a = MultiDict({'x': 1})
        >>> b = MultiDict({'x': 2, 'y': 3})
        >>> a.update(b,)
        >>> a
        MultiDict([('y', 3), ('x', 1), ('x', 2)])
        If the value list for a key in ``other_dict`` is empty, no new values
        will be added to the dict and the key will not be created:
        >>> x = {'empty_list': []}
        >>> y = MultiDict()
        >>> y.update(x,)
        >>> y
        MultiDict([])
        """
        if len(args) > 1:
            raise ValueError("Only one *arg supported for update()")
        if args and kwargs:
            raise ValueError("Must specify **kwargs or one *arg")

        if args:
            for key, value in iter_multi_items(args[0]):
                self.add(key, value)
        if kwargs:
            for key, value in kwargs.items():
                self.add(key, value)

    def pop(
        self, key: _K, default: Union["_Missing", Any] = _missing
    ) -> Union[_T, Any]:
        """Pop the first item for a list on the dict.  Afterwards the
        key is removed from the dict, so additional values are discarded:
        >>> d = MultiDict({"foo": [1, 2, 3]})
        >>> d.pop("foo")
        1
        >>> "foo" in d
        False
        :param key: the key to pop.
        :param default: if provided the value to return if the key was
                        not in the dictionary.
        """
        try:
            lst = dict.pop(self, key)

            if len(lst) == 0:
                raise KeyError(key)

            return lst[0]
        except KeyError:
            if default is not _missing:
                return default
            raise KeyError(key)

    def popitem(self) -> Tuple[_K, _T]:
        """Pop an item from the dict."""
        item = dict.popitem(self)

        if len(item[1]) == 0:
            raise KeyError(item)

        return item[0], item[1][0]

    def poplist(self, key: _K) -> List[_T]:
        """Pop the list for a key from the dict.  If the key is not in the dict
        an empty list is returned.
        .. versionchanged:: 0.5
           If the key does no longer exist a list is returned instead of
           raising an error.
        """
        return dict.pop(self, key, [])

    def popitemlist(self) -> Tuple[_K, List[_T]]:
        """Pop a ``(key, list)`` tuple from the dict."""
        return dict.popitem(self)

    def __copy__(self) -> Union["MultiDict", "OrderedMultiDict"]:
        return self.copy()

    def __deepcopy__(
        self, memo: Dict[Any, Any]
    ) -> Union["MultiDict", "OrderedMultiDict"]:
        return self.deepcopy(memo=memo)  # noqa

    def __repr__(self) -> str:
        return f"{type(self).__name__}({list(self.items(multi=True))!r})"


class _OMDBucket:
    """Wraps values in the :class:`OrderedMultiDict`.  This makes it
    possible to keep an order over multiple different keys.  It requires
    a lot of extra memory and slows down access a lot, but makes it
    possible to access elements in O(1) and iterate in O(n).
    """

    __slots__ = ("prev", "key", "value", "next")

    def __init__(
        self,
        omd: Union["OrderedMultiDict"],
        key: VALID_KEY,
        value: Any,
    ) -> None:
        # I guess this is some sort of `friend` class.
        self.prev = omd._last_bucket  # noqa
        self.key = key
        self.value = value
        self.next = None

        if omd._first_bucket is None:  # noqa
            omd._first_bucket = self  # noqa
        if omd._last_bucket is not None:  # noqa
            omd._last_bucket.next = self  # noqa
        omd._last_bucket = self  # noqa

    def unlink(self, omd: "OrderedMultiDict") -> None:
        if self.prev:
            self.prev.next = self.next
        if self.next:
            self.next.prev = self.prev
        if omd._first_bucket is self:  # noqa
            omd._first_bucket = self.next  # noqa
        if omd._last_bucket is self:  # noqa
            omd._last_bucket = self.prev  # noqa


class OrderedMultiDict(MultiDict[_K, _T]):
    """Works like a regular :class:`MultiDict` but preserves the
    order of the fields.  To convert the ordered multi dict into a
    list you can use the :meth:`items` method and pass it ``multi=True``.
    In general an :class:`OrderedMultiDict` is an order of magnitude
    slower than a :class:`MultiDict`.
    .. admonition:: note
       Due to a limitation in Python you cannot convert an ordered
       multi dict into a regular dict by using ``dict(multidict)``.
       Instead you have to use the :meth:`to_dict` method, otherwise
       the internal bucket objects are exposed.
    """

    def __init__(self, mapping: Optional[Any] = None) -> None:
        dict.__init__(self)
        self._first_bucket = self._last_bucket = None
        if mapping is not None:
            OrderedMultiDict.update(self, mapping, )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MultiDict):
            return NotImplemented
        if isinstance(other, OrderedMultiDict):
            iter1 = iter(self.items(multi=True))
            iter2 = iter(other.items(multi=True))
            try:
                for k1, v1 in iter1:
                    k2, v2 = next(iter2)
                    if k1 != k2 or v1 != v2:
                        return False
            except StopIteration:
                return False
            try:
                next(iter2)
            except StopIteration:
                return True
            return False
        if len(self) != len(other):
            return False
        for key, values in self.lists():
            if other.getlist(key) != values:
                return False
        return True

    __hash__ = None

    def __reduce_ex__(
        self, protocol: int
    ) -> Tuple[
        Type["OrderedMultiDict"],
        Tuple[
            List[
                Union[
                    Tuple[str, str],
                    Tuple[str, int],
                    Tuple[bytes, int],
                    Tuple[bytes, bytes],
                ]
            ]
        ],
    ]:
        return type(self), (list(self.items(multi=True)),)

    def __getstate__(self):
        return list(self.items(multi=True))

    def __setstate__(self, values):
        self.clear()
        for key, value in values:
            self.add(key, value)

    def __getitem__(self, key: _K) -> _T:
        if key in self:
            return dict.__getitem__(self, key)[0].value
        raise KeyError(key)

    def __setitem__(self, key: _K, value: _T) -> None:
        self.poplist(key)
        self.add(key, value)

    def __delitem__(self, key: _K) -> None:
        self.pop(key)

    def values(self) -> ValuesView[_T]:
        return _ValuesView(self)

    def gen_items(
        self, multi: bool = False
    ) -> Iterator[Tuple[_K, _T]]:

        ptr = self._first_bucket
        if multi:
            while ptr is not None:
                yield ptr.key, ptr.value
                ptr = ptr.next
        else:
            returned_keys: Set[_K] = set()
            while ptr is not None:
                if ptr.key not in returned_keys:
                    returned_keys.add(ptr.key)
                    yield ptr.key, ptr.value
                ptr = ptr.next

    def lists(self) -> Iterator[Tuple[_K, List[_T]]]:
        returned_keys: Set[_K] = set()
        ptr = self._first_bucket
        while ptr is not None:
            if ptr.key not in returned_keys:
                yield ptr.key, self.getlist(ptr.key)
                returned_keys.add(ptr.key)
            ptr = ptr.next

    def listvalues(self):
        for _key, values in self.lists():
            yield values

    def add(self, key: _K, value: _T) -> None:
        dict.setdefault(self, key, []).append(_OMDBucket(self, key, value))

    def getlist(self, key: _K, elem_type: Optional[Callable] = None) -> List[Any]:
        try:
            rv = dict.__getitem__(self, key)
        except KeyError:
            return []
        if elem_type is None:
            return [x.value for x in rv]
        result = []
        for item in rv:
            try:
                result.append(elem_type(item.value))
            except ValueError:
                pass
        return result

    def setlist(self, key: _K, new_list: List[_T]) -> None:
        self.poplist(key)
        for value in new_list:
            self.add(key, value)

    def setlistdefault(self, key, default_list=None):
        raise TypeError("setlistdefault is unsupported for ordered multi dicts")

    def poplist(self, key: _K) -> List[_T]:
        buckets = dict.pop(self, key, ())
        for bucket in buckets:
            bucket.unlink(self)
        return [x.value for x in buckets]

    def pop(
        self, key: _K, default: Optional[Union["_Missing", Any]] = _missing
    ) -> Union[_T, Any]:
        try:
            buckets = dict.pop(self, key)
        except KeyError:
            if default is not _missing:
                return default
            raise
        for bucket in buckets:
            bucket.unlink(self)
        return buckets[0].value

    def popitem(self) -> Tuple[_K, _T]:
        key, buckets = dict.popitem(self)
        for bucket in buckets:
            bucket.unlink(self)
        return key, buckets[0].value

    def popitemlist(self) -> Tuple[_K, List[_T]]:
        key, buckets = dict.popitem(self)
        for bucket in buckets:
            bucket.unlink(self)
        return key, [x.value for x in buckets]

    def clear(self) -> None:
        super().clear()
        self._first_bucket = self._last_bucket = None
