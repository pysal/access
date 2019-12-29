import sys
sys.path.append('../..')

import math
import unittest
from random import randint

import numpy as np
import pandas as pd
from access import weights
from access.util import testing as tu


class TestWeights(unittest.TestCase):

    def setUp(self):
        self.r_int = randint(2,101)
        self.series = pd.Series(range(1,self.r_int))


    def apply_weight_fn(self, weight_fn):
        weight_vs = self.series.apply(weight_fn)
        w_applied = self.series * weight_vs

        return w_applied


    def test_step_fn_all_weight_zero_equals_zero_sum(self):
        weight_fn = weights.step_fn({self.r_int: 0})
        w_applied = self.apply_weight_fn(weight_fn)

        expected = w_applied.sum()
        self.assertEqual(expected, 0)


    def test_step_fn_all_weight_one_equals_self(self):
        weight_fn = weights.step_fn({self.r_int: 1})
        w_applied = self.apply_weight_fn(weight_fn)

        expected = w_applied.sum()
        actual = self.series.sum()

        self.assertEqual(expected, actual)


    def test_step_fn_all_weight_half_equals_half(self):
        weight_fn = weights.step_fn({self.r_int: .5})
        w_applied = self.apply_weight_fn(weight_fn)

        expected = w_applied.sum()
        actual = self.series.sum()/2

        self.assertEqual(expected, actual)


    def test_step_fn_all_weight_two_equals_twice(self):
        weight_fn = weights.step_fn({self.r_int: 2})
        w_applied = self.apply_weight_fn(weight_fn)

        expected = w_applied.sum()
        actual = self.series.sum()*2

        self.assertEqual(expected, actual)


    def test_step_fn_negative_weight_raises_error(self):
        with self.assertRaises(ValueError):
            weight_fn = weights.step_fn({self.r_int: -1})


    def test_step_fn_non_dict_input_raises_error(self):
        with self.assertRaises(TypeError):
            weights.step_fn(1)

        with self.assertRaises(TypeError):
            weights.step_fn('a')

        with self.assertRaises(TypeError):
            weights.step_fn([])

        with self.assertRaises(TypeError):
            weights.step_fn(1.0)


    def test_gaussian_width_zero_raises_error(self):
        with self.assertRaises(ValueError):
            weight_fn = weights.gaussian(0)
            w_applied = self.apply_weight_fn(weight_fn)
