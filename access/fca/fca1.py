import pandas as pd
import numpy as np
import geopandas as gpd

def weighted_catchment(loc_df, cost_df, max_cost, cost_source = "origin", cost_dest = "dest", cost_cost = "cost", 
                       loc_dest = "dest",loc_dest_value = None, weight_fn = None,):
    """
    Calculation of the floating catchment (buffered) accessibility
    sum, from DataFrames with computed distances.
    This catchment may be either a simple buffer -- with cost 
      below a single threshold -- or an additional weight may be applied
      as a function of the access cost.
 
    Parameters
    ----------

    loc_df         : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                 should contain at _least_ a list of the locations (`df_dest`) at which facilities are located.
    loc_dest    : str
                 is the the name of the df column that holds the facility locations.
    loc_dest_value   : str
                 If this value is `None`, a count will be used in place of a weight.
                 Use this, for instance, to count restaurants, instead of total doctors in a practice.
    cost_df    : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                 This dataframe contains the precomputed costs from an origin/index location to destinations.
    cost_source : str
                 The name of the column name of the index locations -- this is what will be grouped.
    cost_dest  : str
                 The name of the column name of the destination locations.
                 This is what will be _in_ each group.
    cost_cost  : str
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
    if loc_dest != cost_dest:
        temp = pd.merge(cost_df, loc_df, left_on = cost_dest, right_on = loc_dest)
        temp.drop(columns = loc_dest, inplace = True)
    else:
        temp = pd.merge(cost_df, loc_df, on = cost_dest)
    
    temp = temp[temp[cost_cost] < max_cost]
    
    if loc_dest_value is None:
        return temp.groupby([cost_source])[cost_dest].count()
    else:
        return temp.groupby([cost_source])[loc_dest_value].sum()

def fca_ratio(demand_df, supply_df, demand_cost_df, supply_cost_df, max_cost,
              demand_index = 'geoid', demand_name = "demand",
              supply_index = 'geoid', supply_name  = "supply",
              demand_cost_origin = "origin", demand_cost_dest = "dest", demand_cost_name = "cost",
              supply_cost_origin = "origin", supply_cost_dest = "dest", supply_cost_name = "cost",
              weight_fn = None, normalize = False, noise = 'quiet'):
    """
    Calculation of the floating catchment accessibility
      ratio, from DataFrames with precomputed distances.
    This is accomplished through two calls of the `access.weighted_catchment` method.

    Parameters
    ----------

    demand_df          : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                         The origins dataframe, containing a location index and a total demand.
    supply_df          : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                         The origins dataframe, containing a location index and level of supply
    demand_cost_df     : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                         This dataframe contains a link between neighboring demand locations, and a cost between them.
    supply_cost_df     : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                         This dataframe contains a link between neighboring supply locations, and a cost between them.
    max_cost           : float
                         This is the maximum cost to consider in the weighted sum;
                           note that it applies _along with_ the weight function.
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
    if len(set(demand_df[demand_index]) - set(supply_cost_df[supply_cost_dest].unique())) != 0:
        warnings.warn("some tracts may be unaccounted for in supply_cost")
        

    #get a series of the total demand and another series of the total supply
    total_demand_series = weighted_catchment(demand_df, demand_cost_df, max_cost, 
                                          cost_source = demand_cost_origin, cost_dest = demand_cost_dest, cost_cost = demand_cost_name,
                                          loc_dest = demand_index, loc_dest_value = demand_name, 
                                          weight_fn = weight_fn)
    total_supply_series = weighted_catchment(supply_df, supply_cost_df, max_cost, 
                                          cost_source = supply_cost_origin, cost_dest = supply_cost_dest, cost_cost = supply_cost_name,
                                          loc_dest = supply_index, loc_dest_value = supply_name, 
                                          weight_fn = weight_fn)

    #calculate the base FCA series with total demand divided by total supply
    temp = total_supply_series.to_frame(name = 'supply').join(total_demand_series.to_frame(name = 'demand'), how = 'right').fillna(0)
    temp['FCA'] = temp['supply'] / temp['demand']
    base_FCA_series = temp['FCA']
    
    if noise != 'quiet':
        print (base_FCA_series[pd.isna(base_FCA_series)])
    
    if normalize:
        mean_access = ((base_FCA_series * demand_df[demand_name]).sum() / demand_df[demand_name].sum())
        base_FCA_series = base_FCA_series / mean_access

    return base_FCA_series