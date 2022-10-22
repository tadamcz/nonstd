import numpy as np
import pytest
from scipy import stats

from nonstd.distributions import lognormal, is_frozen_normal, is_frozen_lognormal, is_frozen_beta, \
	FrozenTwoPieceUniform, FrozenCertainty
from nonstd.sequence_math import is_arithmetic_sequence


@pytest.fixture(params=[-1, 0, 3], ids=lambda p: f"mu={p}")
def mu(request):
	return request.param


@pytest.fixture(params=[1, 2], ids=lambda p: f"sigma={p}")
def sigma(request):
	return request.param


def test_lognormal(mu, sigma):
	dist = lognormal(mu=mu, sigma=sigma)

	# Expectation
	assert dist.mean() == pytest.approx(np.exp(mu + sigma ** 2 / 2))

	# Median
	assert dist.ppf(0.5) == pytest.approx(np.exp(mu))


def test_is_frozen():
	normal = stats.norm(1, 1)
	assert is_frozen_normal(normal)
	assert not is_frozen_lognormal(normal)
	assert not is_frozen_beta(normal)

	lognormal = stats.lognorm(1, 1)
	assert not is_frozen_normal(lognormal)
	assert is_frozen_lognormal(lognormal)
	assert not is_frozen_beta(lognormal)

	beta = stats.beta(1, 1)
	assert not is_frozen_normal(beta)
	assert not is_frozen_lognormal(beta)
	assert is_frozen_beta(beta)

	# Distributions that are not frozen
	assert not is_frozen_normal(stats.norm)
	assert not is_frozen_lognormal(stats.lognorm)
	assert not is_frozen_beta(stats.beta)

	# Other objects
	assert not is_frozen_normal(12)
	assert not is_frozen_normal(lambda x: x ** 2)


@pytest.fixture(params=[
	(0, 2, 3),
	(0, 1, 2),
	(-1, 0, 2),
], ids=lambda p: p)
def triple(request):
	return request.param


class TestFrozenTwoPieceUniform:
	def test_pdf(self):
		min, p50, max = 0, 2, 3
		dist = FrozenTwoPieceUniform(min, p50, max)

		assert dist.pdf(0.5) == pytest.approx(1 / 2 * dist.pdf(2.5))

		assert dist.pdf(min - 0.5) == 0
		assert dist.pdf(max + 0.5) == 0

	def test_cdf(self, triple):
		min, p50, max = triple

		dist = FrozenTwoPieceUniform(min, p50, max)

		assert dist.cdf(min) == pytest.approx(0)
		assert dist.cdf(p50) == pytest.approx(0.5)
		assert dist.cdf(max) == pytest.approx(1)

	def test_ppf(self, triple):
		min, p50, max = triple
		dist = FrozenTwoPieceUniform(min, p50, max)

		assert dist.ppf(0) == pytest.approx(min)
		assert is_arithmetic_sequence(dist.ppf([0, 0.1, 0.2, 0.3]))
		assert dist.ppf(0.5) == pytest.approx(p50)
		assert is_arithmetic_sequence(dist.ppf([0.5, 0.6, 0.7, 0.8]))
		assert dist.ppf(1) == pytest.approx(max)

	def test_rvs(self, triple, random_seed):
		"""
		Use the Kolmogorov-Smirnov statistic to check that samples drawn from the two-piece come from the same
		distribution as two samples drawn from two appropriate uniform distributions.
		"""

		min, p50, max = triple
		dist = FrozenTwoPieceUniform(min, p50, max)

		n = 75_000
		test_draws = dist.rvs(n)




@pytest.fixture(params=[0, 1.23])
def certainty_value(request):
	return request.param


class TestCertainty:
	def test_rvs(self, certainty_value):
		dist = FrozenCertainty(certainty_value)
		n = 10
		assert np.all(dist.rvs(size=n) == certainty_value)

	def test_cdf(self, certainty_value):
		dist = FrozenCertainty(certainty_value)
		assert dist.cdf(certainty_value - 1) == 0
		assert dist.cdf(certainty_value + 1) == 1

	def test_ppf(self, certainty_value):
		dist = FrozenCertainty(certainty_value)
		for p in [0.1, 0.123, 0.8]:
			assert dist.ppf(p) == pytest.approx(certainty_value)
