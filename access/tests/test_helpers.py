import pytest
import util as tu

from access import Access
from access.access import helpers


class TestHelpers:
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

    def test_sanitize_supply_cost_set_cost_as_default(self):
        self.model.cost_names.append("other_cost")
        helpers.sanitize_supply_cost(self.model, None, "value")
        actual = self.model.default_cost

        assert actual == "cost"

    def test_sanitize_supply_cost_raise_value_error_if_cost_not_found(self):
        with pytest.raises(ValueError):
            helpers.sanitize_supply_cost(self.model, "some_cost", "value")

    def test_sanitize_demand_cost_set_cost_as_default(self):
        self.model.cost_names.append("other_cost")
        helpers.sanitize_demand_cost(self.model, None, "value")
        actual = self.model.default_cost

        assert actual == "cost"

    def test_sanitize_demand_cost_raise_value_error_if_cost_not_found(self):
        with pytest.raises(ValueError):
            helpers.sanitize_demand_cost(self.model, "some_cost", "value")

    def test_sanitize_supplies_provide_value_as_string(self):
        actual = helpers.sanitize_supplies(self.model, "some_value")

        assert actual == ["some_value"]

    def test_sanitize_supplies_raise_value_error_if_input_other_than_str_or_list(self):
        with pytest.raises(ValueError):
            helpers.sanitize_supplies(self.model, 5)
