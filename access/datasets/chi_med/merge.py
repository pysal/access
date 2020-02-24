#!/usr/bin/env python 

import geopandas as gpd
import pandas    as pd

from fiona.crs import from_epsg
import psycopg2
from netrc import netrc

user, acct, passwd = netrc().authenticators("harris")
cen_con = psycopg2.connect(database = "census", user = user, password = passwd,
                           host = "saxon.harris.uchicago.edu", port = 5432)

il_map = gpd.read_postgis("select geoid, ST_Centroid(ST_Transform(geomsimp, 3528)) geomsimp "
                          "from census_tracts_2015 where state = 17 order by geoid;",
                          index_col = "geoid", geom_col = "geomsimp", 
                          con = cen_con, crs = from_epsg(3528))

il_med = pd.read_csv("docs_dentists_pcsa.csv", index_col = "geoid")
il_map.join(il_med).reset_index().to_file("il_med.geojson", driver = "GeoJSON")

