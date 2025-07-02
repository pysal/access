import unittest

import geopandas as gpd
import pandas as pd

from access import Datasets


class TestDatasets(unittest.TestCase):
    def test_load_geopandas_dataset(self):
        result = Datasets.load_data("chi_doc_geom")
        assert isinstance(result, gpd.GeoDataFrame)

    def test_load_pandas_dataset(self):
        result = Datasets.load_data("chi_times")
        assert isinstance(result, pd.DataFrame)

    def test_prints_available_datasets(self):
        Datasets.available_datasets()
