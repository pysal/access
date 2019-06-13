def raam(demand_df, supply_df, demand_cost_df, supply_cost_df,
         demand_origin = "origin", demand_name   = "demand",
         supply_origin = "dest",   supply_name   = "supply",
         cost_origin   = "origin", cost_dest     = "dest", cost_name = "cost",
         tau = 1, max_cost = None, weight_fn = None):
    """
    Calculate the rational agent access model's total cost -- 
      a weighted travel and congestion cost.
    The balance of the two costs is expressed by the
      $\tau$ parameter, which corresponds to the travel time 
      required to accept of congestion by 100% of the mean demand to supply ratio
      in the study area.

    Parameters
    ----------

    demand_df     : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                    The origins dataframe, containing a location index and a total demand.
    demand_origin : str
                    is the name of the column of `demand` that holds the origin ID.
    demand_value  : str
                    is the name of the column of `demand` that holds the aggregate demand at a location.
    supply_df     : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                    The origins dataframe, containing a location index and level of supply
    supply_df     : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                    The origins dataframe, containing a location index and level of supply
    cost_df       : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
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
    max_cost   : float
                 This is the maximum cost to consider in the weighted sum;
                   note that it applies _along with_ the weight function.

    Returns
    -------
    access     : pandas.Series
                 A -- potentially-weighted -- Rational Agent Access Model cost.
    """
    
    return pandas.Series([10])



