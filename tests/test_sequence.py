from collections import OrderedDict

import pytest

from nonstd.sequence import OneIndexedList, FlexibleSequenceDefinition, FlexibleSequence


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

		with pytest.raises(NotImplementedError):
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
		assert oil.keys() == [1, 2]


@pytest.fixture(params=[FlexibleSequenceDefinition.DIRECT, FlexibleSequenceDefinition.CALLABLE])
def one_two_three(request):
	if request.param == FlexibleSequenceDefinition.DIRECT:
		return FlexibleSequence((1, 2, 3))
	if request.param == FlexibleSequenceDefinition.CALLABLE:
		return FlexibleSequence(lambda index: index + 1)


class TestFlexibleSequence:
	def test_init(self):
		s = FlexibleSequence(1)
		assert s.definition == FlexibleSequenceDefinition.CONSTANT

		s = FlexibleSequence(dict(hello="world"))
		assert s.definition == FlexibleSequenceDefinition.CONSTANT

		# Unclear if this is the ideal behaviour, but it's a defensible choice, and I'll go with it
		s = FlexibleSequence(OrderedDict(hello="world"))
		assert s.definition == FlexibleSequenceDefinition.CONSTANT

		f = lambda x: x ** 2
		s = FlexibleSequence(f)
		assert s.definition == FlexibleSequenceDefinition.CALLABLE

		s = FlexibleSequence((1, 2, 3))
		assert s.definition == FlexibleSequenceDefinition.DIRECT

		s = FlexibleSequence([1, 2, 3])
		assert s.definition == FlexibleSequenceDefinition.DIRECT

		s = FlexibleSequence(OneIndexedList([1, 2, 3]))
		assert s.definition == FlexibleSequenceDefinition.DIRECT

	def test_length(self):
		s = FlexibleSequence(1, length=3)
		assert len(s) == 3

		s = FlexibleSequence(1)
		with pytest.raises(IndexError, match="Infinite"):
			len(s)

		s = FlexibleSequence((1, 2))
		assert len(s) == 2

	def test_callable_start(self):
		f = lambda x: x ** 2
		s = FlexibleSequence(f, callabe_start_i=1, length=4)
		assert s == [1, 4, 9, 16]

		# The parameter is ignored
		assert FlexibleSequence((1, 2), callabe_start_i=42) == FlexibleSequence((1, 2))
		assert FlexibleSequence(1, callabe_start_i=42, length=100) == FlexibleSequence(1, length=100)

	def test_iteration(self):
		s = FlexibleSequence((1, 2, 3))
		assert [i for i in s] == [1, 2, 3]

		s = FlexibleSequence(1, length=3)
		assert [i for i in s] == [1, 1, 1]

		s = FlexibleSequence(1)
		assert [s[i] for i in range(1000)] == [1] * 1000

	def test_access_integer(self):
		s = FlexibleSequence((1, 2, 3))
		assert s[0] == 1
		assert s[-1] == 3

		s = FlexibleSequence(5)
		assert s[0] == 5
		assert s[-1] == 5

		f = lambda x: x ** 2
		s = FlexibleSequence(f)
		assert s[4] == 16
		with pytest.raises(NotImplementedError):
			s[-1]

	def test_access_slice(self, one_two_three):
		"""
		``one_two_three`` is equal to [1,2,3] and parametrized as (1) coming from a sequence, or (2) coming from a
		callable
		"""
		s = one_two_three

		assert s[0:2] == [1, 2]
		assert s[1:3] == [2, 3]

		assert s[:0] == []
		assert s[:1] == [1]
		assert s[:3] == [1, 2, 3]

		if s.definition != FlexibleSequenceDefinition.CALLABLE:
			assert s[0:] == [1, 2, 3]
			assert s[1:] == [2, 3]
			assert s[3:] == []

		assert s[:3:2] == [1, 3]
		assert s[0:3:2] == [1, 3]

		assert s[:3:2] == [1, 3]
		assert s[0:3:2] == [1, 3]

	def test_access_slice_raises(self):
		s_callable = FlexibleSequence(lambda x: x + 1)
		s_callable_length = FlexibleSequence(lambda x: x + 1, length=3)

		# All these should raise an exception, iff no length is provided
		slices = [
			slice(None, None, -1),  # corresponds to seq[::1]
			slice(0, None, None),   # corresponds to seq[0:]
			slice(None, None, -1),  # corresponds to seq[::-1]
		]

		for sl in slices:
			s_callable_length[sl]  # does not raise
			with pytest.raises(IndexError, match="You must provide a slice stop"):
				s_callable[sl]

		assert s_callable_length[::-1] == [3, 2, 1]
		assert s_callable_length[0:] == [1, 2, 3]

	def test_equality(self):
		assert FlexibleSequence(lambda x: x ** 2, length=5) == \
			   FlexibleSequence([0, 1, 4, 9, 16]) == \
			   [0, 1, 4, 9, 16]
