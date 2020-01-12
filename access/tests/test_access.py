import sys
sys.path.append('../..')

import math
import unittest

import numpy as np
import pandas as pd
import geopandas as gpd
from access import access, weights
from access.util import testing as tu


class TestAccess(unittest.TestCase):

    def setUp(self):
        n = 5
        supply_grid = tu.create_nxn_grid(n)
        demand_grid = supply_grid.sample(1)
        cost_matrix = tu.create_cost_matrix(supply_grid, 'euclidean')


    def test_access_initialize_without__raises_value_error(self):
        pass


    def test_access_initialize_without__raises_value_error(self):
        pass


    def test_access_initialize_without__raises_value_error(self):
        pass


    def test_access_initialize_without__raises_value_error(self):
        pass


    def test_access_initialize_without__raises_value_error(self):
        pass


    def test_access_initialize_without__raises_value_error(self):
        pass


    def test_access_initialize_without__raises_value_error(self):
        pass
