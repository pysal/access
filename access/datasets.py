import os
import requests

import pandas as pd


class Datasets(object):
    @staticmethod
    def load_data(key):
        """
        Return path for available datasets.
        """

        _datasets = {
            "chi_times": "chicago_metro_times.csv.bz2",
            "chi_doc": "chicago_metro_docs_dentists.csv",
            "chi_pop": "chicago_metro_pop.csv",
            "chi_doc_geom": "chicago_metro_docs_dentists.geojson",
            "chi_pop_geom": "chicago_metro_pop.geojson",
            "chi_euclidean": "chicago_metro_euclidean_costs.csv.bz2",
            "chi_euclidean_neighbors": "chicago_metro_euclidean_cost_neighbors.csv.bz2",
            "cook_county_hospitals": "cook_county_hospitals.csv",
            "cook_county_hospitals_geom": "hospitals_cookcty.geojson",
            "cook_county_tracts": "cook_county_tracts.geojson",
        }

        url = f"https://d2r7gabxtstf5s.cloudfront.net/ex_datasets/{_datasets[key]}"

        if ".geojson" in url:
            import geopandas as gpd

            return gpd.read_file(url)

        return pd.read_csv(url)

    @staticmethod
    def available_datasets():
        desc = """
chi_times: Cost matrix with travel times from each Chicago Census Tract to all others.\n
chi_doc: Doctor and dentist counts for each Chicago Census Tract.\n
chi_pop: Population counts for each Chicago Census Tract.\n
chi_doc_geom: Doctor and dentist counts for each Chicago Census Tract along with geometric representations for Census Tracts.\n
chi_pop_geom: Population counts for each Chicago Census Tract along with geometric representations for Census Tracts.\n
chi_euclidean: Euclidean distance cost matrix with distances from each demand Chicago Census Tract to all others.\n
chi_euclidean_neighbors: Euclidean distance cost matrix with distances from each supply Census Tract to all others.\n
cook_county_hospitals: Contains data for each hospital location in Cook County including X Y coordinates.\n
cook_county_hospitals_geom: Contains data for each hospital location in Cook County including X Y coordinates, and geometric points for each hospital.\n
cook_county_tracts: Geometric representation of each Census Tract in Cook County.
        """
        print(desc)
