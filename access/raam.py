import numpy as np
import pandas as pd


def iterate_raam(
    demand,
    supply,
    travel,
    max_cycles=151,
    initial_step=0.2,
    min_step=0.005,
    half_life=50,
    limit_initial=20,
    verbose=False,
):

    norig, ndest = travel.shape
    assignment = np.zeros((norig, ndest))
    assignment[range(norig), travel.argmin(axis=1)] = demand

    for i in range(max_cycles):

        demand_at_supply = assignment.sum(axis=0)
        congestion_cost = demand_at_supply / supply
        total_cost = congestion_cost + travel

        max_locations = np.ma.masked_array(total_cost, assignment == 0).argmax(axis=1)
        min_locations = total_cost.argmin(axis=1)

        slmin = supply[min_locations]
        slmax = supply[max_locations]

        trlmin = travel[range(norig), min_locations]
        trlmax = travel[range(norig), max_locations]

        drlmin = assignment[range(norig), min_locations]
        drlmax = assignment[range(norig), max_locations]

        dr = drlmin + drlmax

        drotherlmin = demand_at_supply[min_locations] - drlmin
        drotherlmax = demand_at_supply[max_locations] - drlmax

        drlmin_new = ((slmin * slmax) / (slmin + slmax)) * (
            (trlmax - trlmin) + (dr + drotherlmax) / slmax - drotherlmin / slmin
        )

        delta = drlmin_new - drlmin

        delta = np.minimum(delta, drlmax)
        delta = np.where(max_locations == min_locations, 0, delta)

        if type(initial_step) is float:
            step_size = initial_step * 0.5 ** (i / half_life)
            if step_size < min_step:
                step_size = min_step

            delta = np.minimum(delta, step_size * demand).astype(int)

        else:

            step_size = int(np.round(initial_step * 0.5 ** (i / half_life)))
            if step_size < min_step:
                step_size = min_step

            delta = np.minimum(delta, step_size).astype(int)

        ## We don't want "attractive locations" getting mobbed.
        ## This will only happen in the first 10-20 cycles.
        ## So only do these (somewhat costly checks) then.
        if i < limit_initial:

            delta_mat = np.zeros(travel.shape)
            delta_mat[range(norig), min_locations] += delta

            naive_assignment = delta_mat.sum(axis=0) / (supply)  # * rho)
            scale_factor = np.maximum(naive_assignment, 1)

            delta_mat = (delta_mat / scale_factor).round().astype(int)

            delta = delta_mat.sum(axis=1)

        assignment[range(norig), min_locations] += delta
        assignment[range(norig), max_locations] -= delta

        assert (assignment.sum(axis=1) == demand).all()

        if not (i % 25):
            raam_cost = (total_cost * assignment).sum(axis=1) / assignment.sum(axis=1)

            if verbose:
                print(
                    "{:d} {:.2f} {:d} {:.3f}".format(
                        i, raam_cost.mean(), delta.sum(), step_size
                    ),
                    end=" || ",
                )

    raam_cost = (total_cost * assignment).sum(axis=1) / assignment.sum(axis=1)

    return raam_cost


def raam(
    demand_df,
    supply_df,
    cost_df,
    demand_index=True,
    demand_name="demand",
    supply_index=True,
    supply_name="supply",
    cost_origin="origin",
    cost_dest="dest",
    cost_name="cost",
    tau=60,
    rho=None,
    max_cycles=150,
    initial_step=0.2,
    min_step=0.005,
    half_life=50,
    verbose=False,
):
    """Calculate the rational agent access model's total cost --
    a weighted travel and congestion cost.
    The balance of the two costs is expressed by the
    :math:`\\tau` parameter, which corresponds to the travel time
    required to accept of congestion by 100% of the mean demand to supply ratio
    in the study area.

    Parameters
    ----------

    demand_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                    The origins dataframe, containing a location index and a total demand.
    demand_origin : str
                    is the name of the column of `demand` that holds the origin ID.
    demand_value  : str
                    is the name of the column of `demand` that holds the aggregate demand at a location.
    supply_origin : str
                    is the name of the column of `demand` that holds the origin ID.
    supply_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                    The origins dataframe, containing a location index and level of supply
    cost_df       : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                    This dataframe contains a link between neighboring demand locations, and a cost between them.
    cost_origin   : str
                    The column name of the locations of users or consumers.
    cost_dest     : str
                    The column name of the supply or resource locations.
    cost_name     : str
                    The column name of the travel cost between origins and destinations
    weight_fn  : function
                  This fucntion will weight the value of resources/facilities,
                  as a function of the raw cost.
    max_cycles : int
                  Max number of cycles.
    max_shift  : int
                  This is the maximum number to shift in each cycle.
    max_cost   : float
                  This is the maximum cost to consider in the weighted sum;
                  note that it applies along with the weight function.

    Returns
    -------
    access     : pandas.Series

                  A -- potentially-weighted -- Rational Agent Access Model cost.
    """

    if demand_index is not True:
        demand_df = demand_df.set_index(demand_index)
    if supply_index is not True:
        supply_df = supply_df.set_index(supply_index)

    demand_df = demand_df[demand_df[demand_name] > 0].copy()
    supply_df = supply_df[supply_df[supply_name] > 0].copy()

    demand_locations = list(set(cost_df[cost_origin]) & set(demand_df.index))
    supply_locations = list(set(cost_df[cost_dest]) & set(supply_df.index))

    cost_pivot = cost_df.pivot(index=cost_origin, columns=cost_dest, values=cost_name)
    try:
        travel_np = cost_pivot.loc[demand_locations, supply_locations].to_numpy().copy()
    except:
        travel_np = cost_pivot.loc[demand_locations, supply_locations].values.copy()

    travel_np = travel_np / tau
    travel_np = np.ma.masked_array(travel_np, np.isnan(travel_np))

    # If it is not specified, rho is the average demand to supply ratio.
    if rho is None:
        rho = demand_df[demand_name].sum() / supply_df[supply_name].sum()

    try:
        supply_np = supply_df.loc[supply_locations, supply_name].to_numpy().copy()
    except:
        supply_np = supply_df.loc[supply_locations, supply_name].values.copy()

    supply_np = supply_np * rho

    # Change this -- should be
    try:
        demand_np = demand_df.loc[demand_locations, demand_name].to_numpy().copy()
    except:
        demand_np = demand_df.loc[demand_locations, demand_name].values.copy()

    raam_cost = iterate_raam(
        demand_np,
        supply_np,
        travel_np,
        verbose=verbose,
        max_cycles=max_cycles,
        initial_step=initial_step,
        min_step=min_step,
        half_life=half_life,
    )

    rs = pd.Series(name="RAAM", index=demand_locations, data=raam_cost)

    return rs
