import collections.abc
import contextlib
import enum
import math
from itertools import count
from math import inf
from types import FunctionType
from typing import Optional, Union, Sequence, Callable


class OffsetList(collections.UserList):
    """
    Behaves like a regular Python ``list``, but with the index starting at 1 instead of 0.

    Also provides the ``dict``-like methods ``.keys()`` and ``.items()``
    """

    def __init__(self, initlist=None, start_i=1):
        self.start_i = start_i
        super().__init__(initlist)

    def _wrapped_index(self, index: [int, slice]) -> [int, slice]:
        if isinstance(index, slice):
            return self._wrapped_slice_index(index)
        if isinstance(index, int):
            return self._wrapped_integer_index(index)

    def _wrapped_slice_index(self, index: slice) -> slice:
        start = self._wrapped_integer_index(index.start)
        stop = self._wrapped_integer_index(index.stop)
        return slice(start, stop, index.step)

    def _wrapped_integer_index(self, index: [int, None]) -> [int, None]:
        if index is None:
            return None
        if (
            index < 0
        ):  # In Python, negative indices are used to count backwards from the last element of a list
            return index
        elif index < self.start_i:
            raise IndexError(
                f"This {self.__class__.__name__} is an `OffsetList` with start index {self.start_i}. Index {index} is forbidden."
            )
        else:
            return index - self.start_i

    def __getitem__(self, index: [int, slice]) -> any:
        wrapped_i = self._wrapped_index(index)
        if isinstance(index, slice):
            return OffsetList(start_i=self.start_i, initlist=self.data[wrapped_i])
        else:
            return super().__getitem__(wrapped_i)

    def __setitem__(self, index: [int, slice], value: any) -> None:
        wrapped_i = self._wrapped_index(index)
        super().__setitem__(wrapped_i, value)

    def __delitem__(self, index: [int, slice]) -> None:
        wrapped_i = self._wrapped_index(index)
        super().__delitem__(wrapped_i)

    def insert(self, index: [int, slice], value: any) -> None:
        wrapped_i = self._wrapped_index(index)
        super().insert(wrapped_i, value)

    def pop(self, index: Optional[int] = None) -> any:
        if index is None:
            return self.data.pop()
        wrapped_i = self._wrapped_index(index)
        return super().pop(wrapped_i)

    def index(self, value: any, start: int = None, stop: int = None) -> int:
        if start is None:
            start = self.start_i
        if stop is None:
            stop = len(self) + self.start_i

        wrapped_start = self._wrapped_index(start)
        wrapped_stop = self._wrapped_index(stop)
        wrapped_result = super().index(value, wrapped_start, wrapped_stop)

        return wrapped_result + self.start_i

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        if not isinstance(other, OffsetList):
            raise NotImplementedError(
                f"Cannot compare a `OffsetList` to a {other.__class__.__name__}"
            )
        else:
            if self.start_i != other.start_i:
                raise NotImplementedError(
                    f"Cannot compare two `OffsetList`s with different offsets {self.start_i} and {other.start_i}"
                )
        return self.data == other.data

    def __iter__(self):
        yield from self.data.__iter__()

    def keys(self):
        return list(range(self.start_i, len(self.data) + self.start_i))

    def indices(self):
        """Alias"""
        return self.keys()

    def items(self):
        """
        Behaves similarly to calling ``enumerate()`` on a regular ``list``.
        """
        return [(key, self[key]) for key in self.keys()]


class OneIndexedList(OffsetList):
    def __init__(self, initlist=None):
        super().__init__(initlist, start_i=1)


class FlexibleSequenceDefinition(enum.Enum):
    DIRECT = enum.auto()
    CONSTANT = enum.auto()
    CALLABLE = enum.auto()


class FlexibleSequence(collections.abc.Sequence):
    def __init__(
        self,
        spec: Union[Sequence, object, Callable],
        length: Optional[int] = None,
        callable_start_i: Optional[int] = 0,
    ):
        """
        Specify a sequence in one of three ways:

        -
                directly provide a sequence, in which case the ``FlexibleSequence`` will simply wrap that sequence without any
                changes.

        -
                provide a single object; the ``FlexibleSequence`` will behave like a sequence with that object at every index.

        -
                provide a callable (e.g. a function); the ``FlexibleSequence`` will behave such that
                ``flexible_seq[i] == callable(callable_start_i+i)`` for positive indices ``i``.

        Negative indices will behave as you'd expect, or raise an exception in impossible cases.

        Note: The type annotation ``Union[object, Sequence, Callable]`` doesn't do anything in a type checker, because
        everything is an ``object``. It only suggests the intent.

        :param spec:
                The input. A sequence (that will be used directly), a callable (that will be called with an index as argument),
                or an object that will be returned for any index.

        :param length:
                If you supply a single object or a callable, without specifying a length, by default the `FlexibleSequence`
                will behave like an infinite sequence (so that e.g. the line `[i for i in flex_seq]` will lead to
                an infinite loop). If you specify a length, it will behave as if it were a sequence of that length (even
                though the callable may support arguments greater than that length).

        :param callable_start_i: The callable argument that corresponds to the 0 index of the ``FlexibleSequence``.``flexible_seq[0]==callable(callable_start_i)``
        """
        if isinstance(spec, Sequence) and length and len(spec) != length:
            raise ValueError(f"Mismatched lengths: len(spec)={len(spec)}, length={length}")

        self.c_start_i = callable_start_i
        self.wrapped = spec

        if isinstance(self.wrapped, Sequence):
            self.definition = FlexibleSequenceDefinition.DIRECT
            length = len(self.wrapped)
        elif isinstance(self.wrapped, Callable):
            self.definition = FlexibleSequenceDefinition.CALLABLE
        else:  # any other object
            self.definition = FlexibleSequenceDefinition.CONSTANT

        if length is None:
            if self.definition == FlexibleSequenceDefinition.DIRECT:
                self.length = len(self.wrapped)
            else:
                self.length = inf
        else:
            self.length = length

    def __iter__(self):
        if self.definition == FlexibleSequenceDefinition.DIRECT:
            yield from self.wrapped.__iter__()
        else:
            if math.isfinite(self.length):
                yield from (self[i] for i in range(self.length))
            else:
                yield from (self[i] for i in count())

    def __len__(self):
        if self.definition == FlexibleSequenceDefinition.DIRECT:
            return len(self.wrapped)
        else:
            if math.isfinite(self.length):
                return self.length
            else:
                # We cannot return `math.inf`, as the `len` function (that calls `__len__`) needs an integer.
                raise IndexError("Infinite sequence")

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._get_slice(index)
        if isinstance(index, int):
            return self._get_int(index)

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return [i for i in self] == [i for i in other]

    def __repr__(self):
        if math.isfinite(self.length):
            return [i for i in self].__repr__()
        else:
            if isinstance(self.wrapped, FunctionType):
                return f"FlexibleSequence({self.wrapped.__class__.__name__})"
            return f"FlexibleSequence({self.wrapped})"

    def _get_int(self, index: int):
        if self.definition == FlexibleSequenceDefinition.CONSTANT:
            return self.wrapped
        elif self.definition == FlexibleSequenceDefinition.DIRECT:
            return self.wrapped[index]
        elif self.definition == FlexibleSequenceDefinition.CALLABLE:
            if index < 0:
                if math.isinf(self.length):
                    self._raise_negative_forbidden(index)
                else:
                    index = self.length + index
            return self.wrapped(self.c_start_i + index)

    def _get_slice(self, _slice: slice):
        if isinstance(self.wrapped, Callable) and math.isinf(self.length):
            with CatchNoneComparisons():
                if _slice.start < 0:
                    self._raise_negative_forbidden(_slice.start)
                if _slice.stop < 0:
                    self._raise_negative_forbidden(_slice.stop)

        if math.isfinite(self.length):
            int_indices = range(*_slice.indices(self.length))
        else:
            self._raise_if_infinite_result(_slice)
            max_length = 1

            # A tighter bound is surely possible, but is not necessary and this is easier to reason about
            if _slice.start is not None:
                max_length += abs(_slice.start)
            if _slice.stop is not None:
                max_length += abs(_slice.stop)

            int_indices = range(*_slice.indices(max_length))

        if self.definition == FlexibleSequenceDefinition.CONSTANT:
            slice_length = len(int_indices)
            return FlexibleSequence([self.wrapped] * slice_length)
        elif self.definition == FlexibleSequenceDefinition.DIRECT:
            return FlexibleSequence(self.wrapped[_slice])
        elif self.definition == FlexibleSequenceDefinition.CALLABLE:
            return FlexibleSequence([self._get_int(i) for i in int_indices])

    def _raise_if_infinite_result(self, _slice: slice):
        """
        A possible improvement would be to return an infinite generator. That's quite complex though.

        It may be possible to simplify the logic here, I used a brute force approach of hacking around until all tests
        passed...
        """
        step = _slice.step if _slice.step is not None else 1
        exception = IndexError(
            f"The result of slicing an infinite `FlexibleSequence` with [{_slice.start}:{_slice.stop}:{_slice.step}] would be infinite."
        )

        with CatchNoneComparisons():
            if _slice.start is None and _slice.stop is None:
                raise exception

            if step > 0:
                if _slice.stop is None:
                    if _slice.start >= 0:
                        raise exception
                if (_slice.start is None) or (_slice.start >= 0):
                    if _slice.stop < 0:
                        raise exception

            if step < 0:
                if _slice.start is None:
                    if _slice.stop >= 0:
                        raise exception
                if _slice.start < 0:
                    if (_slice.stop is None) or (_slice.stop >= 0):
                        raise exception

    def _raise_negative_forbidden(self, index):
        raise NotImplementedError(
            f"When supplying a callable without a `length`, the negative index {index} would lead to undefined behaviour."
        )


class CatchNoneComparisons(contextlib.AbstractContextManager):
    """
    Context manager to silently ignore comparisons to ``None`` that would raise a TypeError.

    Usage: ::

            with CatchNoneComparisons():
                    if number < 0:
                            print("it's negative!")
    """

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type == TypeError and "not supported between instances of 'NoneType'" in str(
            exc_value
        ):
            return True
