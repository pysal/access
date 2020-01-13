import sys
sys.path.append('../..')

import math
import unittest

import numpy as np
import pandas as pd
import geopandas as gpd
from access import access, weights
from access.util import testing as tu


class TestEuclidean(unittest.TestCase):

    def setUp(self):
        demand_data = pd.DataFrame({'id':[0], 'x':[0], 'y':[0], 'value':[1]})
        demand_grid = gpd.GeoDataFrame(demand_data, geometry = gpd.points_from_xy(demand_data.x,
                                                                                  demand_data.y))
        demand_grid['geometry'] = demand_grid.buffer(.5)

        supply_data = pd.DataFrame({'id':[1], 'x':[0], 'y':[1], 'value':[1]})
        supply_grid = gpd.GeoDataFrame(supply_data, geometry = gpd.points_from_xy(supply_data.x,
                                                                                  supply_data.y))
        supply_grid['geometry'] = supply_grid.buffer(.5)

        cost_matrix = pd.DataFrame({'origin': [0],
                                    'dest'  : [1],
                                    'cost'  : [1]})

        self.model = access(demand_df = demand_grid, demand_index = 'id',
                                                     demand_value = 'value',
                            supply_df = supply_grid, supply_index = 'id',
                                                     supply_value = 'value',
                            cost_df   = cost_matrix, cost_origin  = 'origin',
                                                     cost_dest = 'dest',
                                                     cost_name    = 'cost',
                            neighbor_cost_df   = cost_matrix, neighbor_cost_origin  = 'origin',
                            neighbor_cost_dest = 'dest',      neighbor_cost_name    = 'cost')


    def test_euclidean_point_to_point(self):
        self.model.euclidean_distance(name = 'euclidian', threshold = 2,
                                      centroid_o = True, centroid_d = True)
        actual = self.model.cost_df['euclidian'][0]

        self.assertAlmostEqual(actual, 1)


    def test_euclidean_point_to_poly(self):
        self.model.euclidean_distance(name = 'euclidian', threshold = 2,
                                      centroid_o = True, centroid_d = False)
        actual = self.model.cost_df['euclidian'][0]

        self.assertAlmostEqual(actual, .5)


    def test_euclidean_poly_to_poly(self):
        self.model.euclidean_distance(name = 'euclidian', threshold = 2,
                                      centroid_o = False, centroid_d = False)
        actual = self.model.cost_df['euclidian'][0]

        self.assertAlmostEqual(actual, 0)


    def test_euclidean_without_geopandas_demand_dataframe_raises_TypeError(self):
        with self.assertRaises(TypeError):
            self.model.demand_df = self.model.demand_df[['x','y','value']]
            self.model.euclidean_distance()


    def test_euclidean_without_geopandas_supply_dataframe_raises_TypeError(self):
        with self.assertRaises(TypeError):
            self.model.supply_df = self.model.supply_df[['x','y','value']]
            self.model.euclidean_distance()


    def test_euclidean_geopandas_not_installed_raises_ModuleNotFoundError(self):
        self.model.HAS_GEOPANDAS = False
        with self.assertRaises(SystemError):
            self.model.euclidean_distance()


    def test_euclidean_sets_euclidean_as_default_if_no_default_exists(self):
        delattr(self.model, 'default_cost')
        self.model.euclidean_distance()

        actual = hasattr(self.model, 'default_cost')

        self.assertEquals(actual, True)


class TestEuclideanNeighbors(unittest.TestCase):

    def setUp(self):
        demand_data = pd.DataFrame({'id'   :[0, 1],
                                    'x'    :[0, 0],
                                    'y'    :[0, 1],
                                    'value':[1, 1]})
        demand_grid = gpd.GeoDataFrame(demand_data, geometry = gpd.points_from_xy(demand_data.x,
                                                                                  demand_data.y))
        demand_grid['geometry'] = demand_grid.buffer(.5)

        supply_data = pd.DataFrame({'id':[1], 'x':[0], 'y':[1], 'value':[1]})
        supply_grid = gpd.GeoDataFrame(supply_data, geometry = gpd.points_from_xy(supply_data.x,
                                                                                  supply_data.y))

        cost_matrix = pd.DataFrame({'origin': [0, 0, 1, 1],
                                    'dest'  : [1, 0, 0, 1],
                                    'cost'  : [1, 0, 1, 0]})

        self.model = access(demand_df = demand_grid, demand_index = 'id',
                                                     demand_value = 'value',
                            supply_df = supply_grid, supply_index = 'id',
                                                     supply_value = 'value',
                            cost_df   = cost_matrix, cost_origin  = 'origin',
                                                     cost_dest = 'dest',
                                                     cost_name    = 'cost',
                            neighbor_cost_df   = cost_matrix, neighbor_cost_origin  = 'origin',
                            neighbor_cost_dest = 'dest',      neighbor_cost_name    = 'cost')


    def test_euclidean_neighbors_centroids(self):
        self.model.euclidean_distance_neighbors(name = 'euclidian', threshold=2,
                                                centroid = True)
        actual1 = self.model.neighbor_cost_df['euclidian'][0]
        actual2 = self.model.neighbor_cost_df['euclidian'][2]
        self.assertAlmostEqual(actual1, 1)
        self.assertAlmostEqual(actual2, 1)


    def test_euclidean_neighbors_poly(self):
        self.model.euclidean_distance_neighbors(name = 'euclidian', threshold=2,
                                                centroid = False)
        actual1 = self.model.neighbor_cost_df['euclidian'][0]
        actual2 = self.model.neighbor_cost_df['euclidian'][2]
        self.assertAlmostEqual(actual1, 0)
        self.assertAlmostEqual(actual2, 0)


    def test_euclidean_neighbors_without_geopandas_demand_dataframe_raises_TypeError(self):
        with self.assertRaises(TypeError):
            self.model.demand_df = self.model.demand_df[['x','y','value']]
            self.model.euclidean_distance_neighbors()


    def test_euclidean_neighbors_sets_euclidean_as_default_if_no_default_exists(self):
        delattr(self.model, 'neighbor_default_cost')
        self.model.euclidean_distance_neighbors()

        actual = hasattr(self.model, 'neighbor_default_cost')

        self.assertEquals(actual, True)
