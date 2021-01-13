# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 19:37:03 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
from pathlib import Path
import geopandas as gpd
from gtv.files.shp import FileShp

fn = Path(r"c:\Users\jpeacock\Downloads\GIS\us_states_land.shp")
#bounds = {"longitude": (-128, -100), "latitude": (50, 70)}
bounds = None
project_to = {"epsg": 26911}
custom_crs = '+proj=tmerc +lat_0=0 +lon_0=-113.25 +k=0.9996 +x_0=4511000 +y_0=0 +ellps=WGS84 +units=m +no_defs'
# bounds = None
# project_to = None
# custom_crs = None

# read in file
gdf = gpd.read_file(fn)

# trim data
if bounds is not None:
    gdf = gdf.cx[
        bounds["longitude"][0] : bounds["longitude"][1],
        bounds["latitude"][0] : bounds["latitude"][1],
    ]

# reproject
if project_to is not None:
    gdf = gdf.to_crs(custom_crs)
    
    # make local shape file
    temp_fn = Path(fn.parent, "temp.shp")
    gdf.to_file(temp_fn)
    
    f = FileShp.read(temp_fn)
    f.toVTK(Path(fn.parent, fn.stem).as_posix())
else:
    f = FileShp.read(fn)
    f.toVTK(Path(fn.parent, fn.stem).as_posix())


    

