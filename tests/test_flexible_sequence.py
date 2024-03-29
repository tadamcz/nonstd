from collections import OrderedDict

import pytest

from nonstd.sequence import OneIndexedList, FlexibleSequenceDefinition, FlexibleSequence


@pytest.fixture(params=[FlexibleSequenceDefinition.DIRECT, FlexibleSequenceDefinition.CALLABLE])
def one_two_three(request):
    if request.param == FlexibleSequenceDefinition.DIRECT:
        return FlexibleSequence((1, 2, 3))
    if request.param == FlexibleSequenceDefinition.CALLABLE:
        return FlexibleSequence(lambda index: index + 1, length=3)


@pytest.fixture()
def one_with_length():
    return FlexibleSequence(1, length=5)


@pytest.fixture(params=list(range(-4, 4)) + [None], ids=lambda x: f"start={x}")
def start(request):
    return request.param


@pytest.fixture(params=list(range(-4, 4)) + [None], ids=lambda x: f"stop={x}")
def stop(request):
    return request.param


@pytest.fixture(params=list(range(-4, 0)) + list(range(1, 4)) + [None], ids=lambda x: f"step={x}")
def step(request):
    return request.param


class TestFlexibleSequence:
    def test_init(self):
        s = FlexibleSequence(1)
        assert s.definition == FlexibleSequenceDefinition.CONSTANT

        s = FlexibleSequence(dict(hello="world"))
        assert s.definition == FlexibleSequenceDefinition.CONSTANT

        # Unclear if this is the ideal behaviour, but it's a defensible choice, and I'll go with it
        s = FlexibleSequence(OrderedDict(hello="world"))
        assert s.definition == FlexibleSequenceDefinition.CONSTANT

        f = lambda x: x**2
        s = FlexibleSequence(f)
        assert s.definition == FlexibleSequenceDefinition.CALLABLE

        s = FlexibleSequence((1, 2, 3))
        assert s.definition == FlexibleSequenceDefinition.DIRECT

        s = FlexibleSequence([1, 2, 3])
        assert s.definition == FlexibleSequenceDefinition.DIRECT

        s = FlexibleSequence(OneIndexedList([1, 2, 3]))
        assert s.definition == FlexibleSequenceDefinition.DIRECT

    def test_length(self):
        s = FlexibleSequence(1, length=3)
        assert len(s) == 3

        s = FlexibleSequence(1)
        with pytest.raises(IndexError, match="Infinite"):
            len(s)

        s = FlexibleSequence((1, 2))
        assert len(s) == 2

    def test_callable_start(self):
        f = lambda x: x**2
        assert FlexibleSequence(f, callable_start_i=5, length=4) == [25, 36, 49, 64]
        assert FlexibleSequence(f, length=4) == [0, 1, 4, 9]

        # The parameter is ignored
        assert FlexibleSequence((1, 2), callable_start_i=42) == FlexibleSequence((1, 2))
        assert FlexibleSequence(1, callable_start_i=42, length=100) == FlexibleSequence(
            1, length=100
        )

    def test_iteration(self):
        s = FlexibleSequence((1, 2, 3))
        assert [i for i in s] == [1, 2, 3]

        s = FlexibleSequence(1, length=3)
        # If we had not provided a `length`, the next line would lead to an infinite loop
        assert [i for i in s] == [1, 1, 1]

        s = FlexibleSequence(1)
        assert [s[i] for i in range(1000)] == [1] * 1000

        s = FlexibleSequence(lambda x: x)
        # This is allowed, but would lead to an infinite loop without a `break` clause
        for i in s:
            if i > 100:
                break

    def test_access_integer(self):
        s = FlexibleSequence((1, 2, 3))
        assert s[0] == 1
        assert s[-1] == 3

        s = FlexibleSequence(5)
        assert s[0] == 5
        assert s[-1] == 5

        f = lambda x: x**2
        infinite = FlexibleSequence(f)
        assert infinite[4] == 16
        with pytest.raises(NotImplementedError):
            infinite[-2]
        with pytest.raises(NotImplementedError):
            infinite[-2:-1]

        finite = FlexibleSequence(f, length=5)
        assert finite[-1] == 16
        assert finite[-3:] == [4, 9, 16]

    def test_access_slice_finite(self, one_two_three, one_with_length, start, stop, step):
        assert one_two_three[start:stop:step] == [1, 2, 3][start:stop:step]

        # Does not raise IndexError
        one_with_length[start:stop:step]

    def test_access_slice_infinite(self, start, stop, step):
        one = FlexibleSequence(1)  # without a length

        # A bit of a hack: If the slice's size depends on the size of the list being sliced, then we should expect
        # an IndexError when attempting to slice an infinite `FlexibleSequence`.
        size_dependent_slice = len(list(range(100))[start:stop:step]) < len(
            list(range(1000))[start:stop:step]
        )

        if size_dependent_slice:
            with pytest.raises(IndexError):
                one[start:stop:step]
        else:
            LARGE_NUMBER = 1000
            length = len(list(range(LARGE_NUMBER))[start:stop:step])
            assert one[start:stop:step] == [1] * length

    def test_equality(self):
        assert (
            FlexibleSequence(lambda x: x**2, length=5)
            == FlexibleSequence([0, 1, 4, 9, 16])
            == [0, 1, 4, 9, 16]
        )

        assert FlexibleSequence((1, 2, 3)) != None

    def test_idempotency(self):
        assert FlexibleSequence([1, 2, 3]) == FlexibleSequence(FlexibleSequence([1, 2, 3]))

    def test_repr(self):
        assert str(FlexibleSequence(1)) == "FlexibleSequence(1)"
        assert str(FlexibleSequence(lambda x: x, length=3)) == "[0, 1, 2]"
        assert str(FlexibleSequence(lambda x: x)) == "FlexibleSequence(function)"
        assert str(FlexibleSequence(None)) == "FlexibleSequence(None)"
