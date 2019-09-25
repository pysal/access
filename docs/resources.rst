.. resources

====================================
Resources for Computing Travel Cost
====================================


The spatial access measures depend on travel times or distances between origins and destinations. If you only need distances between origins and destinations, the package will calculate Euclidean distances for your projected data. If you need travel times for a specific travel mode, you need to generate these so-called travel time matrices from other sources (e.g. `OSRM <http://project-osrm.org/>`_, `OpenTrip Planner <https://www.opentripplanner.org/>`_, `Valhalla <https://github.com/valhalla>`_, `Pandana <https://udst.github.io/urbanaccess/introduction.html>`_, our `PyPi spatial access package <https://pypi.org/project/spatial-access/>`_, or use one of our `pre-computed matrices <https://geoda.s3.amazonaws.com/data/otp/index.html>`_.

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
