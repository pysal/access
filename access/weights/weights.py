import numpy as np

def step_fn(step_dict):
    if type(step_dict) != dict:
        raise TypeError('step_dict must be of type dict.')

    for v in step_dict.values():
        if v < 0:
            raise ValueError('All weights must be positive.')

    def helper(key_to_test):
        for k,v in sorted(step_dict.items()):
            if key_to_test <= k:
                return v
        return 0
    return helper

def gaussian(width):
  if width == 0:
      raise ValueError("Width must be non-zero.")

  return lambda x: np.exp(-x*x / (2 * width**2)) \
                   / np.sqrt(2*np.pi*width**2)

def gravity(scale = 1, alpha = -1):

  return lambda x: np.power(x / scale, alpha)
