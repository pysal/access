__version__ = "1.0.0"
"""
:mod:`access` --- Accessibility Metrics
=================================================
"""

import pandas as pd
import warnings
import logging

try:
  import geopandas as gpd
  HAS_GEOPANDAS = True
except:
  HAS_GEOPANDAS = False

from . import fca
from . import raam
from . import weights
from . import helpers

access_log_stream = logging.StreamHandler()
access_log_format = logging.Formatter('%(name)s %(levelname)-8s :: %(message)s')
access_log_stream.setFormatter(access_log_format)

class access():
    """
    Spatial Access Class

    Parameters
    ----------
    demand_df            : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_ or `geopandas.GeoDataFrame <http://geopandas.org/reference/geopandas.GeoDataFrame.html>`_
                           The origins dataframe, containing a location index and, optionally, a level of demand and geometry.
    demand_index         : {bool, str}
                           boolean of True indicates that the locations are already on the df index; 
                             otherwise the argument is a string containing the name of the column of `demand_df` that holds the origin ID.
    demand_value         : str
                           is the name of the column of `demand` that holds the aggregate demand at a location.
    supply_df            : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_ or `geopandas.GeoDataFrame <http://geopandas.org/reference/geopandas.GeoDataFrame.html>`_
                           The origins dataframe, containing a location index and, optionally, level of supply and geometry.
    supply_index         : {bool, str}
                           boolean of True indicates that the locations are already on the df index; 
                             otherwise the argument is a string containing the name of the column of `supply_df` that holds the origin ID.
    supply_value         : {str, list}
                           is the name of the column of `supply` that holds the aggregate supply at a location, or a list of such columns.
    cost_df              : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                           This dataframe contains a link from demand to supply locations, and a cost between them.
    cost_origin          : str
                           The column name of the index locations -- this is what will be grouped by.
    cost_dest            : str
                           The column name of the neighborhing demand locations -- this is what goes in the groups.
    cost_name            : {str, list}
                           The column(s) name of the travel cost(s).
    neighbor_cost_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                           This dataframe contains a link from demand to neighbor locations, and a cost between them (running consumer to supplier).
    neighbor_cost_origin : str
                           The column name of the origin locations -- this is what will be grouped by.
    neighbor_cost_dest   : str
                           The column name of the destination locations -- this is what goes in the groups.
    neighbor_cost_name   : {str, list}
                           The column name(s) of the travel cost(s).

    Attributes
    ----------

    access               : pandas.DataFrame
                           All of the calculated access measures.
    access_metadata      : pandas.DataFrame
                           Lists currently-available measures of access.
    cost_metadata        : pandas.DataFrame
                           Describes each of the currently-available supply to demand costs.
    """


    def __init__(self, demand_df, demand_value, supply_df, supply_value,
                 demand_index = True, supply_index = True,
                 cost_df = None, cost_origin = None, cost_dest = None, cost_name = None,
                 neighbor_cost_df = None, neighbor_cost_origin = None, neighbor_cost_dest = None, neighbor_cost_name = None):

        """
        Initialize the class.

        Examples
        --------

        Import the base class and example data.

        >>> from access import access, examples as ex

        Inspect the example data:

        >>> ex.il_times.head()

        Using the example data, create an `access` object.

        >>> illinois_primary_care = \
                 access(demand_df = ex.il_pop,   demand_index = "geoid", demand_value = "pop",
                        supply_df = ex.il_doc,   supply_index = "geoid", 
                        supply_value = ["pc_physicians", "dentists"],
                        cost_df   = ex.il_times, cost_origin  = "origin", cost_dest = "dest")

        Attempt to calculate floating catchment area method:

        >>> illinois_primary_care.fca_ratio(max_cost = 60)
        TypeError: unsupported operand type(s) for +: 'int' and 'str'

        This failed, because we had not set a distance from users to their own neighbors.
        In the present case, `il_times` actually runs among 2010 Census Tracts, so we can use the same dataframe again,

        >>> illinois_primary_care.user_cost_neighbors(name = "cost", cost_df = ex.il_times, 
                                                      cost_origin = "origin", cost_dest = "dest")

        But we could have also have gotten a Euclidean distance for this.  First set the CRS to 3528, for Illinois (it already is).
        Note that this is "in place."

        >>> illinois_primary_care.to_crs(epsg = 3528)

        And now set the distances.

        >>> illinois_primary_care.euclidean_distance_neighbors(name = "euclidean")
          
        Calculate two-stage floating catchment method for all supply types, in a catchment of 60 minutes.

        >>> illinois_primary_care.two_stage_fca(max_cost = 60)
        {17031410900 : 0.1234, 17031836200 : 1.234, ... }
          
        Calculate RAAM with a tau parameter of 30 minutes, for every supply type (doctors and dentists).

        >>> illinois_primary_care.raam(name = "raam_tau30", tau = 30)
        {17031410900 : 0.1234, 17031836200 : 1.234, ... }

        Same thing, but with tau of 60 minutes.

        >>> illinois_primary_care.raam(name = "raam_tau60", tau = 60)
        {17031410900 : 0.1234, 17031836200 : 1.234, ... }

        Now doctors only, at 90 minutes:

        >>> illinois_primary_care.raam(supply = "pc_physicians", name = "raam_tau60", tau = 90)
        {17031410900 : 0.1234, 17031836200 : 1.234, ... }

        View all of the calculated types of access.

        >>> illinois_primary_care.access_metadata

        Create a weighted sum of multiple access types, from a dictionary.
        Note that this is based on _normalized_ access values.

        >>> illinois_primary_care.score({"pc_physicians_raam_tau60" : 1, "dentists_raam_tau30" : 0.2})
        """

        self.log = logging.getLogger("access")
        self.log.addHandler(access_log_stream)
        self.log.setLevel(logging.INFO)
        self.log.propagate = False

        ### First all the dummy checks...

        if demand_index is not True and demand_index not in demand_df.columns:
            raise ValueError("demand_index must either be True -- or it must be a column of demand_df")

        if demand_value not in demand_df.columns:
            raise ValueError("demand_value must either be True -- or it must be a column of demand_df")

        if supply_index is not True and supply_index not in supply_df.columns:
            raise ValueError("supply_index must either be True -- or it must be a column of supply_df")

        if type(supply_value) is str and supply_value not in supply_df.columns:
            raise ValueError("supply_value must be a column of supply_df")

        if type(supply_value) is list:
            if any([sv not in supply_df.columns for sv in supply_value]):
                raise ValueError("supply_value must be columns of supply_df")

        if cost_df is not None:

          if cost_origin not in cost_df.columns:
              raise ValueError("cost_origin must be a column of cost_df")

          if cost_dest   not in cost_df.columns:
              raise ValueError("cost_dest must be a column of cost_df")

          if type(cost_name) is str and cost_name not in cost_df.columns:
              raise ValueError("cost_name must be a column of cost_df")

          if type(cost_name) is list:
              if any([cn not in cost_df.columns for cn in cost_name]):
                  raise ValueError("cost_name must be columns of cost_df")

        if neighbor_cost_df is not None:

          if neighbor_cost_origin not in neighbor_cost_df.columns:
              raise ValueError("neighbor_cost_origin must be a column of neighbor_cost_df")

          if neighbor_cost_dest   not in neighbor_cost_df.columns:
              raise ValueError("neighbor_cost_dest must be a column of neighbor_cost_df")

          if type(neighbor_cost_name) is str and neighbor_cost_name not in neighbor_cost_df.columns:
              raise ValueError("neighbor_cost_name must be a column of cost_df")

          if type(neighbor_cost_name) is list:
              if any([cn not in neighbor_cost_df.columns for cn in neighbor_cost_name]):
                  raise ValueError("neighbor_cost_names must be columns of cost_df")


        ### Now load the demand DFs.

        self.demand_df    = demand_df
        self.demand_value = demand_value
        if demand_index is not True: 
            self.demand_df.set_index(demand_index, inplace = True)
    
        ### And now the supply DFs.

        self.supply_df    = supply_df

        if type(supply_value) is str:
            self.supply_types = [supply_value]
        elif type(supply_value) is list:
            self.supply_types = supply_value
        else:
            raise ValueError("supply_value must be string or list of strings.")

        if supply_index is not True: 
            self.supply_df.set_index(supply_index, inplace = True)

        if cost_df is not None:
          
            self.cost_df     = cost_df
            self.cost_origin = cost_origin
            self.cost_dest   = cost_dest

            if type(cost_name) is str:
                self.cost_names = [cost_name]

            elif type(cost_name) is list:
                self.cost_names = cost_name

            else:
                raise ValueError("cost_name must be string or list of strings.")

            self.default_cost = self.cost_names[0]
        
        else:
            self.cost_df = pd.DataFrame(columns = ['origin', 'dest'])
            self.cost_origin = 'origin'
            self.cost_dest = 'dest'
            self.cost_names = []

        if neighbor_cost_df is not None:
          
            self.neighbor_cost_df     = neighbor_cost_df
            self.neighbor_cost_origin = neighbor_cost_origin
            self.neighbor_cost_dest   = neighbor_cost_dest
            self.neighbor_cost_name   = neighbor_cost_name

            if type(neighbor_cost_name) is str:
                self.neighbor_cost_names = [neighbor_cost_name]

            elif type(neighbor_cost_name) is list:
                self.neighbor_cost_names = neighbor_cost_name

            else:
                raise ValueError("neighbor_cost_name must be string or list of strings.")

            self.neighbor_default_cost = self.neighbor_cost_names[0]

        else:
            self.neighbor_cost_df = pd.DataFrame(columns = ['origin', 'dest'])
            self.neighbor_cost_origin = 'origin'
            self.neighbor_cost_dest = 'dest'
            self.neighbor_cost_names = []
       
        self.access_df = self.demand_df[[self.demand_value]].sort_index()

        self.access = pd.DataFrame(index = self.supply_df.index)

        self.access_metadata = pd.DataFrame(columns = ["name", "distance", "function", "descriptor"])
        self.cost_metadata   = pd.DataFrame(columns = ["name", "type", "descriptor"])

        return


    def weighted_catchment(self, name = "catchment", supply_cost = None, supply_values = None,
                           weight_fn = None, max_cost = None, normalize = False):
        """
        Calculate the catchment area (buffer) aggregate access score.

        Parameters
        ----------
        name                : str 
                              Column name for access values
        supply_cost         : str 
                              Name of supply cost value column in supply_df
        supply_values       : {str, list}
                              Name(s) of supply values in supply_df
        weight_fn           : function
                              function to apply to the cost to reach the supply.
                              In this way, you could run, e.g., a gravity function.
                              (Be careful of course of values as distances go to 0!)
        max_cost            : float
                              Cutoff of cost values     
        normalize           : bool 
                              If True, return normalized access values; otherwise, return raw access values                                       
        Returns
        -------

        access              : pandas Series
                              Accessibility score for origin locations.

        Examples
        --------

        Create an access object, as detailed in __init__.py

        >>> illinois_primary_care = access(<...>)

        Call the floating catchment area with max_cost only

        >>> gravity = weights.gravity(scale = 60, alpha = -1)
        >>> illinois_primary_care.weighted_catchment(weight_fn = gravity)

        """

        supply_cost   = helpers.sanitize_supply_cost(self, supply_cost, name)
        supply_values = helpers.sanitize_supplies   (self, supply_values)

        for s in supply_values:

            # Bryan consistently flipped origin and destination in this one -- very confusing.
            series = fca.weighted_catchment(loc_df = self.supply_df, loc_index = True, loc_value = s,
                                            cost_df = self.cost_df, cost_source = self.cost_dest, cost_dest = self.cost_origin,
                                            weight_fn = weight_fn, max_cost = max_cost)

            series.name = name + "_" + s
            if series.name in self.access_df.columns:
                self.log.info("Overwriting {}.".format(series.name))
                self.access_df.drop(series.name, axis = 1, inplace = True)

            # store the raw, un-normalized access values 
            self.access_df = self.access_df.join(series)
        
        if normalize:

            columns = [name + "_" + s for s in supply_values]
            return helpers.normalized_access(self, columns)

        return self.access_df.filter(regex = "^" + name, axis = 1)


    def fca_ratio(self, name = "fca", demand_cost = None, supply_cost = None, 
                  supply_values = None, max_cost = None, normalize = False):
        """
        Calculate the floating catchment area (buffer) ratio access score.

        Parameters
        ----------
        name                : str 
                              Column name for access values
        demand_cost         : str 
                              Name of demand cost value column in demand_df                     
        supply_cost         : str 
                              Name of supply cost value column in supply_df
        supply_values       : {str, list}
                              Name(s) of supply values in supply_df
        max_cost            : float
                              Cutoff of cost values     
        normalize           : bool 
                              If True, return normalized access values; otherwise, return raw access values                                       
        Returns
        -------

        access              : pandas Series
                              Accessibility score for origin locations.

        Examples
        --------

        Create an access object, as detailed in __init__.py

        >>> illinois_primary_care = access(<...>)

        This method will utilize the parameters passed into the access object at time of instantiation.
        Any calls of floating catchment area need only provide method-specific parameters.

        Call the floating catchment area with max_cost only

        >>> illinois_primary_care.fca_ratio(max_cost = 30)

        """

        supply_cost   = helpers.sanitize_supply_cost(self, supply_cost, name)
        demand_cost   = helpers.sanitize_demand_cost(self, demand_cost, name)
        supply_values = helpers.sanitize_supplies   (self, supply_values)

        for s in supply_values:

            series = fca.fca_ratio(demand_df = self.demand_df, 
                                                      demand_name = self.demand_value,
                                                      supply_df = self.supply_df,             
                                                      supply_name = s,
                                                      demand_cost_df = self.neighbor_cost_df, 
                                                      supply_cost_df = self.cost_df,          
                                                      demand_cost_origin = self.neighbor_cost_origin, demand_cost_dest = self.neighbor_cost_dest, demand_cost_name = demand_cost,
                                                      supply_cost_origin = self.cost_origin,          supply_cost_dest = self.cost_dest,          supply_cost_name = supply_cost,
                                                      max_cost = max_cost, normalize = normalize)

            series.name = name + "_" + s
            if series.name in self.access_df.columns:
                self.log.info("Overwriting {}.".format(series.name))
                self.access_df.drop(series.name, axis = 1, inplace = True)

            # store the raw, un-normalized access values 
            self.access_df = self.access_df.join(series)
        
        if normalize:

            columns = [name + "_" + s for s in supply_values]
            return helpers.normalized_access(self, columns)

        return self.access_df.filter(regex = "^" + name, axis = 1)


    def raam(self, name = "raam", cost = None, supply_values = None, normalize = False,
             tau = 60, rho = None, 
             max_cycles = 150, initial_step = 0.2, half_life = 50, min_step = 0.005, 
             verbose = False): 
        """Calculate the rational agent access model. :cite:`2019_saxon_snow_raam`

        Parameters
        ----------
        name                : str 
                              Column name for access values
        cost                : str 
                              Name of cost variable, for reaching supply sites.
        supply_values       : {str, list}
                              Name(s) of supply values in supply_df
        normalize           : bool 
                              If True, return normalized access values; otherwise, return raw access values                               tau                 : float
                              tau parameter (travel time scale)
        rho                 : float 
                              rho parameter (congestion cost scale)
        max_cycles          : int
                              How many cycles to run the RAAM optimization for.
        initial_step        : {int, float}
                              If an float < 1, it is the proportion of a demand site that can shift, in the first cycle.
                              If it is an integer, it is simply a limit on the total number.
        half_life           : int
                              How many cycles does it take to halve the move rate?
        min_step            : {int, float}
                              This is the minimum value, to which the moving fraction converges.
        verbose             : bool
                              Print some information as the optimization proceeds.

        Returns
        -------

        access              : pandas Series
                              Accessibility score for origin locations.

        Examples
        --------

        Call the RAAM, seting the tau parameter to the default value of 60.

        >>> illinois_primary_care.raam(tau = 60)

        """

        cost          = helpers.sanitize_supply_cost(self, cost, name)
        supply_values = helpers.sanitize_supplies   (self, supply_values)

        for s in supply_values:

            raam_costs = raam.raam(demand_df = self.demand_df, supply_df = self.supply_df, cost_df = self.cost_df,
                                   demand_name = self.demand_value,
                                   supply_name = s,
                                   cost_origin = self.cost_origin, cost_dest = self.cost_dest, cost_name = cost,
                                   max_cycles = max_cycles, tau = tau, verbose = verbose)

            raam_costs.name = name + "_" + s
            if raam_costs.name in self.access_df.columns:
                self.log.info("Overwriting {}.".format(raam_costs.name))
                self.access_df.drop(raam_costs.name, axis = 1, inplace = True)
            
            # store the raw, un-normalized access values 
            self.access_df = self.access_df.join(raam_costs)
        
        if normalize:

            columns = [name + "_" + s for s in supply_values]
            return helpers.normalized_access(self, columns)


        return self.access_df.filter(regex = "^" + name, axis = 1)

        

    def two_stage_fca(self, name = "2sfca", cost = None, max_cost = None, 
                      supply_values = None, weight_fn = None, normalize = False):
        """Calculate the two-stage floating catchment area access score.

        Parameters
        ----------
        name                : str 
                              Column name for access values
        cost                : str 
                              Name of cost value column in cost_df (supply-side)
        supply_values       : {str, list}
                              supply type or types.
        max_cost            : float
                              Cutoff of cost values
        weight_fn           : function 
                              Weight to be applied to access values                                       
        normalize           : bool 
                              If True, return normalized access values; otherwise, return raw access values                                                            

        Returns
        -------

        access              : pandas Series
                              Accessibility score for origin locations.

        """

        if cost is None:

            cost = self.default_cost
            if len(self.cost_names) > 1:
                self.log.info("Using default cost, {}, for {}.".format(cost, name))

        if cost not in self.cost_names:

            raise ValueError("{} not an available cost.".format(cost))

        if type(supply_values) is str:
            supply_values = [supply_values]
        if supply_values is None:
            supply_values = self.supply_types

        for s in supply_values:

            series = fca.two_stage_fca(demand_df = self.demand_df, 
                                       demand_name = self.demand_value,
                                       supply_df = self.supply_df, 
                                       supply_name = s,
                                       cost_df = self.cost_df,    
                                       cost_origin = self.cost_origin, cost_dest = self.cost_dest, cost_name = cost,
                                       max_cost = max_cost, weight_fn = weight_fn, normalize = normalize)

            series.name = name + "_" + s
            if series.name in self.access_df.columns:
                self.log.info("Overwriting {}.".format(series.name))
                self.access_df.drop(series.name, axis = 1, inplace = True)

            self.access_df = self.access_df.join(series)
        
        if normalize:

            columns = [name + "_" + s for s in supply_values]
            return helpers.normalized_access(self, columns)

        return self.access_df.filter(regex = "^" + name, axis = 1)

    def enhanced_two_stage_fca(self, name = "e2sfca", cost = None, supply_values = None, 
                               max_cost = None, weight_fn = None, normalize = False):
        """Calculate the enhanced two-stage floating catchment area access score.

        Parameters
        ----------
        name                : str 
                              Column name for access values
        cost                : str 
                              Name of cost value column in cost_df (supply-side)
        max_cost            : float
                              Cutoff of cost values
        supply_values       : {str, list}
                              supply type or types.
        weight_fn           : function 
                              Weight to be applied to access values                                       
        normalize           : bool 
                              If True, return normalized access values; otherwise, return raw access values                                                            

        Returns
        -------

        access              : pandas Series
                              Accessibility score for origin locations.

        """

        if weight_fn is None: weight_fn = weights.step_fn({10 : 1, 20 : 0.68, 30 : 0.22})

        return self.two_stage_fca(name, cost, max_cost, supply_values, weight_fn, normalize)


    def three_stage_fca(self, name = "3sfca", cost = None, supply_values = None, max_cost = None, weight_fn = None, normalize = False):
        """Calculate the three-stage floating catchment area access score.
        Parameters
        ----------
        name                : str 
                              Column name for access values
        cost                : str 
                              Name of cost value column in cost_df (supply-side)
        max_cost            : float
                              Cutoff of cost values
        weight_fn           : function 
                              Weight to be applied to access values                                       
        normalize           : bool 
                              If True, return normalized access values; otherwise, return raw access values                                                            
        Returns
        -------

        access              : pandas Series
                              Accessibility score for origin locations.

        """

        if weight_fn is None:
            weight_fn = weights.step_fn({10 : 0.962, 20 : 0.704, 30 : 0.377, 60 : 0.042})

        cost          = helpers.sanitize_supply_cost(self, cost, name)
        supply_values = helpers.sanitize_supplies   (self, supply_values)

        for s in supply_values:

            series = fca.three_stage_fca(demand_df = self.demand_df, 
                                                      demand_name = self.demand_value,
                                                      supply_df = self.supply_df, 
                                                      supply_name = s,
                                                      cost_df = self.cost_df,    
                                                      cost_origin = self.cost_origin, cost_dest = self.cost_dest, cost_name = cost,
                                                      max_cost = max_cost, weight_fn = weight_fn, normalize = normalize)

            series.name = name + "_" + s
            if series.name in self.access_df.columns:
                self.log.info("Overwriting {}.".format(series.name))
                self.access_df.drop(series.name, axis = 1, inplace = True)

            # store the raw, un-normalized access values 
            self.access_df = self.access_df.join(series)
        
        if normalize:

            columns = [name + "_" + s for s in supply_values]
            return helpers.normalized_access(self, columns)
        
        return self.access_df.filter(regex = "^" + name, axis = 1)

    @property
    def norm_access_df(self):
        for column in self.access_df.columns.difference([self.demand_value]):
            mean_access = (self.access_df[column] * self.access_df[self.demand_value]).sum() / self.access_df[self.demand_value].sum()
            self.access_df[column] /= mean_access
        return self.access_df[self.access_df.columns.difference([self.demand_value])]

    def score(self, col_dict, name = "score"):
        """Weighted aggregate of multiple already-calculated, normalized access components.

        Parameters
        ----------
        name                : str 
                              Column name for access values
        col_dict            : dict
                              Column names (keys) and weights.
        Returns
        -------

        access              : pandas Series
                              Single, aggregate score for origin locations.

        Examples
        --------

        Aggregate RAAM for doctors and dentists, weighting doctors more heavily.

        >>> A.score(name = "raam_combo", col_dict = {"raam_doc" : 0.8, "raam_dentist" : 0.2});
        
        """


        for v in col_dict:
            if v not in self.access_df.columns:
                raise ValueError("{} is not a calculated access value".format(v))

        weights = pd.Series(col_dict)

        weighted_score = self.norm_access_df[weights.index].dot(weights)

        weighted_score.name = name 
        if weighted_score.name in self.access_df.columns:
            self.log.info("Overwriting {}.".format(weighted_score.name))
            self.access_df.drop(weighted_score.name, axis = 1, inplace = True)

        self.access_df = self.access_df.join(weighted_score)

        return weighted_score


    def set_cost(self, new_cost):
        """Change the default cost measure."""

        if new_cost in self.cost_names:
            self.default_cost = new_cost

        else:
            raise ValueError("Tried to set cost not available in cost df")

    def set_neighbor_cost(self, new_cost):
        """Change the default cost measure."""

        if new_cost in self.neighbor_cost_names:
            self.neighbor_default_cost = new_cost

        else:
            raise ValueError("Tried to set cost not available in cost df")


    def user_cost(self, new_cost_df, origin, destination, name):
        """Create a user cost, from demand to supply locations.

        Parameters
        ----------
        new_cost_df         : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                              Holds the new cost....
        cost                : str
                              Name of the new cost variable in new_cost_df
        origin              : str
                              Name of the new origin variable in new_cost_df
        destination         : str
                              Name of the new destination variable in new_cost_df

        """

        # Add it to the list of costs.
        self.neighbor_cost_df = self.neighbor_cost_df.merge(new_cost[[origin, destination, name]], how = 'outer', 
                                                            left_on = [self.neighbor_cost_origin,
                                                                       self.neighbor_cost_destination], 
                                                            right_on = [origin, destination])
        self.neighbor_cost_names.append(name)


    def user_cost_neighbors(self, new_cost_df, origin, destination, name):
        """Create a user cost, from supply locations to other supply locations.

        Parameters
        ----------
        new_cost_df         : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                              Holds the new cost....
        cost                : str
                              Name of the new cost variable in new_cost_df
        origin              : str
                              Name of the new origin variable in new_cost_df
        destination         : str
                              Name of the new destination variable in new_cost_df
        """

        # Add it to the list of costs.
        self.cost_df = self.neighbor_cost_df.merge(new_cost_df[[origin, destination, name]], how = 'outer', 
                                                   left_on = [self.cost_origin, self.cost_destination], 
                                                   right_on = [origin, destination])
        self.cost_names.append(name)

    def euclidean_distance(self, name = "euclidean", threshold = 0, centroid_o = False, centroid_d = False):
        """Calculate the Euclidean distance from demand to supply locations.
           This is simply the geopandas `distance` function.  
           The user is responsible for putting the geometries into an appropriate reference system.

        Parameters
        ----------
        name                : str 
                              Column name for euclidean distances
        threshold           : int 
                              Buffer threshold for non-point geometries, AKA max_distance                                
        centroid_o          : bool 
                              If True, convert geometries of demand_df (origins) to centroids; otherwise, no change 
        centroid_d          : bool 
                              If True, convert geometries of supply_df (destinations) to centroids; otherwise, no change
        """

        if not HAS_GEOPANDAS:
          raise ModuleNotFoundError("System does not have geopandas installed.  Cannot calculate distances.")


        # TO-DO: check for unprojected geometries
        
        
        # Continue if the dataframes are geodataframes, else throw an error
        if type(self.demand_df) is not gpd.GeoDataFrame:
            raise ValueError("Cannot calculate euclidean distance without a geometry of supply side")
            
        if type(self.supply_df) is not gpd.GeoDataFrame:
            raise ValueError("Cannot calculate euclidean distance without a geometry of supply side")

        # Reset the index so that the geoids are accessible 
        df1 = self.demand_df.rename_axis('origin').reset_index()
        df2 = self.supply_df.rename_axis('dest').reset_index()
        
        # Convert to centroids if so-specified
        if centroid_o: df1.set_geometry(df1.centroid, inplace = True)
        if centroid_d: df2.set_geometry(df2.centroid, inplace = True)

        # Calculate the distances.
        if ((df1.geom_type == "Point").all() & (df2.geom_type == "Point").all()):
            # If both geometries are point types, merge on a temporary dummy column
            df1["temp"] = 1
            df2["temp"] = 1
            df1and2 = df1[["temp", "geometry","origin"]].merge(df2[["temp", "geometry","dest"]].rename(columns = {'geometry':'geomb'}))
            df1and2.drop("temp", inplace = True, axis = 1)
            df1and2[name] = df1and2.distance(df1and2.set_geometry("geomb"))
        else:
            # Execute an sjoin for non-point geometries, based upon a buffer zone
            df1and2 = gpd.sjoin(df1, df2.rename(columns = {'geometry':'geomb'}).set_geometry(df2.buffer(threshold)))
            df1and2[name] = df1and2.distance(df1and2.set_geometry("geomb"))
       
        # Add it to the cost df.
        df1and2 = df1and2[df1and2[name] < threshold]
        self.cost_df = self.cost_df.merge(df1and2[[name,'origin','dest']], how = 'outer', left_on = [self.cost_origin, self.cost_dest], right_on = ['origin', 'dest'])
        # Add it to the list of costs.
        self.cost_names.append(name)
        # Set the default cost if it does not exist
        if not hasattr(self, 'default_cost'):
            self.default_cost = name

    def euclidean_distance_neighbors(self, name = "euclidean", threshold = 0, centroid = False):
        """Calculate the Euclidean distance among demand locations.

        Parameters
        ----------
        name                : str 
                              Column name for euclidean distances neighbors
        threshold           : int 
                              Buffer threshold for non-point geometries, AKA max_distance                                
        centroid          : bool 
                              If True, convert geometries to centroids; otherwise, no change 
        """

        # TO-DO: check for unprojected geometries

        
        # Continue if the dataframes are geodataframes, else throw an error
        if type(self.demand_df) is not gpd.GeoDataFrame:
            raise ValueError("Cannot calculate euclidean distance without a geometry of supply side")

        # Reset the index so that the geoids are accessible 
        df1 = self.demand_df.rename_axis('origin').reset_index()
        df2 = self.demand_df.rename_axis('dest').reset_index()

        # Convert to centroids if so-specified
        if centroid:
            df1.set_geometry(df1.centroid, inplace = True)
            df2.set_geometry(df2.centroid, inplace = True)

        # Calculate the distances.
        if ((df1.geom_type == "Point").all() & (df2.geom_type == "Point").all()):
            # If both geometries are point types, merge on a temporary dummy column
            df1["temp"] = 1
            df2["temp"] = 1
            df1and2 = df1[["temp", "geometry","origin"]].merge(df2[["temp", "geometry","dest"]].rename(columns = {'geometry':'geomb'}))
            df1and2.drop("temp", inplace = True, axis = 1)
            df1and2[name] = df1and2.distance(df1and2.set_geometry("geomb"))
        else:
            # Execute an sjoin for non-point geometries, based upon a buffer zone
            df1and2 = gpd.sjoin(df1, df2.rename(columns = {'geometry':'geomb'}).set_geometry(df2.buffer(threshold)))
            df1and2[name] = df1and2.distance(df1and2.set_geometry("geomb"))
       
        # Add it to the cost df.
        df1and2 = df1and2[df1and2[name] < threshold]
        self.neighbor_cost_df = self.neighbor_cost_df.merge(df1and2[[name,'origin','dest']], how = 'outer', left_on = [self.neighbor_cost_origin, self.neighbor_cost_dest], right_on = ['origin', 'dest'])
        # Add it to the list of costs.
        self.neighbor_cost_names.append(name)
        # Set the default cost if it does not exist
        if not hasattr(self, 'neighbor_default_cost'):
            self.neighbor_default_cost = name


