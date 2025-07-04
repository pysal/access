import geopandas as gpd
import pandas as pd
import pytest

from access import Access


class TestEuclidean:
    def setup_method(self):
        demand_data = pd.DataFrame({"id": [0], "x": [0], "y": [0], "value": [1]})
        demand_grid = gpd.GeoDataFrame(
            demand_data, geometry=gpd.points_from_xy(demand_data.x, demand_data.y)
        )
        demand_grid["geometry"] = demand_grid.buffer(0.5)

        supply_data = pd.DataFrame({"id": [1], "x": [0], "y": [1], "value": [1]})
        supply_grid = gpd.GeoDataFrame(
            supply_data, geometry=gpd.points_from_xy(supply_data.x, supply_data.y)
        )
        supply_grid["geometry"] = supply_grid.buffer(0.5)

        cost_matrix = pd.DataFrame({"origin": [0], "dest": [1], "cost": [1]})

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

    def test_euclidean_point_to_point(self):
        self.model.create_euclidean_distance(
            name="euclidian", threshold=2, centroid_o=True, centroid_d=True
        )
        actual = self.model.cost_df["euclidian"][0]

        assert pytest.approx(actual) == 1

    def test_euclidean_point_to_poly(self):
        self.model.create_euclidean_distance(
            name="euclidian", threshold=2, centroid_o=True, centroid_d=False
        )
        actual = self.model.cost_df["euclidian"][0]

        assert pytest.approx(actual) == 0.5

    def test_euclidean_poly_to_poly(self):
        self.model.create_euclidean_distance(
            name="euclidian", threshold=2, centroid_o=False, centroid_d=False
        )
        actual = self.model.cost_df["euclidian"][0]

        assert pytest.approx(actual) == 0

    def test_euclidean_without_geopandas_demand_dataframe_raises_type_error(self):
        with pytest.raises(TypeError):
            self.model.demand_df = self.model.demand_df[["x", "y", "value"]]
            self.model.create_euclidean_distance()

    def test_euclidean_without_geopandas_supply_dataframe_raises_type_error(self):
        with pytest.raises(TypeError):
            self.model.supply_df = self.model.supply_df[["x", "y", "value"]]
            self.model.create_euclidean_distance()

    def test_euclidean_sets_euclidean_as_default_if_no_default_exists(self):
        delattr(self.model, "_default_cost")
        self.model.create_euclidean_distance()

        actual = hasattr(self.model, "_default_cost")

        assert actual


class TestEuclideanNeighbors:
    def setup_method(self):
        demand_data = pd.DataFrame(
            {"id": [0, 1], "x": [0, 0], "y": [0, 1], "value": [1, 1]}
        )
        demand_grid = gpd.GeoDataFrame(
            demand_data, geometry=gpd.points_from_xy(demand_data.x, demand_data.y)
        )
        demand_grid["geometry"] = demand_grid.buffer(0.25)

        supply_data = pd.DataFrame({"id": [1], "x": [0], "y": [1], "value": [1]})
        supply_grid = gpd.GeoDataFrame(
            supply_data, geometry=gpd.points_from_xy(supply_data.x, supply_data.y)
        )

        point_cost_matrix = pd.DataFrame(
            {
                "origin": [0, 0, 1, 1],
                "dest": [1, 0, 0, 1],
                "ctr_expectation": [1, 0, 1, 0],
            }
        )

        self.model = Access(
            demand_df=demand_grid,
            demand_index="id",
            demand_value="value",
            supply_df=supply_grid,
            supply_index="id",
            supply_value="value",
            cost_df=point_cost_matrix,
            cost_origin="origin",
            cost_dest="dest",
            cost_name="ctr_expectation",
            neighbor_cost_df=point_cost_matrix,
            neighbor_cost_origin="origin",
            neighbor_cost_dest="dest",
            neighbor_cost_name="ctr_expectation",
        )

        # The geometries are buffered by 0.25, so the circles are 0.5 apart.
        # Add these as a second set of costs
        buff_cost_matrix = pd.DataFrame(
            {
                "origin": [0, 0, 1, 1],
                "dest": [1, 0, 0, 1],
                "buf_expectation": [0.5, 0, 0.5, 0],
            }
        )

        self.model.append_user_cost_neighbors(
            buff_cost_matrix, "origin", "dest", "buf_expectation"
        )

    def test_euclidean_neighbors_centroids(self):
        self.model.create_euclidean_distance_neighbors(
            name="euclidean", threshold=2, centroid=True
        )
        assert (
            pytest.approx(
                (
                    self.model.neighbor_cost_df.euclidean
                    - self.model.neighbor_cost_df.ctr_expectation
                )
                .abs()
                .max(),
            )
            == 0
        )

    def test_euclidean_neighbors_poly(self):
        self.model.create_euclidean_distance_neighbors(
            name="euclidean", threshold=2, centroid=False
        )

        assert (
            pytest.approx(
                (
                    self.model.neighbor_cost_df.euclidean
                    - self.model.neighbor_cost_df.buf_expectation
                )
                .abs()
                .max()
            )
            == 0
        )

    def test_euclidean_neighbors_without_geopandas_demand_dataframe_raises_type_error(
        self,
    ):
        with pytest.raises(TypeError):
            self.model.demand_df = self.model.demand_df[["x", "y", "value"]]
            self.model.create_euclidean_distance_neighbors()

    def test_euclidean_neighbors_sets_euclidean_as_default_if_no_default_exists(self):
        delattr(self.model, "_neighbor_default_cost")
        self.model.create_euclidean_distance_neighbors()

        actual = hasattr(self.model, "_neighbor_default_cost")

        assert actual
