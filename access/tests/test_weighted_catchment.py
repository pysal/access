from access import Access
from access.access import weights

import math
import unittest

import numpy as np
import pandas as pd
import geopandas as gpd
import util as tu


class TestWeightedCatchment(unittest.TestCase):
    def setUp(self):
        n = 5
        supply_grid = tu.create_nxn_grid(n)
        demand_grid = supply_grid.sample(1)
        cost_matrix = tu.create_cost_matrix(supply_grid, "euclidean")

        self.model = Access(
            demand_df=demand_grid,
            demand_index="id",
            demand_value="value",
            supply_df=supply_grid,
            supply_index="id",
            supply_value="value",
            cost_df=cost_matrix,
            cost_origin="origin",
            cost_dest="dest",
            cost_name="cost",
        )

    def test_weighted_catchment_small_catchment_weight_1(self):
        catchment = 0.5
        weight = 1
        result = self.model.weighted_catchment(
            name="test", weight_fn=weights.step_fn({catchment: weight})
        )
        actual = result.iloc[0]["test_value"]
        self.assertEqual(actual, 1)

    def test_weighted_catchment_small_catchment_weight_x(self):
        catchment = 0.5
        weight = 0.5
        result = self.model.weighted_catchment(
            name="test", weight_fn=weights.step_fn({catchment: weight})
        )
        actual = result.iloc[0]["test_value"]
        self.assertEqual(actual, 0.5)

    def test_weighted_catchment_large_catchment_weight_1(self):
        catchment = 10
        weight = 1
        result = self.model.weighted_catchment(
            name="test", weight_fn=weights.step_fn({catchment: weight})
        )
        actual = result.iloc[0]["test_value"]
        self.assertEqual(actual, 25)

    def test_weighted_catchment_run_again_and_test_overwrite(self):
        catchment = 0.5
        weight = 1
        result = self.model.weighted_catchment(
            name="test", weight_fn=weights.step_fn({catchment: weight})
        )
        result = self.model.weighted_catchment(
            name="test", weight_fn=weights.step_fn({catchment: weight})
        )
        actual = result.iloc[0]["test_value"]
        self.assertEqual(actual, 1)

    def test_weighted_catchment_large_catchment_weight_1_normalized(self):
        catchment = 10
        weight = 1
        result = self.model.weighted_catchment(
            name="test", weight_fn=weights.step_fn({catchment: weight}), normalize=True
        )
        actual = result.iloc[0]["test_value"]
        self.assertEqual(actual, 1)

    def test_weighted_catchment_with_gravity_weights(self):
        n = 5
        supply_grid = tu.create_nxn_grid(n)
        demand_grid = supply_grid
        cost_matrix = tu.create_cost_matrix(supply_grid, "euclidean")

        self.model = Access(
            demand_df=demand_grid,
            demand_index="id",
            demand_value="value",
            supply_df=supply_grid,
            supply_index="id",
            supply_value="value",
            cost_df=cost_matrix,
            cost_origin="origin",
            cost_dest="dest",
            cost_name="cost",
        )

        gravity = weights.gravity(scale=60, alpha=1)
        self.model.weighted_catchment(name="gravity", weight_fn=gravity)

        ids = [1, 5, 13, 19, 24]
        expected_vals = [
            1.322340210,
            1.322340210,
            0.780985109,
            0.925540119,
            1.133733026,
        ]

        for id, expected in zip(ids, expected_vals):
            actual = self.model.access_df.gravity_value.loc[id]

            self.assertAlmostEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
