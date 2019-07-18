import pandas as pd
import numpy as np
import geopandas as gpd
from .fca1 import weighted_catchment

def two_stage_fca(demand_df, supply_df, cost_df, max_cost,
                  demand_index = "geoid", demand_name   = "demand",
                  supply_index = "geoid",   supply_name   = "supply",
                  cost_origin = "dest", cost_dest = "origin", cost_name = "cost",
                  weight_fn = None, normalize = False):
    """
    Calculation of the floating catchment accessibility
      ratio, from DataFrames with precomputed distances.
    This is accomplished through a single call of the `access.weighted_catchment` method,
      to retrieve the patients using each provider.
    The ratio of providers per patient is then calculated at each care destination,
      and that ratio is weighted and summed at each corresponding demand site.
    This is based on the original paper by X,
      as extended by Y and Z.

    Parameters
    ----------

    demand_df     : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                    The origins dataframe, containing a location index and a total demand.
    demand_origin : str
                    is the name of the column of `demand_df` that holds the origin ID.
    demand_value  : str
                    is the name of the column of `demand_df` that holds the aggregate demand at a location.
    supply_df     : [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
                    The origins dataframe, containing a location index and level of supply
    supply_origin : str
                    is the name of the column of `supply_df` that holds the origin ID.
    supply_value  : str
                    is the name of the column of `supply_df` that holds the aggregate demand at a location.
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
    normalize  : bool
                  True to normalize the FCA series, by default False.
    Returns
    -------
    access     : pandas.Series
                 A -- potentially-weighted -- two-stage access ratio.
    """
    
    #weigh the times using the given parameter
    if weight_fn:
        weights_column = cost_df[cost_name].apply(weight_fn)*cost_df[cost_name] 
        cost_df = cost_df.drop([cost_name], axis = 1)
        cost_df[cost_name] = weights_column
        
    #get a series of total demand then calculate the supply to total demand ratio for each location
    total_demand_series = weighted_catchment(demand_df, cost_df, max_cost, 
                                          cost_source = cost_origin, cost_dest = cost_dest, cost_cost = cost_name,
                                          loc_dest = demand_index, loc_dest_value = demand_name, 
                                          weight_fn = weight_fn)
    
    temp = supply_df.set_index(supply_index).join(total_demand_series.to_frame(name = 'demand'), how = 'right').fillna(0)
    temp['Rl'] = temp[supply_name] / temp['demand']
    supply_to_total_demand_frame = pd.DataFrame(data = {'Rl':temp['Rl']})
    
    supply_to_total_demand_frame.reset_index(level = 0, inplace = True)
    supply_to_total_demand_frame.rename({cost_origin: supply_index, 'Rl': 'Rl'}, axis='columns', inplace = True)
    
    #sum, into a series, the supply to total demand ratios for each location
    two_stage_fca_series = weighted_catchment(supply_to_total_demand_frame, cost_df, max_cost, 
                                          cost_source = cost_dest, cost_dest = cost_origin, cost_cost = cost_name,
                                          loc_dest = supply_index, loc_dest_value = "Rl", 
                                          weight_fn = weight_fn)
    
    if normalize:
        mean_access = ((two_stage_fca_series * demand_df[demand_name]).sum() / demand_df[demand_name].sum())
        two_stage_fca_series = two_stage_fca_series / mean_access
    return two_stage_fca_series


