import pytest

from nonstd.sequence_math import is_geometric_sequence, is_arithmetic_sequence, is_increasing, is_non_decreasing, \
	is_decreasing, is_non_increasing


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


def test_is_increasing_sequence():
	assert is_increasing([0])
	assert is_increasing([0, 1, 2])
	assert is_increasing([1, 2, 4])
	assert not is_increasing([3, 2, 1])
	with pytest.raises(IndexError):
		is_increasing([])


def test_is_non_decreasing_sequence():
	assert is_non_decreasing([0])
	assert is_non_decreasing([0, 1, 2])
	assert is_non_decreasing([0, 0, 0])
	assert not is_non_decreasing([3, 2, 1])
	with pytest.raises(IndexError):
		is_non_decreasing([])


def test_is_decreasing_sequence():
	assert is_decreasing([3, 2, 1])
	assert not is_decreasing([0, 1, 2])
	assert not is_decreasing([0, 0, 0])
	with pytest.raises(IndexError):
		is_decreasing([])

def test_is_non_increasing_sequence():
	assert is_non_increasing([3, 2, 1])
	assert is_non_increasing([3, 3, 3])
	assert not is_non_increasing([1, 2, 3])
	with pytest.raises(IndexError):
		is_non_increasing([])
