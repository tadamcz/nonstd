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
