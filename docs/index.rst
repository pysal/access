.. documentation master file

========================
Spatial Access for PySAL
========================

Wether you work with data in health, retail, employment or other domains, spatial accessibility measures help you identify potential spatial mismatches between the supply and demand of services. Spatial access measures indicate how close demand locations are to supply locations.

We built this package for several reasons:

- to make a new spatial access metric available,
- to allow for easy comparison between RAAM and classic spatial access models,
- to support spatial access research at scale by making pre-computed travel time matrices available and sharing code for computing new matrices at scale, and
- to allow users who prefer a point-and-click interface to obtain spatial access results for their data using our web app (for US states)

This PySAL package implements our new measure that simultaneously accounts for congestion at the destination and travel time:

- Rational Agent Access Model (RAAM) (Saxon and Snow 2019, :cite:`2019_saxon_snow_raam`).

Here is an example of the results of the RAAM model: It shows, compared to the national average, how much more or less spatially accessible each Census tract is to primary care. Darker blue areas have better spatial access (below-average travel costs) while darker red areas have worse spatial access (above average travel costs).

.. image:: _static/images/full_us.jpg
   :width: 100%

In addition, the package calculates five classic spatial access models within the same access class as RAAM for easy comparison between models:

- Floating Catchment Areas (FCA): For each provider, this is the ratio of providers to clients within a given travel time to the provider (Huff 1963, :cite:`1963_huff_shopping_trade_areas`, Joseph and Bantock 1982, :cite:`1982_joseph_potential_physical_accessibility_rural` and Luo 2004, :cite:`2004_luo_gis_floating_catchment`).

- Two-Stage FCAs (2SFCA): Calculated in two steps for a given travel time to the provider: 1) for each provider, the provider-to-client ratio is generated, 2) for each point of origin, these ratios are then summed (Luo and Wang, 2002, :cite:`2002_luo_spatial_accessibility_chicago` and Wang and Luo 2005, :cite:`2004_wang_luo_HPSAs`).

- Enhanced 2SFCA (E2SFCA): 2SFCA but with less weight to providers that are still within the travel threshold but at larger distances from the point of origin (Luo and Qi 2009, :cite:`2009_luo_qi_E2SFCA`).

- Three-Stage FCA (3SFCA): adds distance-based allocation function to E2SFCA (Wan, Zou, and Sternberg, 2012, :cite:`2012_wan_3SFCA`).

- Access Score: This is a weighted sum of access components like distance to provider and relative importance of provider type (Isard 1960, :cite:`1960_isard_reganalysis`).

These classic models were also recently implemented in the Python package `aceso <https://github.com/tetraptych/aceso>`_.

These spatial access measures depend on travel times or distances between origins and destinations. The `Resources <resources>`_ section outlines how these can be calculated.

.. toctree::
   :hidden:
   :maxdepth: 3
   :caption: Contents:

   Installation <installation>
   API <api>
   References <references>
   Resources <resources>
   Live App <app>



.. _PySAL: https://github.com/pysal/pysal
