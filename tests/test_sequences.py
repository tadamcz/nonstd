from collections import OrderedDict

import pytest

from nonstd.list import OneIndexedList
from nonstd.sequences import is_arithmetic_sequence, is_geometric_sequence, FlexibleSequence, FlexibleSequenceType


def test_is_geometric_sequence():
	assert is_geometric_sequence([1])
	assert is_geometric_sequence([1, 1, 1])
	assert is_geometric_sequence([1, 2, 4])
	assert is_geometric_sequence([-1, 1, -1])

	assert not is_geometric_sequence([0])
	assert not is_geometric_sequence([0, 1, 1])
	assert not is_geometric_sequence([1, 2, 3])

	with pytest.raises(IndexError):
		is_geometric_sequence([])


def test_is_arithmetic_sequence():
	assert is_arithmetic_sequence([0])
	assert is_arithmetic_sequence([0, 0, 0])
	assert is_arithmetic_sequence([0, 1, 2])
	assert is_arithmetic_sequence([3, 2, 1])

	assert not is_arithmetic_sequence([1, 2, 4])

	with pytest.raises(IndexError):
		is_arithmetic_sequence([])


@pytest.fixture(params=[FlexibleSequenceType.DIRECT, FlexibleSequenceType.CALLABLE])
def one_two_three(request):
	if request.param == FlexibleSequenceType.DIRECT:
		return FlexibleSequence((1, 2, 3))
	if request.param == FlexibleSequenceType.CALLABLE:
		return FlexibleSequence(lambda index: index + 1)


class TestFlexibleSequence:
	def test_init(self):
		s = FlexibleSequence(1)
		assert s.type == FlexibleSequenceType.CONSTANT

		s = FlexibleSequence(dict(hello="world"))
		assert s.type == FlexibleSequenceType.CONSTANT

		# Unclear if this is the ideal behaviour, but it's a defensible choice, and I'll go with it
		s = FlexibleSequence(OrderedDict(hello="world"))
		assert s.type == FlexibleSequenceType.CONSTANT

		f = lambda x: x ** 2
		s = FlexibleSequence(f)
		assert s.type == FlexibleSequenceType.CALLABLE

		s = FlexibleSequence((1, 2, 3))
		assert s.type == FlexibleSequenceType.DIRECT

		s = FlexibleSequence([1, 2, 3])
		assert s.type == FlexibleSequenceType.DIRECT

		s = FlexibleSequence(OneIndexedList([1, 2, 3]))
		assert s.type == FlexibleSequenceType.DIRECT

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

		if s.type != FlexibleSequenceType.CALLABLE:
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