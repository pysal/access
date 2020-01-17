import os
import sys
sys.path.append('../..')

import math
import unittest

import numpy as np
import pandas as pd
import geopandas as gpd
from access.datasets import datasets
from access.util import testing as tu


class TestDatasets(unittest.TestCase):

    def test_file_download(self):
        file_name = 'chi_times'
        file_path = os.path.join(datasets._dir_path, datasets._datasets[file_name])
        if os.path.exists(file_path):
            os.remove(file_path)

        datasets.load_data(file_name)

        actual = os.path.exists(file_path)

        self.assertEqual(actual, True)


    def test_load_geopandas_dataset(self):
        result = datasets.load_data('chi_doc_geom')
        actual = type(result) == gpd.geodataframe.GeoDataFrame

        self.assertEqual(actual, True)


    def test_prints_available_datasets(self):
        datasets.available_datasets()
