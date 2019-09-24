.. documentation master file

========================
Spatial Access for PySAL
========================

This PySAL package calculates how spatially accessible points of origins are to a set of destinations.
We have implemented four classic measures:

- Floating Catchment Areas (FCA) (Huff 1963, :cite:`1963_huff_shopping_trade_areas`, Joseph and Bantock 1982, :cite:`1982_joseph_potential_physical_accessibility_rural` and Luo 2004, :cite:`2004_luo_gis_floating_catchment`).
- Two-Stage FCAs (2SFCA) (Luo and Wang, 2002, :cite:`2002_luo_spatial_accessibility_chicago` and Wang and Luo 2005, :cite:`2004_wang_luo_HPSAs`),
- Enhanced 2SFCA (E2SFCA) (Luo and Qi 2009, :cite:`2009_luo_qi_E2SFCA`),
- Three-Stage FCA (3SFCA) (Wan, Zou, and Sternberg, 2012, :cite:`2012_wan_3SFCA`)

and our new measure:

- Rational Agent Access Model (RAAM) (Saxon and Snow 2019, :cite:`2019_saxon_snow_raam`),

Here is an example of the results of the RAAM model: It shows, compared to the national average, how much more or less spatially accessible each Census tract is to primary care. Darker blue areas have better spatial access (below-average travel costs) while darker red areas have worse spatial access (above average travel costs).

.. image:: _static/images/full_us.jpg
   :width: 100%

These spatial access measures depend on travel times or distances between origins and destinations. You need to generate these so-called travel time matrices from other sources (e.g. `OSRM <http://project-osrm.org/>`_, `OpenTrip Planner <https://www.opentripplanner.org/>`_,`Valhalla <https://github.com/valhalla>`_, `Pandana <https://udst.github.io/urbanaccess/introduction.html>`_, our `PyPi spatial access package <https://pypi.org/project/spatial-access/>`_, or use one of our `pre-computed matrices <https://geoda.s3.amazonaws.com/data/otp/index.html>`_.

If you prefer a point-and-click interface for analysis in the contiguous US states, you can generate results with the PySAL spatial access package through an Amazon Web Service that we are hosting. This is inexpensive since it draws on these pre-computed travel times (driving times between tracts within 100 km (62 miles) of each other for the whole contiguous US, or walking, transit or driving between blocks or tracts for the 20 largest cities in the US).

Explore the map by clicking around or entering an address.
You can also download results data for one tract to all tracts within 100 km (62 miles).

.. raw:: html

   <figure class="figure">
     <embed src="https://saxon.harris.uchicago.edu/mmap/" style="padding: 10pt 0; width:95%; height: 70vh;">
     <figcaption class="figure-caption text-center">
       Web Service to get spatial access results for pre-computed travel times
     </figcaption>
   </figure>


.. toctree::
   :hidden:
   :maxdepth: 3
   :caption: Contents:

   Installation <installation>
   API <api>
   References <references>


.. _PySAL: https://github.com/pysal/pysal
