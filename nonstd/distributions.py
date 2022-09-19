import numpy as np
from scipy import stats


def lognormal(mu, sigma):
    """
    SciPy's `lognorm` does not take the `mu` and `sigma` parameters (it takes its own
    `location` and `scale` parameters).

    This is a convenience wrapper that allows you to create a (frozen) SciPy log-normal distribution using `mu` and
    `sigma`.
    """
    return stats.lognorm(scale=np.exp(mu), s=sigma)


def is_frozen_normal(distribution):
    if isinstance(distribution, stats._distn_infrastructure.rv_frozen):
        if isinstance(distribution.dist, stats._continuous_distns.norm_gen):
            return True
    return False


def is_frozen_lognormal(distribution):
    if isinstance(distribution, stats._distn_infrastructure.rv_frozen):
        if isinstance(distribution.dist, stats._continuous_distns.lognorm_gen):
            return True
    return False


def is_frozen_beta(distribution):
    if isinstance(distribution, stats._distn_infrastructure.rv_frozen):
        if isinstance(distribution.dist, stats._continuous_distns.beta_gen):
            return True
    return False
