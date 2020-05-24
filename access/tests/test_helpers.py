import sys
sys.path.append('../..')

import math
import unittest

import numpy as np
import pandas as pd
import geopandas as gpd
from access import access, weights, helpers
import util as tu


class TestHelpers(unittest.TestCase):

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


    def test_sanitize_supply_cost_set_cost_as_default(self):
        self.model.cost_names.append('other_cost')
        helpers.sanitize_supply_cost(self.model, None, 'value')
        actual = self.model.default_cost

        self.assertEqual(actual, 'cost')


    def test_sanitize_supply_cost_raise_ValueError_if_cost_not_found(self):
        with self.assertRaises(ValueError):
            helpers.sanitize_supply_cost(self.model, 'some_cost', 'value')


    def test_sanitize_demand_cost_set_cost_as_default(self):
        self.model.cost_names.append('other_cost')
        helpers.sanitize_demand_cost(self.model, None, 'value')
        actual = self.model.default_cost

        self.assertEqual(actual, 'cost')


    def test_sanitize_demand_cost_raise_ValueError_if_cost_not_found(self):
        with self.assertRaises(ValueError):
            helpers.sanitize_demand_cost(self.model, 'some_cost', 'value')


    def test_sanitize_supplies_provide_value_as_string(self):
        actual = helpers.sanitize_supplies(self.model, 'some_value')

        self.assertEqual(actual, ['some_value'])


    def test_sanitize_supplies_raise_ValueError_if_input_other_than_str_or_list(self):
        with self.assertRaises(ValueError):
            sesult = helpers.sanitize_supplies(self.model, 5)
