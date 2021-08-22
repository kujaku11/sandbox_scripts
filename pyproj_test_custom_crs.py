# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 15:27:37 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""

import pyproj as proj

crs_wgs84 = proj.Proj(init="epsg:4326")

# custom CRS
c_proj = "tmerc"
c_lat = 0
c_lon = -113.25
c_k = 0.9996
c_bind_x = 4511000
c_bind_y = 0
c_geoid = "WGS84"
c_units = "m"
custom_crs_str = f"+proj={c_proj} +lat_0={c_lat} +lon_0={c_lon} +k={c_k} +x_0={c_bind_x} +y_0={c_bind_y} +ellps={c_geoid} +units={c_units} +no_defs"
crs_custom = proj.Proj(custom_crs_str)

print(proj.transform(crs_wgs84, crs_custom, -131, 31))
