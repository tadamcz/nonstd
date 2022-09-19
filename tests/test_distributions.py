import numpy as np
import pytest
from scipy import stats

from nonstd.distributions import lognormal, is_frozen_normal, is_frozen_lognormal, is_frozen_beta


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


def test_is_frozen():
    normal = stats.norm(1,1)
    assert is_frozen_normal(normal)
    assert not is_frozen_lognormal(normal)
    assert not is_frozen_beta(normal)

    lognormal = stats.lognorm(1,1)
    assert not is_frozen_normal(lognormal)
    assert is_frozen_lognormal(lognormal)
    assert not is_frozen_beta(lognormal)

    beta = stats.beta(1,1)
    assert not is_frozen_normal(beta)
    assert not is_frozen_lognormal(beta)
    assert is_frozen_beta(beta)

    # Distributions that are not frozen
    assert not is_frozen_normal(stats.norm)
    assert not is_frozen_lognormal(stats.lognorm)
    assert not is_frozen_beta(stats.beta)

    # Other objects
    assert not is_frozen_normal(12)
    assert not is_frozen_normal(lambda x: x**2)