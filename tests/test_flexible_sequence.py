from collections import OrderedDict

import pytest

from nonstd.sequence import OneIndexedList, FlexibleSequenceDefinition, FlexibleSequence


@pytest.fixture(params=[FlexibleSequenceDefinition.DIRECT, FlexibleSequenceDefinition.CALLABLE])
def one_two_three(request):
	if request.param == FlexibleSequenceDefinition.DIRECT:
		return FlexibleSequence((1, 2, 3))
	if request.param == FlexibleSequenceDefinition.CALLABLE:
		return FlexibleSequence(lambda index: index + 1, length=3)


@pytest.fixture()
def one_with_length():
	return FlexibleSequence(1, length=5)


@pytest.fixture(params=list(range(-4, 4)) + [None], ids=lambda x: f"start=___{x}___")
def start(request):
	return request.param


@pytest.fixture(params=list(range(-4, 4)) + [None], ids=lambda x: f"stop=___{x}___")
def stop(request):
	return request.param


@pytest.fixture(params=list(range(-4, 0)) + list(range(1, 4)) + [None], ids=lambda x: f"step=___{x}___")
def step(request):
	return request.param


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
		s = FlexibleSequence(f, callable_start_i=1, length=4)
		assert s == [1, 4, 9, 16]

		# The parameter is ignored
		assert FlexibleSequence((1, 2), callable_start_i=42) == FlexibleSequence((1, 2))
		assert FlexibleSequence(1, callable_start_i=42, length=100) == FlexibleSequence(1, length=100)

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
			s[-2]
		with pytest.raises(NotImplementedError):
			s[-2:-1]

	def test_access_slice_finite(self, one_two_three, one_with_length, start, stop, step):
		try:
			assert one_two_three[start:stop:step] == [1, 2, 3][start:stop:step]

			# Does not raise IndexError
			one_with_length[start:stop:step]
		except NotImplementedError:
			pass

	def test_access_slice_infinite(self, start, stop, step):
		one = FlexibleSequence(1)

		size_dependent_slice = len(list(range(100))[start:stop:step]) < len(list(range(1000))[start:stop:step])

		if size_dependent_slice:
			with pytest.raises(IndexError):
				one[start:stop:step]
		else:
			length = len(list(range(100))[start:stop:step])
			assert one[start:stop:step] == [1] * length

	def test_equality(self):
		assert FlexibleSequence(lambda x: x ** 2, length=5) == \
			   FlexibleSequence([0, 1, 4, 9, 16]) == \
			   [0, 1, 4, 9, 16]

		assert FlexibleSequence((1, 2, 3)) != None
