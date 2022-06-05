import numpy as np


def step_fn(step_dict):
    """
    Create a step function from a dictionary.

    Parameters
    ----------
    step_dict           : dict
                          Dictionary of cut-offs and weight values.

    Returns
    -------

    weight_function     : function
                          Function returning weight, for input distance or time, *x*.
                          Values beyond the largest threshold will return 0.

    Examples
    --------

    Import the weights:

    >>> from access import weights

    Create a step function with thresholds at 20, 40, and 60.
    Travel costs are in minutes here, but the code cannot tell if you mix units!

    >>> fn = weights.step_fn({20 : 1, 40 : 0.68, 60 : 0.22})

    >>> {v : fn(v) for v in range(0, 71, 10)}
    {0: 1, 10: 1, 20: 1, 30: 0.68, 40: 0.68, 50: 0.22, 60: 0.22, 70: 0}
    """

    if type(step_dict) != dict:
        raise TypeError("step_dict must be of type dict.")

    for v in step_dict.values():
        if v < 0:
            raise ValueError("All weights must be positive.")

    def helper(key_to_test):

        for k, v in sorted(step_dict.items()):
            if key_to_test <= k:
                return v

        return 0

    return helper


def gaussian(sigma):
    """
    Create a gaussian weight function, for a specified width, :math:`\sigma`.
    The mean / location parameter is assumed to be 0.
    Note that the standard normalization of the Gaussian, :math:`1 / \sqrt{2\pi\sigma^2}`,
    is *not* applied, so :math:`f(0) = 1` regardless of the value of :math:`\sigma`.
    Of course, this is irrelevant if the ultimate access values are ultimately normalized.

    Parameters
    ----------
    sigma               : float
                          This the classical width parameter of the Gaussian / Normal distriution.

    Returns
    -------

    weight_function     : function
                          Function returning weight, for input distance or time, *x*.

    Examples
    --------

    Import the weights.

    >>> from access import weights

    Create a step function with thresholds at 20, 40, and 60.
    Travel costs are in minutes here, but the code cannot tell if you mix units!

    >>> fn = weights.gaussian(sigma = 20)

    >>> {v : fn(v) for v in range(0, 61, 20)}
    {0: 1.0, 20: 0.6065306597126334, 40: 0.1353352832366127, 60: 0.011108996538242306}

    Compare this to a simpler formulation:

    >>> import numpy as np
    >>> {x : np.exp(-x**2/2) for x in range(4)}
    {0: 1.0, 1: 0.6065306597126334, 2: 0.1353352832366127, 3: 0.011108996538242306}
    """

    if sigma == 0:
        raise ValueError("Sigma must be non-zero.")

    return lambda x: np.exp(-x * x / (2 * sigma**2))  # / np.sqrt(2*np.pi*sigma**2)


def gravity(scale, alpha, min_dist=0):
    """
    Create a gravity function from a scale :math:`s` and :math:`\\alpha` parameters
    as well as an optional minimum distance :math:`x_\\text{min}`.
    The function is of the form :math:`f(x) = (\\text{max}(x, x_\\text{min})/s)^\\alpha`.
    Note that there is no overall normalization.

    Parameters
    ----------
    scale               : float
                          Scaling value, normalizing the function input.
    alpha               : float
                          Power to which the normalized inputs are raised.
                          Note that it is not implicitly negative (i.e., :math:`x^\\alpha` instead of :math:`1/x^\\alpha`.
    min_dist            : float
                          A 'standard' issue with gravity model is the infinite potential at 0 distance or time.
                          This can be rectified crudely by specifying a minimum distance,
                          and setting any input exceeding that minimum to the minimum itself.
                          The default threshold is 0.

    Returns
    -------

    weight_function     : function
                          Function returning weight, for input distance or time, *x*.

    Examples
    --------

    Import the weights:

    >>> from access import weights

    Create a step function with thresholds at 20, 40, and 60.
    Travel costs are in minutes here, but the code cannot tell if you mix units!

    >>> fn = weights.gravity(scale = 20, alpha = -2, min_dist = 1)

    >>> {t : round(fn(t), 2) for t in [0, 1, 2, 20, 40, 60]}
    {0: 400.0, 1: 400.0, 2: 100.0, 20: 1.0, 40: 0.25, 60: 0.11}
    """

    return lambda x: np.power(max(x, min_dist) / scale, alpha)
