from numbers import Number
from typing import Union, Mapping, Callable

import numpy as np


# Apply a binary operation to two nested dictionaries recursively
def apply_binary_op(a: Union[dict, Number], b: Union[dict, Number], fun: callable):
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return apply_binary_op(np.asarray(a), np.asarray(b), fun)
    if isinstance(a, (Number, np.ndarray, list)) and isinstance(b, (Number, np.ndarray, list)):
        return fun(a, b)
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            raise ValueError('a and b must have the same keys')
        keys = a.keys()
        return {key: apply_binary_op(a[key], b[key], fun) for key in keys}
    raise ValueError(f'a and b must be of the same type, but are {a,type(a)} and {b,type(b)}')


def flatten_dict(d:dict):
    leaves = []
    for key, value in d.items():
        if isinstance(value, dict):
            leaves += flatten_dict(value)
        else:
            leaves.append(value)
    return leaves


def to_keys(obj):
    if isinstance(obj, Mapping):
        return {key: to_keys(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return tuple(to_keys(value) for value in obj)
    else:
        if isinstance(obj, Callable):
            return obj.__name__
        else:
            return obj