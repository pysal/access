import pandas as pd
import numpy as np
import geopandas as gpd
from .fca1 import weighted_catchment

def two_stage_fca(demand_df, supply_df, demand_cost_df, supply_cost_df, max_cost,
                  demand_index = "geoid", demand_name   = "demand",
                  supply_index = "geoid",   supply_name   = "supply",
                  demand_cost_origin = "origin", demand_cost_dest = "dest", demand_cost_name = "cost",
                  supply_cost_origin = "dest", supply_cost_dest = "origin", supply_cost_name = "cost",
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
    Returns
    -------
    access     : pandas.Series
                 A -- potentially-weighted -- two-stage access ratio.
    """
    
    #get a series of total demand then calculate the supply to total demand ratio for each location
    total_demand_series = weighted_catchment(demand_df, supply_cost_df, max_cost, 
                                          cost_source = supply_cost_origin, cost_dest = supply_cost_dest, cost_cost = supply_cost_name,
                                          loc_dest = demand_index, loc_dest_value = demand_name, 
                                          weight_fn = weight_fn)
    
    temp = supply_df.set_index(supply_index).join(total_demand_series.to_frame(name = 'demand'), how = 'right').fillna(0)
    temp['Rl'] = temp[supply_name] / temp['demand']
    supply_to_total_demand_frame = pd.DataFrame(data = {'Rl':temp['Rl']})
    
    supply_to_total_demand_frame.reset_index(level = 0, inplace = True)
    supply_to_total_demand_frame.rename({supply_cost_origin: supply_index, 'Rl': 'Rl'}, axis='columns', inplace = True)
    
    #sum, into a series, the supply to total demand ratios for each location
    two_stage_fca_series = weighted_catchment(supply_to_total_demand_frame, demand_cost_df, max_cost, 
                                          cost_source = demand_cost_origin, cost_dest = demand_cost_dest, cost_cost = demand_cost_name,
                                          loc_dest = supply_index, loc_dest_value = "Rl", 
                                          weight_fn = weight_fn)

    if normalize:
        mean_access = ((two_stage_fca_series * demand_df[demand_name]).sum() / demand_df[demand_name].sum())
        two_stage_fca_series = two_stage_fca_series / mean_access

    return two_stage_fca_series


