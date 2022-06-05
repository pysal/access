import pandas as pd
import requests
import warnings
import logging

from . import fca
from . import raam
from . import weights
from . import helpers
from .datasets import Datasets

access_log_stream = logging.StreamHandler()
access_log_format = logging.Formatter("%(name)s %(levelname)-8s :: %(message)s")
access_log_stream.setFormatter(access_log_format)


class Access:
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

    Access               : pandas.DataFrame
                           All of the calculated access measures.
    access_metadata      : pandas.DataFrame
                           Lists currently-available measures of access.
    cost_metadata        : pandas.DataFrame
                           Describes each of the currently-available supply to demand costs.
    """

    logger_initialized = False

    def __init__(
        self,
        demand_df,
        demand_value,
        supply_df,
        supply_value=False,
        demand_index=True,
        supply_index=True,
        cost_df=None,
        cost_origin=None,
        cost_dest=None,
        cost_name=None,
        neighbor_cost_df=None,
        neighbor_cost_origin=None,
        neighbor_cost_dest=None,
        neighbor_cost_name=None,
    ):

        """
        Initialize the class.

        Examples
        --------

        Import the base `Access` class and `Datasets`.

        >>> from access import Access, Datasets

        Load each of the example datasets:

        >>> chi_docs_dents   = Datasets.load_data('chi_doc')
        >>> chi_population   = Datasets.load_data('chi_pop')
        >>> chi_travel_costs = Datasets.load_data('chi_times')

        >>> chi_docs_dents.head()
                 geoid  doc  dentist
        0  17031010100    1        1
        1  17031010201    0        1
        2  17031010202    4        1
        3  17031010300    4        1
        4  17031010400    0        2

        >>> chi_population.head()
                 geoid   pop
        0  17031010100  4854
        1  17031010201  6450
        2  17031010202  2818
        3  17031010300  6236
        4  17031010400  5042

        >>> chi_travel_costs.head()
                origin         dest   cost
        0  17093890101  17031010100  91.20
        1  17093890101  17031010201  92.82
        2  17093890101  17031010202  92.95
        3  17093890101  17031010300  89.40
        4  17093890101  17031010400  84.97

        Using the example data, create an `Access` object.

        >>> chicago_primary_care = Access(demand_df = chi_population, demand_index = "geoid",
                                          demand_value = "pop",
                                          supply_df = chi_docs_dents, supply_index = "geoid",
                                          supply_value = ["doc", "dentist"],
                                          cost_df = chi_travel_costs, cost_origin  = "origin",
                                          cost_dest = "destination", cost_name = "cost")
        """
        self.log = logging.getLogger("access")

        if not Access.logger_initialized:
            self.log.addHandler(access_log_stream)
            self.log.setLevel(logging.INFO)
            self.log.propagate = False
            Access.logger_initialized = True

        self.supply_value_provided = True

        ### First all the dummy checks...

        if demand_index is not True and demand_index not in demand_df.columns:
            raise ValueError(
                "demand_index must either be True -- or it must be a column of demand_df"
            )

        if demand_value not in demand_df.columns:
            raise ValueError(
                "demand_value must either be True -- or it must be a column of demand_df"
            )

        if supply_index is not True and supply_index not in supply_df.columns:
            raise ValueError(
                "supply_index must either be True -- or it must be a column of supply_df"
            )

        if type(supply_value) is str and supply_value not in supply_df.columns:
            raise ValueError("supply_value must be a column of supply_df")

        if type(supply_value) is list:
            if any([sv not in supply_df.columns for sv in supply_value]):
                raise ValueError("supply_value must be columns of supply_df")

        if cost_df is not None:

            if cost_origin not in cost_df.columns:
                raise ValueError("cost_origin must be a column of cost_df")

            if cost_dest not in cost_df.columns:
                raise ValueError("cost_dest must be a column of cost_df")

            if type(cost_name) is str and cost_name not in cost_df.columns:
                raise ValueError("cost_name must be a column of cost_df")

            if type(cost_name) is list:
                if any([cn not in cost_df.columns for cn in cost_name]):
                    raise ValueError("cost_name must be columns of cost_df")

        if neighbor_cost_df is not None:

            if neighbor_cost_origin not in neighbor_cost_df.columns:
                raise ValueError(
                    "neighbor_cost_origin must be a column of neighbor_cost_df"
                )

            if neighbor_cost_dest not in neighbor_cost_df.columns:
                raise ValueError(
                    "neighbor_cost_dest must be a column of neighbor_cost_df"
                )

            if (
                type(neighbor_cost_name) is str
                and neighbor_cost_name not in neighbor_cost_df.columns
            ):
                raise ValueError("neighbor_cost_name must be a column of cost_df")

            if type(neighbor_cost_name) is list:
                if any(
                    [cn not in neighbor_cost_df.columns for cn in neighbor_cost_name]
                ):
                    raise ValueError("neighbor_cost_names must be columns of cost_df")

        ### Now load the demand DFs.

        self.demand_df = demand_df.copy()
        self.demand_value = demand_value
        if demand_index is not True:
            self.demand_df.set_index(demand_index, inplace=True)

        ### And now the supply DFs.

        self.supply_df = supply_df.copy()

        if supply_value == False:
            self.log.info(
                """Warning: A supply value was not provided, so a default
                             supply value of 1 was created in the column named "value".
                             Note that without a supply value, you cannot use any of the
                             floating catchment area methods."""
            )
            self.supply_value_provided = False
            supply_value = "value"
            self.supply_df[supply_value] = 1

        if type(supply_value) is str:
            self.supply_types = [supply_value]
        elif type(supply_value) is list:
            self.supply_types = supply_value
        else:
            raise ValueError("supply_value must be string or list of strings.")

        if supply_index is not True:
            self.supply_df.set_index(supply_index, inplace=True)

        if cost_df is not None:

            self.cost_df = cost_df
            self.cost_origin = cost_origin
            self.cost_dest = cost_dest

            if type(cost_name) is str:
                self.cost_names = [cost_name]

            elif type(cost_name) is list:
                self.cost_names = cost_name

            else:
                raise ValueError("cost_name must be string or list of strings.")

            self._default_cost = self.cost_names[0]

        else:
            self.cost_df = pd.DataFrame(columns=["origin", "dest"])
            self.cost_origin = "origin"
            self.cost_dest = "dest"
            self.cost_names = []

        if neighbor_cost_df is not None:

            self.neighbor_cost_df = neighbor_cost_df
            self.neighbor_cost_origin = neighbor_cost_origin
            self.neighbor_cost_dest = neighbor_cost_dest
            self.neighbor_cost_name = neighbor_cost_name

            if type(neighbor_cost_name) is str:
                self.neighbor_cost_names = [neighbor_cost_name]

            elif type(neighbor_cost_name) is list:
                self.neighbor_cost_names = neighbor_cost_name

            else:
                raise ValueError(
                    "neighbor_cost_name must be string or list of strings."
                )

            self._neighbor_default_cost = self.neighbor_cost_names[0]

        else:
            self.neighbor_cost_df = pd.DataFrame(columns=["origin", "dest"])
            self.neighbor_cost_origin = "origin"
            self.neighbor_cost_dest = "dest"
            self.neighbor_cost_names = []

        self.access_df = self.demand_df[[self.demand_value]].sort_index()

        self.access = pd.DataFrame(index=self.supply_df.index)

        self.access_metadata = pd.DataFrame(
            columns=["name", "distance", "function", "descriptor"]
        )
        self.cost_metadata = pd.DataFrame(columns=["name", "type", "descriptor"])

        return

    def weighted_catchment(
        self,
        name="catchment",
        supply_cost=None,
        supply_values=None,
        weight_fn=None,
        max_cost=None,
        normalize=False,
    ):
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

        Create an Access object, as detailed in __init__.py

        >>> illinois_primary_care = Access(<...>)

        Call the floating catchment area with max_cost only

        >>> gravity = weights.gravity(scale = 60, alpha = -1)
        >>> illinois_primary_care.weighted_catchment(weight_fn = gravity)

        """

        supply_cost = helpers.sanitize_supply_cost(self, supply_cost, name)
        supply_values = helpers.sanitize_supplies(self, supply_values)

        for s in supply_values:

            # Bryan consistently flipped origin and destination in this one -- very confusing.
            series = fca.weighted_catchment(
                loc_df=self.supply_df,
                loc_index=True,
                loc_value=s,
                cost_df=self.cost_df,
                cost_source=self.cost_dest,
                cost_dest=self.cost_origin,
                cost_cost=self._default_cost,
                weight_fn=weight_fn,
                max_cost=max_cost,
            )

            series.name = name + "_" + s
            if series.name in self.access_df.columns:
                self.log.info("Overwriting {}.".format(series.name))
                self.access_df.drop(series.name, axis=1, inplace=True)

            # store the raw, un-normalized access values
            self.access_df = self.access_df.join(series)

        if normalize:

            columns = [name + "_" + s for s in supply_values]
            return helpers.normalized_access(self, columns)

        return self.access_df.filter(regex="^" + name, axis=1)

    def fca_ratio(
        self,
        name="fca",
        demand_cost=None,
        supply_cost=None,
        supply_values=None,
        max_cost=None,
        normalize=False,
        noise="quiet",
    ):
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
        noise              : str
                             Default 'quiet', otherwise gives messages that indicate potential issues.

        Returns
        -------
        access              : pandas Series
                              Accessibility score for origin locations.

        Examples
        --------

        Import the base `Access` class and `Datasets`.

        >>> from access import Access, Datasets

        Load each of the example datasets:

        >>> chi_docs_dents   = Datasets.load_data('chi_doc')
        >>> chi_population   = Datasets.load_data('chi_pop')
        >>> chi_travel_costs = Datasets.load_data('chi_times')

        >>> chi_docs_dents.head()
                 geoid  doc  dentist
        0  17031010100    1        1
        1  17031010201    0        1
        2  17031010202    4        1
        3  17031010300    4        1
        4  17031010400    0        2

        >>> chi_population.head()
                 geoid   pop
        0  17031010100  4854
        1  17031010201  6450
        2  17031010202  2818
        3  17031010300  6236
        4  17031010400  5042

        >>> chi_travel_costs.head()
                origin         dest   cost
        0  17093890101  17031010100  91.20
        1  17093890101  17031010201  92.82
        2  17093890101  17031010202  92.95
        3  17093890101  17031010300  89.40
        4  17093890101  17031010400  84.97

        Using the example data, create an `Access` object.

        >>> chicago_primary_care = Access(demand_df = chi_population, demand_index = "geoid",
                                          demand_value = "pop",
                                          supply_df = chi_docs_dents, supply_index = "geoid",
                                          supply_value = ["doc", "dentist"],
                                          cost_df = chi_travel_costs, cost_origin  = "origin",
                                          cost_dest = "destination", cost_name = "cost",
                                          neighbor_cost_df = chi_travel_costs, neighbor_cost_origin = "origin",
                                          neighbor_cost_dest = 'dest', neighbor_cost_name = 'cost')

        >>> chicago_primary_care.fca_ratio(name='fca',max_cost=30)
                      fca_doc  fca_dentist
        geoid
        17031010100  0.001630     0.000807
        17031010201  0.001524     0.000904
        17031010202  0.001521     0.000908
        ...........  ........     ........
        17197884101  0.000437     0.000442
        17197884103  0.000510     0.000498
        17197980100  0.000488     0.000432
        """

        assert (
            self.supply_value_provided == True
        ), "You must provide a supply value in order to use this functionality."

        supply_cost = helpers.sanitize_supply_cost(self, supply_cost, name)
        demand_cost = helpers.sanitize_demand_cost(self, demand_cost, name)
        supply_values = helpers.sanitize_supplies(self, supply_values)

        for s in supply_values:

            series = fca.fca_ratio(
                demand_df=self.demand_df,
                demand_index=self.demand_df.index.name,
                demand_name=self.demand_value,
                supply_df=self.supply_df,
                supply_index=self.supply_df.index.name,
                supply_name=s,
                demand_cost_df=self.neighbor_cost_df,
                supply_cost_df=self.cost_df,
                demand_cost_origin=self.neighbor_cost_origin,
                demand_cost_dest=self.neighbor_cost_dest,
                demand_cost_name=demand_cost,
                supply_cost_origin=self.cost_origin,
                supply_cost_dest=self.cost_dest,
                supply_cost_name=supply_cost,
                max_cost=max_cost,
                normalize=normalize,
                noise=noise,
            )

            series.name = name + "_" + s
            if series.name in self.access_df.columns:
                self.log.info("Overwriting {}.".format(series.name))
                self.access_df.drop(series.name, axis=1, inplace=True)

            # store the raw, un-normalized access values
            self.access_df = self.access_df.join(series)

        if normalize:

            columns = [name + "_" + s for s in supply_values]
            return helpers.normalized_access(self, columns)

        return self.access_df.filter(regex="^" + name, axis=1)

    def raam(
        self,
        name="raam",
        cost=None,
        supply_values=None,
        normalize=False,
        tau=60,
        rho=None,
        max_cycles=150,
        initial_step=0.2,
        half_life=50,
        min_step=0.005,
        verbose=False,
    ):
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
                              If True, return normalized access values; otherwise, return raw access values
        tau                 : float
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

        Import the base `Access` class and `Datasets`.

        >>> from access import Access, Datasets

        Load each of the example datasets which correspond to the demand (population), supply (doctors and dentists)
        and cost (travel time), respectively. The sample data represents the Chicago metro area with a 50km buffer around the city boundaries.

        >>> chi_docs_dents   = Datasets.load_data('chi_doc')
        >>> chi_population   = Datasets.load_data('chi_pop')
        >>> chi_travel_costs = Datasets.load_data('chi_times')

        >>> chi_docs_dents.head()
                 geoid  doc  dentist
        0  17031010100    1        1
        1  17031010201    0        1
        2  17031010202    4        1
        3  17031010300    4        1
        4  17031010400    0        2

        >>> chi_population.head()
                 geoid   pop
        0  17031010100  4854
        1  17031010201  6450
        2  17031010202  2818
        3  17031010300  6236
        4  17031010400  5042

        The `chi_travel_costs` dataset is the cost matrix, showing the travel time between each of the Census Tracts in the Chicago metro area.

        >>> chi_travel_costs.head()
                origin         dest   cost
        0  17093890101  17031010100  91.20
        1  17093890101  17031010201  92.82
        2  17093890101  17031010202  92.95
        3  17093890101  17031010300  89.40
        4  17093890101  17031010400  84.97

        Now, create an instance of the `Access` class and specify the demand, supply, and cost datasets.

        >>> chicago_primary_care = Access(demand_df = chi_population, demand_index = "geoid",
                                          demand_value = "pop",
                                          supply_df = chi_docs_dents, supply_index = "geoid",
                                          supply_value = ["doc", "dentist"],
                                          cost_df = chi_travel_costs, cost_origin  = "origin",
                                          cost_dest = "dest", cost_name = "cost")

        With the demand, supply, and cost data provided, we can now produce the RAAM access measures defining a floating catchment area of 30 minutes by setting the tau value to 30 (60 minutes is the default).

        >>> chicago_primary_care.raam(tau = 30)
                     raam_doc  raam_dentist
        geoid
        17031010100  1.027597      1.137901
        17031010201  0.940239      1.332557
        17031010202  1.031144      1.413279
        ...........  ........      ........
        17197884101  2.365171      1.758800
        17197884103  2.244007      1.709857
        17197980100  2.225820      1.778264

        You can access the results stored in the `Access.access_df` attribute.

        >>> chicago_primary_care.access_df
                      pop  raam_doc  raam_dentist
        geoid
        17031010100  4854  1.027597      1.137901
        17031010201  6450  0.940239      1.332557
        17031010202  2818  1.031144      1.413279
        ...........   ....  ........      ........
        17197884101  4166  2.365171      1.758800
        17197884103  2776  2.244007      1.709857
        17197980100  3264  2.225820      1.778264


        By providing a string to the `name` argument, you can call the `Access.raam` method again using a different parameter of tau and save the outputs without overwriting previous ones.

        >>> chicago_primary_care.raam(name = "raam2", tau = 2)
        >>> chicago_primary_care.access_df
                      pop  raam_doc  raam_dentist  raam45_doc  raam45_dentist
        geoid
        17031010100  4854  1.027597      1.137901    0.967900        1.075116
        17031010201  6450  0.940239      1.332557    0.908518        1.133207
        17031010202  2818  1.031144      1.413279    0.962915        1.206775
        ...........   ....  ........      ........   ........       ........
        17197884101  4166  2.365171      1.758800    1.921161        1.495642
        17197884103  2776  2.244007      1.709857    1.900596        1.517022
        17197980100  3264  2.225820      1.778264    1.868281        1.582177

        If euclidean costs are available (see :meth:`Access.access.create_euclidean_distance`),
        you can use euclidean distance instead of time to calculate RAAM access measures. Insted of being measured in minutes, tau would now be measured in meters.

        >>> chicago_primary_care.raam(name = "raam_euclidean", tau = 100, cost = "euclidean")

        """

        assert (
            self.supply_value_provided == True
        ), "You must provide a supply value in order to use this functionality."

        cost = helpers.sanitize_supply_cost(self, cost, name)
        supply_values = helpers.sanitize_supplies(self, supply_values)

        for s in supply_values:

            raam_costs = raam.raam(
                demand_df=self.demand_df,
                supply_df=self.supply_df,
                cost_df=self.cost_df,
                demand_name=self.demand_value,
                supply_name=s,
                cost_origin=self.cost_origin,
                cost_dest=self.cost_dest,
                cost_name=cost,
                max_cycles=max_cycles,
                tau=tau,
                verbose=verbose,
                initial_step=initial_step,
                min_step=min_step,
            )

            raam_costs.name = name + "_" + s
            if raam_costs.name in self.access_df.columns:
                self.log.info("Overwriting {}.".format(raam_costs.name))
                self.access_df.drop(raam_costs.name, axis=1, inplace=True)

            # store the raw, un-normalized access values
            self.access_df = self.access_df.join(raam_costs)

        if normalize:

            columns = [name + "_" + s for s in supply_values]
            return helpers.normalized_access(self, columns)

        return self.access_df.filter(regex="^" + name, axis=1)

    def two_stage_fca(
        self,
        name="2sfca",
        cost=None,
        max_cost=None,
        supply_values=None,
        weight_fn=None,
        normalize=False,
    ):
        """Calculate the two-stage floating catchment area access score.
        Note that while the 'traditional' 2SFCA method does not weight inputs,
        most modern implementations do, and `weight_fn` is allowed as an argument.

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

        Examples
        --------

        Import the base `Access` class and `Datasets`.

        >>> from access import Access, Datasets

        Load each of the example datasets:

        >>> chi_docs_dents   = Datasets.load_data('chi_doc')
        >>> chi_population   = Datasets.load_data('chi_pop')
        >>> chi_travel_costs = Datasets.load_data('chi_times')

        >>> chi_docs_dents.head()
                 geoid  doc  dentist
        0  17031010100    1        1
        1  17031010201    0        1
        2  17031010202    4        1
        3  17031010300    4        1
        4  17031010400    0        2

        >>> chi_population.head()
                 geoid   pop
        0  17031010100  4854
        1  17031010201  6450
        2  17031010202  2818
        3  17031010300  6236
        4  17031010400  5042

        >>> chi_travel_costs.head()
                origin         dest   cost
        0  17093890101  17031010100  91.20
        1  17093890101  17031010201  92.82
        2  17093890101  17031010202  92.95
        3  17093890101  17031010300  89.40
        4  17093890101  17031010400  84.97

        Using the example data, create an `Access` object.

        >>> chicago_primary_care = Access(demand_df = chi_population, demand_index = "geoid",
                                          demand_value = "pop",
                                          supply_df = chi_docs_dents, supply_index = "geoid",
                                          supply_value = ["doc", "dentist"],
                                          cost_df = chi_travel_costs, cost_origin  = "origin",
                                          cost_dest = "destination", cost_name = "cost",
                                          neighbor_cost_df = chi_travel_costs, neighbor_cost_origin = "origin",
                                          neighbor_cost_dest = 'dest', neighbor_cost_name = 'cost')

        >>> chicago_primary_care.two_stage_fca(name = '2sfca', max_cost = 60)
                      pop  2sfca_doc  2sfca_dentist
        geoid
        17031010100  4854   0.000697       0.000402
        17031010201  6450   0.000754       0.000455
        17031010202  2818   0.000717       0.000424
        ...........  ....   ........       ........
        17197884101  4166   0.000562       0.000370
        17197884103  2776   0.000384       0.000291
        17197980100  3264   0.000457       0.000325

        To create new values for two-stage catchment areas using a different `max_cost`, you can use a new `name` and a different `max_cost` parameter.

        >>> chicago_primary_care.two_stage_fca(name = '2sfca30', max_cost = 30)
                     2sfca30_doc  2sfca30_dentist
        geoid
        17031010100     0.000966         0.000480
        17031010201     0.000996         0.000552
        17031010202     0.000973         0.000542
        ...........     ........         ........
        17197884101     0.000225         0.000258
        17197884103     0.000375         0.000382
        17197980100     0.000352         0.000318

        Both newly created two stage fca measures are stored in the `access_df` attribute of the `Access` object.

        >>> chicago_primary_care.access_df.head()
                      pop  2sfca_doc  2sfca_dentist  2sfca30_doc  2sfca30_dentist
        geoid
        17031010100  4854   0.000697       0.000402     0.000963         0.000479
        17031010201  6450   0.000754       0.000455     0.000991         0.000551
        17031010202  2818   0.000717       0.000424     0.000973         0.000541
        17197884103  2776   0.000384       0.000291     0.000371         0.000377
        17197980100  3264   0.000457       0.000325     0.000348         0.000314
        """

        assert (
            self.supply_value_provided == True
        ), "You must provide a supply value in order to use this functionality."

        if cost is None:

            cost = self._default_cost
            if len(self.cost_names) > 1:
                self.log.info("Using default cost, {}, for {}.".format(cost, name))

        if cost not in self.cost_names:

            raise ValueError("{} not an available cost.".format(cost))

        if type(supply_values) is str:
            supply_values = [supply_values]
        if supply_values is None:
            supply_values = self.supply_types

        for s in supply_values:

            series = fca.two_stage_fca(
                demand_df=self.demand_df,
                demand_index=self.demand_df.index.name,
                demand_name=self.demand_value,
                supply_df=self.supply_df,
                supply_index=self.supply_df.index.name,
                supply_name=s,
                cost_df=self.cost_df,
                cost_origin=self.cost_origin,
                cost_dest=self.cost_dest,
                cost_name=cost,
                max_cost=max_cost,
                weight_fn=weight_fn,
                normalize=normalize,
            )

            series.name = name + "_" + s
            if series.name in self.access_df.columns:
                self.log.info("Overwriting {}.".format(series.name))
                self.access_df.drop(series.name, axis=1, inplace=True)

            self.access_df = self.access_df.join(series)

        if normalize:

            columns = [name + "_" + s for s in supply_values]
            return helpers.normalized_access(self, columns)

        return self.access_df.filter(regex="^" + name, axis=1)

    def enhanced_two_stage_fca(
        self,
        name="e2sfca",
        cost=None,
        supply_values=None,
        max_cost=None,
        weight_fn=None,
        normalize=False,
    ):
        """Calculate the enhanced two-stage floating catchment area access score.
        Note that the only 'practical' difference between this function and the
        :meth:`Access.access.two_stage_fca` is that the weight function from the original paper,
        `weights.step_fn({10 : 1, 20 : 0.68, 30 : 0.22})` is applied if none is provided.

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

        Examples
        --------

        Import the base `Access` class and `Datasets`.

        >>> from access import Access, Datasets

        Load each of the example datasets:

        >>> chi_docs_dents   = Datasets.load_data('chi_doc')
        >>> chi_population   = Datasets.load_data('chi_pop')
        >>> chi_travel_costs = Datasets.load_data('chi_times')

        >>> chi_docs_dents.head()
                 geoid  doc  dentist
        0  17031010100    1        1
        1  17031010201    0        1
        2  17031010202    4        1
        3  17031010300    4        1
        4  17031010400    0        2

        >>> chi_population.head()
                 geoid   pop
        0  17031010100  4854
        1  17031010201  6450
        2  17031010202  2818
        3  17031010300  6236
        4  17031010400  5042


        >>> chi_travel_costs.head()
                origin         dest   cost
        0  17093890101  17031010100  91.20
        1  17093890101  17031010201  92.82
        2  17093890101  17031010202  92.95
        3  17093890101  17031010300  89.40
        4  17093890101  17031010400  84.97

        Using the example data, create an `Access` object.

        >>> chicago_primary_care = Access(demand_df = chi_population, demand_index = "geoid",
                                          demand_value = "pop",
                                          supply_df = chi_docs_dents, supply_index = "geoid",
                                          supply_value = ["doc", "dentist"],
                                          cost_df = chi_travel_costs, cost_origin  = "origin",
                                          cost_dest = "destination", cost_name = "cost")

        We can create multiple stepwise functions for weights.

        >>> fn30 = weights.step_fn({10 : 1, 20 : 0.68, 30 : 0.22})
        >>> fn60 = weights.step_fn({20 : 1, 40 : 0.68, 60 : 0.22})

        Using those two difference stepwise functions, we can create two separate enhanced two stage fca measures.

        >>> chicago_primary_care.enhanced_two_stage_fca(name = '2sfca30', weight_fn = fn30)
                     2sfca30_doc  2sfca30_dentist
        geoid
        17031010100     0.000970         0.000461
        17031010201     0.001080         0.000557
        17031010202     0.001027         0.000531
        ...........     ........         ........
        17197884101     0.000159         0.000241
        17197884103     0.000285         0.000342
        17197980100     0.000266         0.000310

        Note the use of the `name` argument in order to specify a different column name prefix for the access measure.

        >>> chicago_primary_care.enhanced_two_stage_fca(name = '2sfca60', weight_fn = fn60)
                     2sfca60_doc  2sfca60_dentist
        geoid
        17031010100     0.000687         0.000394
        17031010201     0.000750         0.000447
        17031010202     0.000720         0.000416
        ...........     ........         ........
        17197884101     0.000392         0.000301
        17197884103     0.000289         0.000243
        17197980100     0.000333         0.000268

        Both newly created enhanced two stage fca measures are stored in the `access_df` attribute of the `Access` object.

        >>> chicago_primary_care.access_df.head()
                      pop  2sfca30_doc  2sfca30_dentist  2sfca60_doc  2sfca60_dentist
        geoid
        17031010100  4854     0.000970         0.000461     0.000687         0.000394
        17031010201  6450     0.001080         0.000557     0.000750         0.000447
        17031010202  2818     0.001027         0.000531     0.000720         0.000416
        17031010300  6236     0.001030         0.000496     0.000710         0.000402
        17031010400  5042     0.000900         0.000514     0.000786         0.000430
        """

        assert (
            self.supply_value_provided == True
        ), "You must provide a supply value in order to use this functionality."

        if weight_fn is None:
            weight_fn = weights.step_fn({10: 1, 20: 0.68, 30: 0.22})

        return self.two_stage_fca(
            name, cost, max_cost, supply_values, weight_fn, normalize
        )

    def three_stage_fca(
        self,
        name="3sfca",
        cost=None,
        supply_values=None,
        max_cost=None,
        weight_fn=None,
        normalize=False,
    ):
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

        Examples
        --------

        Import the base `Access` class and `Datasets`.

        >>> from access import Access, Datasets

        Load each of the example datasets:

        >>> chi_docs_dents   = Datasets.load_data('chi_doc')
        >>> chi_population   = Datasets.load_data('chi_pop')
        >>> chi_travel_costs = Datasets.load_data('chi_times')

        >>> chi_docs_dents.head()
                 geoid  doc  dentist
        0  17031010100    1        1
        1  17031010201    0        1
        2  17031010202    4        1
        3  17031010300    4        1
        4  17031010400    0        2

        >>> chi_population.head()
                 geoid   pop
        0  17031010100  4854
        1  17031010201  6450
        2  17031010202  2818
        3  17031010300  6236
        4  17031010400  5042

        >>> chi_travel_costs.head()
                origin         dest   cost
        0  17093890101  17031010100  91.20
        1  17093890101  17031010201  92.82
        2  17093890101  17031010202  92.95
        3  17093890101  17031010300  89.40
        4  17093890101  17031010400  84.97

        Using the example data, create an `Access` object.

        >>> chicago_primary_care = Access(demand_df = chi_population, demand_index = "geoid",
                                          demand_value = "pop",
                                          supply_df = chi_docs_dents, supply_index = "geoid",
                                          supply_value = ["doc", "dentist"],
                                          cost_df = chi_travel_costs, cost_origin  = "origin",
                                          cost_dest = "destination", cost_name = "cost")

        >>> chicago_primary_care.three_stage_fca(name='3sfca')
                     3sfca_doc  3sfca_dentist
        geoid
        17031010100   0.001424       0.000690
        17031010201   0.001462       0.000785
        17031010202   0.001411       0.000767
        ...........   ........       ........
        17197884101   0.000285       0.000380
        17197884103   0.000404       0.000464
        17197980100   0.000365       0.000407

        The newly calculated 3sfca access measure is added to the `access_df` attribute of the `Access` object.

        >>> chicago_primary_care.access_df.head()
                             3sfca_doc  3sfca_dentist
        geoid
        17031010100   0.001447       0.000698
        17031010201   0.001487       0.000795
        17031010202   0.001420       0.000777
        17031010300   0.001479       0.000742
        17031010400   0.001274       0.000726
        """

        assert (
            self.supply_value_provided == True
        ), "You must provide a supply value in order to use this functionality."

        if weight_fn is None:
            weight_fn = weights.step_fn({10: 0.962, 20: 0.704, 30: 0.377, 60: 0.042})

        cost = helpers.sanitize_supply_cost(self, cost, name)
        supply_values = helpers.sanitize_supplies(self, supply_values)

        for s in supply_values:

            series = fca.three_stage_fca(
                demand_df=self.demand_df,
                demand_index=self.demand_df.index.name,
                demand_name=self.demand_value,
                supply_df=self.supply_df,
                supply_index=self.supply_df.index.name,
                supply_name=s,
                cost_df=self.cost_df,
                cost_origin=self.cost_origin,
                cost_dest=self.cost_dest,
                cost_name=cost,
                max_cost=max_cost,
                weight_fn=weight_fn,
                normalize=normalize,
            )

            series.name = name + "_" + s
            if series.name in self.access_df.columns:
                self.log.info("Overwriting {}.".format(series.name))
                self.access_df.drop(series.name, axis=1, inplace=True)

            # store the raw, un-normalized access values
            self.access_df = self.access_df.join(series)

        if normalize:

            columns = [name + "_" + s for s in supply_values]
            return helpers.normalized_access(self, columns)

        return self.access_df.filter(regex="^" + name, axis=1)

    @property
    def norm_access_df(self):
        for column in self.access_df.columns.difference([self.demand_value]):
            mean_access = (
                self.access_df[column] * self.access_df[self.demand_value]
            ).sum() / self.access_df[self.demand_value].sum()
            self.access_df[column] /= mean_access
        return self.access_df[self.access_df.columns.difference([self.demand_value])]

    def score(self, col_dict, name="score"):
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

        Import the base `Access` class and `Datasets`.

        >>> from access import Access, Datasets

        Load each of the example datasets which correspond to the demand (population), supply (doctors and dentists)
        and cost (travel time), respectively. The sample data represents the Chicago metro area with a 50km buffer around the city boundaries.

        >>> chi_docs_dents   = Datasets.load_data('chi_doc')
        >>> chi_population   = Datasets.load_data('chi_pop')
        >>> chi_travel_costs = Datasets.load_data('chi_times')

        >>> chi_docs_dents.head()
                 geoid  doc  dentist
        0  17031010100    1        1
        1  17031010201    0        1
        2  17031010202    4        1
        3  17031010300    4        1
        4  17031010400    0        2

        >>> chi_population.head()
                 geoid   pop
        0  17031010100  4854
        1  17031010201  6450
        2  17031010202  2818
        3  17031010300  6236
        4  17031010400  5042

        The `chi_travel_costs` dataset is the cost matrix, showing the travel time between each of the Census Tracts in the Chicago metro area.

        >>> chi_travel_costs.head()
                origin         dest   cost
        0  17093890101  17031010100  91.20
        1  17093890101  17031010201  92.82
        2  17093890101  17031010202  92.95
        3  17093890101  17031010300  89.40
        4  17093890101  17031010400  84.97

        Now, create an instance of the `Access` class and specify the demand, supply, and cost datasets.

        >>> chicago_primary_care = Access(demand_df = chi_population, demand_index = "geoid",
                                          demand_value = "pop",
                                          supply_df = chi_docs_dents, supply_index = "geoid",
                                          supply_value = ["doc", "dentist"],
                                          cost_df = chi_travel_costs, cost_origin  = "origin",
                                          cost_dest = "dest", cost_name = "cost")

        With the demand, supply, and cost data provided, we can now produce the RAAM access measures defining a floating catchment area of 30 minutes by setting the tau value to 30 (60 minutes is the default).

        >>> chicago_primary_care.raam(tau = 30)
                     raam_doc  raam_dentist
        geoid
        17031010100  1.027597      1.137901
        17031010201  0.940239      1.332557
        17031010202  1.031144      1.413279
        ...........  ........      ........
        17197884101  2.365171      1.758800
        17197884103  2.244007      1.709857
        17197980100  2.225820      1.778264

        Aggregate RAAM for doctors and dentists, weighting doctors more heavily.

        >>> chicago_primary_care.score(name = "raam_combo", col_dict = {"raam_doc" : 0.8, "raam_dentist" : 0.2})
        geoid
        17031010100    0.786697
        17031010201    0.765081
        17031010202    0.831578
        ...........    ........
        17197884101    1.677075
        17197884103    1.597554
        17197980100    1.597386
        """

        for v in col_dict:
            if v not in self.access_df.columns:
                raise ValueError("{} is not a calculated access value".format(v))

        weights = pd.Series(col_dict)

        weighted_score = self.norm_access_df[weights.index].dot(weights)

        weighted_score.name = name
        if weighted_score.name in self.access_df.columns:
            self.log.info("Overwriting {}.".format(weighted_score.name))
            self.access_df.drop(weighted_score.name, axis=1, inplace=True)

        self.access_df = self.access_df.join(weighted_score)

        return weighted_score

    @property
    def default_cost(self):
        return self._default_cost

    @default_cost.setter
    def default_cost(self, new_cost):
        """Change the default cost measure."""

        if new_cost in self.cost_names:
            self._default_cost = new_cost

        else:
            raise ValueError("Tried to set cost not available in cost df")

    @property
    def neighbor_default_cost(self):
        return self._neighbor_default_cost

    @neighbor_default_cost.setter
    def neighbor_default_cost(self, new_cost):
        """Change the default cost measure."""

        if new_cost in self.neighbor_cost_names:
            self._neighbor_default_cost = new_cost

        else:
            raise ValueError("Tried to set cost not available in cost df")

    def append_user_cost(self, new_cost_df, origin, destination, name):
        """Create a user cost, from demand to supply locations.

        Parameters
        ----------
        new_cost_df         : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                              Holds the new cost....
        name                : str
                              Name of the new cost variable in new_cost_df
        origin              : str
                              Name of the new origin variable in new_cost_df
        destination         : str
                              Name of the new destination variable in new_cost_df

        Examples
        --------

        Import the base `Access` class and `Datasets`.

        >>> from access import Access, Datasets

        Load each of the example datasets:

        >>> chi_docs_dents   = Datasets.load_data('chi_doc')
        >>> chi_population   = Datasets.load_data('chi_pop')
        >>> chi_travel_costs = Datasets.load_data('chi_times')

        >>> chi_docs_dents.head()
                 geoid  doc  dentist
        0  17031010100    1        1
        1  17031010201    0        1
        2  17031010202    4        1
        3  17031010300    4        1
        4  17031010400    0        2

        >>> chi_population.head()
                 geoid   pop
        0  17031010100  4854
        1  17031010201  6450
        2  17031010202  2818
        3  17031010300  6236
        4  17031010400  5042

        >>> chi_travel_costs.head()
                origin         dest   cost
        0  17093890101  17031010100  91.20
        1  17093890101  17031010201  92.82
        2  17093890101  17031010202  92.95
        3  17093890101  17031010300  89.40
        4  17093890101  17031010400  84.97

        Using the example data, create an `Access` object.

        >>> chicago_primary_care = Access(demand_df = chi_population, demand_index = "geoid",
                                          demand_value = "pop",
                                          supply_df = chi_docs_dents, supply_index = "geoid",
                                          supply_value = ["doc", "dentist"],
                                          cost_df = chi_travel_costs, cost_origin  = "origin",
                                          cost_dest = "destination", cost_name = "cost")

        To add a new cost from demand to supply locations, first load the new cost data.

        >>> euclidean_cost = Datasets.load_data('chi_euclidean')
            euclidean_cost.head()
                origin         dest     euclidean
        0  17093890101  17031010100  63630.788476
        1  17093890101  17031010201  62632.675522
        2  17093890101  17031010202  63073.735631
        3  17093890101  17031010300  63520.029749
        4  17093890101  17031010400  63268.514352

        Add new cost data to existing `Access` instance.

        >>> chicago_primary_care.append_user_cost(new_cost_df = euclidean_cost,
                                           name = "euclidean",
                                           origin = "origin",
                                           destination = "dest")

        The newly added cost data can be seen in the `cost_df` attribute.

        >>> chicago_primary_care.cost_df.head()
                origin         dest   cost     euclidean
        0  17093890101  17031010100  91.20  63630.788476
        1  17093890101  17031010201  92.82  62632.675522
        2  17093890101  17031010202  92.95  63073.735631
        3  17093890101  17031010300  89.40  63520.029749
        4  17093890101  17031010400  84.97  63268.514352

        """

        # Add it to the list of costs.
        self.cost_df = self.cost_df.merge(
            new_cost_df[[origin, destination, name]],
            how="outer",
            left_on=[self.cost_origin, self.cost_dest],
            right_on=[origin, destination],
        )
        self.cost_names.append(name)

    def append_user_cost_neighbors(self, new_cost_df, origin, destination, name):
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

        Examples
        --------

        Import the base `Access` class and `Datasets`.

        >>> from access import Access, Datasets

        Load each of the example datasets:

        >>> chi_docs_dents   = Datasets.load_data('chi_doc')
        >>> chi_population   = Datasets.load_data('chi_pop')
        >>> chi_travel_costs = Datasets.load_data('chi_times')

        >>> chi_docs_dents.head()
                 geoid  doc  dentist
        0  17031010100    1        1
        1  17031010201    0        1
        2  17031010202    4        1
        3  17031010300    4        1
        4  17031010400    0        2

        >>> chi_population.head()
                 geoid   pop
        0  17031010100  4854
        1  17031010201  6450
        2  17031010202  2818
        3  17031010300  6236
        4  17031010400  5042

        >>> chi_travel_costs.head()
                origin         dest   cost
        0  17093890101  17031010100  91.20
        1  17093890101  17031010201  92.82
        2  17093890101  17031010202  92.95
        3  17093890101  17031010300  89.40
        4  17093890101  17031010400  84.97

        Using the example data, create an `Access` object.

        >>> chicago_primary_care = Access(demand_df = chi_population, demand_index = "geoid",
                                          demand_value = "pop",
                                          supply_df = chi_docs_dents, supply_index = "geoid",
                                          supply_value = ["doc", "dentist"],
                                          cost_df = chi_travel_costs, cost_origin  = "origin",
                                          cost_dest = "destination", cost_name = "cost")

        To add a new cost from demand to supply locations, first load the new cost data.

        >>> euclidean_cost_neighbors = Datasets.load_data('chi_euclidean_neighbors')
            euclidean_cost_neighbors.head()
                origin         dest  euclidean_neighbors
        0  17031010100  17031010100             0.000000
        1  17031010100  17031010201           998.259243
        2  17031010100  17031010202           635.203387
        3  17031010100  17031010300           653.415713
        4  17031010100  17031010400          2065.375554

        Add new cost data to existing `Access` instance.

        >>> chicago_primary_care.append_user_cost_neighbors(new_cost_df = euclidean_cost_neighbors,
                                                     name = "euclidean_neighbors",
                                                     origin = "origin",
                                                     destination = "dest")

        The newly added cost data can be seen in the `neighbor_cost_df` attribute.

        >>> chicago_primary_care.neighbor_cost_df.head()
                origin         dest   cost   euclidean_neighbors
        0  17093890101  17031010100  91.20          63630.788476
        1  17093890101  17031010201  92.82          62632.675522
        2  17093890101  17031010202  92.95          63073.735631
        3  17093890101  17031010300  89.40          63520.029749
        4  17093890101  17031010400  84.97          63268.514352
        """

        # Add it to the list of costs.
        self.neighbor_cost_df = self.neighbor_cost_df.merge(
            new_cost_df[[origin, destination, name]],
            how="outer",
            left_on=[self.neighbor_cost_origin, self.neighbor_cost_dest],
            right_on=[origin, destination],
        )
        self.neighbor_cost_names.append(name)

    def create_euclidean_distance(
        self, name="euclidean", threshold=0, centroid_o=False, centroid_d=False
    ):
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

        Examples
        --------

        NOTE: Creating euclidean distance measures requires having a geometry column in a `geopandas.GeoDataFrame <http://geopandas.org/reference/geopandas.GeoDataFrame.html>`_.

        Import the base `Access` class and `Datasets`.

        >>> from access import Access, Datasets

        Load each of the example datasets which correspond to the demand (population), supply (doctors and dentists)
        and cost (travel time), respectively. The sample data represents the Chicago metro area with a 50km buffer around the city boundaries.

        >>> chi_docs_dents   = Datasets.load_data('chi_doc_geom')
        >>> chi_population   = Datasets.load_data('chi_pop_geom')
        >>> chi_travel_costs = Datasets.load_data('chi_times')

        >>> chi_docs_dents.head()
                     doc  dentist                       geometry
        geoid
        17031010100    1        1  POINT (354916.992 594670.505)
        17031010201    0        1  POINT (354105.876 594088.600)
        17031010202    4        1  POINT (354650.684 594093.822)
        17031010300    4        1  POINT (355209.361 594086.149)
        17031010400    0        2  POINT (355809.748 592808.043)

        >>> chi_population.head()
                      pop                       geometry
        geoid
        17031010100  4854  POINT (354916.992 594670.505)
        17031010201  6450  POINT (354105.876 594088.600)
        17031010202  2818  POINT (354650.684 594093.822)
        17031010300  6236  POINT (355209.361 594086.149)
        17031010400  5042  POINT (355809.748 592808.043)

        The `chi_travel_costs` dataset is the cost matrix, showing the travel time between each of the Census Tracts in the Chicago metro area.

        >>> chi_travel_costs.head()
                origin         dest   cost
        0  17093890101  17031010100  91.20
        1  17093890101  17031010201  92.82
        2  17093890101  17031010202  92.95
        3  17093890101  17031010300  89.40
        4  17093890101  17031010400  84.97

        Now, create an instance of the `Access` class and specify the demand, supply, and cost datasets.

        >>> chicago_primary_care = Access(demand_df = chi_population, demand_index = "geoid",
                                          demand_value = "pop",
                                          supply_df = chi_docs_dents, supply_index = "geoid",
                                          supply_value = ["doc", "dentist"],
                                          cost_df = chi_travel_costs, cost_origin  = "origin",
                                          cost_dest = "dest", cost_name = "cost")

        To calculate euclidean distances between Census Tracts within 250km of eachother, you can set the `threshold` to 250000 (meters). Setting `centroid_o` and `centroid_d` to `True` calculates the centroid of the geom in your dataset.

        >>> chicago_primary_care.create_euclidean_distance(threshold = 250000, centroid_o = True, centroid_d = True)

        The newly calculated euclidean costs are added to the `cost_df` attribute of the `Access` class.

        >>> chicago_primary_care_geom.cost_df.head()
                origin         dest   cost     euclidean
        0  17093890101  17031010100  91.20  63630.788476
        1  17093890101  17031010201  92.82  62632.675522
        2  17093890101  17031010202  92.95  63073.735631
        3  17093890101  17031010300  89.40  63520.029749
        4  17093890101  17031010400  84.97  63268.514352
        """
        import geopandas as gpd

        # TO-DO: check for unprojected geometries

        # Continue if the dataframes are geodataframes, else throw an error
        if type(self.demand_df) is not gpd.GeoDataFrame:
            raise TypeError(
                "Cannot calculate euclidean distance without a geometry of demand side"
            )

        if type(self.supply_df) is not gpd.GeoDataFrame:
            raise TypeError(
                "Cannot calculate euclidean distance without a geometry of supply side"
            )

        # Reset the index so that the geoids are accessible
        df1 = self.demand_df.rename_axis("origin").reset_index()
        df2 = self.supply_df.rename_axis("dest").reset_index()

        # Convert to centroids if so-specified
        if centroid_o:
            df1.set_geometry(df1.centroid, inplace=True)
        if centroid_d:
            df2.set_geometry(df2.centroid, inplace=True)

        # Calculate the distances.
        if (df1.geom_type == "Point").all() & (df2.geom_type == "Point").all():
            # If both geometries are point types, merge on a temporary dummy column
            df1["temp"] = 1
            df2["temp"] = 1
            df1and2 = df1[["temp", "geometry", "origin"]].merge(
                df2[["temp", "geometry", "dest"]].rename(columns={"geometry": "geomb"})
            )
            df1and2.drop("temp", inplace=True, axis=1)
            df1and2[name] = df1and2.distance(df1and2.set_geometry("geomb"))
        else:
            # Execute an sjoin for non-point geometries, based upon a buffer zone
            df1and2 = gpd.sjoin(
                df1,
                df2.rename(columns={"geometry": "geomb"}).set_geometry(
                    df2.buffer(threshold)
                ),
            )
            df1and2[name] = df1and2.distance(df1and2.set_geometry("geomb"))

        # Add it to the cost df.
        df1and2 = df1and2[df1and2[name] < threshold]

        if name in self.cost_df.columns:
            self.log.info("Overwriting {}.".format(name))
            self.cost_df.drop(name, axis=1, inplace=True)

        self.cost_df = self.cost_df.merge(
            df1and2[[name, "origin", "dest"]],
            how="outer",
            left_on=[self.cost_origin, self.cost_dest],
            right_on=["origin", "dest"],
        )

        # Add it to the list of costs.
        if name not in self.cost_names:
            self.cost_names.append(name)
        # Set the default cost if it does not exist
        if not hasattr(self, "_default_cost"):
            self._default_cost = name

    def create_euclidean_distance_neighbors(
        self, name="euclidean", threshold=0, centroid=False
    ):
        """Calculate the Euclidean distance among demand locations.

        Parameters
        ----------
        name                : str
                              Column name for euclidean distances neighbors
        threshold           : int
                              Buffer threshold for non-point geometries, AKA max_distance
        centroid            : bool
                              If True, convert geometries to centroids; otherwise, no change

        Examples
        --------

        NOTE: Creating euclidean distance measures requires having a geometry column in a `geopandas.GeoDataFrame <http://geopandas.org/reference/geopandas.GeoDataFrame.html>`_.

        Import the base `Access` class and `Datasets`.

        >>> from access import Access, Datasets

        Load each of the example datasets which correspond to the demand (population), supply (doctors and dentists)
        and cost (travel time), respectively. The sample data represents the Chicago metro area with a 50km buffer around the city boundaries.

        >>> chi_docs_dents   = Datasets.load_data('chi_doc_geom')
        >>> chi_population   = Datasets.load_data('chi_pop_geom')
        >>> chi_travel_costs = Datasets.load_data('chi_times')

        >>> chi_docs_dents.head()
                     doc  dentist                       geometry
        geoid
        17031010100    1        1  POINT (354916.992 594670.505)
        17031010201    0        1  POINT (354105.876 594088.600)
        17031010202    4        1  POINT (354650.684 594093.822)
        17031010300    4        1  POINT (355209.361 594086.149)
        17031010400    0        2  POINT (355809.748 592808.043)

        >>> chi_population.head()
                      pop                       geometry
        geoid
        17031010100  4854  POINT (354916.992 594670.505)
        17031010201  6450  POINT (354105.876 594088.600)
        17031010202  2818  POINT (354650.684 594093.822)
        17031010300  6236  POINT (355209.361 594086.149)
        17031010400  5042  POINT (355809.748 592808.043)

        The `chi_travel_costs` dataset is the cost matrix, showing the travel time between each of the Census Tracts in the Chicago metro area.

        >>> chi_travel_costs.head()
                origin         dest   cost
        0  17093890101  17031010100  91.20
        1  17093890101  17031010201  92.82
        2  17093890101  17031010202  92.95
        3  17093890101  17031010300  89.40
        4  17093890101  17031010400  84.97

        Make sure you assign your desired geometry projection, which you can change as follows.

        >>> chi_population = chi_population.to_crs(epsg = 2790)
        >>> chi_docs_dents = chi_docs_dents.to_crs(epsg = 2790)

        Now, create an instance of the `Access` class and specify the demand, supply, and cost datasets.

        >>> chicago_primary_care = Access(demand_df = chi_population, demand_index = "geoid",
                                          demand_value = "pop",
                                          supply_df = chi_docs_dents, supply_index = "geoid",
                                          supply_value = ["doc", "dentist"],
                                          cost_df = chi_travel_costs, cost_origin  = "origin",
                                          cost_dest = "dest", cost_name = "cost")

        To calculate euclidean distances between Census Tracts within 250km of eachother, you can set the `threshold` to 250000 (meters). Setting `centroid_o` and `centroid_d` to `True` calculates the centroid of the geom in your dataset.

        >>> chicago_primary_care.create_euclidean_distance_neighbors(name= 'euclidean_neighbors', threshold = 250000, centroid_o = True, centroid_d = True)

        The newly calculated euclidean distance is stored in the `neighbor_cost_df` attribute.

        >>> chicago_primary_care_geom.neighbor_cost_df.head()
                origin         dest  euclidean_neighbors
        0  17031010100  17031010100             0.000000
        1  17031010100  17031010201           998.259243
        2  17031010100  17031010202           635.203387
        3  17031010100  17031010300           653.415713
        4  17031010100  17031010400          2065.375554
        """
        import geopandas as gpd

        # TO-DO: check for unprojected geometries

        # Continue if the dataframes are geodataframes, else throw an error
        if type(self.demand_df) is not gpd.GeoDataFrame:
            raise TypeError(
                "Cannot calculate euclidean distance without a geometry of supply side"
            )

        # Reset the index so that the geoids are accessible
        df1 = self.demand_df.rename_axis("origin").reset_index()
        df2 = self.demand_df.rename_axis("dest").reset_index()

        # Convert to centroids if so-specified
        if centroid:
            df1.set_geometry(df1.centroid, inplace=True)
            df2.set_geometry(df2.centroid, inplace=True)

        # Calculate the distances.
        if (df1.geom_type == "Point").all() & (df2.geom_type == "Point").all():
            # If both geometries are point types, merge on a temporary dummy column
            df1["temp"] = 1
            df2["temp"] = 1
            df1and2 = df1[["temp", "geometry", "origin"]].merge(
                df2[["temp", "geometry", "dest"]].rename(columns={"geometry": "geomb"})
            )
            df1and2.drop("temp", inplace=True, axis=1)
            df1and2[name] = df1and2.distance(df1and2.set_geometry("geomb"))
        else:
            # Execute an sjoin for non-point geometries, based upon a buffer zone
            df1and2 = gpd.sjoin(
                df1,
                df2.rename(columns={"geometry": "geomb"}).set_geometry(
                    df2.buffer(threshold)
                ),
            )
            df1and2[name] = df1and2.distance(df1and2.set_geometry("geomb"))

        # Add it to the cost df.
        df1and2 = df1and2[df1and2[name] < threshold]
        self.neighbor_cost_df = self.neighbor_cost_df.merge(
            df1and2[[name, "origin", "dest"]],
            how="outer",
            left_on=[self.neighbor_cost_origin, self.neighbor_cost_dest],
            right_on=["origin", "dest"],
        )
        # Add it to the list of costs.
        self.neighbor_cost_names.append(name)
        # Set the default cost if it does not exist
        if not hasattr(self, "_neighbor_default_cost"):
            self._neighbor_default_cost = name
