import collections.abc
import enum
import math
from itertools import count
from math import ceil, inf
from numbers import Number
from typing import Sequence, Union, Callable, Optional

import numpy as np
import pytest


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
		if ratio != pytest.approx(common_ratio):
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
	return np.all(diff == pytest.approx(common_difference))


class FlexibleSequenceType(enum.Enum):
	DIRECT = enum.auto()
	CONSTANT = enum.auto()
	CALLABLE = enum.auto()


class FlexibleSequence(collections.abc.Sequence):
	def __init__(self, spec: Union[Sequence, object, Callable], length: Optional[int] = None, callabe_start_i:Optional[int]=0):
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

		:param callabe_start_i: The callable argument that corresponds to the 0 index of the ``FlexibleSequence``.``flexible_seq[0]==callable(callable_start_i)``
		"""
		if isinstance(spec, Sequence) and length and len(spec) != length:
			raise ValueError(f"Mismatched lengths: len(spec)={len(spec)}, length={length}")

		self.c_start_i = callabe_start_i
		self.wrapped = spec

		if isinstance(self.wrapped, Sequence):
			self.type = FlexibleSequenceType.DIRECT
			length = len(self.wrapped)
		elif isinstance(self.wrapped, Callable):
			self.type = FlexibleSequenceType.CALLABLE
		else:  # any other object
			self.type = FlexibleSequenceType.CONSTANT

		if length is None:
			self.length = inf
		else:
			self.length = length

	def __iter__(self):
		if self.type == FlexibleSequenceType.DIRECT:
			yield from self.wrapped.__iter__()
		else:
			if math.isfinite(self.length):
				yield from (self[i] for i in range(self.length))
			else:
				yield from (self[i] for i in count())

	def __len__(self):
		if self.type == FlexibleSequenceType.DIRECT:
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
		return [i for i in self] == [i for i in other]

	def __repr__(self):
		if math.isfinite(self.length):
			return [i for i in self].__repr__()
		else:
			return f"FlexibleSequence({self.wrapped})"

	def get_int(self, index):
		if self.type == FlexibleSequenceType.CONSTANT:
			return self.wrapped
		elif self.type == FlexibleSequenceType.DIRECT:
			return self.wrapped[index]
		elif self.type == FlexibleSequenceType.CALLABLE:
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

		if self.type == FlexibleSequenceType.CONSTANT:
			return FlexibleSequence([self.wrapped] * slice_len)
		elif self.type == FlexibleSequenceType.DIRECT:
			return FlexibleSequence(self.wrapped[slice])
		elif self.type == FlexibleSequenceType.CALLABLE:
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
