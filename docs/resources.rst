.. resources

====================================
Resources for Computing Travel Cost
====================================


The spatial access measures depend on travel times or distances between origins and destinations. If you only need distances between origins and destinations, the package will calculate Euclidean distances for your projected data. If you need travel times for a specific travel mode, you need to generate these so-called travel time matrices from other sources.

Since this is computationally expensive and non-trivial to implement at scale, we pre-computed driving times between tracts within 100 km (62 miles) of each other for the whole US. In addition, you can access matrices for walking, transit or driving times between blocks or tracts for the 20 largest cities in the US.

Explore the map of driving times between a selected Census tract and all tracts within 100 km (62 miles) by clicking around or entering an address.
You can also download these results for driving or transit.

.. raw:: html

   <figure class="figure">
     <embed src="https://saxon.harris.uchicago.edu/mmap/" style="padding: 10pt 0; width:95%; height: 70vh;">
     <figcaption class="figure-caption text-center">
       Web Service to explore and download travel times between tracts
     </figcaption>
   </figure>


.. raw:: html

    <iframe src="https://geoda.s3.amazonaws.com/data/otp/index.html" height="2000px" width="100%"></iframe>

If you need to compute customized cost matrices, there are several options.

(e.g. `OSRM <http://project-osrm.org/>`_, `OpenTrip Planner <https://www.opentripplanner.org/>`_, `Valhalla <https://github.com/valhalla>`_, `Pandana <https://udst.github.io/urbanaccess/introduction.html>`_, our `PyPi spatial access package <https://pypi.org/project/spatial-access/>`_, or use one of our `pre-computed matrices <https://geoda.s3.amazonaws.com/data/otp/index.html>`_.

If you prefer a point-and-click interface for analysis in the contiguous US states, you can generate results with the PySAL spatial access package through the `Live App <https://access.readthedocs.io/en/latest/app.html>`_ we are hosting on AWS. This is inexpensive since it draws on these pre-computed travel times.
