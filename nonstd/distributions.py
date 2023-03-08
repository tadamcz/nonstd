"""
TODO [Rob or Mahmoud might have good ideas]: figure out what to do about this 'frozen' business. What SciPy does
	about this seems hella ugly to me (see example of the pattern here [1]), but of course it's good practise to follow
	conventions set out by whatever one is inheriting from. Currently I'm doing a compromise that mostly follows SciPy's
	conventions but deviates in having separate classes explicitly named 'frozen' (which I admit has its own ugliness).
	[1] https://github.com/scipy/scipy/blob/27aaa296daf8f5a81beeb6504ae405719abee626/scipy/stats/_continuous_distns.py#L8812
"""

import numpy as np
from scipy import stats

def lognormal_mu_sigma(mean, sd):
	"""
	Get the ``mu`` and ``sigma`` parameters for a log-normal distribution with the given ``mean`` and ``sd``.
	"""
	var = sd ** 2
	sigma = np.sqrt(np.log(var / (mean ** 2) + 1))

	mu = np.log(mean) - (1 / 2) * np.log(var / (mean ** 2) + 1)

	return mu, sigma

def lognormal(mu, sigma):
	"""
	SciPy's ``lognorm`` does not take the ``mu`` and ``sigma`` parameters (it takes its own
	``scale`` and ``s`` parameters).

	This is a convenience wrapper that allows you to create a (frozen) SciPy log-normal distribution using ``mu`` and
	``sigma``.
	"""
	return stats.lognorm(scale=np.exp(mu), s=sigma)


def is_frozen_normal(distribution):
	"""Type checker"""
	if isinstance(distribution, stats._distn_infrastructure.rv_frozen):
		if isinstance(distribution.dist, stats._continuous_distns.norm_gen):
			return True
	return False


def is_frozen_lognormal(distribution):
	"""Type checker"""
	if isinstance(distribution, stats._distn_infrastructure.rv_frozen):
		if isinstance(distribution.dist, stats._continuous_distns.lognorm_gen):
			return True
	return False


def is_frozen_beta(distribution):
	"""Type checker"""
	if isinstance(distribution, stats._distn_infrastructure.rv_frozen):
		if isinstance(distribution.dist, stats._continuous_distns.beta_gen):
			return True
	return False


class TwoPieceUniform(stats.rv_continuous):
	"""
	A special class of piecewise uniform distributions, with the following restrictions:

	- the distribution is composed of only two pieces
	- each piece contains half the total probability mass

	This means the distribution can be defined by three numbers: its minimum, 50th percentile, and maximum.

	Note that for performance reasons, we don't want to use frozen instances of the components (i.e. the objects
	that would be created by calling e.g. ``stats.uniform(1,2)``). Freezing any distribution causes a large overhead in
	SciPy. This is what leads to this non-object-oriented style where the components are never instantiated, and the arguments
	``min``, ``p50``, ``max`` are instead passed around between methods.

	TODO: consider generalising to support an arbitrary middle quantile
	"""
	normalization_constant = 2

	def args(self, min, p50, max):
		return min, p50, max

	def _argcheck(self, min, p50, max):
		if not (min <= p50 <= max):
			raise ValueError(f"Parameters min={min}, p50={p50}, max={max} do not satisfy min ≤ p50 ≤ max.")

		return True

	def loc_scale(self, min, p50, max):
		"""
		Note the slightly counter-intuitive usage: using SciPy's parameters ``loc`` and ``scale``, one obtains the
		uniform distribution on ``[loc, loc + scale]``.
		"""
		return {
			"left": {"loc": min, "scale": p50 - min},
			"right": {"loc": p50, "scale": max - p50},
		}

	def left_pdf(self, x, min, p50, max):
		loc_scale = self.loc_scale(min, p50, max)["left"]
		return stats.uniform.pdf(x, **loc_scale) / self.normalization_constant

	def right_pdf(self, x, min, p50, max):
		loc_scale = self.loc_scale(min, p50, max)["right"]
		return stats.uniform.pdf(x, **loc_scale) / self.normalization_constant

	def left_ppf(self, p, min, p50, max):
		loc_scale = self.loc_scale(min, p50, max)["left"]
		return stats.uniform.ppf(p, **loc_scale)

	def right_ppf(self, p, min, p50, max):
		loc_scale = self.loc_scale(min, p50, max)["right"]
		return stats.uniform.ppf(p, **loc_scale)

	def _pdf_single(self, x, min, p50, max):
		if x < min:
			return 0
		elif x < p50:
			return self.left_pdf(x, min, p50, max)
		elif x < max:
			return self.right_pdf(x, min, p50, max)
		else:
			return 0

	def _pdf(self, x, min, p50, max):
		return np.vectorize(self._pdf_single)(x, min, p50, max)

	def _rvs(self, min, p50, max, size=None, random_state=None):
		probabilities = stats.uniform.rvs(size=size)

		draws = []

		for p in probabilities:
			if p < 0.5:
				p_piece = p * 2
				draw = self.left_ppf(p_piece, min, p50, max)
			else:
				p_piece = (p - 0.5) * 2
				draw = self.right_ppf(p_piece, min, p50, max)
			draws.append(draw)

		return draws

	def _ppf_single(self, q, min, p50, max):
		if q < 0.5:
			q_piece = q * 2
			return self.left_ppf(q_piece, min, p50, max)
		else:
			q_piece = (q - 0.5) * 2
			return self.right_ppf(q_piece, min, p50, max)

	def _ppf(self, x, min, p50, max):
		return np.vectorize(self._ppf_single)(x, min, p50, max)

	def _get_support(self, min, p50, max):
		return min, max


class FrozenTwoPieceUniform(stats._distn_infrastructure.rv_frozen):
	"""
	Helper to 'freeze' the distribution, i.e. fix its parameters. This appears to be the idiomatic way in SciPy.
	"""

	def __init__(self, min, p50, max):
		super().__init__(
			TwoPieceUniform(name='Two-piece uniform'),
			min, p50, max
		)

	def __repr__(self):
		min, p50, max = self.args
		return f"FrozenTwoPieceUniform(min={min}, p50={p50}, max={max})"


class Certainty(stats.rv_continuous):
	"""
	A discrete distribution with probability 1 on a single value.

	We need to subclass ``rv_continuous`` instead of ``rv_discrete`` because the latter class assumes the support
	is a subset of the integers.
	"""

	def args(self, value):
		return [value]

	def _argcheck(self, value):
		return np.isreal(value)

	def _cdf_single(self, x, value):
		if x < value:
			return 0
		else:
			return 1

	def _cdf(self, x, value):
		return np.vectorize(self._cdf_single)(x, value)

	def _rvs(self, value, size=None, random_state=None):
		return np.full(size, value)

	def _ppf_single(self, value):
		return value

	def _ppf(self, x, value):
		return np.vectorize(self._ppf_single)(value)

	def _get_support(self, value):
		return value, value


class FrozenCertainty(stats._distn_infrastructure.rv_frozen):
	"""
	Helper to 'freeze' the distribution, i.e. fix its parameters. This appears to be the idiomatic way in SciPy.
	"""

	def __init__(self, value):
		super().__init__(
			Certainty(name='Certainty distribution'),
			value
		)

	def __repr__(self):
		value, = self.args
		return f"FrozenCertainty({value})"
