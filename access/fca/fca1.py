def weighted_catchment(df, cost_df, weight_fn = None, max_cost = None,
                       df_dest    = "dest",   df_value = None,
                       cost_index = "origin", cost_dest = "dest", cost_name = "cost"):
    """
    Calculation of the floating catchment (buffered) accessibility
    ratio, from DataFrames with computed distances.
    This catchment may be either a simple buffer -- with cost 
      below a single threshold -- or an additional weight may be applied
      as a function of the access cost.

    Parameters
    ----------

    df         : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                 should contain at _least_ a list of the locations (`df_dest`) at which facilities are located.
    df_dest    : str
                 is the the name of the df column that holds the facility locations.
    df_value   : str
                 If this value is `None`, a count will be used in place of a weight.
                 Use this, for instance, to count restaurants, instead of total doctors in a practice.
    cost_df    : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                 This dataframe contains the precomputed costs from an origin/index location to destinations.
    cost_index : str
                 The name of the column name of the index locations -- this is what will be grouped.
    cost_dest  : str
                 The name of the column name of the destination locations.
                 This is what will be _in_ each group.
    cost_name  : str
                 This is is the name of the cost column.
    weight_fn  : function
                 This fucntion will weight the value of resources/facilities,
                 as a function of the raw cost.
    max_cost   : float
                 This is the maximum cost to consider in the weighted sum;
                   note that it applies _along with_ the weight function.

    Returns
    -------
    resources  : pandas.Series
                 A -- potentially weighted -- sum of resources, facilities, or consumers.
    """
    
    return 10

def fca_ratio(demand_df, supply_df, demand_cost_df, supply_cost_df,
              demand_index = True, demand_name   = "demand",
              supply_index = True, supply_name   = "supply",
              demand_cost_origin = "origin", demand_cost_dest = "dest", demand_cost_name = "cost",
              supply_cost_origin = "origin", supply_cost_dest = "dest", supply_cost_name = "cost",
              max_cost = None, weight_fn = None):
    """
    Calculation of the floating catchment accessibility
      ratio, from DataFrames with precomputed distances.
    This is accomplished through two calls of the `access.weighted_catchment` method.

    Parameters
    ----------

    demand_df          : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                         The origins dataframe, containing a location index and a total demand.
    demand_index       : {bool, str}
                         indicates either that the index of `demand_df` is the ID of the supply locations,
                           or gives the name of the column that holds the IDs.
    demand_value       : str
                         is the name of the column of `demand` that holds the aggregate demand at a location.
    supply_df          : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                         The origins dataframe, containing a location index and level of supply
    supply_index       : {bool, str}
                         indicates either that the index of `supply_df` is the ID of the supply locations, or gives
                           the name of the column that holds the IDs.
    supply_value       : str
                         is the name of the column of `demand` that holds the aggregate demand at a location.
    demand_cost_df     : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                         This dataframe contains a link between neighboring demand locations, and a cost between them.
    demand_cost_origin : str
                         The column name of the index locations -- this is what will be grouped.
    demand_cost_dest   : str
                         The column name of the index locations -- this is what will be grouped.
    demand_cost_name   : str
                         The column name of the travel cost.
    supply_cost_df     : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                         This dataframe contains a link between neighboring supply locations, and a cost between them.
    supply_cost_origin : str
                         The column name of the index locations -- this is what will be grouped.
    supply_cost_dest   : str
                         The column name of the index locations -- this is what will be grouped.
    supply_cost_name   : str
                         The column name of the travel cost.
    weight_fn          : function
                         This fucntion will weight the value of resources/facilities,
                         as a function of the raw cost.
    max_cost           : float
                         This is the maximum cost to consider in the weighted sum;
                           note that it applies _along with_ the weight function.

    Returns
    -------
    access     : pandas.Series
                 A -- potentially-weighted -- access ratio.
    """
    
    return pandas.Series([10])

