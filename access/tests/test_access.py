import sys

sys.path.append("../..")

import math
import unittest

import numpy as np
import pandas as pd
import geopandas as gpd
from access import Access, weights
import util as tu


class TestAccess(unittest.TestCase):
    def setUp(self):
        n = 5
        self.supply_grid = tu.create_nxn_grid(n)
        self.demand_grid = self.supply_grid.sample(1)
        self.cost_matrix = tu.create_cost_matrix(self.supply_grid, "euclidean")

    def test_access_initialize_without_demand_index_col_raises_value_error(self):
        with self.assertRaises(ValueError):
            bad_index_name = "Not a col in demand df"

            Access(
                demand_df=self.demand_grid,
                demand_index=bad_index_name,
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
            )

    def test_access_initialize_without_supply_index_col_raises_value_error(self):
        with self.assertRaises(ValueError):
            bad_index_name = "Not a col in supply df"

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index=bad_index_name,
                supply_value="value",
            )

    def test_access_initialize_without_demand_value_col_raises_value_error(self):
        with self.assertRaises(ValueError):
            bad_value_name = "Not a col in demand df"

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value=bad_value_name,
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
            )

    def test_access_initialize_without_supply_value_col_raises_value_error(self):
        with self.assertRaises(ValueError):
            bad_value_name = "Not a col in supply df"

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value=bad_value_name,
            )

    def test_access_initialize_without_supply_value_col_in_list_raises_value_error(
        self,
    ):
        with self.assertRaises(ValueError):
            bad_value_name = ["Not a col in supply df"]

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value=bad_value_name,
            )

    def test_access_initialize_with_supply_value_col_in_list(self):
        value_in_list = ["value"]

        self.model = Access(
            demand_df=self.demand_grid,
            demand_index="id",
            demand_value="value",
            supply_df=self.supply_grid,
            supply_index="id",
            supply_value=value_in_list,
        )

        actual = self.model.supply_types

        self.assertEqual(actual, ["value"])

    def test_access_initialize_with_supply_value_col_in_dict_raises_value_error(self):
        with self.assertRaises(ValueError):
            value_in_dict = {"value": ""}

            self.model = Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value=value_in_dict,
            )

    def test_access_initialize_without_valid_cost_origin_raises_value_error(self):
        with self.assertRaises(ValueError):
            bad_cost_origin = "Not a valid cost origin column"

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
                cost_df=self.cost_matrix,
                cost_origin=bad_cost_origin,
                cost_dest="dest",
                cost_name="cost",
            )

    def test_access_initialize_without_valid_cost_dest_raises_value_error(self):
        with self.assertRaises(ValueError):
            bad_cost_dest = "Not a valid cost dest column"

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
                cost_df=self.cost_matrix,
                cost_origin="origin",
                cost_dest=bad_cost_dest,
                cost_name="cost",
            )

    def test_access_initialize_without_valid_cost_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            bad_cost_name = "Not a valid cost name column"

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
                cost_df=self.cost_matrix,
                cost_origin="origin",
                cost_dest="dest",
                cost_name=bad_cost_name,
            )

    def test_access_initialize_without_valid_cost_name_in_list_raises_value_error(self):
        with self.assertRaises(ValueError):
            bad_cost_name = ["Not a valid cost name column"]

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
                cost_df=self.cost_matrix,
                cost_origin="origin",
                cost_dest="dest",
                cost_name=bad_cost_name,
            )

    def test_access_initialize_with_valid_cost_name_in_list(self):
        cost_name_list = ["cost"]

        self.model = Access(
            demand_df=self.demand_grid,
            demand_index="id",
            demand_value="value",
            supply_df=self.supply_grid,
            supply_index="id",
            supply_value="value",
            cost_df=self.cost_matrix,
            cost_origin="origin",
            cost_dest="dest",
            cost_name=cost_name_list,
        )

        actual = self.model.cost_names

        self.assertEqual(actual, ["cost"])

    def test_access_initialize_with_valid_cost_name_in_dict_raises_value_error(self):
        with self.assertRaises(ValueError):
            cost_name_dict = {"cost": ""}

            self.model = Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
                cost_df=self.cost_matrix,
                cost_origin="origin",
                cost_dest="dest",
                cost_name=cost_name_dict,
            )

    def test_access_initialize_without_valid_neighbor_cost_origin_raises_value_error(
        self,
    ):
        with self.assertRaises(ValueError):
            bad_cost_origin = "Not a valid cost origin column"

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
                neighbor_cost_df=self.cost_matrix,
                neighbor_cost_origin=bad_cost_origin,
                neighbor_cost_dest="dest",
                neighbor_cost_name="cost",
            )

    def test_access_initialize_without_valid_neighbor_cost_dest_raises_value_error(
        self,
    ):
        with self.assertRaises(ValueError):
            bad_cost_dest = "Not a valid cost dest column"

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
                neighbor_cost_df=self.cost_matrix,
                neighbor_cost_origin="origin",
                neighbor_cost_dest=bad_cost_dest,
                neighbor_cost_name="cost",
            )

    def test_access_initialize_without_valid_neighbor_cost_name_raises_value_error(
        self,
    ):
        with self.assertRaises(ValueError):
            bad_cost_name = "Not a valid cost name column"

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
                neighbor_cost_df=self.cost_matrix,
                neighbor_cost_origin="origin",
                neighbor_cost_dest="dest",
                neighbor_cost_name=bad_cost_name,
            )

    def test_access_initialize_without_valid_neighbor_cost_name_in_list_raises_value_error(
        self,
    ):
        with self.assertRaises(ValueError):
            bad_cost_name = ["Not a valid cost name column"]

            Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
                neighbor_cost_df=self.cost_matrix,
                neighbor_cost_origin="origin",
                neighbor_cost_dest="dest",
                neighbor_cost_name=bad_cost_name,
            )

    def test_access_initialize_with_valid_neighbor_cost_name_in_list(self):
        cost_name_list = ["cost"]

        self.model = Access(
            demand_df=self.demand_grid,
            demand_index="id",
            demand_value="value",
            supply_df=self.supply_grid,
            supply_index="id",
            supply_value="value",
            neighbor_cost_df=self.cost_matrix,
            neighbor_cost_origin="origin",
            neighbor_cost_dest="dest",
            neighbor_cost_name=cost_name_list,
        )

        actual = self.model.neighbor_cost_names

        self.assertEqual(actual, ["cost"])

    def test_access_initialize_with_valid_neighbor_cost_name_in_dict_raises_value_error(
        self,
    ):
        with self.assertRaises(ValueError):
            cost_name_dict = {"cost": ""}

            self.model = Access(
                demand_df=self.demand_grid,
                demand_index="id",
                demand_value="value",
                supply_df=self.supply_grid,
                supply_index="id",
                supply_value="value",
                neighbor_cost_df=self.cost_matrix,
                neighbor_cost_origin="origin",
                neighbor_cost_dest="dest",
                neighbor_cost_name=cost_name_dict,
            )
