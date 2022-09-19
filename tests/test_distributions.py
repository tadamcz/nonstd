import numpy as np
import pytest

from nonstd.distributions import lognormal


@pytest.fixture(params=[-1, 0, 3], ids=lambda p: f"mu={p}")
def mu(request):
    return request.param


@pytest.fixture(params=[1, 2], ids=lambda p: f"sigma={p}")
def sigma(request):
    return request.param


def test_lognormal(mu, sigma):
    dist = lognormal(mu=mu, sigma=sigma)

    # Expectation
    assert dist.mean() == pytest.approx(np.exp(mu + sigma**2 /2))

    # Median
    assert dist.ppf(0.5) == pytest.approx(np.exp(mu))