__version__ = "1.0.0"
"""
:mod:`access` --- Accessibility Metrics
=================================================
"""

import pandas
import geopandas
import warnings

from . import fca
from . import raam

class access():
    """
    Spatial Access Class

    Parameters
    ----------
    demand_df            : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_ or `geopandas.GeoDataFrame <http://geopandas.org/reference/geopandas.GeoDataFrame.html>`_
                           The origins dataframe, containing a location index and, optionally, a level of demand and geometry.
    demand_index         : str
                           is the name of the column of `demand` that holds the origin ID.
    demand_value         : str
                           is the name of the column of `demand` that holds the aggregate demand at a location.
    supply_df            : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_ or `geopandas.GeoDataFrame <http://geopandas.org/reference/geopandas.GeoDataFrame.html>`_
                           The origins dataframe, containing a location index and, optionally, level of supply and geometry.
    supply_index         : str
                           is the name of the column of `supply` that holds the origin ID.
    supply_value         : {str, list}
                           is the name of the column of `supply` that holds the aggregate supply at a location, or a list of such columns.
    cost_df              : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                           This dataframe contains a link from demand to supply locations, and a cost between them.
    cost_origin          : str
                           The column name of the index locations -- this is what will be grouped by.
    cost_dest            : str
                           The column name of the neighborhing demand locations -- this is what goes in the groups.
    cost_name            : str
                           The column name of the travel cost.
    neighbor_cost_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                           This dataframe contains a link from demand to neighbor locations, and a cost between them (running consumer to supplier).
    neighbor_cost_origin : str
                           The column name of the origin locations -- this is what will be grouped by.
    neighbor_cost_dest   : str
                           The column name of the destination locations -- this is what goes in the groups.
    neighbor_cost_name   : str
                           The column name of the travel cost.

    Attributes
    ----------

    access               : pandas.DataFrame
                           All of the calculated access measures.
    access_metadata      : pandas.DataFrame
                           Lists currently-available measures of access.
    cost_metadata        : pandas.DataFrame
                           Describes each of the currently-available supply to demand costs.
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

        >>> illinois_primary_care.score({"pc_physicians_raam_tau60" : 1, "dentists_raam_tau30" : 0.2})
        """

        ### First all the dummy checks...

        if demand_index is not True and demand_index not in demand_df.columns:
            raise ValueError("demand_index must either be True -- or it must be a column of demand_df")

        if demand_value not in demand_df.columns:
            raise ValueError("demand_value must either be True -- or it must be a column of demand_df")

        if supply_index is not True and supply_index not in supply_df.columns:
            raise ValueError("supply_index must either be True -- or it must be a column of supply_df")

        if supply_value not in supply_df.columns:
            raise ValueError("supply_value must either be True -- or it must be a column of supply_df")

        if cost_df is not None:

          if cost_origin not in cost_df.columns:
              raise ValueError("cost_origin must be a column of cost_df")

          if cost_dest   not in cost_df.columns:
              raise ValueError("cost_dest must be a column of cost_df")

          if cost_name   not in cost_df.columns:
              raise ValueError("cost_name must be a column of cost_df")

        if neighbor_cost_df is not None:

          if neighbor_cost_origin not in neighbor_cost_df.columns:
              raise ValueError("neighbor_cost_origin must be a column of neighbor_cost_df")

          if neighbor_cost_dest   not in neighbor_cost_df.columns:
              raise ValueError("neighbor_cost_dest must be a column of neighbor_cost_df")

          if neighbor_cost_name   not in neighbor_cost_df.columns:
              raise ValueError("neighbor_cost_name must be a column of neighbor_cost_df")


        ### Now load the demand DFs.

        self.demand_df    = demand_df
        self.demand_value = demand_value
        if demand_index is not True: 
            self.demand_df.set_index(demand_index)
    
        ### And now the supply DFs.

        self.supply_df    = supply_df
        self.supply_value = supply_value
        if supply_index is not True: 
            self.supply_df.set_index(supply_index)


        return

    def fca_ratio(self, name = "fca", cost = None, max_cost = None):
        """
        Calculate the floating catchment area (buffer) access score.

        Parameters
        ----------
        name                : str 
                              Cutoff of cost values
        max_cost            : float
                              Cutoff of cost values

        Returns
        -------

        access              : pandas Series
                              Accessibility score for origin locations.

        """

        if cost is None:

            cost = self.default_cost
            warnings.warn("deprecated", Warning)

        for s in self.supply_types:

            if "{}_{}.".format(name, s) in demand_df.columns:
                warnings.warn("Overwriting {}_{}.".format(name, s), Warning)
            
            demand_df[name + "_" + s] = fca.fca_ratio(demand_df = self.demand_df, 
                                                      supply_df = self.supply_df, supply_name = s,
                                                      demand_cost_df = self.neighbor_cost_df,
                                                      supply_cost_df = self.cost_df,
                                                      max_cost = max_cost)
        
        return fca.fca()


    def raam(self, tau = 1, cost = None): 
        """Calculate the rational agent access model cost.
        """

        if cost is None:
            cost = self.default_cost

    def two_stage_fca():
        """Calculate the two-stage floating catchment area access score."""
        pass

    def three_stage_fca():
        """Calculate the three-stage floating catchment area access score."""
        pass

    def score():
        """Weighted aggregate of multiple (already-calculated) access components."""
        pass

    def user_cost():
        """Create a user cost, from demand to supply locations."""
        pass

    def user_cost_neighbors():
        """Create a user cost, from supply locations to other supply locations."""
        pass

    def euclidean_distance():
        """Calculate the Euclidean distance from demand to supply locations.
           This is simply the geopandas `distance` function.  
           The user is responsible for putting the geometries into an appropriate reference system.
        """
        pass

    def euclidean_distance_neighbors():
        """Calculate the Euclidean distance among demand locations."""
        pass


