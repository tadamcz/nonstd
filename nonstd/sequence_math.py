from typing import Sequence

import numpy as np


def is_geometric_sequence(sequence: Sequence) -> bool:
    sequence = np.asarray(sequence)
    if np.any(sequence == 0):
        return False
    if len(sequence) == 0:
        raise IndexError("Sequence of length 0")
    if len(sequence) == 1:
        return True

    common_ratio = sequence[1] / sequence[0]
    for i in range(1, len(sequence)):
        ratio = sequence[i] / sequence[i - 1]
        if not np.isclose(ratio, common_ratio):
            return False
    return True


def is_arithmetic_sequence(sequence: Sequence) -> bool:
    sequence = np.asarray(sequence)
    if len(sequence) == 0:
        raise IndexError("Sequence of length 0")
    if len(sequence) == 1:
        return True
    diff = np.diff(sequence)
    common_difference = diff[0]
    return np.all(np.isclose(diff, common_difference))


def is_increasing(sequence: Sequence) -> bool:
    sequence = np.asarray(sequence)
    if len(sequence) == 0:
        raise IndexError("Sequence of length 0")
    return np.all(np.diff(sequence) > 0)


def is_non_decreasing(sequence: Sequence) -> bool:
    sequence = np.asarray(sequence)
    if len(sequence) == 0:
        raise IndexError("Sequence of length 0")
    return np.all(np.diff(sequence) >= 0)


def is_decreasing(sequence: Sequence) -> bool:
    sequence = np.asarray(sequence)
    if len(sequence) == 0:
        raise IndexError("Sequence of length 0")
    return np.all(np.diff(sequence) < 0)


def is_non_increasing(sequence: Sequence) -> bool:
    sequence = np.asarray(sequence)
    if len(sequence) == 0:
        raise IndexError("Sequence of length 0")
    return np.all(np.diff(sequence) <= 0)
