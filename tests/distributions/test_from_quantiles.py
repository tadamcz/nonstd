import pytest

from nonstd.distributions import uniform_from_quantiles

@pytest.fixture(params=[0, 1], ids=lambda p: f"q0={p}")
def q0(request):
    return request.param

@pytest.fixture(params=[2, 4.2], ids=lambda p: f"q1={p}")
def q1(request):
    return request.param

@pytest.fixture(params=[0, .1, .2, .7], ids=lambda p: f"p0={p}")
def p0(request):
    return request.param

@pytest.fixture(params=[0.5], ids=lambda p: f"p1={p}")
def p1(request):
    return request.param


@pytest.fixture
def quantiles_pair(q0, q1, p0, p1):
    q0, q1 = sorted([q0, q1])
    p0, p1 = sorted([p0, p1])
    return {p0: q0, p1: q1}


def test_uniform(quantiles_pair):
    dist = uniform_from_quantiles(quantiles_pair)

    for p, q in quantiles_pair.items():
        assert dist.cdf(q) == pytest.approx(p)

    # Does not raise
    dist.rvs()
    dist.pdf(0)
    dist.ppf(0.5)