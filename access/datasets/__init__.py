import os
import requests

import pandas as pd
import geopandas as gpd

__all__ = ['get_path']

def load_data(key):
    """
    Return path for available datasets.
    """
    dir_path = os.path.join(os.path.dirname(__file__), 'chi_med')

    datasets = {'chi_times': 'chicago_metro_times.csv',
                'chi_doc': 'chicago_metro_docs_dentists.csv',
                'chi_pop': 'chicago_metro_pop.csv',
                'chi_doc_geom': 'chicago_metro_docs_dentists.geojson',
                'chi_pop_geom': 'chicago_metro_pop.geojson',
                'chi_euclidean': 'chicago_metro_euclidean_costs.csv',
                'chi_euclidean_neighbors': 'chicago_metro_euclidean_cost_neighbors.csv'}

    path = os.path.join(dir_path, datasets[key])

    if key == 'chi_times' and not os.path.exists(path):
        pass
        # TO-DO: download file if doesn't exist
    if '.geojson' in path:
        return gpd.read_file(path)

    return pd.read_csv(path)
