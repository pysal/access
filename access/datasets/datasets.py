import os
import requests

import pandas as pd


class datasets(object):

    _dir_path = os.path.join(os.path.dirname(__file__), 'chi_med')

    _dwnld_data = {'chi_times' : 'https://drive.google.com/uc?authuser=0&id=1IcfJimPj4C5ZN5Xc-nvq_DModcCO6GY3&export=download',
                  'chi_euclidean' : 'https://drive.google.com/uc?authuser=0&id=1qq5ZWOaq5uxJOu9QzsNCw5WhdATgIhzK&export=download',
                  'chi_euclidean_neighbors' : 'https://drive.google.com/uc?authuser=0&id=1GQFBbWEtltT5MhbtC3iJXXfPCoXUPfTJ&export=download'}

    _datasets = {'chi_times': 'chicago_metro_times.csv.bz2',
                'chi_doc': 'chicago_metro_docs_dentists.csv',
                'chi_pop': 'chicago_metro_pop.csv',
                'chi_doc_geom': 'chicago_metro_docs_dentists.geojson',
                'chi_pop_geom': 'chicago_metro_pop.geojson',
                'chi_euclidean': 'chicago_metro_euclidean_costs.csv.bz2',
                'chi_euclidean_neighbors': 'chicago_metro_euclidean_cost_neighbors.csv.bz2',
                'cook_county_hospitals': 'hospitals_cookcty.geojson'}


    @staticmethod
    def load_data(key):
        """
        Return path for available datasets.
        """
        assert key in datasets._datasets.keys(), 'Not an available dataset. Use datasets.available_datasets to see the available datasets.'

        path = os.path.join(datasets._dir_path, datasets._datasets[key])

        if key in datasets._dwnld_data.keys() and not os.path.exists(path):
            print('Downloading {key}...'.format(key = key))
            req = requests.get(datasets._dwnld_data[key])
            file_path = os.path.join(datasets._dir_path, datasets._datasets[key])

            with open(file_path, 'wb') as f:
                f.write(req.content)
            print('Download complete.')

        if '.geojson' in path:
            try:
                import geopandas as gpd
            except:
                raise SystemError("Please install geopandas.")

            return gpd.read_file(path)


        return pd.read_csv(path)


    @staticmethod
    def available_datasets():
        print(datasets._datasets)
