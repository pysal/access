import sys
sys.path.append('../..')

import math
import unittest

import numpy as np
import pandas as pd
import geopandas as gpd
from access import access, weights
from access.util import testing as tu


class TestWeightedCatchment(unittest.TestCase):

    def setUp(self):
        n = 5
        supply_grid = tu.create_nxn_grid(n)
        demand_grid = supply_grid.sample(1)
        cost_matrix = tu.create_cost_matrix(supply_grid, 'euclidean')

        self.model = access(demand_df = demand_grid, demand_index = 'id',
                            demand_value = 'value',
                            supply_df = supply_grid, supply_index = 'id',
                            supply_value = 'value',
                            cost_df   = cost_matrix, cost_origin  = 'origin',
                            cost_dest = 'dest',      cost_name = 'cost')


    def test_weighted_catchment_small_catchment_weight_1(self):
        catchment = .5
        weight = 1
        result = self.model.weighted_catchment(name = 'test',
                                               weight_fn = weights.step_fn({catchment:weight}))
        actual = result.iloc[0]['test_value']
        self.assertEqual(actual, 1)


    def test_weighted_catchment_small_catchment_weight_x(self):
        catchment = .5
        weight = .5
        result = self.model.weighted_catchment(name = 'test',
                                               weight_fn = weights.step_fn({catchment:weight}))
        actual = result.iloc[0]['test_value']
        self.assertEqual(actual, .5)


    def test_weighted_catchment_large_catchment_weight_1(self):
        catchment = 10
        weight = 1
        result = self.model.weighted_catchment(name = 'test',
                                               weight_fn = weights.step_fn({catchment:weight}))
        actual = result.iloc[0]['test_value']
        self.assertEqual(actual, 25)


if __name__ == '__main__':
    unittest.main()
