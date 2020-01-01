import sys
sys.path.append('../..')

import math
import unittest

import numpy as np
import pandas as pd
import geopandas as gpd
from access import access, weights
from access.util import testing as tu


class TestFloatingCatchmentArea(unittest.TestCase):

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
        actual = self.model.access_df.iloc[0]['fca_value']

        total_demand = self.model.access_df['value'].sum()
        total_supply = self.model.supply_df['value'].sum()
        expected = total_supply/total_demand

        self.assertEqual(expected, actual)


    def test_floating_catchment_area_ratio_small_catchment(self):
        small_catchment = .9
        result = self.model.fca_ratio(max_cost = small_catchment)
        actual = self.model.access_df.iloc[0]['fca_value']

        self.assertEqual(actual, 1)


    def test_floating_catchment_area_ratio_zero_catchment(self):
        zero_catchment = 0
        result = self.model.fca_ratio(max_cost = zero_catchment)
        actual = math.isnan(self.model.access_df.iloc[0]['fca_value'])

        self.assertEqual(actual, True)


    def test_two_stage_floating_catchment_area_large_catchment(self):
        result = self.model.two_stage_fca()
        actual = self.model.access_df.iloc[0]['2sfca_value']

        self.assertEqual(actual, 25)


    def test_two_stage_floating_catchment_area_small_catchment(self):
        small_catchment = .9
        result = self.model.two_stage_fca(max_cost = small_catchment)
        actual = self.model.access_df.iloc[0]['2sfca_value']

        self.assertEqual(actual, 1)


    def test_two_stage_floating_catchment_area_zero_catchment(self):
        zero_catchment = 0
        result = self.model.two_stage_fca(max_cost = zero_catchment)
        actual = math.isnan(self.model.access_df.iloc[0]['2sfca_value'])

        self.assertEqual(actual, True)


    def test_three_stage_floating_catchment_area_large_catchment(self):
        wfn = weights.step_fn({10:25})
        result = self.model.three_stage_fca(weight_fn = wfn)
        actual = self.model.access_df.iloc[0]['3sfca_value']

        self.assertEqual(actual, 25)


    def test_three_stage_floating_catchment_area_small_catchment(self):
        small_catchment = .9
        wfn = weights.step_fn({10:25})
        result = self.model.three_stage_fca(max_cost = small_catchment,
                                            weight_fn = wfn)
        actual = self.model.access_df.iloc[0]['3sfca_value']

        self.assertEqual(actual, 1)


    def test_three_stage_floating_catchment_area_zero_catchment(self):
        zero_catchment = 0
        result = self.model.three_stage_fca(max_cost = zero_catchment)
        actual = math.isnan(self.model.access_df.iloc[0]['3sfca_value'])

        self.assertEqual(actual, True)


    def test_enhanced_two_stage_floating_catchment_area_large_catchment(self):
        result = self.model.enhanced_two_stage_fca()
        actual = self.model.access_df.iloc[0]['e2sfca_value']

        self.assertEqual(actual, 25)


    def test_enhanced_two_stage_floating_catchment_area_small_catchment(self):
        small_catchment = .9
        result = self.model.enhanced_two_stage_fca(max_cost = small_catchment)
        actual = self.model.access_df.iloc[0]['e2sfca_value']

        self.assertEqual(actual, 1)


    def test_enhanced_two_stage_floating_catchment_area_zero_catchment(self):
        zero_catchment = 0
        result = self.model.enhanced_two_stage_fca(max_cost = zero_catchment)
        actual = math.isnan(self.model.access_df.iloc[0]['e2sfca_value'])

        self.assertEqual(actual, True)
