.. resources

====================================
Resources for Computing Travel Cost
====================================

|

The spatial access measures depend on travel times or distances between origins and destinations. If you only need distances between origins and destinations, the package will calculate Euclidean distances for your projected data. If you need travel times for a specific travel mode, you need to generate these so-called travel time (or travel cost) matrices from other sources.

Explore and Download Pre-Computed Travel Times
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
|
Since computing travel times is computationally expensive and non-trivial at scale, we've pre-computed times between common Census geographies for several travel modes. These times cover the entire United States and the most recent Census years (2020+). They are available via [OpenTimes](https://opentimes.org/), a dedicated website created by research assistant Dan Snow (UChicago MPP'19). For more information on how these times are calculated, visit the [OpenTimes GitHub](https://github.com/dfsnow/opentimes).

Compute your Own Travel Times
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
|
If you need to compute customized cost matrices, there are several options. This table lists some of them:

.. raw:: html

  <table class="tg">
    <tr>
      <th class="tg-1wig"></th>
      <th class="tg-1wig">Name</th>
      <th class="tg-1wig">Installation</th>
      <th class="tg-1wig">Notes</th>
    </tr>
    <tr>
      <td class="tg-0lax"><img src="_static/images/pgrouting.png" height="50" width="120"/></td> 
      <td class="tg-0lax"><a href="https://pgrouting.org/">pgRouting</a></td>
      <td class="tg-0lax"><a href="https://github.com/JamesSaxon/routing-container">docker</a></td>
      <td class="tg-0lax">Good for driving, open-source and free, PostgreSQL/postgis and OpenStreetMap (OSM)</a></td>
    </tr>
    <tr>
      <td class="tg-0lax"><img src="_static/images/osrm.png" height="30" width="120"/></td> 
      <td class="tg-0lax"><a href="http://project-osrm.org/">OSRM</a></td>
      <td class="tg-0lax">
            <a href="https://github.com/Project-OSRM/osrm-backend/wiki/Building-OSRM">install</a> /
            <a href="https://cran.r-project.org/web/packages/osrm/readme/README.html">R</a> /
            <a href="https://github.com/Project-OSRM/osrm-backend#using-docker">docker</a>
      </td>
      <td class="tg-0lax">Best for driving, OSM, open-source and free, customized travel parameters, C++</a></td>      
    </tr>
    <tr>
      <td class="tg-0lax"><img src="_static/images/otp.png" height="50" width="60"/></td> 
      <td class="tg-0lax"><a href="https://www.opentripplanner.org/">Open Trip Planner</a></td>
      <td class="tg-0lax">
            <a href="https://github.com/dfsnow/otp-routing">docker routing</a> /
            <a href="https://github.com/dfsnow/otp-resources">resources</a> /
            <a href="https://cloud.docker.com/u/snowdfs">DockerHub</a>
            </td>
      <td class="tg-0lax">Best for transit, open-source and free, customized travel parameters, Java</a></td>      
    </tr>
     <tr>
      <td class="tg-0lax"><img src="_static/images/valhalla.png" height="30" width="200"/></td> 
      <td class="tg-0lax"><a href="https://valhalla.readthedocs.io/en/latest/">Valhalla</a></td>
      <td class="tg-0lax"><a href="https://github.com/valhalla/valhalla">install</a></td>
      <td class="tg-0lax">Multi-modal, OSM, open-source, for fee at scale, Python</a></td>      
    </tr>  
     <tr>
      <td class="tg-0lax"><img src="_static/images/pandana.png" height="42" width="42"/></td> 
      <td class="tg-0lax"><a href="https://udst.github.io/urbanaccess/introduction.html">Pandana</a></td>
      <td class="tg-0lax"><a href="https://udst.github.io/pandana/installation.html">install</a></td>
      <td class="tg-0lax">Good for driving and walking, OSM, open-source and free, part of UrbanSim, Python</a></td>      
    </tr> 
      <tr>
      <td class="tg-0lax"><img src="_static/images/graphhopper.png" height="30" width="145"/></td> 
      <td class="tg-0lax"><a href="https://www.graphhopper.com/open-source/">Graphhopper</a></td>
      <td class="tg-0lax"><a href="https://github.com/graphhopper/graphhopper">install</a></td>
      <td class="tg-0lax">Multi-modal, OSM, open-source, for fee at scale, Python</a></td>      
    </tr>
      <tr>
      <td class="tg-0lax"><img src="_static/images/csds.png" height="50" width="100"/></td> 
      <td class="tg-0lax"><a href="https://pypi.org/project/spatial-access/">Spatial Access Package</a></td>
      <td class="tg-0lax">
      <a href="https://github.com/GeoDaCenter/spatial_access">install</a> /
      <a href="https://github.com/GeoDaCenter/spatial_access/tree/master/docs/notebooks">notebooks</a>
    </td>
      <td class="tg-0lax">Best for walking, OSM, scales well, open-source and free, includes spatial access metrics, Python</a></td>      
    </tr>
          <tr>
      <td class="tg-0lax"><img src="_static/images/r.png" height="60" width="60"/></td> 
      <td class="tg-0lax">e.g. dogr</a>, R5 and gtfs-router</td>
      <td class="tg-0lax"><a href="https://github.com/ATFutures/dodgr">dogr</a>, <a href="https://ipeagit.github.io/r5r/index.html">R5</a>, <a href="https://github.com/ATFutures/gtfs-router">gtfs-router</a></td>
      <td class="tg-0lax">Selected R packages</a></td>      
     </tr>
      <tr>
      <td class="tg-0lax"><img src="_static/images/googlemaps.png" height="60" width="60"/></td> 
      <td class="tg-0lax"><a href="https://cloud.google.com/maps-platform/">Google Maps</a></td>
      <td class="tg-0lax"><a href="https://developers.google.com/maps/documentation/distance-matrix/intro">install</a></td>
      <td class="tg-0lax">Accurate multi-modal, customized travel parameters, commercial, expensive at scale</a></td>      
     </tr>
  </table>
|


