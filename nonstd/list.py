import collections.abc
from typing import Optional


class OneIndexedList(collections.UserList):
	"""
	Behaves like a regular Python ``list``, but with the index starting at 1 instead of 0.
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
		if not isinstance(other, OneIndexedList):
			# This is a judgement call. One could also follow ``UserList``, which allows comparisons to a simple ``list``.
			raise NotImplementedError(f"Cannot compare a `OneIndexedList` to a {other.__class__.__name__}")
		return self.data == other.data

	def __iter__(self):
		yield from self.data.__iter__()
