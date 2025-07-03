import unittest

import util as tu

from access import Access


class TestRAAM(unittest.TestCase):
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
            neighbor_cost_df=cost_matrix,
            neighbor_cost_origin="origin",
            neighbor_cost_dest="dest",
            neighbor_cost_name="cost",
        )

    def test_raam_single_demand_location_equals_sum_of_supply(self):
        self.model.raam()

        expected = self.model.supply_df.value.sum()
        actual = self.model.access_df["raam_value"].iloc[0]

        self.assertEqual(expected, actual)

    def test_raam_single_demand_location_equals_sum_of_supply_initial_step_int(self):
        self.model.raam(initial_step=1)

        expected = self.model.supply_df.value.sum()
        actual = self.model.access_df["raam_value"].iloc[0]

        self.assertEqual(expected, actual)

    def test_raam_single_demand_location_equals_sum_of_supply_min_step(self):
        self.model.raam(min_step=1, verbose=True)

        expected = self.model.supply_df.value.sum()
        actual = self.model.access_df["raam_value"].iloc[0]

        self.assertEqual(expected, actual)

    def test_raam_run_again_and_test_overwrite(self):
        self.model.raam()
        self.model.raam()

        expected = self.model.supply_df.value.sum()
        actual = self.model.access_df["raam_value"].iloc[0]

        self.assertEqual(expected, actual)

    def test_raam_single_demand_location_equals_sum_of_supply_normalize(self):
        self.model.raam(normalize=True)

        actual = self.model.access_df["raam_value"].iloc[0]

        self.assertEqual(actual, 25)
