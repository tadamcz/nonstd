import pytest

from nonstd.distributions import (
    uniform_from_quantiles,
    normal_from_quantiles,
    lognormal_from_quantiles,
)


@pytest.mark.parametrize(
    "quantiles",
    [
        {0: -0.5, 1: 1},  # 0th and 100th quantiles are allowed
        {0.5: 0, 0.75: 3},
    ],
    ids=lambda x: str(x),
)
def test_uniform(quantiles):
    dist = uniform_from_quantiles(quantiles)

    for p, q in quantiles.items():
        assert dist.cdf(q) == pytest.approx(p)
    methods_do_not_raise(dist)


@pytest.mark.parametrize("quantiles", [{0.1: 1, 0.5: 5}, {0.1: -10, 0.5: 0}], ids=lambda x: str(x))
def test_normal(quantiles):
    dist = normal_from_quantiles(quantiles)
    for p, q in quantiles.items():
        assert dist.cdf(q) == pytest.approx(p)
    methods_do_not_raise(dist)


@pytest.mark.parametrize("quantiles", [{0.1: 1, 0.5: 5}, {0.1: 10, 0.5: 20}], ids=lambda x: str(x))
def test_lognormal(quantiles):
    dist = lognormal_from_quantiles(quantiles)
    for p, q in quantiles.items():
        assert dist.cdf(q) == pytest.approx(p)
    methods_do_not_raise(dist)


def methods_do_not_raise(dist):
    dist.ppf(0.5)
    dist.rvs(size=10)
