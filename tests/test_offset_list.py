import pytest

from nonstd.sequence import OneIndexedList, OffsetList


class TestOneIndexedList:
    """
    Tests all the ``list`` methods noted here [1], i.e.:

    - ``one_indexed_list.append(x)``
    - ``one_indexed_list.extend(iterable)``
    - ``one_indexed_list.insert(i, x)``
    - ``one_indexed_list.remove(x)``
    - ``one_indexed_list.pop([i])``
    - ``one_indexed_list.clear()``
    - ``one_indexed_list.index(x[, start[, end]])``
    - ``one_indexed_list.count(x)``
    - ``one_indexed_list.sort(*, key=None, reverse=False)``
    - ``one_indexed_list.reverse()``
    - ``one_indexed_list.copy()``

    Also tests:

    - accessing by an index (integer or slice) using subscript notation, i.e. ``one_indexed_list[start:stop:step]``
    - equality comparisons
    - ``len(one_indexed_list)``
    - checking membership, i.e. ``member in one_indexed_list``
    - iterating through the list
    - .items() and .keys()

    [1] https://docs.python.org/3.8/tutorial/datastructures.html
    """

    def test_append(self):
        oil = OneIndexedList()
        oil.append(1)
        assert oil == OneIndexedList([1])

    def test_extend(self):
        oil = OneIndexedList([1])
        oil.extend([2, 3])
        assert oil == OneIndexedList([1, 2, 3])

    def test_insert(self):
        oil = OneIndexedList(["world"])
        oil.insert(1, "hello")
        assert oil == OneIndexedList(["hello", "world"])

    def test_remove(self):
        oil = OneIndexedList([1, 2, 3])
        oil.remove(1)
        assert oil == OneIndexedList([2, 3])

        with pytest.raises(ValueError):
            oil.remove(1)

    def test_pop(self):
        oil = OneIndexedList([1])
        assert oil.pop() == 1
        with pytest.raises(IndexError):
            oil.pop()

        oil = OneIndexedList([1, 2])
        assert oil.pop(2) == 2

    def test_clear(self):
        oil = OneIndexedList([1])
        oil.clear()
        assert oil == OneIndexedList()
        assert len(oil) == 0

    def test_index(self):
        oil = OneIndexedList([1, 2, 3])
        assert oil.index(1) == 1
        assert oil.index(2) == 2
        assert oil.index(3) == 3

        oil = OneIndexedList(["waldo", 0, "waldo"])

        assert oil.index("waldo", start=2) == 3
        assert oil.index("waldo", start=1) == 1
        assert oil.index("waldo", stop=2) == 1

        with pytest.raises(ValueError):
            OneIndexedList([1, 2, 3]).index(3, stop=2)

        with pytest.raises(ValueError):
            oil.index(99)

    def test_count(self):
        oil = OneIndexedList([1, 2, 3])
        assert oil.count(3) == 1

    def test_sort(self):
        oil = OneIndexedList([2, 1, 3])
        oil.sort()
        assert oil == OneIndexedList([1, 2, 3])

        oil.sort(reverse=True)
        assert oil == OneIndexedList([3, 2, 1])

        oil.sort(key=lambda x: -x)
        assert oil == OneIndexedList([3, 2, 1])

    def test_reverse(self):
        oil = OneIndexedList([1, 2, 3])
        oil.reverse()
        assert oil == OneIndexedList([3, 2, 1])

    def test_copy(self):
        oil = OneIndexedList([1])
        oil2 = oil.copy()
        del oil
        assert oil2[1] == 1

    def test_access_integer(self):
        oil = OneIndexedList([1, 2])
        with pytest.raises(IndexError):
            oil[0]
        with pytest.raises(IndexError):
            oil[-3]

        assert oil[1] == 1
        assert oil[2] == 2

        assert oil[-1] == 2
        assert oil[-2] == 1

    def test_access_slice(self):
        oil = OneIndexedList([1, 2, 3])
        assert oil[1:2] == OneIndexedList([1])
        assert oil[:2] == OneIndexedList([1])

        assert oil[2:4] == OneIndexedList([2, 3])
        assert oil[2:] == OneIndexedList([2, 3])

        assert oil[1:3] == OneIndexedList([1, 2])

        assert oil[:4] == OneIndexedList([1, 2, 3])
        assert oil[:1] == OneIndexedList([])

        assert oil[:4:2] == OneIndexedList([1, 3])
        assert oil[1:4:2] == OneIndexedList([1, 3])

        assert oil[-2:] == OneIndexedList([2, 3])
        assert oil[:-2] == OneIndexedList([1])

        assert oil[::-1] == OneIndexedList([3, 2, 1])
        assert oil[2::-1] == OneIndexedList([2, 1])

    def test_equality(self):
        assert OneIndexedList() == OneIndexedList()
        assert OneIndexedList([1, 2]) == OneIndexedList([1, 2])
        assert not OneIndexedList([]) == OneIndexedList([1])
        assert not OneIndexedList([1, 2]) == None
        with pytest.raises(
            NotImplementedError,
            match="Cannot compare two `OffsetList`s with different offsets",
        ):
            OneIndexedList([1]) == OffsetList([1], start_i=2)
        with pytest.raises(NotImplementedError, match="Cannot compare a `OffsetList` to a list"):
            OneIndexedList([1]) == [1]

    def test_len(self):
        oil = OneIndexedList()
        assert len(oil) == 0

        oil = OneIndexedList([1])
        assert len(oil) == 1

    def test_contains(self):
        oil = OneIndexedList([1, 2, 3])
        assert 1 in oil
        assert 4 not in oil

    def test_iter(self):
        oil = OneIndexedList([1, 2, 3])
        assert [i for i in oil] == [1, 2, 3]
        for _ in oil:
            pass

    def test_items(self):
        oil = OneIndexedList((1, 5))
        assert oil.items() == [(1, 1), (2, 5)]

    def test_keys(self):
        oil = OneIndexedList((1, 5))
        assert oil.keys() == oil.indices() == [1, 2]

    def test_idempotency(self):
        assert OneIndexedList([1, 2, 3]) == OneIndexedList(OneIndexedList([1, 2, 3]))


class TestOffsetList:
    def test_access_integer(self):
        subject = OffsetList([1, 2, 3], start_i=42)

        with pytest.raises(IndexError, match="Index 41 is forbidden"):
            subject[41]
        with pytest.raises(IndexError, match="index out of range"):
            subject[-4]

        assert subject[42] == 1
        assert subject[43] == 2

        assert subject[-1] == 3
        assert subject[-2] == 2

    def test_access_slice(self):
        subject = OffsetList([1, 2, 3], start_i=10)

        assert subject[10:12] == OffsetList([1, 2], start_i=10)
        assert subject[:15] == OffsetList([1, 2, 3], start_i=10)
