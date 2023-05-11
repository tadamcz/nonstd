from typing import Optional

import scipy.misc


def by_kwarg(f, x0: dict, deriv_dim: str, dx: Optional[float] = None) -> float:
    """
    TODO: add tests

    Wrapper around ``scipy.misc.derivative`` to handle keyword arguments, instead of being limited to positional arguments.
    Uses currying [0].

    [0]: https://en.wikipedia.org/wiki/Currying

    :param f: Function to differentiate
    :param x0: Point at which to differentiate, given as a dict of ``{argument_name: value}``
    :param deriv_dim: The name of dimension along which to differentiate, as a ``str`
    :param dx: Explicitly set the finite difference passed to SciPy.

    :return: The derivative of ``f`` with respect to ``deriv_dim`` at ``x0``.
    """

    if dx is None:
        if x0[deriv_dim] != 0:
            dx = x0[deriv_dim] / 100
        else:
            dx = 1e-12

    def curried_f(x):
        """
        ``f`` expressed as a function of the relevant dimension only
        """
        kwargs = x0
        kwargs[deriv_dim] = x
        return f(**kwargs)

    return scipy.misc.derivative(curried_f, x0=x0[deriv_dim], dx=dx)
