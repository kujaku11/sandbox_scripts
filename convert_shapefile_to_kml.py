# -*- coding: utf-8 -*-
"""
Created on Mon May  6 13:05:25 2019

@author: jpeacock
"""

import geopandas as gpd
import fiona

fiona.drvsupport.supported_drivers["KML"] = "rw"
fiona.drvsupport.supported_drivers["kml"] = "rw"
fiona.drvsupport.supported_drivers[
    "libkml"
] = "rw"  # enable KML support which is disabled by default
fiona.drvsupport.supported_drivers[
    "LIBKML"
] = "rw"  # enable KML support which is disabled by default

shp_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\BuffaloValley\USGS_MTPlan_For_NOI\buffalo_valley_mt_stations.shp"

gdf = gpd.read_file(shp_fn)
gdf = gdf.rename(columns={"station": "name"})
gdf = gdf.to_crs(epsg=4326)
gdf.to_file(shp_fn[:-4] + ".kml", driver="kml")
