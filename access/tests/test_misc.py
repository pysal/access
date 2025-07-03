import pytest
import util as tu

from access import Access


class TestMisc:
    def setup_method(self):
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

    def test_score_half_weight_halves_original_value(self):
        self.model.raam()
        self.model.score(col_dict={"raam_value": 0.5})
        expected = self.model.access_df["raam_value"].iloc[0] / 2
        actual = self.model.access_df["score"].iloc[0]

        assert actual == expected

    def test_score_run_again_and_test_overwrite(self):
        self.model.raam()
        self.model.score(col_dict={"raam_value": 0.5})

        self.model.score(col_dict={"raam_value": 0.25})
        expected = self.model.access_df["raam_value"].iloc[0] / 4
        actual = self.model.access_df["score"].iloc[0]

        assert actual == expected

    def test_score_invalid_access_value_raises_value_error(self):
        with pytest.raises(ValueError):
            bad_access_value = "Not in access df"
            self.model.score(col_dict={bad_access_value: 0.5})

    def test_set_cost_reconizes_column_newly_added(self):
        self.model.cost_names.append("new_cost")

        self.model.default_cost = "new_cost"
        actual = self.model.default_cost

        assert actual == "new_cost"

    def test_set_cost_unavailable_cost_measure_raises_value_error(self):
        with pytest.raises(ValueError):
            bad_cost_name = "Not an available cost name"
            self.model.default_cost = bad_cost_name

    def test_set_cost_neighbors(self):
        self.model.neighbor_cost_names.append("new_cost")

        self.model.neighbor_default_cost = "new_cost"
        actual = self.model.neighbor_default_cost

        assert actual == "new_cost"

    def test_set_cost_neighbors_unavailable_cost_measure_raises_value_error(self):
        with pytest.raises(ValueError):
            bad_cost_name = "Not an available cost name"
            self.model.neighbor_default_cost = bad_cost_name

    def test_user_cost_adds_new_column_to_cost_df(self):
        new_cost = self.model.cost_df.copy()
        new_cost["new_cost"] = 0

        self.model.append_user_cost(
            new_cost_df=new_cost, name="new_cost", origin="origin", destination="dest"
        )

        actual = "new_cost" in self.model.cost_df.columns

        assert actual

    def test_user_cost_adds_new_column_to_cost_names(self):
        new_cost = self.model.cost_df.copy()
        new_cost["new_cost"] = 0

        self.model.append_user_cost(
            new_cost_df=new_cost, name="new_cost", origin="origin", destination="dest"
        )

        actual = "new_cost" in self.model.cost_names

        assert actual

    def test_user_cost_neighbors_adds_new_column_to_neighbor_cost_df(self):
        new_cost = self.model.neighbor_cost_df.copy()
        new_cost["new_cost"] = 0

        self.model.append_user_cost_neighbors(
            new_cost_df=new_cost, name="new_cost", origin="origin", destination="dest"
        )

        actual = "new_cost" in self.model.neighbor_cost_df.columns

        assert actual

    def test_norm_access_df(self):
        self.model.raam()
        self.model.fca_ratio()

        normalized_df = self.model.norm_access_df

        actual1 = normalized_df["fca_value"].iloc[0]

        assert actual1 == 1

        actual2 = normalized_df["raam_value"].iloc[0]

        assert actual2 == 1
