# -*- coding: utf-8 -*-
"""
Created on Mon May  6 13:05:25 2019

@author: jpeacock
"""

from pathlib import Path
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

shp_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\SAGE\2024\MT_2024_draft_locations.shp"
)
# r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\BuffaloValley\USGS_MTPlan_For_NOI\buffalo_valley_mt_stations.shp"

gdf = gpd.read_file(shp_fn)
gdf = gdf.rename(columns={"station": "name"})
# gdf["name"] = [f"ld{x:03}" for x in range(len(gdf.name))]
gdf = gdf.to_crs(epsg=4326)
gdf.to_file(shp_fn.parent.joinpath(f"{shp_fn.stem}.kml"), driver="kml")

gdf = gdf.rename(columns={"Id": "name"})
gdf.name = gdf.name.astype(str)
gdf.to_file(shp_fn.parent.joinpath(f"{shp_fn.stem}.gpx"), driver="GPX")
