import pytest

from nonstd.sequences import is_arithmetic_sequence, is_geometric_sequence


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
