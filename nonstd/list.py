import collections.abc
from typing import Iterable, Optional


class OneIndexedList(collections.abc.MutableSequence):
	"""
	Behaves like a regular Python ``list``, but with the index starting at 1 instead of 0.
	"""

	def __init__(self, init: list = None) -> None:
		self._wrapped = []
		if init is not None:
			self._wrapped.extend(init)

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
		return self._wrapped[wrapped_i]

	def __setitem__(self, index: [int, slice], val: any) -> None:
		wrapped_i = self._wrapped_index(index)
		self._wrapped[wrapped_i] = val

	def __delitem__(self, index: [int, slice]) -> None:
		wrapped_i = self._wrapped_index(index)
		del self._wrapped[wrapped_i]

	def insert(self, index: [int, slice], val: any) -> None:
		wrapped_i = self._wrapped_index(index)
		self._wrapped.insert(wrapped_i, val)

	def __len__(self) -> int:
		return len(self._wrapped)

	def __repr__(self) -> str:
		return f"{self._wrapped}"

	def __eq__(self, other) -> bool:
		if not isinstance(other, OneIndexedList):
			raise NotImplementedError(f"Cannot compare a `OneIndexedList` to a {other.__class__.__name__}")
		return self._wrapped == other._wrapped

	def append(self, value: any) -> None:
		self._wrapped.append(value)

	def extend(self, values: Iterable) -> None:
		self._wrapped.extend(values)

	def pop(self, index: Optional[int] = None) -> any:
		if index is None:
			return self._wrapped.pop()
		wrapped_i = self._wrapped_index(index)
		return self._wrapped.pop(wrapped_i)

	def index(self, value: any, start: int = None, stop: int = None) -> int:
		if start is None:
			start = 1
		if stop is None:
			stop = len(self) + 1

		wrapped_start = self._wrapped_index(start)
		wrapped_stop = self._wrapped_index(stop)
		wrapped_i = self._wrapped.index(value, wrapped_start, wrapped_stop)

		return wrapped_i + 1

	def reverse(self) -> None:
		self._wrapped.reverse()

	def sort(self, key=None, reverse=False):
		self._wrapped.sort(key=key, reverse=reverse)

	def remove(self, value: any):
		self._wrapped.remove(value)

	def count(self, value: any) -> int:
		return self._wrapped.count(value)

	def copy(self):
		return OneIndexedList(self._wrapped)
