import math
import random

import numpy as np
import pandas as pd
import geopandas as gpd
from access.util import testing as tu

def create_nxn_grid(n, buffer = 0, random_values=False, seed=44):
    '''
    Helper function to create an n x n matrix in a GeoDataFrame.

    Parameters
    ----------
    n: integer determining the size of the resulting grid
    buffer: create points with a buffer of radius size given

    Returns
    -------
    grid: nxn size grid in a GeoDataFrame with columns 'id', 'x', 'y', 'value'
    '''
    rows = []
    id = 0
    value = 1

    random.seed(seed)

    for x in range(n):
        for y in range(n):
            if random_values:
                value = random.randint(1,200)
            id += 1
            rows.append({'id'    :id,
                          'x'    :x,
                          'y'    :y,
                          'value':value})

    data = pd.DataFrame(rows, columns=['id','x','y','value'])
    grid = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.x,data.y))

    if buffer:
        grid = grid.buffer(buffer)

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

    funcs = {'manhattan': lambda i, j: abs(i.x - j.x) + abs(i.y - j.y),
            'euclidean': lambda i, j: math.sqrt((i.x - j.x)**2 + (i.y - j.y)**2)}
    dist_func = funcs[dist_func]

    for x in grid.iterrows():
        x = x[1]
        for y in grid.iterrows():
            y = y[1]
            dist = dist_func(x, y)
            rows.append([x.id, y.id, dist])

    cost_matrix = pd.DataFrame(rows, columns = ['origin', 'dest', 'cost'])

    return cost_matrix
