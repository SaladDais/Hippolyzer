"""
Copyright 2007 Pallets
Copyright 2021 Salad Dais

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
"""

import pickle
from copy import copy
from copy import deepcopy

import pytest

from hippolyzer.lib.base.multidict import MultiDict, OrderedMultiDict


class TestNativeItermethods:
    def test_basic(self):
        class StupidDict:
            def keys(self, multi=1):
                return iter(["a", "b", "c"] * multi)

            def values(self, multi=1):
                return iter([1, 2, 3] * multi)

            def items(self, multi=1):
                return iter(
                    zip(iter(self.keys(multi=multi)), iter(self.values(multi=multi)))
                )

        d = StupidDict()
        expected_keys = ["a", "b", "c"]
        expected_values = [1, 2, 3]
        expected_items = list(zip(expected_keys, expected_values))

        assert list(d.keys()) == expected_keys
        assert list(d.values()) == expected_values
        assert list(d.items()) == expected_items

        assert list(d.keys(2)) == expected_keys * 2
        assert list(d.values(2)) == expected_values * 2
        assert list(d.items(2)) == expected_items * 2


class _MutableMultiDictTests:
    storage_class = None

    def test_pickle(self):
        cls = self.storage_class

        def create_instance(module=None):
            if module is None:
                d_inst = cls()
            else:
                old = cls.__module__
                cls.__module__ = module
                d_inst = cls()
                cls.__module__ = old
            d_inst.setlist(b"foo", [1, 2, 3, 4])
            d_inst.setlist(b"bar", b"foo bar baz".split())
            return d_inst

        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            d = create_instance()
            s = pickle.dumps(d, protocol)
            ud = pickle.loads(s)
            assert type(ud) is type(d)
            assert ud == d
            alternative = pickle.dumps(create_instance("werkzeug"), protocol)
            assert pickle.loads(alternative) == d
            ud[b"newkey"] = b"bla"
            assert ud != d

    def test_basic_interface(self):
        md = self.storage_class()
        assert isinstance(md, dict)

        mapping = [
            ("a", 1),
            ("b", 2),
            ("a", 2),
            ("d", 3),
            ("a", 1),
            ("a", 3),
            ("d", 4),
            ("c", 3),
        ]
        md = self.storage_class(mapping)

        # simple getitem gives the first value
        assert md["a"] == 1
        assert md["c"] == 3
        with pytest.raises(KeyError):
            md["e"]  # noqa
        assert md.get("a") == 1

        # list getitem
        assert md.getlist("a") == [1, 2, 1, 3]
        assert md.getlist("d") == [3, 4]
        # do not raise if key not found
        assert md.getlist("x") == []

        # simple setitem overwrites all values
        md["a"] = 42
        assert md.getlist("a") == [42]

        # list setitem
        md.setlist("a", [1, 2, 3])
        assert md["a"] == 1
        assert md.getlist("a") == [1, 2, 3]

        # verify that it does not change original lists
        l1 = [1, 2, 3]
        md.setlist("a", l1)
        del l1[:]
        assert md["a"] == 1

        # setdefault, setlistdefault
        assert md.setdefault("u", 23) == 23
        assert md.getlist("u") == [23]
        del md["u"]

        md.setlist("u", [-1, -2])

        # delitem
        del md["u"]
        with pytest.raises(KeyError):
            md["u"]  # noqa
        del md["d"]
        assert md.getlist("d") == []

        # keys, values, items, lists
        assert list(sorted(md.keys())) == ["a", "b", "c"]
        assert list(sorted(md.keys())) == ["a", "b", "c"]

        # Changed from werkzeug. IMO this is less wrong than only
        # returning the first item for each.
        assert list(sorted(md.values())) == [1, 2, 2, 3, 3]
        assert list(sorted(md.values())) == [1, 2, 2, 3, 3]

        assert list(sorted(md.items(multi=False))) == [("a", 1), ("b", 2), ("c", 3)]
        assert list(sorted(md.items())) == [
            ("a", 1),
            ("a", 2),
            ("a", 3),
            ("b", 2),
            ("c", 3),
        ]
        assert list(sorted(md.items(multi=False))) == [("a", 1), ("b", 2), ("c", 3)]
        assert list(sorted(md.items())) == [
            ("a", 1),
            ("a", 2),
            ("a", 3),
            ("b", 2),
            ("c", 3),
        ]

        assert list(sorted(md.lists())) == [("a", [1, 2, 3]), ("b", [2]), ("c", [3])]
        assert list(sorted(md.lists())) == [("a", [1, 2, 3]), ("b", [2]), ("c", [3])]

        # copy method
        c = md.copy()
        assert c["a"] == 1
        assert c.getlist("a") == [1, 2, 3]

        # copy method 2
        c = copy(md)
        assert c["a"] == 1
        assert c.getlist("a") == [1, 2, 3]

        # deepcopy method
        c = md.deepcopy()
        assert c["a"] == 1
        assert c.getlist("a") == [1, 2, 3]

        # deepcopy method 2
        c = deepcopy(md)
        assert c["a"] == 1
        assert c.getlist("a") == [1, 2, 3]

        # update with a multidict
        od = self.storage_class([("a", 4), ("a", 5), ("y", 0)])
        md.update(od)
        assert md.getlist("a") == [1, 2, 3, 4, 5]
        assert md.getlist("y") == [0]

        # update with a regular dict
        md = c
        od = {"a": 4, "y": 0}
        md.update(od)
        assert md.getlist("a") == [1, 2, 3, 4]
        assert md.getlist("y") == [0]

        # pop, poplist, popitem, popitemlist
        assert md.pop("y") == 0
        assert "y" not in md
        assert md.poplist("a") == [1, 2, 3, 4]
        assert "a" not in md
        assert md.poplist("missing") == []

        # remaining: b=2, c=3
        popped = md.popitem()
        assert popped in [("b", 2), ("c", 3)]
        popped = md.popitemlist()
        assert popped in [("b", [2]), ("c", [3])]

        # repr
        md = self.storage_class([("a", 1), ("a", 2), ("b", 3)])
        assert "('a', 1)" in repr(md)
        assert "('a', 2)" in repr(md)
        assert "('b', 3)" in repr(md)

        # add and getlist
        md.add("c", "42")
        md.add("c", "23")
        assert md.getlist("c") == ["42", "23"]
        md.add("c", "blah")
        assert md.getlist("c", elem_type=int) == [42, 23]

        # setdefault
        md = self.storage_class()
        md.setdefault("x", []).append(42)
        md.setdefault("x", []).append(23)
        assert md["x"] == [42, 23]

        # to dict
        md = self.storage_class()
        md["foo"] = 42
        md.add("bar", 1)
        md.add("bar", 2)
        assert md.to_dict() == {"foo": 42, "bar": 1}
        assert md.to_dict(flat=False) == {"foo": [42], "bar": [1, 2]}

        # popitem from empty dict
        with pytest.raises(KeyError):
            self.storage_class().popitem()

        with pytest.raises(KeyError):
            self.storage_class().popitemlist()

        # key errors are of a special type
        with pytest.raises(KeyError):
            self.storage_class()[42]  # noqa

        # setlist works
        md = self.storage_class()
        md["foo"] = 42
        md.setlist("foo", [1, 2])
        assert md.getlist("foo") == [1, 2]


class TestMultiDict(_MutableMultiDictTests):
    storage_class = MultiDict  # type: ignore

    def test_multidict_pop(self):
        def make_d():
            return self.storage_class({"foo": [1, 2, 3, 4]})

        d = make_d()
        assert d.pop("foo") == 1
        assert not d
        d = make_d()
        assert d.pop("foo", 32) == 1
        assert not d
        d = make_d()
        assert d.pop("foos", 32) == 32
        assert d

        with pytest.raises(KeyError):
            d.pop("foos")

    def test_multidict_pop_raise_keyerror_for_empty_list_value(self):
        mapping = [("a", "b"), ("a", "c")]
        md = self.storage_class(mapping)

        md.setlistdefault("empty", [])

        with pytest.raises(KeyError):
            md.pop("empty")

    def test_multidict_popitem_raise_keyerror_for_empty_list_value(self):
        mapping = []
        md = self.storage_class(mapping)

        md.setlistdefault("empty", [])

        with pytest.raises(KeyError):
            md.popitem()

    def test_setlistdefault(self):
        md = self.storage_class()
        assert md.setlistdefault("u", [-1, -2]) == [-1, -2]
        assert md.getlist("u") == [-1, -2]
        assert md["u"] == -1

    def test_iter_interfaces(self):
        mapping = [
            ("a", 1),
            ("b", 2),
            ("a", 2),
            ("d", 3),
            ("a", 1),
            ("a", 3),
            ("d", 4),
            ("c", 3),
        ]
        md = self.storage_class(mapping)
        assert list(zip(md.keys(), md.listvalues())) == list(md.lists())
        assert list(zip(md, md.listvalues())) == list(md.lists())
        assert list(zip(md.keys(), md.listvalues())) == list(md.lists())

    def test_getitem_raise_keyerror_for_empty_list_value(self):
        mapping = [("a", "b"), ("a", "c")]
        md = self.storage_class(mapping)

        md.setlistdefault("empty", [])

        with pytest.raises(KeyError):
            md["empty"]  # noqa


class TestOrderedMultiDict(_MutableMultiDictTests):
    storage_class = OrderedMultiDict  # type: ignore

    def test_ordered_interface(self):
        cls = self.storage_class

        d = cls()
        assert not d
        d.add("foo", "bar")
        assert len(d) == 1
        d.add("foo", "baz")
        assert len(d) == 2
        assert list(d.items(multi=False)) == [("foo", "bar")]
        assert list(d) == ["foo"]
        assert list(d.items()) == [("foo", "bar"), ("foo", "baz")]
        del d["foo"]
        assert not d
        assert len(d) == 0
        assert list(d) == []

        d.update([("foo", 1), ("foo", 2), ("bar", 42)])
        d.add("foo", 3)
        assert d.getlist("foo") == [1, 2, 3]
        assert d.getlist("bar") == [42]
        assert list(d.items(multi=False)) == [("foo", 1), ("bar", 42)]

        expected = ["foo", "bar"]

        assert list(d.keys()) == expected
        assert list(d) == expected
        assert list(d.keys()) == expected

        assert list(d.items()) == [
            ("foo", 1),
            ("foo", 2),
            ("bar", 42),
            ("foo", 3),
        ]
        assert len(d) == 4

        assert d.pop("foo") == 1
        assert d.pop("blafasel", None) is None
        assert d.pop("blafasel", 42) == 42
        assert len(d) == 1
        assert d.poplist("bar") == [42]
        assert not d

        assert d.get("missingkey") is None

        d.add("foo", 42)
        d.add("foo", 23)
        d.add("bar", 2)
        d.add("foo", 42)
        assert d == MultiDict(d)
        storage_id = self.storage_class(d)
        assert d == storage_id
        d.add("foo", 2)
        assert d != storage_id

        d.update({"blah": [1, 2, 3]})
        assert d["blah"] == 1
        assert d.getlist("blah") == [1, 2, 3]

        # setlist works
        d = self.storage_class()
        d["foo"] = 42
        d.setlist("foo", [1, 2])
        assert d.getlist("foo") == [1, 2]
        with pytest.raises(KeyError):
            d.pop("missing")

        with pytest.raises(KeyError):
            d["missing"]  # noqa

        # popping
        d = self.storage_class()
        d.add("foo", 23)
        d.add("foo", 42)
        d.add("foo", 1)
        assert d.popitem() == ("foo", 23)
        with pytest.raises(KeyError):
            d.popitem()
        assert not d

        d.add("foo", 23)
        d.add("foo", 42)
        d.add("foo", 1)
        assert d.popitemlist() == ("foo", [23, 42, 1])

        with pytest.raises(KeyError):
            d.popitemlist()

        # Unhashable
        d = self.storage_class()
        d.add("foo", 23)
        pytest.raises(TypeError, hash, d)

    def test_clear_clears_values(self):
        foo = self.storage_class()
        foo.add("bar", 1)
        foo.add("bar", 2)
        foo.add("foo", 3)
        foo.clear()
        assert list(foo.keys()) == []
        assert list(foo.values()) == []
        foo.add("bar", 1)
        assert dict(foo.items()) == {"bar": 1}
