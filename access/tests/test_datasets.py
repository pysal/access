import os
import sys
sys.path.append('../..')

import math
import unittest

import numpy as np
import pandas as pd
import geopandas as gpd
from access.datasets import Datasets
import util as tu


class TestDatasets(unittest.TestCase):

    def test_file_download(self):
        file_name = 'chi_times'
        file_path = os.path.join(Datasets._dir_path, Datasets._datasets[file_name])
        if os.path.exists(file_path):
            os.remove(file_path)

        Datasets.load_data(file_name)

        actual = os.path.exists(file_path)

        self.assertEqual(actual, True)


    def test_load_geopandas_dataset(self):
        result = Datasets.load_data('chi_doc_geom')
        actual = type(result) == gpd.geodataframe.GeoDataFrame

        self.assertEqual(actual, True)


    def test_prints_available_datasets(self):
        Datasets.available_datasets()
