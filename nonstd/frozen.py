from boltons.dictutils import FrozenDict
import numpy as np


def freeze(obj):
    # Recursively freeze an object
    if isinstance(obj, dict):
        return FrozenDict({key: freeze(value) for key, value in obj.items()})
    elif isinstance(obj, set):
        return frozenset(freeze(value) for value in obj)
    elif isinstance(obj, (list, tuple)):
        return tuple(freeze(value) for value in obj)
    elif isinstance(obj, np.ndarray):
        return freeze(obj.tolist())
    else:
        return obj