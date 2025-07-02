import math
import unittest

import pandas as pd
import util as tu

from access import Access
from access.access import weights


class TestFloatingCatchmentArea(unittest.TestCase):
    def setUp(self):
        n = 5
        supply_grid = tu.create_nxn_grid(n)
        demand_grid = supply_grid.sample(5)
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
            neighbor_cost_df=cost_matrix,
            neighbor_cost_origin="origin",
            neighbor_cost_dest="dest",
            neighbor_cost_name="cost",
        )

    def test_floating_catchment_area_ratio_large_catchment(self):
        self.model.fca_ratio()
        actual = self.model.access_df.iloc[0]["fca_value"]

        total_demand = self.model.access_df["value"].sum()
        total_supply = self.model.supply_df["value"].sum()
        expected = total_supply / total_demand

        self.assertEqual(actual, expected)

    def test_floating_catchment_area_ratio_small_catchment(self):
        small_catchment = 0.9
        self.model.fca_ratio(max_cost=small_catchment)
        actual = (self.model.access_df["fca_value"] == 1).all()

        self.assertTrue(actual)

    def test_floating_catchment_area_ratio_large_catchment_normalized(self):
        self.model.fca_ratio(normalize=True)
        actual = self.model.access_df.iloc[0]["fca_value"]

        self.assertEqual(actual, 5)

    def test_floating_catchment_area_ratio_warns_if_demand_supply_locs_differ_and_noise(
        self,
    ):
        new_dem_row = pd.DataFrame(
            [[1, 1, 1, None], [1, 1, 1, None]],
            columns=["x", "y", "value", "geometry"],
            index=[28, 29],
        )
        self.model.demand_df = pd.concat([self.model.demand_df, new_dem_row])
        self.model.demand_df.index.name = "id"
        self.model.fca_ratio(noise=True)

    def test_floating_catchment_area_ratio_overwrites_column(self):
        small_catchment = 0.9
        self.model.fca_ratio(max_cost=small_catchment)

        small_catchment = 0.8
        self.model.fca_ratio(max_cost=small_catchment)

        actual = self.model.access_df.iloc[0]["fca_value"]

        self.assertEqual(actual, 1)

    def test_floating_catchment_area_ratio_zero_catchment(self):
        zero_catchment = 0
        self.model.fca_ratio(max_cost=zero_catchment)
        actual = math.isnan(self.model.access_df.iloc[0]["fca_value"])

        self.assertEqual(actual, True)

    def test_two_stage_floating_catchment_area_large_catchment(self):
        self.model.two_stage_fca()
        actual = self.model.access_df.iloc[0]["2sfca_value"]

        self.assertEqual(actual, 5)

    def test_two_stage_floating_catchment_area_small_catchment(self):
        small_catchment = 0.9
        self.model.two_stage_fca(max_cost=small_catchment)
        actual = self.model.access_df.iloc[0]["2sfca_value"]

        self.assertEqual(actual, 1)

    def test_two_stage_floating_catchment_area_zero_catchment(self):
        zero_catchment = 0
        self.model.two_stage_fca(max_cost=zero_catchment)
        actual = math.isnan(self.model.access_df.iloc[0]["2sfca_value"])

        self.assertEqual(actual, True)

    def test_two_stage_floating_catchment_area_warning_default_cost_if_more_than_one(
        self,
    ):
        cost_list = ["cost", "other_cost"]
        self.model.cost_names = cost_list
        self.model.two_stage_fca()
        actual = self.model.default_cost

        self.assertEqual(actual, "cost")

    def test_two_stage_floating_catchment_area_unavailable_cost_name_raises_value_error(
        self,
    ):
        with self.assertRaises(ValueError):
            bad_cost_name = "euclidean"
            self.model.two_stage_fca(cost=bad_cost_name)

    def test_two_stage_floating_catchment_area_large_catchment_supply_value_explicit(
        self,
    ):
        self.model.two_stage_fca(supply_values="value")
        actual = self.model.access_df.iloc[0]["2sfca_value"]

        self.assertEqual(actual, 5)

    def test_two_stage_floating_catchment_area_run_again_and_test_overwrite(self):
        self.model.two_stage_fca()
        actual = self.model.access_df.iloc[0]["2sfca_value"]

        self.assertEqual(actual, 5)

    def test_two_stage_floating_catchment_area_large_catchment_normalize(self):
        self.model.two_stage_fca(normalize=True)
        actual = self.model.access_df.iloc[0]["2sfca_value"]

        self.assertEqual(actual, 5)

    def test_three_stage_floating_catchment_area_large_catchment(self):
        wfn = weights.step_fn({10: 25})
        self.model.three_stage_fca(weight_fn=wfn)
        actual = self.model.access_df.iloc[0]["3sfca_value"]

        self.assertEqual(actual, 5)

    def test_three_stage_floating_catchment_area_large_catchment_run_again_and_test_overwrite(  # noqa: E501
        self,
    ):
        wfn = weights.step_fn({10: 25})
        self.model.three_stage_fca(weight_fn=wfn)
        actual = self.model.access_df.iloc[0]["3sfca_value"]

        self.assertEqual(actual, 5)

    def test_three_stage_floating_catchment_area_large_catchment_normalize(self):
        wfn = weights.step_fn({10: 25})
        self.model.three_stage_fca(weight_fn=wfn, normalize=True)
        actual = self.model.access_df.iloc[0]["3sfca_value"]

        self.assertEqual(actual, 5)

    def test_three_stage_floating_catchment_area_small_catchment(self):
        small_catchment = 0.9
        wfn = weights.step_fn({10: 25})
        self.model.three_stage_fca(max_cost=small_catchment, weight_fn=wfn)
        actual = self.model.access_df.iloc[0]["3sfca_value"]

        self.assertEqual(actual, 1)

    def test_three_stage_floating_catchment_area_zero_catchment(self):
        zero_catchment = 0
        self.model.three_stage_fca(max_cost=zero_catchment)
        actual = math.isnan(self.model.access_df.iloc[0]["3sfca_value"])

        self.assertEqual(actual, True)

    def test_enhanced_two_stage_floating_catchment_area_large_catchment(self):
        self.model.enhanced_two_stage_fca()
        actual = self.model.access_df.iloc[0]["e2sfca_value"]

        self.assertEqual(actual, 5)

    def test_enhanced_two_stage_floating_catchment_area_small_catchment(self):
        small_catchment = 0.9
        self.model.enhanced_two_stage_fca(max_cost=small_catchment)
        actual = self.model.access_df.iloc[0]["e2sfca_value"]

        self.assertEqual(actual, 1)

    def test_enhanced_two_stage_floating_catchment_area_zero_catchment(self):
        zero_catchment = 0
        self.model.enhanced_two_stage_fca(max_cost=zero_catchment)
        actual = math.isnan(self.model.access_df.iloc[0]["e2sfca_value"])

        self.assertEqual(actual, True)
