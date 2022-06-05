import warnings
import numpy as np
import pandas as pd

from .weights import step_fn


def weighted_catchment(
    loc_df,
    cost_df,
    max_cost=None,
    cost_source="origin",
    cost_dest="dest",
    cost_cost="cost",
    loc_index="geoid",
    loc_value=None,
    weight_fn=None,
    three_stage_weight=None,
):
    """
    Calculation of the floating catchment (buffered) accessibility
    sum, from DataFrames with computed distances.
    This catchment may be either a simple buffer -- with cost below
    a single threshold -- or an additional weight may be applied
    as a function of the access cost.

    Parameters
    ----------

    loc_df         : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                 should contain at _least_ a list of the locations (`df_dest`) at which facilities are located.
    loc_index   : {bool, str}
                 is the the name of the df column that holds the facility locations.
                 If it is a bool, then the it the location is already on the index.
    loc_value   : str
                 If this value is `None`, a count will be used in place of a weight.
                 Use this, for instance, to count restaurants, instead of total doctors in a practice.
    cost_df    : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                 This dataframe contains the precomputed costs from an origin/index location to destinations.
    cost_source : str
                 The name of the column name of the index locations -- this is what will be grouped.
    cost_dest  : str
                 The name of the column name of the destination locations.
                 This is what will be _in_ each group.
    cost_cost  : str
                 This is is the name of the cost column.
    weight_fn  : function
                 This function will weight the value of resources/facilities,
                 as a function of the raw cost.
    max_cost   : float
                 This is the maximum cost to consider in the weighted sum;
                 note that it applies _along with_ the weight function.

    Returns
    -------
    resources  : pandas.Series
                 A -- potentially weighted -- sum of resources, facilities, or consumers.
    """
    # merge the loc dataframe and cost dataframe together
    if loc_index is True:
        temp = pd.merge(cost_df, loc_df, left_on=cost_source, right_index=True)
    else:
        temp = pd.merge(cost_df, loc_df, left_on=cost_source, right_on=loc_index)

    # constrain by max cost
    if max_cost is not None:
        temp = temp[temp[cost_cost] < max_cost].copy()

    # apply a weight function if inputted -- either enhanced two stage or three stage
    if weight_fn:
        if three_stage_weight is not None:
            new_loc_value_column = temp[loc_value] * temp.W3 * temp.G
            temp = temp.drop([loc_value], axis=1)
            temp[loc_value] = new_loc_value_column
        else:
            temp[loc_value] *= temp[cost_cost].apply(weight_fn)

    return temp.groupby([cost_dest])[loc_value].sum()


def fca_ratio(
    demand_df,
    supply_df,
    demand_cost_df,
    supply_cost_df,
    max_cost,
    demand_index="geoid",
    demand_name="demand",
    supply_index="geoid",
    supply_name="supply",
    demand_cost_origin="origin",
    demand_cost_dest="dest",
    demand_cost_name="cost",
    supply_cost_origin="origin",
    supply_cost_dest="dest",
    supply_cost_name="cost",
    weight_fn=None,
    normalize=False,
    noise="quiet",
):
    """Calculation of the floating catchment accessibility
    ratio, from DataFrames with precomputed distances.
    This is accomplished through two calls of the :meth:`Access.access.weighted_catchment` method.

    Parameters
    ----------

    demand_df          : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                         The origins dataframe, containing a location index and a total demand.
    supply_df          : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                         The origins dataframe, containing a location index and level of supply
    demand_cost_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                         This dataframe contains a link between neighboring demand locations, and a cost between them.
    supply_cost_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                         This dataframe contains a link between neighboring supply locations, and a cost between them.
    max_cost           : float
                         This is the maximum cost to consider in the weighted sum;
                         note that it applies *along with* the weight function.
    demand_index       : str
                         is the name of the column that holds the IDs.
    demand_name       : str
                         is the name of the column of `demand` that holds the aggregate demand at a location.
    supply_index       : str
                         is the name of the column that holds the IDs.
    supply_name       : str
                         is the name of the column of `supply_df` that holds the aggregate supply at a location.
    demand_cost_origin : str
                         The column name of the index locations -- this is what will be grouped.
    demand_cost_dest   : str
                         The column name of the index locations -- this is what will be grouped.
    demand_cost_name   : str
                         The column name of the travel cost.
    supply_cost_origin : str
                         The column name of the index locations -- this is what will be grouped.
    supply_cost_dest   : str
                         The column name of the index locations -- this is what will be grouped.
    supply_cost_name   : str
                         The column name of the travel cost.
    weight_fn          : function
                         This function will weight the value of resources/facilities,
                         as a function of the raw cost.
    normalize          : bool
                         True to normalize the FCA series, by default False.
    noise              : str
                         Default 'quiet', otherwise gives messages that indicate potential issues.

    Returns
    -------
    access     : pandas.Series
                 A -- potentially-weighted -- access ratio.
    """

    # if there is a discrepancy between the demand and supply cost dataframe locations, print it
    if (
        len(
            set(demand_df.index.tolist())
            - set(supply_cost_df[supply_cost_dest].unique())
        )
        != 0
    ):
        warnings.warn("some tracts may be unaccounted for in supply_cost", stacklevel=1)

    # get a series of the total demand within the buffer zone
    total_demand_series = weighted_catchment(
        demand_df,
        demand_cost_df,
        max_cost,
        cost_source=demand_cost_dest,
        cost_dest=demand_cost_origin,
        cost_cost=demand_cost_name,
        loc_index=demand_index,
        loc_value=demand_name,
        weight_fn=weight_fn,
    )
    # get a series of the total supply within the buffer zone
    total_supply_series = weighted_catchment(
        supply_df,
        supply_cost_df,
        max_cost,
        cost_source=supply_cost_dest,
        cost_dest=supply_cost_origin,
        cost_cost=supply_cost_name,
        loc_index=supply_index,
        loc_value=supply_name,
        weight_fn=weight_fn,
    )

    # join the aggregate demand and the aggregate supply into one dataframe
    temp = (
        total_supply_series.to_frame(name="supply")
        .join(total_demand_series.to_frame(name="demand"), how="right")
        .fillna(0)
    )

    # calculate the floating catchement area, or supply divided by demand
    temp["FCA"] = temp["supply"] / temp["demand"]
    base_FCA_series = temp["FCA"]

    if noise != "quiet":
        # depending on the version history of the census tract data you use, this will print out the tracts that have undefined FCA values
        print(base_FCA_series[pd.isna(base_FCA_series)])

    return base_FCA_series


def two_stage_fca(
    demand_df,
    supply_df,
    cost_df,
    max_cost=None,
    demand_index="geoid",
    demand_name="demand",
    supply_index="geoid",
    supply_name="supply",
    cost_origin="origin",
    cost_dest="dest",
    cost_name="cost",
    weight_fn=None,
    normalize=False,
):
    """
    Calculation of the two-stage floating catchment accessibility
    ratio, from DataFrames with precomputed distances.
    This is accomplished through a single call of the `access.weighted_catchment` method,
    to retrieve the patients using each provider.
    The ratio of providers per patient is then calculated at each care destination,
    and that ratio is weighted and summed at each corresponding demand site.
    This is based on the original paper by Luo and Wang :cite:`2002_luo_spatial_accessibility_chicago`,
    as extended by Luo and Qi :cite:`2009_luo_qi_E2SFCA`
    and McGrail and Humphreys :cite:`2009_mcgrail_improved_2SFCA`.

    Parameters
    ----------

    demand_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                    The origins dataframe, containing a location index and a total demand.
    demand_origin : str
                    is the name of the column of `demand_df` that holds the origin ID.
    demand_value  : str
                    is the name of the column of `demand_df` that holds the aggregate demand at a location.
    supply_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                    The origins dataframe, containing a location index and level of supply
    supply_origin : str
                    is the name of the column of `supply_df` that holds the origin ID.
    supply_value  : str
                    is the name of the column of `supply_df` that holds the aggregate demand at a location.
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
    max_cost   : float
                 This is the maximum cost to consider in the weighted sum;
                   note that it applies _along with_ the weight function.
    normalize  : bool
                  True to normalize the FCA series, by default False.
    Returns
    -------
    access     : pandas.Series
                 A -- potentially-weighted -- two-stage access ratio.
    """
    # get a series of total demand then calculate the supply to total demand ratio for each location
    total_demand_series = weighted_catchment(
        demand_df,
        cost_df,
        max_cost,
        cost_source=cost_origin,
        cost_dest=cost_dest,
        cost_cost=cost_name,
        loc_index=demand_index,
        loc_value=demand_name,
        weight_fn=weight_fn,
    )

    # create a temporary dataframe, temp, that holds the supply and aggregate demand at each location
    total_demand_series.name += "_W"
    temp = supply_df.join(total_demand_series, how="right")

    # there may be NA values due to a shorter supply dataframe than the demand dataframe.
    # in this case, replace any potential NA values(which correspond to supply locations with no supply) with 0.
    temp[supply_name].fillna(0, inplace=True)

    # calculate the fractional ratio of supply to aggregate demand at each location, or Rl
    temp["Rl"] = temp[supply_name] / temp[demand_name + "_W"]

    # separate the fractional ratio of supply to aggregate demand at each location, or Rl, into a new dataframe
    supply_to_total_demand_frame = pd.DataFrame(data={"Rl": temp["Rl"]})
    supply_to_total_demand_frame.index.name = "geoid"

    # sum, into a series, the supply to total demand ratios for each location
    two_stage_fca_series = weighted_catchment(
        supply_to_total_demand_frame,
        cost_df,
        max_cost,
        cost_source=cost_dest,
        cost_dest=cost_origin,
        cost_cost=cost_name,
        loc_index="geoid",
        loc_value="Rl",
        weight_fn=weight_fn,
    )

    return two_stage_fca_series


def three_stage_fca(
    demand_df,
    supply_df,
    cost_df,
    max_cost,
    demand_index="geoid",
    demand_name="demand",
    supply_index="geoid",
    supply_name="supply",
    cost_origin="origin",
    cost_dest="dest",
    cost_name="cost",
    weight_fn=None,
    normalize=False,
):
    """Calculation of the three-stage floating catchment accessibility
    ratio, from DataFrames with precomputed distances.
    This is accomplished through a single call of the :meth:`access.access.weighted_catchment` method,
    to retrieve the patients using each provider.
    The ratio of providers per patient is then calculated at each care destination,
    and that ratio is weighted and summed at each corresponding demand site.
    The only difference weight respect to the 2SFCA method is that,
    in addition to a distance-dependent weight (`weight_fn`),
    a preference weight *G* is calculated.  That calculation
    uses the value :math:`\\beta`.
    See the original paper by Wan, Zou, and Sternberg. :cite:`2012_wan_3SFCA`

    Parameters
    ----------

    demand_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                    The origins dataframe, containing a location index and a total demand.
    demand_origin : str
                    is the name of the column of `demand` that holds the origin ID.
    demand_value  : str
                    is the name of the column of `demand` that holds the aggregate demand at a location.
    supply_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                    The origins dataframe, containing a location index and level of supply
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
    max_cost   : float
                 This is the maximum cost to consider in the weighted sum;
                 note that it applies *along with* the weight function.
    preference_weight_beta : float
                             Parameter scaling with the gaussian weights,
                             used to generate preference weights.

    Returns
    -------
    access     : pandas.Series
                 A -- potentially-weighted -- three-stage access ratio.
    """

    # create preference weight 'G', which is the weight
    cost_df["W3"] = cost_df[cost_name].apply(weight_fn)
    W3sum_frame = (
        cost_df[[cost_origin, "W3"]]
        .groupby(cost_origin)
        .sum()
        .rename(columns={"W3": "W3sum"})
        .reset_index()
    )
    cost_df = pd.merge(cost_df, W3sum_frame)
    cost_df["G"] = cost_df.W3 / cost_df.W3sum

    # get a series of total demand then calculate the supply to total demand ratio for each location
    total_demand_series = weighted_catchment(
        demand_df,
        cost_df,
        max_cost,
        cost_source=cost_origin,
        cost_dest=cost_dest,
        cost_cost=cost_name,
        loc_index=demand_index,
        loc_value=demand_name,
        weight_fn=weight_fn,
        three_stage_weight=True,
    )

    # create a temporary dataframe, temp, that holds the supply and aggregate demand at each location
    total_demand_series.name += "_W"
    temp = supply_df.join(total_demand_series, how="right")

    # there may be NA values due to a shorter supply dataframe than the demand dataframe.
    # in this case, replace any potential NA values(which correspond to supply locations with no supply) with 0.
    temp[supply_name].fillna(0, inplace=True)

    # calculate the fractional ratio of supply to aggregate demand at each location, or Rl
    temp["Rl"] = temp[supply_name] / temp[demand_name + "_W"]

    # separate the fractional ratio of supply to aggregate demand at each location, or Rl, into a new dataframe
    supply_to_total_demand_frame = pd.DataFrame(data={"Rl": temp["Rl"]})
    supply_to_total_demand_frame.index.name = "geoid"

    # sum, into a series, the supply to total demand ratios for each location
    three_stage_fca_series = weighted_catchment(
        supply_to_total_demand_frame,
        cost_df.sort_index(),
        max_cost,
        cost_source=cost_dest,
        cost_dest=cost_origin,
        cost_cost=cost_name,
        loc_index="geoid",
        loc_value="Rl",
        weight_fn=weight_fn,
        three_stage_weight=True,
    )

    # remove the preference weight G from the original costs dataframe
    cost_df.drop(columns=["G", "W3", "W3sum"], inplace=True)

    return three_stage_fca_series
