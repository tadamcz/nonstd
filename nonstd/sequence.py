import collections.abc
import enum
import math
from itertools import count
from math import inf, ceil
from numbers import Number
from typing import Optional, Union, Sequence, Callable


class OneIndexedList(collections.UserList):
	"""
	Behaves like a regular Python ``list``, but with the index starting at 1 instead of 0.

	Also provides the ``dict``-like methods ``.keys()`` and ``.items()``
	"""

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
		if index == 0:
			raise IndexError(
				f"This {self.__class__.__name__} is an instance of `OneIndexedList`. Index 0 is forbidden.")
		if index > 0:
			return index - 1
		else:  # In Python, negative indices are used to count backwards from the last element of a list
			return index

	def __getitem__(self, index: [int, slice]) -> any:
		wrapped_i = self._wrapped_index(index)
		return super(OneIndexedList, self).__getitem__(wrapped_i)

	def __setitem__(self, index: [int, slice], value: any) -> None:
		wrapped_i = self._wrapped_index(index)
		super(OneIndexedList, self).__setitem__(wrapped_i, value)

	def __delitem__(self, index: [int, slice]) -> None:
		wrapped_i = self._wrapped_index(index)
		super(OneIndexedList, self).__delitem__(wrapped_i)

	def insert(self, index: [int, slice], value: any) -> None:
		wrapped_i = self._wrapped_index(index)
		super(OneIndexedList, self).insert(wrapped_i, value)

	def pop(self, index: Optional[int] = None) -> any:
		if index is None:
			return self.data.pop()
		wrapped_i = self._wrapped_index(index)
		return super(OneIndexedList, self).pop(wrapped_i)

	def index(self, value: any, start: int = None, stop: int = None) -> int:
		if start is None:
			start = 1
		if stop is None:
			stop = len(self) + 1

		wrapped_start = self._wrapped_index(start)
		wrapped_stop = self._wrapped_index(stop)
		wrapped_result = super(OneIndexedList, self).index(value, wrapped_start, wrapped_stop)

		return wrapped_result + 1

	def __eq__(self, other) -> bool:
		if other is None:
			return False
		if not isinstance(other, OneIndexedList):
			# This is a judgement call. One could also follow ``UserList``, which allows comparisons to a simple ``list``.
			raise NotImplementedError(f"Cannot compare a `OneIndexedList` to a {other.__class__.__name__}")
		return self.data == other.data

	def __iter__(self):
		yield from self.data.__iter__()

	def keys(self):
		return list(range(1, len(self.data) + 1))

	def items(self):
		"""
		Behaves similarly to calling ``enumerate()`` on a regular ``list``.
		"""
		return [(key, self[key]) for key in self.keys()]


class FlexibleSequenceDefinition(enum.Enum):
	DIRECT = enum.auto()
	CONSTANT = enum.auto()
	CALLABLE = enum.auto()


class FlexibleSequence(collections.abc.Sequence):
	def __init__(self, spec: Union[Sequence, object, Callable], length: Optional[int] = None, callable_start_i:Optional[int]=0):
		"""
		Specify a sequence in one of three ways:

		-
			directly provide a sequence, in which case the ``FlexibleSequence`` will simply wrap that sequence without any
			changes.

		-
			provide a single object; the ``FlexibleSequence`` will behave like a sequence with that object at every index.

		-
			provide a callable (e.g. a function); the ``FlexibleSequence`` will behave such that
			``flexible_seq[i] == callable(callable_start_i+i)`` for all ``i``.


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
			return self.get_slice(index)
		if isinstance(index, int):
			return self.get_int(index)

	def __eq__(self, other) -> bool:
		if other is None:
			return False
		return [i for i in self] == [i for i in other]

	def __repr__(self):
		if math.isfinite(self.length):
			return [i for i in self].__repr__()
		else:
			return f"FlexibleSequence({self.wrapped})"

	def get_int(self, index):
		if self.definition == FlexibleSequenceDefinition.CONSTANT:
			return self.wrapped
		elif self.definition == FlexibleSequenceDefinition.DIRECT:
			return self.wrapped[index]
		elif self.definition == FlexibleSequenceDefinition.CALLABLE:
			if index < 0:
				raise NotImplementedError("Negative indices with callables would lead to unexpected behaviour.")
			return self.wrapped(self.c_start_i + index)

	def get_slice(self, slice):
		if isinstance(self.wrapped, (Number, Callable)):
			if slice.stop is None and math.isinf(self.length):
				raise IndexError(
					f"You must provide a slice stop when the `SequenceSpecifier` is infinite.")
			if self.length is None:
				slice_len = self._slice_len(slice, inf)
			else:
				slice_len = self._slice_len(slice, self.length)

		if self.definition == FlexibleSequenceDefinition.CONSTANT:
			return FlexibleSequence([self.wrapped] * slice_len)
		elif self.definition == FlexibleSequenceDefinition.DIRECT:
			return FlexibleSequence(self.wrapped[slice])
		elif self.definition == FlexibleSequenceDefinition.CALLABLE:
			if slice.stop is None:
				end_range = self.length
			else:
				end_range = min(self.length, slice.stop)

			indices = range(end_range)[slice]
			return FlexibleSequence([self.get_int(i) for i in indices])

	def _max_slice_len(self, s: slice):
		"""https://stackoverflow.com/a/65500526/8010877"""
		assert s.stop or s.stop == 0, "Must define stop for max slice len!"
		assert s.step != 0, "Step slice cannot be zero"

		start = s.start or 0
		stop = s.stop
		step = s.step or 1

		delta = (stop - start)
		dsteps = int(ceil(delta / step))

		return dsteps if dsteps >= 0 else 0

	def _slice_len(self, s: slice, src_len: int):
		"""https://stackoverflow.com/a/65500526/8010877"""
		if (s.start is None or s.start == 0) and s.stop is None:
			return self.length
		stop = min(s.stop, src_len)
		return self._max_slice_len(slice(s.start, stop, s.step))
