import sys
sys.path.append('../..')

import math
import unittest

import numpy as np
import pandas as pd
import geopandas as gpd
from access import access, weights
from access.util import testing as tu


class TestFloatingCatchmentAreaRatio(unittest.TestCase):

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
                            cost_dest = 'dest',      cost_name = 'cost',
                            neighbor_cost_df   = cost_matrix, neighbor_cost_origin  = 'origin',
                            neighbor_cost_dest = 'dest',      neighbor_cost_name = 'cost')


    def test_floating_catchment_area_ratio_large_catchment(self):
        result = self.model.fca_ratio()
        expected = self.model.access_df.iloc[0]['fca_value']

        total_demand = self.model.access_df['value'].sum()
        total_supply = self.model.supply_df['value'].sum()
        actual = total_supply/total_demand

        self.assertEqual(expected, actual)


    def test_floating_catchment_area_ratio_small_catchment(self):
        small_catchment = .9
        result = self.model.fca_ratio(max_cost = small_catchment)
        expected = self.model.access_df.iloc[0]['fca_value']

        self.assertEqual(expected, 1)


    def test_floating_catchment_area_ratio_zero_catchment(self):
        zero_catchment = 0
        result = self.model.fca_ratio(max_cost = zero_catchment)
        expected = math.isnan(self.model.access_df.iloc[0]['fca_value'])

        self.assertEqual(expected, True)
