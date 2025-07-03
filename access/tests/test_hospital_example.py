import pandas as pd
import pytest

from access import Access
from access.access import weights


def simple_2sfca(od, supply, demand, locs, max_travel=61, three_stage=False):
    """
    Base python implementation / sanity check of 2SFCA results.

    Assumes gravity weights with power of -1

    Params:
        od (pd.DataFrame): origin/destination matrix with
            origin columns and destinations on index.
        supply (Dict[int,int]): amount of supply at each location
        demand (Dict[int,int]): amount of demand at each location
        locs (List[int]): list of locations.

    Returns:
        Dict[int, float]: access per location

    """

    god = od
    if three_stage:
        w = 1 / od

        ws = w.sum(axis=0)  # Sum over destinations / within columns.
        g = w.divide(ws, axis=1)  # Divide columns by their sums.

        god = od / g

    d = {
        hosp: sum(
            demand[res] / god[res][hosp] for res in locs if od[res][hosp] < max_travel
        )
        for hosp in locs
    }

    r = {loc: supply[loc] / d[loc] for loc in locs}

    a = {
        res: sum(
            r[hosp] / god[res][hosp] for hosp in locs if od[res][hosp] < max_travel
        )
        for res in locs
    }

    return a


class TestHospitalExample:
    def setup_method(self):
        tracts = pd.DataFrame(
            [
                {"geoid": 1, "pop": 100, "doc": 15},
                {"geoid": 2, "pop": 50, "doc": 20},
                {"geoid": 3, "pop": 10, "doc": 100},
            ]
        )

        self.costs = []

        # Scenario 0 is gridlock
        # Gridlock. travel is congested in both directions
        self.costs.append(
            pd.DataFrame(
                [
                    # Self
                    {"origin": 1, "dest": 1, "cost": 1},
                    {"origin": 2, "dest": 2, "cost": 1},
                    {"origin": 3, "dest": 3, "cost": 1},
                    # Inbound
                    {"origin": 1, "dest": 3, "cost": 40},
                    {"origin": 2, "dest": 3, "cost": 40},
                    # Outbound
                    {"origin": 3, "dest": 1, "cost": 40},
                    {"origin": 3, "dest": 2, "cost": 40},
                    # Cross-city
                    {"origin": 1, "dest": 2, "cost": 80},
                    {"origin": 2, "dest": 1, "cost": 80},
                ]
            )
        )

        # Scenario 1 is faster treavel to the city
        # Commuter toll lane into the city  (similar dynamics to PM peak)
        self.costs.append(
            pd.DataFrame(
                [
                    # Self
                    {"origin": 1, "dest": 1, "cost": 1},
                    {"origin": 2, "dest": 2, "cost": 1},
                    {"origin": 3, "dest": 3, "cost": 1},
                    # Inbound -- faster
                    {"origin": 1, "dest": 3, "cost": 20},
                    {"origin": 2, "dest": 3, "cost": 20},
                    # Outbound
                    {"origin": 3, "dest": 1, "cost": 40},
                    {"origin": 3, "dest": 2, "cost": 40},
                    # Cross-city -- should also 40 + 20, but leaving...
                    {"origin": 1, "dest": 2, "cost": 80},
                    {"origin": 2, "dest": 1, "cost": 80},
                ]
            )
        )

        # Scenario 2 is faster travel out of the city
        # Commuter toll lane out of the city  (similar dynamics to AM peak)
        self.costs.append(
            pd.DataFrame(
                [
                    # Self
                    {"origin": 1, "dest": 1, "cost": 1},
                    {"origin": 2, "dest": 2, "cost": 1},
                    {"origin": 3, "dest": 3, "cost": 1},
                    # Inbound
                    {"origin": 1, "dest": 3, "cost": 40},
                    {"origin": 2, "dest": 3, "cost": 40},
                    # Outbound - faster
                    {"origin": 3, "dest": 1, "cost": 20},
                    {"origin": 3, "dest": 2, "cost": 20},
                    # Cross-city - should also be 40 + 20.
                    {"origin": 1, "dest": 2, "cost": 80},
                    {"origin": 2, "dest": 1, "cost": 80},
                ]
            )
        )

        # Scenario 3 is symmetric, but faster travel.
        # Commuter toll lane out of the city (similar dynamics to AM peak)
        self.costs.append(
            pd.DataFrame(
                [
                    # Self
                    {"origin": 1, "dest": 1, "cost": 1},
                    {"origin": 2, "dest": 2, "cost": 1},
                    {"origin": 3, "dest": 3, "cost": 1},
                    # Inbound
                    {"origin": 1, "dest": 3, "cost": 20},
                    {"origin": 2, "dest": 3, "cost": 20},
                    # Outbound - faster
                    {"origin": 3, "dest": 1, "cost": 20},
                    {"origin": 3, "dest": 2, "cost": 20},
                    # Cross-city -- twice each half...
                    {"origin": 1, "dest": 2, "cost": 40},
                    {"origin": 2, "dest": 1, "cost": 40},
                ]
            )
        )

        # input parameters fixed across scenarios
        # Neighbor cost not used; supressed to avoid confusion.
        params = {
            "demand_df": tracts,
            "demand_index": "geoid",
            "demand_value": "pop",
            "supply_df": tracts,
            "supply_index": "geoid",
            "supply_value": "doc",
            "cost_origin": "origin",
            "cost_dest": "dest",
            "cost_name": "cost",
        }

        # Dictionaries for simple version.
        locs = [1, 2, 3]
        pops = tracts.set_index("geoid")["pop"].to_dict()
        docs = tracts.set_index("geoid")["doc"].to_dict()

        # Instantiate the objects and run access.
        self.val_2sfca = {}
        self.val_3sfca = {}
        self.reference_2sfca = {}
        self.reference_3sfca = {}

        for n, costs in enumerate(self.costs):
            a = Access(**params, cost_df=costs)
            a.two_stage_fca(
                name=f"2sfca_s{n}", weight_fn=weights.gravity(1, -1), max_cost=61
            )
            a.three_stage_fca(
                name=f"3sfca_s{n}", weight_fn=weights.gravity(1, -1), max_cost=61
            )

            self.val_2sfca[n] = a.access_df[f"2sfca_s{n}_doc"].to_dict()
            self.val_3sfca[n] = a.access_df[f"3sfca_s{n}_doc"].to_dict()

            od = costs.pivot_table(index="origin", columns="dest", values="cost").T

            self.reference_2sfca[n] = simple_2sfca(od, docs, pops, locs)
            self.reference_3sfca[n] = simple_2sfca(
                od, docs, pops, locs, three_stage=True
            )

    def test_simple_2sfca_scenario_0(self):
        assert pytest.approx(self.val_2sfca[0][1]) == self.reference_2sfca[0][1]
        assert pytest.approx(self.val_2sfca[0][2]) == self.reference_2sfca[0][2]
        assert pytest.approx(self.val_2sfca[0][3]) == self.reference_2sfca[0][3]

    def test_simple_2sfca_scenario_1(self):
        assert pytest.approx(self.val_2sfca[1][1]) == self.reference_2sfca[1][1]
        assert pytest.approx(self.val_2sfca[1][2]) == self.reference_2sfca[1][2]
        assert pytest.approx(self.val_2sfca[1][3]) == self.reference_2sfca[1][3]

    def test_simple_2sfca_scenario_2(self):
        assert pytest.approx(self.val_2sfca[2][1]) == self.reference_2sfca[2][1]
        assert pytest.approx(self.val_2sfca[2][2]) == self.reference_2sfca[2][2]
        assert pytest.approx(self.val_2sfca[2][3]) == self.reference_2sfca[2][3]

    def test_simple_2sfca_scenario_3(self):
        assert pytest.approx(self.val_2sfca[3][1]) == self.reference_2sfca[3][1]
        assert pytest.approx(self.val_2sfca[3][2]) == self.reference_2sfca[3][2]
        assert pytest.approx(self.val_2sfca[3][3]) == self.reference_2sfca[3][3]

    def test_scenario_0_v_1(self):
        # access at 1 should increase.
        # Supply at 3 is more pertinent / lower cost since people can get there faster.
        assert self.val_2sfca[1][1] > self.val_2sfca[0][1]

        # access at 2 should increase. Same reasoning as above.
        assert self.val_2sfca[1][2] > self.val_2sfca[0][2]

        # access at 3 should decrease.
        # More patients from 1 and 2 means greater demands on 3's doctors.
        assert self.val_2sfca[1][3] < self.val_2sfca[0][3]

    def test_scenario_0_v_2(self):
        # access at 1 should decrease.
        # There is more demand coming from 3 since people can come from there faster
        assert self.val_2sfca[2][1] < self.val_2sfca[0][1]

        # access at 2 should decrease.
        # There is more demand coming from 3 since people can come from there faster
        assert self.val_2sfca[2][2] < self.val_2sfca[0][2]

        # access at 3 should increase.
        # There is more supply available from 1,2 since people can get there faster
        assert self.val_2sfca[2][3] > self.val_2sfca[0][3]

    def test_scenario_0_v_3(self):
        # access at 1 should increase. It is easier to use the place with more docs.
        assert self.val_2sfca[3][1] > self.val_2sfca[0][1]

        # access at 2 should increase. Same reasoning as for 1.
        assert self.val_2sfca[3][2] > self.val_2sfca[0][2]

        # access at 3 should decrease. Same but in reverse
        # -- suburbanites are using "urban" supply.
        assert self.val_2sfca[3][3] < self.val_2sfca[0][3]

    def test_simple_3sfca_scenario_0(self):
        assert pytest.approx(self.val_3sfca[0][1]) == self.reference_3sfca[0][1]
        assert pytest.approx(self.val_3sfca[0][2]) == self.reference_3sfca[0][2]
        assert pytest.approx(self.val_3sfca[0][3]) == self.reference_3sfca[0][3]

    def test_simple_3sfca_scenario_1(self):
        assert pytest.approx(self.val_3sfca[1][1]) == self.reference_3sfca[1][1]
        assert pytest.approx(self.val_3sfca[1][2]) == self.reference_3sfca[1][2]
        assert pytest.approx(self.val_3sfca[1][3]) == self.reference_3sfca[1][3]

    def test_simple_3sfca_scenario_2(self):
        assert pytest.approx(self.val_3sfca[2][1]) == self.reference_3sfca[2][1]
        assert pytest.approx(self.val_3sfca[2][2]) == self.reference_3sfca[2][2]
        assert pytest.approx(self.val_3sfca[2][3]) == self.reference_3sfca[2][3]

    def test_simple_3sfca_scenario_3(self):
        assert pytest.approx(self.val_3sfca[3][1]) == self.reference_3sfca[3][1]
        assert pytest.approx(self.val_3sfca[3][2]) == self.reference_3sfca[3][2]
        assert pytest.approx(self.val_3sfca[3][3]) == self.reference_3sfca[3][3]
