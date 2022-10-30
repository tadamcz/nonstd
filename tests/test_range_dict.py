import pytest

from nonstd.sequence import RangeDict


class TestRangeDict:
	def test_append(self):
		rd = RangeDict()
		rd.append(1)
		assert rd == {0:1}

		rd = RangeDict(start=5)
		rd.append(1)
		assert rd == {5: 1}

	def test_extend(self):
		rd = RangeDict()
		rd.extend((1, 2))
		assert rd == {0: 1, 1: 2}

		rd = RangeDict(["hello"], start=5)
		rd.extend((1, 2))
		assert rd == {5: "hello", 6: 1, 7: 2}

	def test_step(self):
		rd = RangeDict([1,2,3], start=5, step=10)
		rd.append(4)
		assert rd == {5:1, 15:2, 25:3, 35:4}

	def test_pop(self):
		rd = RangeDict((1,2), start=42)

		assert rd.pop(42) == 1
		with pytest.raises(KeyError):
			rd.pop(42)
		assert rd.pop(43) == 2

	def test_access_slice(self):
		rd = RangeDict([1, 2, 3], start=1)
		assert rd[1:2] == RangeDict([1], start=1)
		assert rd[:2] == RangeDict([1], start=1)

		assert rd[2:4] == RangeDict([2, 3], start=2)
		assert rd[2:] == RangeDict([2, 3], start=2)

		assert rd[1:3] == RangeDict([1, 2], start=1)

		assert rd[:4] == RangeDict([1, 2, 3], start=1)
		assert rd[:1] == RangeDict([], start=1)

		assert rd[:4:2] == RangeDict([1, 3], start=1, step=2)
		assert rd[1:4:2] == RangeDict([1, 3], start=1, step=2)
