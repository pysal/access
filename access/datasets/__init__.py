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

    dwnld_data = {'chi_times' : 'https://drive.google.com/uc?authuser=0&id=1IcfJimPj4C5ZN5Xc-nvq_DModcCO6GY3&export=download',
                  'chi_euclidean' : 'https://drive.google.com/uc?authuser=0&id=1qq5ZWOaq5uxJOu9QzsNCw5WhdATgIhzK&export=download',
                  'chi_euclidean_neighbors' : 'https://drive.google.com/uc?authuser=0&id=1GQFBbWEtltT5MhbtC3iJXXfPCoXUPfTJ&export=download'}

    datasets = {'chi_times': 'chicago_metro_times.csv.bz2',
                'chi_doc': 'chicago_metro_docs_dentists.csv',
                'chi_pop': 'chicago_metro_pop.csv',
                'chi_doc_geom': 'chicago_metro_docs_dentists.geojson',
                'chi_pop_geom': 'chicago_metro_pop.geojson',
                'chi_euclidean': 'chicago_metro_euclidean_costs.csv.bz2',
                'chi_euclidean_neighbors': 'chicago_metro_euclidean_cost_neighbors.csv.bz2'}

    path = os.path.join(dir_path, datasets[key])

    if key in dwnld_data.keys() and not os.path.exists(path):
        print(f'Downloading {key}...')
        req = requests.get(dwnld_data[key])
        file_path = os.path.join(dir_path, datasets[key])

        with open(file_path, 'wb') as f:
            f.write(req.content)
        print('Download complete.')

    if '.geojson' in path:
        return gpd.read_file(path)

    return pd.read_csv(path)
