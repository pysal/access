import sys
sys.path.append('../..')

import math
import unittest


import numpy as np
import pandas as pd
import geopandas as gpd
from access import access, weights
import matplotlib.pyplot as plt


def create_nxn_grid(n):
    '''
    Helper function to create an n x n matrix in a GeoDataFrame.

    Parameters
    ----------
    n: integer determining the size of the resulting grid

    Returns
    -------
    grid: nxn size grid in a GeoDataFrame with columns 'id', 'x', 'y', 'value'
    '''
    rows = []
    id = 0
    for x in range(n):
        for y in range(n):
            id += 1
            rows.append({'id'    :id,
                          'x'    :x,
                          'y'    :y,
                          'value':1})

    data = pd.DataFrame(rows, columns=['id','x','y','value'])
    grid = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.x,data.y))

    return grid


def create_cost_matrix(grid, dist_func):
    '''
    Helper function to create a play cost matrix for an nxn grid.

    Parameters
    ----------
    grid: an nxn grid in a DataFrame or GeoDataFrame
    dist_func: distance function, either euclidean or manhattan

    Returns
    -------
    cost_matrix: a cost_matrix of size n**4 with distance between each point
                 to every other point in the play grid. Has columns 'origin',
                 'dest', and 'cost'
    '''
    rows = []
    for x in grid.iterrows():
        x = x[1]
        for y in grid.iterrows():
            y = y[1]
            dist = dist_func(x, y)
            rows.append([x.id, y.id, dist])

    cost_matrix = pd.DataFrame(rows, columns = ['origin', 'dest', 'cost'])

    return cost_matrix

manhattan = lambda i, j: abs(i.x - j.x) + abs(i.y - j.y)
euclidean = lambda i, j: math.sqrt((i.x - j.x)**2 + (i.y - j.y)**2)


class TestWeightedCatchment(unittest.TestCase):

    def setUp(self):
        supply_grid = create_nxn_grid(5)
        demand_grid = supply_grid.sample(1)
        cost_matrix = create_cost_matrix(supply_grid, euclidean)

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
