# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 19:37:03 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""

import geopandas as gpd
from pyevtk.hl import polyLinesToVTK

fn = r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\qfaults.shp"
bounds = {"longitude": (-123, -114), "latitude": (37, 42)}
project_to = {"epsg": 26911}

# read in file
gdf = gpd.read_file(fn)

# trim data
if bounds is not None:
    gdf = gdf.cx[bounds["longitude"][0]:bounds["longitude"][1], 
                 bounds["latitude"][0]:bounds["latitude"][1]]
    
# reproject
if project_to is not None:
    gdf = gdf.to_crs(**project_to)



